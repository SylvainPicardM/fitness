# Generated by Django 2.1 on 2018-09-15 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0015_auto_20180914_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='en_attente',
            field=models.BooleanField(default=False, verbose_name='en_attente'),
        ),
    ]