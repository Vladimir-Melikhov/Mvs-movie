from typing import Tuple
from django.utils import timezone
from .models import Subscription, DailyWatchLimit


def has_active_subscription(user) -> bool:
    if not user.is_authenticated:
        return False

    try:
        subscription = Subscription.objects.get(user=user, is_active=True)
        return not subscription.is_expired()
    except Subscription.DoesNotExist:
        return False


def get_daily_watch_limit(user) -> Tuple[int, int, bool]:
    has_subscription = has_active_subscription(user)

    if has_subscription:
        return (0, -1, True)                      

    today = timezone.now().date()
    limit, created = DailyWatchLimit.objects.get_or_create(
        user=user,
        date=today,
        defaults={'watched_seconds': 0}
    )

    remaining = limit.get_remaining_seconds()
    return (limit.watched_seconds, remaining, False)


def can_watch_video(user) -> Tuple[bool, str]:
    if not user.is_authenticated:
        return (False, "Please login to watch movies")

    watched, remaining, has_sub = get_daily_watch_limit(user)

    if has_sub:
        return (True, "")

    if remaining <= 0:
        return (False, "Daily watch limit reached. Subscribe to watch unlimited!")

    return (True, f"You have {remaining // 60} minutes remaining today")


def update_watch_time(user, seconds: int) -> None:
    if has_active_subscription(user):
        return

    today = timezone.now().date()
    limit, created = DailyWatchLimit.objects.get_or_create(
        user=user,
        date=today,
        defaults={'watched_seconds': 0}
    )

    limit.add_watch_time(seconds)
