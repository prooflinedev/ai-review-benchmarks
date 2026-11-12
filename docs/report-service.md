# Scheduled reports

This internal application schedules named report deliveries. Operators use the Python console to enqueue jobs, run a worker for a named queue, browse history, and export records. It runs with Python 3.10+ and SQLite 3.35+. The console creates the database and applies pending migrations on startup. The receipt table represents successful delivery in this fixture.

```sh
python3 console.py schedule "Weekly orders" 1700000000
python3 console.py work --queue reports --now 1700000001
python3 console.py summary
python3 console.py history --limit 10
python3 console.py export
python3 console.py archive
```

Pass `--db PATH` before a command to choose a database. Scheduled times are Unix seconds. Schedulers can enqueue multiple reports for the same second. A worker invocation delivers all due jobs for its queue. History cursors are opaque integers and belong to their original query. The export command writes a CSV header followed by one record per delivery. Archive sends batches to a callback; the console prints one JSON array per request.
