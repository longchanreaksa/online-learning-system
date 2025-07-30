from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Course, Lesson, Review, CourseProgress
from .forms import CourseForm, LessonForm, ReviewForm
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied

class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10

    def get_queryset(self):
        queryset = Course.objects.filter(status='published')
        
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
            
        instructor_id = self.request.GET.get('instructor')
        if instructor_id:
            queryset = queryset.filter(instructor__id=instructor_id)
            
        return queryset.order_by('-created_at')


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug' 
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated and hasattr(self.request.user, 'student'):
            context['is_enrolled'] = self.object.enrollments.filter(
                student=self.request.user.student
            ).exists()
            
        context['reviews'] = self.object.reviews.filter(is_approved=True)
        
        return context

class InstructorCourseMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return hasattr(self.request.user, 'instructor_profile')

class CourseCreateView(LoginRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    success_url = reverse_lazy('courses:course_list')

    def form_valid(self, form):
        if not hasattr(self.request.user, 'instructor_profile'):
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Only instructors can create courses")
        form.instance.instructor = self.request.user.instructor_profile
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:course_manage', kwargs={'slug': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instructor'] = self.request.user.instructor_profile
        return kwargs

class CourseUpdateView(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'
    
    def get_object(self, queryset=None):
        if 'slug' in self.kwargs:
            return get_object_or_404(Course, slug=self.kwargs['slug'])
        elif 'pk' in self.kwargs:
            return get_object_or_404(Course, pk=self.kwargs['pk'])
        raise Http404("Course not found")

class CourseManageView(InstructorCourseMixin, DetailView):
    model = Course
    template_name = 'courses/course_manage.html'
    slug_url_kwarg = 'slug'
    
    context_object_name = 'course'
    
    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user.instructor_profile)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lessons'] = self.object.lessons.all().order_by('order')
        return context
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object 
class LessonCreateView(InstructorCourseMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_create.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(
            Course, 
            slug=kwargs['slug'], 
            instructor=request.user.instructor
        )
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.course = self.course
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Lesson added successfully!')
        return reverse_lazy('courses:course_manage', kwargs={'slug': self.course.slug})

class LessonUpdateView(InstructorCourseMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/lesson_edit.html'
    pk_url_kwarg = 'lesson_id'
    
    def get_queryset(self):
        return Lesson.objects.filter(
            course__instructor=self.request.user.instructor
        )
    
    def get_success_url(self):
        messages.success(self.request, 'Lesson updated successfully!')
        return reverse_lazy('courses:course_manage', kwargs={'slug': self.object.course.slug})

class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'courses/lesson_detail.html'
    pk_url_kwarg = 'lesson_id'
    context_object_name = 'lesson'
    
    def get_queryset(self):
        if hasattr(self.request.user, 'student'):
            return Lesson.objects.filter(
                course__enrollments__student=self.request.user.student
            )
        elif hasattr(self.request.user, 'instructor'):
            return Lesson.objects.filter(
                course__instructor=self.request.user.instructor
            )
        return Lesson.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if hasattr(self.request.user, 'student'):
            progress, created = CourseProgress.objects.get_or_create(
                enrollment__student=self.request.user.student,
                enrollment__course=self.object.course,
                lesson=self.object,
                defaults={'is_completed': False}
            )
            context['progress'] = progress
            
        return context

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'courses/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs['slug'])
        
        if not hasattr(request.user, 'student') or not self.course.enrollments.filter(
            student=request.user.student
        ).exists():
            messages.error(request, 'You must enroll in the course to leave a review.')
            return redirect('courses:course_detail', slug=self.course.slug)
            
        if Review.objects.filter(course=self.course, student=request.user.student).exists():
            messages.error(request, 'You have already reviewed this course.')
            return redirect('courses:course_detail', slug=self.course.slug)
            
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.instance.course = self.course
        form.instance.student = self.request.user.student
        messages.success(self.request, 'Review submitted for approval!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('courses:course_detail', kwargs={'slug': self.course.slug})

def mark_lesson_complete(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if not hasattr(request.user, 'student'):
        return redirect('login')
    
    enrollment = lesson.course.enrollments.filter(
        student=request.user.student
    ).first()
    
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('courses:course_detail', slug=lesson.course.slug)
    
    progress, created = CourseProgress.objects.get_or_create(
        enrollment=enrollment,
        lesson=lesson,
        defaults={'is_completed': True}
    )
    
    if not created:
        progress.is_completed = not progress.is_completed
        progress.save()
    
    return redirect('courses:lesson_detail', slug=lesson.course.slug, lesson_id=lesson.id)


class CourseLearnView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'courses/course_learn.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.objects.filter(
            enrollments__student=self.request.user.student_profile
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['first_lesson'] = self.object.lessons.first()
        return context
    
def course_archive(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user.instructor_profile)
    course.status = 'archived'
    course.save()
    messages.success(request, f"Course '{course.title}' has been archived")
    return redirect('courses:course_manage', slug=slug)

def course_publish(request, slug):
    course = get_object_or_404(Course, slug=slug, instructor=request.user.instructor_profile)
    course.status = 'published'
    course.save()
    messages.success(request, f"Course '{course.title}' has been published")
    return redirect('courses:course_manage', slug=slug)