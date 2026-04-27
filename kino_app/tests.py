from django.test import TestCase
from django.urls import reverse
from kino_app.models import Movie, Genre, Seans
from django.utils import timezone

class KinoAppTests(TestCase):

    def setUp(self):
        # Przygotowanie danych testowych
        self.genre = Genre.objects.create(name="Sci-Fi")
        self.movie = Movie.objects.create(
            title="Interstellar",
            description="Grupa astronautów wyrusza w misję poza granice naszej galaktyki, aby znaleźć nowy dom dla ludzkości, której zagraża globalna susza i głód na Ziemi.",
            date_realise="2014-11-07",
            duration=169,
            genre=self.genre
        )

    def test_movie_creation(self):
        """Sprawdza, czy film poprawnie zapisuje się w bazie."""
        movie = Movie.objects.get(title="Interstellar")
        self.assertEqual(movie.duration, 169)
        self.assertEqual(str(movie), "Interstellar")

    def test_seans_creation(self):
        """Sprawdza, czy seans przypisuje się do filmu."""
        seans = Seans.objects.create(
            movie=self.movie,
            start_time=timezone.now(),
            price=25.00
        )
        self.assertEqual(seans.movie.title, "Interstellar")

    # --- Testy Widoków (Status 200) ---

    def test_home_page_status_code(self):
        """Sprawdza, czy strona główna działa."""
        response = self.client.get('/') 
        self.assertEqual(response.status_code, 200)

    def test_movie_list_view(self):
        """Sprawdza widok listy filmów (jeśli masz taki w urls.py)."""
        url = reverse('movie_list') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Interstellar")

# Create your tests here.
