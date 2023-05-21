from django.shortcuts import redirect, render
from django.contrib.auth import login,authenticate,logout
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.template import loader
from django.contrib import messages
from userview.forms import UserForm, RatingForm
from django.contrib.auth.decorators import login_required

from userview.forms import NewUserForm
from .models import Movie,Genre,Rating
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.

from django.http import HttpRequest, HttpResponse
from django.views import generic
# def index(request : HttpRequest):
#     return HttpResponse("Sample response")

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


class IndexView(LoginRequiredMixin, generic.ListView):
    login_url = '/login'
    paginate_by = 1
    template_name = 'userview/index.html'
    context_object_name = 'movies'

    def get_queryset(self):
        return Movie.objects.order_by('-title')
    
class MovieView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login'
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

class MovieView(LoginRequiredMixin, generic.DetailView):
    login_url = '/login'
    model = Movie
    template_name = 'userview/movie.html'

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
            rating = form.save(commit=False)
            rating.user = request.user
            rating.save()
            messages.success(request, 'Rating added successfully.')
    else:
        form = RatingForm()

    user_ratings = Rating.objects.filter(user=request.user)

    context = {'user_ratings': user_ratings, 'form': form}
    
    return render(request, 'rated_movies.html', context)

@login_required(login_url="/login")
def search_results(request):

    data = request.GET.get('data')
    option = request.GET.get('option')
    movies = Movie.objects.all()
    genres = Genre.objects.all()
    print(movies)
    if option == "title":
        movie = movies.filter(title__icontains=data)

    elif option == "genre":
        movies = genres.filter(name=data)
        print(movies)
    elif option == "rating":
        pass

    # # Filter the movies based on the provided filters
    # 
    # if title:
    #     movies = movies.filter(title__icontains=title)
    # if genre:
    #     movies = movies.filter(genre=genre)
    # if min_rating:
    #     movies = movies.filter(rating__gte=min_rating)

    # # Pass the filtered movies to the template
    # context = {
    #     'movies': movies,
    #     'title': title,
    #     'genre': genre,
    #     'min_rating': min_rating,
    # }
    # return render(request, 'search_results.html', context)
    print("OK")
    return redirect("/")