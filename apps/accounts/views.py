from typing import Any, Dict

from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordResetView,
)
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DetailView

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    CustomPasswordResetForm,
    CustomSetPasswordForm,
    UserProfileUpdateForm
)
from .models import EmailVerificationToken, PasswordResetToken
from .tasks import send_verification_email, send_password_reset_email

User = get_user_model()


class UserRegistrationView(CreateView):
    """
    View for user registration.
    """

    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:registration_complete')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Redirect authenticated users to home page."""
        if request.user.is_authenticated:
            return redirect('accounts:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: UserRegistrationForm) -> HttpResponse:
        """Save user and send verification email."""
        user = form.save()

                                                
        send_verification_email.delay(user.id)

        messages.success(
            self.request,
            _('Registration successful! Please check your email to verify your account.')
        )

        return super().form_valid(form)

    def form_invalid(self, form: UserRegistrationForm) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(
            self.request,
            _('Please correct the errors below.')
        )
        return super().form_invalid(form)


class UserLoginView(LoginView):
    """
    View for user login.
    """

    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form: UserLoginForm) -> HttpResponse:
        """Handle successful login with 'remember me' functionality."""
        remember_me = form.cleaned_data.get('remember_me')

        if not remember_me:
                                                       
            self.request.session.set_expiry(0)
        else:
                                              
            self.request.session.set_expiry(1209600)                      

        return super().form_valid(form)

    def form_invalid(self, form: UserLoginForm) -> HttpResponse:
        """Handle invalid login attempt."""
        messages.error(
            self.request,
            _('Invalid username/email or password.')
        )
        return super().form_invalid(form)


class UserLogoutView(LogoutView):
    """View for user logout."""

    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Add logout message."""
        if request.user.is_authenticated:
            messages.info(request, _('You have been logged out successfully.'))
        return super().dispatch(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """
    Custom password reset view.

    Sends password reset email asynchronously using Celery.
    """

    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'

    def form_valid(self, form: CustomPasswordResetForm) -> HttpResponse:
        """Send password reset email asynchronously."""
        email = form.cleaned_data['email']
        user = User.objects.get(email=email)

                                                  
        send_password_reset_email.delay(user.id)

        messages.success(
            self.request,
            _('Password reset link has been sent to your email.')
        )

        return redirect(self.success_url)


class CustomPasswordResetConfirmView(View):
    """
    Custom password reset confirm view.
    """

    template_name = 'accounts/password_reset_confirm.html'

    def get(self, request, token):
        """Display the password reset form."""
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token,
                is_used=False
            )

            if reset_token.is_expired():
                messages.error(
                    request,
                    _('This password reset link has expired. Please request a new one.')
                )
                return render(request, self.template_name, {'validlink': False})

            form = CustomSetPasswordForm(user=reset_token.user)
            return render(request, self.template_name, {
                'form': form,
                'validlink': True,
                'token': token
            })

        except PasswordResetToken.DoesNotExist:
            messages.error(
                request,
                _('Invalid password reset link.')
            )
            return render(request, self.template_name, {'validlink': False})

    def post(self, request, token):
        """Process the password reset form."""
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token,
                is_used=False
            )

            if reset_token.is_expired():
                messages.error(
                    request,
                    _('This password reset link has expired. Please request a new one.')
                )
                return render(request, self.template_name, {'validlink': False})

            form = CustomSetPasswordForm(user=reset_token.user, data=request.POST)

            if form.is_valid():
                                       
                form.save()

                                    
                reset_token.mark_as_used()

                messages.success(
                    request,
                    _('Your password has been reset successfully. You can now login with your new password.')
                )

                return redirect('accounts:password_reset_complete')

            return render(request, self.template_name, {
                'form': form,
                'validlink': True,
                'token': token
            })

        except PasswordResetToken.DoesNotExist:
            messages.error(
                request,
                _('Invalid password reset link.')
            )
            return render(request, self.template_name, {'validlink': False})


class UserProfileView(DetailView):
    """
    View for displaying user profile.
    """

    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        user = self.object

                                  
        from apps.ratings.models import Rating, Comment
        context['ratings'] = Rating.objects.filter(user=user).select_related('movie')[:5]
        context['comments'] = Comment.objects.filter(user=user).select_related('movie')[:5]

        return context


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating user profile.

    Allows users to update their profile information and password.
    """

    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_update.html'

    def get_object(self, queryset=None) -> User:
        """Return the current user."""
        return self.request.user

    def get_success_url(self) -> str:
        """Redirect to user's profile after successful update."""
        return reverse_lazy('accounts:profile', kwargs={'username': self.request.user.username})

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Handle POST request for both profile and password forms."""
        self.object = self.get_object()
        form_type = request.POST.get('form_type')

        if form_type == 'password':
                                    
            password_form = PasswordChangeForm(user=request.user, data=request.POST)

            if password_form.is_valid():
                password_form.save()
                                                  
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, password_form.user)
                messages.success(request, _('Your password has been changed successfully.'))
                return redirect(self.get_success_url())
            else:
                messages.error(request, _('Please correct the errors in the password form.'))
                profile_form = self.form_class(instance=self.object)
                return self.render_to_response(self.get_context_data(
                    form=profile_form,
                    password_form=password_form
                ))
        else:
                                              
            form = self.form_class(request.POST, request.FILES, instance=self.object)
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add password form to context."""
        context = super().get_context_data(**kwargs)
        if 'password_form' not in context:
            context['password_form'] = PasswordChangeForm(user=self.request.user)
        return context

    def form_valid(self, form: UserProfileUpdateForm) -> HttpResponse:
        """Handle successful profile update."""
        messages.success(
            self.request,
            _('Your profile has been updated successfully.')
        )
        return super().form_valid(form)

    def form_invalid(self, form: UserProfileUpdateForm) -> HttpResponse:
        """Handle invalid form submission."""
        messages.error(
            self.request,
            _('Please correct the errors below.')
        )
        return super().form_invalid(form)


def verify_email(request: HttpRequest, token: str) -> HttpResponse:
    """
    View for email verification.
    """
    try:
        verification_token = EmailVerificationToken.objects.select_related('user').get(
            token=token,
            is_used=False
        )

        if verification_token.is_expired():
            messages.error(
                request,
                _('This verification link has expired. Please request a new one.')
            )
            return redirect('accounts:resend_verification')

                                 
        user = verification_token.user
        user.email_verified = True
        user.save(update_fields=['email_verified'])

                            
        verification_token.mark_as_used()

        messages.success(
            request,
            _('Your email has been verified successfully! You can now login.')
        )

        return redirect('accounts:login')

    except EmailVerificationToken.DoesNotExist:
        messages.error(
            request,
            _('Invalid verification link.')
        )
        return redirect('accounts:login')


@login_required
def resend_verification_email(request: HttpRequest) -> HttpResponse:
    """
    View for resending verification email.
    """
    user = request.user

    if user.email_verified:
        messages.info(
            request,
            _('Your email is already verified.')
        )
        return redirect('accounts:profile', username=user.username)

    send_verification_email.delay(user.id)

    messages.success(
        request,
        _('A new verification email has been sent to your email address.')
    )

    return redirect('accounts:profile', username=user.username)


def registration_complete(request: HttpRequest) -> HttpResponse:
    """
    View for registration complete page.

    Shows a message after successful registration.
    """
    return render(request, 'accounts/registration_complete.html')


def password_reset_done(request: HttpRequest) -> HttpResponse:
    """
    View for password reset done page.

    Shows a message after password reset email has been sent.
    """
    return render(request, 'accounts/password_reset_done.html')


def password_reset_complete(request: HttpRequest) -> HttpResponse:
    """
    View for password reset complete page.
    """
    return render(request, 'accounts/password_reset_complete.html')
