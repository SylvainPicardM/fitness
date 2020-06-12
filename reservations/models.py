from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import timedelta
from django.utils import timezone
from django.core.validators import RegexValidator


class MyUser(AbstractUser):
    prenom = models.CharField('Prenom', max_length=200)
    nom = models.CharField('Nom', max_length=200)
    credit = models.IntegerField('credits', default=1)
    telephone = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.email

    def get_reservations(self):
        return Reservation.objects.filter(user=self)

    def nb_resa(self):
        count = 0 
        reservations = self.get_reservations()
        day = timezone.now()
        for res in reservations:
            if res.creneau.date > day:
                count += 1
        return count


class Cours(models.Model):
    JOUR_DE_LA_SEMAINE = (
        ('LUN', 'LUNDI'),
        ('MAR', 'MARDI'),
        ('MER', 'MERCREDI'),
        ('JEU', 'JEUDI'),
        ('VEN', 'VENDREDI'),
        ('SAM', 'SAMEDI'),
        ('DIM', 'DIMANCHE'),
    )

    nom = models.CharField('Nom du cours', max_length=200)
    heure = models.TimeField('Heure du cours')
    duree = models.IntegerField('Duree en minutes', default=60)
    jour = models.CharField('Jour de la semaine', max_length=20,
        choices=JOUR_DE_LA_SEMAINE)
    actif = models.BooleanField('Actif', default=True)
    actif_every = models.IntegerField("Actif every", default=1)
    nb_velos = models.IntegerField('Nb de velos disponibles', default=25)
    
    def __str__(self):
        return f"{self.nom} - {self.jour} - {self.heure}h - Actif {self.actif} every {self.actif_every}"
    
    class Meta:
        verbose_name_plural = "cours"
        unique_together = ('jour', 'heure',)


class Creneau(models.Model):
    date = models.DateTimeField('Date du cours')
    reservations = models.IntegerField('Nombre de reservations', default=0)
    reservations_max = models.IntegerField('Nb de reservation max', default=25)
    en_attente = models.IntegerField('En attente', default=0)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "creneaux"

    def __str__(self):
        return '{} : {}'.format(self.date, self.cours.nom)

    def get_places_libres(self):
        return self.reservations_max - self.reservations

    def is_reservable(self):
        date = self.date
        now = timezone.now()
        delta_jour = date.date() - now.date()
        delta_heure = date.hour - now.hour

        if self.get_en_attente() > 9:
            return False
        if self.en_attente >= 10:
            return False
        if delta_jour < timedelta(days=0):
            return False
        elif delta_jour == timedelta(days=0):
            if delta_heure <= 0:
                return False
        return True

    def get_en_attente(self):
        all_resa = Reservation.objects.filter(creneau=self)
        en_attente = 0
        for resa in all_resa:
            if resa.en_attente > 0:
                en_attente += 1
        return en_attente

    def get_name(self):
        days = {
            "LUN": "LUNDI",
            "MAR": "MARDI",
            "MER": "MERCREDI",
            "JEU": "JEUDI",
            "VEN": "VENDREDI",
            "SAM": "SAMEDI",
            "DIM": "DIMANCHE",
        }
        date = self.date.strftime('%d/%m/%y')
        jour = days[self.cours.jour]
        heure = self.date.strftime('%H')
        minute = self.date.strftime('%M')
        return "{} - {} - {}:{}".format(jour, date, heure, minute)

    def get_user_resa(self, user):
        all_resa = Reservation.objects.filter(creneau=self)
        for res in all_resa:
            if res.user == user:
                return res
        return None


class Reservation(models.Model):
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    en_attente = models.IntegerField("en_attente", default=0)

    class Meta:
        unique_together = ('creneau', 'user',)

    def is_en_attente(self):
        return self.en_attente > 0
        
    def is_annulable(self):
        creneau = self.creneau
        date = self.creneau.date
        now = timezone.now()
        delta = date - now
        return delta > timedelta(days=1)
        # if delta <= timedelta(days=1):
        #     return False
        # return True


class Message(models.Model):
    message = models.TextField('message')
    date_debut = models.DateField('date_debut')
    date_fin = models.DateField('date_fin')