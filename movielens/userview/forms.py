from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import Rating, Movie

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
