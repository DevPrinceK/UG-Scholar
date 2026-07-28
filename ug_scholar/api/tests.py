from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api.models import Author, Profile, Publication, SyncRun
from api.services import queue_sync, sync_profile
from ug_scholar.library.utils_functions import get_author_ids


class FakeProvider:
    name = "openalex"

    def __init__(self, articles=None):
        self.articles = articles or [
            {
                "source": "openalex",
                "external_id": "W1",
                "doi": "10.1000/one",
                "article_title": "First paper",
                "article_link": "https://doi.org/10.1000/one",
                "article_year": 2024,
                "article_citation_id": "W1",
                "article_authors": "Ada Author",
                "article_publication": "Journal One",
                "article_cited_by_value": 4,
            },
            {
                "source": "openalex",
                "external_id": "W2",
                "article_title": "Second paper",
                "article_year": 2025,
                "article_citation_id": "W2",
                "article_authors": "Ada Author",
                "article_publication": "Journal Two",
                "article_cited_by_value": 2,
            },
        ]

    def fetch_author(self, profile):
        return {
            "author_data": {
                "name": "Ada Author",
                "affiliations": "University of Ghana",
                "interests": [{"title": "Testing"}],
                "cited_by_table": {
                    "citations": 6,
                    "h_index": 2,
                    "i10_index": 1,
                },
                "citations": 6,
                "h_index": 2,
                "i10_index": 1,
                "source_author_id": "A1",
            },
            "author_articles": self.articles,
        }


class SyncServiceTests(TestCase):
    def setUp(self):
        self.profile = Profile.objects.create(
            scholar_id="scholar-1", name="Ada Author"
        )
        Author.objects.create(profile=self.profile)

    def test_sync_is_idempotent_and_replaces_stale_links(self):
        first = sync_profile(self.profile, FakeProvider())
        self.assertEqual(first["publications"], 2)
        self.assertEqual(Publication.objects.count(), 2)
        self.assertEqual(self.profile.author.publications.count(), 2)

        self.profile.refresh_from_db()
        second_article = FakeProvider().articles[:1]
        second_article[0]["article_cited_by_value"] = 9
        sync_profile(self.profile, FakeProvider(second_article))

        self.assertEqual(Publication.objects.count(), 1)
        self.assertEqual(self.profile.author.publications.count(), 1)
        self.assertEqual(
            Publication.objects.get(external_id="W1").citations, 9
        )
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.data_source, "openalex")
        self.assertEqual(self.profile.h_index, 2)

    def test_duplicate_queue_request_reuses_pending_run(self):
        first, created = queue_sync(profile_ids=[self.profile.pk])
        second, second_created = queue_sync(profile_ids=[self.profile.pk])
        self.assertTrue(created)
        self.assertFalse(second_created)
        self.assertEqual(first.pk, second.pk)


class ApiPermissionTests(TestCase):
    def test_sync_endpoint_requires_staff(self):
        response = APIClient().post("/api/populate-db/", {}, format="json")
        self.assertIn(response.status_code, (401, 403))
        self.assertEqual(SyncRun.objects.count(), 0)

    @override_settings(SCHOLAR_DATA_PROVIDER="openalex")
    def test_staff_can_queue_sync(self):
        user = get_user_model().objects.create_user(
            email="admin@example.com", password="password", is_staff=True
        )
        client = APIClient()
        client.force_authenticate(user)
        response = client.post("/api/populate-db/", {}, format="json")
        self.assertEqual(response.status_code, 202)
        self.assertEqual(SyncRun.objects.count(), 1)


class CsvImportTests(TestCase):
    def test_utf8_csv_and_raw_scholar_id_are_supported(self):
        upload = SimpleUploadedFile(
            "authors.csv",
            (
                "scholar,name,email,college,school,department,rank\n"
                "abc-123,José Author,jose@example.com,College,School,Department,Lecturer\n"
            ).encode("utf-8"),
        )
        rows = get_author_ids(upload)
        self.assertEqual(rows[0]["author_id"], "abc-123")
        self.assertEqual(rows[0]["name"], "José Author")
