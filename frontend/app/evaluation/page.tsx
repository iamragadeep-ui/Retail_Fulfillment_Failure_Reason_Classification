import Link from 'next/link';

export default function EvaluationPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Evaluation</p>
            <h1 className="text-3xl font-bold">Classification Quality Dashboard</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
          </nav>
        </div>

        <div className="grid gap-4 md:grid-cols-3">
          <div className="card">
            <p className="text-sm uppercase text-slate-400">Accuracy</p>
            <p className="mt-3 text-3xl font-bold text-emerald-400">94%</p>
          </div>
          <div className="card">
            <p className="text-sm uppercase text-slate-400">Precision</p>
            <p className="mt-3 text-3xl font-bold text-blue-400">92%</p>
          </div>
          <div className="card">
            <p className="text-sm uppercase text-slate-400">Human Review Rate</p>
            <p className="mt-3 text-3xl font-bold text-amber-400">12%</p>
          </div>
        </div>
      </div>
    </main>
  );
}
