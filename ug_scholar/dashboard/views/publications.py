from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views import View

from api.models import Publication, SyncRun
from api.services import queue_sync
from ug_scholar.library.decorators import AdministratorsOnly


class PublicationsView(View):
    template_name = "pages/publications.html"

    def get(self, request):
        query = (request.GET.get("q") or "").strip()
        publications = Publication.objects.all()
        if query:
            publications = publications.filter(
                Q(title__icontains=query)
                | Q(authors__icontains=query)
                | Q(journal__icontains=query)
                | Q(doi__icontains=query)
            )
        page = Paginator(publications, 100).get_page(request.GET.get("page"))
        context = {
            "publications": page,
            "page_obj": page,
            "query": query,
            "latest_sync": SyncRun.objects.first(),
        }
        return render(request, self.template_name, context)


class RefreshPublicationsView(View):
    """Queue a refresh and immediately return control to the browser."""

    @AdministratorsOnly
    def post(self, request):
        run, created = queue_sync(requested_by=request.user)
        if created:
            messages.success(
                request,
                f"Refresh #{run.pk} queued. A background worker will process it.",
            )
        else:
            messages.info(
                request,
                f"Refresh #{run.pk} is already {run.get_status_display().lower()}.",
            )
        return redirect("dashboard:publications")
