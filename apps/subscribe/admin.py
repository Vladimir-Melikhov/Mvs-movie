from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Subscription, DailyWatchLimit


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for Subscription model."""

    list_display = (
        'user',
        'start_date',
        'end_date',
        'days_remaining_display',
        'is_active',
        'status_display',
        'created_at'
    )

    list_filter = (
        'is_active',
        'start_date',
        'end_date',
        'created_at'
    )

    search_fields = (
        'user__username',
        'user__email'
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'start_date', 'end_date', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

    def days_remaining_display(self, obj):
        """Display days remaining"""
        days = obj.days_remaining()
        if days == 0:
            return format_html('<span style="color: #dc2626;">Expired</span>')
        elif days <= 7:
            return format_html('<span style="color: #f59e0b;">{} days</span>', days)
        else:
            return format_html('<span style="color: #10b981;">{} days</span>', days)

    days_remaining_display.short_description = _('Days Remaining')

    def status_display(self, obj):
        """Display subscription status"""
        if obj.is_active and not obj.is_expired():
            return format_html('<span style="color: #10b981; font-weight: bold;">✓ Active</span>')
        elif obj.is_expired():
            return format_html('<span style="color: #dc2626; font-weight: bold;">✗ Expired</span>')
        else:
            return format_html('<span style="color: #6b7280;">Inactive</span>')

    status_display.short_description = _('Status')


@admin.register(DailyWatchLimit)
class DailyWatchLimitAdmin(admin.ModelAdmin):
    """Admin interface for DailyWatchLimit model."""

    list_display = (
        'user',
        'date',
        'watched_display',
        'remaining_display',
        'limit_reached_display',
        'updated_at'
    )

    list_filter = (
        'date',
        'created_at'
    )

    search_fields = (
        'user__username',
        'user__email'
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-date', '-updated_at')

    date_hierarchy = 'date'

    fieldsets = (
        (None, {
            'fields': ('user', 'date', 'watched_seconds')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')

    def watched_display(self, obj):
        """Display watched time in minutes"""
        minutes = obj.get_watched_minutes()
        return f"{minutes} min"

    watched_display.short_description = _('Watched')

    def remaining_display(self, obj):
        """Display remaining time"""
        remaining = obj.get_remaining_seconds()
        minutes = remaining // 60
        if obj.is_limit_reached():
            return format_html('<span style="color: #dc2626;">0 min</span>')
        elif minutes <= 10:
            return format_html('<span style="color: #f59e0b;">{} min</span>', minutes)
        else:
            return format_html('<span style="color: #10b981;">{} min</span>', minutes)

    remaining_display.short_description = _('Remaining')

    def limit_reached_display(self, obj):
        """Display if limit is reached"""
        if obj.is_limit_reached():
            return format_html('<span style="color: #dc2626;">✓ Reached</span>')
        else:
            return format_html('<span style="color: #10b981;">✗ Not Reached</span>')

    limit_reached_display.short_description = _('Limit Reached')
