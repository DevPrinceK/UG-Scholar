from urllib.parse import urlencode

from django.db.models import Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse
from django.views import View

from api.models import Profile, Publication


class GlobalSearchView(View):
    """Search publications, authors, and organizational units."""

    template_name = "pages/search-results.html"
    result_limit = 25

    def get(self, request):
        query = (request.GET.get("q") or "").strip()[:200]
        context = {
            "global_search_query": query,
            "authors": [],
            "publications": [],
            "organizations": [],
            "author_result_count": 0,
            "publication_result_count": 0,
            "total_result_count": 0,
        }
        if not query:
            return render(request, self.template_name, context)

        author_filter = (
            Q(name__icontains=query)
            | Q(scholar_id__icontains=query)
            | Q(email__icontains=query)
            | Q(affiliation__icontains=query)
            | Q(college__icontains=query)
            | Q(school__icontains=query)
            | Q(department__icontains=query)
            | Q(rank__icontains=query)
        )
        author_results = Profile.objects.filter(author_filter)
        context["author_result_count"] = author_results.count()
        context["authors"] = list(
            author_results.annotate(
                publication_count=Count(
                    "author__publications",
                    distinct=True,
                ),
                citation_count=Coalesce(
                    Sum("author__publications__citations"),
                    Value(0),
                    output_field=IntegerField(),
                ),
            )
            .order_by("name", "pk")[: self.result_limit]
        )

        publication_filter = (
            Q(title__icontains=query)
            | Q(authors__icontains=query)
            | Q(journal__icontains=query)
            | Q(doi__icontains=query)
            | Q(external_id__icontains=query)
            | Q(thematic_area__icontains=query)
        )
        if query.isdigit():
            publication_filter |= Q(year=int(query))
        publication_results = Publication.objects.filter(publication_filter)
        context["publication_result_count"] = publication_results.count()
        context["publications"] = list(
            publication_results.order_by("-citations", "-year", "title")[
                : self.result_limit
            ]
        )

        organizations = []
        organization_types = (
            (
                "College",
                "college",
                "dashboard:college_details",
                "college",
            ),
            (
                "Institute / Centre",
                "school",
                "dashboard:institution_details",
                "institution",
            ),
            (
                "Department",
                "department",
                "dashboard:department_details",
                "department",
            ),
        )
        for kind, field, route_name, parameter in organization_types:
            rows = (
                Profile.objects.exclude(**{f"{field}__isnull": True})
                .exclude(**{field: ""})
                .filter(**{f"{field}__icontains": query})
                .values(field)
                .annotate(
                    total_authors=Count("id", distinct=True),
                    total_publications=Count(
                        "author__publications",
                        distinct=True,
                    ),
                )
                .order_by(field)[:10]
            )
            for row in rows:
                name = row[field]
                organizations.append(
                    {
                        "kind": kind,
                        "name": name,
                        "total_authors": row["total_authors"],
                        "total_publications": row["total_publications"],
                        "url": (
                            f"{reverse(route_name)}?"
                            f"{urlencode({parameter: name})}"
                        ),
                    }
                )

        context["organizations"] = organizations
        context["total_result_count"] = (
            context["author_result_count"]
            + context["publication_result_count"]
            + len(organizations)
        )
        return render(request, self.template_name, context)
