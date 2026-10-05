'use client';

import Link from 'next/link';
import { useState } from 'react';
import { analyzeCase } from '@/lib/api';

export default function AnalyzePage() {
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
    failure_description: 'Order ORD123 was expected yesterday but has not arrived. Payment succeeded, inventory was available and the warehouse dispatched the package, but carrier tracking shows a delivery exception.',
  });

  const handleChange = (key: string, value: string) => setForm((current) => ({ ...current, [key]: value }));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    try {
      const payload = { ...form, quantity: Number(form.quantity || 0), order_value: Number(form.order_value || 0) };
      const response = await analyzeCase(payload);
      setResult(response);
    } catch (error: any) {
      alert(error.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 p-8 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-8 flex items-center justify-between border-b border-slate-800 pb-5">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-blue-400">Failure Analysis</p>
            <h1 className="text-3xl font-bold">Analyze Fulfillment Failure</h1>
          </div>
          <nav className="flex gap-3 text-sm">
            <Link href="/" className="rounded border border-slate-700 px-3 py-2">Dashboard</Link>
            <Link href="/analyze" className="rounded border border-slate-700 px-3 py-2">Analyze</Link>
            <Link href="/reviews" className="rounded border border-slate-700 px-3 py-2">Reviews</Link>
          </nav>
        </div>

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
                <textarea className="input min-h-[120px]" value={form[key as keyof typeof form]} onChange={(event) => handleChange(key, event.target.value)} />
              ) : (
                <input className="input" value={form[key as keyof typeof form]} onChange={(event) => handleChange(key, event.target.value)} />
              )}
            </div>
          ))}
          <div className="md:col-span-2 xl:col-span-3">
            <button className="button" type="submit" disabled={loading}>{loading ? 'Analyzing...' : 'Analyze Fulfillment Failure'}</button>
          </div>
        </form>

        {result && (
          <div className="card mt-8">
            <h2 className="mb-4 text-2xl font-semibold">Outcome</h2>
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-xs uppercase text-slate-400">Failure Reason</p>
                <p className="mt-1 text-2xl font-bold text-blue-400">{result.classification?.failure_reason}</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Confidence</p>
                <p className="mt-1 text-xl">{Math.round((result.classification?.confidence_score || 0) * 100)}%</p>
              </div>
              <div>
                <p className="text-xs uppercase text-slate-400">Decision</p>
                <p className="mt-1 text-2xl font-bold text-emerald-400">{result.final_decision}</p>
                <p className="mt-6 text-xs uppercase text-slate-400">Severity</p>
                <p className="mt-1 text-xl">{result.classification?.severity}</p>
              </div>
            </div>
            <p className="mt-6 text-slate-300">{result.classification?.explanation}</p>
          </div>
        )}
      </div>
    </main>
  );
}
