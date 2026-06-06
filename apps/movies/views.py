from typing import Any, Dict

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView

from .models import Category, Movie


class MovieListView(ListView):
    """
    View for displaying list of movies with filtering and pagination.
    """

    model = Movie
    template_name = 'movies/home.html'
    context_object_name = 'movies'
    paginate_by = 24

    def get_queryset(self) -> QuerySet:
        """
        Get filtered and sorted queryset of movies.
        """
        queryset = Movie.objects.select_related('category')

                            
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

                        
        year = self.request.GET.get('year')
        if year and year.isdigit():
            queryset = queryset.filter(year=int(year))

                      
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(director__icontains=search_query) |
                Q(actors__icontains=search_query)
            )

              
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = [
            '-created_at', 'created_at',
            'title', '-title',
            'year', '-year',
            '-views_count'
        ]

        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)

                            
        context['categories'] = Category.objects.all()

                                            
        category_slug = self.request.GET.get('category')
        if category_slug:
            context['selected_category'] = get_object_or_404(
                Category,
                slug=category_slug
            )

                                     
        context['search_query'] = self.request.GET.get('q', '')

                                           
        context['available_years'] = Movie.objects.values_list(
            'year',
            flat=True
        ).distinct().order_by('-year')

        return context


class MovieDetailView(DetailView):
    """
    View for displaying single movie details.
    """

    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    slug_url_kwarg = 'slug'

    def get_queryset(self) -> QuerySet:
        """Optimize queryset with related data."""
        return Movie.objects.select_related('category')

    def get_object(self, queryset=None) -> Movie:
        """Get movie object and increment views counter."""
        movie = super().get_object(queryset)

                                                                        
        if not self.request.user.is_staff:
            movie.increment_views()

        return movie

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        movie = self.object

                               
        context['average_rating'] = movie.get_average_rating()
        context['ratings_count'] = movie.get_ratings_count()

                                            
        if self.request.user.is_authenticated:
            try:
                from apps.ratings.models import Rating
                user_rating = Rating.objects.get(
                    movie=movie,
                    user=self.request.user
                )
                context['user_rating'] = user_rating
            except Rating.DoesNotExist:
                context['user_rating'] = None

                                         
            try:
                from apps.ratings.models import Comment
                user_comment = Comment.objects.get(
                    movie=movie,
                    user=self.request.user
                )
                context['user_comment'] = user_comment
            except Comment.DoesNotExist:
                context['user_comment'] = None

                      
        context['comments'] = movie.comments.select_related('user').order_by('-created_at')[:10]

                                            
        context['related_movies'] = Movie.objects.filter(
            category=movie.category
        ).exclude(
            id=movie.id
        ).order_by('?')[:6]

        return context


class CategoryMoviesView(ListView):
    """
    View for displaying movies in a specific category.
    """

    model = Movie
    template_name = 'movies/category_movies.html'
    context_object_name = 'movies'
    paginate_by = 24

    def get_queryset(self) -> QuerySet:
        """Get movies filtered by category."""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Movie.objects.filter(
            category=self.category
        ).select_related('category')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """Add category to context."""
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.all()
        return context


def search_movies(request: HttpRequest) -> HttpResponse:
    """
    View for searching movies.
    """
    query = request.GET.get('q', '')
    movies = []

    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(director__icontains=query) |
            Q(actors__icontains=query)
        ).select_related('category')[:20]

    context = {
        'movies': movies,
        'query': query,
        'categories': Category.objects.all()
    }

    return render(request, 'movies/search_results.html', context)
