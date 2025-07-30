# courses/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from .models import Course

@receiver(pre_save, sender=Course)
def ensure_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)