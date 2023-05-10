from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class RegisterForm(UserCreationForm):
    real_name = forms.CharField(max_length=64, required=True, help_text='Required.')

    class Meta:
        model = CustomUser
        fields = ('username', 'real_name', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
