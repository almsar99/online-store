from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    AuthenticationForm,
)

from users.models import User


class UserRegisterForm(UserCreationForm):

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User

        fields = (
            "email",
            "password1",
            "password2",
            "avatar",
            "phone",
            "country",
        )

        widgets = {
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }


class UserLoginForm(AuthenticationForm):

    username = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = User

        fields = (
            "avatar",
            "phone",
            "country",
        )

        widgets = {
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
        }
