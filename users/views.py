from django.contrib import messages
from django.contrib.auth import logout
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
from django.views import View
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
)

from users.forms import (
    UserRegisterForm,
    UserLoginForm,
    UserProfileForm,
)
from users.models import User


def user_can_view_all_users(user):
    return user.has_perm("users.can_view_all_users")


def user_can_block_user(user):
    return user.has_perm("users.can_block_user")


class UserRegisterView(CreateView):

    model = User
    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):

        user = form.save(commit=False)
        user.is_active = False
        user.save()

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_url = self.request.build_absolute_uri(
            reverse(
                "users:email_confirm",
                kwargs={
                    "uidb64": uid,
                    "token": token,
                },
            )
        )

        send_mail(
            subject="Подтверждение email",
            message=(
                "Спасибо за регистрацию в нашем магазине.\n\n"
                "Для подтверждения email перейдите по ссылке:\n"
                f"{activation_url}"
            ),
            from_email="admin@localhost",
            recipient_list=[user.email],
            fail_silently=False,
        )

        messages.success(
            self.request,
            "Регистрация почти завершена. Проверьте email и подтвердите аккаунт.",
        )

        return redirect("users:login")


# Email confirmation view
class UserEmailConfirmView(CreateView):

    model = User
    fields = []
    template_name = "users/register.html"

    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            user_id = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=user_id)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.save(
                update_fields=[
                    "is_active",
                ]
            )

            messages.success(request, "Email подтверждён. Теперь вы можете войти.")
        else:
            messages.error(
                request, "Ссылка подтверждения недействительна или устарела."
            )

        return redirect("users:login")


class UserLoginView(LoginView):

    form_class = UserLoginForm
    template_name = "users/login.html"


class UserLogoutView(LogoutView):

    next_page = reverse_lazy("catalog:home")

    def get(self, request, *args, **kwargs):
        logout(request)

        return redirect(self.next_page)


class UserProfileView(LoginRequiredMixin, UpdateView):

    model = User
    form_class = UserProfileForm
    template_name = "users/profile.html"
    success_url = reverse_lazy("catalog:home")

    login_url = "/users/login/"

    def get_object(self, queryset=None):

        return self.request.user


class UserListView(LoginRequiredMixin, ListView):

    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def dispatch(self, request, *args, **kwargs):
        if not user_can_view_all_users(request.user):
            messages.error(
                request, "У вас нет прав для просмотра списка пользователей."
            )

            return redirect("catalog:home")

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return User.objects.all().order_by("email")


class UserBlockView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if not user_can_block_user(request.user):
            messages.error(request, "У вас нет прав для блокировки пользователей.")

            return redirect("catalog:home")

        user = get_object_or_404(User, pk=pk)

        if user == request.user:
            messages.error(request, "Нельзя заблокировать самого себя.")

            return redirect("users:user_list")

        user.is_active = False
        user.save(
            update_fields=[
                "is_active",
            ]
        )

        messages.success(request, "Пользователь заблокирован.")

        return redirect("users:user_list")


class UserUnblockView(LoginRequiredMixin, View):

    def post(self, request, pk):
        if not user_can_block_user(request.user):
            messages.error(request, "У вас нет прав для разблокировки пользователей.")

            return redirect("catalog:home")

        user = get_object_or_404(User, pk=pk)

        user.is_active = True
        user.save(
            update_fields=[
                "is_active",
            ]
        )

        messages.success(request, "Пользователь разблокирован.")

        return redirect("users:user_list")
