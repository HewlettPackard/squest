# Prometheus metrics

Squest supports optionally exposing native Prometheus metrics from the application. 
[Prometheus](https://prometheus.io/) is a popular time series metric platform used for monitoring.

Squest exposes metrics at the `/metrics` HTTP endpoint, e.g. https://squest.domain.local/metrics. 

## Squest config

Metrics page is disabled by default.
Update your `docker/environment_variables/squest.env` to enable metrics.

```bash
METRICS_ENABLED=True
METRICS_PASSWORD_PROTECTED=True
METRICS_AUTHORIZATION_USERNAME=admin
METRICS_AUTHORIZATION_PASSWORD=my_secret_password
```

## Prometheus config

Here is an example of prometheus configuration you can use to scrape squest metrics
```yaml
scrape_configs:
  - job_name: 'squest'
    scrape_interval: 30s
    metrics_path: '/metrics/'
    static_configs:
      - targets: ['squest.domain.local']
    scheme: http
    basic_auth:
      username: admin
      password: my_secret_password
```

## Exported metrics 

### squest_instance_per_service_total

Expose the total number of instance per service.

**Labels:** `['service']`

E.g:
```
squest_instance_per_service_total{service="Kubernetes"} 5.0
squest_instance_per_service_total{service="Openshift"} 11.0
squest_instance_per_service_total{service="VMWare"} 14.0
```

### squest_instance_per_state_total

Expose the total number of instance per state.

**Labels:** `['state']`

E.g:
```
squest_instance_per_state_total{state="AVAILABLE"} 2.0
squest_instance_per_state_total{state="PENDING"} 28.0
```

### squest_request_per_state_total

Expose the total number of request per state.

**Labels:** `['state']`

E.g:
```
squest_request_per_state_total{state="ACCEPTED"} 4.0
squest_request_per_state_total{state="CANCELED"} 3.0
squest_request_per_state_total{state="COMPLETE"} 5.0
squest_request_per_state_total{state="FAILED"} 4.0
squest_request_per_state_total{state="ON_HOLD"} 2.0
squest_request_per_state_total{state="PROCESSING"} 3.0
squest_request_per_state_total{state="REJECTED"} 5.0
squest_request_per_state_total{state="SUBMITTED"} 4.00
```

### squest_instance_total

Total number of instance in squest

**Labels:** `['service', 'state', 'billing_group']`

E.g:
```
squest_instance_total{billing_group="Orchestration",service="VMWare",state="AVAILABLE"} 1.0
squest_instance_total{billing_group="Assurance",service="VMWare",state="AVAILABLE"} 1.0
squest_instance_total{billing_group="Orchestration",service="VMWare",state="PENDING"} 3.0
squest_instance_total{billing_group="5G",service="VMWare",state="PENDING"} 6.0
squest_instance_total{billing_group="Assurance",service="VMWare",state="PENDING"} 3.0
squest_instance_total{billing_group="Assurance",service="Openshift",state="PENDING"} 3.0
squest_instance_total{billing_group="5G",service="Openshift",state="PENDING"} 3.0
squest_instance_total{billing_group="Orchestration",service="Openshift",state="PENDING"} 4.0
squest_instance_total{billing_group="Orchestration",service="Kubernetes",state="PENDING"} 1.0
squest_instance_total{billing_group="5G",service="Kubernetes",state="PENDING"} 2.0
squest_instance_total{billing_group="Assurance",service="Kubernetes",state="PENDING"} 2.0
squest_instance_total{billing_group="None",service="Openshift",state="PENDING"} 1.0
```

### squest_request_total

Total number of request in squest

**Labels:** `['service', 'state']`

E.g:
```
squest_request_total{service="VMWare",state="COMPLETE"} 3.0
squest_request_total{service="VMWare",state="PROCESSING"} 2.0
squest_request_total{service="VMWare",state="ACCEPTED"} 2.0
squest_request_total{service="VMWare",state="ON_HOLD"} 1.0
squest_request_total{service="VMWare",state="REJECTED"} 4.0
squest_request_total{service="VMWare",state="SUBMITTED"} 1.0
squest_request_total{service="VMWare",state="FAILED"} 1.0
squest_request_total{service="Openshift",state="REJECTED"} 1.0
squest_request_total{service="Openshift",state="CANCELED"} 2.0
squest_request_total{service="Openshift",state="FAILED"} 3.0
squest_request_total{service="Openshift",state="COMPLETE"} 1.0
squest_request_total{service="Openshift",state="SUBMITTED"} 2.0
squest_request_total{service="Openshift",state="ACCEPTED"} 2.0
squest_request_total{service="Kubernetes",state="SUBMITTED"} 1.0
squest_request_total{service="Kubernetes",state="COMPLETE"} 1.0
squest_request_total{service="Kubernetes",state="CANCELED"} 1.0
squest_request_total{service="Kubernetes",state="PROCESSING"} 1.0
squest_request_total{service="Kubernetes",state="ON_HOLD"} 1.0
```

### squest_support_total

Total number of support

**Labels:** `['state']`

E.g:
```
squest_support_total{service="VMWare",state="CLOSED"} 2.0
squest_support_total{service="VMWare",state="OPENED"} 1.0
```

### squest_user_total

Total number of user

**Labels:** `['is_superuser']`

E.g:
```
squest_user_total{is_superuser="true"} 1.0
squest_user_total{is_superuser="false"} 6.0
```

### squest_team_total

Total number of team

E.g:
```
squest_team_total 3.0
```

### squest_billing_group_total

Total number of team

E.g:
```
squest_billing_group_total 3.0
```

### squest_quota_consumed

Consumption of quota per billing group and attribute

E.g:
```
squest_quota_consumed{billing_group="5G",quota_attribute="CPU"} 22.0
squest_quota_consumed{billing_group="5G",quota_attribute="Memory"} 45.0
squest_quota_consumed{billing_group="Assurance",quota_attribute="CPU"} 20.0
squest_quota_consumed{billing_group="Assurance",quota_attribute="Memory"} 23.0
```

### squest_quota_limit

Limit of quota per billing group and attribute

```
squest_quota_limit{billing_group="5G",quota_attribute="CPU"} 100.0
squest_quota_limit{billing_group="5G",quota_attribute="Memory"} 50.0
squest_quota_limit{billing_group="Assurance",quota_attribute="CPU"} 45.0
squest_quota_limit{billing_group="Assurance",quota_attribute="Memory"} 12.0)
```

A percentage of consumption can be calculated by using `squest_quota_consumed` and `squest_quota_limit`. PromQL example:
```
round((squest_quota_consumed / squest_quota_limit) * 100)
```
