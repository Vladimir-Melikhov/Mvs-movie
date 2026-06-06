from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import StripeCustomer, Payment, WebhookEvent


@admin.register(StripeCustomer)
class StripeCustomerAdmin(admin.ModelAdmin):
    """Admin interface for StripeCustomer model."""

    list_display = (
        'user',
        'stripe_customer_id',
        'created_at'
    )

    list_filter = ('created_at',)

    search_fields = (
        'user__username',
        'user__email',
        'stripe_customer_id'
    )

    readonly_fields = ('stripe_customer_id', 'created_at', 'updated_at')

    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': ('user', 'stripe_customer_id')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin interface for Payment model."""

    list_display = (
        'user',
        'amount_display',
        'status_display',
        'subscription_months',
        'created_at',
        'completed_at'
    )

    list_filter = (
        'status',
        'currency',
        'subscription_months',
        'created_at',
        'completed_at'
    )

    search_fields = (
        'user__username',
        'user__email',
        'stripe_payment_intent_id',
        'stripe_checkout_session_id'
    )

    readonly_fields = (
        'stripe_payment_intent_id',
        'stripe_checkout_session_id',
        'created_at',
        'updated_at',
        'completed_at',
        'metadata'
    )

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'status')
        }),
        (_('Stripe Information'), {
            'fields': (
                'stripe_payment_intent_id',
                'stripe_checkout_session_id'
            )
        }),
        (_('Payment Details'), {
            'fields': (
                'amount',
                'currency',
                'subscription_months',
                'description'
            )
        }),
        (_('Metadata'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

    def amount_display(self, obj):
        """Display formatted amount."""
        return format_html(
            '<span style="font-weight: bold;">${}</span>',
            obj.amount
        )

    amount_display.short_description = _('Amount')

    def status_display(self, obj):
        """Display colored status badge."""
        colors = {
            'pending': '#f59e0b',
            'processing': '#3b82f6',
            'succeeded': '#10b981',
            'failed': '#ef4444',
            'canceled': '#6b7280',
            'refunded': '#8b5cf6',
        }

        color = colors.get(obj.status, '#6b7280')

        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 12px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_display.short_description = _('Status')


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    """Admin interface for WebhookEvent model."""

    list_display = (
        'stripe_event_id',
        'event_type',
        'processed_display',
        'created_at',
        'processed_at'
    )

    list_filter = (
        'processed',
        'event_type',
        'created_at'
    )

    search_fields = (
        'stripe_event_id',
        'event_type',
        'processing_error'
    )

    readonly_fields = (
        'stripe_event_id',
        'event_type',
        'payload',
        'created_at',
        'processed_at',
        'processing_error'
    )

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('stripe_event_id', 'event_type', 'processed')
        }),
        (_('Payload'), {
            'fields': ('payload',),
            'classes': ('collapse',)
        }),
        (_('Processing'), {
            'fields': ('processing_error',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )

    def processed_display(self, obj):
        """Display processed status."""
        if obj.processed:
            if obj.processing_error:
                return format_html(
                    '<span style="color: #ef4444;">✗ Failed</span>'
                )
            else:
                return format_html(
                    '<span style="color: #10b981;">✓ Processed</span>'
                )
        else:
            return format_html(
                '<span style="color: #f59e0b;">⏳ Pending</span>'
            )

    processed_display.short_description = _('Status')
