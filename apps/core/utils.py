import os
import uuid
from typing import Optional
from django.utils.text import slugify


def generate_unique_slug(model_class, title: str, slug_field: str = 'slug') -> str:
    """Generate a unique slug for a model instance."""
    slug = slugify(title)
    unique_slug = slug
    counter = 1

    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    return unique_slug


def get_upload_path(instance, filename: str, folder: str = '') -> str:
    """Generate upload path for files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"

    if folder:
        return os.path.join(folder, filename)
    return filename


def format_duration(seconds: int) -> str:
    """Format duration in seconds to human-readable format."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"
