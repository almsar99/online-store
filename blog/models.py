from django.db import models


class Blog(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )

    content = models.TextField(
        verbose_name='Содержимое'
    )

    preview = models.ImageField(
        upload_to='blog/',
        verbose_name='Превью',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликовано'
    )

    views_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество просмотров'
    )

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.title
