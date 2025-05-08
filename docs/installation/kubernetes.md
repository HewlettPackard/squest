# Kubernetes deployment

There are currently two deployment options available:

- Official Ansible-based installation
- Community-maintained Helm Chart

## Ansible-based Installation 

!!!warning

    This deployment is still a beta feature. Feel free to send pull requests to enhance the deployment or give us feedback though Gitter chat or GitHub discutions.

### Pre-requisites

The Kubernetes deployment is wrapped by Ansible. The code has been tested with Ansible version `2.15.5`.

#### Python

Install Python dependencies:
```bash
pip3 install -r k8s/requirements.txt
```

#### Ansible

Install Ansible dependencies:

```bash
ansible-galaxy install -r k8s/requirements.yml
```

#### Helm

Operators installation is handled by Helm. Follow [the official documentation](https://helm.sh/docs/intro/install/) to install Helm on your workstation.

### Ansible inventory

An example inventory file is present in `k8s/inventory/group_vars/all/squest.yml`.

For a minimal installation  you need to at least provide information concerning your Kubernetes environment
```yaml
k8s_kubeconfig_path: "/path/to/kubeconfig"
k8s_cluster_fqdn: "k8s.domain.local"
squest_namespace: "squest"
k8s_storage_class: "thin"
```

### Deploy Squest using Ansible

Run the `deploy` playbook against your inventory config file:

```bash
cd k8s
ansible-playbook -v -i inventory deploy.yml
```

**Tags:**

| Name        | Description                                 |
|-------------|---------------------------------------------|
| namespace   | Create the Squest namespace                 |
| db          | Deploy mariadb CRDs, operator and server    |
| rabbitmq    | Deploy rabbitmq CRDs, operator and service  |
| redis       | Deploy redis CRDs, operator and service     |
| django      | Deploy Squest application                   |
| celery      | Deploy Celery components (worker and beat)  |
| maintenance | Deploy nginx maintenance pod                |
| backup      | Deploy backup cron jobs                     |


## Configuration

#### Squest config

The [Squest configuration](../configuration/squest_settings.md) is injected as environment variables. The environment is placed in `squest.yml` as `env` flag like the following:
```yaml
squest_django:
  env:  # squest settings
    TZ: "Europe/Paris"
    DB_HOST: "mariadb"
    DB_PORT: "3306"
    DB_USER: "{{ squest_db.user }}"
    DB_DATABASE: "{{ squest_db.database }}"
    REDIS_CACHE_HOST: "redis-master"
    DEBUG: "false"
    RABBITMQ_HOST: "rabbitmq"
    RABBITMQ_PORT: "5672"
```

Secrets can be injected using the `squest_django.env_secrets` variable or can be created manually by creating a secret named `squest-secrets`.
```yaml
squest_django:
  env_secrets:
    EMAIL_HOST_PASSWORD: "my-secret-password"
    METRICS_AUTHORIZATION_PASSWORD: "metrics-password"
    SECRET_KEY: "django-secret-key"
    DEFAULT_ADMIN_TOKEN: "XXXXXX----TOKEN----XXXXXX"
    DEFAULT_ADMIN_PASSWORD: "my-secret-password"
    AUTH_LDAP_BIND_PASSWORD: "my-secret-password"
```

### LDAP custom config

LDAP can be configured using environment variable. For very specific use case you may need to inject a custom `ldap_config.py`.
```yaml
squest_django:  
  ldap:  # extra ldap config
    enabled: true  # this will create a config map for ldap_config.py
    ldap_config_file: "{{ lookup('file', playbook_dir + '/../Squest/ldap_config.py') }}"  # we mount by default the file provided in squest core code
```

### Use your own ingress

By default, the playbook will configure an ingress that point to `squest.{{ k8s_cluster_fqdn }}` based on the [nginx ingress controller](https://docs.nginx.com/nginx-ingress-controller/).

Update the ingress configuration, in the `squest.yml` inventory file:
```yaml
squest_django:
  ingress:  # default ingress based on nginx controller
    enabled: true
    host: "squest.{{ k8s_cluster_fqdn }}"
    classname: my-ingress-controller-name
    annotations:
      ingress_key: "ingress_value"
```

## Helm-based Installation

### Pre-requisites

Installation is handled by Helm. Follow [the official documentation](https://helm.sh/docs/intro/install/) to install Helm on your workstation.

### Installation

```bash
helm repo add christianhuth https://charts.christianhuth.de
helm repo update
helm install my-release christianhuth/squest
```

### Configuration

Please check the documentation of the Chart for all available configuration options: [Documentation on ArtifactHub](https://artifacthub.io/packages/helm/christianhuth/squest).
