# Architecture Notes

The application uses a multi-agent workflow to process retail fulfillment failures from intake to final decision.

## Main layers

- Frontend dashboard in Next.js for operations teams.
- API layer in FastAPI to receive and persist case requests.
- Workflow layer in LangGraph for orchestration.
- Agent layer for specialized investigation and validation.
- Policy/RAG layer for evidence retrieval.
- Data layer with SQLAlchemy models and SQLite/PostgreSQL compatibility.

## Key decision logic

- Payment failure or decline before fulfillment begins leads to PAYMENT_FAILURE.
- Inventory shortage or unavailability leads to INVENTORY_SHORTAGE.
- Warehouse backlog leads to WAREHOUSE_PROCESSING_DELAY.
- Carrier delay after successful upstream execution leads to CARRIER_DELAY.
- Unknown, missing, or contradictory evidence leads to UNKNOWN_REQUIRES_REVIEW and HUMAN_REVIEW.
