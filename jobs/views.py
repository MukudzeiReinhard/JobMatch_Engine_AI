from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView
from .forms import JobEntryForm
from .models  import  Job, JobEmployeeCompatibility, JobApplications
from accounts.models import employee_account


# this view will display a list of all the jobs in the database.
#  It will use the Job model to retrieve all the job entries and pass them to the template for rendering. 
# The template will loop through the job entries and display their details such as title, description, skills, company name, and location. 
# This view will be accessible via a URL pattern that maps to it, allowing users to see the list of available jobs on the website.
# on the  template remember to show skills, link for application, and abstract target cognitive scores for the recommendation engine from normal users.
def job_list(request):
    all_jobs = Job.objects.all()
    user_role = None
    is_hr = False
    is_employee = False

    if request.user.is_authenticated:
        try:
            user_role = request.user.employee_account.role
            is_hr = user_role == employee_account.IS_HR
            is_employee = user_role == employee_account.IS_EMPLOYEE
        except (AttributeError, employee_account.DoesNotExist):
            pass

    context = {
        'jobs': all_jobs,
        'user_role': user_role,
        'is_hr': is_hr,
        'is_employee': is_employee,
    }
    return render(request, 'jobs/job_list.html', context)

# a form on a job that is submitted to the database and will display job list if invalid and a success message if valid.
#  The form should include fields for job title, description, skills, company name, location, and user.
#  The form should also have a submit button that will save the job entry to the database when clicked.
#  After submission, the user should be redirected to the job list page where they can see all the job entries including the one they just submitted.
@login_required
def create_job(request):
    if request.user.employee_account.role != employee_account.IS_HR:
        raise PermissionDenied
    if request.method == "POST":
        form = JobEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('job_list')
        else:
           print(form.errors)
    else:
        form = JobEntryForm()
    return render(request, "jobs/create_job.html", {"form": form})


# the view will take all the employee accounts and all the jobs. 
# for each job in the system, it will calculate the compatibility score for each employee based on their skills and cognitive scores.
# it will list the jobs and for each job, it will list the potential candidates sorted by their compatibility score in descending order. 

class PotentialCandidatesView(LoginRequiredMixin, ListView):
    model = JobEmployeeCompatibility
    template_name = 'jobs/potential_candidates.html'
    context_object_name = 'jobs'

    def dispatch(self, request, *args, **kwargs):
        try:
            if request.user.employee_account.role != employee_account.IS_HR:
                raise PermissionDenied("Access denied")
        except (AttributeError, employee_account.DoesNotExist):
            raise PermissionDenied("Access denied")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        active_jobs = Job.objects.all()
        top_candidates = []

        for job in active_jobs:
            # Exclude candidates who have the HR role
            candidates = JobEmployeeCompatibility.objects.filter(job=job).exclude(
                employee__role=employee_account.IS_HR
            ).order_by('-compatibility_score')[:5]
            top_candidates.extend(list(candidates))

        return top_candidates


# View to show job applications for recruiters
@login_required
def job_applications(request):
    try:
        if request.user.employee_account.role != employee_account.IS_HR:
            raise PermissionDenied("Access denied")
    except (AttributeError, employee_account.DoesNotExist):
        raise PermissionDenied("Access denied")

    jobs = Job.objects.all()
    applications = {}
    for job in jobs:
        apps = JobApplications.objects.filter(job=job).select_related('employee')
        applications[job] = apps
    context = {'applications': applications}
    return render(request, 'jobs/job_applications.html', context)

@login_required
def delete_job(request, job_id):
    user = request.user
    try:
        if user.employee_account.role != employee_account.IS_HR:
            raise PermissionDenied("Request Denied")
    except (AttributeError, employee_account.DoesNotExist):
        raise PermissionDenied("Request Denied")

    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        job.delete()
        return redirect('job_list')

    return render(request, 'jobs/delete_job.html', {'job': job})

   