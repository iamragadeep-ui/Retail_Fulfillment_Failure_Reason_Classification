'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { analyzeCase, fetchDashboard } from '@/lib/api';

export default function HomePage() {
  const [stats, setStats] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [form, setForm] = useState({
    order_id: 'ORD123',
    customer_id: 'CUST1001',
    sku: 'SKU-778',
    order_status: 'PENDING_DELIVERY',
    payment_status: 'SUCCESS',
    inventory_status: 'AVAILABLE',
    warehouse_status: 'DISPATCHED',
    carrier_status: 'DELAYED',
    shipping_address_status: 'VALID',
    expected_delivery_date: '2026-10-05',
    current_delivery_status: 'DELAYED',
    tracking_id: 'TRK-12345',
    warehouse_id: 'WH-01',
    carrier_name: 'NorthStar Freight',
    quantity: '1',
    priority: 'STANDARD',
    order_value: '120',
    failure_description: 'Order ORD123 was expected yesterday but has not arrived. Payment succeeded, inventory was available, and the warehouse dispatched the package, but carrier tracking shows a delivery exception.',
  });

  useEffect(() => {
    async function loadDashboard() {
      try {
        const data = await fetchDashboard();
        setStats(data.stats);
        setRecent(data.recent_decisions || []);
      } catch (error) {
        console.error(error);
      }
    }
    loadDashboard();
  }, []);

  const handleChange = (key: string, value: string) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        quantity: Number(form.quantity || 0),
        order_value: Number(form.order_value || 0),
      };
      const response = await analyzeCase(payload);
      setResult(response);
      const refreshed = await fetchDashboard();
      setStats(refreshed.stats);
      setRecent(refreshed.recent_decisions || []);
    } catch (error: any) {
      alert(error.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Enterprise AI Operations</p>
            <h1 className="mt-2 text-3xl font-bold">Retail Fulfillment Failure Reason Classification</h1>
            <h2 className="mt-1 text-lg text-slate-300">Fulfillment Failure Supervisor Dashboard</h2>
          </div>
          <nav className="flex gap-3 text-sm text-slate-300">
            <Link href="/" className="rounded-lg border border-slate-700 px-3 py-2 hover:border-blue-500">Dashboard</Link>
            <Link href="/analyze" className="rounded-lg border border-slate-700 px-3 py-2 hover:border-blue-500">Analyze Failure</Link>
            <Link href="/reviews" className="rounded-lg border border-slate-700 px-3 py-2 hover:border-blue-500">Reviews</Link>
            <Link href="/settings" className="rounded-lg border border-slate-700 px-3 py-2 hover:border-blue-500">Settings</Link>
          </nav>
        </div>

        <section className="mb-8 grid gap-4 md:grid-cols-4">
          <div className="card">
            <p className="text-xs uppercase text-slate-400">Total Cases</p>
            <p className="mt-4 text-3xl font-bold">{stats?.total_cases ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs uppercase text-slate-400">Auto Classified</p>
            <p className="mt-4 text-3xl font-bold text-emerald-400">{stats?.auto_classified ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs uppercase text-slate-400">Human Review</p>
            <p className="mt-4 text-3xl font-bold text-amber-400">{stats?.human_review ?? 0}</p>
          </div>
          <div className="card">
            <p className="text-xs uppercase text-slate-400">Latest Case</p>
            <p className="mt-4 text-3xl font-bold text-blue-400">{stats?.latest_case ?? 'N/A'}</p>
          </div>
        </section>

        <section className="mb-8 grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <div className="card">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-xl font-semibold">Recent Classification Decisions</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="table w-full">
                <thead>
                  <tr>
                    <th>Order ID</th>
                    <th>Failure Reason</th>
                    <th>Confidence</th>
                    <th>Decision</th>
                    <th>Severity</th>
                    <th>Reviewer</th>
                    <th>Created</th>
                  </tr>
                </thead>
                <tbody>
                  {recent.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="py-6 text-slate-400">No decision history available yet.</td>
                    </tr>
                  ) : (
                    recent.map((item, index) => (
                      <tr key={`${item.order_id}-${index}`}>
                        <td>{item.order_id}</td>
                        <td>{item.failure_reason}</td>
                        <td>{item.confidence}</td>
                        <td>{item.decision}</td>
                        <td>{item.severity}</td>
                        <td>{item.reviewer}</td>
                        <td>{new Date(item.created).toLocaleString()}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h3 className="text-xl font-semibold">Workflow Visualization</h3>
            <div className="mt-5 space-y-2 text-sm text-slate-300">
              {['Triage', 'Supervisor', 'Planner', 'Order Investigation', 'Inventory', 'Payment', 'Warehouse', 'Carrier', 'Policy Retrieval', 'Classification', 'Critic', 'Reviewer', 'Validator', 'Final Decision'].map((step, index) => (
                <div key={step} className="flex items-center gap-3 rounded-lg border border-slate-700 bg-slate-950 p-2">
                  <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold">{index + 1}</span>
                  <span>{step}</span>
                  <span className="ml-auto rounded bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300">COMPLETED</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="card">
          <h3 className="mb-6 text-2xl font-semibold">Analyze a Fulfillment Failure</h3>
          <form onSubmit={handleSubmit} className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {Object.entries({
              order_id: 'Order ID',
              customer_id: 'Customer ID',
              sku: 'Product SKU',
              order_status: 'Order Status',
              payment_status: 'Payment Status',
              inventory_status: 'Inventory Status',
              warehouse_status: 'Warehouse Status',
              carrier_status: 'Carrier Status',
              shipping_address_status: 'Shipping Address Status',
              expected_delivery_date: 'Expected Delivery Date',
              current_delivery_status: 'Current Delivery Status',
              tracking_id: 'Tracking ID',
              warehouse_id: 'Warehouse ID',
              carrier_name: 'Carrier Name',
              quantity: 'Quantity',
              priority: 'Priority',
              order_value: 'Order Value',
              failure_description: 'Failure Description',
            }).map(([key, label]) => (
              <div key={key} className={key === 'failure_description' ? 'md:col-span-2 xl:col-span-3' : ''}>
                <label className="label">{label}</label>
                {key === 'failure_description' ? (
                  <textarea
                    className="input min-h-[90px]"
                    value={form[key as keyof typeof form]}
                    onChange={(event) => handleChange(key, event.target.value)}
                  />
                ) : (
                  <input
                    className="input"
                    value={form[key as keyof typeof form]}
                    onChange={(event) => handleChange(key, event.target.value)}
                  />
                )}
              </div>
            ))}
            <div className="md:col-span-2 xl:col-span-3 mt-2">
              <button className="button" type="submit" disabled={loading}>
                {loading ? 'Analyzing...' : 'Analyze Fulfillment Failure'}
              </button>
            </div>
          </form>
        </section>

        {result && (
          <section className="card mt-8">
            <h3 className="mb-6 text-2xl font-semibold">Result View</h3>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-xs uppercase text-slate-400">Order</p>
                <p className="mt-1 text-xl font-semibold">{result.case_id}</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Failure Reason</p>
                <p className="mt-1 text-xl font-bold text-blue-400">{result.classification?.failure_reason}</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Final Decision</p>
                <p className="mt-1 text-xl font-bold text-emerald-400">{result.final_decision}</p>
              </div>
              <div>
                <p className="text-xs uppercase text-slate-400">Confidence</p>
                <p className="mt-1 text-xl font-bold">{Math.round((result.classification?.confidence_score || 0) * 100)}%</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Severity</p>
                <p className="mt-1 text-xl font-bold text-amber-300">{result.classification?.severity}</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Workflow ID</p>
                <p className="mt-1 text-xl font-bold">{result.workflow_id}</p>
              </div>
            </div>
            <div className="mt-8 space-y-5">
              <div>
                <h4 className="text-lg font-semibold">Root Cause Explanation</h4>
                <p className="mt-2 text-slate-300">{result.classification?.explanation || result.result?.classification?.explanation}</p>
              </div>
              <div>
                <h4 className="text-lg font-semibold">Evidence</h4>
                <ul className="mt-2 list-disc space-y-1 pl-6 text-slate-300">
                  {(result.classification?.evidence || []).map((item: string) => <li key={item}>{item}</li>)}
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold">Recommended Action</h4>
                <p className="mt-2 text-slate-300">{result.classification?.recommended_action || result.result?.classification?.recommended_action}</p>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
