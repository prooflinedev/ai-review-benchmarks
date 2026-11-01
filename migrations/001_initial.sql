CREATE TABLE deliveries (
    id INTEGER PRIMARY KEY,
    report TEXT NOT NULL,
    scheduled_at INTEGER NOT NULL,
    queue TEXT NOT NULL,
    legacy_format TEXT NOT NULL DEFAULT 'csv',
    delivered_at INTEGER
);

CREATE TABLE receipts (
    delivery_id INTEGER PRIMARY KEY REFERENCES deliveries(id),
    recorded_at INTEGER NOT NULL
);
