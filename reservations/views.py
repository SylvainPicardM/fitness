from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy
from django.views import generic
from .models import MyUser, Creneau, Cours, Reservation, Message
from .forms import CustomUserCreationForm
import datetime
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
import locale
from collections import OrderedDict
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# locale.setlocale(locale.LC_TIME, '')
ADMIN_EMAIL = "contact@aquabike-rieuxvolvestre.fr"


class IndexView(generic.TemplateView):
    template_name = 'reservations/index.html'


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class ReservationView(LoginRequiredMixin, generic.DetailView):
    template_name = "reservations/resa.html"
    model = Creneau


# TODO: Remplacer par vue générique
def reserver_cours(request, creneau_id):
    user = request.user
    creneau = Creneau.objects.get(pk=creneau_id)

    # EMAIL SETTINGS
    from_email=ADMIN_EMAIL
    to = [user.email]
    date = creneau.date
    date = date.strftime('%A') + " " +date.strftime('%x')
    if user.credit >= 0:
        if creneau.get_places_libres() == 0:
            # creneau.en_attente += 1
            # creneau.save()
            nb_attente = creneau.get_en_attente()
            reservation = Reservation.objects.create(creneau=creneau, user=user,
                en_attente=nb_attente + 1)
            subject = "Inscription du {} en liste d'attente".format(date)
            message = "Bonjour {},\nNous vous confirmons que votre inscription "
            message += "au cours du {} a bien été enregistrée en liste d'attente.\n\n"
            message += "Cordialement,\nAquabike Rieux-volvestre."
            message += "\n\nwww.aquabike-rieuxvolvestre.fr"
            
        else:
            creneau.reservations += 1
            creneau.save()
            reservation = Reservation.objects.create(creneau=creneau, user=user)
            user.credit -= 1
            user.save()
            subject = "Inscription du {}".format(date)
            message = "Bonjour {},\nNous vous confirmons que votre inscription "
            message += "au cours du {} a bien été enregistrée.\n\n"
            message += "Cordialement,\nAquabike Rieux-volvestre."
            message += "\n\nwww.aquabike-rieuxvolvestre.fr"

        message = message.format(user.username, date)    
        send_mail(subject, message, from_email, to)   
    
    return redirect('/accounts/profile/')


class UserAccountView(LoginRequiredMixin, generic.ListView):
    template_name = "reservations/user_account.html"
    context_object_name = 'reservations_list'
    model = Reservation

    def get_queryset(self):
        all_res = Reservation.objects.filter(user=self.request.user)
        reservations = []
        for r in all_res:
            if r.creneau.is_reservable():
                reservations.append(r)
        return reservations

    def get_context_data(self, **kwargs):
        # RECUPERATION DES MESSAGES
        context = super(UserAccountView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        today = datetime.date.today()  
        messages = Message.objects.filter(
            date_debut__lte=today,
            date_fin__gte=today
        )
        context['messages'] = messages

        # RECUPERATION DES CRENEAUX
        start_week = datetime.date.today()  
        end_week = start_week + datetime.timedelta(6)
        end_week_req = start_week + datetime.timedelta(7)
        creneaux = Creneau.objects.filter(date__range=[start_week, end_week_req])
        
        for creneau in creneaux:
            res = creneau.get_user_resa(self.request.user)
            creneau.user_res = res

        context['creneaux'] = creneaux                                                
        return context

class ReservationDelete(LoginRequiredMixin, generic.DeleteView):
    template_name = "reservations/suppr_reservation.html"
    context_object_name = 'reservation'
    model = Reservation
    success_url = reverse_lazy("user_account")

    # TODO: Revoir algo gestion file, probleme le compteur de personne en attente ne se modifie pas correctement
    """
    Quand annulation:
        Recup toutes les resa en attente du creneau
        - Si la resa est en attente:
            - Faire remonter toutes les resa qui etait plus bas dans la file
        - Sinon:
            - Faire remonter toutes les resa en attente
            - Passer la premiere hors de la file d'attente
            - Si pas de remontee en file principale, -1 au compteur d'inscits au creneay
    Le compteur de nbre de personne en attente doit etre géré en comptant le nb de resa en attente
   
    """
    
    def move_queue(self, reservation, creneau, user):
        all_resa = Reservation.objects.filter(creneau=creneau)
        resa_en_attente = [r for r in all_resa if r.is_en_attente]

        if reservation.is_en_attente():
            for res in resa_en_attente:
                if res.en_attente > reservation.en_attente:
                    res.en_attente -= 1
                    res.save()
        else:
            creneau.reservations -= 1
            creneau.save()
            user.credit += 1
            user.save()
            for res in resa_en_attente:
                res.en_attente -= 1
                res.save()
                if res.en_attente == 0:
                    creneau.reservations += 1
                    creneau.save()
                    res.user.credit -= 1
                    res.user.save()
                    if res.user.credit == -1:
                        user_resa = Reservation.objects.filter(user=res.user)
                        for ur in user_resa:
                            if ur.en_attente > 0:
                                ur.delete()

                    # EMAIL SETTINGS
                    from_email=ADMIN_EMAIL
                    to = [res.user.email]
                    date = creneau.date
                    date = date.strftime('%A') + " " +date.strftime('%x')
                    subject = "Confirmation inscription du {}".format(date)
                    message = "Bonjour {},\nNous vous confirmons que votre inscription "
                    message += "au cours du {} a été passée en liste principale.\n\n"
                    message += "Cordialement,\nAquabike Rieux-volvestre."
                    message += "\n\nwww.aquabike-rieuxvolvestre.fr"
                    message = message.format(res.user.username, date)
                    send_mail(subject, message, from_email, to)  
                
        # print("NB ATTENTE", creneau.get_en_attente())


    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        creneau = self.object.creneau
        user = request.user
        self.move_queue(self.object, creneau, user)
        self.object.delete()

        # EMAIL SETTINGS
        from_email=ADMIN_EMAIL
        to = [request.user.email]
        date = creneau.date
        date = date.strftime('%A') + " " + date.strftime('%x')
        subject = "Annulation inscription du {}".format(date)
        message = "Bonjour {},\nNous vous confirmons que votre inscription "
        message += "au cours du {} a bien été annulée.\n\n"
        message += "Cordialement,\nAquabike Rieux-volvestre."
        message += "\n\nwww.aquabike-rieuxvolvestre.fr"
        message = message.format(request.user.username, date)
        send_mail(subject, message, from_email, to) 

        return HttpResponseRedirect(success_url)




