from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os


def validate_file_size(file, max_size_mb: int = 5):
    """Validate file size."""
    max_size = max_size_mb * 1024 * 1024                       
    if file.size > max_size:
        raise ValidationError(
            _(f'File size cannot exceed {max_size_mb}MB.')
        )


def validate_image_extension(file):
    """Validate that file is an image."""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in valid_extensions:
        raise ValidationError(
            _('Only image files are allowed (jpg, jpeg, png, gif, webp).')
        )


def validate_video_extension(file):
    """Validate that file is a video."""
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    ext = os.path.splitext(file.name)[1].lower()

    if ext not in valid_extensions:
        raise ValidationError(
            _('Only video files are allowed (mp4, avi, mov, mkv, webm).')
        )
