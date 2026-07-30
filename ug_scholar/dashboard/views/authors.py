import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, IntegerField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from django.views import View

from api.models import Author, Profile
from api.services import queue_sync
from dashboard.forms import AuthorProfileForm
from ug_scholar.library.constants import UG, SampleAuthorData
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import get_author_ids, log_user_action


class AuthorsView(View):
    template_name = "pages/authors.html"

    def get(self, request):
        ug = UG()
        query = (request.GET.get("q") or "").strip()
        authors = Profile.objects.select_related("author").annotate(
            publication_count=Count("author__publications", distinct=True),
            citation_count=Coalesce(
                Sum("author__publications__citations"),
                Value(0),
                output_field=IntegerField(),
            ),
        )
        if query:
            authors = authors.filter(
                Q(name__icontains=query)
                | Q(scholar_id__icontains=query)
                | Q(department__icontains=query)
                | Q(school__icontains=query)
            )
        authors = authors.order_by("name", "pk")
        page = Paginator(authors, 100).get_page(request.GET.get("page"))
        context = {
            "authors": page,
            "page_obj": page,
            "query": query,
            "colleges": ug.get_colleges(),
            "schools": ug.get_schools(),
            "departments": ug.get_departments(),
            "ranks": ug.get_ranks(),
        }
        return render(request, self.template_name, context)


class CreateUpdateAuthorView(View):
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        log_user_action(request.user, "Tried to access author form using get request")
        return redirect("dashboard:authors")

    @method_decorator(AdministratorsOnly)
    def post(self, request):
        user = request.user
        scholar_id = (request.POST.get("scholar_id") or "").strip()
        if Profile.objects.filter(scholar_id=scholar_id).exists():
            log_user_action(
                user, "Tried to create author profile with an existing scholar id"
            )
            messages.info(request, "Author Profile Already Exists")
            return redirect("dashboard:authors")

        form = AuthorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save()
            Author.objects.get_or_create(profile=profile)
            run, _ = queue_sync(requested_by=user, profile_ids=[profile.pk])
            log_user_action(user, f"Created author profile: {profile}")
            messages.success(
                request,
                f"Author created. Metadata refresh #{run.pk} has been queued.",
            )
            return redirect("dashboard:authors")

        for field, error in form.errors.items():
            message = f"{field.title()}: {strip_tags(error)}"
            log_user_action(user, f"Author form error: {message}")
            messages.info(request, message)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", "/authors/"))


class BulkUploadAuthorView(View):
    @method_decorator(AdministratorsOnly)
    def get(self, request):
        log_user_action(
            request.user, "Tried to access bulk upload author form using get request"
        )
        return redirect("dashboard:authors")

    @method_decorator(AdministratorsOnly)
    def post(self, request):
        authors_only = request.POST.get("authors_only") == "on"
        csv_file = request.FILES.get("csv_file")
        if not csv_file:
            messages.info(request, "Please choose a CSV file.")
            return redirect("dashboard:authors")
        try:
            infos = get_author_ids(csv_file)
        except Exception as exc:
            messages.info(request, f"Could not read CSV: {exc}")
            return redirect("dashboard:authors")

        profile_ids = []
        for info in infos:
            defaults = {
                key: info.get(key) or None
                for key in ("name", "rank", "email", "college", "school", "department")
            }
            profile, _ = Profile.objects.update_or_create(
                scholar_id=info["author_id"], defaults=defaults
            )
            Author.objects.get_or_create(profile=profile)
            profile_ids.append(profile.pk)

        if not authors_only and profile_ids:
            run, _ = queue_sync(requested_by=request.user, profile_ids=profile_ids)
            messages.success(
                request,
                f"Imported {len(profile_ids)} authors; refresh #{run.pk} queued.",
            )
        else:
            messages.success(request, f"Imported {len(profile_ids)} authors.")
        log_user_action(request.user, "Imported authors from CSV")
        return redirect("dashboard:authors")


class DownloadSampleBulkFileView(View):
    def get(self, request):
        sample_data = SampleAuthorData().get_author_sample_data()
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            'attachment; filename="bulk_author_upload_sample.csv"'
        )
        response.write("\ufeff")
        writer = csv.writer(response)
        writer.writerow(
            ["scholar", "name", "email", "college", "school", "department", "rank"]
        )
        for data in sample_data:
            writer.writerow(
                [
                    data["scholar"],
                    data.get("name", ""),
                    data["email"],
                    data["college"],
                    data["school"],
                    data["department"],
                    data["rank"],
                ]
            )
        return response
