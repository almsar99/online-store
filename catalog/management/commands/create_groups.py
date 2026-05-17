from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Blog
from catalog.models import Product


class Command(BaseCommand):

    help = 'Создает группы и назначает права'

    def handle(self, *args, **options):

        product_content_type = ContentType.objects.get_for_model(Product)

        blog_content_type = ContentType.objects.get_for_model(Blog)

        unpublish_permission = Permission.objects.get(
            codename='can_unpublish_product',
            content_type=product_content_type
        )

        delete_product_permission = Permission.objects.get(
            codename='delete_product',
            content_type=product_content_type
        )

        manage_blog_permission = Permission.objects.get(
            codename='can_manage_blog',
            content_type=blog_content_type
        )

        moderators_group, created = Group.objects.get_or_create(
            name='Модератор продуктов'
        )

        moderators_group.permissions.set([
            unpublish_permission,
            delete_product_permission,
        ])

        content_managers_group, created = Group.objects.get_or_create(
            name='Контент-менеджер'
        )

        content_managers_group.permissions.set([
            manage_blog_permission,
        ])

        self.stdout.write(
            self.style.SUCCESS(
                'Группы успешно созданы'
            )
        )
