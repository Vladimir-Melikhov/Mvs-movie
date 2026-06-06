from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


class EmailVerificationRequiredMixin:
    """Mixin that requires user's email to be verified."""

    verification_url = reverse_lazy('accounts:resend_verification')

    def dispatch(self, request, *args, **kwargs):
        """Check if user's email is verified."""
        if request.user.is_authenticated and not request.user.email_verified:
            messages.warning(
                request,
                'Please verify your email address to access this page.'
            )
            return redirect(self.verification_url)
        return super().dispatch(request, *args, **kwargs)


class AjaxResponseMixin:
    """Mixin to add AJAX support to views."""

    def is_ajax(self):
        """Check if request is AJAX/HTMX request."""
        return (
            self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            self.request.headers.get('HX-Request') == 'true'
        )
