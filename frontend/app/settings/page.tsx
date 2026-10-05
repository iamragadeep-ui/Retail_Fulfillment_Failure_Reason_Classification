import Link from 'next/link';

export default function SettingsPage() {
  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-5xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Settings</p>
            <h1 className="text-3xl font-bold">Operational Configuration</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
            <Link href="/analyze" className="rounded border border-slate-700 px-3 py-2">Analyze</Link>
          </nav>
        </div>

        <div className="card space-y-4">
          <div>
            <label className="label">Environment</label>
            <input className="input" value="development" readOnly />
          </div>
          <div>
            <label className="label">API URL</label>
            <input className="input" value="http://localhost:8000" readOnly />
          </div>
          <div>
            <label className="label">Review Mode</label>
            <input className="input" value="Human-in-the-loop review" readOnly />
          </div>
        </div>
      </div>
    </main>
  );
}
