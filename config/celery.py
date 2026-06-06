                  

"""
Celery configuration for VideoHub project.
"""

import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('videohub')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'deactivate-expired-subscriptions': {
        'task': 'apps.subscribe.tasks.deactivate_expired_subscriptions',
        'schedule': crontab(minute='*/30'),
    },
    'cleanup-old-watch-limits': {
        'task': 'apps.subscribe.tasks.cleanup_old_watch_limits',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),
    },
    'cleanup-expired-tokens': {
        'task': 'apps.accounts.tasks.cleanup_expired_tokens',
        'schedule': crontab(hour=1, minute=0),
    },
    'cleanup-pending-payments': {
        'task': 'apps.payment.tasks.cleanup_pending_payments',
        'schedule': crontab(hour=2, minute=30),                      
    },
    'send-subscription-expiry-reminders': {
        'task': 'apps.payment.tasks.send_subscription_expiry_reminder',
        'schedule': crontab(hour=10, minute=0),                       
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery."""
    print(f'Request: {self.request!r}')
