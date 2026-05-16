from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    UpdateView,
)

from users.forms import (
    UserRegisterForm,
    UserLoginForm,
    UserProfileForm,
)
from users.models import User


class UserRegisterView(CreateView):

    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):

        user = form.save()

        send_mail(
            subject='Добро пожаловать!',
            message='Спасибо за регистрацию в нашем магазине.',
            from_email='admin@localhost',
            recipient_list=[user.email],
            fail_silently=True,
        )

        login(
            self.request,
            user,
            backend='users.backends.EmailBackend'
        )

        return super().form_valid(form)


class UserLoginView(LoginView):

    form_class = UserLoginForm
    template_name = 'users/login.html'


class UserLogoutView(LogoutView):

    next_page = reverse_lazy('catalog:home')


class UserProfileView(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('catalog:home')

    login_url = '/users/login/'

    def get_object(self, queryset=None):

        return self.request.user
