# Deploy Squest

The current deployment is based on Docker compose for testing the tool.

Pre-requisites:

- docker
- docker-compose

To test the application, run the full env docker compose file
```bash
docker-compose -f dev-env.docker-compose.yml -f full-env.docker-compose.yml up
```

Then connect with your web browser to [http://127.0.0.1:8000](http://127.0.0.1:8000)
The default admin account is `admin // admin`
