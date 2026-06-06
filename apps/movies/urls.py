from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.MovieListView.as_view(), name='home'),
    path('movie/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('category/<slug:slug>/', views.CategoryMoviesView.as_view(), name='category'),
    path('search/', views.search_movies, name='search'),
]