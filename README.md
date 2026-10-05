# Retail Fulfillment Failure Reason Classification

A production-style demo that combines a multi-agent workflow, LangGraph orchestration, policy-aware evidence retrieval, and a dashboard for retail fulfillment failure investigation.

## Final architecture overview

### Runtime architecture

- Frontend: Next.js + TypeScript + Tailwind UI for the operations dashboard and case analysis form.
- Backend: FastAPI with SQLAlchemy models and REST endpoints.
- Workflow: LangGraph stateful orchestration for supervisor, planner, router, specialized agents, validator, and decision output.
- AI layer: Python-based agent logic with deterministic mock operational data and a lightweight policy/RAG retrieval service.
- Data: SQLite by default for local development, with PostgreSQL-compatible configuration.

### Multi-agent design

The system orchestrates a supervisor-driven workflow that investigates the case using specialized agents for order, inventory, payment, warehouse, carrier, and address validation. The workflow then classifies the root cause, applies critic and reviewer checks, and sends insufficient evidence cases to human review.

## Repository structure

- `agentic_ai/`: workflow, prompts, state, security, tools, and mock operational services
- `backend/`: FastAPI app, database abstractions, and API models
- `docs/`: architecture notes
- `deployment/`: deployment guidance
- `evaluation/`: sample evaluation data
- `frontend/`: Next.js dashboard and analysis UI
- `tests/`: API and workflow verification tests

## Implementation plan

1. Establish the project skeleton and configuration.
2. Implement the Python backend and SQLAlchemy models.
3. Build deterministic mock retail services and policy retrieval.
4. Add workflow orchestration and classification logic.
5. Create the Next.js dashboard and case analysis flow.
6. Verify the demo scenarios and run automated tests.

## Demo scenario

The first demo scenario is:

- Order ID: ORD123
- Payment: SUCCESS
- Inventory: AVAILABLE
- Warehouse: DISPATCHED
- Carrier: DELAYED

Expected result:

- Failure reason: `CARRIER_DELAY`
- Decision: `AUTO_CLASSIFIED`

## Local setup

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

Start backend:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start frontend:

```bash
cd frontend
npm run dev
```

Open the browser to http://localhost:3000.

## Tests

```bash
source .venv/bin/activate
pytest -q
```

## Deployment

- Frontend: deploy the `frontend` app to Vercel with `NEXT_PUBLIC_API_URL` set to the backend URL.
- Backend: host on any Python-capable platform or container runtime with the production database URL configured.

## Notes

This is a functional demonstration of the requested enterprise architecture, using deterministic mock services so the workflow can be exercised without external providers.
