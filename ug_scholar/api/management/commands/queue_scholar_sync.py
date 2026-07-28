from django.core.management.base import BaseCommand

from api.services.sync import queue_stale_sync


class Command(BaseCommand):
    help = "Queue profiles whose scholarly metadata is stale."

    def add_arguments(self, parser):
        parser.add_argument("--max-age-hours", type=int, default=168)

    def handle(self, *args, **options):
        run, created = queue_stale_sync(max_age_hours=options["max_age_hours"])
        if run is None:
            self.stdout.write("No stale profiles found.")
            return
        message = "Queued" if created else "Already queued"
        self.stdout.write(f"{message} sync run #{run.pk} for {run.total_profiles} profiles.")
