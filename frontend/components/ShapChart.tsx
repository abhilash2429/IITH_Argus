/**
 * ShapChart — Recharts horizontal BarChart for SHAP values.
 * Red bars = positive SHAP (risk increase). Green bars = negative SHAP (risk decrease).
 */

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
    <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h3 className="text-white font-semibold text-lg mb-4">
        SHAP Feature Importance — Why this score?
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} layout="vertical" margin={{ left: 160, right: 30 }}>
          <XAxis type="number" tick={{ fill: '#c8d7c0', fontSize: 12 }} />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fill: '#e8f2df', fontSize: 12 }}
            width={150}
          />
          <Tooltip
            formatter={(value: number) => value.toFixed(3)}
            contentStyle={{
              backgroundColor: '#253021',
              border: '1px solid #6a8b58',
              borderRadius: '8px',
              color: '#eef6e9',
            }}
          />
          <ReferenceLine x={0} stroke="#6f8e5f" />
          <Bar dataKey="value" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={index}
                fill={entry.value > 0 ? '#dc2626' : '#4cbb17'}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="flex gap-6 mt-3 text-sm">
        <span className="flex items-center gap-2">
          <span className="w-3 h-3 bg-red-500 rounded" /> Risk Increase
        </span>
        <span className="flex items-center gap-2">
          <span className="w-3 h-3 bg-green-500 rounded" /> Risk Decrease
        </span>
      </div>
    </div>
  );
}
