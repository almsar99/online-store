from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from mailing.models import (
    Attempt,
    Mailing,
    Message,
    Recipient,
)
from mailing.services import send_mailing

User = get_user_model()


class MailingModelsTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="test_password_123"
        )

        self.message = Message.objects.create(
            subject="Тестовая тема", body="Тестовое тело письма", owner=self.user
        )

        self.recipient = Recipient.objects.create(
            email="client@example.com",
            full_name="Иван Иванов",
            comment="Тестовый получатель",
            owner=self.user,
        )

    def test_recipient_creation(self):
        self.assertEqual(self.recipient.email, "client@example.com")

        self.assertEqual(self.recipient.full_name, "Иван Иванов")

        self.assertEqual(self.recipient.owner, self.user)

    def test_message_creation(self):
        self.assertEqual(self.message.subject, "Тестовая тема")

        self.assertEqual(self.message.body, "Тестовое тело письма")

        self.assertEqual(self.message.owner, self.user)

    def test_mailing_status_updates_to_created(self):
        mailing = Mailing.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=2),
            message=self.message,
            owner=self.user,
        )

        mailing.update_status()

        self.assertEqual(mailing.status, Mailing.STATUS_CREATED)

    def test_mailing_status_updates_to_started(self):
        mailing = Mailing.objects.create(
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=1),
            message=self.message,
            owner=self.user,
        )

        mailing.update_status()

        self.assertEqual(mailing.status, Mailing.STATUS_STARTED)

    def test_mailing_status_updates_to_finished(self):
        mailing = Mailing.objects.create(
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1),
            message=self.message,
            owner=self.user,
        )

        mailing.update_status()

        self.assertEqual(mailing.status, Mailing.STATUS_FINISHED)


class MailingServiceTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="owner@example.com", password="test_password_123"
        )

        self.message = Message.objects.create(
            subject="Тестовая рассылка", body="Текст тестовой рассылки", owner=self.user
        )

        self.recipient = Recipient.objects.create(
            email="recipient@example.com",
            full_name="Получатель",
            comment="Комментарий",
            owner=self.user,
        )

        self.mailing = Mailing.objects.create(
            start_time=timezone.now() - timedelta(minutes=5),
            end_time=timezone.now() + timedelta(minutes=5),
            message=self.message,
            owner=self.user,
        )

        self.mailing.recipients.add(self.recipient)

    @patch("mailing.services.send_mail")
    def test_send_mailing_creates_successful_attempt(self, mocked_send_mail):
        mocked_send_mail.return_value = 1

        attempts = send_mailing(self.mailing)

        self.assertEqual(len(attempts), 1)

        self.assertEqual(Attempt.objects.count(), 1)

        attempt = Attempt.objects.first()

        self.assertEqual(attempt.mailing, self.mailing)

        self.assertEqual(attempt.status, Attempt.STATUS_SUCCESS)

    @patch("mailing.services.send_mail")
    def test_send_mailing_creates_failed_attempt(self, mocked_send_mail):
        mocked_send_mail.side_effect = Exception("SMTP error")

        attempts = send_mailing(self.mailing)

        self.assertEqual(len(attempts), 1)

        self.assertEqual(Attempt.objects.count(), 1)

        attempt = Attempt.objects.first()

        self.assertEqual(attempt.status, Attempt.STATUS_FAILED)

        self.assertIn("SMTP error", attempt.server_response)


# Views tests


class MailingViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="views_owner@example.com",
            password="test_password_123",
            is_active=True,
        )
        self.other_user = User.objects.create_user(
            email="views_other@example.com",
            password="test_password_123",
            is_active=True,
        )
        self.client.force_login(self.user)

        self.message = Message.objects.create(
            subject="Тема для views",
            body="Тело письма для views",
            owner=self.user,
        )
        self.recipient = Recipient.objects.create(
            email="views_recipient@example.com",
            full_name="Получатель Views",
            comment="Комментарий",
            owner=self.user,
        )
        self.other_recipient = Recipient.objects.create(
            email="other_recipient@example.com",
            full_name="Чужой получатель",
            comment="Комментарий",
            owner=self.other_user,
        )
        self.mailing = Mailing.objects.create(
            start_time=timezone.now() - timedelta(minutes=10),
            end_time=timezone.now() + timedelta(minutes=10),
            message=self.message,
            owner=self.user,
        )
        self.mailing.recipients.add(self.recipient)

    def test_mailing_home_page_for_authenticated_user(self):
        response = self.client.get(reverse("mailing:home"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("total_mailings", response.context)
        self.assertEqual(response.context["total_mailings"], 1)

    def test_recipient_list_shows_only_owner_recipients(self):
        response = self.client.get(reverse("mailing:recipient_list"))

        self.assertEqual(response.status_code, 200)
        recipients = list(response.context["object_list"])
        self.assertIn(self.recipient, recipients)
        self.assertNotIn(self.other_recipient, recipients)

    def test_recipient_list_search(self):
        response = self.client.get(
            reverse("mailing:recipient_list"),
            data={"q": "views_recipient"},
        )

        self.assertEqual(response.status_code, 200)
        recipients = list(response.context["object_list"])
        self.assertIn(self.recipient, recipients)

    def test_recipient_detail_page(self):
        response = self.client.get(
            reverse("mailing:recipient_detail", kwargs={"pk": self.recipient.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.recipient)

    def test_recipient_create_page(self):
        response = self.client.get(reverse("mailing:recipient_create"))

        self.assertEqual(response.status_code, 200)

    def test_recipient_create_post(self):
        response = self.client.post(
            reverse("mailing:recipient_create"),
            data={
                "email": "new_recipient@example.com",
                "full_name": "Новый Получатель",
                "comment": "Новый комментарий",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Recipient.objects.filter(email="new_recipient@example.com").exists()
        )

    def test_message_list_page(self):
        response = self.client.get(reverse("mailing:message_list"))

        self.assertEqual(response.status_code, 200)
        messages = list(response.context["object_list"])
        self.assertIn(self.message, messages)

    def test_message_detail_page(self):
        response = self.client.get(
            reverse("mailing:message_detail", kwargs={"pk": self.message.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["object"], self.message)

    def test_message_create_post(self):
        response = self.client.post(
            reverse("mailing:message_create"),
            data={
                "subject": "Новая тема",
                "body": "Новое тело письма",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Message.objects.filter(subject="Новая тема").exists())

    def test_mailing_list_page(self):
        response = self.client.get(reverse("mailing:mailing_list"))

        self.assertEqual(response.status_code, 200)
        mailings = list(response.context["object_list"])
        self.assertIn(self.mailing, mailings)

    def test_mailing_detail_page_updates_status_and_context(self):
        response = self.client.get(
            reverse("mailing:mailing_detail", kwargs={"pk": self.mailing.pk})
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["recipients_count"], 1)
        self.assertIn("attempts_count", response.context)

    @patch("mailing.views.send_mailing")
    def test_mailing_send_view_success(self, mocked_send_mailing):
        mocked_send_mailing.return_value = [Attempt(mailing=self.mailing)]

        response = self.client.post(
            reverse("mailing:mailing_send", kwargs={"pk": self.mailing.pk})
        )

        self.assertEqual(response.status_code, 302)
        mocked_send_mailing.assert_called_once_with(self.mailing)
