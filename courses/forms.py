from django import forms
from django.core.exceptions import ValidationError
from .models import Course, Lesson, Review
from categories.models import Category, Tag
from users.models import Instructor
from django.utils.text import slugify

class CourseForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text="Select a primary category for your course",
        required=True 
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Add relevant tags to help students find your course"
    )
    
    price = forms.DecimalField(
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        help_text="Set price in USD. Use 0.00 for free courses"
    )

    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'tags', 'price', 'image', 'status']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Python for Beginners'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe what students will learn...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'status': "Draft: Not visible to students. Published: Live on platform.",
        }

    def __init__(self, *args, **kwargs):
        self.instructor = kwargs.pop('instructor', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['category'].initial = self.instance.category
            self.fields['tags'].initial = self.instance.tags.all()

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            
            if not image.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                raise forms.ValidationError("Only JPG/JPEG/PNG images allowed")
        return image

    def clean_price(self):
        price = self.cleaned_data['price']
        if price < 0:
            raise ValidationError("Price cannot be negative")
        return price
    
    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('slug') and not self.instance.slug:
            title = cleaned_data.get('title')
            if title:
                cleaned_data['slug'] = slugify(title)
        return cleaned_data
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            raise forms.ValidationError("Slug cannot be empty")
        return slug

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.slug:
            instance.slug = slugify(instance.title)
            # Handle uniqueness
            base_slug = instance.slug
            counter = 1
            while Course.objects.filter(slug=instance.slug).exclude(pk=instance.pk).exists():
                instance.slug = f"{base_slug}-{counter}"
                counter += 1
        if commit:
            instance.save()
            self.save_m2m()
        return instance

class LessonForm(forms.ModelForm):
    video_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://youtube.com/embed/...'
        }),
        help_text="Paste YouTube/Vimeo embed URL (not watch link)"
    )
    
    resources = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        help_text="Upload supplementary materials (PDFs, slides, etc.)"
    )

    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category', 'tags',
            'price', 'image', 'status'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Introduction to Variables'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lesson objectives and key points...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'placeholder': 'Estimated duration in minutes'
            }),
            'is_preview': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_order(self):
        order = self.cleaned_data['order']
        course = self.instance.course if self.instance.pk else None
        
        if course and Lesson.objects.filter(course=course, order=order).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A lesson with this order already exists in the course.")
        
        return order

    def clean(self):
        cleaned_data = super().clean()
        video_url = cleaned_data.get('video_url')
        resources = cleaned_data.get('resources')
        
        if not video_url and not resources:
            raise ValidationError("At least one of video URL or resource file is required.")
        
        return cleaned_data

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '★★★★★ - Excellent'),
        (4, '★★★★☆ - Good'),
        (3, '★★★☆☆ - Average'),
        (2, '★★☆☆☆ - Poor'),
        (1, '★☆☆☆☆ - Terrible'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        initial=5,
        help_text="Your overall rating for this course"
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your learning experience...'
        }),
        required=False,
        help_text="Optional detailed review"
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
    def clean_rating(self):
        return int(self.cleaned_data['rating'])