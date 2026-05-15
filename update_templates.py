from pathlib import Path
files = {
    'accounts/templates/accounts/edit_employee_profile.html': '''{% extends 'base.html' %}

{% block title %}Edit Employee Profile{% endblock %}

{% block head %}
<style>
    .profile-container { background-color: #ffffff; padding: 2rem; border-radius: 0.75rem; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.08); }
    .btn-group { display: flex; gap: 0.75rem; flex-wrap: wrap; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-8">
        <div class="profile-container">
            <h2 class="mb-4 text-center">Update Employee Profile</h2>
            <form method="post" class="profile-form" enctype="multipart/form-data">
                {% csrf_token %}
                {{ form.as_p }}
                <div class="btn-group mt-3">
                    <button type="submit" class="btn btn-primary flex-fill">Save Changes</button>
                    <a href="{% url 'employee_profile' %}" class="btn btn-secondary flex-fill">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/employee_profile.html': '''{% extends 'base.html' %}

{% block title %}Profile | {{ employee.name }} {{ employee.surname }}{% endblock %}

{% block head %}
<style>
    .profile-card { border-top: 0.35rem solid #0d6efd; }
    .profile-avatar { width: 100px; height: 100px; object-fit: cover; border-radius: 50%; border: 0.35rem solid #dee2e6; }
    .status-badge { font-weight: 600; }
</style>
{% endblock %}

{% block content %}
<div class="row g-4">
    <div class="col-12 col-md-4">
        <div class="card shadow-sm profile-card h-100">
            <div class="card-body text-center">
                <img class="profile-avatar mb-3" src="https://ui-avatars.com/api/?name={{ employee.name }}+{{ employee.surname }}&size=256" alt="Profile Picture">
                <h2 class="h5 mb-1">{{ employee.name }} {{ employee.surname }}</h2>
                <p class="text-muted mb-3">Update your account information below.</p>
                <a href="{% url 'login' %}" class="btn btn-link">← Log Out</a>
            </div>
        </div>
    </div>
    <div class="col-12 col-md-8">
        <div class="card shadow-sm profile-card h-100">
            <div class="card-body">
                <div class="d-flex align-items-center gap-2 mb-4">
                    <span class="text-primary fs-5">Employee Profile</span>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">First Name</p>
                        <p class="mb-0">{{ employee.name }}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Last Name</p>
                        <p class="mb-0">{{ employee.surname }}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Email</p>
                        <p class="mb-0">{{ employee.email }}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Location</p>
                        <p class="mb-0">{{ employee.location|default:"Not specified" }}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Department</p>
                        <p class="mb-0">{{ employee.department|default:"Not specified" }}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Birth Date</p>
                        <p class="mb-0">{{ employee.birth_date|default:"Not specified" }}</p>
                    </div>
                </div>
                <div class="mb-4">
                    <p class="mb-1 text-muted small">Bio</p>
                    <p class="mb-0">{{ employee.bio|default:"No bio added yet" }}</p>
                </div>
                <div class="row g-3 mb-4">
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Resume Status</p>
                        <p class="mb-0 status-badge {% if employee.resume %}text-success{% else %}text-warning{% endif %}">{% if employee.resume %}✓ Resume Uploaded{% else %}⚠ No Resume Uploaded{% endif %}</p>
                    </div>
                    <div class="col-12 col-sm-6">
                        <p class="mb-1 text-muted small">Cognitive Assessment</p>
                        <p class="mb-0 status-badge {% if employee.target_analytical %}text-success{% else %}text-warning{% endif %}">{% if employee.target_analytical %}✓ Assessment Completed{% else %}⚠ Assessment Not Completed{% endif %}</p>
                    </div>
                </div>
                {% if employee.target_analytical %}
                <div class="mb-4">
                    <small class="text-muted">Assessment Scores</small>
                    <div class="row g-3 mt-2">
                        <div class="col-6 col-sm-3"><strong>Analytical</strong><br>{{ employee.target_analytical }}</div>
                        <div class="col-6 col-sm-3"><strong>Practical</strong><br>{{ employee.target_practical }}</div>
                        <div class="col-6 col-sm-3"><strong>Relational</strong><br>{{ employee.target_relational }}</div>
                        <div class="col-6 col-sm-3"><strong>Experimental</strong><br>{{ employee.target_experimental }}</div>
                    </div>
                </div>
                {% endif %}
                <div class="d-grid gap-2 gap-md-3">
                    <a href="{% url 'upload_resume' %}" class="btn btn-success">📄 Upload Resume</a>
                    <a href="{% url 'take_survey' %}" class="btn btn-purple" style="background-color:#6f42c1; color:#fff;">📋 Take Survey</a>
                    <a href="{% url 'match_results' %}" class="btn btn-primary">🎯 Find Job Matches</a>
                    <a href="{% url 'edit_employee_profile' %}" class="btn btn-secondary">✏️ Edit Profile</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    'jobs/templates/job_entry.html': '''{% extends 'base.html' %}

{% block title %}Add Job Entry{% endblock %}

{% block head %}
<style>
    .job-card { max-width: 720px; margin: 0 auto; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-8">
        <div class="card shadow-sm job-card p-4">
            <h1 class="h4 mb-3">Create a Job Entry</h1>
            <p class="text-muted mb-4">Add a new job listing to the recruitment engine.</p>
            <form method="post">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/signup.html': '''{% extends 'base.html' %}

{% block title %}Create Account{% endblock %}

{% block head %}
<style>
    .signup-card { border-radius: 1rem; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-6">
        <div class="card shadow-sm signup-card p-4">
            <h2 class="h4 text-center mb-2">Join the System</h2>
            <p class="text-center text-muted mb-4">Please fill in the details below to create your dissertation account.</p>
            <form method="post" class="signup-form">
                {% csrf_token %}
                {{ form.as_p }}
                <button type="submit" class="btn btn-success w-100">Register Account</button>
            </form>
            <div class="text-center mt-4">
                <p class="mb-0">Already have an account? <a href="{% url 'login' %}">Log in here</a></p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
'''
}
for relative, content in files.items():
    path = Path(relative)
    if not path.exists():
        raise FileNotFoundError(f"Missing {relative}")
    path.write_text(content, encoding='utf-8')
print('Updated:', ', '.join(files.keys()))
