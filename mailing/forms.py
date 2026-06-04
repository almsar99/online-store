from django import forms
from django.utils import timezone

from mailing.models import (
    Recipient,
    Message,
    Mailing,
)


class RecipientForm(forms.ModelForm):

    class Meta:
        model = Recipient
        fields = (
            'email',
            'full_name',
            'comment',
        )


class MessageForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = (
            'subject',
            'body',
        )


class MailingForm(forms.ModelForm):

    class Meta:
        model = Mailing
        fields = (
            'start_time',
            'end_time',
            'message',
            'recipients',
        )

        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                }
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                }
            ),
            'recipients': forms.CheckboxSelectMultiple(),
        }

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')

        if start_time and start_time < timezone.now():
            raise forms.ValidationError(
                'Дата начала рассылки не может быть в прошлом.'
            )

        return start_time

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                'Дата начала рассылки должна быть раньше даты окончания.'
            )

        return cleaned_data
