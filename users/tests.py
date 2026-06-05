from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class UserAuthenticationTestCase(TestCase):

    def test_user_registration_creates_inactive_user(self):
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "new_user@example.com",
                "password1": "StrongPassword123",
                "password2": "StrongPassword123",
            },
        )

        self.assertEqual(response.status_code, 302)

        user = User.objects.get(email="new_user@example.com")

        self.assertFalse(user.is_active)

    def test_active_user_can_login(self):
        User.objects.create_user(
            email="active@example.com", password="StrongPassword123", is_active=True
        )

        response = self.client.post(
            reverse("users:login"),
            data={
                "username": "active@example.com",
                "password": "StrongPassword123",
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_to_home_page(self):
        user = User.objects.create_user(
            email="logout@example.com", password="StrongPassword123", is_active=True
        )
        self.client.force_login(user)

        response = self.client.post(reverse("users:logout"))

        self.assertEqual(response.status_code, 302)

    def test_regular_user_cannot_access_user_list(self):
        user = User.objects.create_user(
            email="regular@example.com", password="StrongPassword123", is_active=True
        )
        self.client.force_login(user)

        response = self.client.get(reverse("users:user_list"))

        self.assertEqual(response.status_code, 302)


class UserManagementViewsTestCase(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(
            email="manager@example.com",
            password="StrongPassword123",
            is_active=True,
        )
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="StrongPassword123",
            is_active=True,
        )

        view_users_permission = Permission.objects.get(codename="can_view_all_users")
        block_user_permission = Permission.objects.get(codename="can_block_user")

        self.manager.user_permissions.add(
            view_users_permission,
            block_user_permission,
        )

    def test_profile_page_is_available_for_authenticated_user(self):
        self.client.force_login(self.target_user)

        response = self.client.get(reverse("users:profile"))

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_manager_can_open_user_list(self):
        self.client.force_login(self.manager)

        response = self.client.get(reverse("users:user_list"))

        self.assertEqual(
            response.status_code,
            200,
        )
        self.assertContains(
            response,
            "target@example.com",
        )

    def test_manager_can_block_user(self):
        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("users:user_block", kwargs={"pk": self.target_user.pk})
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.target_user.refresh_from_db()

        self.assertFalse(
            self.target_user.is_active,
        )

    def test_manager_can_unblock_user(self):
        self.target_user.is_active = False
        self.target_user.save(update_fields=["is_active"])

        self.client.force_login(self.manager)

        response = self.client.post(
            reverse("users:user_unblock", kwargs={"pk": self.target_user.pk})
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.target_user.refresh_from_db()

        self.assertTrue(
            self.target_user.is_active,
        )
