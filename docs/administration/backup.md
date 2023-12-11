# Backup

Persistent data of squest are:

- database
- media folder (used to store images)

An integrated backup solution based on [django-dbbackup](https://django-dbbackup.readthedocs.io/en/master/) is 
available. Once enabled, backups are placed in the `/app/backup` folder of one of the django based container.

!!! note

    Get more info on dbrestore and mediarestore command arguments on the 
    [official doc](https://django-dbbackup.readthedocs.io/en/master/commands.html#).

## Using Docker compose

### Enable automatic backup

Enable automatic backup by updating your environment configuration file `docker/environment_variables/squest.env`:
```bash
BACKUP_ENABLED=True
```

By default, backup is performed every day at 1 AM.

!!! note
  
    Follow the full [configuration documentation](../configuration/squest_settings.md) to know all available flags
    for the backup service.


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

## Using Kubernetes

### Enable automatic backup

Enable the backup in `squest.yml` inventory:
```yaml
squest_django:
  backup: 
    enabled: true
    crontab: "0 1 * * *"
```

Run the deployment playbook
```bash
ansible-playbook -v -i inventory deploy.yml --tags backup
```

### Externalize backup via SSH

This feature is optional. By default, the backup cronjob will place backup file into a PVC. Depending on your K8S environment, you might want to externalize them.
If you want to push those files into an external ssh server you can use the integrated rsync solution.

```yaml
squest_django:
  externalize_backup_via_rsync:  # rsync backup files into and external server
    enabled: true
    crontab: "30 1 * * *"
    private_ssh_key: "{{ lookup('file', '/path/to/id_ed25519_squest_k8s_dev') + '\n' }}"
    ssh_user: "squest_k8s_dev"
    ssh_server: "remote.server.ssh.net"
    remote_path: "/backup/squest_k8s_dev/"
```

### Execute a backup manually

Run the `backup.yml` playbook
```bash
ansible-playbook -v -i inventory backup.yml
```

This command will execute a job in K8S that add a backup of the database and media files into a PVC.

### Restore

To restore Squest. First, deploy the app like for the first deployment using the playbook.

Once Squest is available, copy backup files into django pod
```bash
kubectl -n squest cp ~/path/to/db-2023-12-06-182115.dump django-54b69fbb48-wrt9j:/app/backup
kubectl -n squest cp ~/path/to/media-2023-12-06-182117.tar django-54b69fbb48-wrt9j:/app/backup
```

Check backup is listed
```bash
kubectl -n squest exec -it django-54b69fbb48-wrt9j python manage.py listbackups
```

Restore by passing backup file name
```bash
kubectl -n squest exec -it django-54b69fbb48-wrt9j -- python manage.py dbrestore --database default -i db-2023-12-06-182115.dump
kubectl -n squest exec -it django-54b69fbb48-wrt9j -- python manage.py mediarestore -i media-2023-12-06-182117.tar
```
