from django.contrib import admin
from .models import Skill, Job, Department, JobSkillRequirement, JobEmployeeCompatibility

# Register your models here.
admin.site.register(Skill)
#admin.site.register(Job)
admin.site.register(Department)
admin.site.register(JobSkillRequirement)
admin.site.register(JobEmployeeCompatibility)



# This allows you to edit skills directly inside the Job page
class SkillInline(admin.TabularInline):
    model = JobSkillRequirement
    extra = 1

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    inlines = [SkillInline]