import Link from 'next/link';
import { fetchObservabilityLogs } from '../../lib/api';

export const dynamic = 'force-dynamic';

export default async function LogsPage() {
  const data = await fetchObservabilityLogs();

  return (
    <main style={{ padding: '32px', fontFamily: 'Arial' }}>
      <Link href="/">← Dashboard</Link>

      <h1>Application Logs</h1>
      <p>Total logs: {data.total}</p>

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
                'Timestamp',
                'Level',
                'Status',
                'Service',
                'Trace ID',
                'Message',
                'Latency',
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
            {data.items.map((log: any) => (
              <tr key={log.id}>
                <td style={{ padding: '12px' }}>{log.timestamp}</td>
                <td style={{ padding: '12px' }}>{log.log_level}</td>
                <td style={{ padding: '12px' }}>{log.status}</td>
                <td style={{ padding: '12px' }}>{log.service}</td>
                <td style={{ padding: '12px' }}>
                  <code>{log.trace_id || '-'}</code>
                </td>
                <td style={{ padding: '12px' }}>{log.message}</td>
                <td style={{ padding: '12px' }}>
                  {log.latency_ms != null
                    ? `${Number(log.latency_ms).toFixed(2)} ms`
                    : '-'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}