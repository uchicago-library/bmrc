#!/bin/bash
set -e

PG_VERSION=14
PG_DATA="/var/lib/postgresql/${PG_VERSION}/main"
INIT_MARKER="/var/lib/postgresql/.bmrc_initialized"

# On a fresh named volume there's no cluster yet; create one.
if [ ! -f "${PG_DATA}/PG_VERSION" ]; then
    echo "Initializing PostgreSQL cluster..."
    chown -R postgres:postgres /var/lib/postgresql
    pg_dropcluster --stop "${PG_VERSION}" main 2>/dev/null || true
    pg_createcluster "${PG_VERSION}" main
    # Re-apply trust auth (the new cluster ships with default pg_hba.conf)
    sed -i 's/^local\s\+all\s\+all\s\+peer/local all all trust/' "/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
    sed -i 's/^host\s\+all\s\+all\s\+127.0.0.1\/32\s\+scram-sha-256/host all all 127.0.0.1\/32 trust/' "/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
    sed -i 's/^host\s\+all\s\+all\s\+::1\/128\s\+scram-sha-256/host all all ::1\/128 trust/' "/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
fi

echo "Starting PostgreSQL..."
service postgresql start

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h localhost -U postgres >/dev/null 2>&1; do
    sleep 1
done

# Ensure the bmrc role and bmrc_dev database exist
if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_roles WHERE rolname='bmrc'\"" | grep -q 1; then
    echo "Creating bmrc PostgreSQL role..."
    su - postgres -c "createuser -s bmrc"
fi
if ! su - postgres -c "psql -tAc \"SELECT 1 FROM pg_database WHERE datname='bmrc_dev'\"" | grep -q 1; then
    echo "Creating bmrc_dev database..."
    su - postgres -c "createdb -O bmrc bmrc_dev"
fi

# First-boot setup: migrate and load the dev fixtures. Subsequent boots skip
# this so manual edits to the dev DB aren't clobbered.
if [ ! -f "${INIT_MARKER}" ]; then
    echo "Running Django migrations and loading dev fixtures..."
    cd /app
    python manage.py migrate --noinput
    python manage.py loaddata /app/home/fixtures/dev.json
    touch "${INIT_MARKER}"
fi

exec "$@"
