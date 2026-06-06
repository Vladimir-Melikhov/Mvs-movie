from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, EmailVerificationToken, PasswordResetToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model.

    Extends Django's UserAdmin with custom fields and filters.
    """

    list_display = (
        'username', 
        'email', 
        'first_name', 
        'last_name', 
        'email_verified',
        'is_staff',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'email_verified',
        'created_at'
    )

    search_fields = ('username', 'email', 'first_name', 'last_name')

    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'avatar')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'email_verified',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'is_staff',
                'is_active'
            ),
        }),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related()


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for EmailVerificationToken model.
    """

    list_display = (
        'user',
        'token',
        'created_at',
        'expires_at',
        'is_used',
        'is_expired'
    )

    list_filter = ('is_used', 'created_at', 'expires_at')

    search_fields = ('user__username', 'user__email', 'token')

    readonly_fields = ('token', 'created_at', 'expires_at')

    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """
    Admin interface for PasswordResetToken model.
    """

    list_display = (
        'user',
        'token',
        'created_at',
        'expires_at',
        'is_used',
        'is_expired'
    )

    list_filter = ('is_used', 'created_at', 'expires_at')

    search_fields = ('user__username', 'user__email', 'token')

    readonly_fields = ('token', 'created_at', 'expires_at')

    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('user')

