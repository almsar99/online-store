from django.contrib import admin

from mailing.models import (
    Recipient,
    Message,
    Mailing,
    Attempt,
)


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'full_name',
        'owner',
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'subject',
        'owner',
    )


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'status',
        'start_time',
        'end_time',
        'owner',
    )


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'attempt_time',
        'status',
        'mailing',
    )
