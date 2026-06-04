from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView


class MailingHomeView(TemplateView):
    template_name = 'mailing/home.html'
