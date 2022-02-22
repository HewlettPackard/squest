# Teams

Teams can be used to give a set of permissions on an object to a user or a group of users.
This feature allows, for example, to share instances of provisioned services to multiple users so they can retrieve and  manage request of those instances in their own Squest session.

A team can be created by any logged user. The creator become the default administrator of the team and can then:

- link instances
- add users
- set permissions

!!! note

    A team can have multiple admins but needs to have at least one admin

## Team roles

| Role          | Team permissions                                                           |
| ------------- | -------------------------------------------------------------------------- |
| Administrator | List members<br>Manage members<br>Link instances<br>Assign permissions<br> |
| Member        | List members                                                               |


## Role permissions in teams

| Role          | Instance permissions                                               | Request permissions                           |
| ------------- | ------------------------------------------------------------------ | --------------------------------------------- |
| Administrator | Open support<br>Request new operations<br>List<br>Update<br>Delete | List<br>Cancel<br>Comment<br>Update<br>Delete |
| Operator      | Open support<br>Request new operations<br>List                     | List<br>Cancel<br>Comment                     |
| Reader        | List                                                               | List                                          |
