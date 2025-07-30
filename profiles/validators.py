# profiles/validators.py
from django.core.exceptions import ValidationError

def validate_profile_photo_size(value):
    filesize = value.size
    if filesize > 2 * 1024 * 1024:  # 2MB
        raise ValidationError("The maximum file size that can be uploaded is 2MB")
    if value.image.width != value.image.height:
        raise ValidationError("Profile photo must be square (1:1 aspect ratio)")