from typing import Optional
from datetime import timedelta
import secrets

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse

from .models import EmailVerificationToken, PasswordResetToken

User = get_user_model()


@shared_task(bind=True, max_retries=3)
def send_verification_email(self, user_id: int) -> Optional[str]:
    """Send email verification link to user asynchronously."""
    try:
        user = User.objects.get(id=user_id)

                               
        token = secrets.token_urlsafe(32)

                                   
        expires_at = timezone.now() + timedelta(hours=24)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

                                                                              
        verification_url = f"{settings.SITE_URL}{reverse('accounts:verify_email', kwargs={'token': token})}"

                              
        context = {
            'user': user,
            'verification_url': verification_url,
            'expiry_hours': 24
        }

        html_message = render_to_string('accounts/emails/verification_email.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject='Verify Your Email - VideoHub',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        return f"Verification email sent to {user.email}"

    except User.DoesNotExist:
        return None
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def send_password_reset_email(self, user_id: int) -> Optional[str]:
    """Send password reset link to user asynchronously."""
    try:
        user = User.objects.get(id=user_id)

        token = secrets.token_urlsafe(32)

        expires_at = timezone.now() + timedelta(hours=1)
        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )

        reset_url = f"{settings.SITE_URL}{reverse('accounts:password_reset_confirm', kwargs={'token': token})}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'expiry_hours': 1
        }

        html_message = render_to_string('accounts/emails/password_reset_email.html', context)
        plain_message = strip_tags(html_message)

                    
        send_mail(
            subject='Password Reset Request - VideoHub',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )

        return f"Password reset email sent to {user.email}"

    except User.DoesNotExist:
        return None
    except Exception as exc:
                                           
        raise self.retry(exc=exc, countdown=60)


@shared_task
def cleanup_expired_tokens() -> str:
    """
    Periodic task to clean up expired verification and password reset tokens.

    This task should be run periodically (e.g., daily) using Celery Beat.

    Returns:
        Message indicating number of tokens deleted
    """
    now = timezone.now()

    expired_email_tokens = EmailVerificationToken.objects.filter(
        expires_at__lt=now
    ).delete()

    expired_password_tokens = PasswordResetToken.objects.filter(
        expires_at__lt=now
    ).delete()

    return (
        f"Deleted {expired_email_tokens[0]} expired email verification tokens "
        f"and {expired_password_tokens[0]} expired password reset tokens"
    )

