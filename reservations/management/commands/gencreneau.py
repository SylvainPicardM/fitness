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
    
    def handle(self, *args, **options):
        cours = Cours.objects.all()
        now = datetime.now()
        until = now + timedelta(days=7)
        cours = Cours.objects.all()
        days = [ x for x in self._perdelta(now, until, timedelta(days=1))]
        for day in days:
            for cour in cours:
                if int(self.day_dict[cour.jour]) == int(day.strftime("%w")):
                    date = day
                    new_hour = cour.heure
                    date = date.replace(hour=new_hour.hour,
                                        minute=new_hour.minute, 
                                        second=0,
                                        microsecond=0)
                    print(date)
                    obj, created = Creneau.objects.get_or_create(
                        cours=cour,
                        date=date
                    )
                    if created:
                        print(datetime.now())
                        print("Creneau created")
                        print(obj)
