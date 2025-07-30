from django.contrib import admin
from .models import Course, Lesson, Review

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'status', 'price')
    list_filter = ('status', 'category')
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Lesson)
admin.site.register(Review)