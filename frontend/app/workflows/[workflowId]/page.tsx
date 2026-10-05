import Link from 'next/link';
import { fetchWorkflow } from '@/lib/api';

async function getWorkflow(workflowId: string) {
  try {
    return await fetchWorkflow(workflowId);
  } catch (error) {
    return null;
  }
}

export default async function WorkflowPage({ params }: { params: { workflowId: string } }) {
  const workflow = await getWorkflow(params.workflowId);

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-4xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Workflow</p>
            <h1 className="text-3xl font-bold">Workflow {params.workflowId}</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
          </nav>
        </div>

        <div className="card">
          {workflow ? (
            <div>
              <p><strong>Status:</strong> {workflow.status}</p>
              <p className="mt-3"><strong>Case ID:</strong> {workflow.case_id}</p>
            </div>
          ) : (
            <p>Workflow not found.</p>
          )}
        </div>
      </div>
    </main>
  );
}
