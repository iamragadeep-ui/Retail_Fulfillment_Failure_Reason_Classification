import Link from 'next/link';
import { fetchObservabilityMetrics } from '../../lib/api';

export const dynamic = 'force-dynamic';

function Card({
  title,
  value,
}: {
  title: string;
  value: string | number;
}) {
  return (
    <div
      style={{
        padding: '20px',
        border: '1px solid #ddd',
        borderRadius: '12px',
        minWidth: '200px',
      }}
    >
      <div style={{ fontSize: '14px', opacity: 0.7 }}>{title}</div>

      <div
        style={{
          fontSize: '28px',
          fontWeight: 700,
          marginTop: '8px',
        }}
      >
        {value}
      </div>
    </div>
  );
}

export default async function MetricsPage() {
  const data = await fetchObservabilityMetrics();

  return (
    <main style={{ padding: '32px', fontFamily: 'Arial' }}>
      <Link href="/">← Dashboard</Link>

      <h1>Observability Metrics</h1>

      <h2>Requests</h2>

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <Card
          title="Total Requests"
          value={data.requests.total_requests}
        />

        <Card
          title="Successful Requests"
          value={data.requests.successful_requests}
        />

        <Card
          title="Failed Requests"
          value={data.requests.failed_requests}
        />

        <Card
          title="Average Latency"
          value={
            data.requests.avg_latency_ms != null
              ? `${Number(data.requests.avg_latency_ms).toFixed(2)} ms`
              : 'N/A'
          }
        />

        <Card
          title="Maximum Latency"
          value={
            data.requests.max_latency_ms != null
              ? `${Number(data.requests.max_latency_ms).toFixed(2)} ms`
              : 'N/A'
          }
        />
      </div>

      <h2 style={{ marginTop: '32px' }}>Tracing</h2>

      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '16px',
        }}
      >
        <Card title="Total Traces" value={data.traces.total_traces} />

        <Card
          title="Successful Traces"
          value={data.traces.successful_traces}
        />

        <Card
          title="Failed Traces"
          value={data.traces.failed_traces}
        />

        <Card
          title="Guardrail Events"
          value={data.guardrails.total_guardrail_events}
        />

        <Card
          title="Blocked Events"
          value={data.guardrails.blocked_events}
        />

        <Card title="Errors" value={data.errors.total_errors} />
      </div>
    </main>
  );
}