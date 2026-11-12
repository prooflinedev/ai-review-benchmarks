Effective archive receiver configuration from the report service simulator. These limits apply to each request at the recorded site. An oversized request is rejected in full. The scheduler submits its complete ready archive in one invocation at the cutover.

```json
{
  "observation": "archive-318",
  "observed_at": "2026-10-21T09:00:00Z",
  "sites": {
    "elm": {"receiver_revision": "archive-12", "max_rows_per_request": 100, "ready_rows": 70},
    "cedar": {"receiver_revision": "archive-11", "max_rows_per_request": 40, "ready_rows": 70}
  }
}
```
