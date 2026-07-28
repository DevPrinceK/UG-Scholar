from django.contrib.auth.models import AnonymousUser
from django.db import connection
from django.test import RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext

from api.models import Author, Profile, Publication
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
