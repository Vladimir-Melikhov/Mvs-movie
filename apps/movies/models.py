from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db.models import Avg

from apps.core.utils import generate_unique_slug


class Category(models.Model):
    """Category model for organizing movies."""

    name = models.CharField(
        _('name'),
        max_length=100,
        unique=True,
        help_text=_('Category name (e.g., Action, Comedy, Drama)')
    )

    slug = models.SlugField(
        _('slug'),
        max_length=100,
        unique=True,
        help_text=_('URL-friendly version of the name')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Category description')
    )

    order = models.IntegerField(
        _('order'),
        default=0,
        help_text=_('Sort order for displaying categories')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['order']),
        ]

    def __str__(self) -> str:
        """Return string representation of the category."""
        return self.name

    def get_absolute_url(self) -> str:
        """Return the URL for the category."""
        return reverse('movies:category', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Generate slug if not provided."""
        if not self.slug:
            self.slug = generate_unique_slug(Category, self.name)
        super().save(*args, **kwargs)

    def get_movies_count(self) -> int:
        """Return the number of movies in this category."""
        return self.movies.count()


class Movie(models.Model):
    """
    Movie model for storing film information.

    Movies are managed only through the admin panel.
    """

    RATING_CHOICES = [
        ('G', 'G - General Audiences'),
        ('PG', 'PG - Parental Guidance Suggested'),
        ('PG-13', 'PG-13 - Parents Strongly Cautioned'),
        ('R', 'R - Restricted'),
        ('NC-17', 'NC-17 - Adults Only'),
    ]

    title = models.CharField(
        _('title'),
        max_length=255,
        help_text=_('Movie title')
    )

    slug = models.SlugField(
        _('slug'),
        max_length=255,
        unique=True,
        help_text=_('URL-friendly version of the title')
    )

    description = models.TextField(
        _('description'),
        help_text=_('Movie synopsis/description')
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='movies',
        verbose_name=_('category')
    )

    year = models.IntegerField(
        _('year'),
        validators=[MinValueValidator(1888), MaxValueValidator(2100)],
        help_text=_('Release year')
    )

    duration = models.IntegerField(
        _('duration'),
        help_text=_('Duration in minutes')
    )

    poster = models.ImageField(
        _('poster'),
        upload_to='movies/posters/%Y/%m/%d/',
        help_text=_('Movie poster image for catalog')
    )

    video_url = models.URLField(
        _('video URL'),
        blank=True,
        help_text=_('URL to video file or streaming link')
    )

    video_file = models.FileField(
        _('video file'),
        upload_to='movies/videos/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Video file upload (optional if video_url is provided)')
    )

    director = models.CharField(
        _('director'),
        max_length=255,
        blank=True,
        help_text=_('Movie director')
    )

    actors = models.TextField(
        _('actors'),
        blank=True,
        help_text=_('Main actors (comma-separated)')
    )

    mpaa_rating = models.CharField(
        _('MPAA rating'),
        max_length=10,
        choices=RATING_CHOICES,
        blank=True,
        help_text=_('MPAA rating (G, PG, PG-13, R, NC-17)')
    )

    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        help_text=_('Country of production')
    )

    views_count = models.IntegerField(
        _('views count'),
        default=0,
        help_text=_('Number of views')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('movie')
        verbose_name_plural = _('movies')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
            models.Index(fields=['year']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-views_count']),
        ]

    def __str__(self) -> str:
        """Return string representation of the movie."""
        return f"{self.title} ({self.year})"

    def get_absolute_url(self) -> str:
        """Return the URL for the movie."""
        return reverse('movies:movie_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        """Generate slug if not provided."""
        if not self.slug:
            self.slug = generate_unique_slug(Movie, self.title)
        super().save(*args, **kwargs)

    def get_average_rating(self) -> float:
        """Calculate and return the average rating."""
        result = self.ratings.aggregate(avg_rating=Avg('score'))
        return round(result['avg_rating'], 1) if result['avg_rating'] else 0

    def get_ratings_count(self) -> int:
        """Return the number of ratings."""
        return self.ratings.count()

    def get_comments_count(self) -> int:
        """Return the number of comments."""
        return self.comments.count()

    def increment_views(self) -> None:
        """Increment the views counter."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

    def get_duration_display(self) -> str:
        """Return formatted duration (e.g., '2h 30m')."""
        hours = self.duration // 60
        minutes = self.duration % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def get_actors_list(self) -> list:
        """Return list of actors."""
        if self.actors:
            return [actor.strip() for actor in self.actors.split(',')]
        return []
