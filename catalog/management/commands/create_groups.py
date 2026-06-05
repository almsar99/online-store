from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from blog.models import Blog
from catalog.models import Product
from mailing.models import (
    Recipient,
    Mailing,
)
from users.models import User


class Command(BaseCommand):

    help = 'Создает группы и назначает права'

    def handle(self, *args, **options):

        product_content_type = ContentType.objects.get_for_model(Product)

        blog_content_type = ContentType.objects.get_for_model(Blog)

        recipient_content_type = ContentType.objects.get_for_model(Recipient)

        mailing_content_type = ContentType.objects.get_for_model(Mailing)

        user_content_type = ContentType.objects.get_for_model(User)

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

        view_all_recipients_permission = Permission.objects.get(
            codename='can_view_all_recipients',
            content_type=recipient_content_type
        )

        view_all_mailings_permission = Permission.objects.get(
            codename='can_view_all_mailings',
            content_type=mailing_content_type
        )

        disable_mailing_permission = Permission.objects.get(
            codename='can_disable_mailing',
            content_type=mailing_content_type
        )

        view_all_users_permission = Permission.objects.get(
            codename='can_view_all_users',
            content_type=user_content_type
        )

        block_user_permission = Permission.objects.get(
            codename='can_block_user',
            content_type=user_content_type
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

        mailing_managers_group, created = Group.objects.get_or_create(
            name='Менеджер рассылок'
        )

        mailing_managers_group.permissions.set([
            view_all_recipients_permission,
            view_all_mailings_permission,
            disable_mailing_permission,
            view_all_users_permission,
            block_user_permission,
        ])

        self.stdout.write(
            self.style.SUCCESS(
                'Группы успешно созданы'
            )
        )
