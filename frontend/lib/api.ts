const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function fetchDashboard(): Promise<any> {
  const res = await fetch(`${API_URL}/api/v1/dashboard`);
  if (!res.ok) throw new Error('Dashboard request failed');
  return res.json();
}

export async function analyzeCase(payload: Record<string, any>) {
  const res = await fetch(`${API_URL}/api/v1/cases/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Analysis failed');
  }
  return res.json();
}

export async function fetchCase(caseId: string): Promise<any> {
  const res = await fetch(`${API_URL}/api/v1/cases/${encodeURIComponent(caseId)}`);
  if (!res.ok) throw new Error('Case request failed');
  return res.json();
}

export async function fetchWorkflow(workflowId: string): Promise<any> {
  const res = await fetch(`${API_URL}/api/v1/workflows/${encodeURIComponent(workflowId)}`);
  if (!res.ok) throw new Error('Workflow request failed');
  return res.json();
}

export async function fetchObservabilityLogs(
  limit = 50,
  offset = 0
): Promise<any> {
  const res = await fetch(
    `${API_URL}/api/v1/observability/logs?limit=${limit}&offset=${offset}`,
    { cache: 'no-store' }
  );

  if (!res.ok) throw new Error('Observability logs request failed');
  return res.json();
}

export async function fetchObservabilityMetrics(): Promise<any> {
  const res = await fetch(`${API_URL}/api/v1/observability/metrics`, {
    cache: 'no-store',
  });

  if (!res.ok) throw new Error('Observability metrics request failed');
  return res.json();
}

export async function fetchObservabilityTraces(
  limit = 50,
  offset = 0
): Promise<any> {
  const res = await fetch(
    `${API_URL}/api/v1/observability/traces?limit=${limit}&offset=${offset}`,
    { cache: 'no-store' }
  );

  if (!res.ok) throw new Error('Observability traces request failed');
  return res.json();
}

export async function fetchObservabilityTrace(traceId: string): Promise<any> {
  const res = await fetch(
    `${API_URL}/api/v1/observability/traces/${encodeURIComponent(traceId)}`,
    { cache: 'no-store' }
  );

  if (!res.ok) throw new Error('Trace details request failed');
  return res.json();
}

export async function fetchObservabilityDrift(): Promise<any> {
  const res = await fetch(`${API_URL}/api/v1/observability/drift`, {
    cache: 'no-store',
  });

  if (!res.ok) throw new Error('Observability drift request failed');
  return res.json();
}
