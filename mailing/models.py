from django.conf import settings
from django.db import models
from django.utils import timezone


class Recipient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mailing_recipients',
        verbose_name='Пользователь сайта'
    )

    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )

    full_name = models.CharField(
        max_length=255,
        verbose_name='ФИО'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipients',
        verbose_name='Владелец'
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Получатель'
        verbose_name_plural = 'Получатели'
        permissions = [
            (
                'can_view_all_recipients',
                'Can view all recipients'
            ),
        ]


class Message(models.Model):
    subject = models.CharField(
        max_length=255,
        verbose_name='Тема письма'
    )

    body = models.TextField(
        verbose_name='Текст письма'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Владелец'
    )

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):

    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_FINISHED = 'finished'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_FINISHED, 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name='Начало рассылки'
    )

    end_time = models.DateTimeField(
        verbose_name='Окончание рассылки'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name='Статус'
    )

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Сообщение'
    )

    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name='Получатели'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name='Владелец'
    )

    def update_status(self):

        now = timezone.now()

        if now < self.start_time:
            new_status = self.STATUS_CREATED

        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_STARTED

        else:
            new_status = self.STATUS_FINISHED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f'Рассылка #{self.pk}'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        permissions = [
            (
                'can_view_all_mailings',
                'Can view all mailings'
            ),
            (
                'can_disable_mailing',
                'Can disable mailing'
            ),
        ]


class Attempt(models.Model):

    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата попытки'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        verbose_name='Статус'
    )

    server_response = models.TextField(
        blank=True,
        verbose_name='Ответ сервера'
    )

    mailing = models.ForeignKey(
        Mailing,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Рассылка'
    )

    def __str__(self):
        return f'{self.get_status_display()}'

    class Meta:
        verbose_name = 'Попытка отправки'
        verbose_name_plural = 'Попытки отправки'
