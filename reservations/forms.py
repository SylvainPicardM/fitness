from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import MyUser


class CustomUserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = MyUser
        fields = ('username', 'prenom', 'nom', 'email')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = MyUser
        fields = ('username', 'prenom', 'nom', 'email')
