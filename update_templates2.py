from pathlib import Path
files = {
    'jobs/templates/jobs/potential_candidates.html': '''{% extends 'base.html' %}

{% block title %}Potential Candidates by Job{% endblock %}

{% block head %}
<style>
    .job-section { background-color: #ffffff; border-radius: 0.75rem; box-shadow: 0 0.5rem 1rem rgba(0,0,0,0.06); border-left: 0.4rem solid #0d6efd; }
    .candidate-row { transition: background-color 0.2s; border-radius: 0.5rem; }
    .candidate-row:hover { background-color: #f8f9fa; }
    .score-pill { font-size: 0.9rem; font-weight: bold; min-width: 65px; text-align: center; }
</style>
{% endblock %}

{% block content %}
    <div class="row mb-4">
        <div class="col-12">
            <h1 class="h3 fw-bold text-dark">Potential Candidates by Job</h1>
            <p class="text-muted">Browse jobs and see automatically ranked talent based on composite matching scores.</p>
        </div>
    </div>

    {% regroup jobs by job as job_list %}

    {% if job_list %}
        {% for group in job_list %}
            <div class="job-section p-4 mb-4">
                <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center mb-3 gap-3">
                    <div>
                        <h2 class="h5 mb-1 text-primary">{{ group.grouper.title }}</h2>
                        <span class="text-muted small">
                            <i class="bi bi-building"></i> {{ group.grouper.company|default:"Internal Role" }}
                            | <i class="bi bi-geo-alt"></i> {{ group.grouper.location|default:"Remote" }}
                        </span>
                    </div>
                    <span class="badge bg-secondary">{{ group.list|length }} Candidates</span>
                </div>

                <div class="table-responsive">
                    <table class="table table-borderless align-middle">
                        <thead>
                            <tr class="text-uppercase text-secondary fs-7" style="font-size: 0.8rem;">
                                <th style="width: 5%">Rank</th>
                                <th style="width: 40%">Candidate</th>
                                <th style="width: 35%">Employee Location</th>
                                <th style="width: 20%">Compatibility</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for record in group.list %}
                                <tr class="candidate-row">
                                    <td class="fw-bold text-secondary">#{{ forloop.counter }}</td>
                                    <td>
                                        <div class="d-flex align-items-center">
                                            <div class="bg-light text-primary rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px;">
                                                <i class="bi bi-person-fill"></i>
                                            </div>
                                            <div>
                                                <div class="fw-bold text-dark">{{ record.employee.user.get_full_name|default:record.employee.user.username }}</div>
                                                <div class="text-muted small">{{ record.employee.email|default:"No Email" }}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="text-muted">{{ record.employee.location|default:"No Location" }}</span>
                                    </td>
                                    <td>
                                        <div class="d-flex align-items-center justify-content-end">
                                            <span class="badge p-2 score-pill {% if record.compatibility_score >= 80 %}bg-success{% elif record.compatibility_score >= 50 %}bg-warning text-dark{% else %}bg-danger{% endif %}">
                                                {{ record.compatibility_score|floatformat:1 }}%
                                            </span>
                                        </div>
                                    </td>
                                </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        {% endfor %}
    {% else %}
        <div class="text-center py-5 bg-white rounded-3 shadow-sm">
            <i class="bi bi-folder-x display-1 text-muted"></i>
            <h3 class="mt-3 text-dark">No Compatibility Data Found</h3>
            <p class="text-muted">Run your recommendation engine matching algorithm to populate this list.</p>
        </div>
    {% endif %}
{% endblock %}
''',
    'accounts/templates/accounts/match_results.html': '''{% extends 'base.html' %}

{% block title %}Job Match Results{% endblock %}

{% block head %}
<style>
    .match-bar-container { height: 12px; border-radius: 10px; background-color: #e9ecef; }
    .custom-bar { transition: width 0.6s ease; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12">
        <h1 class="mb-4">Your Job Match Results</h1>

        {% if not resume_exists %}
        <div class="alert alert-warning" role="alert">
            <strong>No resume uploaded!</strong> Upload your resume to get more accurate skill-based matches.
            <a href="{% url 'upload_resume' %}" class="alert-link">Upload Resume</a>
        </div>
        {% endif %}

        {% if results %}
            {% for item in results %}
            <div class="card mb-4 shadow-sm">
                <div class="card-body">
                    <div class="row gy-3">
                        <div class="col-12 col-md-8">
                            <h5 class="card-title">{{ item.job.title }}</h5>
                            {% if item.job.company %}
                            <p class="card-text"><strong>Company:</strong> {{ item.job.company }}</p>
                            {% endif %}
                            {% if item.job.location %}
                            <p class="card-text"><strong>Location:</strong> {{ item.job.location }}</p>
                            {% endif %}
                            {% if item.job.description %}
                            <p class="card-text"><strong>Description:</strong> {{ item.job.description }}</p>
                            {% endif %}
                            {% if item.job.department %}
                            <p class="card-text"><strong>Department:</strong> {{ item.job.department.name }}</p>
                            {% endif %}
                        </div>
                        <div class="col-12 col-md-4 text-md-end">
                            <h6>Match Score</h6>
                            <div class="d-flex align-items-center justify-content-md-end gap-2 mb-3">
                                <div class="progress flex-grow-1 match-bar-container" style="max-width: 150px;">
                                    <div class="progress-bar bg-success custom-bar" role="progressbar" style="width: {{ item.score }}%;" aria-valuenow="{{ item.score }}" aria-valuemin="0" aria-valuemax="100"></div>
                                </div>
                                <span class="fw-bold fs-5">{{ item.score }}%</span>
                            </div>
                            <form method="post" action="{% url 'apply_to_job' item.job.id %}">
                                {% csrf_token %}
                                <button type="submit" class="btn btn-primary w-100">Apply Now</button>
                            </form>
                        </div>
                    </div>
                    {% if item.missing_skills %}
                    <div class="mt-3">
                        <small class="text-muted">Missing Skills:</small><br>
                        {% for skill in item.missing_skills %}
                            <span class="badge {% if skill.importance >= 4 %}bg-danger{% else %}bg-warning text-dark{% endif %} me-1">{{ skill.name }} ({{ skill.importance }}/5)</span>
                        {% endfor %}
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="alert alert-info" role="alert">
                No job matches found. Try updating your profile or uploading a resume for better results.
            </div>
        {% endif %}
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/apply_success.html': '''{% extends 'base.html' %}

{% block title %}Application Submitted{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-8">
        <div class="card shadow-sm">
            <div class="card-body text-center">
                <h1 class="card-title">Application Submitted!</h1>
                {% if message %}
                <p class="card-text">{{ message }}</p>
                {% endif %}
                <p class="card-text">You have successfully applied for the job: <strong>{{ job.title }}</strong></p>
                <a href="{% url 'match_results' %}" class="btn btn-primary">Back to Job Matches</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/upload.html': '''{% extends 'base.html' %}

{% block title %}Upload Resume{% endblock %}

{% block head %}
<style>
    .upload-card { max-width: 640px; margin: 0 auto; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-8">
        <div class="card shadow-sm upload-card p-4">
            <h1 class="h4 mb-3">Upload Your Resume</h1>
            {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
            {% endif %}
            <form method="post" enctype="multipart/form-data">
                {% csrf_token %}
                <div class="mb-3">
                    <label for="resume" class="form-label">Select Resume (PDF or DOCX):</label>
                    <input type="file" id="resume" name="resume" accept=".pdf,.docx" required class="form-control">
                </div>
                <button type="submit" class="btn btn-success">Upload Resume</button>
            </form>
            <div class="mt-3">
                <a href="{% url 'employee_profile' %}">Back to Profile</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/take_survey.html': '''{% extends 'base.html' %}

{% block title %}Employee Cognitive Survey{% endblock %}

{% block head %}
<style>
    .question { margin-bottom: 1.5rem; }
    .question label { display: block; font-weight: 600; margin-bottom: 0.5rem; }
    .options label { display: inline-block; margin-right: 1rem; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-lg-10">
        <div class="card shadow-sm p-4">
            <h1 class="h4 mb-3">HBDI Cognitive Profile Assessment</h1>
            <p class="text-muted mb-4">Please answer the following questions to assess your cognitive preferences. There are no right or wrong answers.</p>
            <form method="post">
                {% csrf_token %}
                <div class="mb-4">
                    <h2 class="h6">Analytical Thinking</h2>
                    {% for field in form.q1|slice:":5" %}
                        <div class="question">
                            <label>{{ field.label }}</label>
                            <div class="options">{{ field }}</div>
                        </div>
                    {% endfor %}
                </div>
                <div class="mb-4">
                    <h2 class="h6">Practical Thinking</h2>
                    {% for field in form.q6|slice:":5" %}
                        <div class="question">
                            <label>{{ field.label }}</label>
                            <div class="options">{{ field }}</div>
                        </div>
                    {% endfor %}
                </div>
                <div class="mb-4">
                    <h2 class="h6">Relational Thinking</h2>
                    {% for field in form.q11|slice:":5" %}
                        <div class="question">
                            <label>{{ field.label }}</label>
                            <div class="options">{{ field }}</div>
                        </div>
                    {% endfor %}
                </div>
                <div class="mb-4">
                    <h2 class="h6">Experimental Thinking</h2>
                    {% for field in form.q16|slice:":5" %}
                        <div class="question">
                            <label>{{ field.label }}</label>
                            <div class="options">{{ field }}</div>
                        </div>
                    {% endfor %}
                </div>
                <button type="submit" class="btn btn-primary">Submit Survey</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/survey_submitted.html': '''{% extends 'base.html' %}

{% block title %}Survey Complete{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-6">
        <div class="card shadow-sm p-4 text-center">
            <h1 class="h4 mb-3">Success! 🎉</h1>
            <p>Your cognitive profile has been successfully recorded in the HR database.</p>
            <p>Our algorithm is now ready to match you with open job roles based on your unique strengths.</p>
            <a href="{% url 'take_survey' %}" class="btn btn-primary mt-3">Take another survey</a>
        </div>
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/registration/login.html': '''{% extends 'base.html' %}

{% block title %}System Login{% endblock %}

{% block head %}
<style>
    .login-card { max-width: 420px; margin: 0 auto; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center align-items-center min-vh-75">
    <div class="col-12 col-md-6">
        <div class="card shadow-sm login-card p-4">
            <h2 class="h4 text-center mb-3">System Login</h2>
            {% if form.errors %}
                <div class="alert alert-danger">Your username and password didn't match. Please try again.</div>
            {% endif %}
            {% if next %}
                {% if user.is_authenticated %}
                    <div class="alert alert-warning">Your account doesn't have access to this page. To proceed, please login with an account that has access.</div>
                {% else %}
                    <div class="alert alert-info">Please login to see this page.</div>
                {% endif %}
            {% endif %}
            <form method="post" action="{% url 'login' %}">
                {% csrf_token %}
                <div class="mb-3">
                    {{ form.username.label_tag }}
                    {{ form.username }}
                </div>
                <div class="mb-3">
                    {{ form.password.label_tag }}
                    {{ form.password }}
                </div>
                <button type="submit" class="btn btn-primary w-100">Log In</button>
                <input type="hidden" name="next" value="{{ next }}" />
            </form>
            <div class="text-center mt-3">
                <a href="{% url 'password_reset' %}">Forgot your password?</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    'jobs/templates/jobs/job_list.html': '''{% extends 'base.html' %}

{% block title %}Company Job Board{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-lg-10">
        <h1 class="h3 mb-3">Open Job Positions</h1>
        <div class="list-group">
            {% for job in jobs %}
            <div class="list-group-item list-group-item-action mb-2 shadow-sm rounded-3">
                <h5 class="mb-1">{{ job.title }}</h5>
                <p class="mb-1"><strong>Description:</strong> {{ job.description }}</p>
                <p class="mb-0 text-muted">Analytical: {{ job.target_analytical }} | Practical: {{ job.target_practical }}</p>
            </div>
            {% empty %}
            <div class="alert alert-info">No jobs are currently available in the database.</div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
''',
    'jobs/templates/jobs/create_job.html': '''{% extends 'base.html' %}

{% block title %}Create a New Job{% endblock %}

{% block head %}
<style>
    .job-card { max-width: 760px; margin: 0 auto; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-10 col-lg-8">
        <div class="card shadow-sm job-card p-4">
            <h1 class="h4 mb-2">Post a New Job Vacancy</h1>
            <p class="text-muted mb-4">Fill in the job details below so candidates can discover and apply for this opportunity.</p>
            <form method="POST" class="job-form">
                {% csrf_token %}
                {{ form.as_p }}
                <div class="d-flex flex-column flex-md-row gap-2 mt-3">
                    <button type="submit" class="btn btn-primary">Save Job</button>
                    <a href="{% url 'job_list' %}" class="btn btn-outline-secondary">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
''',
    'jobs/templates/jobs/job_applications.html': '''{% extends 'base.html' %}

{% block title %}Job Applications{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-lg-10">
        <h1 class="mb-4">Job Applications</h1>
        {% for job, apps in applications.items %}
        <div class="card mb-4 shadow-sm">
            <div class="card-header">
                <h5 class="mb-1">{{ job.title }}</h5>
                <small class="text-muted">{{ job.company }} - {{ job.location }}</small>
            </div>
            <div class="card-body">
                {% if apps %}
                <ul class="list-group list-group-flush">
                    {% for app in apps %}
                    <li class="list-group-item">
                        <div class="d-flex flex-column flex-md-row justify-content-between align-items-start align-items-md-center gap-3">
                            <div>
                                <strong>{{ app.employee.name }} {{ app.employee.surname }}</strong> ({{ app.employee.username }})
                                <br>
                                <small class="text-muted">Applied on: {{ app.application_date|date:"M d, Y" }}</small>
                                {% if app.employee.resume %}
                                <br>
                                <a href="{{ app.employee.resume.url }}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">View Resume</a>
                                {% endif %}
                            </div>
                        </div>
                    </li>
                    {% endfor %}
                </ul>
                {% else %}
                <p class="text-muted">No applications yet.</p>
                {% endif %}
            </div>
        </div>
        {% empty %}
        <div class="alert alert-info">No jobs available.</div>
        {% endfor %}
    </div>
</div>
{% endblock %}
''',
    'accounts/templates/accounts/create_employee_profile.html': '''{% extends 'base.html' %}

{% block title %}Create Employee Profile{% endblock %}

{% block head %}
<style>
    .form-section { margin-bottom: 1.75rem; }
    .form-group label { font-weight: 600; }
    .error { color: #c92a2a; margin-top: 0.5rem; }
</style>
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12 col-md-8">
        <div class="card shadow-sm p-4 mb-4">
            <h1 class="h3 mb-3">Create Your Employee Profile</h1>
            <p class="text-muted">Complete your profile information to get started with job matching.</p>
            <hr>
            <form method="POST">
                {% csrf_token %}

                <div class="form-section">
                    <h2 class="h5">Personal Information</h2>
                    <div class="mb-3">
                        <label for="id_name" class="form-label">{{ form.name.label }}</label>
                        {{ form.name }}
                        {% if form.name.errors %}
                            <div class="error">{{ form.name.errors }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_surname" class="form-label">{{ form.surname.label }}</label>
                        {{ form.surname }}
                        {% if form.surname.errors %}
                            <div class="error">{{ form.surname.errors }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_birth_date" class="form-label">{{ form.birth_date.label }}</label>
                        {{ form.birth_date }}
                        {% if form.birth_date.errors %}
                            <div class="error">{{ form.birth_date.errors }}</div>
                        {% endif %}
                    </div>
                </div>

                <div class="form-section">
                    <h2 class="h5">Contact Information</h2>
                    <div class="mb-3">
                        <label for="id_username" class="form-label">{{ form.username.label }}</label>
                        {{ form.username }}
                        {% if form.username.errors %}
                            <div class="error">{{ form.username.errors }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_email" class="form-label">{{ form.email.label }}</label>
                        {{ form.email }}
                        {% if form.email.errors %}
                            <div class="error">{{ form.email.errors }}</div>
                        {% endif %}
                    </div>
                    <div class="mb-3">
                        <label for="id_location" class="form-label">{{ form.location.label }}</label>
                        {{ form.location }}
                        {% if form.location.errors %}
                            <div class="error">{{ form.location.errors }}</div>
                        {% endif %}
                    </div>
                </div>

                <div class="form-section">
                    <h2 class="h5">About You</h2>
                    <div class="mb-3">
                        <label for="id_bio" class="form-label">{{ form.bio.label }}</label>
                        {{ form.bio }}
                        {% if form.bio.errors %}
                            <div class="error">{{ form.bio.errors }}</div>
                        {% endif %}
                    </div>
                </div>

                <button type="submit" class="btn btn-primary">Create Profile</button>
            </form>
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
