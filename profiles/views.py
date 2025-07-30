from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, UpdateView, DetailView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django import forms

# Local imports
from .models import VerificationSubmission
from .forms import (
    StudentProfileForm,
    InstructorProfileForm,
    EmployeeProfileForm,
    ProfilePhotoForm,
    VerificationForm
)

# Get models from users app
try:
    from users.models import Student, Instructor, Employee
except ImportError:
    Student = None
    Instructor = None
    Employee = None

class ProfileTypeDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if hasattr(request.user, 'student_profile'):
            return redirect('profiles:student_dashboard')
        elif hasattr(request.user, 'instructor_profile'):
            return redirect('profiles:instructor_dashboard')
        elif hasattr(request.user, 'employee_profile'):
            return redirect('profiles:employee_dashboard')
        
        messages.error(request, 'No valid profile type found')
        return redirect('login')

class DashboardView(LoginRequiredMixin, ProfileTypeDispatchMixin, TemplateView):
    template_name = 'profiles/dashboard/base.html'

class StudentDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard/student.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'student_profile'):
            messages.error(request, 'Access restricted to students')
            return redirect('profiles:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user.student_profile
        context['student'] = student
        return context

class InstructorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard/instructor.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'instructor_profile'):
            messages.error(request, 'Access restricted to instructors')
            return redirect('profiles:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instructor = self.request.user.instructor_profile
        context['instructor'] = instructor
        return context

class EmployeeDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'profiles/dashboard/employee.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'employee_profile'):
            messages.error(request, 'Access restricted to employees')
            return redirect('profiles:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = self.request.user.employee_profile
        context['employee'] = employee
        return context

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'profiles/edit_profile.html'
    success_url = reverse_lazy('profiles:dashboard')

    def get_object(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return user.student_profile
        elif hasattr(user, 'instructor_profile'):
            return user.instructor_profile
        elif hasattr(user, 'employee_profile'):
            return user.employee_profile
        raise Http404("Profile not found")

    def get_form_class(self):
        profile = self.get_object()
        if hasattr(profile, 'academic_level'):
            return StudentProfileForm
        elif hasattr(profile, 'specialization'):
            return InstructorProfileForm
        elif hasattr(profile, 'department'):
            return EmployeeProfileForm
        return forms.ModelForm

class PublicProfileView(DetailView):
    template_name = 'profiles/public_profile.html'
    context_object_name = 'profile'

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        for model in [Student, Instructor, Employee]:
            try:
                return model.objects.get(user__id=user_id)
            except (model.DoesNotExist, AttributeError):
                continue
        raise Http404("Profile not found")

class ProfilePhotoUpdateView(LoginRequiredMixin, FormView):
    template_name = 'profiles/edit_photo.html'
    form_class = ProfilePhotoForm
    success_url = reverse_lazy('profiles:edit_profile')

    def form_valid(self, form):
        profile = self.get_profile()
        if form.cleaned_data.get('remove_photo'):
            profile.profile_photo.delete()
        elif form.cleaned_data.get('profile_photo'):
            profile.profile_photo = form.cleaned_data['profile_photo']
            profile.save()
        messages.success(self.request, "Profile photo updated!")
        return super().form_valid(form)

    def get_profile(self):
        user = self.request.user
        if hasattr(user, 'student_profile'):
            return user.student_profile
        elif hasattr(user, 'instructor_profile'):
            return user.instructor_profile
        return user.employee_profile

class VerificationRequestView(LoginRequiredMixin, FormView):
    template_name = 'profiles/verification_request.html'
    form_class = VerificationForm
    success_url = reverse_lazy('profiles:dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'instructor_profile'):
            messages.error(request, "Only instructors can submit verification")
            return redirect('profiles:dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        verification = form.save(commit=False)
        verification.instructor = self.request.user.instructor_profile
        verification.status = 'pending'
        verification.save()
        messages.success(self.request, "Verification request submitted!")
        return super().form_valid(form)