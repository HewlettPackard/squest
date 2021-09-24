# Backup

Persistent data of squest are:

- database
- media folder (used to store images)

An integrated backup solution based on [django-dbbackup](https://django-dbbackup.readthedocs.io/en/master/) is 
available. Once enabled, backups are placed in the `/app/backup` folder of the `celery-beat` container.

## Execute a backup manually

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

## Enable automatic backup

Enable automatic backup by updating your environment configuration file `docker/environment_variables/squest.env`:
```bash
BACKUP_ENABLED=True
```

By default, backup is performed every day at 1 AM.

>**Note**: Follow the full [configuration documentation](../configuration/squest_settings.md) to know all available flags
 for the backup service.


## Restore

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
