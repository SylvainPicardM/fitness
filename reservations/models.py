from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum


class MyUser(AbstractUser):
    prenom = models.CharField('Prenom', max_length=200, default="Prenom")
    nom = models.CharField('Nom', max_length=200, default='Nom')
    credit = models.IntegerField('credits', default=0)
    
    def __str__(self):
        return self.email


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
    heure = models.IntegerField('Heure du cours')
    duree = models.IntegerField('Duree en minutes', default=60)
    jour = models.CharField('Jour de la semaine', max_length=20,
        choices=JOUR_DE_LA_SEMAINE)
    
    def __str__(self):
        return "{} - {} - {}h".format(self.nom, self.jour, self.heure)
    
    class Meta:
        verbose_name_plural = "cours"
        unique_together = ('jour', 'heure',)


class Creneau(models.Model):
    date = models.DateField('Date du cours')
    reservations = models.IntegerField('Nombre de reservations', default=0)
    reservations_max = models.IntegerField('Nb de reservation max', default=10)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "creneaux"

    def __str__(self):
        return '{}h : {}'.format(self.cours.heure, self.cours.nom)

    def get_places_libres(self):
        return self.reservations_max - self.reservations


class Reservation(models.Model):
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
