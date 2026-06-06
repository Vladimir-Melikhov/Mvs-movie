from django.db import models
from django.db.models import Avg, Count, Q


class MovieQuerySet(models.QuerySet):
    """Custom QuerySet for Movie model."""

    def with_ratings(self):
        """Annotate queryset with rating statistics."""
        return self.annotate(
            avg_rating=Avg('ratings__score'),
            ratings_count=Count('ratings', distinct=True),
            comments_count=Count('comments', distinct=True)
        )

    def by_category(self, category_slug: str):
        """Filter movies by category slug."""
        return self.filter(category__slug=category_slug)

    def by_year(self, year: int):
        """Filter movies by year."""
        return self.filter(year=year)

    def search(self, query: str):
        """Search movies by title, description, director, or actors."""
        return self.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(director__icontains=query) |
            Q(actors__icontains=query)
        )

    def popular(self):
        """Return movies ordered by views count."""
        return self.order_by('-views_count')

    def top_rated(self):
        """Return movies ordered by average rating."""
        return self.with_ratings().order_by('-avg_rating')

    def recent(self):
        """Return recently added movies."""
        return self.order_by('-created_at')


class MovieManager(models.Manager):
    """Custom manager for Movie model."""

    def get_queryset(self):
        """Return custom queryset."""
        return MovieQuerySet(self.model, using=self._db)

    def with_ratings(self):
        """Get movies with rating statistics."""
        return self.get_queryset().with_ratings()

    def by_category(self, category_slug: str):
        """Get movies by category."""
        return self.get_queryset().by_category(category_slug)

    def search(self, query: str):
        """Search movies."""
        return self.get_queryset().search(query)

    def popular(self):
        """Get popular movies."""
        return self.get_queryset().popular()

    def top_rated(self):
        """Get top rated movies."""
        return self.get_queryset().top_rated()

    def recent(self):
        """Get recent movies."""
        return self.get_queryset().recent()
