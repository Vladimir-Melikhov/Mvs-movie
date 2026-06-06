from typing import Optional
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings

from .models import Payment
from apps.subscribe.models import Subscription

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def process_successful_payment(self, payment_id: int) -> Optional[str]:
    try:
        payment = Payment.objects.select_related('user').get(id=payment_id)

        if not payment.is_successful():
            return f"Payment {payment_id} is not successful"

        user = payment.user
        subscription_months = payment.subscription_months

                                    
        subscription, created = Subscription.objects.get_or_create(
            user=user,
            defaults={
                'start_date': timezone.now(),
                'end_date': timezone.now() + timedelta(days=30 * subscription_months),
                'is_active': True,
            }
        )

        if not created:
                                          
            if subscription.is_active and not subscription.is_expired():
                                                   
                subscription.end_date = subscription.end_date + timedelta(days=30 * subscription_months)
            else:
                                                 
                subscription.start_date = timezone.now()
                subscription.end_date = timezone.now() + timedelta(days=30 * subscription_months)
                subscription.is_active = True

            subscription.save(update_fields=['start_date', 'end_date', 'is_active', 'updated_at'])

                                 
        send_subscription_confirmation_email.delay(user.id, payment.id)

        return f"Successfully processed payment {payment_id} for user {user.username}"

    except Payment.DoesNotExist:
        return None
    except Exception as exc:
                                           
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_subscription_confirmation_email(self, user_id: int, payment_id: int) -> Optional[str]:
    try:
        user = User.objects.get(id=user_id)
        payment = Payment.objects.get(id=payment_id)

                          
        subscription = Subscription.objects.get(user=user)

                              
        context = {
            'user': user,
            'payment': payment,
            'subscription': subscription,
            'days_remaining': subscription.days_remaining(),
        }

        html_message = render_to_string('payment/emails/subscription_confirmation.html', context)
        plain_message = strip_tags(html_message)

                    
        send_mail(
            subject='VideoHub Premium Subscription Activated',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        return f"Confirmation email sent to {user.email}"

    except (User.DoesNotExist, Payment.DoesNotExist, Subscription.DoesNotExist):
        return None
    except Exception as exc:
                                           
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_pending_payments() -> str:
                                                 
    cutoff_time = timezone.now() - timedelta(hours=24)

    old_pending_payments = Payment.objects.filter(
        status='pending',
        created_at__lt=cutoff_time
    )

    count = old_pending_payments.count()
    old_pending_payments.delete()

    return f"Cleaned up {count} old pending payments"


@shared_task
def send_subscription_expiry_reminder() -> str:
                                          
    three_days_from_now = timezone.now() + timedelta(days=3)
    four_days_from_now = timezone.now() + timedelta(days=4)

    expiring_subscriptions = Subscription.objects.filter(
        is_active=True,
        end_date__gte=three_days_from_now,
        end_date__lt=four_days_from_now
    ).select_related('user')

    count = 0
    for subscription in expiring_subscriptions:
        try:
            user = subscription.user

                                  
            context = {
                'user': user,
                'subscription': subscription,
                'days_remaining': subscription.days_remaining(),
            }

            html_message = render_to_string('payment/emails/subscription_expiry_reminder.html', context)
            plain_message = strip_tags(html_message)

                        
            send_mail(
                subject='Your VideoHub Subscription is Expiring Soon',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=True
            )

            count += 1

        except Exception:
            continue

    return f"Sent {count} subscription expiry reminders"