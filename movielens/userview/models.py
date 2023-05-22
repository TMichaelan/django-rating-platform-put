from django.db import models
from django.conf import settings

class Genre(models.Model):
    name = models.CharField(max_length=300)

    def __str__(self):
        return self.name
    
class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=1000)
    imdb_url = models.CharField(max_length=100, default='N/A')  # Use 'N/A' as a default IMDB ID
    year = models.IntegerField(default=0)  # Assuming year is an integer
    img_url = models.URLField(max_length=600, default='N/A')  # Assuming URL is a string of max 200 chars
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title

class Rating(models.Model):
    value = models.IntegerField(default=0)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = [['user', 'movie']]

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user_review = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ImdbRating(models.Model):
    audience_rating = models.FloatField()
    critic_rating = models.FloatField()
    movie = models.OneToOneField(Movie, on_delete=models.CASCADE)