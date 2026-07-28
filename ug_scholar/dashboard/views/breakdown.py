import json

from django.db.models import Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views import View

from api.models import Profile


def _annotated_profiles(queryset):
    return queryset.annotate(
        publication_count=Count("author__publications", distinct=True),
        citation_count=Coalesce(
            Sum("author__publications__citations"),
            Value(0),
            output_field=IntegerField(),
        ),
    )


def _summary(queryset):
    profile_metrics = queryset.aggregate(
        total_authors=Count("id"),
        total_h_index=Coalesce(Sum("h_index"), Value(0)),
        total_i10_index=Coalesce(Sum("i10_index"), Value(0)),
    )
    publication_metrics = queryset.aggregate(
        publishing_authors=Count(
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
    )
    return {**profile_metrics, **publication_metrics}


def _breakdown(queryset, field):
    rows = list(
        queryset.values(field)
        .annotate(
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
        )
        .order_by(field)
    )
    metrics = {
        row[field]: row
        for row in queryset.values(field).annotate(
            total_h_index=Coalesce(Sum("h_index"), Value(0)),
            total_i10_index=Coalesce(Sum("i10_index"), Value(0)),
        )
    }
    for row in rows:
        row.update(
            metrics.get(
                row[field], {"total_h_index": 0, "total_i10_index": 0}
            )
        )
        row["abbr"] = "".join(
            word[0] for word in (row[field] or "").split() if word
        ).upper()
    return rows


class CollegesView(View):
    template_name = "pages/colleges.html"

    def get(self, request):
        rows = _breakdown(Profile.objects.all(), "college")
        return render(
            request,
            self.template_name,
            {
                "college_breakdown_info": rows,
                "college_breakdown_json": json.dumps(rows),
            },
        )


class CollegeDetailsView(View):
    template_name = "pages/college-details.html"

    def get(self, request):
        college_name = (request.GET.get("college") or "").strip()
        base = Profile.objects.filter(college=college_name)
        stats = _summary(base)
        authors = _annotated_profiles(base)
        filtered_departments = _breakdown(base, "department")
        college_indexes = [
            {"name": "H-INDEX", "index": stats["total_h_index"]},
            {"name": "I-INDEX", "index": stats["total_i10_index"]},
        ]
        college_auth_pub = [
            {"name": "Total Authors", "index": stats["total_authors"]},
            {
                "name": "Total Publications",
                "index": stats["total_publications"],
            },
        ]
        return render(
            request,
            self.template_name,
            {
                "college_name": college_name,
                "authors": authors,
                "college_indexes_json": json.dumps(college_indexes),
                "college_auth_pub_json": json.dumps(college_auth_pub),
                "college_h_index": stats["total_h_index"],
                "college_i_index": stats["total_i10_index"],
                "college_total_authors": stats["total_authors"],
                "college_total_publications": stats["total_publications"],
                "college_total_citations": stats["total_citations"],
                "college_publishing_authors": stats["publishing_authors"],
                "filtered_departments": filtered_departments,
            },
        )


class DepartmentDetailsView(View):
    template_name = "pages/department-details.html"

    def get(self, request):
        department_name = (request.GET.get("department") or "").strip()
        query = (request.GET.get("author-query") or "").strip()
        base = Profile.objects.filter(department=department_name)
        stats = _summary(base)
        annotated = _annotated_profiles(base)
        top_department_authors = annotated.order_by("-publication_count")[:5]
        matching_authors = annotated.filter(name__icontains=query) if query else []
        indexes = [
            {"name": "H-INDEX", "index": stats["total_h_index"]},
            {"name": "I-INDEX", "index": stats["total_i10_index"]},
        ]
        author_publication_stats = [
            {"name": "Total Authors", "index": stats["total_authors"]},
            {
                "name": "Total Publications",
                "index": stats["total_publications"],
            },
        ]
        return render(
            request,
            self.template_name,
            {
                "department_name": department_name,
                "authors": matching_authors,
                "department_indexes_json": json.dumps(indexes),
                "department_auth_pub_json": json.dumps(
                    author_publication_stats
                ),
                "department_h_index": stats["total_h_index"],
                "department_i_index": stats["total_i10_index"],
                "department_total_authors": stats["total_authors"],
                "department_total_publications": stats["total_publications"],
                "department_total_citations": stats["total_citations"],
                "department_publishing_authors": stats["publishing_authors"],
                "top_department_authors": top_department_authors,
            },
        )


class FacultiesView(View):
    template_name = "pages/faculties.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"school_breakdown_info": _breakdown(Profile.objects.all(), "school")},
        )


class FacultyDetailsView(View):
    template_name = "pages/faculty-details.html"

    def get(self, request):
        institution_name = (request.GET.get("institution") or "").strip()
        query = (request.GET.get("author-query") or "").strip()
        base = Profile.objects.filter(school=institution_name)
        stats = _summary(base)
        annotated = _annotated_profiles(base)
        matching_authors = annotated.filter(name__icontains=query) if query else []
        indexes = [
            {"name": "H-INDEX", "index": stats["total_h_index"]},
            {"name": "I-INDEX", "index": stats["total_i10_index"]},
        ]
        author_publication_stats = [
            {"name": "Total Authors", "index": stats["total_authors"]},
            {
                "name": "Total Publications",
                "index": stats["total_publications"],
            },
        ]
        return render(
            request,
            self.template_name,
            {
                "institution_name": institution_name,
                "authors": matching_authors,
                "institution_indexes_json": json.dumps(indexes),
                "institution_auth_pub_json": json.dumps(
                    author_publication_stats
                ),
                "institution_h_index": stats["total_h_index"],
                "institution_i_index": stats["total_i10_index"],
                "institution_total_authors": stats["total_authors"],
                "institution_total_publications": stats["total_publications"],
                "institution_total_citations": stats["total_citations"],
                "institution_publishing_authors": stats["publishing_authors"],
                "filtered_departments": _breakdown(base, "department"),
            },
        )


class DepartmentsView(View):
    template_name = "pages/departments.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {
                "department_breakdown_info": _breakdown(
                    Profile.objects.all(), "department"
                )
            },
        )


class DepartmentsInCollegeView(View):
    template_name = "pages/departments_in_college.html"

    def get(self, request, college):
        return render(
            request,
            self.template_name,
            {
                "college": college,
                "department_breakdown_info": _breakdown(
                    Profile.objects.filter(college=college), "department"
                ),
            },
        )
