from urllib.parse import urlencode
from django.shortcuts import redirect, render
from .models import Auditorium, Booking, Customer, Movie, Reservations, Screening, Seat
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .models import Customer
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import uuid
from django.conf import settings
from instamojo_wrapper import Instamojo

api = Instamojo(api_key=settings.API_KEY,
                auth_token=settings.AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/'
                )


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
            user = User.objects.create_user(
                username=username, password=password, email=email, first_name=first_name, last_name=last_name)
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
            messages.error(
                request, 'An error occurred during signup. Please try again.')
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
                is_booked = Booking.objects.filter(showtime=screening, booked_seats__row=chr(
                    65 + row), booked_seats__seat_number=col).exists()
                # Append the seat details to the seat_row list
                seat_row.append({'name': seat_name, 'is_booked': is_booked})
            # Append the seat_row to the seat_layout list
            seat_layout.append(seat_row)
        # Return the generated seat layout
        return seat_layout
    except Auditorium.DoesNotExist:
        return HttpResponse("Auditorium not found")


def generate_booking_id():
    return str(uuid.uuid4())[:5].upper()


def my_view(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        # Retrieve the username of the logged-in user
        username = request.user.username
        # Now you can use the username as needed
        return HttpResponse(f'Logged in as {username}')
    else:
        # Handle the case where the user is not authenticated
        return HttpResponse('Please log in first')


@login_required(login_url='login')
def confirm_booking(request):
    if request.method == 'POST':
        try:
            selected_seats = request.POST.getlist('selected_seats')
            total_amount = request.POST.get('total_amount')
            screening_date = request.POST.get('screening_date')
            movie_title = request.POST.get('movie_title')
            price = request.POST.get('price')
            booking_id = generate_booking_id()
            show_time = request.POST.get('show_time')
            auditorium = request.POST.get('auditorium')

            # Process the booking and payment here
            response = api.payment_request_create(
                amount=total_amount,
                purpose="ticket payment",
                buyer_name="ajay",
                email="ajay@gmail.com",
                redirect_url='http://127.0.0.1:8000/payment_success/?' + urlencode({
                    'booking_id': booking_id,
                    'total_amount': total_amount,
                    'screening_date': screening_date,
                    'movie_title': movie_title,
                    'price': price,
                    'show_time': show_time,
                    'auditorium': auditorium,
                    'selected_seats': ','.join(selected_seats),
                })
            )

            payment_id = response['payment_request']['id']

            # Render the confirm_booking.html template with relevant data
            return render(request, 'confirm_booking.html', {'seats': selected_seats,
                                                            'amount': total_amount, 'movie': movie_title,
                                                            'screening_date': screening_date, 'price': price,
                                                            'show_time': show_time, 'auditorium': auditorium,
                                                            'booking_id': booking_id, 'payment_id': payment_id,
                                                            'payment_url': response['payment_request']['longurl']})

        except Exception as e:
            # Log the error or handle it appropriately
            print(f"An error occurred during booking: {str(e)}")
            # Render an error page or redirect to an appropriate URL
            return render(request, 'error.html', {'error_message': 'An error occurred during booking. Please try again later.'})

    # If request method is not POST, redirect to the home page
    return redirect('home')  # Redirect to home page if not a POST request


@login_required(login_url='login')
def payment_success(request):
    booking_id = request.GET.get('booking_id')
    total_amount = request.GET.get('total_amount')
    screening_date = request.GET.get('screening_date')
    movie_title = request.GET.get('movie_title')
    price = request.GET.get('price')
    show_time = request.GET.get('show_time')
    auditorium = request.GET.get('auditorium')
    selected_seats = request.GET.get('selected_seats').split(',')

    # user_data = User.objects.get(pk=request.user.id)
    # username = user_data.username
    user = request.user
    customer = Customer.objects.get(user=user)
    screening_instance = Screening.objects.get(screening_starts=show_time)
    auditorium_instance = Auditorium.objects.get(name=auditorium)

    print(booking_id, total_amount, screening_date, movie_title,
          price, show_time, auditorium, selected_seats, customer)

    # Booking entry

    booking = Booking.objects.create(
        # booking_id=booking_id,
        total_amount=total_amount,
        showtime=screening_instance,
        bkd_customer=customer,
        booking_status=True  # Assuming the user is authenticated and related to the booking
        # Add other fields as needed
    )
    
    
    
    selected_seats_str = ', '.join(
        [f"'{seat.strip()}'" for seat in selected_seats if seat.strip()])
    reservation = Reservations.objects.create(
        bkd_customer=customer,
        show=screening_instance,
        seat_name=selected_seats_str

    )

    for seat in selected_seats:
        if len(seat) >= 2:
            row = seat[0]
            # Extract the numeric part of the seat number string
            seat_number_str = seat[1:]

        # Check if the seat number string contains only numeric characters
            if seat_number_str.isdigit():
                # Convert the numeric part to an integer
                seat_number = int(seat_number_str)
                print("row:", row, "seat number:", seat_number)

            # Create a new Seat instance and associate it with the booking
                seat_instance = Seat.objects.create(
                    screen=auditorium_instance,  # Assuming you have auditorium_instance defined elsewhere
                    row=row,
                    seat_number=seat_number,
                    is_booked=True,  # Assuming the seat is booked for this booking
                )
            else:
                # Handle the case where the seat number contains non-numeric characters
                print(f"Invalid seat number: {seat}")

    # Process payment success logic with booking data
    # For example, save the booking details to the database or display a success message
    return render(request, 'payment_success.html', {
        'booking_id': booking_id,
        'total_amount': total_amount,
        'screening_date': screening_date,
        'movie_title': movie_title,
        'price': price,
        'show_time': show_time,
        'auditorium': auditorium,
        'selected_seats': selected_seats,
    })


def view_ticket(request):
    return render(request, 'view_ticket.html')












    # for seat in selected_seats:
    # Extract row and seat number from the seat value
    #    row, seat_number = seat.split()
    #    print(row,"  ",seat_number)# Assuming the seat value is in the format 'A3', 'B5', etc.
    # Create a new Seat instance and associate it with the booking
    #     seat_instance = Seat.objects.create(
    #     screen=auditorium,  # Assuming you have auditorium_instance defined elsewhere
    #     row=row,
    #     seat_number=int(seat_number),
    #     is_booked=True,  # Assuming the seat is booked for this booking
    # )
    # Add the seat instance to the booked_seats of the booking
   # booking.booked_seats.add(seat_instance)


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
