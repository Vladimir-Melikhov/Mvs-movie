from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Rating, Comment


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'movie',
        'score',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'score',
        'created_at',
        'updated_at'
    )

    search_fields = (
        'user__username',
        'user__email',
        'movie__title'
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'movie', 'score')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'movie')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'movie',
        'text_preview',
        'is_edited_display',
        'created_at',
        'updated_at'
    )

    list_filter = (
        'created_at',
        'updated_at'
    )

    search_fields = (
        'user__username',
        'user__email',
        'movie__title',
        'text'
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (None, {
            'fields': ('user', 'movie', 'text')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'movie')

    def text_preview(self, obj):
        """Display preview of comment text."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text

    text_preview.short_description = _('Comment Preview')

    def is_edited_display(self, obj):
        """Display if comment was edited."""
        return '✓' if obj.is_edited() else '✗'

    is_edited_display.short_description = _('Edited')
    is_edited_display.boolean = True
