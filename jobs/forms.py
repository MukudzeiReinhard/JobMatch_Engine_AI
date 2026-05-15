from django import forms
from .models import Job

class JobEntryForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'company', 'location', 'target_analytical',
                   'target_practical', 'target_relational', 'target_experimental']