from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (
    MailingHomeView,
    RecipientListView,
    RecipientDetailView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDeleteView,
)

app_name = MailingConfig.name

urlpatterns = [
    path(
        '',
        MailingHomeView.as_view(),
        name='home'
    ),

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
]
