import os
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.validators import MinLengthValidator, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from datetime import date
from django.db.models import Count, Sum

def user_profile_picture_path(instance, filename):
    return f'profile_photos/user_{instance.user.id}/{filename}'

def profile_photo_path(instance, filename):
    """Returns upload path for user profile photos"""
    return os.path.join('profile_photos', f'user_{instance.user.id}', filename)

class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        INSTRUCTOR = 'instructor', _('Instructor')
        EMPLOYEE = 'employee', _('Employee')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT
    )
    
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        related_name="custom_users",
        related_query_name="custom_user",
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        related_name="custom_users",
        related_query_name="custom_user",
    )

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        
    def __str__(self):
        return self.get_full_name() or self.username

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='%(class)s_profile'
    )
    
    profile_photo = models.ImageField(
        upload_to=profile_photo_path,
        default='default_profile.png',
        blank=True
    )
    
    bio = models.TextField(
        blank=True,
        validators=[MinLengthValidator(10)],
        help_text=_('Tell others about yourself')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Student(Profile):
    enrollment_id = models.CharField(
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(5)],
        help_text="Unique student identification number"
    )
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True
    )
    profile_photo = models.ImageField(
        upload_to=profile_photo_path,
        default='default_profile.png',
        blank=True
    )

    class Meta(Profile.Meta):
        verbose_name = "Student Profile"
        verbose_name_plural = "Student Profiles"

class Instructor(Profile):
    qualifications = models.TextField(
        help_text="List your degrees, certifications, and qualifications"
    )
    specialization = models.CharField(
        max_length=100,
        help_text="Your primary field of expertise"
    )
    is_verified = models.BooleanField(default=False)
    years_of_experience = models.PositiveIntegerField(default=0)
    website = models.URLField(blank=True)
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    profile_photo = models.ImageField(upload_to=profile_photo_path, default='default_profile.png', blank=True)

    class Meta(Profile.Meta):
        verbose_name = "Instructor Profile"
        verbose_name_plural = "Instructor Profiles"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(years_of_experience__lte=50),
                name="reasonable_experience_years",
            ),
        ]

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_verified and not self.qualifications:
            raise ValidationError("Verified instructors must have qualifications listed")
        
    @property
    def get_student_count(self):
        """Return total number of students across all courses"""
        from django.db.models import Count
        return self.courses.annotate(
            student_count=Count('enrollments')
        ).aggregate(
            total=Sum('student_count')
        )['total'] or 0

    def get_absolute_url(self):
        return reverse('users:instructor_detail', kwargs={'pk': self.id})

class Employee(Profile):
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    employee_id = models.CharField(
        max_length=20,
        unique=True
    )
    is_full_time = models.BooleanField(default=True)
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates'
    )
    profile_photo = models.ImageField(
        upload_to=profile_photo_path,
        default='default_profile.png',
        blank=True
    )

    class Meta(Profile.Meta):
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        permissions = [
            ("manage_employees", "Can manage employee records"),
        ]

    @property
    def tenure(self):
        from datetime import date
        return date.today().year - self.hire_date.year