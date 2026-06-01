from django.db import models
from django.contrib.auth.models import User
#from jobs.models import Department
from jobs.models import Skill
from .validators import validate_resume_size_and_type

# Create your models here.
class employee_account (models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    IS_HR = 'HR'
    IS_EMPLOYEE = 'EMPLOYEE'
    ROLE_CHOICES = [
        (IS_HR, 'HR'),
        (IS_EMPLOYEE, 'Employee')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=IS_EMPLOYEE)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True, validators=[validate_resume_size_and_type])
    uploaded_at = models.DateTimeField(null= True, blank=True)
    cv_text = models.TextField(blank=True, null=True)  # Field to store extracted text from the resume
    skills_list = models.TextField(blank=True, null=True)  # Field to store extracted skills from the resume
    #department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    #cognitive scores for the recommendation engine
    target_analytical = models.IntegerField(default=0)
    target_practical = models.IntegerField(default=0)
    target_relational = models.IntegerField(default=0)
    target_experimental = models.IntegerField(default=0)
    #compatibility_score = models.FloatField(default=0.0) # This will be calculated based on the job requirements and the employee's skills and cognitive scores

    def __str__(self):
        return self.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    

    #password = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username or 'Unknown User'
'''    
class employee_competency(models.Model):
    employee = models.ForeignKey(employee_account, on_delete=models.CASCADE)
    skills = models.ManyToManyField(Skill, blank=True)
    tools = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.employee.user.username} - {self.skills}: {self.tools}"
''' 
    #name = models.CharField(max_length=100)
    #surname = models.CharField(max_length=100)
    #username = models.CharField(max_length=100, unique=True)
    #email = models.EmailField(unique=True)

