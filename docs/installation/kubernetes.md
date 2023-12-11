# Kubernetes deployment

!!!warning

    This deployment is still a beta feature. Feel free to send pull requests to enhance the deployment or give us feedback though Gitter chat or GitHub discutions.

## Pre-requisites

The Kubernetes deployment is wrapped by Ansible. The code has been tested with Ansible version `2.15.5`.

Install Ansible dependencies:

```bash
ansible-galaxy collection install kubernetes.core
```

Install Python dependencies:
```bash
pip3 install kubernetes
```

## Ansible inventory

An example inventory file is present in `k8s/inventory/group_vars/all/squest.yml`.

For a minimal installation  you need to at least provide information concerning your Kubernetes environment
```yaml
k8s_kubeconfig_path: "/path/to/kubeconfig"
k8s_cluster_fqdn: "k8s.domain.local"
squest_namespace: "squest"
k8s_storage_class: "thin"
```

## Deploy Squest using Ansible

Run the `deploy` playbook against your inventory config file:

```bash
cd k8s
ansible-playbook -v -i inventory deploy.yml
```

**Tags:**

| Name        | Description                                 |
|-------------|---------------------------------------------|
| namespace   | Create the Squest namespace                 |
| utils       | Install CRD utils (certmanager, Prometheus) |
| db          | Deploy mariadb CRDs, operator and server    |
| rabbitmq    | Deploy rabbitmq CRDs, operator and service  |
| redis       | Deploy redis CRDs, operator and service     |
| django      | Deploy Squest application                   |
| celery      | Deploy Celery components (worker and beat)  |
| maintenance | Deploy nginx maintenance pod                |
| backup      | Deploy backup cron jobs                     |


!!! note

    By default, the deployment uses **nginx ingress controller** to configure the Squest external access on `squest.{{ k8s_cluster_fqdn }}`.

## Configuration

### Squest config

The [Squest configuration](../configuration/squest_settings.md) is injected as environment variables. The environment is placed in `squest.yml` as `env` flag like the following:
```yaml
squest_django:
  env:
    TZ: "Europe/Paris"
    DB_HOST: "mariadb"
    DB_PORT: "3306"
    REDIS_CACHE_HOST: "rfrm-redis"
    DEBUG: "true"
    DB_USER: "{{ squest_db.user }}"
    DB_PASSWORD: "{{ squest_db.password }}"
    WAIT_HOSTS: "mariadb:3306,rabbitmq:5672"
```

### Use your own ingress

By default, the playbook will configure an ingress that point to `squest.{{ k8s_cluster_fqdn }}` based on the [nginx ingress controller](https://docs.nginx.com/nginx-ingress-controller/).

To expose the Squest URL by using your own ingress controller, you can either update `annotations` (when the target controller can be managed by annotations) or disable the default ingress to declare then your ingress rules on your own.

To disable the default ingress configuration, in the `squest.yml` inventory file:
```yaml
squest_django:
  image: "quay.io/hewlettpackardenterprise/squest:latest"
  ingress:
    enabled: false
```
