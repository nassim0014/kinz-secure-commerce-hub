'use client';

import { useEffect, useState } from 'react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid,
  PieChart, Pie, Cell, Legend,
} from 'recharts';

type KpiSummary = {
  revenue_tnd: number;
  orders: number;
  avg_order_value_tnd: number;
  gross_margin_tnd: number;
  gross_margin_pct: number;
  unique_customers: number;
  b2b_share_pct: number;
  top_category: string;
};

type ChannelRow = {
  channel: string;
  revenue_tnd: number;
  orders: number;
  avg_order_value_tnd: number;
  gross_margin_pct: number;
};

const PIE_COLORS = ['#0f766e', '#f59e0b', '#8a5e21', '#cba163', '#b07f3a', '#33240c'];

export function Dashboard() {
  const [kpi, setKpi] = useState<KpiSummary | null>(null);
  const [channels, setChannels] = useState<ChannelRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        // In dev, Next.js rewrites /api/* to the FastAPI backend.
        // For the demo we don't require auth — the dashboard reads public
        // summary endpoints. Wire a login flow before going live.
        const [k, c] = await Promise.all([
          fetch('/api/v1/kpis/summary').then((r) => r.json()),
          fetch('/api/v1/kpis/channels').then((r) => r.json()),
        ]);
        setKpi(k);
        setChannels(c);
      } catch (e: any) {
        setError(e?.message ?? 'Failed to load');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="text-kinz-500">Loading KINZ dashboard…</div>;
  if (error || !kpi) return <div className="text-red-600">Error: {error ?? 'no data'}</div>;

  return (
    <div className="space-y-8">
      {/* Headline */}
      <div>
        <h2 className="font-serif text-3xl text-kinz-700">Business Overview</h2>
        <p className="text-kinz-500 text-sm mt-1">
          Snapshot of revenue, margin, and channel mix across the KINZ catalog.
        </p>
      </div>

      {/* KPI grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <KpiCard label="Revenue"        value={`${kpi.revenue_tnd.toLocaleString('en-TN')} TND`} />
        <KpiCard label="Orders"         value={kpi.orders.toLocaleString('en-TN')} />
        <KpiCard label="Avg Order Value" value={`${kpi.avg_order_value_tnd.toFixed(0)} TND`} />
        <KpiCard label="Gross Margin"   value={`${kpi.gross_margin_pct.toFixed(1)} %`} />
        <KpiCard label="Unique Customers" value={kpi.unique_customers.toLocaleString('en-TN')} />
        <KpiCard label="B2B Share"      value={`${kpi.b2b_share_pct.toFixed(1)} %`} />
        <KpiCard label="Top Category"   value={kpi.top_category} />
        <KpiCard label="Gross Margin TND" value={`${kpi.gross_margin_tnd.toLocaleString('en-TN')} TND`} />
      </div>

      {/* Channel chart */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-serif text-lg text-kinz-700 mb-4">Revenue by Channel</h3>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={channels} layout="vertical" margin={{ left: 30, right: 20 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" tickFormatter={(v) => `${(v/1000).toFixed(0)}k`} />
              <YAxis dataKey="channel" type="category" width={120} />
              <Tooltip formatter={(v: any) => `${Number(v).toLocaleString()} TND`} />
              <Bar dataKey="revenue_tnd" fill="#0f766e" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h3 className="font-serif text-lg text-kinz-700 mb-4">Channel Mix by Orders</h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={channels}
                dataKey="orders"
                nameKey="channel"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
              >
                {channels.map((_, i) => (
                  <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function KpiCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="card">
      <p className="kpi-label">{label}</p>
      <p className="kpi-value mt-2">{value}</p>
    </div>
  );
}
