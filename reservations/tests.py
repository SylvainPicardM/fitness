from django.test import TestCase
from .models import MyUser, Creneau, Cours, Reservation
from django.contrib.auth import authenticate, login, logout, get_user_model
import datetime


class ProjectTests(TestCase):

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_signup(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)


def create_creneau(heure, date, jour):
    cours = Cours.objects.create(
        nom = "TEST - " + jour,
        heure = heure,
        jour = jour
    )
    return Creneau.objects.create(
        date = date,
        cours = cours
    )

class CreneauTest(TestCase):

    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')

    def test_week_creneau(self):
        User = get_user_model()
        self.client.login(username='temporary', password='temporary')
        date = datetime.date.today()
        lundi = date - datetime.timedelta(date.weekday())
        create_creneau(9, lundi, "LUNDI")
        create_creneau(10, lundi, "LUNDI")
        create_creneau(9, date + datetime.timedelta(days=1), "MARDI")
        create_creneau(10, date + datetime.timedelta(days=1), "MARDI")
        response = self.client.get('/0/creneaux/')
        self.assertEqual(response.status_code, 200)

    def test_reservation(self):
            User = get_user_model()
            self.client.login(username='temporary', password='temporary')
            date = datetime.date.today()
            lundi = date - datetime.timedelta(date.weekday())
            create_creneau(9, lundi, "LUNDI")
            response = self.client.get('/1/reserver')
            reservations = Reservation.objects.all()
            self.assertEqual(response.status_code, 200)            
            self.assertQuerysetEqual(reservations, ['<Reservation: Reservation object (1)>'])


    
