"""Run one scheduled-report experiment against an isolated database."""

from contextlib import closing
import sqlite3

import reports


def handler(event, context):
    with closing(sqlite3.connect(":memory:")) as db:
        reports.migrate(db)
        job = reports.schedule(db, event["report"], event["scheduled_at"])
        delivered = reports.deliver_due(db, event["queue"], event["run_at"])
        receipt = db.execute(
            "SELECT recorded_at FROM receipts WHERE delivery_id = ?", (job,)
        ).fetchone()
        return {
            "commit": SOURCE_COMMIT,
            "request_id": context.aws_request_id,
            "report": reports.history(db, 1).rows[0][1],
            "delivered_this_run": delivered,
            "receipt_at": receipt[0] if receipt else None,
            "summary": reports.summary(db),
        }
