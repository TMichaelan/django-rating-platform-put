from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.contrib import messages
from userview.forms import UserForm, RatingForm, UserRatingForm, CommentForm,AddMovieForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg
from userview.forms import NewUserForm
from .models import Movie,Genre,Rating,Comment
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.views import View,generic
from bs4 import BeautifulSoup
import requests

def index(request : HttpRequest):
    movies = Movie.objects.order_by('-title')
    template = loader.get_template('userview/index.html')
    context = {
    'movies' : movies
    }
    return HttpResponse(template.render(context,request))

def view_movie(request: HttpRequest, movie_id):
    response = 'you are looking at the movie with an id %s'
    return HttpResponse(response % movie_id)

def view_genre(request: HttpRequest, genre_id):
    response = 'you are looking at the genre with an id %s'
    return HttpResponse(response % genre_id)

class IndexView(generic.ListView):
    paginate_by = 12

    template_name = 'userview/index.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.order_by('-title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_comments = list(Comment.objects.order_by('-timestamp').values_list('movie_id', flat=True)[:10])
        recent_ratings = list(Rating.objects.order_by('-id').values_list('movie_id', flat=True)[:10])
        context['recent_movies'] = Movie.objects.filter(
            id__in=set(recent_comments + recent_ratings)
        )
        context['recent_movies'] = context['recent_movies'][:8]
        return context
    
class MovieView(generic.DetailView):
    model = Movie
    template_name = 'userview/movie.html'

    context_object_name = 'movies_list'
    paginate_by = 1
    
    def get_queryset(self):
        object_list = Movie.objects.all()
        paginator = Paginator(object_list, self.paginate_by)

        page_num = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)

        print(page_obj)

        return page_obj.object_list

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        object_list = Movie.objects.all()
        paginator = Paginator(object_list, self.paginate_by)

        page_num = self.request.GET.get('page')
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)

        context['page_obj'] = page_obj
        return context
    
def img_gallery_parser(imdb_url):
    
    url = f"https://www.imdb.com/title/{imdb_url}/mediaindex"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    article_block = soup.find('div', class_='article')
    try:
        image_links = [img['src'] for img in article_block.find_all('img') if 'src' in img.attrs]
    except:
        image_links = []

    return image_links
    
class MovieView(generic.DetailView):
    model = Movie
    template_name = 'userview/movie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.get_object()
        average_rating = movie.rating_set.aggregate(Avg('value'))['value__avg']

        user_rating = None
        if self.request.user.is_authenticated:
            user_rating = movie.rating_set.filter(user=self.request.user).first()

        context['average_rating'] = average_rating
        context['form'] = UserRatingForm(initial={'value': user_rating.value if user_rating else None})
        context['comment_form'] = CommentForm()
        context['gallery_images'] = img_gallery_parser(movie.imdb_url)
        context['user_rating'] = user_rating

        return context
    
    def post(self, request, *args, **kwargs):
        form = UserRatingForm(request.POST)
        comment_form = CommentForm(request.POST)
        movie = self.get_object()
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                movie=movie, user=request.user, 
                defaults={'value': form.cleaned_data['value']}
            )
            if created:
                messages.success(request, "Your rating has been saved.")
            else:
                messages.success(request, "Your rating has been updated.")
            return HttpResponseRedirect(self.request.path_info)
        
        elif comment_form.is_valid(): 
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.movie = movie
            comment.save()
            messages.success(request, "Your comment has been posted.")
            return HttpResponseRedirect(self.request.path_info)

        else:
            return self.get(request, *args, **kwargs)

class GenreView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login'
    model = Genre
    template_name = 'userview/genre.html'

def register_request(request):

    form = NewUserForm()

    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful." )
            return redirect("/")
        messages.error(request, "Unsuccessful registration. Invalid information.")

    return render (request=request, template_name="register.html", context={"register_form":form})

def login_request(request):
    form = UserForm()
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        print(username,password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
                print("user is not none")
                messages.success(request, "Log in successful." )
                login(request, user)
                return redirect("/")
        else:
            return redirect("/login")
    return render (request=request, template_name="login.html", context={"login_form":form})

def logout_request(request):
    logout(request)
    return redirect("/login")
     
@login_required(login_url="/login")
def rated_movies(request):
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                movie=form.cleaned_data['movie'], user=request.user, 
                defaults={'value': form.cleaned_data['value']}
            )
            if created:
                messages.success(request, 'Rating added successfully.')
            else:
                messages.success(request, 'Rating updated successfully.')
    else:
        form = RatingForm()

    user_ratings = Rating.objects.filter(user=request.user)

    context = {'user_ratings': user_ratings, 'form': form}
    
    return render(request, 'rated_movies.html', context)

def search_results(request):
    data = request.GET.get('data')
    option = request.GET.get('option')
    movies = Movie.objects.all()

    if option == "title":
        movies = movies.filter(title__icontains=data)

    elif option == "genre":
        movies = movies.filter(genres__name__icontains=data)
        print(movies)
       
    elif option == "rating":
        data = float(data)
        movies = movies.annotate(avg_rating=Avg('rating__value'))
        movies = movies.filter(avg_rating__gte=data)

    print(movies)

    return render(request, 'search_results.html', {'movies': movies})

class RatedMoviesView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    model = Movie
    template_name = 'user_rated_movies.html'

    def get_queryset(self):
        user = self.request.user
        return Movie.objects.filter(rating__user=user).distinct()
    
class CommentedMoviesView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    model = Movie
    template_name = 'user_commented_movies.html'
    
    paginate_by = 12
    context_object_name = 'movies'

    def get_queryset(self):
        user = self.request.user
        return Movie.objects.filter(comment__user=user).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recent_comments = list(Comment.objects.order_by('-timestamp').values_list('movie_id', flat=True)[:10])
        recent_ratings = list(Rating.objects.order_by('-id').values_list('movie_id', flat=True)[:10])
        context['recent_movies'] = Movie.objects.filter(
            id__in=set(recent_comments + recent_ratings)
        )
        context['recent_movies'] = context['recent_movies'][:8]
        return context

class DeleteCommentView(View):
    def post(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
        return redirect('movie', pk=comment.movie.id)

class DeleteRatingView(View):
    def post(self, request, rating_id):
        rating = get_object_or_404(Rating, id=rating_id)
        if request.user == rating.user:
            rating.delete()
        return redirect('movie', pk=rating.movie.id)
    
def user_is_admin(user):
    return user.is_superuser

# @login_required
# @user_passes_test(user_is_admin)
# def add_movie_admin(request):
#     if request.method == 'POST':
#         form = AddMovieForm(request.POST)
#         if form.is_valid():
#             movie = form.save()
#             messages.success(request, 'Movie added successfully.')
#             return redirect('movie', pk=movie.id)
#     else:
#         form = AddMovieForm()
#     return render(request, 'add_movie_admin.html', {'form': form})

@login_required
@user_passes_test(user_is_admin)
def add_movie_admin(request):
    if request.method == 'POST':
        form = AddMovieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movie added successfully.')
            return redirect('/')
    else:
        form = AddMovieForm()
    return render(request, 'add_movie_admin.html', {'form': form})

# @login_required
# @user_passes_test(lambda u: u.is_superuser)
# def edit_movie_admin(request, movie_id):
#     movie = get_object_or_404(Movie, id=movie_id)
#     if request.method == 'POST':
#         form = AddMovieForm(request.POST, instance=movie)
#         if form.is_valid():
#             form.save()
#             return redirect('movie', pk=movie.id)
#     else:
#         form = AddMovieForm(instance=movie)
#     return render(request, 'edit_movie_admin.html', {'form': form})

@login_required
@user_passes_test(user_is_admin)
def edit_movie_admin(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    if request.method == 'POST':
        form = AddMovieForm(request.POST, instance=movie)
        if form.is_valid():
            form.save()
            messages.success(request, 'Movie updated successfully.')
            return redirect(f'/movie/{movie_id}')
    else:
        initial = {
            'title': movie.title,
            'imdb_url': movie.imdb_url,
            'year': movie.year,
            'img_url': movie.img_url,
            'genres': movie.genres.all()
        }
        if hasattr(movie, 'imdbrating'):
            initial.update({
                'audience_rating': movie.imdbrating.audience_rating,
                'critic_rating': movie.imdbrating.critic_rating,
            })
        form = AddMovieForm(initial=initial)
    return render(request, 'edit_movie_admin.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_movie_admin(request, movie_id):  
    movie = get_object_or_404(Movie, pk=movie_id)
    movie.delete()
    return redirect('/')