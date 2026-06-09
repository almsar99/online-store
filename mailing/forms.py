from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from mailing.models import (
    Recipient,
    Message,
    Mailing,
)

User = get_user_model()


class RecipientForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Зарегистрированный пользователь",
    )

    class Meta:
        model = Recipient
        fields = (
            "user",
            "email",
            "full_name",
            "comment",
        )

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        self.fields["email"].required = False
        self.fields["full_name"].required = False

        if current_user:
            can_view_all_users = (
                current_user.is_staff
                or current_user.is_superuser
                or current_user.has_perm("mailing.can_view_all_recipients")
                or current_user.groups.filter(name="Модератор продуктов").exists()
                or current_user.groups.filter(name="Менеджер рассылок").exists()
            )

            if can_view_all_users:
                self.fields["user"].queryset = User.objects.all()
            else:
                self.fields["user"].queryset = User.objects.filter(pk=current_user.pk)

    def clean(self):
        cleaned_data = super().clean()

        user = cleaned_data.get("user")
        email = cleaned_data.get("email")
        full_name = cleaned_data.get("full_name")

        if user:
            cleaned_data["email"] = user.email

            if not full_name:
                if hasattr(user, "get_full_name") and user.get_full_name():
                    cleaned_data["full_name"] = user.get_full_name()
                else:
                    cleaned_data["full_name"] = user.email

        else:
            if not email:
                self.add_error(
                    "email",
                    "Укажите email или выберите зарегистрированного пользователя.",
                )

            if not full_name:
                self.add_error(
                    "full_name",
                    "Укажите ФИО или выберите зарегистрированного пользователя.",
                )

        return cleaned_data


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = (
            "subject",
            "body",
        )


class MailingForm(forms.ModelForm):

    class Meta:
        model = Mailing
        fields = (
            "start_time",
            "end_time",
            "message",
            "recipients",
        )

        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "recipients": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["message"].queryset = Message.objects.filter(owner=self.user)

            self.fields["recipients"].queryset = Recipient.objects.filter(
                owner=self.user
            )

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")

        if start_time and start_time < timezone.now():
            raise forms.ValidationError("Дата начала рассылки не может быть в прошлом.")

        return start_time

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                "Дата начала рассылки должна быть раньше даты окончания."
            )

        return cleaned_data
