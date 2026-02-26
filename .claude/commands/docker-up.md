Start all Docker services using docker-compose.

For full deployment (prod + test + RDF server + proxy):
```bash
docker compose up -d
```

For local development (RDF server + proxy only):
```bash
cd local-compose && docker compose up -d
```

Check service status with: `docker compose ps`
Check logs with: `docker compose logs -f <service-name>`
