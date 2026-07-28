from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services import queue_sync


class OverviewAPI(APIView):
    """Give the overview of the UG Scholar API."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "message": "Welcome to the UG Scholar API",
                "status": status.HTTP_200_OK,
            }
        )


class QueueDatabaseSyncAPIView(APIView):
    """Queue a provider synchronization without blocking the HTTP request."""

    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        profile_ids = request.data.get("profile_ids") or []
        run, created = queue_sync(
            requested_by=request.user,
            profile_ids=profile_ids,
            provider_name=request.data.get("provider"),
        )
        return Response(
            {
                "message": "Synchronization queued" if created else "Synchronization already queued",
                "run_id": run.pk,
                "status": run.status,
            },
            status=status.HTTP_202_ACCEPTED,
        )


# Backward-compatible class names for existing imports and routes.
UpdatedDBAPIView = QueueDatabaseSyncAPIView
PopulateDBAPIView = QueueDatabaseSyncAPIView
