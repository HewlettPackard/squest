# Jinja templating

[Jinja templating](https://jinja.palletsprojects.com/en/3.1.x/templates/) can be used in some part of the Squest configuration.

Jinja templating usage with `{{ instance }}` as context:

- [Custom links](tools.md#custom-links)
- [Operation survey default field config](../service_catalog/operation.md#default-value)

Jinja templating usage with `{{ request }}` as context:

- Operation job template config (inventory, credentials, tags, limit)

## Examples

### String with no jinja

Even if the context is sent, a hard coded string can be used without using it.
<table>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>My hard coded value</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>My hard coded value</td>
    </tr>
</table>

### Using the instance as context

Accessing instance name:
<table>
    <tr>
        <td><strong>Instance context</strong></td>
        <td>
            ```json
            {
                "id": 31,
                "state": "AVAILABLE",
                "resources": [],
                "billing_group": null,
                "spoc": {
                    "id": 2,
                    "username": "admin",
                    "email": "admin@squest.domain",
                    "profile": {
                        "request_notification_enabled": true,
                        "instance_notification_enabled": true,
                        "request_notification_filters": [],
                        "instance_notification_filters": []
                    },
                    "first_name": "",
                    "last_name": "",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "billing_groups": []
                },
                "name": "my_instance",
                "spec": {
                    "test": 2
                },
                "user_spec": {},
                "date_available": null,
                "service": 1
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>My hard coded value with {{ instance.name }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>My hard coded value with my_instance</td>
    </tr>
</table>

Accessing instance spec:
<table>
    <tr>
        <td><strong>Instance context</strong></td>
        <td>
            ```json
            {
                "id": 31,
                "state": "AVAILABLE",
                "resources": [],
                "billing_group": null,
                "spoc": {
                    "id": 2,
                    "username": "admin",
                    "email": "admin@squest.domain",
                    "profile": {
                        "request_notification_enabled": true,
                        "instance_notification_enabled": true,
                        "request_notification_filters": [],
                        "instance_notification_filters": []
                    },
                    "first_name": "",
                    "last_name": "",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "billing_groups": []
                },
                "name": "my_instance",
                "spec": {
                    "os": "linux"
                },
                "user_spec": {},
                "date_available": null,
                "service": 1
            }            
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td> {{ instance.spec.os }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>linux</td>
    </tr>
</table>

!!! note

    The `spec` and `user_spec` variables are only usable on **Update** or **Delete** operations as the pending instance does not contain any spec before its provisioning.

!!! note

    If the given variable key doesn't exist, the default value will be set to an empty string.

### Using the request as context

This example, used in the "default limit" of the operation job template config, allows to automatically configure the inventory limit following the given "dns" field of the survey.

<table>
    <tr>
        <td><strong>Instance context</strong></td>
        <td>
            ```json
            {
                "id": 32,
                "instance": {
                    "id": 31,
                    "state": "PENDING",
                    "resources": [],
                    "billing_group": null,
                    "spoc": {
                        "id": 2,
                        "username": "admin",
                        "email": "admin@squest.domain",
                        "profile": {
                            "request_notification_enabled": true,
                            "instance_notification_enabled": true,
                            "request_notification_filters": [],
                            "instance_notification_filters": []
                        },
                        "first_name": "",
                        "last_name": "",
                        "is_staff": true,
                        "is_superuser": true,
                        "is_active": true,
                        "billing_groups": []
                    },
                    "name": "my-instance",
                    "spec": {                        
                    },
                    "user_spec": {},
                    "date_available": null,
                    "service": 1
                },
                "user": {
                    "id": 2,
                    "username": "admin",
                    "email": "admin@squest.domain",
                    "profile": {
                        "request_notification_enabled": true,
                        "notification_filters": []
                    },
                    "first_name": "",
                    "last_name": "",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "billing_groups": []
                },
                "fill_in_survey": {
                    "dns": "vm-name.domain.com"
                },
                "admin_fill_in_survey": {},
                "date_submitted": "2022-09-29T16:01:45.409615+02:00",
                "date_complete": null,
                "date_archived": null,
                "tower_job_id": null,
                "state": "ACCEPTED",
                "operation": 7,
                "approval_step": null
            }         
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td> {{ request.fill_in_survey.dns }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>vm-name.domain.com</td>
    </tr>
</table>

### Dict access

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": {
                        "linux": "ubuntu"
                    }
                }               
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>{{ instance.spec.os['linux'] }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>ubuntu</td>
    </tr>
</table>

### List access

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": ["linux", "windows"]
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>{{ spec.os[1] }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>windows</td>
    </tr>
</table>

### Filters

Jinja filters can also be used to transform variables.

For example, the 'select multiple' field type requires a list of string separated with a carriage return marker (`\n`).

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "os": ["linux", "windows"]
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>{{ spec.os | join('\n') }}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>linux\nwindows</td>
    </tr>
</table>

### Conditions

In this example, the target inventory ID is changed following a survey variable `is_prod`.

<table>
    <tr>
        <td><strong>Instance JSON spec</strong></td>
        <td>
            ```json
            {
                "spec": {
                    "is_prod": true
                },
                "user_spec": {}
            }
            ```
        </td>
    </tr>
    <tr>
        <td><strong>Jinja string</strong></td>
        <td>{% if is_prod %}1{% else %}3{% endif %}</td>
    </tr>
    <tr>
        <td><strong>Result</strong></td>
        <td>linux\nwindows</td>
    </tr>
</table>
