# RBAC (Role Based Access Control)

Role-based access control (RBAC), is a mechanism that restricts Squest access. 
It involves setting **permissions** to enable access to authorized users. Permissions are then grouped 
into **Roles** and given to a scope which can be a _user_, a _team_ or and _organizations_.

The Squest RBAC system enable an administrator to grant users or groups the ability to perform an action 
on arbitrary subsets of objects in Squest.

## Permissions

Permission in Squest represent a relationship with following components:

- **Name:** A short description  of the permission.
- **Codename:** A unique identifier for the permission with camel case format.
- **Content type:** A Squest object (E.g: Request, Instance)

For example, a permission named "Can request a day2 operation on instance" attached to the content type "instance".
This permission is required, like the name is suggesting, to create a request for a day 2 operation on an existing instance.

!!!note

    New permissions can be created in the context of [approval steps](approval_workflow.md#steps). 

## Default permissions

Default permissions are permissions granted to all logged Squest user. Permissions are purely additive (there are no "deny" rules).

!!!warning

    Changing the list of default permissions may impact the global bahavior of Squest. Use with caution.

## Role

A role is a set of permissions. 
After creating a _Role_, you can assign it to a _user_, _team_ or _organization_.
