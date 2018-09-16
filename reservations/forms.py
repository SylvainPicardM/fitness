from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUser, Creneau
import datetime

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = ('username', 'prenom', 'nom', 'email')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ('username', 'prenom', 'nom', 'email')


class DateInput(forms.DateInput):
    input_type = 'date'

class AutoCreneauForm(forms.ModelForm):
    class Meta:
        model = Creneau
        fields = ['date']
        widgets = {
            'date': DateInput()
        }