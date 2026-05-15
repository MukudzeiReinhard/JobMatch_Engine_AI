from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True) # Unique prevents duplicates
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Department(models.Model):

    name = models.CharField(max_length=100, unique=True)
    analytical_weight = models.FloatField(default=0.25)
    practical_weight = models.FloatField(default=0.25)
    relational_weight = models.FloatField(default=0.25)
    experimental_weight = models.FloatField(default=0.25)  

    def __str__(self):

        return self.name


class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100, default='')
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    # Link directly to skills here
    required_skills = models.ManyToManyField(Skill, related_name='jobs', through= "JobSkillRequirement")
    # Cognitive Scores
    target_analytical = models.IntegerField(default=0)
    target_practical = models.IntegerField(default=0)
    target_relational = models.IntegerField(default=0)
    target_experimental = models.IntegerField(default=0)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class JobSkillRequirement(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey('Skill', on_delete=models.CASCADE)
    importance = models.IntegerField(default=1) # 1 = Low, 5 = Critical
    
    def __str__(self):
        return f"{self.job.title} - {self.skill.name} (Importance: {self.importance})"


# a class that stores the compatibility score between a job and an employee,
#  to be used in the recommendation engine
# we will use this class for recruiters to see how well a candidate matches a job, and for candidates to see how well they match a job
class JobEmployeeCompatibility(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey('accounts.employee_account', on_delete=models.CASCADE)
    compatibility_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.employee.username} - {self.job.title} (Compatibility: {self.compatibility_score:.2f})"
    
class JobApplications(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    employee = models.ForeignKey('accounts.employee_account', on_delete=models.CASCADE)
    application_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} applied for {self.job.title} on {self.application_date.strftime('%Y-%m-%d')}"