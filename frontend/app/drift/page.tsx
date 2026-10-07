import Link from 'next/link';
import { fetchObservabilityDrift } from '../../lib/api';

export const dynamic = 'force-dynamic';

function formatName(name: string) {
  return name
    .replaceAll('_', ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export default async function DriftPage() {
  const data = await fetchObservabilityDrift();

  return (
    <main style={{ padding: '32px', fontFamily: 'Arial' }}>
      <Link href="/">← Dashboard</Link>

      <h1>AI Drift Monitoring</h1>

      <p>
        Model, data, prediction, concept, prompt, retrieval and output
        drift monitoring.
      </p>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '20px',
          marginTop: '24px',
        }}
      >
        {Object.entries(data.drift).map(
          ([category, records]: [string, any]) => {
            const latest = records[0];

            return (
              <div
                key={category}
                style={{
                  border: '1px solid #ddd',
                  borderRadius: '12px',
                  padding: '20px',
                }}
              >
                <h2>{formatName(category)}</h2>

                <p>
                  Records: <strong>{records.length}</strong>
                </p>

                {latest ? (
                  <>
                    <p>
                      Status:{' '}
                      <strong>{latest.status || 'UNKNOWN'}</strong>
                    </p>

                    <p>
                      Drift score:{' '}
                      <strong>
                        {latest.drift_score != null
                          ? Number(latest.drift_score).toFixed(3)
                          : 'N/A'}
                      </strong>
                    </p>

                    <p>
                      Environment:{' '}
                      <strong>
                        {latest.environment || 'unknown'}
                      </strong>
                    </p>

                    <p style={{ fontSize: '13px', opacity: 0.7 }}>
                      {latest.timestamp}
                    </p>
                  </>
                ) : (
                  <p>No drift records available.</p>
                )}
              </div>
            );
          }
        )}
      </div>
    </main>
  );
}