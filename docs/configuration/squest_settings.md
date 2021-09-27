# Configure settings

Default settings are configured to provide a testing/development environment. For a production setup it is recommended
to adjust them following you production target environment.

The configuration is loaded from environment variables file placed in the folder `docker/environment_variables`.

## Environment variables

| Variable                          | Default                                          | Comment                                                                                                                                                             |
| --------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SECRET_KEY                        | Default randomly-generated                       | Django secret key used for cryptographic signing. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-SECRET_KEY).                                |
| DEBUG                             | `TRUE`                                           | Django DEBUG mode.                                                                                                                                                  |
| ALLOWED_HOSTS                     | `*`                                              | Comma separated list of allowed FQDN. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#allowed-hosts).                                                     |
| MYSQL_DATABASE                    | `squest_db`                                      | Mysql database name.                                                                                                                                                |
| MYSQL_USER                        | `squest_user`                                    | Mysql user used to connect to the DB name.                                                                                                                          |
| MYSQL_PASSWORD                    | `squest_password`                                | Password of the mysql user name.                                                                                                                                    |
| MYSQL_HOST                        | `127.0.0.1`                                      | Mysql DB host. Switch to `db` when not in dev env.                                                                                                                  |
| MYSQL_PORT                        | `3306`                                           | Mysql DB port.                                                                                                                                                      |
| LDAP_ENABLED                      | `False`                                          | Set to `True` to enable LDAP based authentication. [See configuration doc](../installation/ldap.md).                                                                                         |
| CELERY_BROKER_URL                 | `amqp://rabbitmq:rabbitmq@localhost:5672/squest` | Rabbitmq URL. Replace `localhost` by `rabbitmq` when not in dev env.                                                                                                |
| CELERYD_TASK_SOFT_TIME_LIMIT      | `300`                                            | Async task execution timeout. [Doc](https://docs.celeryproject.org/en/v2.2.4/configuration.html#celeryd-task-soft-time-limit).                                      |
| SQUEST_HOST                       | `squest.domain.local`                            | Domain name used as email sender. E.g: "squest@squest.domain.local".                                                                                                |
| SQUEST_EMAIL_NOTIFICATION_ENABLED | Based on `DEBUG` value by default                | Set to `True` to enable email notification.                                                                                                                         |
| EMAIL_HOST                        | `localhost`                                      | The SMTP host to use for sending email.                                                                                                                             |
| EMAIL_PORT                        | `25`                                             | Port to use for the SMTP server defined in `EMAIL_HOST`.                                                                                                            |
| LANGUAGE_CODE                     | `en-us`                                          | Django language. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#language-code)                                                                           |
| TIME_ZONE                         | `Europe/Paris`                                   | Time zone of the server that host Squest service. [Doc](https://docs.djangoproject.com/en/3.2/ref/settings/#std:setting-TIME_ZONE)                                  |
| DBBACKUP_CLEANUP_KEEP             | `5`                                              | Number of db backup file to keep [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media)   |
| DBBACKUP_CLEANUP_KEEP_MEDIA       | `5`                                              | Number of media backup tar to keep [Doc](https://django-dbbackup.readthedocs.io/en/master/configuration.html#dbbackup-cleanup-keep-and-dbbackup-cleanup-keep-media) |
| BACKUP_ENABLED                    | `False`                                          | Switch to `True` to enable backup                                                                                                                                   |
| BACKUP_CRONTAB                    | `0 1 * * *`                                      | Crontab line for backup. By default the backup is performed every day at 1AM                                                                                        |
| DOC_IMAGES_CLEANUP_ENABLED        | `False`                                          | Switch to `True` to enable automatic cleanup of ghost docs images from media folder                                                                                 |
| DOC_IMAGES_CLEANUP_CRONTAB        | `30 1 * * *`                                     | Crontab line for ghost image cleanup. By default performed every day at 1:30 AM                                                                                     |
