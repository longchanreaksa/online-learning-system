from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.views.generic import DetailView
from .models import Instructor

from .models import Student, Instructor, Employee
from .forms import (
    User,
    UserUpdateForm,
    RegisterForm,
    StudentProfileUpdateForm,
    InstructorProfileUpdateForm,
    EmployeeProfileUpdateForm
)
from courses.models import Course, CourseActivity
from enrollments.models import Enrollment

def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect_dashboard(request)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def redirect_dashboard(request):
    """Route user to appropriate dashboard based on role"""
    if not request.user.is_authenticated:
        return redirect('users:login')
        
    if not hasattr(request.user, 'role'):
        auth_logout(request)
        messages.error(request, 'User account not properly configured')
        return redirect('users:login')
        
    role = request.user.role.lower()
    
    if role == 'student':
        return redirect('users:student_dashboard')
    elif role == 'instructor':
        return redirect('users:instructor_dashboard')
    elif role == 'employee':
        return redirect('users:employee_dashboard')
    else:
        auth_logout(request)
        messages.error(request, 'Invalid user role')
        return redirect('users:login')

@login_required
def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('users:login')

@login_required
def profile(request):
    """Handle user profile updates"""
    user = request.user
    if not hasattr(user, 'role'):
        messages.error(request, "User role not defined")
        return redirect('users:login')

    role = user.role.lower()
    profile_attr = f'{role}_profile'
    
    try:
        profile = getattr(user, profile_attr)
    except AttributeError:
        messages.error(request, "Profile not found")
        return redirect('users:login')

    ProfileForm = {
        'student': StudentProfileUpdateForm,
        'instructor': InstructorProfileUpdateForm,
        'employee': EmployeeProfileUpdateForm
    }.get(role)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect(f'users:{role}_dashboard')
        else:
            for field, errors in u_form.errors.items():
                for error in errors:
                    messages.error(request, f"User {field}: {error}")
            for field, errors in p_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profile {field}: {error}")
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileForm(instance=profile)

    return render(request, 'users/profile.html', {
        'u_form': u_form,
        'p_form': p_form,
        'active_tab': 'profile'
    })

@login_required
def dashboard(request):
    """Redirect to role-specific dashboard"""
    if not hasattr(request.user, 'role'):
        messages.error(request, 'User role not defined')
        return redirect('users:login')
    return redirect(f'users:{request.user.role.lower()}_dashboard')

@login_required
def student_dashboard(request):
    """Student dashboard with course progress tracking"""
    try:
        student = request.user.student_profile
    except (Student.DoesNotExist, AttributeError):
        messages.error(request, 'Student profile not found')
        auth_logout(request)
        return redirect('users:login')
    
    enrollments = Enrollment.objects.filter(
        student=student
    ).select_related(
        'course', 
        'course__instructor__user'
    ).prefetch_related(
        'progress_records__lesson'
    ).order_by('-enrolled_at')
    
    for enrollment in enrollments:
        total_lessons = enrollment.course.lessons.count()
        completed = enrollment.progress_records.filter(is_completed=True).count()
        enrollment.progress_percentage = int((completed / total_lessons) * 100) if total_lessons > 0 else 0
        enrollment.completed_lessons = completed
        enrollment.total_lessons = total_lessons
        if enrollment.progress_records.exists():
            enrollment.last_accessed = enrollment.progress_records.latest('last_accessed').last_accessed

    context = {
        'enrollments': enrollments,
        'completed_courses': sum(1 for e in enrollments if e.progress_percentage == 100),
        'in_progress_courses': sum(1 for e in enrollments if 0 < e.progress_percentage < 100),
        'active_tab': 'dashboard'
    }
    return render(request, 'users/student_dashboard.html', context)

@login_required
def instructor_dashboard(request):
    """Instructor dashboard with course statistics"""
    try:
        instructor = request.user.instructor_profile
    except (Instructor.DoesNotExist, AttributeError):
        messages.error(request, 'Instructor profile not found')
        auth_logout(request)
        return redirect('users:login')
    
    courses = Course.objects.filter(
        instructor=instructor
    ).annotate(
        student_count=Count('enrollments', distinct=True),
        avg_rating=Avg('reviews__rating')
    ).order_by('-created_at')[:10]
    
    total_students = sum(c.student_count for c in courses if c.student_count)
    avg_rating = courses.aggregate(avg=Avg('reviews__rating'))['avg'] or 0
    
    context = {
        'courses': courses,
        'total_students': total_students,
        'average_rating': round(avg_rating, 1) if avg_rating else None,
        'recent_activity': CourseActivity.objects.filter(
            enrollment__course__instructor=instructor
        ).select_related(
            'enrollment__student__user',
            'enrollment__course'
        ).order_by('-timestamp')[:10],
        'active_tab': 'dashboard'
    }
    return render(request, 'users/instructor_dashboard.html', context)

@login_required
def employee_dashboard(request):
    """Employee/admin dashboard with system statistics"""
    try:
        employee = request.user.employee_profile
    except (Employee.DoesNotExist, AttributeError):
        messages.error(request, 'Employee profile not found')
        auth_logout(request)
        return redirect('users:login')

    from datetime import datetime, timedelta

    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    context = {
        'total_users': User.objects.count(),
        'new_users_week': User.objects.filter(date_joined__gte=last_week).count(),
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(status='published').count(),
        'new_courses_month': Course.objects.filter(created_at__gte=last_month).count(),
        'total_enrollments': Enrollment.objects.count(),
        'active_enrollments': Enrollment.objects.filter(
            Q(completion_date__isnull=True) &
            Q(enrolled_at__gte=last_month)
        ).count(),
        'recent_activities': CourseActivity.objects.select_related(
            'enrollment__student__user',
            'enrollment__course'
        ).order_by('-timestamp')[:10],
        'pending_tasks': [
            {'description': 'Review new courses', 'priority_class': 'warning'},
            {'description': 'Process refund requests', 'priority_class': 'danger'},
        ],
        'reported_issues': 5,
        'active_tab': 'dashboard'
    }
    return render(request, 'users/employee_dashboard.html', context)

def register(request):
    """Handle new user registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('users:login')
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def instructor_list(request):
    """List of verified instructors"""
    instructors = Instructor.objects.all()
    return render(request, 'users/instructor_list.html', {
        'instructors': instructors,
        'active_tab': 'instructors'
    })
    
@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_users(request):
    """View for managing users (staff only)"""
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'users/manage_users.html', {
        'users': users,
        'active_tab': 'manage_users'
    })
    
    
class InstructorDetailView(DetailView):
    model = Instructor
    template_name = 'users/instructor_detail.html'
    context_object_name = 'instructor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['courses'] = self.object.courses.filter(status='published')
        return context