# Enterprise AI Ingestion Service

This is the Stage 1 local-only, health-only service skeleton. It intentionally does not receive data, persist data, connect to platform backends, or use credentials.

## Local health check

```powershell
python app.py
Invoke-WebRequest http://127.0.0.1:8080/health -UseBasicParsing
```

## Docker Compose validation

```powershell
docker compose -f compose.yaml config
```

The Compose file binds the service only to loopback. Running the container is outside this first task's minimum verification requirement.
