import Link from 'next/link';

export default function ReviewsPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Human Review</p>
            <h1 className="text-3xl font-bold">Review Queue</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
            <Link href="/analyze" className="rounded border border-slate-700 px-3 py-2">Analyze</Link>
            <Link href="/reviews" className="rounded border border-slate-700 px-3 py-2">Reviews</Link>
          </nav>
        </div>

        <div className="card">
          <table className="table w-full">
            <thead>
              <tr>
                <th>Case</th>
                <th>Original</th>
                <th>Decision</th>
                <th>Reviewer</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>CASE-20261005-ORD123</td>
                <td>CARRIER_DELAY</td>
                <td>AUTO_CLASSIFIED</td>
                <td>SYSTEM</td>
                <td>Carrier delay confirmed after successful upstream fulfillment.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
}
