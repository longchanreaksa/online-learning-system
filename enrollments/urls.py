from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll'),
    path('progress/<int:enrollment_id>/', views.course_progress, name='progress'),
    path('my-enrollments/', views.EnrollmentListView.as_view(), name='my_enrollments'),
    path('update-grade/<int:pk>/', views.UpdateGradeView.as_view(), name='update_grade'),
]