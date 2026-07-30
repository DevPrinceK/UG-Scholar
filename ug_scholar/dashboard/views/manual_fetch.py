from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from api.models import Profile, SyncRun
from api.providers import ProviderError, get_provider
from api.services import queue_sync
from ug_scholar.library.decorators import AdministratorsOnly
from ug_scholar.library.utils_functions import log_user_action


PROVIDERS = (
    {
        "value": "openalex",
        "label": "OpenAlex",
        "description": "Open scholarly metadata and citation counts.",
    },
    {
        "value": "google_scholar",
        "label": "SerpAPI (Google Scholar)",
        "description": "Uses the configured paid SerpAPI key.",
    },
)


@method_decorator(AdministratorsOnly, name="dispatch")
class ManualFetchView(View):
    template_name = "pages/manual-fetch.html"

    def get(self, request):
        return render(request, self.template_name, self._context())

    def post(self, request):
        provider = (request.POST.get("provider") or "").strip().lower()
        allowed_providers = {option["value"] for option in PROVIDERS}
        if provider not in allowed_providers:
            messages.error(request, "Choose a supported publication provider.")
            return redirect("dashboard:manual_fetch")

        provider_label = next(
            option["label"]
            for option in PROVIDERS
            if option["value"] == provider
        )
        try:
            get_provider(provider)
        except ProviderError as exc:
            log_user_action(
                request.user,
                f"Could not queue {provider_label} publication fetch: {exc}",
            )
            messages.error(
                request,
                f"{provider_label} fetch could not be queued: {exc}.",
            )
            return redirect("dashboard:manual_fetch")

        raw_profile_id = (request.POST.get("profile_id") or "").strip()
        profile_ids = []
        target = "all authors"
        if raw_profile_id:
            try:
                profile = Profile.objects.get(pk=int(raw_profile_id))
            except (TypeError, ValueError, Profile.DoesNotExist):
                messages.error(request, "Choose a valid author profile.")
                return redirect("dashboard:manual_fetch")
            profile_ids = [profile.pk]
            target = profile.name or profile.scholar_id

        run, created = queue_sync(
            requested_by=request.user,
            profile_ids=profile_ids,
            provider_name=provider,
        )
        if created:
            log_user_action(
                request.user,
                f"Queued {provider_label} publication fetch #{run.pk} for {target}",
            )
            messages.success(
                request,
                f"{provider_label} fetch #{run.pk} queued for {target}.",
            )
        else:
            log_user_action(
                request.user,
                f"Reused existing publication fetch #{run.pk} for {target}",
            )
            messages.info(
                request,
                f"Fetch #{run.pk} for {target} is already "
                f"{run.get_status_display().lower()}.",
            )
        return redirect("dashboard:manual_fetch")

    @staticmethod
    def _context():
        return {
            "providers": PROVIDERS,
            "profiles": Profile.objects.only("id", "name", "scholar_id").order_by(
                "name", "scholar_id"
            ),
            "sync_runs": SyncRun.objects.select_related("requested_by")[:10],
        }


@method_decorator(AdministratorsOnly, name="dispatch")
class ManualFetchStatusView(View):
    """Return recent synchronization progress for live admin-page updates."""

    def get(self, request):
        runs = list(SyncRun.objects.all()[:10])
        return JsonResponse(
            {
                "active": any(
                    run.status
                    in {SyncRun.Status.PENDING, SyncRun.Status.RUNNING}
                    for run in runs
                ),
                "runs": [
                    {
                        "id": run.pk,
                        "status": run.status,
                        "status_label": run.get_status_display(),
                        "processed_profiles": run.processed_profiles,
                        "total_profiles": run.total_profiles,
                        "updated_publications": run.updated_publications,
                        "failed_profiles": run.failed_profiles,
                        "error": run.error[:500],
                    }
                    for run in runs
                ],
            }
        )
