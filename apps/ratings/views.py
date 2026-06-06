from typing import Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy

from apps.movies.models import Movie
from .models import Rating, Comment
from .forms import RatingForm, CommentForm


@login_required
def add_or_update_rating(request: HttpRequest, movie_slug: str) -> HttpResponse:
    movie = get_object_or_404(Movie, slug=movie_slug)

    try:
        rating = Rating.objects.get(user=request.user, movie=movie)
        is_update = True
    except Rating.DoesNotExist:
        rating = None
        is_update = False

    if request.method == 'POST':
        form = RatingForm(
            request.POST,
            instance=rating,
            user=request.user,
            movie=movie
        )

        if form.is_valid():
            form.save()

            if is_update:
                messages.success(request, _('Your rating has been updated.'))
            else:
                messages.success(request, _('Your rating has been saved.'))

            return redirect('movies:movie_detail', slug=movie_slug)
    else:
        form = RatingForm(instance=rating, user=request.user, movie=movie)

    return render(request, 'ratings/rating_form.html', {
        'form': form,
        'movie': movie,
        'is_update': is_update
    })


@login_required
def delete_rating(request: HttpRequest, rating_id: int) -> HttpResponse:
    rating = get_object_or_404(Rating, id=rating_id, user=request.user)
    movie_slug = rating.movie.slug

    if request.method == 'POST':
        rating.delete()
        messages.success(request, _('Your rating has been deleted.'))
        return redirect('movies:movie_detail', slug=movie_slug)

    return render(request, 'ratings/rating_confirm_delete.html', {
        'rating': rating
    })


@login_required
def add_or_update_comment(request: HttpRequest, movie_slug: str) -> HttpResponse:
    movie = get_object_or_404(Movie, slug=movie_slug)

    try:
        comment = Comment.objects.get(user=request.user, movie=movie)
        is_update = True
    except Comment.DoesNotExist:
        comment = None
        is_update = False

    if request.method == 'POST':
        form = CommentForm(
            request.POST,
            instance=comment,
            user=request.user,
            movie=movie
        )

        if form.is_valid():
            form.save()

            if is_update:
                messages.success(request, _('Your comment has been updated.'))
            else:
                messages.success(request, _('Your comment has been posted.'))

            return redirect('movies:movie_detail', slug=movie_slug)
    else:
        form = CommentForm(instance=comment, user=request.user, movie=movie)

    return render(request, 'ratings/comment_form.html', {
        'form': form,
        'movie': movie,
        'is_update': is_update
    })


@login_required
def delete_comment(request: HttpRequest, comment_id: int) -> HttpResponse:
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    movie_slug = comment.movie.slug

    if request.method == 'POST':
        comment.delete()
        messages.success(request, _('Your comment has been deleted.'))
        return redirect('movies:movie_detail', slug=movie_slug)

    return render(request, 'ratings/comment_confirm_delete.html', {
        'comment': comment
    })


class UserRatingsListView(LoginRequiredMixin, ListView):
    model = Rating
    template_name = 'ratings/user_ratings.html'
    context_object_name = 'ratings'
    paginate_by = 20

    def get_queryset(self):
        """Get ratings for current user."""
        queryset = Rating.objects.filter(
            user=self.request.user
        ).select_related('movie', 'movie__category')

                       
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = [
            '-created_at', 'created_at',
            '-score', 'score',
            'movie__title', '-movie__title'
        ]

        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)

                         
        filter_by = self.request.GET.get('filter')
        if filter_by:
            if filter_by == '10':
                queryset = queryset.filter(score=10)
            elif filter_by == '9-10':
                queryset = queryset.filter(score__gte=9)
            elif filter_by == '7-8':
                queryset = queryset.filter(score__gte=7, score__lte=8)
            elif filter_by == '5-6':
                queryset = queryset.filter(score__gte=5, score__lte=6)
            elif filter_by == '1-4':
                queryset = queryset.filter(score__lte=4)

        return queryset
