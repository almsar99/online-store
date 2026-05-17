from django.db import models

from users.models import User


class Category(models.Model):

    name = models.CharField(
        max_length=100,
        verbose_name='Наименование'
    )

    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:

        verbose_name = 'Категория'

        verbose_name_plural = 'Категории'

    def __str__(self):

        return self.name


class Product(models.Model):

    STATUS_DRAFT = 'draft'

    STATUS_PENDING = 'pending'

    STATUS_PUBLISHED = 'published'

    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (
            STATUS_DRAFT,
            'Черновик'
        ),
        (
            STATUS_PENDING,
            'На проверке'
        ),
        (
            STATUS_PUBLISHED,
            'Опубликован'
        ),
        (
            STATUS_REJECTED,
            'Отклонён'
        ),
    ]

    name = models.CharField(
        max_length=100,
        verbose_name='Наименование'
    )

    description = models.TextField(
        verbose_name='Описание'
    )

    image = models.ImageField(
        upload_to='products/',
        verbose_name='Изображение',
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Категория'
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец'
    )

    price = models.IntegerField(
        verbose_name='Цена за покупку'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name='Статус'
    )

    moderator_comment = models.TextField(
        verbose_name='Комментарий модератора',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )

    class Meta:

        verbose_name = 'Продукт'

        verbose_name_plural = 'Продукты'

        permissions = [
            (
                'can_unpublish_product',
                'Can unpublish product'
            ),
        ]

    def __str__(self):

        return self.name


class Contact(models.Model):

    city = models.CharField(
        max_length=100,
        verbose_name='Город'
    )

    phone = models.CharField(
        max_length=35,
        verbose_name='Телефон'
    )

    email = models.EmailField(
        verbose_name='Email'
    )

    class Meta:

        verbose_name = 'Контакт'

        verbose_name_plural = 'Контакты'

    def __str__(self):

        return self.city
