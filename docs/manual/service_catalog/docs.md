# Docs

Docs section allow administrators to create and link documentation to Squest services or operations.

Documentation are writen with Markdown syntax.

!!!note

    Docs linked to a service or an operation are not listed in the global doc list from the sidebar menu.

## Linked to services

When linked to one or more service, the documentation is shown in each "instance detail" page that correspond to the type of selected services.

Jinja templating is supported with the `instance` as context.

E.g:
```
You instance is available at {{ instance.spec.dns }}
```

## Linked to operations

When linked to one or more operation, the documentation is shown during the survey of the selected operations.

Like for services, Jinja templating is supported with the `instance` as context.

!!!note

    No instance context is injected on "create" operations as the instance doesn't exist yet at this stage

## When filter

When filter can be applied to only show the documentation when some criteria based on the instance are respected.

E.g:
```
instance.user_spec.cluster_hostname == "cluster-test.lab.local"
```
