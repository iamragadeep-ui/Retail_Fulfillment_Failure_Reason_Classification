import Link from 'next/link';
import { fetchObservabilityTraces } from '../../lib/api';

export const dynamic = 'force-dynamic';

export default async function TracesPage() {
  const data = await fetchObservabilityTraces();

  return (
    <main style={{ padding: '32px', fontFamily: 'Arial' }}>
      <Link href="/">← Dashboard</Link>

      <h1>Distributed Traces</h1>
      <p>Total traces: {data.total}</p>

      <div style={{ overflowX: 'auto' }}>
        <table
          style={{
            width: '100%',
            borderCollapse: 'collapse',
            marginTop: '24px',
          }}
        >
          <thead>
            <tr>
              {[
                'Trace ID',
                'Request ID',
                'Service',
                'Status',
                'Duration',
                'Started',
              ].map((heading) => (
                <th
                  key={heading}
                  style={{
                    textAlign: 'left',
                    padding: '12px',
                    borderBottom: '1px solid #ccc',
                  }}
                >
                  {heading}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {data.items.map((trace: any) => (
              <tr key={trace.trace_id}>
                <td style={{ padding: '12px' }}>
                  <code>{trace.trace_id}</code>
                </td>

                <td style={{ padding: '12px' }}>
                  <code>{trace.request_id}</code>
                </td>

                <td style={{ padding: '12px' }}>
                  {trace.service_name}
                </td>

                <td style={{ padding: '12px' }}>
                  {trace.status}
                </td>

                <td style={{ padding: '12px' }}>
                  {trace.duration_ms != null
                    ? `${Number(trace.duration_ms).toFixed(2)} ms`
                    : '-'}
                </td>

                <td style={{ padding: '12px' }}>
                  {trace.start_time}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}