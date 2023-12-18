# Release Notes

Squest releases are numbered as major, minor, and patch releases. 
For example, version `1.1.0` is a minor release, and `1.1.5` is a patch release. These can be described as follows:

- **Major** - Introduces or removes an entire API or other core functionality
- **Minor** - Implements major new features but may include breaking changes for API consumers or other integrations
- **Patch** - A maintenance release which fixes bugs and may introduce backward-compatible enhancements

## v2.4.0

This is a **Minor** update of Squest:

### Breaking changes
- Rename "NEED INFO" state into "ON HOLD", related urls changed

### Fix
- Fix step ordering in RequestDetail
- Fix bug on DeleteView related to Django 4
- Cancel button was not displayed in RequestDetail when using ApprovalWorkflow
- Documentation contrast fixed when using dark mode
- Notifications were not sent when filtering on states
- Squest survey fields are sorted in the same way as AWX survey fields.
- Fix TypeError error when social login (OIDC) is enabled

### Enhancement
- Add a transition in FSM to switch from "ON HOLD" to "ACCEPTED"
- Add field "enabled" in ApprovalWorkflow
- Remove "operations" field in ApprovalWorkflow form when editing
- Add the number of items displayed at the end of lists
- Improve API performance for /api/service-catalog/request/ and /api/service-catalog/instance/
- Improve performance in homepage when several requests where displayed in "To be reviewed"*
- Cache is disabled during django command execution (e.g. migration, collect-static,...)
- In quota filter, display the Organization and Team name instead of the Team name
- Service details page added

### Feature
- Support Kubernetes deployment (Beta)
- Service request for team will automatically use the approval workflow set - by the parent organization
- ApprovalWorkflow can now reset all submitted requests using (or no more using) the workflow
- In RequestDetail, Submitted request can now be re_submit to reset all approval steps (Permission "service_catalog.re_submit_request" needed)
- Add new permission "service_catalog.list_approvers" that allow users to see who can accept a request
- Link attributes to services


## v2.3.0

This is a **Minor** update of Squest:

### Fix
- Permission allow to show only the linked item in the sidebar group
- Remove the quota when limit is unset in form
- RequestNotification/InstanceNotificationFilter filter were not saved

### Feature
- Email notification template


## v2.2.0

This is a **Minor** update of Squest:

### Internal
- Bump libraries and upgrade to Django 4

### Fix
- Fix profile page raise a 500 error

### Enhancement
- Change the verbose name of "Requester" to "Owner" in Instance model

### Feature
- OpenID Connect supported


## v2.1.2

This is a **Patch** update of Squest:

### Fix
- Fix operation field when min and max are not set
- Display the admin survey when request is processing or rejected
- Set the request to fail state when AWX api return no job id
- Fix sort in tables + fix HTML anchor in tables
- Fix bug in permission when user is both owner_permissions and in global_permissions
- Fix approval.html for ARCHIVED state
- Fix per_page on table in tabs
- FiX CSS on tables
- Fix maintenance page was not showing up after nginx restart

### Enhancement
- Add service_catalog_instance filter in ResourceApi
- Add ID to instance and request filters
- Add "organization" and "team" to ScopeSerializer
- Archive and unarchive request without confirmation
- Add review again button after request fail or accepted


## v2.1.1

This is a **Patch** update of Squest:

### Fix
- Email were not sent to some requester
- Fix Squest logo size in email
- Add back current instance spec and admin spec in request details page
- Fix displayed info in user details page
- Fix global sync when no default value set on survey field


## v2.1.0

This is a **Minor** update of Squest:

### Fix
- Breadcrumbs in Teams did not show Organization in some views.

### Enhancement
- Login page redirect to the next page.

### Feature
- Introducing "owner permissions" in Global scopes. Admin can add permissions to users for objects that belong to them (Instance, Request and Support).
This enables a v1-like functionality in terms of permissions.


## v2.0.0

This is a **Major** update of Squest:

### Breaking changes
- Resource tracker v1 is removed. Data are lost after migration to v2. A migration script is available, read the documentation for more information
- API complete refactoring. Use Swagger documentation to get new endpoints
- Approval workflow v1 has been removed. Workflow need to be re-created manually
- Teams v1 are removed and will need to be created back manually
- Quota scope (formerly billing group is now mandatory)

### Fix
- Processing a request is auto-process no longer produce 500 error

### Enhancement
- Resource tracking refactoring. Resource pool are removed. Links are done directly between resource groups
- Approval workflow refactoring (with configurable auto accept on each step)
- Dashboard refactored. Added list of request that can be approved by the current user based on permissions
- Survey max value on integer can be limited by quota
- Request details page reworked
- Pagination now available up to 1000 on each list
- Support of emojis in request and support message
- Add "user" data to jinja context
- New state on instance: ABORTED (when cancelling a request)

### Feature
- RBAC
- Organizations added as top layer (replacing billing groups)
- Quota management. Quota attribute are same as resource tracker attribute and linkable to survey fields.
- Move resource from a resource group to another resource group
- Dark theme

NOTES:

- The resource tracker component has been entirely refactored and cannot be migrated automatically
- The API has been reworked
- The previous team feature has been discontinued and replaced by an Organization/Team feature. Please note that teams data from v1 will be lost

To migrate from v1 to v2 if you were using the **resource tracking** feature:

- Make sure that _attribute definitions_ that are common (same type) are exactly the same **name**
- Follow the [upgrade documentation](administration/upgrade.md) to bump your current Squest installation to the last v1 version available: `v1.10.5`
- Execute the resource tracker export script:

```bash
docker-compose exec -T django python3 manage.py export_resource_tracker_v1
```

- Follow the upgrade documentation to bump your installation to `v2.X.X`
- Execute the resource tracker import script: 

```bash
docker-compose exec -T django python3 manage.py import_resource_tracker_v1
```


## v1.10.6

This is a **Patch** update of Squest:

### Fix
- Fix Celery beat execution command in Docker Compose


## v1.10.5

This is a **Patch** update of Squest:

### Feature
- Command to generate resource tracker v1 migration YAML.

## v1.10.4

This is a **Patch** update of Squest:

### Fix
- Freeze caddy image to 2.6 (2.7 is not stable yet)


## v1.10.3

This is a **Patch** update of Squest:

### Fix
- Freeze image versions in docker-compose
- Mariadb command is used instead of mysql command (since mariadb 11 msql command is no longer compatible)


## v1.10.2

This is a **Patch** update of Squest:

### Fix
- Fix IS_DEV_SERVER boolean

### Enhancement
- Go to process after accepting
- Add accept and process
- Add error 500 page


## v1.10.1

This is a **Patch** update of Squest:

### Fix
- Close MySQL port by default
- Move phpmyadmin in dev.docker-compose.yml

### Enhancement
- Refactoring mail templates
- Add billing group filter on request list page
- Expose SQUEST_IMAGE and SQUEST_TAG as variables in docker-compose (see documentation)
- Always mount volume for field_validators

### Feature
- Add IS_DEV_SERVER flag


## v1.10.0

This is a **Minor** update of Squest:

### Fix
- Fix SQUEST_EMAIL_HOST env var to match the behavior described in the doc. Removed hard coded squest@. ⚠️may break your config if @ is not set.

### Feature
- CVS export on resource pool page
- Add PostgreSQL database support
- Add a custom note into the login page


## v1.9.0

This is a **Minor** update of Squest:

### Breaking changes
- Global hook execution now send the same "squest" metadata to the job template as the one used in service operations

### Fix
- Global hook now send squest metadata
- Global hook use admin request serializer instead of read only serializer
- Fix table sort in request and instance list page

### Enhancement
- Minor UI enhancements
- Add a link to go back to a request details from request comment page


## v1.8.2

This is a **Patch** update of Squest:

### Fix
- In API, extra_vars JSON fields were displayed as str instead of dict.
- Allow to delete UserRoleBinding linked to deleted object.
- UserRoleBindings on Request object were not deleted when deleting Request (Fix and cleanup migration).

### Feature
- Tags can be filtered with 'AND' or 'OR' method (only 'AND' before).


## v1.8.1

This is a **Patch** update of Squest:

### Fix
- Fix the request serializer on day 2 operations. fill_in_survey was saved as string instead of dict

### Enhancement
- Minor UI enhancements


## v1.8.0

This is a **Minor** update of Squest:

### Breaking changes
- Context usable with Jinja has changed. spec/user_spec --> instance. Impacted pages:
  - default values of an operation survey
  - 'when' of a profile notification filter

### Fix
- URL for available instances was wrong
- Fix JSON integer cast in survey
- Remove exposed MySQL port from prod

### Enhancement
- Add billing group field in UserSerializer
- Filter instance by spec and user spec
- Update filter sidebar size
- Add accepted_by and approved_by field

### Feature
- Add job template config on request process
- Notification filters split: Support or request notification

## v1.7.5

This is a **Patch** update of Squest:

### Fix
- Fix bad queryset 😅


## v1.7.4

This is a **Patch** update of Squest:

### Fix
- Accept request from API without survey doesn't work
- Auto-process only worked if auto-accept is enabled
- The extra_vars field is not valid if it is in JSON from the API.
- Update resource from API does not work for all fields

### Enhancement
- Link docs to operations
- Add request messages to request detail


## v1.7.3

This is a **Patch** update of Squest:

### Fix
- Request operation from API return the new request
- Support choices as list in AWX survey

### Enhancement
- Create instance from API return full serializer
- Instance filtered by multiple choice instead of text in UI
- Link to access instances by service from home page in UI
- Service catalog forms with data live search in UI
- Filter for attribute definitions in API


## v1.7.2

This is a **Patch** update of Squest:

### Fix
- Date submitted was updated on each save
- Hide disabled services from homepage
- Hide admin only create operations for end users

### Enhancement
- Custom threshold color on resource pool and quota
- Add description documentation to services and portfolios

### Feature
- Custom links on instance detail page


## v1.7.1

This is a **Patch** update of Squest:

### Fix
- Fix breadcrumbs links in notification page
- Link to the doc now target the correct current version of the running squest instance
- fill_in_survey flag was saved as a string when created from the API
- Fix maintenance mode was not working when used from the API

### Enhancement
- Date format can be set for all date from the settings
- Merge operation name and operation color type


## v1.7.0

This is a **Minor** update of Squest:

### Internal
- Bump python version to 3.10
### Fix
- Global hook was not working
- Fix ajax call when synchronizing job template. Number of template was not updated
### Enhancement
- Operations can be limited to administrators only
### Feature
- Notification filters
- Extra vars on Tower server, service and operation
- Add maintenance mode



## v1.6.1

This is a **Patch** update of Squest:

### Fix
- Pagination navigation was not working with https scheme

### Feature
- Add support of external tool as support URL


## v1.6.0

This is a **Minor** update of Squest:

### Breaking changes
-  API: Pagination added to all GET list of objects
### Fix
- API: ID was not given when new request created
- Format issue with fill in survey
- instance_name variable can be used in the tower survey
### Enhancement
- Swagger page support bearer auth
- Send email when support is closed
- show specs on accept/review page
- Add pending request for each service in the admin dashboard
- Save tags in session
### Feature
- API: Add filters (filter by exact name in API vs contains in UI)
- Default API admin token can be added to the settings
- Python script based validator for form field
- Approval workflow
- Bulk delete for Instances
- Allow several create operations
- Portfolio


## v1.5.2

This is a **Patch** update of Squest:

### Fix
- Remove hardcoded url in email template
- Mails were not send to user after receiving a new message

### Enhancement
- Instance serializer used User serializer instead of id
- Supports list can be filtered by Service
- Global hook can be linked to an operation
- Instance can be deleted by an admin from API

### Feature
- Message can be edited
- Operations can be disabled


## v1.5.1

This is a **Patch** update of Squest:

### Fix
- Calculate total resources of a resource group was not called when creating a resource from the API

### Enhancement
- Added a button to re calculate total of a resource group


## v1.5.0

This is a **Minor** update of Squest:

### Breaking changes
- API: Service and Operation creation split.

### Fix
- Patch a resource without "text_attribute" field filled.
- Fix Squest logo not shown in maintenance page for non-root URLs.
- Resource group and Resource pool with the same name was not displayed in the graph.
- Add missing swagger doc for operation survey.

### Enhancement
- Performance: cache + calculation + asynchronous call.
- API : Create a Service return full Service Serializer.
- Catch all Tower exceptions when processing a request.
- Remove role binding from team details.
- Global hook can be linked to a service.
- Admin can set to blank a non required field with default value in Tower survey.
- Split Service and Operation form.
- API: Split Service and Operation serializer.

### Feature
- Jinja template on survey default field value.


## v1.4.1

This is a **Patch** update of Squest:

### Breaking changes
- API: Split between admin survey and user survey

### Fix
- Fix Celery wait timeout when starting Docker compose

### Enhancement
- Admin accept request form can now update billing group and instance name
- Add date available on successfully processed instance
- Custom 404 page
- Bulk delete on request page as admin
- Added delete button on resource details page
- Hide admin filled fields from the end user survey

### Feature
- API: request state machine management
- Added "user spec" field to instance. Spec are now only visible by admin.


## v1.4.0

This is a **Minor** update of Squest:

### Breaking changes
- API: Move job template URL behind Tower URLs

### Fix
- Fix collect static in Docker image
- Service image upload on edit service
- Fix global hooks execution
- Instance details page was not displayed when the SPOC was not defined
- Several fix in UI
- Fix email notifications
- Fix team deletion. Old role bindings are deleted

### Enhancement
- Auto deletion of resource from resource group when instance from service catalog is deleted
- Celery containers wait for Squest app to be ready before starting
- Admin can manually edit requests
- End user can access request details page
- Comment field for each request
- Instance list: add some filter
- Request details page for end users

### Feature
- Resource quota per billing group
- Prometheus metrics
- Support list for end users
- API: Job Template sync


## v1.3.1

This is a **Patch** update of Squest:

### Fix
- Collect static are not executed during the docker image build anymore to prevent caching
- Email sent when request execution fail
- Migration of old permission after creating Teams
- Fix job template sync when multiple tower/awx instance are declared
- Fix swagger generated page on POST /service//request.

### Enhancement
- Remove metrics and graph from the main dashboard to speed up the loading
- Add squest host to metadata sent to Tower
- UI: refactoring of the resource group list page
- Add billing group to instance list filter

### Feature
- Bulk delete on resources


## v1.3.0

This is a **Minor** update of Squest:

### Fix
- Support and instance in sidebar are no more highlighted together
- Total resource was empty in resource group list
- Email notification for comment on request and support message

### Enhancement
- Filter hidden by default in graph

### Feature
- Team management to share instances
- API - get resource/resource group/resource pool by name


## v1.2.1

This is a **Patch** update of Squest:

### Fix
- Resource pool consumption is now updated after resource deletion
- Fix resource group save form
- Fix resource pool calculation executed when adding/deleting resources

### Enhancement
- Load git module only once in settings
- Remove useless calculation call
- Enhance test execution speed
- Add scroll bar in resource list table
- Filters moved into a sidebar


## v1.2.0

This is a **Minor** update of Squest:

### Fix
- Update permissions when SPOC is changed from instance
- Fix display error in resource pool list
- Fix default value when integer is used in Tower survey

### Enhancement
- Re-process failed requests
- Add a filter in resource tracker resource list
- Graph perf enhancement

### Feature
- User and billing group API
- User can disable email notification


## v1.1.0

This is a **Minor** update of Squest:

### Breaking changes
- Replace API token key work "Token" by "Bearer"

### Fix
- Fix empty job template survey
- Fix attribute text display in some form
- Fix link to doc in instance pages

### Enhancement
- Add a button to collapse filters in the graph view

### Feature
- Add functional testing playbooks
- API: CRUD on resource group
- API: CRUD on resource pool
- Add static HTML maintenance page
- API: CRUD on Request
- API: CRUD on Service
- API: CRUD on Operation
- Show GIT sha in the footer


## v1.0.0 - First prod release

This is a **Major** update of Squest:

### Fix
- Fix LDAP TLS support with self-signed certificates
- Fix email host url from settings

### Enhancement
- API authentication via token
- Text attribute on resource group
- Add instance and request details page
- Add job template details page
- Admin can delete instance
- Admin can archive and/or delete requests
- Add titles to identify squest fields and survey fields
- Multi stage Docker build
- Add button to list resources from resource group edit page
- Add filter on all page that list resources

### Feature
- Add documentation linkable to services
- Automatic cleanup of ghost images from documentation
- Add overcommitment ratio on resource group attributes
- Add announcements
- Token management
- Job template compliancy checking
- Add integrated backup support
- Add official Docker image


## v0.1.1

This is a **Patch** update of Squest:

### Fix
- All fields from AWX/Tower are available when admin accept a request
- Error in pie chart if Instance doesn't have a Service


## v0.1.0 - First release

This is a **Major** update of Squest:

### Features
- Service catalog
- Resource tracking
- Billing groups management
- User and group management
