"""Run the report service with Python 3.10 or later."""

import argparse
import json
import sqlite3
import sys
from contextlib import closing
from dataclasses import asdict

import reports


def main():
    parser = argparse.ArgumentParser(description="Schedule reports and inspect deliveries.")
    parser.add_argument("--db", default="reports.sqlite")
    commands = parser.add_subparsers(required=True, dest="command")
    schedule = commands.add_parser("schedule")
    schedule.add_argument("name")
    schedule.add_argument("at", type=int, help="Unix time in seconds")
    work = commands.add_parser("work")
    work.add_argument("--queue", required=True)
    work.add_argument("--now", type=int, required=True)
    history = commands.add_parser("history")
    history.add_argument("--limit", type=int, default=20)
    history.add_argument("--cursor", type=int)
    commands.add_parser("export")
    commands.add_parser("summary")
    commands.add_parser("archive")
    args = parser.parse_args()
    with closing(sqlite3.connect(args.db)) as db:
        reports.migrate(db)
        if args.command == "schedule":
            print(reports.schedule(db, args.name, args.at))
        elif args.command == "work":
            print(reports.deliver_due(db, args.queue, args.now))
        elif args.command == "history":
            print(json.dumps(asdict(reports.history(db, args.limit, args.cursor))))
        elif args.command == "export":
            reports.write_export(db, sys.stdout)
        elif args.command == "summary":
            print(json.dumps(reports.summary(db)))
        elif args.command == "archive":
            reports.export_to_sink(db, lambda batch: print(json.dumps(batch)))


if __name__ == "__main__":
    main()
