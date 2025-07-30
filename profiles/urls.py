from django.urls import path
from .views import (
    DashboardView,
    StudentDashboardView,
    InstructorDashboardView,
    EmployeeDashboardView,
    ProfileUpdateView,
    PublicProfileView,
    ProfilePhotoUpdateView,
    VerificationRequestView
)

app_name = 'profiles'

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('student/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('instructor/', InstructorDashboardView.as_view(), name='instructor_dashboard'),
    path('employee/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    path('edit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('edit/photo/', ProfilePhotoUpdateView.as_view(), name='edit_photo'),
    
    path('public/<int:user_id>/', PublicProfileView.as_view(), name='public_profile'),
    path('verify/', VerificationRequestView.as_view(), name='verification_request'),
]