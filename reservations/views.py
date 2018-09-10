from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from .models import MyUser, Creneau, Cours, Reservation
import datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin

def index(request):
    if request.method == "POST":
        form = AuthenticationForm()
        if form.is_valid():
            username = request.POST['email']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return render(request,"reservations/index.html", {})
            else:
                #TODO: Renvoyer une erreur
                return render(request, 'reservations/index.html', {'form': form})

    else:
        form = AuthenticationForm()
    return render(request, 'reservations/index.html', {'form': form})

def deconnexion(request):
    logout(request)
    return render(request, 'reservations/index.html', {})


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class CreneauView(LoginRequiredMixin, generic.ListView):
    template_name = "reservations/creneaux.html"
    context_object_name = 'creneaux_list'
    login_url = '/login/'

    def get_queryset(self):
        semaine = self.kwargs['semaine']
        date = datetime.date.today() + datetime.timedelta(semaine*7)
        start_week = date - datetime.timedelta(date.weekday())
        end_week = start_week + datetime.timedelta(6)
        entries = Creneau.objects.filter(date__range=[start_week, end_week]).order_by('cours__heure')
        creneaux_dict = {}
        for entry in entries:
            if entry.cours.heure not in creneaux_dict.keys():
                creneaux_dict[entry.cours.heure] = {}
                for jour in Cours._meta.get_field('jour').choices:
                    creneaux_dict[entry.cours.heure][jour[0]] = None
                creneaux_dict[entry.cours.heure][entry.cours.jour] = entry
            else:
                creneaux_dict[entry.cours.heure][entry.cours.jour] = entry

        return creneaux_dict

    def get_context_data(self, **kwargs):
        context = super(CreneauView, self).get_context_data(**kwargs)
        context['week_days'] = Cours._meta.get_field('jour').choices
        semaine = self.kwargs['semaine']
        context['semaine'] = semaine
        date = datetime.date.today() + datetime.timedelta(semaine*7)
        context['start_week'] = date - datetime.timedelta(date.weekday())
        context['end_week'] = context['start_week'] + datetime.timedelta(6)
        return context


class ReservationView(LoginRequiredMixin, generic.DetailView):
    template_name = "reservations/resa.html"
    model = Creneau


def reserver_cours(request, creneau_id):
    creneau = Creneau.objects.get(pk=creneau_id)
    reservation = Reservation.objects.create(creneau=creneau, user=request.user)
    return render(request, "reservations/resa.html", {})
