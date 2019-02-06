from django.core.management.base import BaseCommand, CommandError
from reservations.models import Creneau, Cours
from datetime import datetime, timedelta
from django.core.mail import send_mail


class Command(BaseCommand):
    help = "Test envoi de mail via smtp"

    def handle(self, *args, **options):
        from_email="contact@aquabike-rieuxvolvestre.fr"
        to = ["picard.sylvain3@gmail.com"]
        subject = "Aquabike test email"
        message = "Working email system"
        send_mail(subject, message, from_email, to)
