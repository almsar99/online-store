from django.urls import (
    path,
    reverse_lazy,
)
from django.contrib.auth import views as auth_views

from users.apps import UsersConfig
from users.views import (
    UserRegisterView,
    UserEmailConfirmView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
)

app_name = UsersConfig.name

urlpatterns = [

    # Регистрация
    path(
        'register/',
        UserRegisterView.as_view(),
        name='register'
    ),

    path(
        'email-confirm/<uidb64>/<token>/',
        UserEmailConfirmView.as_view(),
        name='email_confirm'
    ),

    # Вход
    path(
        'login/',
        UserLoginView.as_view(),
        name='login'
    ),

    # Выход
    path(
        'logout/',
        UserLogoutView.as_view(),
        name='logout'
    ),

    # Профиль
    path(
        'profile/',
        UserProfileView.as_view(),
        name='profile'
    ),

    # Восстановление пароля
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done')
        ),
        name='password_reset'
    ),

    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),

    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),

]
