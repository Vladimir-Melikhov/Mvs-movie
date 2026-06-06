from celery import shared_task
from django.utils import timezone
from django.db.models import Q

from .models import Subscription, DailyWatchLimit


@shared_task
def deactivate_expired_subscriptions() -> str:
    now = timezone.now()

    expired_subscriptions = Subscription.objects.filter(
        is_active=True,
        end_date__lt=now
    )

    count = expired_subscriptions.count()

    for subscription in expired_subscriptions:
        subscription.deactivate()

    return f"Deactivated {count} expired subscriptions"


@shared_task
def cleanup_old_watch_limits() -> str:
    cutoff_date = timezone.now().date() - timezone.timedelta(days=30)

    old_limits = DailyWatchLimit.objects.filter(date__lt=cutoff_date)
    count = old_limits.count()
    old_limits.delete()

    return f"Deleted {count} old watch limit records"
