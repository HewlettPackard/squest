# Squest

<p align="center">
    <img src="images/squest_full_logo.png">
</p>

The current deployment is based on Docker compose.

Pre-requisites:

- docker
- docker-compose

To run the application, execute the docker compose file
```bash
docker-compose up
```

Then connect with your web browser to [http://127.0.0.1:8080](http://127.0.0.1:8080)
The default admin account is `admin // admin`

The default export the port 8080. If you want to use the standard HTTP port 80, update the 
file `docker-compose.override.yml`.
```yaml
services:
  nginx:
    ports:
      - "80:8080"
```

More details are available in the "Installation" section of this documentation.
