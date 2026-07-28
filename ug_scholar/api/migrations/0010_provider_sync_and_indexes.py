from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def populate_provider_fields(apps, schema_editor):
    Profile = apps.get_model("api", "Profile")
    Publication = apps.get_model("api", "Publication")

    for profile in Profile.objects.all().iterator():
        profile.data_source = "google_scholar"
        profile.source_author_id = profile.scholar_id
        profile.interests = profile.interests or []
        profile.statistics = profile.statistics or {}
        stats = profile.statistics
        try:
            if isinstance(stats, list):
                profile.provider_citations = int(stats[0]["citations"]["all"])
                profile.h_index = int(stats[1]["h_index"]["all"])
                profile.i10_index = int(stats[2]["i10_index"]["all"])
            elif isinstance(stats, dict):
                profile.provider_citations = int(stats.get("citations", 0))
                profile.h_index = int(stats.get("h_index", 0))
                profile.i10_index = int(stats.get("i10_index", 0))
        except (IndexError, KeyError, TypeError, ValueError):
            pass
        profile.save(
            update_fields=[
                "data_source",
                "source_author_id",
                "interests",
                "statistics",
                "provider_citations",
                "h_index",
                "i10_index",
            ]
        )

    Publication.objects.filter(external_id__isnull=True).update(
        source="google_scholar", external_id=models.F("citation_id")
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("api", "0009_alter_profile_interests_alter_profile_statistics"),
    ]

    operations = [
        migrations.AddField(
            model_name="publication",
            name="doi",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="publication",
            name="external_id",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="publication",
            name="last_synced_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="publication",
            name="source",
            field=models.CharField(
                db_index=True, default="google_scholar", max_length=32
            ),
        ),
        migrations.AlterField(
            model_name="publication",
            name="authors",
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name="publication",
            name="citation_id",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AlterField(
            model_name="publication",
            name="citations",
            field=models.IntegerField(db_index=True, default=0),
        ),
        migrations.AlterField(
            model_name="publication",
            name="year",
            field=models.IntegerField(db_index=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="data_source",
            field=models.CharField(
                db_index=True, default="google_scholar", max_length=32
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="h_index",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="i10_index",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="last_synced_at",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="profile",
            name="orcid",
            field=models.CharField(
                blank=True, db_index=True, max_length=50, null=True
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="provider_citations",
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="profile",
            name="source_author_id",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="sync_error",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AlterField(
            model_name="profile",
            name="affiliation",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="thumbnail",
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="interests",
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="statistics",
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="college",
            field=models.CharField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="department",
            field=models.CharField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="school",
            field=models.CharField(
                blank=True, db_index=True, max_length=200, null=True
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="scholar_id",
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AlterField(
            model_name="author",
            name="profile",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="author",
                to="api.profile",
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="publications",
            field=models.ManyToManyField(
                related_name="author_entities", to="api.publication"
            ),
        ),
        migrations.CreateModel(
            name="SyncRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("running", "Running"),
                            ("succeeded", "Succeeded"),
                            ("partial", "Partially succeeded"),
                            ("failed", "Failed"),
                        ],
                        db_index=True,
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("provider", models.CharField(db_index=True, max_length=32)),
                ("profile_ids", models.JSONField(blank=True, default=list)),
                ("total_profiles", models.PositiveIntegerField(default=0)),
                ("processed_profiles", models.PositiveIntegerField(default=0)),
                ("updated_publications", models.PositiveIntegerField(default=0)),
                ("failed_profiles", models.PositiveIntegerField(default=0)),
                ("error", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("finished_at", models.DateTimeField(blank=True, null=True)),
                (
                    "requested_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="scholar_sync_runs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"db_table": "sync_run", "ordering": ["-created_at"]},
        ),
        migrations.RunPython(populate_provider_fields, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="profile",
            name="interests",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name="profile",
            name="statistics",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddConstraint(
            model_name="publication",
            constraint=models.UniqueConstraint(
                condition=Q(external_id__isnull=False),
                fields=("source", "external_id"),
                name="unique_publication_source_id",
            ),
        ),
        migrations.AddConstraint(
            model_name="profile",
            constraint=models.UniqueConstraint(
                condition=Q(source_author_id__isnull=False),
                fields=("data_source", "source_author_id"),
                name="unique_profile_source_author",
            ),
        ),
    ]
