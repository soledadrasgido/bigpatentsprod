from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    
    class Meta:
        model = Project
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Título'}),
            'description': forms.Textarea(attrs={'class':'form-control'}),
        }
        labels = {
            'title':'', 'description': ''
        }