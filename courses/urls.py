from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='course_list'),
    path('create/', views.CourseCreateView.as_view(), name='course_create'),  
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses-by-id/<int:pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit_by_pk'),
    path('courses/<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),
    path('courses/<slug:slug>/manage/', views.CourseManageView.as_view(), name='course_manage'),
    path('<slug:slug>/lessons/create/', views.LessonCreateView.as_view(), name='lesson_create'),
    path('<slug:course_slug>/lessons/<int:lesson_id>/', views.LessonDetailView.as_view(), name='lesson_detail'),
    path('<slug:slug>/lessons/<int:lesson_id>/edit/', views.LessonUpdateView.as_view(), name='lesson_edit'),
    path('lessons/<int:lesson_id>/complete/', views.mark_lesson_complete, name='lesson_complete'),
    
    path('<slug:slug>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    
    
    path('<slug:slug>/archive/', views.course_archive, name='course_archive'),
    path('<slug:slug>/publish/', views.course_publish, name='course_publish'),
    
]