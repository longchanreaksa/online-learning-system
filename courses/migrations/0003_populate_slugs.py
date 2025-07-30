from django.db import migrations
from django.utils.text import slugify

def generate_slugs(apps, schema_editor):
    Course = apps.get_model('courses', 'Course')
    for course in Course.objects.all():
        if not course.slug:
            base_slug = slugify(course.title)
            unique_slug = base_slug
            counter = 1
            while Course.objects.filter(slug=unique_slug).exclude(pk=course.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            course.slug = unique_slug
            course.save()

class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0002_initial'),  # your last migration
    ]

    operations = [
        migrations.RunPython(generate_slugs),
    ]