from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('',views.home),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('home/',views.home,name='home'),
    path('booking/<int:screening_id>/', views.booking, name='booking'),
    path('my_account/',views.my_account,name='my_account'),
    path('confirm_booking/', views.confirm_booking, name='confirm_booking'),
    path('payment_success/',views.payment_success,name='payment_success'),
    path('view_ticket/<int:reservation_id>/', views.view_ticket, name='view_ticket'),
    path('contact_us/', views.contact_us, name='contact_us'),
    path('login_admin/', views.login_admin, name='login_admin'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('add_auditorium/', views.add_auditorium, name='add_auditorium'),
    path('schedule_show/', views.schedule_show, name='schedule_show'),
    path('view_tickets/', views.view_tickets, name='view_tickets'),
    path('list_movies/', views.list_movies, name='list_movies'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('show_list/', views.show_list, name='show_list'),
    path('delete_screening/<int:screening_id>/', views.delete_screening, name='delete_screening'),
    path('list_screenings/', views.list_screenings, name='list_screenings'),
    path('list_auditoriums/', views.list_auditoriums, name='list_auditoriums'),
    path('delete_auditorium/<int:auditorium_id>/', views.delete_auditorium, name='delete_auditorium'),

     
    #path('home/',views.film_listing,name='home')
    
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)