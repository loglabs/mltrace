# DB migrations

The following releases have DB migrations:

- v0.15 (Component staleness)

To run DB migrations:

1. Make sure your DB is running (via `docker-compose`)
2. Navigate to `mltrace/db/migrations` in your shell
3. Edit the url in `alembic.ini` to reflect your database url
4. Run `alembic upgrade head`
