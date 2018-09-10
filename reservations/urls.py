from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('<int:semaine>/creneaux/', views.CreneauView.as_view(), name='creneaux'),
    path('<int:pk>/reservations', views.ReservationView.as_view(), name="reservations"),
    path('<int:creneau_id>/reserver', views.reserver_cours, name="reserver"),
]