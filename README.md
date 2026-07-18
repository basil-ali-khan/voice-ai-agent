# CareCloud Voice Patient Registration

A small, persistent patient-registration service designed for a Retell inbound voice agent. It uses FastAPI and SQLAlchemy with SQLite, runs locally or on an EC2 host through Docker Compose, and keeps HTTP, use-case, persistence, and voice-provider concerns separate.

Use fictional data only. This assessment implementation is **not HIPAA-ready**: it has no user authentication, audit trail, encryption-at-rest configuration, BAA, or production monitoring.

## Architecture

```text
Caller -> Retell inbound agent -> POST /voice/register-patient -> PatientService -> SQLite volume
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
# Fill in the values
python -m pytest -q
docker compose up --build
```

The API binds to `http://127.0.0.1:8000`. The deployed public health and docs endpoints are [health](https://rind-rebuff-elf.ngrok-free.dev/health) and [docs](https://rind-rebuff-elf.ngrok-free.dev/docs).

Never run `docker compose down -v`: the `-v` flag deletes the persistent patient database.

## Environment

Copy `.env.example` to `.env`; `.env` is intentionally ignored by Git.

| Variable | Required | Purpose |
| --- | --- | --- |
| `NGROK_DOMAIN` | Yes for the public tunnel | Reserved ngrok domain, without `https://`. |
| `NGROK_AUTHTOKEN` | Yes for the public tunnel | Authenticates the ngrok container. |
| `RETELL_API_KEY` | No in the current evaluation mode | Reserved for HMAC verification when signed webhook mode is restored. |
| `LOG_LEVEL` | No | Application logging level; defaults to `INFO`. |

Docker Compose supplies `DATABASE_URL=sqlite:////data/patients.db` and mounts that path on the `patient_data` named volume. For bare local API development, set `DATABASE_URL=sqlite:///./data/patients.db`.

## Live Demo

- Voice agent browser test: [Open the Retell agent](https://agent.retellai.com/orb/agent_9c87894631095482713bd61d1b?token=ffab042c41005ac1c77e6305d04b896d).
- Public API base URL: `https://rind-rebuff-elf.ngrok-free.dev`.

## Retell Configuration

1. Create an inbound Retell agent and paste the prompt from `app/voice/prompt.py`.
2. Add a POST custom function named `register_patient` using `config/retell-register-patient.schema.json`.
3. Set its URL to `https://rind-rebuff-elf.ngrok-free.dev/voice/register-patient` and use Retell's normal payload envelope (not `args` only).
4. Allow the agent to speak after function execution, bind a purchased U.S. number, and add Retell's built-in end-call tool.
5. Place a fictional-data test call that includes an invalid value, a correction, optional-field decline, full readback, and explicit confirmation.

The current evaluation deployment accepts the normal Retell envelope and a flat payload variant used by the active voice-provider integration. Signature validation is intentionally bypassed in `app/voice/routes.py` so the deployed tunnel can receive these tool calls. Do not expose this mode beyond the assessment: restore `X-Retell-Signature` HMAC-SHA256 verification with `RETELL_API_KEY` before any broader deployment.

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


