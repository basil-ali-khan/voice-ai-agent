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

# CareCloud Voice Patient Registration

CareCloud is a conversational patient-registration experience that collects demographics naturally, confirms the complete record with the caller, and persists the confirmed registration for retrieval through a REST API.

**Use fictional data only.**

## Try It

1. [Open the live voice agent](https://agent.retellai.com/orb/agent_9c87894631095482713bd61d1b?token=ffab042c41005ac1c77e6305d04b896d).
2. Register a fictional patient. The agent collects required demographics in any order, offers optional information, reads the complete record back, and saves only after explicit confirmation.
3. Inspect the persisted registration at the [live API documentation](https://rind-rebuff-elf.ngrok-free.dev/docs) or query [the patient list](https://rind-rebuff-elf.ngrok-free.dev/patients).

The public health check is available at [https://rind-rebuff-elf.ngrok-free.dev/health](https://rind-rebuff-elf.ngrok-free.dev/health).
The free ngrok plan displays a one-time browser interstitial; select **Visit Site** to continue to the API. It does not affect voice-provider webhook requests.

For a representative evaluation, provide an invalid value, correct a field, decline the optional group, and confirm the final readback. A registration is only created after that confirmation.

## What It Delivers

- Natural-language voice intake for required U.S. patient demographics.
- Server-side validation of dates, names, phone numbers, states, ZIP codes, and email addresses.
- Optional insurance, emergency-contact, and preferred-language collection.
- Confirmation-before-save and retry-safe voice tool handling.
- Persistent registrations with list, filter, read, partial update, and soft-delete REST operations.

## Architecture

```text
Caller -> Retell voice agent -> POST /voice/register-patient -> Patient service -> SQLite volume
Reviewer/API client ----------> REST /patients ------------> Patient service -> SQLite volume
```

FastAPI provides the HTTP adapters, SQLAlchemy owns persistence, and SQLite is mounted on a Docker Compose named volume. This keeps registrations intact across container recreation while keeping the assessment deployment small and easy to run.

The voice prompt and custom-function schema are version-controlled in [app/voice/prompt.py](app/voice/prompt.py) and [config/retell-register-patient.schema.json](config/retell-register-patient.schema.json). The HTTP, service, and repository layers remain separate so voice-provider behavior does not leak into patient persistence.

## API

All API responses use a consistent envelope: `{ "data": ..., "error": null }` for successful requests and `{ "data": null, "error": { ... } }` for domain or validation errors.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/patients` | List active patients; filter by `last_name`, `date_of_birth`, or `phone_number`. |
| `GET` | `/patients/{patient_id}` | Retrieve one active patient. |
| `POST` | `/patients` | Create a patient registration. |
| `PUT` | `/patients/{patient_id}` | Partially update a patient. |
| `DELETE` | `/patients/{patient_id}` | Soft-delete a patient. |
| `GET` | `/health` | Confirm API and database availability. |

Example request against the live deployment:

```bash
curl 'https://rind-rebuff-elf.ngrok-free.dev/patients?last_name=Doe'
```

## Run Locally

Requirements: Docker Engine with the Compose plugin. For local source-level testing, use Python 3.12 or newer.

```bash
cp .env.example .env
# Set NGROK_DOMAIN and NGROK_AUTHTOKEN in .env for a public voice webhook.
docker compose up --build
```

The local API is bound to `http://127.0.0.1:8000`; ngrok exposes it publicly when configured. Compose sets `DATABASE_URL=sqlite:////data/patients.db` and persists it in the `patient_data` named volume.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/python -m pytest -q
```

Use `docker compose down` to stop local services. Do not add `-v` unless intentionally deleting the local patient database.

## Configuration

Copy `.env.example` to `.env`; it is excluded from source control.

| Variable | Purpose |
| --- | --- |
| `NGROK_DOMAIN` | Reserved ngrok domain, without `https://`. |
| `NGROK_AUTHTOKEN` | Authenticates the ngrok tunnel. |
| `RETELL_API_KEY` | Reserved for future signed-webhook verification. |
| `LOG_LEVEL` | Application log level; defaults to `INFO`. |

For a hosted deployment, run the same Compose stack on the host with a private `.env`. The API listens only on loopback; ngrok creates the outbound public tunnel. Both services use `unless-stopped` restart policies.

## Assessment Scope

This is a time-boxed assessment implementation, not a HIPAA-ready product. It intentionally does not include authentication, audit logging, encryption-at-rest configuration, a BAA, production monitoring, or webhook-signature verification. A production implementation would use PostgreSQL with migrations, authenticated access, redacted audit logs, provider webhook verification, and durable asynchronous retry handling.


