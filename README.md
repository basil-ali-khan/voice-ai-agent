# CareCloud Voice Patient Registration

A small, persistent patient-registration service designed for a Retell inbound voice agent. It uses FastAPI and SQLAlchemy with SQLite, runs locally or on an EC2 host through Docker Compose, and keeps HTTP, use-case, persistence, and voice-provider concerns separate.

Use fictional data only. This assessment implementation is **not HIPAA-ready**: it has no user authentication, audit trail, encryption-at-rest configuration, BAA, or production monitoring.

## Architecture

```text
Caller -> Retell inbound agent -> signed POST /voice/register-patient -> PatientService -> SQLite volume
Reviewer/API client ----------------> REST /patients ------------------> PatientService -> SQLite volume
```

- `app/patients/routes.py`: thin REST adapter with the required envelopes.
- `app/patients/service.py`: creation, reads, partial updates, soft delete, and Retell retry idempotency.
- `app/patients/repository.py`: the only layer that performs SQLAlchemy queries.
- `app/voice/routes.py`: raw-body Retell webhook verification and tool adapter.
- `app/voice/prompt.py` and `config/retell-register-patient.schema.json`: version-controlled dashboard configuration.

SQLite is appropriate for this time-boxed assessment and is mounted on the Compose named volume, so it survives a container recreation. Production follow-ups are PostgreSQL, Alembic migrations, authentication, structured redacted audit logging, and an async queue for provider retries.

## Local Setup

```bash
cp .env.example .env
# Fill in Retell and ngrok values. For bare local API development, optionally add:
# DATABASE_URL=sqlite:///./data/patients.db
/home/basilkhan/carecloud/.venv/bin/python -m pytest -q
docker compose up --build
```

The API binds to `http://127.0.0.1:8000`. With the configured stable ngrok domain, public health and docs are at `https://YOUR_NGROK_DOMAIN/health` and `https://YOUR_NGROK_DOMAIN/docs`.

Never run `docker compose down -v`: the `-v` flag deletes the persistent patient database.

## Retell Configuration

1. Create an inbound Retell agent and paste the prompt from `app/voice/prompt.py`.
2. Add a POST custom function named `register_patient` using `config/retell-register-patient.schema.json`.
3. Set its URL to `https://YOUR_NGROK_DOMAIN/voice/register-patient`, use the normal Retell payload envelope (not `args` only), and configure the Retell signing secret/API key as `RETELL_API_KEY`.
4. Allow the agent to speak after function execution, bind a purchased U.S. number, and add Retell's built-in end-call tool.
5. Place a fictional-data test call that includes an invalid value, a correction, optional-field decline, full readback, and explicit confirmation.

The webhook accepts an HMAC-SHA256 signature of the raw request body in `X-Retell-Signature` (hex or base64). Confirm Retell's current signing format in the dashboard/provider documentation before production use.

## API

All REST responses use `{ "data": ..., "error": null }` on success and `{ "data": null, "error": { ... } }` on domain or validation errors.

```bash
curl -X POST http://127.0.0.1:8000/patients \
  -H 'Content-Type: application/json' \
  -d '{"first_name":"Jane","last_name":"Doe","date_of_birth":"02/14/1988","sex":"Female","phone_number":"415-555-2671","address_line_1":"10 Market Street","city":"San Francisco","state":"CA","zip_code":"94105"}'

curl 'http://127.0.0.1:8000/patients?last_name=Doe'
```

Endpoints are `GET /patients`, filtered `GET /patients`, `GET /patients/{patient_id}`, `POST /patients`, partial `PUT /patients/{patient_id}`, soft `DELETE /patients/{patient_id}`, and `GET /health`.

## EC2 Deployment

Provision an Ubuntu EC2 instance, install Docker Engine plus the Compose plugin, then clone the repository and create a private `.env` from `.env.example` with `chmod 600 .env`.

```bash
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 api ngrok
```

Only SSH needs an inbound EC2 security-group rule because ngrok makes the outbound tunnel. Keep the EBS root volume on instance termination and use a reserved ngrok domain so the Retell URL remains stable. The Compose restart policies restore services after a reboot.

## Verification

```bash
/home/basilkhan/carecloud/.venv/bin/python -m pytest -q
curl http://127.0.0.1:8000/health
```

The tests cover validation, create/read/filter/update/soft-delete, SQLite persistence across requests, Retell signature rejection, and Retell call-ID idempotency. A real phone number, Retell account, EC2 host, and ngrok domain must be provisioned outside source control and entered above before review.
