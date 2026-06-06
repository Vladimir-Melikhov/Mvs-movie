from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Rating, Comment


class RatingForm(forms.ModelForm):

    score = forms.IntegerField(
        label=_('Rating'),
        min_value=1,
        max_value=10,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rate from 1 to 10'
        })
    )

    class Meta:
        model = Rating
        fields = ('score',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.movie = kwargs.pop('movie', None)
        super().__init__(*args, **kwargs)

    def clean_score(self):
        score = self.cleaned_data.get('score')
        if score < 1 or score > 10:
            raise ValidationError(
                _('Score must be between 1 and 10.'),
                code='invalid_score'
            )
        return score

    def save(self, commit=True):
        """Save the rating with user and movie."""
        rating = super().save(commit=False)
        if self.user:
            rating.user = self.user
        if self.movie:
            rating.movie = self.movie
        if commit:
            rating.save()
        return rating


class CommentForm(forms.ModelForm):
    """
    Form for creating/updating movie comments.
    """

    text = forms.CharField(
        label=_('Comment'),
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Share your thoughts about this movie...',
            'rows': 4
        })
    )

    class Meta:
        model = Comment
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.movie = kwargs.pop('movie', None)
        super().__init__(*args, **kwargs)

    def clean_text(self):
        """Validate comment text."""
        text = self.cleaned_data.get('text')
        if len(text.strip()) < 10:
            raise ValidationError(
                _('Comment must be at least 10 characters long.'),
                code='text_too_short'
            )
        return text.strip()

    def save(self, commit=True):
        """Save the comment with user and movie."""
        comment = super().save(commit=False)
        if self.user:
            comment.user = self.user
        if self.movie:
            comment.movie = self.movie
        if commit:
            comment.save()
        return comment
