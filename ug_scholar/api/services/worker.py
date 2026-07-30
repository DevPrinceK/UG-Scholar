import logging
import os
import sys
import threading
from pathlib import Path

from django.conf import settings
from django.db import close_old_connections
from django.db.utils import OperationalError, ProgrammingError

from api.models import SyncRun
from api.services.sync import process_sync_run


logger = logging.getLogger(__name__)
_worker_lock = threading.Lock()
_worker_thread = None


def _manage_py_command():
    if Path(sys.argv[0]).name.lower() != "manage.py":
        return ""
    return sys.argv[1] if len(sys.argv) > 1 else ""


def should_autostart_queue_worker():
    """Return whether this process should host the lightweight queue worker."""

    if not settings.SCHOLAR_QUEUE_AUTOSTART:
        return False

    # Management commands should not unexpectedly process paid API work. The
    # exception is the development server, where an embedded worker makes the
    # queue usable without requiring a second terminal.
    command = _manage_py_command()
    if command:
        if command != "runserver":
            return False
        if "--noreload" not in sys.argv:
            # The autoreloader parent survives code changes; its child does
            # not. Hosting the worker in the parent prevents interrupted runs
            # whenever a Python file is saved during development.
            return os.environ.get("RUN_MAIN") != "true"
    return True


def process_next_queued_run():
    """Process the oldest pending run, returning it when one was found."""

    run = (
        SyncRun.objects.filter(status=SyncRun.Status.PENDING)
        .order_by("created_at", "pk")
        .first()
    )
    if not run:
        return None
    return process_sync_run(run)


def _queue_worker_loop():
    poll_seconds = max(settings.SCHOLAR_QUEUE_POLL_SECONDS, 0.5)
    while True:
        try:
            close_old_connections()
            run = process_next_queued_run()
            if run is not None:
                continue
        except Exception:
            logger.exception("The embedded scholar queue worker failed an iteration.")
        finally:
            close_old_connections()
        threading.Event().wait(poll_seconds)


def start_queue_worker():
    """Start one daemon queue-consumer thread in this application process."""

    global _worker_thread
    if not should_autostart_queue_worker():
        return None
    with _worker_lock:
        if _worker_thread is not None and _worker_thread.is_alive():
            return _worker_thread
        if _manage_py_command() == "runserver":
            # No embedded worker from an earlier runserver process can still
            # be alive here. Reset interrupted work so idempotent sync can
            # resume cleanly after Ctrl+C, a crash, or a machine restart.
            try:
                SyncRun.objects.filter(status=SyncRun.Status.RUNNING).update(
                    status=SyncRun.Status.PENDING,
                    started_at=None,
                    finished_at=None,
                )
            except (OperationalError, ProgrammingError):
                # The first development startup may occur before migrations.
                logger.debug("Sync table is not ready for interrupted-run recovery.")
        _worker_thread = threading.Thread(
            target=_queue_worker_loop,
            name="scholar-sync-worker",
            daemon=True,
        )
        _worker_thread.start()
        logger.info("Started embedded scholar queue worker.")
        return _worker_thread
