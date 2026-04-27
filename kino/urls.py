"""
URL configuration for kino project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from kino import settings
from kino_app import views
import kino_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='guest_reservation.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('rejestracja/', kino_app.views.register_view, name='register'),
    path("main_page/", views.main_page, name="main_page"),
    path("movie_list/", views.movie_list, name="movie_list"),
    path('movie_detail/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('actor/<int:actor_id>/', views.actor_detail, name='actor_detail'),
    path("movie_reviews/", views.movie_reviews, name="movie_reviews"),
    path("add_review/", views.add_review, name="add_review"),
    path('movie/<int:movie_id>/add_review/', views.add_review, name='add_review'),
    path("all_reservations/", views.all_reservations, name="all_reservations"),
    path("my_reservations/", views.my_reservations, name="my_reservations"),
    path("accounts/", include("django.contrib.auth.urls")),
    path('reservation/<int:seans_id>/', views.reservation_page, name='reservation_page'),
    path('book_seats/<int:seans_id>/', views.book_seats, name='book_seats'),
    path("base/", views.base, name="base"),
    path('', views.main_page, name='home'),
    path("reservation_success/", views.reservation_success, name="reservation_success"),
    path('dla-szkol/', views.for_school, name='for_school'),
    path('dla-dzieci/', views.for_kids, name='for_kids'),
    path('auto_research/', views.auto_research, name='auto_research'),
    path('rezerwacja-sali/', views.private_room, name='private_room'),
    
    # path('get_hours_for_school/', views.get_hours_for_school, name='get_hours_for_school'),
    path('premiere_detail/<int:movie_id>/', views.premiere_detail, name='premiere_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
