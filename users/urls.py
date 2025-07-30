from django.urls import path
from . import views

app_name = 'users' 

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('instructors/<int:pk>/', views.InstructorDetailView.as_view(), name='instructor_detail'),
]