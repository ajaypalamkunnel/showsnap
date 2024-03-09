from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    STATUS_CHOICES = (
        ('released', 'Released'),
        ('upcoming', 'Upcoming'),
    )
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    duration = models.PositiveIntegerField()  # Assuming time in minutes
    genre = models.CharField(max_length=255)
    language = models.CharField(max_length=25)
    # Assuming storing posters in a 'posters' directory
    poster = models.ImageField(upload_to='posters/')
    film_director = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title

class Auditorium(models.Model):#screen
    name = models.CharField(max_length=50)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Screening(models.Model):
    TIME_CHOICES = [
        ('11:00', '11:00 AM'),
        ('14:00', '2:00 PM'),
        ('18:00', '6:00 PM'),
        ('21:00', '9:00 PM'),
        # Add additional predefined times as needed
    ]
    screen_movie = models.ForeignKey(
        Movie, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    auditorium_tbl = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    screening_starts = models.CharField(max_length=5, choices=TIME_CHOICES)
    screening_date = models.DateField()  # New date field

    def __str__(self):
        return f"{self.screen_movie.title} Screening"





class Seat(models.Model):
    screen = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    row = models.CharField(max_length=1)  # Represents the row identifier (e.g., A, B, C)
    seat_number = models.IntegerField()   # Represents the seat number within the row
    is_booked = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.row} ({self.seat_number})"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} ({self.user.first_name} {self.user.last_name})"






class Booking(models.Model):
    bkd_customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE)  
    showtime = models.ForeignKey(Screening, on_delete=models.CASCADE)
    booking_status = models.BooleanField(default=False)
    booked_seats = models.ManyToManyField(Seat)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Booking ID: {self.id}, Customer: {self.bkd_customer}"



class Payment(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Booking {self.booking_id}"


# class Customer(models.Model): 
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone = models.CharField(max_length=20)
    
#     # models.ForeignKey(User, on_delete=models.CASCADE)
#     # customer_id =  models.ForeignKey(User, on_delete=models.CASCADE)
#     # password = models.CharField(max_length=20)
#     # first_name = models.CharField(max_length=20)
#     # last_name = models.CharField(max_length=20)
#     # email = models.EmailField()

#     def __str__(self):
#         return f"{self.first_name} {self.last_name}"