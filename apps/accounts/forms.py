from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """
    Form for user registration.
    """
    
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    username = forms.CharField(
        label=_('Username'),
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    
    password1 = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (min 8 characters)'
        }),
        help_text=_(
            'Your password must contain at least 8 characters and '
            'cannot be entirely numeric.'
        )
    )
    
    password2 = forms.CharField(
        label=_('Confirm Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        help_text=_('Enter the same password as before, for verification.')
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self) -> str:
        """Validate that the email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _('A user with this email already exists.'),
                code='email_exists'
            )
        return email.lower()
    
    def clean_username(self) -> str:
        """Validate username."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(
                _('A user with this username already exists.'),
                code='username_exists'
            )
        return username
    
    def save(self, commit: bool = True) -> User:
        """Save the user with email verification status set to False."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.email_verified = False
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Form for user login.
    """

    username = forms.CharField(
        label=_('Username or Email'),
        max_length=254,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email',
            'autofocus': True
        })
    )

    password = forms.CharField(
        label=_('Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    remember_me = forms.BooleanField(
        label=_('Remember me'),
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def clean_username(self) -> str:
        """Allow login with email or username."""
        username_or_email = self.cleaned_data.get('username')

        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email.lower())
                return user.username
            except User.DoesNotExist:
                pass
        
        return username_or_email


class CustomPasswordResetForm(PasswordResetForm):
    """
    Custom password reset form.
    """

    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self) -> str:
        """Validate that a user with this email exists."""
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email.lower()).exists():
            raise ValidationError(
                _('No user found with this email address.'),
                code='email_not_found'
            )
        return email.lower()


class CustomSetPasswordForm(SetPasswordForm):
    """
    Custom set password form.
    
    Used for setting a new password after password reset.
    """
    
    new_password1 = forms.CharField(
        label=_('New Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        }),
        help_text=_(
            'Your password must contain at least 8 characters and '
            'cannot be entirely numeric.'
        )
    )
    
    new_password2 = forms.CharField(
        label=_('Confirm New Password'),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )


class UserProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    """
    
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )

    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
 
    bio = forms.CharField(
        label=_('Biography'),
        max_length=500,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Tell us about yourself',
            'rows': 4
        })
    )

    avatar = forms.ImageField(
        label=_('Avatar'),
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'avatar')

    def clean_avatar(self):
        """Validate avatar file size and type."""
        avatar = self.cleaned_data.get('avatar')

        if avatar:
                                       
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError(
                    _('Avatar file size cannot exceed 5MB.'),
                    code='file_too_large'
                )

                             
            if not avatar.content_type.startswith('image/'):
                raise ValidationError(
                    _('Only image files are allowed.'),
                    code='invalid_file_type'
                )

        return avatar
