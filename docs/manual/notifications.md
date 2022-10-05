# Notifications

!!! note
    
    Squest current notification system only support emails.

## Enable or disable notifications

By default, notifications are enabled. You can disable all notifications from your profile page by accessing the profile page in the top right corner of the Squest application.

!!! note

    Administrators receive all notifications for all events. Filters can be added to limit notifications to some criteria. See below.

## Notification filters (admin)

Notification filters can be set on several criteria:

- Services
- Operations
- Request states
- Instance states
- On instance spec conditions (when)

When a filter is declared, all criteria in the filter must be valid to send a notification. For example, if a service and an operation is defined both need to be valid. 

Example behavior with 2 criteria defined:
```
service1 AND operation2
```

When multiple item are selected for a particular criteria, only one item need to match to validate the criteria.

Example behavior when setting multiple service and multiple operation:
```
(service1 OR service2) AND (operation2 OR operation2)
```

### When: Ansible like conditions

The `when` condition allows to filter notification based on current "request".
The syntax is the same as the one used in Ansible. The `request` object is directly usable as context in the condition without JINJA double-curly braces.
See the [Jinja documentation](jinja.md) for more example.

E.g with a 'when' based on the survey filled by the user
```python
request.fill_in_survey['location'] == 'grenoble'
```

E.g with instance spec
```python
request.instance.spec['spec_key1'] == 'spec_value1'
```
