from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category, Tag
from users.models import Instructor, Student, Employee
from django.db import models
from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from categories.models import Category, Tag
from users.models import Instructor, Student, Employee
from PIL import Image

import unicodedata
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

class Course(models.Model):
    """Core course model with publishing controls and monetization"""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name="Course Category"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='courses')
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        upload_to='courses/images/',
        blank=True,
        null=True,
        help_text="Upload image with 16:9 aspect ratio (recommended 1200x675px)"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    students = models.ManyToManyField(
        Student,
        through='enrollments.Enrollment',
        related_name='enrolled_courses'
    )

    class Meta:
        ordering = ['-created_at']
        permissions = [
            ('publish_course', 'Can publish course'),
            ('archive_course', 'Can archive course'),
        ]

    def clean(self):
        super().clean()
        if self.image:
            max_size = 2 * 1024 * 1024 
            if self.image.size > max_size:
                raise ValidationError("Image file too large ( > 2MB )")
            
            try:
                img = Image.open(self.image)
                width, height = img.size
                if width > 2000 or height > 2000:
                    raise ValidationError("Image dimensions too large (max 2000x2000px)")
            except:
                raise ValidationError("Invalid image format")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def resize_image(self):
        img_path = self.image.path
        try:
            img = Image.open(img_path)
            
            target_width = 1200
            target_height = 675
            
            if img.size[0] > target_width or img.size[1] > target_height:
                img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
                
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                temp_file = BytesIO()
                img.save(temp_file, format='JPEG', quality=85, optimize=True)
                temp_file.seek(0)
                
                self.image.save(
                    os.path.basename(img_path),
                    ContentFile(temp_file.read()),
                    save=False
                )
                temp_file.close()
                super().save(update_fields=['image'])
        except Exception as e:
            print(f"Error processing image: {str(e)}")

    def __str__(self):
        return f"{self.title} by {self.instructor.user.get_full_name()}"

    @property
    def is_published(self):
        return self.status == 'published'
    
    @property
    def is_free(self):
        return self.price == 0

    def get_enrollment_count(self):
        return self.enrollments.count()


class Lesson(models.Model):
    """Learning units within a course with multimedia support"""
    course = models.ForeignKey(
        'courses.Course',   
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    description = models.TextField(blank=True)
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="YouTube/Vimeo embed URL"
    )
    resources = models.FileField(
        upload_to='lessons/resources/',
        blank=True,
        null=True,
        help_text="PDFs, slides, or other materials"
    )
    duration_minutes = models.PositiveIntegerField(
        default=0,
        help_text="Estimated lesson duration in minutes"
    )
    is_preview = models.BooleanField(
        default=False,
        help_text="Mark as free preview lesson"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'title'],
                name='unique_lesson_title_per_course'
            )
        ]

    def __str__(self):
        return f"{self.course.title} - Lesson {self.order}: {self.title}"


class Review(models.Model):
    """Student reviews and ratings for courses"""
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='course_reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(
        default=False,
        help_text="Employee must approve reviews"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'student')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.rating}★ by {self.student.user.username} for {self.course.title}"


class CourseProgress(models.Model):
    """Tracks student progress through course lessons"""
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='progress'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='course_progress_records' 
    )
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')
        verbose_name_plural = 'Course Progress'

    def __str__(self):
        status = "Completed" if self.is_completed else "In Progress"
        return f"{self.enrollment.student} - {self.lesson.title} ({status})"
    
    
class CourseActivity(models.Model):
    ACTIVITY_TYPES = [
        ('enrollment', 'Enrollment'),
        ('completion', 'Completion'),
        ('progress', 'Progress'),
    ]
    
    enrollment = models.ForeignKey(
        'enrollments.Enrollment',
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=20, 
        choices=ACTIVITY_TYPES
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(blank=True, null=True)
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.course_id and self.enrollment:
            self.course = self.enrollment.course
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.enrollment.student.user.username} - {self.activity_type}"