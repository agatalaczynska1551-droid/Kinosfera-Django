from django.core.management.base import BaseCommand
from faker import Faker
from kino_app.models import Movie, Actor, Director, Genre, Seans 
import random
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Testowe dane do bazy'

    def handle(self, *args, **kwargs):
        fake = Faker('pl_PL') 

        self.stdout.write("Czyszczenie starej bazy danych...")

        Seans.objects.all().delete()
        Movie.objects.all().delete()
        Actor.objects.all().delete()
        Director.objects.all().delete()
        Genre.objects.all().delete()

        self.stdout.write("Generowanie danych...")

        directors = []
        for _ in range(40):
            fake_directors = Director.objects.create(name=fake.first_name(), surname=fake.last_name())
            directors.append(fake_directors)

        actors = []
        for _ in range(150):
            fake_actors = Actor.objects.create(name=fake.first_name(), surname=fake.last_name())
            actors.append(fake_actors)

        genres_names = ['Horror', 'Komedia', 'Akcja', 'Sci-Fi', 'Dramat', 'Animacja', 'Romantyczny']
        genres = []
        for name in genres_names:
            fake_genres = Genre.objects.create(name=name)
            genres.append(fake_genres)

        movies = []
        for _ in range(300):

            templates = [
                f"Film o {fake.first_name()} i {fake.last_name()}",
                f"{fake.last_name()} i {fake.first_name()} w akcji",
                f"Historia {fake.first_name()} i {fake.last_name()}",
                f"Przygody {fake.first_name()} i {fake.first_name()}",
                f"Tajemnica {fake.first_name()} i {fake.word()}",
                f"Miłość między {fake.first_name()} a {fake.first_name()}",
                f"Przygoda {fake.first_name()} i {fake.word()}",
                f"Ucieczka {fake.first_name()} i {fake.first_name()}",
                f"Zagadka {fake.word()} i {fake.word()}",
                f"Wyprawa {fake.first_name()} do {fake.city()}",
                f"Powrót do {fake.city()} i {fake.word()}"
            ]

            fake_movie = Movie.objects.create(
                title=random.choice(templates),
                description=fake.text(),
                date_realise=fake.date_between(start_date='-2y', end_date='+3m'),
                directors=random.choice(directors),
                genre=random.choice(genres),
                duration=random.randint(90, 230)
            )
            fake_movie.actors.set(random.sample(actors, random.randint(10, 30)))

            movies.append(fake_movie)

        self.stdout.write("Generowanie seansów dla każdego filmu...")

        for movie in movies:
            for _ in range(random.randint(3, 7)):
                random_day = random.randint(0, 7)
                random_hour = random.randint(10, 22)
                random_minute = random.choice([0, 15, 30, 45])
                
                start_time = timezone.now().replace(
                    hour=random_hour, 
                    minute=random_minute, 
                    second=0, 
                    microsecond=0
                ) + timedelta(days=random_day)

                Seans.objects.create(
                    movie=movie,
                    start_time=start_time,
                    price=round(random.uniform(15.0, 45.0), 2)
                )

        self.stdout.write(self.style.SUCCESS("Dane zostały wygenerowane!"))