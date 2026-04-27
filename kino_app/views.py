from multiprocessing import context
from urllib import request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Movie, SchoolBooking, Seans, Reservation, Genre, Review, Actor, Director, PrivateReservation, UpcomingMovie
from datetime import datetime, date
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from kino_app import models
from django import forms
from django.core.mail import send_mail
from django.conf import settings
import locale
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Prefetch
from django.contrib.auth.forms import UserCreationForm


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Konto stworzone dla {username}! Możesz się zalogować.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


class SchoolReservationForm(forms.Form):
    school_name = forms.CharField(label="Nazwa szkoły", max_length=200, widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    email = forms.EmailField(label="E-mail kontaktowy", widget=forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    movie = forms.ModelChoiceField(
        queryset=Movie.objects.all(),
        label="Wybierz film",
        empty_label="-- Wybierz film --",
        widget=forms.Select(attrs={'name': 'movie'})
    )
    
    date = forms.CharField(label="Data seansu", widget=forms.TextInput(attrs={
        'class': 'form-control bg-dark text-white border-secondary',
        'id': 'flatpickr-input',
        'readonly': 'readonly'
    }))

    students_count = forms.IntegerField(label="Liczba uczniów", widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    message = forms.CharField(label="Dodatkowe uwagi", widget=forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3}), required=False)

# def get_hours_for_school(request):
#     movie_id = request.GET.get('movie_id')
#     date = request.GET.get('date')
    
#     # Pobieramy pełne obiekty Seans
#     seanses = Seans.objects.filter(movie_id=movie_id, start_time__date=date)
    
#     # Zwracamy ID (do zapisu) i godzinę (do wyświetlenia)
#     data = [
#         {'id': s.id, 'time': s.start_time.strftime('%H:%M')} 
#         for s in seanses
#     ]
#     return JsonResponse(data, safe=False)
    
def for_school(request):
    if request.method == 'POST':
        form = SchoolReservationForm(request.POST)

       
    
        if form.is_valid():
            SchoolBooking.objects.create(
                school_name=form.cleaned_data['school_name'],
                email=form.cleaned_data['email'],
                movie=form.cleaned_data['movie'],
                students_count=form.cleaned_data['students_count'],
                message=form.cleaned_data['message'],
            )
           
            subject = f"Nowe zgłoszenie: {form.cleaned_data['school_name']}"
            message_body = f"""
            Otrzymano nowe zgłoszenie od szkoły!

            Szkoła: {form.cleaned_data['school_name']}
            Film: {form.cleaned_data['movie']}
            Data: {form.cleaned_data['date']}
            Liczba uczniów: {form.cleaned_data['students_count']}
            Email: {form.cleaned_data['email']}
            Uwagi: {form.cleaned_data['message']}
            """

            send_mail(
                subject,
                message_body,
                settings.EMAIL_HOST_USER,  
                ['admin@kinosfera.pl'],    
                fail_silently=False,
            )

            messages.success(request, 'Zapytanie zostało wysłane!')
            return redirect('for_school')
        else:
            print(form.errors)
    else:
        form = SchoolReservationForm()
   
    
    return render(request, 'for_school.html', {'form': form})

class KidsOfferForm(forms.Form):
    parent_name = forms.CharField(label="Imię i nazwisko rodzica", widget=forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    email = forms.EmailField(label="E-mail", widget=forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    
    SERVICE_CHOICES = [
        ('urodziny', 'Organizacja urodzin'),
        ('wynajem', 'Wynajem sali na wyłączność'),
        ('atrakcje', 'Dodatkowe atrakcje (warsztaty, zwiedzanie kabiny)')
    ]
    service_type = forms.ChoiceField(choices=SERVICE_CHOICES, label="Co Cię interesuje?", widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'}))
    
    kids_count = forms.IntegerField(label="Przewidywana liczba dzieci", widget=forms.NumberInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}))
    message = forms.CharField(label="Twoje pytania", required=False, widget=forms.Textarea(attrs={'class': 'form-control bg-dark text-white border-secondary', 'rows': 3}))


def for_kids(request):
    if request.method == 'POST':
        form = KidsOfferForm(request.POST)
        if form.is_valid():
            # Tutaj wysyłka maila (podobnie jak w szkołach)
            messages.success(request, 'Dziękujemy! Skontaktujemy się, aby zaplanować niezapomniane chwile dla Twojego dziecka.')
            return redirect('for_kids')
    else:
        form = KidsOfferForm()
    return render(request, 'for_kids.html', {'form': form})


def main_page(request):
    today = timezone.now().date()

    # 1. Przygotowanie zakresu dni (kalendarzyk)
    days_range = []
    for i in range(7):
        d = today + timedelta(days=i)
        days_range.append({
            'full_date': d.strftime('%Y-%m-%d'),
            'day_name': d.strftime('%a'),
            'day_num': d.day
        })
    
    # 2. Filmy grane DZISIAJ (z seansami)
    playing_today = Movie.objects.filter(seanses__start_time__date=today).distinct()
    movies_list = playing_today.order_by("title")
    
    # 3. NADCHODZĄCE PREMIERY
    # Pobieramy filmy z przyszłą datą, wykluczając te, które mają już seanse dzisiaj
    upcoming_movies = UpcomingMovie.objects.all().order_by('premiere_date')[:4]

    # Awaryjne zapełnienie (tylko jeśli baza jest pusta lub seed nie zadziałał)
    # if not upcoming_movies.exists():
    #     upcoming_movies = Movie.objects.exclude(id__in=playing_today)[:4]

    # 4. Paginacja dla sekcji "DZISIAJ GRAMY"
    paginator = Paginator(movies_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'main_page.html', {
        'page_obj': page_obj, 
        'days_range': days_range,
        'upcoming_movies': upcoming_movies
    })

def premiere_detail(request, movie_id):
    movie = get_object_or_404(UpcomingMovie, id=movie_id)
    return render(request, "premiere_detail.html", {"movie": movie})

def base(request):
    return render(request, "base.html")

def movie_list(request):
    date_filter = request.GET.get("date")
    query = request.GET.get("q")
    genre_filter = request.GET.get("genre")
    today = datetime.now().date()
    
    # 1. Określamy, jakie seanse nas interesują (tylko przyszłe lub z konkretnego dnia)
    if date_filter:
        relevant_seanses = Seans.objects.filter(start_time__date=date_filter)
    else:
        relevant_seanses = Seans.objects.filter(start_time__date__gte=today)

    # 2. Tworzymy bazowy queryset filmów, które mają te seanse
    # Prefetch sprawi, że movie.seanses.all w HTML pokaże tylko te przefiltrowane daty!
    movies_queryset = Movie.objects.prefetch_related(
        Prefetch("seanses", queryset=relevant_seanses.order_by('start_time'))
    ).filter(seanses__in=relevant_seanses).distinct()

    # 3. Nakładamy dodatkowe filtry (wyszukiwarka i gatunek)
    if query:
        movies_queryset = movies_queryset.filter(title__icontains=query)
    if genre_filter:
        movies_queryset = movies_queryset.filter(genre__name=genre_filter)

    # 4. Sortowanie końcowe
    movies_queryset = movies_queryset.order_by("-date_realise")

    # --- Reszta Twojego kodu (kalendarz i paginacja) ---
    try:
        locale.setlocale(locale.LC_TIME, 'pl_PL.UTF-8')
    except locale.Error:
        pass

    days_range = []
    for i in range(7):
        date_obj = today + timedelta(days=i)
        days_range.append({
            'full_date': date_obj.strftime('%Y-%m-%d'),
            'day_name': date_obj.strftime('%a'), 
            'day_num': date_obj.day,
        })

    all_genres = Movie.objects.values_list("genre__name", flat=True).distinct()

    paginator = Paginator(movies_queryset, 15)
    page_number = request.GET.get("page")
    movies = paginator.get_page(page_number)

    context = {
        "movies": movies,
        "all_genres": all_genres,
        "selected_genre": genre_filter,
        "selected_date": date_filter,
        "days_range": days_range,
        "today": today,
    }
    return render(request, "movie_list.html", context)

def reservation_page(request, seans_id):
    seans = get_object_or_404(Seans, id=seans_id)
    reserved_seats = Reservation.objects.filter(seans=seans).values_list('seat_number', flat=True)
    clean_reserved_seats = [s for s in reserved_seats if s and s.strip()]

    print(f"DEBUG BAZA: {list(reserved_seats)}")

    reserved_seats_list = list(reserved_seats)

    rows = range(1, 16)
    seats_in_row = range(1, 21)

    context = {
        "seans": seans,
        "reserved_seats": clean_reserved_seats,
        "rows": range(1, 16),
        "seats_in_row":range(1, 21),
        "ticket_adult": 40,
        "ticket_student": 30,
    }
    return render(request, "reservation_page.html", context)

@login_required
def book_seats(request, seans_id):
    if request.method == 'POST':
        seans = get_object_or_404(Seans, id=seans_id)
        seats_list = request.POST.getlist('selected_seats')

        print(f"--- PRÓBA REZERWACJI ---")
        print(f"Dane z POST: {request.POST}")
        print(f"Lista miejsc: {seats_list}")

        if not seats_list:
            messages.error(request, "Nie wybrano żadnych miejsc!")
            return redirect('reservation_page', seans_id=seans_id)
        
        already_reserved = Reservation.objects.filter(
            seans=seans, 
            seat_number__in=seats_list
        ).values_list('seat_number', flat=True)

        if already_reserved:
            reserved_str = ", ".join(already_reserved)
            messages.error(request, f"Przepraszamy, miejsca {reserved_str} zostały właśnie zajęte.")
            return redirect('reservation_page', seans_id=seans_id)

        for seat_num in seats_list:
            if seat_num:
                Reservation.objects.create(
                    user=request.user,
                    seans=seans,
                    seat_number=seat_num 
                )
        
            print(f"Zapisano miejsce: {seat_num}")

        return render(request, 'reservation_success.html', {
            'seans': seans, 
            'seats': seats_list
            })
    
    return redirect('movie_list')

def reservation_success(request):
    return render(request, "reservation_success.html")

# def for_school_view(request):
#     return render(request, "for_school.html")

def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    seanses = Seans.objects.filter(movie=movie).order_by('start_time')
    reviews = movie.reviews.all().order_by('-created_at')

    return render(request, "movie_detail.html", {
        "movie": movie, 
        "seanses": seanses,
        "reviews": reviews}
        )


def actor_detail(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    movies = actor.movies.all().order_by('-date_realise') 

    paginator = Paginator(movies, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "actor_detail.html", {
        "actor": actor, 
        "page_obj": page_obj
        })

def movie_reviews(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    reviews = movie.reviews.all()
    return render(request, "movie_reviews.html", {
        "movie": movie, 
        "reviews": reviews})

@login_required
def add_review(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating"))
        comment = request.POST.get("comment")

        if comment:
            Review.objects.create(
                movie=movie,
                user=request.user,
                comment=comment,
                rating=rating
            )
            
        return redirect('movie_detail', movie_id=movie_id)

def auto_research(request):
    query = request.GET.get('term', '') # jQuery UI domyślnie wysyła parametr 'term'
    movies = Movie.objects.filter(title__icontains=query)[:10]
    results = [movie.title for movie in movies]
    return JsonResponse(results, safe=False)

def private_room(request):
    if request.method == "POST":
        date = request.POST.get('date')
        movie = request.POST.get('movie_title')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        reservation = PrivateReservation.objects.create(
            date=date,
            email=email,
            phone=phone
        )

        full_message = f"Nowe zapytanie o salę VIP!\nData: {date}\nKontakt: {email}, {phone}"
        
        try:
            send_mail(
                f'Nowa rezerwacja VIP: {date}',
                full_message,
                'twoj-email@gmail.com', 
                ['manager-kina@gmail.com'], 
                fail_silently=False,
            )
            messages.success(request, "Dziękujemy! Twoje zapytanie zostało wysłane. Skontaktujemy się wkrótce.")
        except:
            messages.warning(request, "Zapisaliśmy rezerwację, ale wystąpił problem z wysyłką maila.")

        return redirect('private_room')

    return render(request, 'private_room.html')

@login_required
def my_reservations(request):
    reservations = Reservation.objects.filter(user=request.user).select_related('seans__movie').order_by('-seans__start_time')
    return render(request, "my_reservations.html", {"reservations": reservations})

@login_required
def all_reservations(request):
    reservations = Reservation.objects.all().select_related('seans__movie').order_by('-seans__start_time')
    return render(request, "all_reservations.html", {"reservations": reservations})





# Create your views here.
