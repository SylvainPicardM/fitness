# Generated by Django 2.1 on 2018-09-21 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0018_auto_20180915_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='reservations_max',
            field=models.IntegerField(default=19, verbose_name='Nb de reservation max'),
        ),
    ]
