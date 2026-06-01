from django.urls import path
from . import views
from .views import SecureResumeDownloadView

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('create-profile/', views.create_employee_profile, name='create_employee_profile'),
    path('edit-profile/', views.edit_employee_profile, name='edit_employee_profile'),
    #path('employee_profile/', views.EmployeeProfileView.as_view(), name='employee_profile'),
    path('list/', views.employee_list, name='employee_list'),
    path('survey/', views.take_survey, name='take_survey'),
    path('survey-submitted/', views.survey_submitted, name='survey_submitted'),
    path('match-results/', views.JobMatchView.as_view(), name='match_results'),
    path('employee_profile/', views.employee_profile, name='employee_profile'),
    path('hr-dashboard/', views.hr_dashboard, name='hr_dashboard'),
    path('apply/<int:job_id>/', views.ApplyJobView.as_view(), name='apply_to_job'),
    path('upload/', views.ResumeUploadView.as_view(), name='upload_resume'),
    path('resumes/download/<int:account_id>/', SecureResumeDownloadView.as_view(), name='download_resume'),

    ]