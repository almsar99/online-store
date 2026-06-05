from django.contrib import messages
from django.contrib.auth import (
    login,
    logout,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
)
from django.shortcuts import (
    redirect,
    get_object_or_404,
)
from django.core.mail import send_mail
from django.urls import (
    reverse,
    reverse_lazy,
)
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_encode,
    urlsafe_base64_decode,
)
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

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(
            force_bytes(user.pk)
        )
        token = default_token_generator.make_token(user)

        activation_url = self.request.build_absolute_uri(
            reverse(
                'users:email_confirm',
                kwargs={
                    'uidb64': uid,
                    'token': token,
                }
            )
        )

        send_mail(
            subject='Подтверждение email',
            message=(
                'Спасибо за регистрацию в нашем магазине.\n\n'
                'Для подтверждения email перейдите по ссылке:\n'
                f'{activation_url}'
            ),
            from_email='admin@localhost',
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            'Регистрация почти завершена. Проверьте email и подтвердите аккаунт.'
        )

        return redirect('users:login')


# Email confirmation view
class UserEmailConfirmView(CreateView):

    model = User
    fields = []
    template_name = 'users/register.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(
                User,
                pk=user_id
            )
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(
                update_fields=[
                    'is_active',
                ]
            )

            messages.success(
                request,
                'Email подтверждён. Теперь вы можете войти.'
            )
        else:
            messages.error(
                request,
                'Ссылка подтверждения недействительна или устарела.'
            )

        return redirect('users:login')


class UserLoginView(LoginView):

    form_class = UserLoginForm
    template_name = 'users/login.html'


class UserLogoutView(LogoutView):

    next_page = reverse_lazy('catalog:home')

    def get(self, request, *args, **kwargs):
        logout(request)

        return redirect(self.next_page)


class UserProfileView(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('catalog:home')

    login_url = '/users/login/'

    def get_object(self, queryset=None):

        return self.request.user
