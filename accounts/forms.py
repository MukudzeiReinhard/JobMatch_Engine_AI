from django import forms
from .models import employee_account

class UserProfileAccountForm(forms.ModelForm):
    class Meta:
        model = employee_account
        # List ONLY the fields the employee should fill out themselves
        fields = [
            'name', 'surname',
            'username', 'email',
            'location', 'birth_date',
            'bio', 
            #'target_analytical', 
            #'target_practical', 
            #'target_relational', 
            #'target_experimental'

        ]
        '''# Optional: Add 'widgets' to make the scores look like number boxes
        widgets = {
            'target_analytical': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'target_practical': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'target_relational': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'target_experimental': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }'''

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date == '':
            return None
        return birth_date
    
CHOICES = [
    (1, 'Strongly Disagree'),
    (2, 'Disagree'),
    (3, 'Neutral'),
    (4, 'Agree'),
    (5, 'Strongly Agree'),
]

class HBIForm(forms.Form):
   # Analytical
   q1 = forms.TypedChoiceField(label='I prefer to use cold, hard facts rather than intuition when making a professional decision.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q2 = forms.TypedChoiceField(label='I am comfortable analyzing complex numerical data or financial spreadsheets.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q3 = forms.TypedChoiceField(label='I enjoy solving technical problems that require deep critical thinking and logic.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q4 = forms.TypedChoiceField(label='I value precision and accuracy above all else when completing a task.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q5 = forms.TypedChoiceField(label='I like to understand exactly how a system works from a mechanical or structural perspective.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   # Practical
   q6 = forms.TypedChoiceField(label='I feel most productive when I have a detailed "to-do" list or a strict schedule to follow.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q7 = forms.TypedChoiceField(label='I prefer tasks that have a clear, step-by-step procedure already established.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q8 = forms.TypedChoiceField(label='I pay close attention to small details that others in the team might overlook.', choices=CHOICES, coerce=int, widget=forms.RadioSelect) 
   q9 = forms.TypedChoiceField(label='I value stability, consistency, and a predictable routine in my working environment.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q10 = forms.TypedChoiceField(label='I make sure my workspace and digital files are organized in a systematic, orderly way.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   # Relational
   q11 = forms.TypedChoiceField(label='I believe that team harmony and morale are more important than meeting a pure efficiency target.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q12 = forms.TypedChoiceField(label='I am highly sensitive to the feelings and moods of the people I work with.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q13 = forms.TypedChoiceField(label='I find great satisfaction in teaching, coaching, or supporting the development of others.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q14 = forms.TypedChoiceField(label='I prefer to communicate through personal discussion and face-to-face meetings rather than formal reports.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q15 = forms.TypedChoiceField(label='I am often praised for being an empathetic listener and considering the "human element" of a project.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   # Experimental
   q16 = forms.TypedChoiceField(label='I enjoy brainstorming "big picture" ideas even if they are not immediately practical or realistic.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q17 = forms.TypedChoiceField(label='I am comfortable taking calculated risks to try a completely new way of doing things.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q18 = forms.TypedChoiceField(label='I find it easy to imagine how a project or a company will look five to ten years into the future.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q19 = forms.TypedChoiceField(label='I frequently use metaphors, analogies, or visual illustrations to explain my thoughts to others.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)
   q20 = forms.TypedChoiceField(label='I get bored with repetitive routines and prefer to work on varied, fast-changing projects.', choices=CHOICES, coerce=int, widget=forms.RadioSelect)             