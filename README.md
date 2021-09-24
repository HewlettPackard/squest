<p align="center">
    <img src="docs/images/squest_full_logo.png">
</p>

# Squest - Request portal on top of Ansible Tower/AWX

[![Gitter](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/HewlettPackard/squest)

Squest is a Web portal that allow to expose Tower/AWX based automation as a service.

Main features:

- Service catalog:
  - Add services to your catalog based on job template you have in your Tower/AWX instance
  - Create requests for service
  - Review and approve requests
  - Provision a service
  - Manage lifecycle of each instance of a service
  - Support page
- Reserved resource tracking
  - Create generic objects
  - Link objects to compose layers of your infrastructure (Physical servers, Virtualization, Containers, Projects, Tenants,...)
  - Visualize pool of resource of what you have provided (CPU, vCPU, memory, disk...)
  - Check consumptions before approving new requests
- Billing groups 
  - Group users per billing group
  - Get charts and stats about resource consumption per group

If you want an idea of what you can do with Squest, click on the image below

[![DEMO](https://img.youtube.com/vi/ZfTjS1t7X74/maxresdefault.jpg)](https://www.youtube.com/watch?v=ZfTjS1t7X74)

## Links

- [Documentation](https://hewlettpackard.github.io/squest/latest)
- [Chat on Gitter](https://gitter.im/HewlettPackard/squest)
- Squest demo video:
  - [Service catalog](https://www.youtube.com/watch?v=ZfTjS1t7X74)
  - [Resource tracking](https://www.youtube.com/watch?v=KxJbYxnR5Ug)
