"""Append lines from `requirements_additions.txt` to `requirements.txt` safely.

Run from project root:

    python scripts/append_requirements.py

It will detect common encodings and avoid duplicating existing entries.
"""
from pathlib import Path
import codecs

ROOT = Path(__file__).resolve().parent.parent
REQ = ROOT / 'requirements.txt'
ADD = ROOT / 'requirements_additions.txt'

def read_text_auto(path: Path) -> str:
    """Try common encodings to read a file."""
    for enc in ('utf-8', 'utf-8-sig', 'utf-16', 'latin-1'):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    raise RuntimeError('Unable to read file with known encodings')

def main():
    if not ADD.exists():
        print('No additions file found:', ADD)
        return
    additions = [l.strip() for l in read_text_auto(ADD).splitlines() if l.strip()]
    if not REQ.exists():
        # create requirements.txt
        REQ.write_text('\n'.join(additions) + '\n', encoding='utf-8')
        print('Created requirements.txt with additions')
        return

    orig = read_text_auto(REQ)
    orig_lines = {l.strip() for l in orig.splitlines() if l.strip()}
    to_add = [l for l in additions if l not in orig_lines]
    if not to_add:
        print('All additions already present in requirements.txt')
        return
    # append using utf-8
    with REQ.open('a', encoding='utf-8') as f:
        for line in to_add:
            f.write(line + '\n')
    print('Appended', len(to_add), 'lines to requirements.txt')

if __name__ == '__main__':
    main()
