from django.urls import path
from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("genre/<int:pk>", views.GenreView.as_view(), name="genre"),
    path("movie/<int:pk>", views.MovieView.as_view(), name="movie"),
    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    path('rated_movies/', views.rated_movies, name='rated_movies'),
    path('user_rated_movies/', views.RatedMoviesView.as_view(), name='user_rated_movies'),
    path('search/', views.search_results, name='search_results'),
]
