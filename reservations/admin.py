from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Cours, Creneau, Reservation

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nom', 'prenom', 'email', 'credit')

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'jour', 'heure', 'duree')

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ('date', 'reservations', 'reservations_max', 'cours')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('creneau', 'user')