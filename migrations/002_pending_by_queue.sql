CREATE INDEX deliveries_due_by_queue ON deliveries (queue, scheduled_at, id)
WHERE delivered_at IS NULL;
