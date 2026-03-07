'use client';

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
} from 'recharts';

interface ShapEntry {
  feature: string;
  value: number;
  direction: string;
}

const FEATURE_LABELS: Record<string, string> = {
  dscr: 'Debt Service Coverage',
  ebitda_margin_pct: 'EBITDA Margin %',
  current_ratio: 'Current Ratio',
  debt_to_equity: 'Debt-to-Equity',
  revenue_growth_yoy: 'Revenue Growth YoY',
  gst_bank_mismatch_pct: 'GST-Bank Mismatch %',
  active_litigation_count: 'Active Litigation',
  promoter_red_flag: 'Promoter Red Flag',
  factory_capacity_pct: 'Factory Capacity %',
  auditor_qualified: 'Auditor Qualified',
  charge_count: 'MCA Charge Count',
  bounced_cheques_12m: 'Bounced Cheques (12m)',
  sector_risk_index: 'Sector Risk Index',
};

export default function ShapChart({ data }: { data: ShapEntry[] }) {
  const chartData = data.map((d) => ({
    ...d,
    label: FEATURE_LABELS[d.feature] || d.feature,
  }));

  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">
        SHAP Feature Importance
      </p>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 160, right: 30 }}>
          <XAxis
            type="number"
            tick={{ fill: 'var(--ic-muted)', fontSize: 11, fontFamily: 'DM Mono, monospace' }}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: 'var(--ic-text)', fontSize: 12, fontFamily: 'DM Sans, sans-serif' }}
            width={150}
          />
          <Tooltip
            formatter={(value: number) => value.toFixed(3)}
            contentStyle={{
              backgroundColor: 'var(--ic-surface)',
              border: '1px solid var(--ic-border)',
              borderRadius: '8px',
              color: 'var(--ic-text)',
              fontFamily: 'DM Mono, monospace',
            }}
          />
          <ReferenceLine x={0} stroke="var(--ic-border)" />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.value > 0 ? 'var(--ic-accent)' : 'var(--ic-warning)'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-6 mt-3 text-[12px]">
        <span className="flex items-center gap-2">
          <span className="w-3 h-3 bg-ic-accent rounded" /> Risk Increase
        </span>
        <span className="flex items-center gap-2">
          <span className="w-3 h-3 bg-ic-warning rounded" /> Risk Decrease
        </span>
      </div>
    </div>
  );
}
