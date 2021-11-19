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
