from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Rating, Movie,Comment,ImdbRating

class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
        return user
    
class UserForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ("username", "password")
    

class RatingForm(forms.ModelForm):
    movie = forms.ModelChoiceField(queryset=Movie.objects.all())

    class Meta:
        model = Rating
        fields = ['movie', 'value']

class UserRatingForm(forms.ModelForm):
    value = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Rating
        fields = ['value']
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['user_review']

class AddMovieForm(forms.ModelForm):
    audience_rating = forms.FloatField(required=False,min_value=0, max_value=10)
    critic_rating = forms.FloatField(required=False,min_value=0, max_value=10)

    class Meta:
        model = Movie
        fields = ['title', 'imdb_url', 'year', 'img_url','genres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            imdb_rating = getattr(self.instance, 'imdbrating', None)
            if imdb_rating:
                self.fields['audience_rating'].initial = imdb_rating.audience_rating
                self.fields['critic_rating'].initial = imdb_rating.critic_rating

    def save(self, commit=True):
        movie = super().save(commit)
        audience_rating = self.cleaned_data.get('audience_rating')
        critic_rating = self.cleaned_data.get('critic_rating')
        if audience_rating is not None and critic_rating is not None:
            ImdbRating.objects.update_or_create(
                movie=movie,
                defaults={'audience_rating': audience_rating, 'critic_rating': critic_rating}
            )
        return movie