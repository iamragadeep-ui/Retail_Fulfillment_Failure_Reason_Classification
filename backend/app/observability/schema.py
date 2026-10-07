from backend.app.observability.database import get_connection


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS application_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    log_level TEXT NOT NULL,
    service TEXT,
    environment TEXT,
    request_id TEXT,
    trace_id TEXT,
    session_id TEXT,
    agent_name TEXT,
    tool_name TEXT,
    model_name TEXT,
    endpoint TEXT,
    message TEXT NOT NULL,
    latency_ms REAL,
    status TEXT,
    error_type TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS request_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT NOT NULL,
    trace_id TEXT NOT NULL,
    session_id TEXT,
    user_id TEXT,
    conversation_id TEXT,
    agent_run_id TEXT,
    endpoint TEXT,
    method TEXT,
    environment TEXT,
    start_time DATETIME,
    end_time DATETIME,
    latency_ms REAL,
    status TEXT,
    status_code INTEGER,
    error_type TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trace_id TEXT NOT NULL UNIQUE,
    request_id TEXT,
    session_id TEXT,
    user_id TEXT,
    conversation_id TEXT,
    agent_run_id TEXT,
    service_name TEXT,
    environment TEXT,
    start_time DATETIME,
    end_time DATETIME,
    duration_ms REAL,
    status TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS spans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    trace_id TEXT NOT NULL,
    span_id TEXT NOT NULL UNIQUE,
    parent_span_id TEXT,
    span_name TEXT NOT NULL,
    span_type TEXT,
    service_name TEXT,
    agent_name TEXT,
    model_name TEXT,
    tool_name TEXT,
    start_time DATETIME,
    end_time DATETIME,
    duration_ms REAL,
    status TEXT,
    input_data TEXT,
    output_data TEXT,
    error TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS guardrail_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    guardrail_name TEXT NOT NULL,
    guardrail_type TEXT,
    request_id TEXT,
    trace_id TEXT,
    input_data TEXT,
    decision TEXT,
    reason TEXT,
    severity TEXT,
    action_taken TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS human_approval_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    agent_run_id TEXT,
    approval_status TEXT,
    escalation_reason TEXT,
    reviewer TEXT,
    requested_at DATETIME,
    completed_at DATETIME,
    approval_duration_ms REAL,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS error_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    service TEXT,
    agent_name TEXT,
    tool_name TEXT,
    endpoint TEXT,
    error_type TEXT,
    error_message TEXT,
    stack_trace TEXT,
    severity TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS security_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    event_type TEXT NOT NULL,
    severity TEXT,
    decision TEXT,
    reason TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS system_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    environment TEXT,
    cpu_usage REAL,
    memory_usage REAL,
    disk_usage REAL,
    disk_io_read REAL,
    disk_io_write REAL,
    network_io_sent REAL,
    network_io_received REAL,
    active_connections INTEGER,
    request_queue INTEGER,
    process_memory REAL,
    process_cpu REAL,
    thread_count INTEGER,
    database_connections INTEGER,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS llm_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    agent_run_id TEXT,
    model_name TEXT,
    provider TEXT,
    prompt_version TEXT,
    system_prompt_version TEXT,
    temperature REAL,
    max_tokens INTEGER,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cached_tokens INTEGER,
    reasoning_tokens INTEGER,
    latency_ms REAL,
    time_to_first_token_ms REAL,
    tokens_per_second REAL,
    retry_count INTEGER DEFAULT 0,
    status TEXT,
    error TEXT,
    estimated_cost REAL,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS agent_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    agent_name TEXT,
    agent_run_id TEXT,
    start_time DATETIME,
    end_time DATETIME,
    duration_ms REAL,
    status TEXT,
    number_of_steps INTEGER,
    number_of_llm_calls INTEGER,
    number_of_tool_calls INTEGER,
    number_of_retries INTEGER,
    planning_time_ms REAL,
    execution_time_ms REAL,
    human_approval_required INTEGER DEFAULT 0,
    human_approval_time_ms REAL,
    environment TEXT,
    error TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS tool_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    agent_run_id TEXT,
    tool_name TEXT,
    tool_type TEXT,
    agent_name TEXT,
    input_data TEXT,
    output_data TEXT,
    start_time DATETIME,
    end_time DATETIME,
    latency_ms REAL,
    status TEXT,
    retry_count INTEGER DEFAULT 0,
    error TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS rag_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    query TEXT,
    rewritten_query TEXT,
    documents_retrieved INTEGER,
    top_k INTEGER,
    retrieval_latency_ms REAL,
    vector_search_latency_ms REAL,
    reranking_latency_ms REAL,
    context_size INTEGER,
    context_tokens INTEGER,
    similarity_score REAL,
    top_similarity_score REAL,
    average_similarity_score REAL,
    chunk_ids TEXT,
    document_ids TEXT,
    source_documents TEXT,
    precision_at_k REAL,
    recall_at_k REAL,
    hit_rate REAL,
    mrr REAL,
    ndcg REAL,
    context_relevance REAL,
    answer_relevance REAL,
    faithfulness REAL,
    groundedness REAL,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS model_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    metric_name TEXT,
    baseline_value REAL,
    current_value REAL,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS data_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    feature_name TEXT,
    psi REAL,
    ks_statistic REAL,
    js_divergence REAL,
    wasserstein_distance REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS prediction_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    prediction_type TEXT,
    baseline_distribution TEXT,
    current_distribution TEXT,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS concept_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    accuracy REAL,
    precision_score REAL,
    recall_score REAL,
    f1_score REAL,
    roc_auc REAL,
    mae REAL,
    rmse REAL,
    baseline_score REAL,
    current_score REAL,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS prompt_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    prompt_length INTEGER,
    prompt_tokens INTEGER,
    system_prompt_version TEXT,
    prompt_template_version TEXT,
    instruction_changes TEXT,
    embedding_similarity REAL,
    prompt_failure_rate REAL,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS retrieval_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    average_similarity_score REAL,
    documents_retrieved INTEGER,
    document_distribution TEXT,
    top_k INTEGER,
    context_tokens INTEGER,
    retrieval_latency_ms REAL,
    no_result_rate REAL,
    precision_at_k REAL,
    recall_at_k REAL,
    mrr REAL,
    ndcg REAL,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS output_drift (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    response_length INTEGER,
    response_tokens INTEGER,
    sentiment TEXT,
    classification TEXT,
    refusal_rate REAL,
    hallucination_rate REAL,
    groundedness REAL,
    faithfulness REAL,
    drift_score REAL,
    status TEXT,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS cost_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    session_id TEXT,
    user_id TEXT,
    agent_name TEXT,
    model_name TEXT,
    provider TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost REAL,
    environment TEXT,
    metadata TEXT
);

CREATE TABLE IF NOT EXISTS token_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_id TEXT,
    trace_id TEXT,
    agent_name TEXT,
    model_name TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    cached_tokens INTEGER,
    reasoning_tokens INTEGER,
    total_tokens INTEGER,
    environment TEXT,
    metadata TEXT
);


CREATE INDEX IF NOT EXISTS idx_logs_timestamp
ON application_logs(timestamp);

CREATE INDEX IF NOT EXISTS idx_logs_request_id
ON application_logs(request_id);

CREATE INDEX IF NOT EXISTS idx_logs_trace_id
ON application_logs(trace_id);

CREATE INDEX IF NOT EXISTS idx_logs_session_id
ON application_logs(session_id);

CREATE INDEX IF NOT EXISTS idx_logs_status
ON application_logs(status);

CREATE INDEX IF NOT EXISTS idx_logs_environment
ON application_logs(environment);


CREATE INDEX IF NOT EXISTS idx_requests_timestamp
ON request_metrics(timestamp);

CREATE INDEX IF NOT EXISTS idx_requests_request_id
ON request_metrics(request_id);

CREATE INDEX IF NOT EXISTS idx_requests_trace_id
ON request_metrics(trace_id);

CREATE INDEX IF NOT EXISTS idx_requests_agent_run_id
ON request_metrics(agent_run_id);

CREATE INDEX IF NOT EXISTS idx_requests_status
ON request_metrics(status);

CREATE INDEX IF NOT EXISTS idx_requests_environment
ON request_metrics(environment);


CREATE INDEX IF NOT EXISTS idx_traces_timestamp
ON traces(timestamp);

CREATE INDEX IF NOT EXISTS idx_traces_trace_id
ON traces(trace_id);

CREATE INDEX IF NOT EXISTS idx_traces_request_id
ON traces(request_id);

CREATE INDEX IF NOT EXISTS idx_traces_session_id
ON traces(session_id);

CREATE INDEX IF NOT EXISTS idx_traces_agent_run_id
ON traces(agent_run_id);

CREATE INDEX IF NOT EXISTS idx_traces_status
ON traces(status);

CREATE INDEX IF NOT EXISTS idx_traces_environment
ON traces(environment);


CREATE INDEX IF NOT EXISTS idx_spans_trace_id
ON spans(trace_id);

CREATE INDEX IF NOT EXISTS idx_spans_parent_span_id
ON spans(parent_span_id);

CREATE INDEX IF NOT EXISTS idx_spans_agent_name
ON spans(agent_name);

CREATE INDEX IF NOT EXISTS idx_spans_model_name
ON spans(model_name);

CREATE INDEX IF NOT EXISTS idx_spans_tool_name
ON spans(tool_name);

CREATE INDEX IF NOT EXISTS idx_spans_status
ON spans(status);


CREATE INDEX IF NOT EXISTS idx_guardrails_timestamp
ON guardrail_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_guardrails_request_id
ON guardrail_events(request_id);

CREATE INDEX IF NOT EXISTS idx_guardrails_trace_id
ON guardrail_events(trace_id);


CREATE INDEX IF NOT EXISTS idx_approvals_request_id
ON human_approval_events(request_id);

CREATE INDEX IF NOT EXISTS idx_approvals_trace_id
ON human_approval_events(trace_id);


CREATE INDEX IF NOT EXISTS idx_errors_timestamp
ON error_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_errors_request_id
ON error_events(request_id);

CREATE INDEX IF NOT EXISTS idx_errors_trace_id
ON error_events(trace_id);


CREATE INDEX IF NOT EXISTS idx_security_timestamp
ON security_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_security_request_id
ON security_events(request_id);

CREATE INDEX IF NOT EXISTS idx_security_trace_id
ON security_events(trace_id);
"""


def initialize_observability_schema() -> None:
    """
    Create the core observability tables and indexes.
    """

    connection = get_connection()

    try:
        connection.executescript(SCHEMA_SQL)
        connection.commit()
    finally:
        connection.close()


def get_observability_tables() -> list[str]:
    """
    Return all user-created tables in observability.db.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name;
            """
        ).fetchall()

        return [row["name"] for row in rows]
    finally:
        connection.close()


if __name__ == "__main__":
    initialize_observability_schema()

    print("Observability schema initialized.")
    print("Tables:")

    for table in get_observability_tables():
        print(f" - {table}")