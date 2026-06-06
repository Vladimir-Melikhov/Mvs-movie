                      
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Category, Movie


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'slug',
        'order',
        'movies_count',
        'created_at'
    )

    list_filter = ('created_at',)

    search_fields = ('name', 'description')

    prepopulated_fields = {'slug': ('name',)}

    ordering = ('order', 'name')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'order')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at')

    def movies_count(self, obj):
        """Display number of movies in category."""
        return obj.get_movies_count()

    movies_count.short_description = _('Movies Count')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'category',
        'year',
        'duration_display',
        'mpaa_rating',
        'average_rating',
        'ratings_count',
        'views_count',
        'poster_preview',
        'created_at'
    )

    list_filter = (
        'category',
        'year',
        'mpaa_rating',
        'created_at'
    )

    search_fields = (
        'title',
        'description',
        'director',
        'actors',
        'country'
    )

    prepopulated_fields = {'slug': ('title',)}

    ordering = ('-created_at',)

    date_hierarchy = 'created_at'

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'description', 'category')
        }),
        (_('Details'), {
            'fields': ('year', 'duration', 'director', 'actors', 'mpaa_rating', 'country')
        }),
        (_('Media'), {
            'fields': ('poster', 'video_url', 'video_file')
        }),
        (_('Statistics'), {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'views_count')

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('category')

    def poster_preview(self, obj):
        """Display poster preview in admin."""
        if obj.poster:
            return format_html(
                '<img src="{}" width="50" height="75" style="object-fit: cover;" />',
                obj.poster.url
            )
        return '-'

    poster_preview.short_description = _('Poster')

    def duration_display(self, obj):
        """Display formatted duration."""
        return obj.get_duration_display()

    duration_display.short_description = _('Duration')

    def average_rating(self, obj):
        """Display average rating."""
        avg = obj.get_average_rating()
        if avg > 0:
            return format_html(
                '<span style="color: #10b981; font-weight: bold;">{}</span> ⭐',
                avg
            )
        return '-'

    average_rating.short_description = _('Avg Rating')

    def ratings_count(self, obj):
        """Display number of ratings."""
        return obj.get_ratings_count()

    ratings_count.short_description = _('Ratings')