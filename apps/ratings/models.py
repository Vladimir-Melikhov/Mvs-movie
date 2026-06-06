from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Rating(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('user')
    )

    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='ratings',
        verbose_name=_('movie')
    )

    score = models.IntegerField(
        _('score'),
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text=_('Rating score from 1 to 10')
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
        verbose_name = _('rating')
        verbose_name_plural = _('ratings')
        ordering = ['-created_at']
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['movie', '-created_at']),
            models.Index(fields=['score']),
        ]

    def __str__(self) -> str:
        """Return string representation of the rating."""
        return f"{self.user.username} rated {self.movie.title}: {self.score}/10"


class Comment(models.Model):
    """Comment model for movie comments."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('user')
    )

    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('movie')
    )

    text = models.TextField(
        _('text'),
        max_length=1000,
        help_text=_('Comment text (max 1000 characters)')
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
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-created_at']
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', 'movie']),
            models.Index(fields=['movie', '-created_at']),
        ]

    def __str__(self) -> str:
        """Return string representation of the comment."""
        return f"Comment by {self.user.username} on {self.movie.title}"

    def is_edited(self) -> bool:
        """Check if the comment has been edited."""
        return self.updated_at > self.created_at
