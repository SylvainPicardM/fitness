# Generated by Django 2.1 on 2018-09-21 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservations', '0020_auto_20180921_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creneau',
            name='date',
            field=models.DateTimeField(unique_for_date=True, verbose_name='Date du cours'),
        ),
    ]