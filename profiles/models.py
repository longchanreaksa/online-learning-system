from django.db import models
from django.core.validators import MinLengthValidator
from online_learning_system import settings
from users.models import User, Student
from .validators import validate_profile_photo_size  # Custom validator example
    
class VerificationSubmission(models.Model):
    """Model for instructor verification submissions"""
    instructor = models.OneToOneField(
        'users.Instructor',
        on_delete=models.CASCADE,
        related_name='verification'
    )
    document = models.FileField(
        upload_to='verifications/',
        help_text="Upload proof of qualifications"
    )
    message = models.TextField(
        blank=True,
        help_text="Additional information for verification"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reviewed_verifications'
    )

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Verification Submission"
        verbose_name_plural = "Verification Submissions"

    def __str__(self):
        return f"Verification for {self.instructor.user.username}"