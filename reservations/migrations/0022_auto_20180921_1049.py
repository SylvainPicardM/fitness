# Generated by Django 2.1 on 2018-09-21 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0021_auto_20180921_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='date',
            field=models.DateTimeField(verbose_name='Date du cours'),
        ),
    ]
