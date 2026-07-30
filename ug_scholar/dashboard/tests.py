from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.test import RequestFactory, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from api.models import Author, Profile, Publication, SyncRun
from dashboard.views.authors import AuthorsView
from dashboard.views.publications import PublicationsView


class ListPerformanceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        for index in range(5):
            profile = Profile.objects.create(
                scholar_id=f"scholar-{index}", name=f"Author {index}"
            )
            author = Author.objects.create(profile=profile)
            publication = Publication.objects.create(
                title=f"Paper {index}",
                year=2025,
                source="openalex",
                external_id=f"W{index}",
                citations=index,
            )
            author.publications.add(publication)

    def _request(self, path):
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        return request

    def test_author_list_uses_bounded_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = AuthorsView.as_view()(self._request("/authors/"))
            response.content
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(queries), 3)

    def test_publication_list_uses_bounded_queries(self):
        with CaptureQueriesContext(connection) as queries:
            response = PublicationsView.as_view()(
                self._request("/publications/")
            )
            response.content
        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(queries), 4)


class ManualFetchTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            scholar_id="fetch-author", name="Fetch Author"
        )
        self.staff = get_user_model().objects.create_user(
            email="staff@example.com",
            password="password",
            is_staff=True,
        )

    def test_manual_fetch_requires_an_administrator(self):
        response = self.client.get(reverse("dashboard:manual_fetch"))
        self.assertRedirects(response, reverse("dashboard:index"))

    def test_staff_can_choose_provider_and_author(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            reverse("dashboard:manual_fetch"),
            {
                "provider": "openalex",
                "profile_id": str(self.profile.pk),
            },
        )
        self.assertRedirects(response, reverse("dashboard:manual_fetch"))
        run = SyncRun.objects.get()
        self.assertEqual(run.provider, "openalex")
        self.assertEqual(run.profile_ids, [self.profile.pk])
        self.assertEqual(run.requested_by, self.staff)

    @override_settings(SERPAPI_API_KEY="")
    def test_unconfigured_serpapi_is_selectable_but_fails_gracefully(self):
        self.client.force_login(self.staff)
        page = self.client.get(reverse("dashboard:manual_fetch"))
        self.assertContains(page, 'value="google_scholar"')
        self.assertNotContains(page, 'value="google_scholar" disabled')

        response = self.client.post(
            reverse("dashboard:manual_fetch"),
            {"provider": "google_scholar"},
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse("dashboard:manual_fetch"),
            status_code=302,
            target_status_code=200,
        )
        self.assertContains(
            response,
            "SERPAPI_API_KEY is not configured",
        )
        self.assertFalse(SyncRun.objects.exists())

    @override_settings(SERPAPI_API_KEY="test-key")
    @patch("dashboard.views.manual_fetch.get_provider")
    def test_configured_serpapi_fetch_can_be_queued(self, get_provider):
        self.client.force_login(self.staff)

        response = self.client.post(
            reverse("dashboard:manual_fetch"),
            {
                "provider": "google_scholar",
                "profile_id": str(self.profile.pk),
            },
        )

        self.assertRedirects(response, reverse("dashboard:manual_fetch"))
        run = SyncRun.objects.get()
        get_provider.assert_called_once_with("google_scholar")
        self.assertEqual(run.provider, "google_scholar")
        self.assertEqual(run.profile_ids, [self.profile.pk])

    def test_admin_sidebar_places_manual_fetch_between_accounts_and_logs(self):
        self.client.force_login(self.staff)
        content = self.client.get(reverse("dashboard:index")).content.decode()
        administrators = content.index(reverse("dashboard:administrators"))
        manual_fetch = content.index(reverse("dashboard:manual_fetch"))
        logs = content.index(reverse("dashboard:logs"))
        self.assertLess(administrators, manual_fetch)
        self.assertLess(manual_fetch, logs)

    def test_manual_fetch_page_live_polls_run_status(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard:manual_fetch"))

        self.assertContains(
            response,
            reverse("dashboard:manual_fetch_status"),
        )
        self.assertContains(response, "pollFetchStatus")

    def test_staff_can_read_live_fetch_progress(self):
        run = SyncRun.objects.create(
            provider="openalex",
            total_profiles=267,
            processed_profiles=12,
            updated_publications=34,
            requested_by=self.staff,
        )
        self.client.force_login(self.staff)

        response = self.client.get(reverse("dashboard:manual_fetch_status"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["active"])
        self.assertEqual(payload["runs"][0]["id"], run.pk)
        self.assertEqual(payload["runs"][0]["processed_profiles"], 12)
        self.assertEqual(payload["runs"][0]["updated_publications"], 34)

    def test_missing_stored_avatar_has_a_static_fallback(self):
        self.staff.profile_picture.name = "profile_pictures/missing-avatar.png"
        self.staff.save(update_fields=["profile_picture"])
        self.client.force_login(self.staff)
        response = self.client.get(reverse("dashboard:index"))
        self.assertContains(response, self.staff.profile_picture.url)
        self.assertContains(
            response,
            "this.src='/static/dashboard/assets/images/app/google-scholar.png'",
        )


class DashboardThematicChartTests(TestCase):
    def test_dashboard_uses_stored_thematic_counts_not_demo_values(self):
        Publication.objects.create(
            title="A clinical study",
            year=2025,
            source="openalex",
            external_id="W-health",
            thematic_area="Health Sciences",
        )
        response = self.client.get(reverse("dashboard:index"))
        self.assertContains(
            response,
            '&quot;name&quot;: &quot;Health Sciences&quot;, '
            '&quot;count&quot;: 1',
        )
        self.assertNotContains(response, 'style="overflow-y: scroll;"')
        self.assertNotContains(response, 'class="product-list ')


class GlobalSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        profile = Profile.objects.create(
            scholar_id="ada-scholar-id",
            name="Ada Lovelace",
            email="ada@example.com",
            affiliation="University of Ghana",
            college="College of Basic and Applied Sciences",
            school="School of Physical and Mathematical Sciences",
            department="Department of Computer Science",
            rank="Professor",
            h_index=42,
        )
        author = Author.objects.create(profile=profile)
        publication = Publication.objects.create(
            title="Machine learning for malaria diagnosis",
            year=2025,
            source="openalex",
            external_id="W-MALARIA",
            doi="10.1000/malaria",
            authors="Ada Lovelace and Grace Hopper",
            journal="Journal of Medical Informatics",
            citations=123,
            thematic_area="Health Sciences",
        )
        author.publications.add(publication)

    def test_header_search_submits_to_global_search(self):
        response = self.client.get(reverse("dashboard:index"))

        self.assertContains(
            response,
            f'action="{reverse("dashboard:global_search")}"',
        )
        self.assertContains(response, 'name="q"')

    def test_search_finds_publications_by_title(self):
        response = self.client.get(
            reverse("dashboard:global_search"),
            {"q": "malaria"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Machine learning for malaria diagnosis")
        self.assertContains(response, "123")

    def test_search_finds_authors_and_organizational_units(self):
        author_response = self.client.get(
            reverse("dashboard:global_search"),
            {"q": "Ada Lovelace"},
        )
        organization_response = self.client.get(
            reverse("dashboard:global_search"),
            {"q": "Computer Science"},
        )

        self.assertContains(author_response, "Ada Lovelace")
        self.assertContains(organization_response, "Department of Computer Science")
        self.assertContains(
            organization_response,
            reverse("dashboard:department_details"),
        )

    def test_search_finds_publications_by_year(self):
        response = self.client.get(
            reverse("dashboard:global_search"),
            {"q": "2025"},
        )

        self.assertContains(response, "Machine learning for malaria diagnosis")
