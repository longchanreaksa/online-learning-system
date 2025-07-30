from django import forms
from django.contrib.auth import get_user_model
from profiles.models import VerificationSubmission
from users.models import Student, Instructor, Employee

User = get_user_model()

class BaseProfileForm(forms.ModelForm):
    profile_photo = forms.ImageField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        fields = ['profile_photo',]

class StudentProfileForm(BaseProfileForm):

    class Meta(BaseProfileForm.Meta):
        model = Student
        fields = BaseProfileForm.Meta.fields

class InstructorProfileForm(BaseProfileForm):
    specialization = forms.CharField(max_length=100, required=True)
    qualifications = forms.CharField(widget=forms.Textarea, required=True)

    class Meta(BaseProfileForm.Meta):
        model = Instructor
        fields = BaseProfileForm.Meta.fields + ['specialization', 'qualifications']

class EmployeeProfileForm(BaseProfileForm):
    class Meta(BaseProfileForm.Meta):
        model = Employee
        fields = BaseProfileForm.Meta.fields

class ProfilePhotoForm(forms.Form):
    profile_photo = forms.ImageField(required=False)
    remove_photo = forms.BooleanField(required=False)

class VerificationForm(forms.ModelForm):
    class Meta:
        model = VerificationSubmission
        fields = ['document', 'message']