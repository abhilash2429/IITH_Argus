'use client';

import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from 'recharts';

interface Props {
  company: {
    character: number;
    capacity: number;
    capital: number;
    collateral: number;
    conditions: number;
  };
  benchmark?: {
    character: number;
    capacity: number;
    capital: number;
    collateral: number;
    conditions: number;
  };
}

export default function FiveCsRadar({ company, benchmark }: Props) {
  const b = benchmark || {
    character: 7.2,
    capacity: 7.0,
    capital: 6.8,
    collateral: 6.5,
    conditions: 6.9,
  };

  const data = [
    { metric: 'Character', company: company.character, benchmark: b.character },
    { metric: 'Capacity', company: company.capacity, benchmark: b.capacity },
    { metric: 'Capital', company: company.capital, benchmark: b.capital },
    { metric: 'Collateral', company: company.collateral, benchmark: b.collateral },
    { metric: 'Conditions', company: company.conditions, benchmark: b.conditions },
  ];

  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Five Cs Radar</p>
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data}>
          <PolarGrid stroke="var(--ic-border)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: 'var(--ic-muted)', fontSize: 11, fontFamily: 'DM Sans, sans-serif' }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 10]}
            tick={{ fill: 'var(--ic-muted)', fontSize: 11, fontFamily: 'DM Mono, monospace' }}
          />
          <Radar
            name="Company Score"
            dataKey="company"
            stroke="var(--ic-accent)"
            fill="var(--ic-accent)"
            fillOpacity={0.15}
          />
          <Radar
            name="Industry Benchmark"
            dataKey="benchmark"
            stroke="var(--ic-tan)"
            fill="var(--ic-tan)"
            fillOpacity={0.1}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--ic-surface)',
              border: '1px solid var(--ic-border)',
              color: 'var(--ic-text)',
              fontFamily: 'DM Mono, monospace',
            }}
          />
          <Legend wrapperStyle={{ color: 'var(--ic-text)', fontSize: 12 }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
