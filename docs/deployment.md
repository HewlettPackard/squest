# Deploy Squest

## Docker compose based deployment

The current deployment is based on Docker compose for testing the tool.

Pre-requisites:

- docker
- docker-compose

To run the application, execute the docker compose file
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

## TLS

This section explains how to add TLS support on Squest.

The TLS endpoint is managed by a reverse proxy on top of the default web server.
This is not the only way to handle this part. Many tools like Nginx, Apache or Traefik could be used, and you are free 
to use the one you want instead of this proposed configuration.
The only recommendation we have is to keep the default nginx web server as main http entrypoint.

### TLS using Caddy

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
docker-compose -f dev-env.docker-compose.yml -f full-env.docker-compose.yml -f tls.docker-compose.yml up
```

The squest service is then reachable via HTTP and HTTPS standard ports (80/443).

- http://squest.domain.local
- https://squest.domain.local


## Backup

Persistent data of squest are:

- database
- media folder (used to store images)

An integrated backup solution based on [django-dbbackup](https://django-dbbackup.readthedocs.io/en/master/) is 
available. Once enabled, backups are placed in the `/app/backup` folder of the `celery-beat` container.

### Execute a backup manually

Execute the command below against the celery-beat container:
```bash
docker-compose exec celery-beat python manage.py dbbackup --clean
docker-compose exec celery-beat python manage.py mediabackup --clean
```

Get the backup list
```bash
docker-compose exec celery-beat python manage.py listbackups
```

Output example:
```
Name                                            Datetime            
default-3095326a6ee7-2021-09-10-112953.dump     09/10/21 11:29:53   
3095326a6ee7-2021-09-10-113338.tar              09/10/21 11:33:38 
```

Data are placed by default in a mounted volume named `squest_backup`. You can get the real path on the host by inspecting 
the volume:
```
docker volume inspect squest_backup
```

Output example:
```json
[
    {
        "CreatedAt": "2021-09-13T09:42:26+02:00",
        "Driver": "local",
        "Labels": {
            "com.docker.compose.project": "squest",
            "com.docker.compose.version": "1.28.4",
            "com.docker.compose.volume": "backup"
        },
        "Mountpoint": "/var/lib/docker/volumes/squest_backup/_data",
        "Name": "squest_backup",
        "Options": null,
        "Scope": "local"
    }
]

```

In this example, data are placed in the mount point `/var/lib/docker/volumes/squest_backup/_data` on the host. 
Files in this path need to be placed in a safe place.

### Enable automatic backup

Enable automatic backup by updating your environment configuration file `docker/environment_variables/squest.env`:
```bash
BACKUP_ENABLED=True
```

By default, backup is performed every day at 1 AM.

>**Note**: Follow the full [configuration documentation](configuration/squest_settings.md) to know all available flags
 for the backup service.


### Restore

Start Squest services like for the initial deployment
```bash
docker-compose up
```

Copy you backup files into the `squest_backup` mount point of your host
```bash
sudo cp <backup_folder_path>/* <squest_backup_mount_point>
```

E.g:
```bash
sudo cp ~/Desktop/squest_backup/* /var/lib/docker/volumes/squest_backup/_data/
```

Check that the tool can list your backup files
```bash
docker-compose exec celery-beat python manage.py listbackups
```

Restore the database and media folder
```bash
docker-compose exec celery-beat python manage.py dbrestore
docker-compose exec celery-beat python manage.py mediarestore 
```

>**Note:** Get more info on dbrestore and mediarestore command arguments on the 
 [official doc](https://django-dbbackup.readthedocs.io/en/master/commands.html#).
