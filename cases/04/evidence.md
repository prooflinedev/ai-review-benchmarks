Deployment inventory from the report service simulator, recorded immediately before the proposed migration. Each entry lists every active worker revision, its replica count, and the prepared read it issues when polling the deliveries table. Each site has its own database. The migration runs online while the listed workers continue polling.

```json
{
  "observation": "inventory-204",
  "observed_at": "2026-10-21T09:00:00Z",
  "sites": {
    "elm": [
      {"revision": "workers-17", "replicas": 2, "poll_sql": "SELECT id, legacy_format FROM deliveries WHERE delivered_at IS NULL"},
      {"revision": "workers-18", "replicas": 3, "poll_sql": "SELECT id, report FROM deliveries WHERE delivered_at IS NULL"}
    ],
    "cedar": [
      {"revision": "workers-18", "replicas": 4, "poll_sql": "SELECT id, report FROM deliveries WHERE delivered_at IS NULL"}
    ]
  }
}
```
