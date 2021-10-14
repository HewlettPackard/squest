# Squest upgrade

This documentation aims at explaining how to perform an upgrade of squest on new release.

> **Note:** Read the changelog of the version before performing any update to know what are the breaking changes or specific requirements of the new release.

> **Note:** We recommend performing a manual backup before any upgrade. See the dedicated [backup doc](backup.md)

Stop all containers that use the Squest image
```bash
docker-compose kill django celery-worker celery-beat
```

Starting from here, the maintenance page should appear automatically in place of the Squest app.

Pull the new image
```bash
docker pull quay.io/hewlettpackardenterprise/squest:<version>
```

E.g
```bash
docker pull quay.io/hewlettpackardenterprise/squest:latest
```

Start back containers
```bash
docker-compose start django celery-worker celery-beat
```
