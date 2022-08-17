# 1.7.3 2022-08-31

## Enhancement

- Create instance from API return full serializer
- Instance filtered by multiple choice instead of text in UI
- Link to access instances by service from home page in UI
- Service catalog forms with data live search in UI
- Filter for attribute definitions in API

## Fix

- Request operation from API return the new request 
- Support choices as list in AWX survey


# 1.7.2 2022-08-04

## Feature

- Custom links on instance detail page

## Enhancement

- Custom threshold color on resource pool and quota
- Add description documentation to services and portfolios

## Fix

- Date submitted was updated on each save
- Hide disabled services from homepage
- Hide admin only create operations for end users

# 1.7.1 2022-07-21

## Enhancement

- Date format can be set for all date from the settings
- Merge operation name and operation color type

## Fix

- Fix breadcrumbs links in notification page
- Link to the doc now target the correct current version of the running squest instance
- fill_in_survey flag was saved as a string when created from the API
- Fix maintenance mode was not working when used from the API


# 1.7.0 2022-07-18

## Internal

- Bump python version to 3.10

## Fix

- Global hook was not working
- Fix ajax call when synchronizing job template. Number of template was not updated

## Feature

- Notification filters
- Extra vars on Tower server, service and operation
- Add maintenance mode

## Enhancement

- Operations can be limited to administrators only

# 1.6.1 2022-07-04

## Fix

- Pagination navigation was not working with https scheme

## Feature

- Add support of external tool as support URL

# 1.6.0 2022-06-30

## Breaking changes

- API: Pagination added to all GET list of objects

## Fix

- API: ID was not given when new request created
- Format issue with fill in survey
- instance_name variable can be used in the tower survey 

## Enhancement

- Swagger page support bearer auth
- Send email when support is closed
- show specs on accept/review page
- Add pending request for each service in the admin dashboard
- Save tags in session

## Feature

- API: Add filters (filter by exact name in API vs contains in UI)
- Default API admin token can be added to the settings
- Python script based validator for form field
- Approval workflow
- Bulk delete for Instances
- Allow several create operations
- Portfolio

# 1.5.2 2022-04-04

## Fix

- Remove hardcoded url in email template
- Mails were not send to user after receiving a new message
- Right part of the graph was not clickable with large graph

## Enhancement

- Instance serializer used User serializer instead of id
- Supports list can be filtered by Service
- Global hook can be linked to an operation
- Instance can be deleted by an admin from API

## Feature

- Message can be edited
- Operations can be disabled

# 1.5.1 2022-03-01

## Fix

- Calculate total resources of a resource group was not called when creating a resource from the API

## Enhancement

- Added a button to re calculate total of a resource group

# 1.5.0 2022-02-28

## Breaking changes

- API: Service and Operation creation split.

## Fix

- Patch a resource without "text_attribute" field filled.
- Fix Squest logo not shown in maintenance page for non-root URLs.
- Resource group and Resource pool with the same name was not displayed in the graph.
- Add missing swagger doc for operation survey.

## Enhancement

- Performance: cache + calculation + asynchronous call.
- API : Create a Service return full Service Serializer.
- Catch all Tower exceptions when processing a request.
- Remove role binding from team details.
- Global hook can be linked to a service.
- Admin can set to blank a non required field with default value in Tower survey.
- Split Service and Operation form.
- API: Split Service and Operation serializer.

## Feature

- Jinja template on survey default field value.

# 1.4.1 2022-02-02

## Breaking changes

- API: Split between admin survey and user survey

## Fix

- Fix Celery wait timeout when starting Docker compose

## Enhancement

- Admin accept request form can now update billing group and instance name
- Add date available on successfully processed instance
- Custom 404 page
- Bulk delete on request page as admin
- Added delete button on resource details page
- Hide admin filled fields from the end user survey

## Feature

- API: request state machine management
- Added "user spec" field to instance. Spec are now only visible by admin.

# 1.4.0 2022-01-20

## Breaking changes

- API: Move job template URL behind Tower URLs

## Fix

- Fix collect static in Docker image
- Service image upload on edit service
- Fix global hooks execution
- Instance details page was not displayed when the SPOC was not defined
- Several fix in UI
- Fix email notifications
- Fix team deletion. Old role bindings are deleted

## Enhancement

- Auto deletion of resource from resource group when instance from service catalog is deleted
- Celery containers wait for Squest app to be ready before starting
- Admin can manually edit requests
- End user can access request details page
- Comment field for each request
- Instance list: add some filter
- Request details page for end users

## Feature

- Resource quota per billing group
- Prometheus metrics
- Support list for end users
- API: Job Template sync

# v1.3.1 2021-12-20

## Fix
- Collect static are not executed during the docker image build anymore to prevent caching
- Email sent when request execution fail
- Migration of old permission after creating Teams
- Fix job template sync when multiple tower/awx instance are declared
- Fix swagger generated page on POST /service/<id>/request. Fileds w

## Enhancement
- Remove metrics and graph from the main dashboard to speed up the loading
- Add squest host to metadata sent to Tower
- UI: refactoring of the resource group list page
- Add billing group to instance list filter

## Feature
- Bulk delete on resources

# v1.3 2021-12-15

## Fix
- Support and instance in sidebar are no more highlighted together
- Total resource was empty in resource group list
- Email notification for comment on request and support message

## Enhancement
-  Filter hidden by default in graph

## Feature
- Team management to share instances
- API - get resource/resource group/resource pool by name

# v1.2.1 2021-11-19

## Fix
- Resource pool consumption is now updated after resource deletion
- Fix resource group save form
- Fix resource pool calculation executed when adding/deleting resources

## Enhancement
- load git module only once in settings
- remove useless calculation call
- enhance test execution speed
- add scroll bar in resource list table
- filters moved into a sidebar

# v1.2 2021-11-15

## Fix
- Update permissions when SPOC is changed from instance
- Fix display error in resource pool list
- Fix default value when integer is used in Tower survey

## Enhancement
- Re-process failed requests
- Add a filter in resource tracker resource list
- Graph perf enhancement

## Feature
- User and billing group API
- User can disable email notification

# v1.1 2021-10-22

## Breaking changes
- Replace API token key work "Token" by "Bearer"

## Fix
- Fix empty job template survey
- Fix attribute text display in some form
- Fix link to doc in instance pages

## Enhancement
- Add a button to collapse filters in the graph view

## Feature
- Add functional testing playbooks
- API: CRUD on resource group
- API: CRUD on resource pool
- add static HTML maintenance page
- API: CRUD on Request
- API: CRUD on Service
- API: CRUD on Operation
- Show GIT sha in the footer

# v1.0 2021-09-30

## Fix
- Fix LDAP TLS support with self-signed certificates
- Fix email host url from settings

## Enhancement
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

## Feature
- add documentation linkable to services
- automatic cleanup of ghost images from documentation 
- add overcommitment ratio on resource group attributes
- add announcements
- Token management
- Job template compliancy checking
- add integrated backup support
- add official Docker image

# v1.1 2021-08-11

- Fix: #114 Fix process request

# v0.1 2021-08-03

First release
