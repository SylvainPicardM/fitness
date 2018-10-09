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
from django.http import HttpResponseRedirect
import locale
from collections import OrderedDict
from django.core.mail import send_mail

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
    
    if user.credit >= 0:
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

        send_mail(
            subject="nouvelle_reservation",
            message="message",
            from_email="picard.sylvain3@gmail.com",
            recipient_list=[user.email],
            fail_silently=False
        )   
    
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

    def move_queue(self, creneau):
        all_resa = Reservation.objects.filter(creneau=creneau)
        for res in all_resa:
            if res.en_attente > self.object.en_attente:
                res.en_attente -= 1
                res.save()
                if res.en_attente == 0:
                    res.user.credit -= 1
                    res.user.save()
                if res.user.credit == -1:
                    user_resa = Reservation.objects.filter(user=res.user)
                    for ur in user_resa:
                        if ur.en_attente > 0:
                            ur.delete()


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        creneau = self.object.creneau

        # Si la resa est en attente et qu'il y a une file d'attente
        if self.object.is_en_attente() and creneau.en_attente > 0:
            creneau.en_attente -= 1
            creneau.save()
        # Si pas en attente , on recredite une seance
        elif not self.object.is_en_attente():
            # Si personne en liste d'attente, -1 resa
            if creneau.en_attente == 0:
                creneau.reservations -= 1
                creneau.save()
            request.user.credit += 1
            request.user.save()
       
        self.move_queue(creneau)
        self.object.delete()
        return HttpResponseRedirect(success_url)


