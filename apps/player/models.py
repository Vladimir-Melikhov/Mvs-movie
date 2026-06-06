from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class WatchHistory(models.Model):
    """
    Model to track user's watch history and progress.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watch_history',
        verbose_name=_('user')
    )

    movie = models.ForeignKey(
        'movies.Movie',
        on_delete=models.CASCADE,
        related_name='watch_history',
        verbose_name=_('movie')
    )

    progress = models.IntegerField(
        _('progress'),
        default=0,
        help_text=_('Playback progress in seconds')
    )

    duration = models.IntegerField(
        _('duration'),
        default=0,
        help_text=_('Total video duration in seconds')
    )

    completed = models.BooleanField(
        _('completed'),
        default=False,
        help_text=_('Whether the movie was watched completely')
    )

    last_watched = models.DateTimeField(
        _('last watched'),
        auto_now=True
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('watch history')
        verbose_name_plural = _('watch histories')
        ordering = ['-last_watched']
        unique_together = ('user', 'movie')
        indexes = [
            models.Index(fields=['user', '-last_watched']),
            models.Index(fields=['movie', '-last_watched']),
        ]

    def __str__(self) -> str:
        """Return string representation."""
        return f"{self.user.username} - {self.movie.title}"

    def get_progress_percentage(self) -> int:
        """Calculate progress percentage."""
        if self.duration > 0:
            return int((self.progress / self.duration) * 100)
        return 0

    def mark_as_completed(self) -> None:
        """Mark movie as completed."""
        self.completed = True
        self.save(update_fields=['completed'])
