from time import timezone
from datetime import date
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
import qrcode
import io
import base64

class Movie(models.Model):
    title = models.CharField(max_length=200)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    date_realise = models.DateField()
    directors = models.ForeignKey('Director', on_delete=models.CASCADE, null=True, blank=True)
    actors = models.ManyToManyField('Actor', related_name='movies')
    duration = models.IntegerField()
    #poster = models.ImageField(_("Image"), upload_to=None, height_field=None, width_field=None, max_length=None)

    def get_poster_url(self):
        # placeholders = {
        #     "Horror": "dark,forest,scary, ghost",
        #     'Komedia': 'comedy,funny,smile',
        #     'Akcja': 'action,car,explosion',
        #     'Sci-Fi': 'space,robot,future',
        #     'Dramat': 'sad,people,rain',
        #     'Animacja': 'cartoon,colorful,toy',
        #     'Romantyczny': 'love,couple,heart'
        # }
        
        # keyword = placeholders.get(self.genre, 'movie,cinema,film')
        return f"https://picsum.photos/seed/{self.id}/400/600"
    
    def __str__(self):
        return self.title

class Actor(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    
    def get_photo_url(self):
        return f"https://i.pravatar.cc/{600}?u={self.id}"

    def __str__(self):
        return f"{self.name} {self.surname}"

class Director(models.Model):
    name = models.CharField(max_length=200)
    surname = models.CharField(max_length=200)
    #photo = models.ImageField(_("Image"), upload_to=None, height_field=None, width_field=None, max_length=None)
    def __str__(self):
        return f"{self.name} {self.surname}"

class Genre(models.Model):
    name = models.CharField(max_length=200, unique=True)
    def __str__(self):
        return self.name

class Seans(models.Model):
    start_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name="seanses")

    def __str__(self):
        time = timezone.localtime(self.start_time)
        return f"{self.movie.title} - {time.strftime('%d.%m %H:%M')}"

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    seans = models.ForeignKey(Seans, on_delete=models.CASCADE, null=True, blank=True)
    status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    seat_number = models.CharField(max_length=20, null=True, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def get_qr_code(self):
        # Dane zaszyte w kodzie (np. dla skanera biletera)
        qr_data = f"ID:{self.id}|Film:{self.seans.movie.title}|Miejsce:{self.seat_number}"
        
        qr = qrcode.QRCode(version=1, box_size=10, border=1)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Zamiana obrazka na tekst base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


    def __str__(self):
        if self.user:
            return f"Rezerwacja dla {self.user.username} na: {self.seans.movie.title} ({self.seat_number})"
        else:
            return f"Rezerwacja dla {self.first_name} {self.last_name} na: {self.seans.movie.title} ({self.seat_number}) (Gość)"
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    movie = models.ForeignKey(Movie, related_name="reviews", on_delete=models.CASCADE, null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"
    
class SchoolBooking(models.Model):
    school_name = models.CharField(max_length=200)
    email = models.EmailField()
    students_count = models.IntegerField()
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, null=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    seans = models.ForeignKey('Seans', on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.school_name} - {self.movie.title if self.movie else 'Brak filmu'}"


class PrivateReservation(models.Model):
    date = models.DateField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rezerwacja {self.date} - {self.email}"
    
class UpcomingMovie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    premiere_date = models.DateField()
    genre = models.CharField(max_length=100)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    trailer_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"Premiera: {self.title}"
    
# Create your models here.
