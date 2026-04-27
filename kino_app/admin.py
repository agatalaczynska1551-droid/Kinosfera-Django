from django.contrib import admin
from .models import Movie, Actor, Director, Genre, PrivateReservation, Review, SchoolBooking, Seans, Reservation, UpcomingMovie

class SeansInline(admin.TabularInline):
    model = Seans
    extra = 3  # Ile pustych pól na nowe seanse wyświetlić
    fields = ('start_time', 'price')

class ReviewInline(admin.StackedInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False # Opcjonalnie: blokada usuwania recenzji z poziomu filmu



@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_realise', 'genre')
    list_filter = ('date_realise', 'directors', 'genre')
    search_fields = ('title',)
    filter_horizontal = ('actors',)
    inlines = [SeansInline, ReviewInline] 


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname')
    search_fields = ('name', 'surname')


@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'surname')
    search_fields = ('name', 'surname')


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Seans)
class SeansAdmin(admin.ModelAdmin):
    list_display = ('get_movie_title', 'start_time', 'price')
    list_filter = ('start_time', 'movie')
    search_fields = ('movie__title',)

    @admin.display(description='Film')
    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else "Brak filmu"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'seans', 'status', 'created_at', 'seat_number')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(SchoolBooking)
class SchoolBookingAdmin(admin.ModelAdmin):
    list_display = ('school_name', 'email', 'students_count', 'movie', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('school_name', 'movie',)
    readonly_fields = ('created_at',)

@admin.register(PrivateReservation)
class PrivateReservationAdmin(admin.ModelAdmin):
    list_display = ('date', 'email', 'phone', 'created_at')
    list_filter = ('date', 'phone', 'created_at')
    search_fields = ('email', 'phone',)
    readonly_fields = ('created_at',)

@admin.register(UpcomingMovie)
class UpcomingMovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'premiere_date')
    list_filter = ('premiere_date',)
    search_fields = ('title',)



# Register your models here.
