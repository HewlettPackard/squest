<p align="center">
    <img src="docs/images/squest_full_logo.png">
</p>

<h3 align="center">Self service portal on top of Red Hat Ansible Automation Platform(RHAAP)/AWX (formerly known as Ansible Tower)</h3>

<p align="center">
<a href="https://hewlettpackard.github.io/squest/latest"><img alt="Doc" src="https://img.shields.io/badge/read-documentation-1abc9c?style=flat-square"></a>
<a href="https://gitter.im/HewlettPackard/squest"><img alt="Gitter" src="https://img.shields.io/gitter/room/HewlettPackard/squest?color=1abc9c&style=flat-square"></a>
<a href= "https://coveralls.io/github/HewlettPackard/squest"><img alt="Coveralls" src="https://img.shields.io/coveralls/github/HewlettPackard/squest?style=flat-square"></a>
<a href="https://github.com/HewlettPackard/squest/releases/latest"><img alt="GitHub release (latest)" src="https://img.shields.io/github/v/release/HewlettPackard/squest?style=flat-square"></a>
<a href="https://github.com/HewlettPackard/squest/blob/master/LICENSE.md"><img alt="License" src="https://img.shields.io/github/license/HewlettPackard/squest?style=flat-square"></a>
<img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/HewlettPackard/squest?style=flat-square">
</p>

Squest is a framework that allow you to expose an **Everything-as-a-Service** web portal. 

Exposed services in Squest are not hard coded. A service is actually a pointer to your automation in the backend engine Red Hat Ansible Automation Platform(RHAAP)/AWX (formerly known as Ansible Tower). 
It means everything, as long as it exists as an automation script, can be exposed as a service. **The only limit is your own capability of automation**.

More than a fire and forget tool, Squest can store in its database each deployed instance of services it has provisioned so you can attach to them more automation that allow 
your users to **manage the lifecycle** of their resources. 
Each operation corresponds to another link to an automation process in the backend. This allows to make end users more autonomous and free you from time spent in support 
and object update management.

If you want an idea of what you can do with Squest, click on the image below.

[![DEMO](https://i3.ytimg.com/vi/mQnNkSMMXwg/maxresdefault.jpg)](https://youtu.be/mQnNkSMMXwg)

## Features

- Service catalog:
  - Add services to your catalog based on job templates you have in your Red Hat Ansible Automation Platform/AWX instance
  - Manage requests for services (review, update, approve and process)
  - Manage lifecycle of each instance of a service
  - Integrated or external support page
  - Link billing group and track resource consumption
  - Quota
  - Auto approval
  - Multiple layer approval configuration
  - Custom on-boarding documentation
  - Teams to share resources
- Reserved resource tracking
  - Create generic objects
  - Link objects to compose layers of your infrastructure (Physical servers, Virtualization, Containers, Projects, Tenants,...)
  - Visualize pool of resource of what you have provided (CPU, vCPU, memory, disk...)
  - Check consumptions before approving new requests
  - Graph representation of resource layers
  
## Links

:blue_book: [Documentation](https://hewlettpackard.github.io/squest/latest)<br/>
:speech_balloon: [Chat on Gitter](https://gitter.im/HewlettPackard/squest)<br/>
:movie_camera: Demo video
- [Service catalog](https://youtu.be/mQnNkSMMXwg)
- [Resource tracking](https://www.youtube.com/watch?v=KxJbYxnR5Ug)

> If you like the project, star it ⭐, it motivates us a lot 🙂
