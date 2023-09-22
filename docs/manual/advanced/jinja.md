# Jinja templating

[Jinja templating](https://jinja.palletsprojects.com/en/3.1.x/templates/) is applicable within specific sections of the
Squest configuration. For example, Jinja templating enables the prefilling of a survey field for a day 2 operation using
the specs of the instance.

Jinja templating usage with `{{ instance }}` as context:

- [Custom links](../administration/extras.md#custom-links)
- [Operation survey default field config](../service_catalog/operation.md#default-value)

Jinja templating usage with `{{ request }}` as context:

- [Operation](../service_catalog/operation.md) job template config (inventory, credentials, tags, limit)
- [Approval workflow step](../administration/approval_workflow.md)


Jinja templating usage with `{{ user }}` as context:

- [Operation survey default field config](../service_catalog/operation.md#default-value)


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
                "id": 1,
                "state": 10,
                "resources": [],
                "requester": {
                    "id": 3,
                    "username": "admin@squest.com",
                    "email": "admin@squest.com",
                    "profile": {
                        "request_notification_enabled": true,
                        "instance_notification_enabled": true,
                        "request_notification_filters": [],
                        "instance_notification_filters": []
                    },
                    "first_name": "admin",
                    "last_name": "squest",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "groups": []
                },
                "quota_scope": {
                    "id": 1,
                    "rbac": [],
                    "name": "test_scope",
                    "description": "",
                    "roles": []
                },
                "name": "test",
                "spec": {
                    "os": "linux"
                },
                "user_spec": {
                    "vCPU": 2,
                    "memory": 4,
                },
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
                "id": 1,
                "state": 10,
                "resources": [],
                "requester": {
                    "id": 3,
                    "username": "admin@squest.com",
                    "email": "admin@squest.com",
                    "profile": {
                        "request_notification_enabled": true,
                        "instance_notification_enabled": true,
                        "request_notification_filters": [],
                        "instance_notification_filters": []
                    },
                    "first_name": "admin",
                    "last_name": "squest",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "groups": []
                },
                "quota_scope": {
                    "id": 1,
                    "rbac": [],
                    "name": "test_scope",
                    "description": "",
                    "roles": []
                },
                "name": "test",
                "spec": {
                    "os": "linux"
                },
                "user_spec": {
                    "vCPU": 2,
                    "memory": 4,
                },
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

This example, used in the "default limit" of the operation job template config, allows to automatically configure the
inventory limit following the given "dns" field of the survey.

<table>
    <tr>
        <td><strong>Instance context</strong></td>
        <td>
            ```json
            {
                "id": 1,
                "instance": {
                    "id": 1,
                    "state": 10,
                    "resources": [],
                    "requester": {
                        "id": 3,
                        "username": "admin@squest.com",
                        "email": "admin@squest.com",
                        "profile": {
                            "request_notification_enabled": true,
                            "instance_notification_enabled": true,
                            "request_notification_filters": [],
                            "instance_notification_filters": []
                        },
                        "first_name": "admin",
                        "last_name": "squest",
                        "is_staff": true,
                        "is_superuser": false,
                        "is_active": true,
                        "groups": []
                    },
                    "quota_scope": {
                        "id": 1,
                        "rbac": [],
                        "created": "2023-09-15T14:39:00.662779+02:00",
                        "last_updated": "2023-09-15T14:39:00.675268+02:00",
                        "name": "test",
                        "description": "",
                        "roles": []
                    },
                    "created": "2023-09-15T14:39:03.321285+02:00",
                    "last_updated": "2023-09-15T14:39:03.367724+02:00",
                    "name": "test",
                    "spec": {
                    "os": "linux"
                },
                "user_spec": {
                    "vCPU": 2,
                    "memory": 4,
                },
                    "date_available": null,
                    "service": 1
                },
                "user": {
                    "id": 3,
                    "username": "admin@squest.com",
                    "email": "admin@squest.com",
                    "profile": {
                        "request_notification_enabled": true,
                        "instance_notification_enabled": true,
                        "request_notification_filters": [],
                        "instance_notification_filters": []
                    },
                    "first_name": "admin",
                    "last_name": "squest",
                    "is_staff": true,
                    "is_superuser": true,
                    "is_active": true,
                    "groups": []
                },
                "created": "2023-09-15T14:39:03.545051+02:00",
                "last_updated": "2023-09-15T14:39:03.590197+02:00",
                "fill_in_survey": {
                    "vm_os": "rhel8.5"
                },
                "admin_fill_in_survey": {},
                "date_submitted": "2022-08-30T14:46:05.856352+02:00",
                "date_complete": "2022-08-30T17:05:05.356421+02:00",
                "date_archived": null,
                "tower_job_id": 1,
                "state": 7,
                "operation": 9,
                "accepted_by": null,
                "processed_by": null,
                "approval_workflow_state": null
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
