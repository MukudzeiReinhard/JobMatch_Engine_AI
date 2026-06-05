import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# 1. Configuration
SQLITE_DB = 'db.sqlite3'
# PASTE YOUR ACTUAL RENDER EXTERNAL DATABASE URL HERE:
POSTGRES_URL = "postgresql://jobmatch_prod_user:PbjM3i16XZQ9tmkjRZskbVhJCSvmQ5Ve@dpg-d8h4ins2m8qs73alls20-a.frankfurt-postgres.render.com/jobmatch_prod"

print("🚀 Starting completely isolated database migration pipeline...")

def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

try:
    # 2. Connect to both databases
    lite_conn = sqlite3.connect(SQLITE_DB)
    lite_conn.row_factory = dict_factory  
    lite_cur = lite_conn.cursor()
    
    pg_conn = psycopg2.connect(POSTGRES_URL)
    pg_cur = pg_conn.cursor()
    
    # 3. Fetch all tables from SQLite
    lite_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    all_tables = [t['name'] for t in lite_cur.fetchall()]
    
    # 4. Standard ordering
    ordered_tables = [
        'django_content_type',
        'auth_permission',
        'auth_group',
        'auth_user',
        'auth_group_permissions',
        'auth_user_groups',
        'auth_user_user_permissions',
        'django_admin_log',
        'django_session',
    ]
    for table in all_tables:
        if table not in ordered_tables and table not in ['sqlite_sequence', 'django_migrations']:
            ordered_tables.append(table)

    # 5. FORCE A CLEAN SLATE ON POSTGRESQL (Using CASCADE)
    print("🧹 Executing deep cascade wipe on existing cloud rows...")
    for table in reversed(ordered_tables):
        if table in ['sqlite_sequence', 'django_migrations']:
            continue
        try:
            # TRUNCATE CASCADE forcefully empties the table and any dependent child rows,
            # and RESTART IDENTITY resets primary key IDs back to 1.
            pg_cur.execute(f"TRUNCATE TABLE \"{table}\" RESTART IDENTITY CASCADE;")
            pg_conn.commit()
        except Exception:
            pg_conn.rollback()
            try:
                pg_cur.execute(f"DELETE FROM \"{table}\";")
                pg_conn.commit()
            except Exception:
                pg_conn.rollback()

    # 6. Adaptive Independent Multi-Pass Queue
    queue = list(ordered_tables)
    pass_number = 1

    while queue and pass_number <= 6:
        print(f"\n🔄 --- STARTING INTEGRITY PASS #{pass_number} ({len(queue)} tables remaining) ---")
        postponed_tables = []
        
        for table in queue:
            if table in ['sqlite_sequence', 'django_migrations']:
                continue
                
            lite_cur.execute(f"SELECT * FROM \"{table}\";")
            rows = lite_cur.fetchall()
            
            if not rows:
                continue
                
            pg_cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';")
            pg_columns = pg_cur.fetchall()
            
            target_columns = [col[0] for col in pg_columns]
            boolean_columns = {col[0] for col in pg_columns if col[1] == 'boolean'}
            
            cleaned_rows = []
            for row_dict in rows:
                values_in_pg_order = []
                for col_name in target_columns:
                    val = row_dict.get(col_name, None)
                    if col_name in boolean_columns and val in (0, 1, '0', '1'):
                        val = bool(int(val))
                    values_in_pg_order.append(val)
                cleaned_rows.append(tuple(values_in_pg_order))
            
            cols_str = ", ".join([f'"{c}"' for c in target_columns])
            insert_query = f"INSERT INTO \"{table}\" ({cols_str}) VALUES %s"
            
            try:
                execute_values(pg_cur, insert_query, cleaned_rows)
                pg_conn.commit()
                print(f"🟢 Successfully migrated: {table} ({len(rows)} records)")
            except Exception as table_err:
                pg_conn.rollback()
                
                if "foreign key" in str(table_err).lower():
                    print(f"🟡 Postponing table {table} (waiting for parent table to be seeded first...)")
                    postponed_tables.append(table)
                else:
                    print(f"🔴 Fatal table failure for {table}: {table_err}")
                    raise table_err
                    
        queue = list(postponed_tables)
        pass_number += 1

    if not queue:
        print("\n🟢 SUCCESS: Your entire relational dataset has been successfully mirrored to PostgreSQL!")
    else:
        print(f"\n🔴 Migration finished, but some tables remained uncopied: {queue}")

except Exception as e:
    print(f"\n🔴 Pipeline crashed: {e}")
finally:
    if 'lite_conn' in locals(): lite_conn.close()
    if 'pg_conn' in locals(): pg_conn.close()