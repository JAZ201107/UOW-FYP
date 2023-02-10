from django.forms import  ModelForm
from django.contrib.auth.forms import UserCreationForm
from django import forms
from apps.api.models import User

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = [
            'email',
            'password',
            'password2'
        ]