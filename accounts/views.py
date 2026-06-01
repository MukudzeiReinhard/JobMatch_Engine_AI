import io
import json
import logging
import os

from django.http import Http404, FileResponse
import fitz
from docx import Document
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View

from . import skills_extraction
from .forms import HBIForm, UserProfileAccountForm
from .models import employee_account
from .validators import validate_resume_size_and_type
from jobs.models import Job, JobEmployeeCompatibility, JobApplications

logger = logging.getLogger(__name__)

# Create your views here.
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            employee_account.objects.create(
                user=user,
                username=user.username,
                email=user.email or None,
                name=user.first_name or '',
                surname=user.last_name or ''
            )
            authenticated_user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            if authenticated_user is not None:
                login(request, authenticated_user)
                return redirect('create_employee_profile')
            return render(request, 'accounts/signup.html', {
                'form': form,
                'error': 'Authentication failed after signup. Please log in manually.'
            })
    else:
        form = UserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

#TODO: in the employee profile add a button to take the survey, and a button to upload a resume. The survey should be a form that allows the employee to input their cognitive scores, and save them to their profile. The matched jobs page should also show the top 5 matching jobs based on the cognitive scores, and a button to view the details of each job. The job details page should show the job description, required skills, company name, location, and a button to apply for the job. The apply button should redirect to a page where the employee can submit their application for the job, and upload their resume if they haven't already. The application page should also show the job description and required skills for reference.  
@login_required
def employee_profile(request):
    current_user_employee = request.user.employee_account
    top_jobs = Job.objects.all()  # Get the 5 most recent active jobs


    context = {
        'employee': current_user_employee,
        'top_jobs': top_jobs
    }
    return render(request, 'accounts/employee_profile.html', context)

@login_required
def hr_dashboard(request):
    try:
        profile = request.user.employee_account
    except (AttributeError, employee_account.DoesNotExist):
        raise PermissionDenied("Access denied")

    if profile.role != employee_account.IS_HR:
        raise PermissionDenied("Access denied")

    context = {
        'employee': profile,
    }
    return render(request, 'accounts/hr_dashboard.html', context)

# create a view that will allow the logged-in employee to upload their resume, 
# and use the cv_extraction.py module to extract the text from the resume and save it to the employee's profile. 
# This will be used to match the employee to jobs based on the skills and experience listed in their resume.

class ResumeUploadView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'accounts/upload.html')

    def post(self, request):
        resume_file = request.FILES.get('resume')
        
        if not resume_file:
            return render(request, 'accounts/upload.html', {'error': 'No file uploaded.'})

        try:
            # 1. Validate file using validator function (size, format, integrity)
            try:
                validate_resume_size_and_type(resume_file)
            except ValidationError as ve:
                return render(request, 'accounts/upload.html', {'error': str(ve)})

            # 2. Extract text based on file type
            resume_file.seek(0)
            file_content = resume_file.read()
            file_name = resume_file.name.lower()
            text = ""
            
            if file_name.endswith('.pdf'):
                try:
                    doc = fitz.open(stream=file_content, filetype='pdf')
                    text = ' '.join([page.get_text() for page in doc])
                    doc.close()
                except Exception as e:
                    logger.exception('PDF parsing error')
                    return render(request, 'accounts/upload.html', {
                        'error': 'Failed to read PDF. Please ensure it is a valid PDF file.'
                    })
            elif file_name.endswith('.docx'):
                try:
                    docx_file = io.BytesIO(file_content)
                    doc = Document(docx_file)
                    text = ' '.join([para.text for para in doc.paragraphs])
                except Exception as e:
                    logger.exception('DOCX parsing error')
                    return render(request, 'accounts/upload.html', {
                        'error': 'Failed to read DOCX. Please ensure it is a valid Word document.'
                    })
            else:
                return render(request, 'accounts/upload.html', {
                    'error': 'Unsupported file format. Please upload a PDF or DOCX file.'
                })

            if not text.strip():
                return render(request, 'accounts/upload.html',
                            {'error': 'The uploaded file contains no readable text. Please try another resume.'})

            # 3. Wrap DB transaction and Gemini API call
            with transaction.atomic():
                emp_acc = request.user.employee_account
                
                # Call Gemini API to extract skills
                try:
                    skills = skills_extraction.extract_skills_with_gemini(text)
                    if not isinstance(skills, list):
                        skills = [s.strip() for s in str(skills).split(',') if s.strip()]
                    skills = [s for s in skills if s.strip()]

                    if not skills:
                        return render(request, 'accounts/upload.html', {
                            'error': 'No skills were extracted from the resume. Please upload a different resume or improve the document quality.'
                        })
                except Exception as e:
                    logger.exception('Gemini API error')
                    error_text = str(e) or 'Unknown skill extraction error.'
                    return render(request, 'accounts/upload.html', {
                        'error': f'Failed to extract skills from resume: {error_text}'
                    })
                
                # Save to database
                emp_acc.resume = resume_file
                emp_acc.cv_text = text
                emp_acc.skills_list = ', '.join(skills).lower() if skills else ''
                emp_acc.save()

            return render(request, 'accounts/upload.html', {
                'success': 'Resume uploaded successfully! Your skills have been extracted.'
            })

        except Exception:
            logger.exception('Resume upload error')
            return render(request, 'accounts/upload.html', {
                'error': 'An unexpected error occurred. Please try again.'
            })
        
# This view is HR-only and should only be visible to authorized users.
@login_required
def employee_list(request):
    try:
        profile = request.user.employee_account
    except (AttributeError, employee_account.DoesNotExist):
        raise PermissionDenied("Access denied")

    if profile.role != employee_account.IS_HR:
        raise PermissionDenied("Access denied")

    all_accounts = employee_account.objects.all()
    return render(request, 'accounts/create_account.html', {'accounts': all_accounts})
# ----------- change into initial data collectioin for profile creation----------- 
@login_required
def create_employee_profile(request):
    profile, created = employee_account.objects.get_or_create(user=request.user)  # Ensure the profile exists for the current user

    if request.method == 'POST':
        form = UserProfileAccountForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('employee_profile')  # Redirect to the profile page after saving
    else:
            #print(form.errors)
        form = UserProfileAccountForm(instance=profile)  # Re-instantiate the form to clear it after a failed POST
    return render(request, 'accounts/create_profile.html', {'form': form})  # Re-render the form with errors
# New view for taking the survey and saving the cognitive scores to the employee profile. This will be linked from the employee profile page, and will allow the employee to input their cognitive scores for analytical, practical, relational, and experimental skills. The scores will be saved to the employee's profile and used for job matching.
@login_required
def take_survey(request):
    profile, created = employee_account.objects.get_or_create(user=request.user)  # Ensure the profile exists for the current user

    if request.method == 'POST':
        form = HBIForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            analytical = (data['q1'] + data['q2'] + data['q3'] + data['q4'] + data['q5']) * 4
            practical = (data['q6'] + data['q7'] + data['q8'] + data['q9'] + data['q10']) * 4
            relational = (data['q11'] + data['q12'] + data['q13'] + data['q14'] + data['q15']) * 4
            experimental = (data['q16'] + data['q17'] + data['q18'] + data['q19'] + data['q20']) * 4

            profile.target_analytical = analytical
            profile.target_practical = practical
            profile.target_relational = relational
            profile.target_experimental = experimental
            profile.save()
            return redirect('employee_profile')
    else:
        form = HBIForm()  # Show blank form on GET

    return render(request, 'accounts/take_survey.html', {'form': form})  
#

def survey_submitted(request):
    return render(request, 'accounts/survey_submitted.html')

# @login_required
# def match_employee(request):
#     current_user_employee = request.user.employee_account  # Get the employee account associated with the current user
#     available_jobs = Job.objects.all()
    
#     scores = []

#     for job in available_jobs:

#         analytical_score_gap = abs(current_user_employee.target_analytical - job.target_analytical)
#         practical_score_gap = abs(current_user_employee.target_practical - job.target_practical)
#         relational_score_gap= abs(current_user_employee.target_relational - job.target_relational)
#         experimental_score_gap = abs(current_user_employee.target_experimental - job.target_experimental)

#         total_score_gap = analytical_score_gap + practical_score_gap + relational_score_gap + experimental_score_gap
#         match_percentage = (1 - total_score_gap/400) * 100
#         scores.append((job, match_percentage))

#     scores.sort(key=lambda x: x[1], reverse=True)
#     if scores:
#         best_match_tuple = scores[0] #if scores else None
#         context = {
#             'employee': current_user_employee,
#             'best_match': best_match_tuple[0], # The job itself
#             'match_score': best_match_tuple[1], # The percentage score
#             'no_jobs': False,
#         }
#     else:
#         context = {
#             'employee': current_user_employee,
#             'best_match': None,
#             'match_score': 0,
#             'no_jobs': True,
#         }
#     return render(request, 'accounts/match_employee.html', context)

@login_required
def edit_employee_profile(request):
    employee_profile = request.user.employee_account
    if request.method == 'POST':
        form = UserProfileAccountForm(request.POST, instance=employee_profile)
        if form.is_valid():
            form.save()
            return redirect('employee_profile')
        else:
            return render(request, 'accounts/edit_employee_profile.html', {'form': form})
    else:
        form = UserProfileAccountForm(instance=employee_profile)  # Pre-fill the form with existing data
    return render(request, 'accounts/edit_employee_profile.html', {'form': form})

#This view will take the employee's cognitive scores and the text extracted from their resume, and match them to the available jobs in the system. 
#The matching algorithm will consider both the cognitive score gaps and the presence of required skills in the resume text.
#The results will be displayed on a new page, showing the matched jobs along with their match scores and any missing skills that the employee may want to acquire to improve their chances for those jobs.
class JobMatchView(LoginRequiredMixin, View):
    def get(self, request):
        user_emp = request.user.employee_account
        
        # Check if survey is completed (all cognitive scores > 0)
        survey_completed = (
            user_emp.target_analytical > 0 and
            user_emp.target_practical > 0 and
            user_emp.target_relational > 0 and
            user_emp.target_experimental > 0
        )
        resume_exists = bool(user_emp.resume)
        
        available_jobs = Job.objects.all().prefetch_related('jobskillrequirement_set__skill')
        results = []

        # Load training recommendations
        training_file_path = os.path.join(os.path.dirname(__file__), 'training_recomendations.json')
        try:
            with open(training_file_path, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning('Unable to load training recommendations: %s', e)
            training_data = {'training_recommendations': []}

        training_dict = {item['skill'].lower(): item['courses'] for item in training_data.get('training_recommendations', [])}
        user_skills = {skill.strip().lower() for skill in (user_emp.skills_list or '').split(',') if skill.strip()}

        for job in available_jobs:
            dept = job.department
            if dept is None:
                # Use default weights if no department
                analytical_w = 0.25
                practical_w = 0.25
                relational_w = 0.25
                experimental_w = 0.25
            else:
                analytical_w = dept.analytical_weight
                practical_w = dept.practical_weight
                relational_w = dept.relational_weight
                experimental_w = dept.experimental_weight

            # --- COGNITIVE SCORE (Weighted) ---
            cog_gap = (
                abs(user_emp.target_analytical - job.target_analytical) * analytical_w +
                abs(user_emp.target_practical - job.target_practical) * practical_w +
                abs(user_emp.target_relational - job.target_relational) * relational_w +
                abs(user_emp.target_experimental - job.target_experimental) * experimental_w
            )
            cog_match = max(0, 100 - cog_gap) # Convert gap to a match percentage (100% = perfect match, 0% = very poor match)

            # --- SKILL SCORE (Importance Weighting) ---
            requirements = job.jobskillrequirement_set.all()
            total_job_weight = 0
            user_earned_weight = 0
            missing_trainings = []

            for req in requirements:
                total_job_weight += req.importance
                skill_name_lower = req.skill.name.strip().lower()
                if skill_name_lower in user_skills:
                    user_earned_weight += req.importance
                else:
                    trainings = training_dict.get(skill_name_lower, [])
                    if trainings:
                        missing_trainings.append({
                            'skill_name': req.skill.name,
                            'importance': req.importance,
                            'courses': trainings
                        })

            skill_match_score = (user_earned_weight / total_job_weight * 100) if total_job_weight > 0 else 100
            
            # Final Compound Score (60% Skills, 40% Cognitive) 
            final_score = (skill_match_score * 0.6) + (cog_match * 0.4)

            # Save each job-employee compatibility score to database
            JobEmployeeCompatibility.objects.update_or_create(
                job=job,
                employee=user_emp,
                defaults={'compatibility_score': final_score}
            )

            if final_score >= 30:
                results.append({
                    'job': job,  
                    'score': round(final_score, 1),
                    'missing_trainings': missing_trainings
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return render(request, 'accounts/match_results.html', {
            'results': results,
            'resume_exists': resume_exists,
            'survey_completed': survey_completed
        })

# A simple View to handle the 'Apply' action
class ApplyJobView(LoginRequiredMixin, View):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        employee = request.user.employee_account
        
        # Check if already applied
        if JobApplications.objects.filter(job=job, employee=employee).exists():
            return render(request, 'accounts/apply_success.html', {'job': job, 'message': 'You have already applied for this job.'})
        
        # Create application
        JobApplications.objects.create(job=job, employee=employee)
        
        return render(request, 'accounts/apply_success.html', {'job': job, 'message': 'Application submitted successfully!'})
    
#TODO: improve the security of the resume download by ensuring that only authorized users can access the resume files, and that the files are served securely without exposing the file system structure. Consider using Django's FileResponse to serve the files and implementing proper access controls to prevent unauthorized access.
class SecureResumeDownloadView(LoginRequiredMixin, View):
    def get(self, request, account_id):
        try:
            # Fetch the requested profile
            emp_acc = get_object_or_404(employee_account, id=account_id)
            
            # --- AUTHORIZATION RULE LAYER ---
            # Check if the requester is the owner OR an authorized HR recruiter
            is_owner = request.user == emp_acc.user
            is_hr = getattr(request.user, 'employee_account', None) and request.user.employee_account.role == 'HR'
            
            if not (is_owner or is_hr):
                raise Http404("You do not have permission to view this resume.")
                
            if not emp_acc.resume:
                raise Http404("No resume uploaded.")

            # Open and serve the file securely from the protected directory
            return FileResponse(emp_acc.resume.open('rb'), content_type='application/pdf')

        except employee_account.DoesNotExist:
            raise Http404("Profile not found.")
