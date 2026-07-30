from collections import Counter

from django.core.management.base import BaseCommand

from api.models import Publication
from api.services.thematic import (
    UNCLASSIFIED_AREA,
    classify_publication_metadata,
)


class Command(BaseCommand):
    help = (
        "Classify publications into dashboard thematic areas using provider "
        "topics and weighted local metadata."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Reclassify publications that already have a thematic area.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of publication records to update per database batch.",
        )

    def handle(self, *args, **options):
        batch_size = max(1, options["batch_size"])
        publications = Publication.objects.prefetch_related(
            "author_entities__profile"
        ).order_by("pk")
        if not options["force"]:
            publications = publications.filter(thematic_area=UNCLASSIFIED_AREA)

        pending = []
        counts = Counter()
        processed = 0
        for publication in publications.iterator(chunk_size=batch_size):
            profiles = [
                author.profile for author in publication.author_entities.all()
            ]
            classification = classify_publication_metadata(
                title=publication.title,
                journal=publication.journal,
                provider_topics=publication.provider_topics,
                profiles=profiles,
            )
            publication.thematic_area = classification["area"]
            publication.thematic_confidence = classification["confidence"]
            publication.thematic_evidence = classification["evidence"]
            pending.append(publication)
            counts[classification["area"]] += 1
            processed += 1

            if len(pending) >= batch_size:
                self._save_batch(pending)
                pending = []

        if pending:
            self._save_batch(pending)

        self.stdout.write(
            self.style.SUCCESS(f"Classified {processed} publications.")
        )
        for area, count in counts.most_common():
            self.stdout.write(f"  {area}: {count}")

    @staticmethod
    def _save_batch(publications):
        Publication.objects.bulk_update(
            publications,
            [
                "thematic_area",
                "thematic_confidence",
                "thematic_evidence",
            ],
        )
