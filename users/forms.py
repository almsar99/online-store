from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User

        fields = (
            'email',
            'password1',
            'password2',
            'avatar',
            'phone',
            'country',
        )

        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),

            'phone': forms.TextInput(attrs={
                'class': 'form-control'
            }),

            'country': forms.TextInput(attrs={
                'class': 'form-control'
            }),
        }

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control'
        })
    )
