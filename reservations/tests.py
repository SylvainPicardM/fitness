from django.test import TestCase
from .models import MyUser, Creneau, Cours, Reservation
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.utils import timezone
from django.test import Client
from django.urls import reverse
from django.test import SimpleTestCase
import datetime


"""
    TODO:
        - Dashboatd utilisateur:
            - Affichage du bon nb de seances de la semaine
            - Affichage des seances reservées par user
            - 
        - Inscription a un cours:
            - Nb de seances de l'utilisateur
            - Nb d'inscrit au cours
            - Nb de personnes en attente
            - Pas de possibilité de s'inscrire deux fois au mm cours
            - Pas plus de deux reservations similtanée
            - 
        - Annulation d'une resa:
            - Si pas en attente: 
                - verifier nb de seances de l'user
                - Verfifier le nb d'inscrit au cours
                - Verifier la gestion file d'attente
            - Si en attente:
                - verifier le fonctionnement de la file d'attente
                - verifier nb de seances 
                - verifier nb de personnes en file d'attente
            - Verifier le n° dans la file des autres personnes

        - Redirections:
            - Apres deconnection
            - Reset mot de passe
            - 

"""

class HomePageTest(SimpleTestCase):
    def test_home_page_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_view_url_by_name(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
    
    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('index'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'reservations/index.html')

    def test_home_page_contains_correct_html(self):
        response = self.client.get('/')
        self.assertContains(response, '<h1 class="main-title">AQUABIKE RIEUX-VOLVESTRE</h1>')

    def test_home_page_does_not_contain_incorrect_html(self):
        response = self.client.get('/')
        self.assertNotContains(
            response, 'Hi there! I should not be on the page.')


def get_week_days():
    today = datetime.date(2018, 11, 1)
    return [today + datetime.timedelta(days=i) for i in range(0 - today.weekday(), 7 - today.weekday())]

def create_cours():
    dates = get_week_days()
    for date in dates:
        day = date.strftime("%a").upper()
        Cours.objects.create(
            nom="TEST-" + day,
            heure = "13:00:00",
            duree=60,
            jour=day)
        
def create_users(nb=1):
    users = []
    for i in range(nb):
        username = "user_" + str(i)
        pwd = "password_" + str(i)
        mail = username + "@gmail.com"
        user = User.objects.create_user(username, mail, pwd)
        users.append(user)
    return users

class CoursTestCase(TestCase):
    def setUp(self):
        create_cours()

    def test_cours_exist(self):
        cours = Cours.objects.all()
        cour = Cours.objects.get(id=1)
        self.assertEqual(len(cours), 7)
        self.assertEqual(cour.heure, datetime.time(13, 0))
        self.assertEqual(cour.jour, "MON")

class CreneauTestCase(TestCase):
    def setUp(self):
        create_cours()
        cours = Cours.objects.all()
        days = get_week_days()
        User = get_user_model()
        users = create_users(nb=20)
        for cour, day in zip(cours, days):
            Creneau.objects.create(
                date = day,
                cours = cour
            )

    def test_creneau_list(self):
        User = get_user_model()
        creneaux = Creneau.objects.all()
        self.assertEqual(len(creneaux), 7)
        users = MyUser.objects.all()
        self.client.login(username="user1", password="password1")
        response = self.client.get(reverse('creneaux'))
        self.assertEqual(response.status_code, 200)
        
class ReservationTestCase(TestCase):
    def setUp(self):
        create_cours()
        cours = Cours.objects.all()
        days = get_week_days()
        User = get_user_model()
        users = create_users(nb=20)
        for cour, day in zip(cours, days):
            Creneau.objects.create(
                date = day,
                cours = cour
            )

    def test_acces_page_reservations(self):
        creneau = Creneau.objects.get(pk=1)
        self.client.login(username="user1", password="password1")
        response = self.client.get("/" + str(creneau.pk) + "/reservations")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "RESERVER")

    def test_reservation_post(self):
        creneau = Creneau.objects.get(pk=1)
        self.client.login(username="user1", password="password1")
        response = self.client.get("/" + str(creneau.pk) + "/reserver")
        self.assertEqual(response.status_code, 200)