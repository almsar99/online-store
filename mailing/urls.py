from django.urls import path

from mailing.apps import MailingConfig
from mailing.views import (
    MailingHomeView,
)

app_name = MailingConfig.name

urlpatterns = [
    path(
        '',
        MailingHomeView.as_view(),
        name='home'
    ),
]
