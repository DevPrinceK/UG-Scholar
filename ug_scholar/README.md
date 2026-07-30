# UG Scholar

UG Scholar collects author profiles, publications, and citation metrics for the
University of Ghana. OpenAlex is the default metadata provider; SerpAPI remains
available as an optional fallback.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` in the project root and configure its values.
   Existing installations with `ug_scholar/.env` are also supported. Variables
   supplied directly by the hosting environment take priority over either file.
4. Create a free OpenAlex API key at
   <https://openalex.org/settings/api> and set `OPENALEX_API_KEY`.
5. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

## Metadata synchronization

Web and API refresh actions create a `SyncRun` instead of making hundreds of
external requests inside an HTTP request. During local development, `runserver`
automatically starts a lightweight queue worker and the Manual Fetch page polls
for live progress.

In production, run a worker as a separate process:

```powershell
python manage.py process_sync_queue --watch
```

Set `SCHOLAR_QUEUE_AUTOSTART=false` in production when using the separate
worker. It defaults to enabled only when Django debug mode is enabled.

Administrators can also open **Manual Fetch** in the sidebar, choose OpenAlex
or SerpAPI, and fetch all authors or one selected author. SerpAPI is always
selectable; if `SERPAPI_API_KEY` is missing, the submitted request returns a
clear administrator-facing configuration message without queueing a run.

For a scheduler or cron job, queue profiles older than one week and process one
run:

```powershell
python manage.py queue_scholar_sync --max-age-hours 168
python manage.py process_sync_queue
```

OpenAlex matching prefers a saved OpenAlex Author ID, then ORCID, then an exact
name match checked against known affiliations. Ambiguous profiles are skipped
with a visible synchronization error instead of silently importing another
researcher's publications.

To use SerpAPI temporarily:

```text
SCHOLAR_DATA_PROVIDER=serpapi
SERPAPI_API_KEY=...
```

No SerpAPI key is stored in source control.

## Thematic classification

The dashboard's Research Thematic Areas chart uses stored classifications
rather than demo values. New OpenAlex works use their primary topic, topic
hierarchy, and topic scores. If structured topics are unavailable, a
deterministic weighted heuristic uses the publication title, journal, and
low-weight author department/school/interests. Each publication stores its
classification confidence and matching evidence for review.

After deploying the thematic classification migration, classify existing
records once:

```powershell
python manage.py classify_publications --force
```

Run the same command after changing classification vocabulary. Publications
without enough evidence remain explicitly marked
`Multidisciplinary / Unclassified` instead of being forced into a misleading
category.

## Production notes

- Use PostgreSQL through `DATABASE_URL` when running background workers.
- Run only one queue worker with SQLite.
- Keep `DJANGO_SECRET_KEY` stable across deployments and all web workers.
  `DJANGO_SECRET_KEY_FALLBACKS` can hold previous keys during a controlled
  rotation.
- Set `DJANGO_SESSION_COOKIE_SECURE=true` and
  `DJANGO_CSRF_COOKIE_SECURE=true` when the public site uses HTTPS.
- Citation counts are provider-specific. The application stores the source on
  each publication and must not label OpenAlex counts as Google Scholar counts.
- Keep `DJANGO_DEBUG=false`, configure explicit hosts, and rotate any SerpAPI
  keys that appeared in earlier repository history.

## Verification

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```
