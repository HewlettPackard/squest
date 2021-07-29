# Billing groups

> **Note: ** Billing groups is optional feature.

Billing groups allow Squest administrator to visualize who is consuming what.

## Billing groups management

The administrator can create a new billing group and manage users in a billing groups.

From the sidebar, click on 'Billing Groups'. 
All billing groups are listed in this page, you can see the name and the users count of each billing group.

### Create a new billing group

From the billing groups page, click on 'Add' button in the upper left corner then choose an unused billing group name.

### Edit a billing group

From the billing groups page, click on 'Edit' button of the billing group then choose an unused billing group name.

### Manage users in a billing group

From the billing groups page, click on user count button of the billing group then choose select users will be in the group.

### Delete a billing group

From the billing groups page, click on 'Delete' button of the billing group you must confirm before delete.

## Define billing group in a service

As an administrator, you must describe how the billing of your service will be predefined.
Through the service form, you have several choices:

### Admin defined billing group
The administrator choose a fixed billing group (can be none) with a choice field. 
The billing group chosen will be predefined foreach instance created by this service.
The administrator can also hide the billing for user in the request form with a checkbox field.

### User defined billing group

#### From his billing group

The administrator let user choose from his billing group (user without billing group could not use your service) when he sends an instance request

#### From all billing group

The administrator let user choose from all billing group when he sends an instance request

## Select a billing group in a request

### Administrator defined a fixed billing group

If administrator allow the user to see the billing group, a choice field shown the billing defined by the administrator.

### Administrator let user choose the billing group

#### From his billing group

The users can choose the billing group from his billing groups with a choice field.

#### From all billing group

The users can choose the billing group from all billing groups with a choice field.
