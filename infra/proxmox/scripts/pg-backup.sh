#!/usr/bin/env bash
# Nightly logical backup on the Data VM (cron 01:30, before the 02:30 PBS snapshot that carries it off-host).
# shortcut: nightly dump gives RPO 24 h; add WAL archiving (point-in-time recovery) before the first client's production data.
set -euo pipefail
DEST=${DEST:-/var/backups/postgresql}
KEEP_DAYS=${KEEP_DAYS:-7}
stamp=$(date -u +%Y%m%dT%H%M%SZ)
umask 077
mkdir -p "$DEST"

sudo -u postgres pg_dumpall --globals-only > "$DEST/globals-$stamp.sql.partial"
mv "$DEST/globals-$stamp.sql.partial" "$DEST/globals-$stamp.sql"

for db in $(sudo -u postgres psql -Atc "select datname from pg_database where not datistemplate and datname <> 'postgres'"); do
  sudo -u postgres pg_dump -Fc "$db" > "$DEST/$db-$stamp.dump.partial"
  mv "$DEST/$db-$stamp.dump.partial" "$DEST/$db-$stamp.dump"
done

# Only completed files are pruned; a failed run leaves .partial files for inspection.
find "$DEST" -type f \( -name '*.dump' -o -name '*.sql' \) -mtime +"$KEEP_DAYS" -delete
