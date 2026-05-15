from django.urls import path

from users.apps import UsersConfig
from users.views import (
    UserRegisterView,
    UserLoginView,
    UserLogoutView,
)

app_name = UsersConfig.name

urlpatterns = [

    # Регистрация
    path(
        'register/',
        UserRegisterView.as_view(),
        name='register'
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

]
