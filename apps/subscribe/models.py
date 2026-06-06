from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Subscription(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscription',
        verbose_name=_('user')
    )

    start_date = models.DateTimeField(
        _('start date'),
        default=timezone.now
    )

    end_date = models.DateTimeField(
        _('end date'),
        help_text=_('Subscription expiration date')
    )

    is_active = models.BooleanField(
        _('is active'),
        default=True,
        help_text=_('Whether subscription is currently active')
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
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['end_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self) -> str:
        return f"Subscription for {self.user.username}"

    def is_expired(self) -> bool:
        return timezone.now() > self.end_date

    def days_remaining(self) -> int:
        if self.is_expired():
            return 0
        delta = self.end_date - timezone.now()
        return delta.days

    def deactivate(self) -> None:
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])


class DailyWatchLimit(models.Model):
    """
    Daily watch time tracking for users without subscription.

    Tracks how much time user has watched today.
    Resets daily at midnight.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='daily_limits',
        verbose_name=_('user')
    )

    date = models.DateField(
        _('date'),
        default=timezone.now
    )

    watched_seconds = models.IntegerField(
        _('watched seconds'),
        default=0,
        help_text=_('Total seconds watched today')
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
        verbose_name = _('daily watch limit')
        verbose_name_plural = _('daily watch limits')
        ordering = ['-date']
        unique_together = ('user', 'date')
        indexes = [
            models.Index(fields=['user', 'date']),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.date}"

    def get_watched_minutes(self) -> int:
        return self.watched_seconds // 60

    def get_remaining_seconds(self) -> int:
        """Returns remaining seconds (max 3600 = 1 hour)"""
        limit = 3600                     
        remaining = limit - self.watched_seconds
        return max(0, remaining)

    def is_limit_reached(self) -> bool:
        return self.watched_seconds >= 3600

    def add_watch_time(self, seconds: int) -> None:
        self.watched_seconds += seconds
        self.save(update_fields=['watched_seconds', 'updated_at'])
