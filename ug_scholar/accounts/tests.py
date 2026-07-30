from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthenticationPersistenceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="admin@example.com",
            password="original-password",
            fullname="Admin User",
            is_staff=True,
        )

    def test_login_survives_refresh_and_protected_page_navigation(self):
        response = self.client.post(
            reverse("accounts:login"),
            {
                "email": "  ADMIN@EXAMPLE.COM  ",
                "password": "original-password",
            },
        )
        self.assertRedirects(response, reverse("dashboard:index"))

        for route_name in (
            "dashboard:index",
            "dashboard:administrators",
            "dashboard:manual_fetch",
            "dashboard:logs",
            "dashboard:profile",
        ):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    self.client.session.get("_auth_user_id"),
                    str(self.user.pk),
                )

    def test_get_logout_does_not_destroy_an_authenticated_session(self):
        self.client.force_login(self.user)

        self.client.get(reverse("accounts:logout"))

        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.user.pk),
        )
        self.assertEqual(
            self.client.get(reverse("dashboard:manual_fetch")).status_code,
            200,
        )

    def test_post_logout_ends_the_session(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("accounts:logout"))

        self.assertRedirects(response, reverse("dashboard:index"))
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_password_change_keeps_current_session_authenticated(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("dashboard:profile"),
            {
                "fullname": self.user.fullname,
                "email": self.user.email,
                "phone": "",
                "password": "new-secure-password",
                "password2": "new-secure-password",
            },
        )

        self.assertRedirects(response, reverse("dashboard:profile"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new-secure-password"))
        self.assertEqual(
            self.client.session.get("_auth_user_id"),
            str(self.user.pk),
        )
        self.assertEqual(
            self.client.get(reverse("dashboard:manual_fetch")).status_code,
            200,
        )

    def test_anonymous_admin_form_gets_redirect_instead_of_error(self):
        for route_name in (
            "dashboard:create_author",
            "dashboard:bulk_upload_authors",
            "dashboard:profile",
        ):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertRedirects(response, reverse("dashboard:index"))
