from django.core.management.base import BaseCommand, CommandError
from reservations.models import Creneau, Cours
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = "Creation automatique des creneaux"

    def __init__(self, *args, **kwargs):
        self.day_dict= {"DIM": 0, "LUN": 1, "MAR": 2, "MER": 3, "JEU": 4, "VEN": 5,
                        "SAM": 6}

    def _perdelta(self, start, end, delta):
        curr = start
        while curr < end:
            yield curr
            curr += delta
    
    def _create_cours(self, day, cour):
        date = day
        new_hour = cour.heure
        date = date.replace(hour=new_hour.hour,
                            minute=new_hour.minute, 
                            second=0,
                            microsecond=0)
        obj, created = Creneau.objects.get_or_create(
            cours=cour,
            date=date,
            reservations_max=cour.nb_velos,
        )
        if created:
            print(datetime.now())
            print("Creneau created")
            print(obj)
    

    def handle(self, *args, **options):
        cours = Cours.objects.all()
        now = datetime.now()
        until = now + timedelta(days=7)
        cours = Cours.objects.all()
        days = [ x for x in self._perdelta(now, until, timedelta(days=1))]
        for day in days:
            for cour in cours:
                if cour.actif:
                    if int(self.day_dict[cour.jour]) == int(day.strftime("%w")):
                        if cour.actif_every == 1:
                            self._create_cours(day, cour)
                        elif cour.actif_every > 1:
                            # Recupere le dernier creneau pour le jour
                            creneaux = Creneau.objects.filter(cours=cour).order_by("-date")
                            if len(creneaux) == 0:
                                self._create_cours(day, cour)
                            else:
                                creneau = creneaux[0]
                                delta_jours = (7 * cour.actif_every) - 1
                                delta = day - creneau.date
                                if delta.days >= delta_jours:
                                    self._create_cours(day, cour)

