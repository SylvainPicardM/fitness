from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import MyUser, Cours, Creneau, Reservation, Message

@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'nom', 'prenom', 'email', 'credit', 'telephone')

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('nom', 'jour', 'heure', 'actif', 'actif_every')

@admin.register(Creneau)
class CreneauAdmin(admin.ModelAdmin):
    list_display = ('date', 'reservations', 'reservations_max', 'cours',
                    'nombre_attente')

    def nombre_attente(self, obj):
        return obj.get_en_attente()

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('creneau', 'user','prenom_nom', 'en_attente',)
    list_filter = ('creneau', )

    def prenom_nom(self, obj):
        
        p = str(obj.user.prenom).capitalize()
        n = str(obj.user.nom).upper()
        return "{} {}".format(p, n)

admin.site.register(Message)
admin.site.site_url = "/accounts/profile/"