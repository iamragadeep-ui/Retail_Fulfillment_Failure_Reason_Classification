import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from backend.app.observability.context import TraceContext
from backend.app.observability.database import get_connection


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """
    return datetime.now(timezone.utc).isoformat()


def safe_json(data: Any) -> Optional[str]:
    """
    Convert data to JSON text for SQLite storage.
    """
    if data is None:
        return None

    try:
        return json.dumps(data, default=str)
    except (TypeError, ValueError):
        return json.dumps({"value": str(data)})


def log_event(
    context: TraceContext,
    event: str,
    message: str,
    log_level: str = "INFO",
    service: str = "retail-fulfillment-api",
    environment: str = "development",
    endpoint: Optional[str] = None,
    agent_name: Optional[str] = None,
    tool_name: Optional[str] = None,
    model_name: Optional[str] = None,
    latency_ms: Optional[float] = None,
    status: Optional[str] = None,
    error_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Store a structured application log.
    """
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO application_logs (
                timestamp,
                log_level,
                service,
                environment,
                request_id,
                trace_id,
                session_id,
                agent_name,
                tool_name,
                model_name,
                endpoint,
                message,
                latency_ms,
                status,
                error_type,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                log_level.upper(),
                service,
                environment,
                context.request_id,
                context.trace_id,
                context.session_id,
                agent_name,
                tool_name,
                model_name,
                endpoint,
                message,
                latency_ms,
                status,
                error_type,
                safe_json(
                    {
                        "event": event,
                        **(metadata or {}),
                    }
                ),
            ),
        )

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def start_trace(
    context: TraceContext,
    service_name: str = "retail-fulfillment-api",
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Create the root trace record for a request.
    """
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR IGNORE INTO traces (
                timestamp,
                trace_id,
                request_id,
                session_id,
                user_id,
                conversation_id,
                agent_run_id,
                service_name,
                environment,
                start_time,
                status,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.trace_id,
                context.request_id,
                context.session_id,
                context.user_id,
                context.conversation_id,
                context.agent_run_id,
                service_name,
                environment,
                utc_now(),
                "RUNNING",
                safe_json(metadata),
            ),
        )

        connection.commit()
    finally:
        connection.close()


def end_trace(
    context: TraceContext,
    status: str,
    duration_ms: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Complete an existing trace.
    """
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE traces
            SET end_time = ?,
                duration_ms = ?,
                status = ?,
                metadata = COALESCE(?, metadata)
            WHERE trace_id = ?
            """,
            (
                utc_now(),
                duration_ms,
                status,
                safe_json(metadata),
                context.trace_id,
            ),
        )

        connection.commit()
    finally:
        connection.close()


def start_span(
    context: TraceContext,
    span_name: str,
    span_type: str,
    parent_span_id: Optional[str] = None,
    service_name: str = "retail-fulfillment-api",
    agent_name: Optional[str] = None,
    model_name: Optional[str] = None,
    tool_name: Optional[str] = None,
    input_data: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a trace span and return its span ID.
    """
    span_id = context.create_span_id()
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO spans (
                timestamp,
                trace_id,
                span_id,
                parent_span_id,
                span_name,
                span_type,
                service_name,
                agent_name,
                model_name,
                tool_name,
                start_time,
                status,
                input_data,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.trace_id,
                span_id,
                parent_span_id,
                span_name,
                span_type,
                service_name,
                agent_name,
                model_name,
                tool_name,
                utc_now(),
                "RUNNING",
                safe_json(input_data),
                safe_json(metadata),
            ),
        )

        connection.commit()
        context.current_span_id = span_id
        return span_id
    finally:
        connection.close()


def end_span(
    span_id: str,
    status: str,
    duration_ms: Optional[float] = None,
    output_data: Any = None,
    error: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Complete a trace span.
    """
    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE spans
            SET end_time = ?,
                duration_ms = ?,
                status = ?,
                output_data = ?,
                error = ?,
                metadata = COALESCE(?, metadata)
            WHERE span_id = ?
            """,
            (
                utc_now(),
                duration_ms,
                status,
                safe_json(output_data),
                error,
                safe_json(metadata),
                span_id,
            ),
        )

        connection.commit()
    finally:
        connection.close()


def record_guardrail_event(
    context: TraceContext,
    guardrail_name: str,
    guardrail_type: str,
    decision: str,
    reason: str,
    severity: str = "INFO",
    action_taken: Optional[str] = None,
    input_data: Any = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Record a guardrail decision.
    """
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO guardrail_events (
                timestamp,
                guardrail_name,
                guardrail_type,
                request_id,
                trace_id,
                input_data,
                decision,
                reason,
                severity,
                action_taken,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                guardrail_name,
                guardrail_type,
                context.request_id,
                context.trace_id,
                safe_json(input_data),
                decision,
                reason,
                severity,
                action_taken,
                safe_json(metadata),
            ),
        )

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_error(
    context: TraceContext,
    error_type: str,
    error_message: str,
    service: str = "retail-fulfillment-api",
    agent_name: Optional[str] = None,
    tool_name: Optional[str] = None,
    endpoint: Optional[str] = None,
    severity: str = "ERROR",
    environment: str = "development",
    stack_trace: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    """
    Record an application, agent, tool, RAG or API error.
    """
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO error_events (
                timestamp,
                request_id,
                trace_id,
                service,
                agent_name,
                tool_name,
                endpoint,
                error_type,
                error_message,
                stack_trace,
                severity,
                environment,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                service,
                agent_name,
                tool_name,
                endpoint,
                error_type,
                error_message,
                stack_trace,
                severity,
                environment,
                safe_json(metadata),
            ),
        )

        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def record_request_metric(
    context: TraceContext,
    endpoint: str,
    method: str,
    latency_ms: float,
    status: str,
    status_code: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    error_type: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO request_metrics (
                timestamp, request_id, trace_id, session_id, user_id,
                conversation_id, agent_run_id, endpoint, method,
                environment, start_time, end_time, latency_ms,
                status, status_code, error_type, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                context.session_id,
                context.user_id,
                context.conversation_id,
                context.agent_run_id,
                endpoint,
                method,
                environment,
                start_time,
                end_time or utc_now(),
                latency_ms,
                status,
                status_code,
                error_type,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_agent_metric(
    context: TraceContext,
    agent_name: str,
    duration_ms: float,
    status: str,
    number_of_steps: int = 0,
    number_of_llm_calls: int = 0,
    number_of_tool_calls: int = 0,
    number_of_retries: int = 0,
    planning_time_ms: Optional[float] = None,
    execution_time_ms: Optional[float] = None,
    human_approval_required: bool = False,
    human_approval_time_ms: Optional[float] = None,
    error: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO agent_metrics (
                timestamp, request_id, trace_id, agent_name, agent_run_id,
                duration_ms, status, number_of_steps, number_of_llm_calls,
                number_of_tool_calls, number_of_retries, planning_time_ms,
                execution_time_ms, human_approval_required,
                human_approval_time_ms, environment, error, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                agent_name,
                context.agent_run_id,
                duration_ms,
                status,
                number_of_steps,
                number_of_llm_calls,
                number_of_tool_calls,
                number_of_retries,
                planning_time_ms,
                execution_time_ms,
                int(human_approval_required),
                human_approval_time_ms,
                environment,
                error,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_tool_call(
    context: TraceContext,
    tool_name: str,
    latency_ms: float,
    status: str,
    tool_type: Optional[str] = None,
    agent_name: Optional[str] = None,
    input_data: Any = None,
    output_data: Any = None,
    retry_count: int = 0,
    error: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO tool_metrics (
                timestamp, request_id, trace_id, agent_run_id,
                tool_name, tool_type, agent_name, input_data,
                output_data, latency_ms, status, retry_count,
                error, environment, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                context.agent_run_id,
                tool_name,
                tool_type,
                agent_name,
                safe_json(input_data),
                safe_json(output_data),
                latency_ms,
                status,
                retry_count,
                error,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_rag_metric(
    context: TraceContext,
    query: str,
    documents_retrieved: int,
    retrieval_latency_ms: float,
    top_k: Optional[int] = None,
    rewritten_query: Optional[str] = None,
    top_similarity_score: Optional[float] = None,
    average_similarity_score: Optional[float] = None,
    context_tokens: Optional[int] = None,
    chunk_ids: Any = None,
    document_ids: Any = None,
    source_documents: Any = None,
    precision_at_k: Optional[float] = None,
    recall_at_k: Optional[float] = None,
    hit_rate: Optional[float] = None,
    mrr: Optional[float] = None,
    ndcg: Optional[float] = None,
    context_relevance: Optional[float] = None,
    answer_relevance: Optional[float] = None,
    faithfulness: Optional[float] = None,
    groundedness: Optional[float] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO rag_metrics (
                timestamp, request_id, trace_id, query, rewritten_query,
                documents_retrieved, top_k, retrieval_latency_ms,
                context_tokens, top_similarity_score,
                average_similarity_score, chunk_ids, document_ids,
                source_documents, precision_at_k, recall_at_k,
                hit_rate, mrr, ndcg, context_relevance,
                answer_relevance, faithfulness, groundedness,
                environment, metadata
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                query,
                rewritten_query,
                documents_retrieved,
                top_k,
                retrieval_latency_ms,
                context_tokens,
                top_similarity_score,
                average_similarity_score,
                safe_json(chunk_ids),
                safe_json(document_ids),
                safe_json(source_documents),
                precision_at_k,
                recall_at_k,
                hit_rate,
                mrr,
                ndcg,
                context_relevance,
                answer_relevance,
                faithfulness,
                groundedness,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_security_event(
    context: TraceContext,
    event_type: str,
    decision: str,
    reason: str,
    severity: str = "INFO",
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO security_events (
                timestamp, request_id, trace_id, event_type,
                severity, decision, reason, environment, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                event_type,
                severity,
                decision,
                reason,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_human_approval(
    context: TraceContext,
    approval_status: str,
    escalation_reason: Optional[str] = None,
    reviewer: Optional[str] = None,
    requested_at: Optional[str] = None,
    completed_at: Optional[str] = None,
    approval_duration_ms: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO human_approval_events (
                timestamp, request_id, trace_id, agent_run_id,
                approval_status, escalation_reason, reviewer,
                requested_at, completed_at, approval_duration_ms,
                metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                context.agent_run_id,
                approval_status,
                escalation_reason,
                reviewer,
                requested_at or utc_now(),
                completed_at,
                approval_duration_ms,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()

def record_llm_metric(
    context: TraceContext,
    model_name: str,
    provider: str,
    latency_ms: float,
    status: str,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    cached_tokens: Optional[int] = None,
    reasoning_tokens: Optional[int] = None,
    time_to_first_token_ms: Optional[float] = None,
    tokens_per_second: Optional[float] = None,
    retry_count: int = 0,
    estimated_cost: Optional[float] = None,
    prompt_version: Optional[str] = None,
    system_prompt_version: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    error: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO llm_metrics (
                timestamp, request_id, trace_id, agent_run_id,
                model_name, provider, prompt_version,
                system_prompt_version, temperature, max_tokens,
                prompt_tokens, completion_tokens, total_tokens,
                cached_tokens, reasoning_tokens, latency_ms,
                time_to_first_token_ms, tokens_per_second,
                retry_count, status, error, estimated_cost,
                environment, metadata
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                context.agent_run_id,
                model_name,
                provider,
                prompt_version,
                system_prompt_version,
                temperature,
                max_tokens,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                cached_tokens,
                reasoning_tokens,
                latency_ms,
                time_to_first_token_ms,
                tokens_per_second,
                retry_count,
                status,
                error,
                estimated_cost,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_token_metric(
    context: TraceContext,
    model_name: str,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    cached_tokens: Optional[int] = None,
    reasoning_tokens: Optional[int] = None,
    agent_name: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO token_metrics (
                timestamp, request_id, trace_id, agent_name,
                model_name, prompt_tokens, completion_tokens,
                cached_tokens, reasoning_tokens, total_tokens,
                environment, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                agent_name,
                model_name,
                prompt_tokens,
                completion_tokens,
                cached_tokens,
                reasoning_tokens,
                total_tokens,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def record_cost_metric(
    context: TraceContext,
    model_name: str,
    provider: str,
    estimated_cost: float,
    prompt_tokens: Optional[int] = None,
    completion_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
    agent_name: Optional[str] = None,
    environment: str = "development",
    metadata: Optional[Dict[str, Any]] = None,
) -> int:
    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO cost_metrics (
                timestamp, request_id, trace_id, session_id,
                user_id, agent_name, model_name, provider,
                prompt_tokens, completion_tokens, total_tokens,
                estimated_cost, environment, metadata
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                utc_now(),
                context.request_id,
                context.trace_id,
                context.session_id,
                context.user_id,
                agent_name,
                model_name,
                provider,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                estimated_cost,
                environment,
                safe_json(metadata),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()