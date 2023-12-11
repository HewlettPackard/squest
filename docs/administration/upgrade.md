# Squest upgrade

This documentation aims at explaining how to perform an upgrade of squest on new release.
 
!!! note

    Read the changelog and release note of the version before performing any update to know what are the breaking changes or specific requirements of the new release.

!!! note

    We recommend performing a manual backup before any upgrade. See the dedicated [backup doc](backup.md)

## Using Docker compose

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

## Using Kubernetes

Change the Squest image version in the inventory
```yaml
squest_django:
  image: quay.io/hewlettpackardenterprise/squest:<version>
```

Run the update playbook
```bash
ansible-playbook -v -i inventory update.yml
```

The playbook will:

- Redirect the traffic to maintenance page
- Rollout Django containers with the new image
- Execute database migration
- Restore traffic to Squest once the app is back available
