from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api.models import Author, Profile, Publication, SyncRun
from api.services import process_sync_run, queue_sync, sync_profile
from api.services.thematic import (
    UNCLASSIFIED_AREA,
    classify_publication_metadata,
)
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

    def test_sync_persists_provider_topics_and_thematic_classification(self):
        article = {
            **FakeProvider().articles[0],
            "article_title": "Malaria epidemiology and disease prevalence",
            "provider_topics": [
                {
                    "name": "Malaria epidemiology",
                    "field": "Medicine",
                    "domain": "Health Sciences",
                    "score": 0.99,
                    "primary": True,
                }
            ],
        }
        sync_profile(self.profile, FakeProvider([article]))
        publication = Publication.objects.get()
        self.assertEqual(publication.thematic_area, "Health Sciences")
        self.assertGreater(publication.thematic_confidence, 0.5)
        self.assertEqual(
            publication.thematic_evidence["method"],
            "provider_topic_plus_metadata",
        )
        self.assertEqual(publication.provider_topics[0]["domain"], "Health Sciences")

    def test_duplicate_queue_request_reuses_pending_run(self):
        first, created = queue_sync(profile_ids=[self.profile.pk])
        second, second_created = queue_sync(profile_ids=[self.profile.pk])
        self.assertTrue(created)
        self.assertFalse(second_created)
        self.assertEqual(first.pk, second.pk)

    @patch("api.services.sync.get_provider")
    def test_pending_run_is_claimed_and_completed(self, get_provider):
        get_provider.return_value = FakeProvider()
        run, _ = queue_sync(profile_ids=[self.profile.pk])

        completed = process_sync_run(run)

        completed.refresh_from_db()
        self.assertEqual(completed.status, SyncRun.Status.SUCCEEDED)
        self.assertEqual(completed.processed_profiles, 1)
        self.assertEqual(completed.updated_publications, 2)
        self.assertIsNotNone(completed.started_at)
        self.assertIsNotNone(completed.finished_at)

    @patch("api.services.sync.get_provider")
    def test_already_claimed_run_is_not_processed_twice(self, get_provider):
        run, _ = queue_sync(profile_ids=[self.profile.pk])
        SyncRun.objects.filter(pk=run.pk).update(status=SyncRun.Status.RUNNING)

        result = process_sync_run(run)

        self.assertEqual(result.status, SyncRun.Status.RUNNING)
        get_provider.assert_not_called()

    @patch("api.services.sync.get_provider")
    def test_interrupted_run_resumes_after_completed_profiles(self, get_provider):
        provider = FakeProvider()
        provider.fetch_author = Mock(wraps=provider.fetch_author)
        get_provider.return_value = provider
        run, _ = queue_sync(profile_ids=[self.profile.pk])
        SyncRun.objects.filter(pk=run.pk).update(processed_profiles=1)
        run.refresh_from_db()

        completed = process_sync_run(run)

        completed.refresh_from_db()
        self.assertEqual(completed.status, SyncRun.Status.SUCCEEDED)
        self.assertEqual(completed.processed_profiles, 1)
        provider.fetch_author.assert_not_called()


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


class ThematicClassificationTests(TestCase):
    def test_business_title_is_classified_as_social_sciences(self):
        result = classify_publication_metadata(
            title="Capital structure and profitability of listed firms",
            journal="Journal of Finance",
        )
        self.assertEqual(result["area"], "Social Sciences")
        self.assertGreater(result["confidence"], 0)

    def test_author_department_is_a_low_weight_fallback(self):
        profile = Profile(
            scholar_id="law-author",
            department="School of Law",
            college="College of Humanities",
        )
        result = classify_publication_metadata(
            title="A comparative analysis",
            profiles=[profile],
        )
        self.assertEqual(result["area"], "Law")
        self.assertEqual(result["evidence"]["method"], "metadata_heuristic")

    def test_no_signal_remains_explicitly_unclassified(self):
        result = classify_publication_metadata(title="A comparative analysis")
        self.assertEqual(result["area"], UNCLASSIFIED_AREA)
        self.assertEqual(result["confidence"], 0)

    def test_specialized_finance_vocabulary_is_social_sciences(self):
        result = classify_publication_metadata(
            title="A GARCH-MIDAS approach to modelling stock returns",
        )
        self.assertEqual(result["area"], "Social Sciences")


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
