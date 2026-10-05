import Link from 'next/link';
import { fetchCase } from '@/lib/api';

async function getCase(caseId: string) {
  try {
    return await fetchCase(caseId);
  } catch (error) {
    return null;
  }
}

export default async function CaseDetailPage({ params }: { params: { caseId: string } }) {
  const caseData = await getCase(params.caseId);

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Case Detail</p>
            <h1 className="text-3xl font-bold">Case {params.caseId}</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
          </nav>
        </div>

        <div className="card">
          {caseData ? (
            <div className="space-y-3 text-slate-200">
              <p><strong>Order ID:</strong> {caseData.order_id}</p>
              <p><strong>Status:</strong> {caseData.status}</p>
              <p><strong>Failure Reason:</strong> {caseData.classification?.failure_reason || 'N/A'}</p>
              <p><strong>Confidence:</strong> {caseData.classification?.confidence_score ? `${Math.round(caseData.classification.confidence_score * 100)}%` : 'N/A'}</p>
            </div>
          ) : (
            <p>Case not found.</p>
          )}
        </div>
      </div>
    </main>
  );
}
