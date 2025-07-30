from django.contrib import admin
from .models import Enrollment, Progress

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'enrolled_at', 'get_progress_percentage')
    list_filter = ('status', 'course', 'enrolled_at')
    search_fields = ('student__user__username', 'course__title')
    readonly_fields = ('enrolled_at', 'get_progress_percentage')
    
    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage}%"
    get_progress_percentage.short_description = 'Progress'

@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'last_accessed')
    list_filter = ('is_completed', 'lesson__course')
    search_fields = ('enrollment__student__user__username', 'lesson__title')