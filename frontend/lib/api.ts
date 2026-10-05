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
