from django.shortcuts import redirect, render
from .models import Auditorium, Booking, Customer,Movie, Screening, Seat
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login, logout as auth_logout
from .models import Customer
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required



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
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        
        print(username)
        print(password)
        # Check if any field is empty
        if not all([username, password, first_name, last_name, email, phone]):
            messages.error(request, 'Please fill in all the fields.')
            return render(request, 'signup.html')

        try:
            # Check if username or email already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists.')
                return render(request, 'signup.html')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists.')
                return render(request, 'signup.html')

            # Attempt to create a new User object
            print("Before user object creation")
            user = User.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
            print("after user object creation")
            # Attempt to create a new Customer object associated with the user
            print("Before customer object creation")
            customer = Customer.objects.create(user=user, phone_number=phone)
            print("after customer object creation")

            messages.success(request, 'Account created successfully!')
            # Redirect to the login page
            return redirect('login')
                
        except Exception as e:
            # Handle specific errors here
            messages.error(request, 'An error occurred during signup. Please try again.')
            return render(request, 'signup.html')

    return render(request, 'signup.html')



def logout(request):
    auth_logout(request)
    return redirect('login')

def my_account(request):
    # Fetch data from the User table
    user_data = User.objects.get(pk=request.user.id)
    
    return render(request, 'my_account.html', {'user_data': user_data})


@login_required(login_url='login')
def booking(request, screening_id):
    try:
        # Get the screening instance
        screening = Screening.objects.get(pk=screening_id)
        # Get the auditorium instance
        auditorium = screening.auditorium_tbl 
        # Generate seat layout dynamically based on auditorium capacity and booking status
        seat_layout = generate_seat_layout(screening)
        # Pass the screening, seat_layout, and other necessary data to the template
        return render(request, 'booking_page.html', {'screening': screening, 'seat_layout': seat_layout})
    except Screening.DoesNotExist:
        return HttpResponse("Screening not found")

def generate_seat_layout(screening):
    # Initialize an empty seat layout
    seat_layout = []
    try:
        # Get the auditorium instance
        auditorium = screening.auditorium_tbl
        # Calculate the number of rows needed based on auditorium capacity
        rows = auditorium.capacity // 10  # Assuming 10 columns per row
        # Iterate through each row
        for row in range(rows):
            seat_row = []
            # Iterate through each seat in the row
            for col in range(1, 11):  # Assuming 10 columns per row
                # Generate the seat name (e.g., A1, A2, B1, B2, etc.)
                seat_name = f'{chr(65 + row)}{col}'
                # Check if the seat is booked for the current screening
                is_booked = Booking.objects.filter(showtime=screening, booked_seats__row=chr(65 + row), booked_seats__seat_number=col).exists()
                # Append the seat details to the seat_row list
                seat_row.append({'name': seat_name, 'is_booked': is_booked})
            # Append the seat_row to the seat_layout list
            seat_layout.append(seat_row)
        # Return the generated seat layout
        return seat_layout
    except Auditorium.DoesNotExist:
        return HttpResponse("Auditorium not found")



def confirm_booking(request):  
    if request.method == 'POST':
        selected_seats = request.POST.getlist('selected_seats')
        total_amount = request.POST.get('total_amount')
        # Process the booking and payment here
        return redirect('booking_success')
    return redirect('home')  # Redirect to home page if not a POST request


    
    
    
    
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
   
    
    
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




'''

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
                customer = Customer.objects.create(user=my_user, phone=phone)
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

'''

