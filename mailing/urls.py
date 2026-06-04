from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (
    MailingHomeView,

    RecipientListView,
    RecipientDetailView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDeleteView,

    MessageListView,
    MessageDetailView,
    MessageCreateView,
    MessageUpdateView,
    MessageDeleteView,

    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
)

app_name = MailingConfig.name

urlpatterns = [
    path(
        '',
        MailingHomeView.as_view(),
        name='home'
    ),

    # Recipients

    path(
        'recipients/',
        RecipientListView.as_view(),
        name='recipient_list'
    ),

    path(
        'recipients/create/',
        RecipientCreateView.as_view(),
        name='recipient_create'
    ),

    path(
        'recipients/<int:pk>/',
        RecipientDetailView.as_view(),
        name='recipient_detail'
    ),

    path(
        'recipients/<int:pk>/update/',
        RecipientUpdateView.as_view(),
        name='recipient_update'
    ),

    path(
        'recipients/<int:pk>/delete/',
        RecipientDeleteView.as_view(),
        name='recipient_delete'
    ),

    # Messages

    path(
        'messages/',
        MessageListView.as_view(),
        name='message_list'
    ),

    path(
        'messages/create/',
        MessageCreateView.as_view(),
        name='message_create'
    ),

    path(
        'messages/<int:pk>/',
        MessageDetailView.as_view(),
        name='message_detail'
    ),

    path(
        'messages/<int:pk>/update/',
        MessageUpdateView.as_view(),
        name='message_update'
    ),

    path(
        'messages/<int:pk>/delete/',
        MessageDeleteView.as_view(),
        name='message_delete'
    ),

    # Mailings

    path(
        'mailings/',
        MailingListView.as_view(),
        name='mailing_list'
    ),

    path(
        'mailings/create/',
        MailingCreateView.as_view(),
        name='mailing_create'
    ),

    path(
        'mailings/<int:pk>/',
        MailingDetailView.as_view(),
        name='mailing_detail'
    ),

    path(
        'mailings/<int:pk>/update/',
        MailingUpdateView.as_view(),
        name='mailing_update'
    ),

    path(
        'mailings/<int:pk>/delete/',
        MailingDeleteView.as_view(),
        name='mailing_delete'
    ),
]
