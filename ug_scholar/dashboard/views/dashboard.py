import json
from datetime import datetime

from django.db.models import Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views import View

from api.models import Author, Profile, Publication


def _group_breakdown(field, limit=None):
    breakdown = Profile.objects.values(field).annotate(
        total_authors=Count("id", distinct=True),
        authors_with_publications=Count(
            "id",
            filter=Q(author__publications__isnull=False),
            distinct=True,
        ),
        total_publications=Count("author__publications"),
        total_citations=Coalesce(
            Sum("author__publications__citations"),
            Value(0),
            output_field=IntegerField(),
        ),
    ).order_by(field)
    if limit:
        breakdown = breakdown[:limit]
    rows = list(breakdown)
    metrics = {
        row[field]: row
        for row in Profile.objects.values(field).annotate(
            total_h_index=Coalesce(Sum("h_index"), Value(0)),
            total_i10_index=Coalesce(Sum("i10_index"), Value(0)),
        )
    }
    for row in rows:
        row.update(
            metrics.get(
                row[field],
                {"total_h_index": 0, "total_i10_index": 0},
            )
        )
    return rows


class IndexView(View):
    """Render the dashboard using bounded aggregate queries."""

    template_name = "pages/index.html"

    def get(self, request):
        total_authors = Author.objects.count()
        publishing_authors = (
            Author.objects.filter(publications__isnull=False).distinct().count()
        )
        publication_totals = Publication.objects.aggregate(
            total_publications=Count("id"),
            total_citations=Coalesce(Sum("citations"), Value(0)),
        )
        total_publications = publication_totals["total_publications"]
        total_citations = publication_totals["total_citations"]

        college_breakdown_info = _group_breakdown("college")
        college_publications = [
            {
                "college": row["college"],
                "total_publications": row["total_publications"],
            }
            for row in college_breakdown_info
        ]
        college_publication_total = (
            sum(row["total_publications"] for row in college_publications) or 1
        )
        for row in college_publications:
            row["percentages"] = (
                row["total_publications"] / college_publication_total
            ) * 100

        college_citations = [
            {"college": row["college"], "total_citations": row["total_citations"]}
            for row in college_breakdown_info
        ]
        college_citation_total = (
            sum(row["total_citations"] for row in college_citations) or 1
        )
        for row in college_citations:
            row["percentage"] = (
                row["total_citations"] / college_citation_total
            ) * 100

        school_publications = list(
            Profile.objects.values("school")
            .annotate(total_publications=Count("author__publications"))
            .order_by("-total_publications")[:3]
        )
        school_total = sum(
            row["total_publications"] for row in school_publications
        ) or 1
        for row in school_publications:
            row["percentage"] = row["total_publications"] / school_total * 100
        schools_pub_data = [
            {
                "school": row["school"],
                "total_publications": row["total_publications"],
            }
            for row in school_publications
        ]

        current_year = datetime.now().year
        last_three_years = list(range(current_year - 2, current_year + 1))
        last_ten_years = list(range(current_year - 9, current_year + 1))

        three_years_performance = (
            Publication.objects.filter(year__in=last_three_years)
            .values("year")
            .annotate(
                total_publications=Count("id"),
                total_citations=Coalesce(Sum("citations"), Value(0)),
            )
            .order_by("year")
        )
        performance_data = list(three_years_performance)

        ten_years_performance = (
            Publication.objects.filter(year__in=last_ten_years)
            .values("year")
            .annotate(
                total_publications=Count("id"),
                total_citations=Coalesce(Sum("citations"), Value(0)),
            )
            .order_by("year")
        )
        ten_years_performance_data = list(ten_years_performance)

        top_journals = (
            Publication.objects.exclude(journal__isnull=True)
            .exclude(journal="")
            .values("journal")
            .annotate(
                total_publications=Count("id"),
                total_citations=Coalesce(Sum("citations"), Value(0)),
            )
            .order_by("-total_publications")[:7]
        )
        journals_data = list(top_journals)

        top_10_authors = list(
            Author.objects.select_related("profile")
            .annotate(total_publications=Count("publications"))
            .order_by("-total_publications")[:10]
        )
        top_authors_by_citations = list(
            Author.objects.select_related("profile")
            .annotate(
                total_citations=Coalesce(
                    Sum("publications__citations"), Value(0)
                )
            )
            .order_by("-total_citations")[:10]
        )
        top_citation_total = (
            sum(author.total_citations for author in top_authors_by_citations) or 1
        )
        for author in top_authors_by_citations:
            author.percentage = author.total_citations / top_citation_total * 100

        top_10_publications = list(
            Publication.objects.prefetch_related("author_entities__profile")
            .order_by("-citations")[:10]
        )
        profile_metrics = Profile.objects.aggregate(
            total_hindex=Coalesce(Sum("h_index"), Value(0)),
            total_i10index=Coalesce(Sum("i10_index"), Value(0)),
        )
        department_breakdown_info = _group_breakdown("department", limit=10)

        context = {
            "total_authors": total_authors,
            "publishing_authors": publishing_authors,
            "total_publications": total_publications,
            "total_citations": total_citations,
            "total_hindex": profile_metrics["total_hindex"],
            "total_i10index": profile_metrics["total_i10index"],
            "college_publications": college_publications,
            "college_citations": college_citations,
            "performance_json": json.dumps(performance_data),
            "ten_years_performance_json": json.dumps(
                ten_years_performance_data
            ),
            "top_10_authors": top_10_authors,
            "top_10_publications": top_10_publications,
            "school_publications": school_publications,
            "college_breakdown_info": college_breakdown_info,
            "department_breakdown_info": department_breakdown_info,
            "top_authors_by_citations": top_authors_by_citations,
            "total_pubs_for_top_3_schools": sum(
                row["total_publications"] for row in school_publications
            ),
            "top_journals_json": json.dumps(journals_data),
            "schools_publications_json": json.dumps(schools_pub_data),
        }
        return render(request, self.template_name, context)
