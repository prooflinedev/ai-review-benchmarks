"""Report scheduling, delivery, and export for the operations console."""

import csv
from dataclasses import dataclass
from itertools import islice
from pathlib import Path


DELIVERY_QUEUE = "reports"
EXPORT_BATCH_SIZE = 25


def migrate(db):
    """Run numbered migrations on a new or existing database."""
    version = db.execute("PRAGMA user_version").fetchone()[0]
    for path in sorted(Path(__file__).with_name("migrations").glob("*.sql")):
        number = int(path.name.split("_", 1)[0])
        if number > version:
            with db:
                db.executescript(f"BEGIN;\n{path.read_text()}\nPRAGMA user_version = {number};\nCOMMIT;")


def schedule(db, report, scheduled_at):
    with db:
        row = db.execute(
            "INSERT INTO deliveries (report, scheduled_at, queue) VALUES (?, ?, ?)",
            (report, scheduled_at, DELIVERY_QUEUE),
        )
    return row.lastrowid


@dataclass(frozen=True)
class HistoryPage:
    rows: list
    next_cursor: int | None


def history(db, limit, cursor=None):
    """Return a page and the cursor for the next request."""
    if limit < 1:
        raise ValueError("page size must be positive")
    query = "SELECT id, report, scheduled_at FROM deliveries"
    params = []
    if cursor is not None:
        query += " WHERE id < ?"
        params.append(cursor)
    query += " ORDER BY id DESC LIMIT ?"
    rows = db.execute(query, (*params, limit + 1)).fetchall()
    next_cursor = rows[limit - 1][0] if len(rows) > limit else None
    return HistoryPage(rows[:limit], next_cursor)


def write_export(db, output):
    writer = csv.writer(output)
    writer.writerow(["id", "report", "scheduled_at"])
    rows = db.execute("SELECT id, report, scheduled_at FROM deliveries ORDER BY id").fetchall()
    for row in rows:
        writer.writerow(row)


def export_to_sink(db, send):
    """Send consecutive batches to the archive sink; each call is one request."""
    rows = iter(db.execute("SELECT id, report, scheduled_at FROM deliveries ORDER BY id"))
    while batch := list(islice(rows, EXPORT_BATCH_SIZE)):
        send(batch)


def deliver_due(db, queue, now):
    """Deliver the due jobs on one queue in a single transaction."""
    with db:
        jobs = db.execute(
            "SELECT id FROM deliveries WHERE queue = ? AND delivered_at IS NULL "
            "AND scheduled_at <= ? ORDER BY scheduled_at, id",
            (queue, now),
        ).fetchall()
        for (job_id,) in jobs:
            db.execute("INSERT INTO receipts VALUES (?, ?)", (job_id, now))
            db.execute("UPDATE deliveries SET delivered_at = ? WHERE id = ?", (now, job_id))
    return len(jobs)


def summary(db):
    sent, waiting = db.execute(
        "SELECT count(delivered_at), count(*) - count(delivered_at) FROM deliveries"
    ).fetchone()
    return {"delivered": sent, "pending": waiting, "total": sent + waiting}
