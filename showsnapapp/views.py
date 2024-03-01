from django.shortcuts import redirect, render
from .models import Customer,Movie, Screening
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login, logout as auth_logout
from .models import Customer
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.


# def home(request):
#     # Fetch movies, for example, let's assume we want to display released movies
#     released_movies = Movie.objects.filter(status='released')
    
    
#     return render(request, 'home.html', {'released_movies': released_movies})

# def film_listing(request):
#     # Retrieve all screenings with related movie data using select_related
#     screenings = Screening.objects.select_related('screen_movie').all()

#     # Render the template with the screenings data
#     print("film",screenings.screen_movie.title)
#     return render(request, 'film_listing.html', {'screenings': screenings})


def home(request):
    # Fetch released movies
    released_movies = Movie.objects.filter(status='released')
    
    # Retrieve all screenings with related movie data
    screenings = Screening.objects.select_related('screen_movie').all()

    # Render the template with the released movies and screenings data
    return render(request, 'home.html', {'released_movies': released_movies, 'screenings': screenings})



def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print("Username:", username)  
        print("Password:", password) 
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        print("Authenticated User:", user)  
        
        if user:
            auth_login(request, user)
            return redirect('home')
        else:
            
            print("Authentication failed: Invalid username or password")
            return HttpResponse('<script>alert("Invalid username or password"); window.location.href = "/login/";</script>')  
    
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        
        # Check if any field is empty
        if not all([username, password, first_name, last_name, email, phone]):
            messages.error(request, 'Please fill in all the fields.')
        else:
            try:
                # Attempt to create a new User object
                print("checking")
                print(username)
                print(password)
                my_user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                print(username)
                # Attempt to create a new Customer object associated with the user
                #customer = Customer.objects.create(user=my_user, phone=phone)
                print("helloo")
                my_user.save()
               
                messages.success(request, 'Account created successfully!')
                # Redirect to the login page
                return redirect('login')
                
            except Exception as e:
                # Handle specific errors here
                if 'unique constraint' in str(e).lower():
                    messages.error(request, 'Username or email already exists.')
                else:
                    messages.error(request, 'An error occurred during signup.')
    
    return render(request, 'signup.html')

def logout(request):
    auth_logout(request)
    return redirect('login')

def my_account(request):
    # Fetch data from the User table
    user_data = User.objects.get(pk=request.user.id)
    
    return render(request, 'my_account.html', {'user_data': user_data})

@login_required(login_url='login')
def booking(request):
    
    if 'screening_id' in request.GET:
        screening_id = request.GET['screening_id']
        screening = Screening.objects.get(pk=screening_id)
        return render(request, 'booking_page.html', {'screening': screening})
    else:
        # Handle case when screening_id is not provided
        # Redirect or display an error message
        pass