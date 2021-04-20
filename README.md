[![Gitter](https://badges.gitter.im/gitterHQ/gitter.svg)](https://gitter.im/HewlettPackard/squest)

# Squest - A service request portal based on Ansible Tower

Squest is a Web portal that allow to expose Tower based automation as a service.

If you want an idea of what you can do with Squest, click on the image below
[![DEMO](https://img.youtube.com/vi/ZfTjS1t7X74/maxresdefault.jpg)](https://www.youtube.com/watch?v=ZfTjS1t7X74)

## Deploy a testing environment

Pre-requisites:

- Docker
- Docker-compose

To test the application, run the full env docker compose file
```bash
docker-compose -f dev-env.docker-compose.yml -f full-env.docker-compose.yml up
```

Then connect with your web browser to [http://127.0.0.1:8000](http://127.0.0.1:8000)
The default admin account is `admin // admin`

## Documentation

- [Setup a development environment](docs/dev-env.md)
- [Settings](docs/settings.md)

## Links

- [Chat on Gitter](https://gitter.im/HewlettPackard/squest)
