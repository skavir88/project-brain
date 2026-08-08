# Enterprise AI Ingestion Service

This is a Stage 1 local-only synthetic ingestion and structural-validation slice. It does not persist records, connect to platform backends, or use credentials.

## Local health check

```powershell
python app.py
Invoke-WebRequest http://127.0.0.1:8080/health -UseBasicParsing
```

## Synthetic intake contract

`POST /v1/records` accepts only this minimal JSON structure:

```json
{
  "source_id": "synthetic-source",
  "record_id": "synthetic-record-001",
  "payload": {"example": true}
}
```

The service returns `202` for a first structurally valid request and `422` with machine-readable validation errors for invalid requests. For accepted requests it trims surrounding whitespace from `source_id` and `record_id`, then returns a SHA-256 fingerprint of a stable JSON representation of that canonical record.

For this local demonstration only, the process keeps accepted fingerprints in memory. A repeated equivalent fingerprint returns `409` with `duplicate=true`. This state is cleared whenever the service restarts and is never written to disk, a Docker volume, or an external backend.

## Docker Compose

```powershell
docker compose -f compose.yaml config
```

The Compose file binds the service only to loopback. It is intended solely for local verification.
