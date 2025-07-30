from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from courses.models import Course
from .models import Enrollment, Progress
from .forms import EnrollmentForm, GradeForm

@login_required
def enroll_course(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    student = request.user.student_profile
    
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.warning(request, _('You are already enrolled in this course'))
        return redirect('courses:course_detail', slug=course.slug)

    
    Enrollment.objects.create(student=student, course=course)
    messages.success(request, _('Successfully enrolled in %(course)s') % {'course': course.title})
    return redirect('student_dashboard')

@login_required
def course_progress(request, enrollment_id):
    enrollment = get_object_or_404(
        Enrollment,
        pk=enrollment_id,
        student=request.user.student_profile
    )
    
    progress_records = enrollment.progress_records.select_related('lesson').order_by('lesson__order')
    
    context = {
        'enrollment': enrollment,
        'progress_records': progress_records,
    }
    return render(request, 'enrollments/progress.html', context)

class EnrollmentListView(ListView):
    model = Enrollment
    template_name = 'enrollments/enrollment_list.html'
    context_object_name = 'enrollments'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student_profile'):
            return Enrollment.objects.filter(student=self.request.user.student_profile)
        elif hasattr(self.request.user, 'instructor_profile'):
            return Enrollment.objects.filter(course__instructor=self.request.user.instructor_profile)
        return Enrollment.objects.none()

class UpdateGradeView(UpdateView):
    model = Enrollment
    form_class = GradeForm
    template_name = 'enrollments/update_grade.html'
    success_url = reverse_lazy('instructor_dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Grade updated successfully'))
        return response