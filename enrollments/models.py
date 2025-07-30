from datetime import timezone
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from courses.models import Lesson  

class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        COMPLETED = 'completed', _('Completed')
        DROPPED = 'dropped', _('Dropped')
        SUSPENDED = 'suspended', _('Suspended')

    student = models.ForeignKey(
        'users.Student',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Student')
    )
    completed = models.BooleanField(default=False)
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name=_('Course')
    )
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Enrollment Date'))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_('Status')
    )
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name=_('Completion Date'))
    grade = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Grade')
    )
    
    def get_progress_percentage(self):
        """Admin-friendly progress percentage"""
        total_lessons = self.course.lessons.count()
        if total_lessons == 0:
            return 0
        completed = self.progress_records.filter(is_completed=True).count()
        return int((completed / total_lessons) * 100)
    
    get_progress_percentage.short_description = 'Progress %'
    get_progress_percentage.admin_order_field = 'progress_records__is_completed'

    class Meta:
        verbose_name = _('Enrollment')
        verbose_name_plural = _('Enrollments')
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']
        
        permissions = [
        ("view_all_enrollments", "Can view all enrollments"),
        ("change_enrollment_status", "Can change enrollment status"),
    ]

    def __str__(self):
        return f"{self.student} in {self.course} ({self.status})"

    def complete(self, grade=None):
        self.status = self.Status.COMPLETED
        self.completion_date = timezone.now()
        if grade is not None:
            self.grade = grade
        self.save()
        
    @property
    def completed(self):
        return self.completion_date is not None

class Progress(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name='progress_records',
        verbose_name=_('Enrollment')
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='enrollment_progress_records' 
    )
    is_completed = models.BooleanField(default=False, verbose_name=_('Completed'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completion Date'))
    last_accessed = models.DateTimeField(auto_now=True, verbose_name=_('Last Accessed'))

    class Meta:
        verbose_name = _('Progress')
        verbose_name_plural = _('Progress Records')
        unique_together = ('enrollment', 'lesson')
        ordering = ['lesson__order']

    def __str__(self):
        return f"{self.enrollment.student}'s progress in {self.lesson}"

    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
        
@property
def progress_percentage(self):
    total_lessons = self.course.lessons.count()
    if total_lessons == 0:
        return 0
    completed = self.progress_records.filter(is_completed=True).count()
    return int((completed / total_lessons) * 100)

def get_grade_display(self):
    if self.grade is None:
        return "N/A"
    return f"{self.grade}%"