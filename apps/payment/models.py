from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class StripeCustomer(models.Model):
    """
    Model to store Stripe customer information.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='stripe_customer',
        verbose_name=_('user')
    )

    stripe_customer_id = models.CharField(
        _('Stripe customer ID'),
        max_length=255,
        unique=True,
        help_text=_('Stripe customer identifier')
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
        verbose_name = _('Stripe customer')
        verbose_name_plural = _('Stripe customers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['stripe_customer_id']),
        ]

    def __str__(self) -> str:
        return f"Stripe Customer: {self.user.username}"


class Payment(models.Model):
    """
    Model to track payment transactions.

    Stores information about each payment attempt and its status.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name=_('user')
    )

    stripe_payment_intent_id = models.CharField(
        _('Stripe payment intent ID'),
        max_length=255,
        unique=True,
        help_text=_('Stripe PaymentIntent identifier')
    )

    stripe_checkout_session_id = models.CharField(
        _('Stripe checkout session ID'),
        max_length=255,
        blank=True,
        help_text=_('Stripe Checkout Session identifier')
    )

    amount = models.DecimalField(
        _('amount'),
        max_digits=10,
        decimal_places=2,
        help_text=_('Payment amount in USD')
    )

    currency = models.CharField(
        _('currency'),
        max_length=3,
        default='USD',
        help_text=_('Payment currency code')
    )

    status = models.CharField(
        _('status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_('Payment status')
    )

    subscription_months = models.IntegerField(
        _('subscription months'),
        default=1,
        help_text=_('Number of subscription months')
    )

    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Payment description')
    )

    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Additional payment metadata')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )

    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('When the payment was completed')
    )

    class Meta:
        verbose_name = _('payment')
        verbose_name_plural = _('payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['stripe_payment_intent_id']),
            models.Index(fields=['stripe_checkout_session_id']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"Payment {self.stripe_payment_intent_id} - {self.user.username} - ${self.amount}"

    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == 'succeeded'

    def mark_as_succeeded(self) -> None:
        """Mark payment as succeeded."""
        from django.utils import timezone
        self.status = 'succeeded'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    def mark_as_failed(self) -> None:
        """Mark payment as failed."""
        self.status = 'failed'
        self.save(update_fields=['status', 'updated_at'])


class WebhookEvent(models.Model):
    """
    Model to track Stripe webhook events.

    Stores all webhook events for debugging and auditing purposes.
    """

    stripe_event_id = models.CharField(
        _('Stripe event ID'),
        max_length=255,
        unique=True,
        help_text=_('Stripe event identifier')
    )

    event_type = models.CharField(
        _('event type'),
        max_length=100,
        help_text=_('Type of webhook event')
    )

    payload = models.JSONField(
        _('payload'),
        help_text=_('Full webhook payload')
    )

    processed = models.BooleanField(
        _('processed'),
        default=False,
        help_text=_('Whether the event was processed')
    )

    processing_error = models.TextField(
        _('processing error'),
        blank=True,
        help_text=_('Error message if processing failed')
    )

    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )

    processed_at = models.DateTimeField(
        _('processed at'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _('webhook event')
        verbose_name_plural = _('webhook events')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stripe_event_id']),
            models.Index(fields=['event_type']),
            models.Index(fields=['processed']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self) -> str:
        return f"{self.event_type} - {self.stripe_event_id}"

    def mark_as_processed(self) -> None:
        """Mark webhook event as processed."""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.save(update_fields=['processed', 'processed_at'])

    def mark_as_failed(self, error_message: str) -> None:
        """Mark webhook event as failed."""
        from django.utils import timezone
        self.processed = True
        self.processed_at = timezone.now()
        self.processing_error = error_message
        self.save(update_fields=['processed', 'processed_at', 'processing_error'])