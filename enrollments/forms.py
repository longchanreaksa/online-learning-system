from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Enrollment

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['course']
        labels = {
            'course': _('Select Course')
        }
        widgets = {
            'course': forms.Select(attrs={'class': 'form-select'})
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['grade']
        labels = {
            'grade': _('Grade (0-100)')
        }
        widgets = {
            'grade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.01'
            })
        }