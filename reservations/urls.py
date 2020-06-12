from django.urls import path, include
from django.conf.urls import url
from . import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    path('', views.IndexView.as_view(), name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('<int:pk>/reservations', views.ReservationView.as_view(), name="reservations"),
    path('<int:creneau_id>/reserver', views.reserver_cours, name="reserver"),
    path('accounts/profile/', views.UserAccountView.as_view(),  name="user_account"),
    path('<int:pk>/supprimer_reservation/', views.ReservationDelete.as_view(), name="supprimer_resa")
    ]