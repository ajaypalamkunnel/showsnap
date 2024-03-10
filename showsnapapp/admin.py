from django.contrib import admin
from .models import Movie, Auditorium, Screening, Seat, Customer, Booking, Payment,Reservations

admin.site.register(Movie)
admin.site.register(Auditorium)
admin.site.register(Screening)
admin.site.register(Seat)
admin.site.register(Customer)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Reservations)
