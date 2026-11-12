Queue subscription inventory from the report service simulator at the scheduled routing cutover. The inventory covers every consumer of reporting jobs at each site. Each worker subscription is an exact queue name. Existing subscriptions stay in place throughout the observation window.

```json
{
  "observation": "subscriptions-416",
  "observed_at": "2026-10-21T09:00:00Z",
  "window_end": "2026-10-21T09:30:00Z",
  "sites": {
    "elm": {"subscribed_queues": ["reports"], "new_jobs_due_in_window": 8},
    "cedar": {"subscribed_queues": ["reports", "report-dispatch"], "new_jobs_due_in_window": 8}
  }
}
```
