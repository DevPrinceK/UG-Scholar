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

3. Copy `.env.example` to `.env` and expose the values to the application
   process. Django does not read `.env` files automatically.
4. Create a free OpenAlex API key at
   <https://openalex.org/settings/api> and set `OPENALEX_API_KEY`.
5. Apply migrations:

   ```powershell
   python manage.py migrate
   ```

## Metadata synchronization

Web and API refresh actions create a `SyncRun` instead of making hundreds of
external requests inside an HTTP request. Run a worker as a separate process:

```powershell
python manage.py process_sync_queue --watch
```

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

## Production notes

- Use PostgreSQL through `DATABASE_URL` when running background workers.
- Run only one queue worker with SQLite.
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
