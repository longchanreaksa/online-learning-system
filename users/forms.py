
from django import forms
from django.contrib.auth import get_user_model
from .models import Profile, Student, Instructor, Employee

from .models import Instructor

User = get_user_model()

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    profile_photo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        help_text='Upload a profile picture'
    )
    
    class Meta:
        model = Profile
        fields = ['profile_photo']

class StudentProfileUpdateForm(ProfileUpdateForm):
    
    class Meta(ProfileUpdateForm.Meta):
        model = Student
        fields = ProfileUpdateForm.Meta.fields

class InstructorProfileUpdateForm(ProfileUpdateForm):
    
    class Meta:
        model = Instructor
        fields = ['profile_photo']  
        widgets = {
            'profile_photo': forms.FileInput(attrs={'class': 'form-control'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['profile_photo'].required = False

class EmployeeProfileUpdateForm(ProfileUpdateForm):
    
    class Meta(ProfileUpdateForm.Meta):
        model = Employee
        fields = ProfileUpdateForm.Meta.fields

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(
        label='Confirm password', 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.Role.choices,
        label="Account Type",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'password', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = self.cleaned_data['role']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            if user.role == 'student':
                Student.objects.create(user=user)
            elif user.role == 'instructor':
                Instructor.objects.create(user=user)
            elif user.role == 'employee':
                Employee.objects.create(user=user)
        return user