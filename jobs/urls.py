from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('create/', views.create_job, name='create_job'),
    path('potential_candidates/', views.PotentialCandidatesView.as_view(), name='potential_candidates'),
    path('applications/', views.job_applications, name='job_applications'),
    path('delete/<int:job_id>/', views.delete_job, name='delete_job'),
]