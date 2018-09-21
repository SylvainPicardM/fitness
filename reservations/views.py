from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm, AutoCreneauForm
from .models import MyUser, Creneau, Cours, Reservation
import datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
import locale
from collections import OrderedDict
locale.setlocale(locale.LC_TIME, '')

class IndexView(generic.TemplateView):
    template_name = 'reservations/index.html'


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')
    template_name = 'registration/signup.html'

class CreneauView(LoginRequiredMixin, generic.ListView):
    template_name = "reservations/creneaux.html"
    context_object_name = 'creneaux_list'
    login_url = '/login/'

    def get_queryset(self):
        start_week = datetime.date.today()  
        end_week = start_week + datetime.timedelta(6)
        end_week_req = start_week + datetime.timedelta(7)

        entries = Creneau.objects.filter(date__range=[start_week, end_week_req]).order_by('cours__heure')
        creneaux_dict = OrderedDict()
        self.week_days = []
        jours = []
        for n in range(int((end_week - start_week).days) + 1):
             day = start_week + datetime.timedelta(n)
             day_name = day.strftime('%A')
             day_num = day.strftime('%d')
             month_name = day.strftime('%b')
             day_str = "{} {} {}".format(day_name, day_num, month_name)
             self.week_days.append(day_str)
             jours.append(day.strftime('%w').upper())

        for entry in entries:
            if entry.cours.heure not in creneaux_dict.keys():
                creneaux_dict[entry.cours.heure] = OrderedDict()
                for jour in jours:
                    creneaux_dict[entry.cours.heure][str(jour)] = None
                creneaux_dict[entry.cours.heure][entry.date.strftime('%w')] = entry
            else:
                creneaux_dict[entry.cours.heure][entry.date.strftime('%w')] = entry
        return creneaux_dict

    def get_context_data(self, **kwargs):
        context = super(CreneauView, self).get_context_data(**kwargs)
        context['week_days'] = self.week_days
        reservations = Reservation.objects.filter(user=self.request.user)
        context['creneaux_occuped'] = []
        context['creneaux_en_attente'] = []
        for resa in reservations:
            if resa.is_en_attente():
                context['creneaux_en_attente'].append(resa.creneau)
            else:
                context['creneaux_occuped'].append(resa.creneau)
        return context


class ReservationView(LoginRequiredMixin, generic.DetailView):
    template_name = "reservations/resa.html"
    model = Creneau

# TODO: Remplacer par vue générique
def reserver_cours(request, creneau_id):
    user = request.user
    creneau = Creneau.objects.get(pk=creneau_id)
    
    print(creneau.get_places_libres())
    if creneau.get_places_libres() == 0:
        creneau.en_attente += 1
        creneau.save()
        reservation = Reservation.objects.create(creneau=creneau, user=user,
                                                 en_attente=creneau.en_attente)
    else:
        creneau.reservations += 1
        creneau.save()
        reservation = Reservation.objects.create(creneau=creneau, user=user)
        user.credit -= 1
        user.save()
    
    return redirect('/creneaux')


class UserAccountView(LoginRequiredMixin, generic.ListView):
    template_name = "reservations/user_account.html"
    context_object_name = 'reservations_list'
    model = Reservation

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class ReservationDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = "reservations/suppr_reservation.html"
    context_object_name = 'reservation'
    model = Reservation
    success_url = reverse_lazy("user_account")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        creneau = self.object.creneau
        all_resa = Reservation.objects.all()
        for res in all_resa:
            if res.en_attente > self.object.en_attente:
                res.en_attente -= 1
                res.save()
                if res.en_attente == 0:
                    res.user.credit -= 1
                    res.user.save()

        if self.object.is_en_attente():
            creneau.en_attente -= 1
            creneau.save()
        else:
            if creneau.en_attente == 0:
                creneau.reservations -= 1
                creneau.save()
            elif creneau.en_attente > 0:
                creneau.en_attente -= 1
                creneau.save()
        self.object.delete()
        request.user.credit += 1
        request.user.save()
        return HttpResponseRedirect(success_url)


class GenerationCreneau(LoginRequiredMixin, generic.CreateView):
    template_name = "reservations/generation_creneau.html"
    form_class = AutoCreneauForm
    model = Creneau
    success_url = reverse_lazy("user_account") 

    def perdelta(self, start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta

    def form_valid(self, form):
        cours = Cours.objects.all()
        days = [ x for x in self.perdelta(timezone.now(), form.cleaned_data['date'],
                datetime.timedelta(days=1))]
        day_dict= {
            "DIM": 0,
            "LUN": 1,
            "MAR": 2,
            "MER": 3,
            "JEU": 4,
            "VEN": 5,
            "SAM": 6,
        }
        for day in days:
            for cour in cours:
                if int(day_dict[cour.jour]) == int(day.strftime("%w")):
                    date = day
                    new_hour = cour.heure
                    date = date.replace(hour=int(new_hour.strftime('%H')),
                                        minute=0, second=0)

                    obj, created = Creneau.objects.get_or_create(
                        cours=cour,
                        defaults={
                            'date': date
                        }
                    )
        return HttpResponseRedirect(self.success_url)   

