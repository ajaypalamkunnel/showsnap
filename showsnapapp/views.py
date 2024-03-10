from .models import Reservations
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
import io
import os
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


from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.platypus import Image
from reportlab.lib.styles import getSampleStyleSheet


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

@login_required(login_url='login')
def my_account(request):
    # Fetch data from the User table
    user_data = request.user
    # Fetch booking history from the Reservations table
    booking_history = Reservations.objects.filter(bkd_customer=user_data.customer)
    
    return render(request, 'my_account.html', {'user': user_data, 'booking_history': booking_history})


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
        reservations = Reservations.objects.filter(show_id=screening_id)
        reserved_seats = [reservation.seat_name for reservation in reservations]
        
        print(reserved_seats)
        #print("Reservationsssssss:",reservation.id)
        return render(request, 'booking_page.html', {'screening': screening, 'seat_layout': seat_layout, 'reserved_seats': reserved_seats,})
    except Screening.DoesNotExist:
        return HttpResponse("Screening not found")

@login_required(login_url='login')
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

@login_required(login_url='login')
def generate_booking_id():
    return str(uuid.uuid4())[:5].upper()

@login_required(login_url='login')
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
    print("Reservation ID", reservation.id)

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
        'reservation_id': reservation.id
    })


# def view_ticket(request):
#     return render(request, 'view_ticket.html')
#



def contact_us(request):
    return render(request,'contact_us.html')


@login_required(login_url='login')
def view_ticket(request, reservation_id):
    # Retrieve the reservation details
    reservation = get_object_or_404(Reservations, id=reservation_id)

    # Create a buffer for the PDF content
    buffer = io.BytesIO()

    # Create a new PDF document
    pdf = SimpleDocTemplate(buffer, pagesize=letter)

    # Add content to the PDF
    elements = []

    # Set background color
    background_color = colors.HexColor('#00002f')
    rect_svg = '<rect width="100%" height="100%" fill="{}" />'.format(
        background_color)
    elements.append(Paragraph(rect_svg, getSampleStyleSheet()['Normal']))

    # Title
    title_style = ParagraphStyle(
        name='Title', fontName='Helvetica-Bold', fontSize=16, textColor=colors.blueviolet)
    title = Paragraph("<b>ShowSnap - Movie Ticket</b>", title_style)
    elements.append(title)

    # Ticket details
    ticket_details = [
        ["Booking ID", "Movie", "Screen", "Show Time", "Seats"],
        [reservation.id, reservation.show.screen_movie.title, reservation.show.auditorium_tbl.name, f"{
            reservation.show.screening_date} {reservation.show.screening_starts}", reservation.seat_name],
    ]

    # Create a table for ticket details
    table = Table(ticket_details, colWidths=[100, 150, 100, 100, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    elements.append(table)

    # Add QR code
    qr_code = qr.QrCodeWidget('dummy qr code')
    d = Drawing(100, 100, transform=[100, 0, 0, 100, 0, 0])
    d.add(qr_code)
    elements.append(d)

    # Build the PDF document
    pdf.build(elements)

    # Get the value of the buffer and return as a PDF response
    pdf_data = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="movie_ticket.pdf"'
    response.write(pdf_data)
    return response

