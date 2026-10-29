# Docker Compose deployment

## Deploy Squest app

The docker-compose based deployment is a good way to easily and quickly test Squest. This way of deploying is also stable enough to be used in production.

To run the Squest application, execute the `docker-compose.yml` file:
```bash
docker-compose up
```

Then connect with your web browser to [http://127.0.0.1:8080](http://127.0.0.1:8080)
The default admin account is `admin // admin`

The default export the port 8080. If you want to use the standard HTTP port 80, update the 
file `docker-compose.override.yml`.
```yaml
services:
  nginx:
    ports:
      - "80:8080"
```

## Infrastructure image updates

Compose pins infrastructure images to explicit releases: MariaDB 11.8 LTS,
RabbitMQ 4.4 (management), Redis 8.10, Nginx 1.30 stable, PostgreSQL 18, and
Caddy 2.11. phpMyAdmin remains on 5.2.3. The Squest image is selected separately
with `SQUEST_IMAGE` and `SQUEST_TAG`.

`docker/rabbitmq.conf` permits transient non-exclusive queues for compatibility
with the pinned Celery 5.5/Kombu client. RabbitMQ 4.3+ denies these queues by
default. Keep this configuration mounted when deploying the new broker; remove
the compatibility setting only after upgrading and verifying the client's
control/reply queue behavior. Django's HTTP readiness check gates Celery and
Nginx startup so migrations and initial data finish before they start.
The application image uses Python 3.12 on Debian Bookworm. Startup stops on a
failed migration or initialization command instead of serving a partial schema.
Build and deploy the updated Squest image as well, so it includes the backend
configuration and migration compatibility fixes:

```bash
docker build -t squest:compose-update -f docker/squest.Dockerfile .
SQUEST_IMAGE=squest SQUEST_TAG=compose-update docker compose up -d
```

For PostgreSQL, use Docker Compose 2.24.4 or newer:

```bash
docker compose -f docker-compose.yml -f psql.docker-compose.yaml -f docker-compose.override.yml up -d
```

The override selects PostgreSQL as the default backend (`DB_ENGINE`) for Django
and Celery, including transactions and third-party schedulers, initializes
the application database, and uses a PostgreSQL healthcheck. `DB_DATABASE`,
`DB_USER`, and `DB_PASSWORD` can be set in the shell or Compose `.env` file to
configure both initialization and the application. The administrator password
is configured through `POSTGRES_PASSWORD` in `docker/environment_variables/db.env`.
PostgreSQL uses a separate `psql_data` volume mounted at `/var/lib/postgresql`,
as required by the PostgreSQL 18 image layout. Initialization scripts run only
on an empty database volume.

Fresh installations use replacement migrations for four historical
`service_catalog` migrations:

- `0014_postgresql_compatible` and `0044_postgresql_compatible` check foreign keys
  immediately within their transactions to avoid pending-trigger errors between
  data changes and DDL.
- `0023_portable_state_conversion` and `0024_portable_hook_conversion` use
  historical ORM models to convert legacy states, replacing MySQL-specific SQL
  string quoting. The hook split retains its original behavior for valid legacy
  hooks.

The replacements set a transaction-local 2-second lock timeout on PostgreSQL.
Existing installations that already applied the original migrations do not
rerun their operations. Keep the original migration files: the replacements
reuse their historical schema definitions. These are compatibility fixes,
not zero-downtime rewrites: the original table locks and schema changes still
require a planned upgrade window when updating an installation from before
those migrations.

### Existing deployments

Back up persistent data before changing database or broker versions. Successful
startup on a fresh volume does not validate an upgrade of existing data.

- **MariaDB 11.0 → 11.8:** follow the
  [MariaDB upgrade documentation](https://mariadb.com/docs/server/server-management/install-and-upgrade-mariadb/upgrading).
  Use a supported intermediate upgrade path or a logical dump/restore into a
  fresh volume. When following an in-place upgrade procedure, run the required
  system-table upgrade (`mariadb-upgrade`, or the image's `MARIADB_AUTO_UPGRADE`
  option) and verify the result before starting Squest.
- **RabbitMQ 3.13 → 4.4:** follow the
  [supported upgrade paths](https://www.rabbitmq.com/docs/upgrade).
  Enable the required feature flags and upgrade through the supported release
  series; do not attach the existing 3.13 data volume directly to 4.4. An
  alternative is a new broker with exported/imported definitions and a planned
  drain or transfer of queued messages (definitions do not include messages).
- **PostgreSQL:** the previous `latest` tag did not identify the installed major
  version. Check the running server's version before upgrading. For a major
  upgrade, use PostgreSQL's documented `pg_upgrade` or dump/restore procedure.
  Existing `db_data` volumes mounted at `/var/lib/postgresql/data` are not
  migrated automatically into the new `psql_data` volume.
- **Redis:** this Compose service is a password-protected, disposable cache
  without a persistent volume; expect a cold cache after replacement.

## TLS

This section explains how to add TLS support on Squest when using docker-compose based deployment.

The TLS endpoint is managed by a reverse proxy on top of the default web server.
This is not the only way to handle this part. Many tools like Nginx, Apache or Traefik could be used, and you are free 
to use the one you want instead of this proposed configuration.
The only recommendation we have is to keep the default nginx web server as main http entrypoint.

### Using Caddy

[Caddy](https://caddyserver.com/) is a powerful webserver written in Go which provide a 
[reverse proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#reverse-proxy) feature.

In the example below, we'll use self-signed certificate. Follow the [official documentation](https://caddyserver.com/docs/automatic-https) 
if you want to configure it to use an ACME like "Let's Encrypt" instead.

Place your certificate and key file in the folder `docker/certs`.

E.g:
```
docker
├── Caddyfile
├── certs
│    ├── squest.crt
│    └── squest.key
```

Update the `docker/Caddyfile` with the FQDN of your server. By default, the FQDN is set to `squest.domain.local`
```
squest.domain.local {   # This line should match the ALLOWED_HOSTS in your Squest environment
    reverse_proxy nginx:8080
    encode gzip zstd
    tls /etc/ssl/private/squest.crt /etc/ssl/private/squest.key
    # or:
    # tls /etc/ssl/private/cert.pem

    log {
      level error
    }
}
```

Update the `ALLOWED_HOSTS` environment variable from the configuration file `docker/environment_variables/squest.env` 
to match your FQDN.
```bash
ALLOWED_HOSTS=squest.domain.local
```

Start docker compose with the TLS configuration:
```bash
docker-compose -f docker-compose.yml -f tls.docker-compose.yml up
```

The squest service is then reachable via HTTP and HTTPS standard ports (80/443).

- http://squest.domain.local
- https://squest.domain.local
