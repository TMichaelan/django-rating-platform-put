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
    path('user_commented_movies/', views.CommentedMoviesView.as_view(), name='user_commented_movies'),
    path('search/', views.search_results, name='search_results'),
    path('delete_comment/<int:comment_id>/', views.DeleteCommentView.as_view(), name='delete_comment'),
    path('delete_rating/<int:rating_id>/', views.DeleteRatingView.as_view(), name='delete_rating'),
    path('add_movie_admin/', views.add_movie_admin, name='add_movie_admin'),
    path('edit_movie_admin/<int:movie_id>/', views.edit_movie_admin, name='edit_movie_admin'),
    path('delete_movie/<int:movie_id>/', views.delete_movie_admin, name='delete_movie_admin'),
]
