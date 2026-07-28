import time

from django.core.management.base import BaseCommand

from api.models import SyncRun
from api.services import process_sync_run


class Command(BaseCommand):
    help = "Process queued scholarly metadata synchronization runs."

    def add_arguments(self, parser):
        parser.add_argument("--run-id", type=int)
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Keep polling for new runs (suitable for a worker service).",
        )
        parser.add_argument("--poll-seconds", type=float, default=5.0)
        parser.add_argument("--max-runs", type=int, default=1)

    def handle(self, *args, **options):
        processed = 0
        while True:
            queryset = SyncRun.objects.filter(status=SyncRun.Status.PENDING)
            if options["run_id"]:
                queryset = queryset.filter(pk=options["run_id"])
            run = queryset.order_by("created_at").first()
            if run:
                self.stdout.write(
                    f"Processing sync run #{run.pk} with {run.provider}"
                )
                completed = process_sync_run(run)
                processed += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Run #{completed.pk}: {completed.status}; "
                        f"{completed.processed_profiles} profiles, "
                        f"{completed.updated_publications} publication records"
                    )
                )
                if processed >= options["max_runs"] and not options["watch"]:
                    break
                continue
            if not options["watch"]:
                self.stdout.write("No pending synchronization runs.")
                break
            time.sleep(max(options["poll_seconds"], 0.5))
