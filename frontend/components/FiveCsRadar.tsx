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
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-3">Five Cs Radar</h3>
      <ResponsiveContainer width="100%" height={360}>
        <RadarChart data={data}>
          <PolarGrid stroke="#6a8b58" />
          <PolarAngleAxis dataKey="metric" tick={{ fill: '#e8f2df', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 10]} tick={{ fill: '#c8d7c0', fontSize: 11 }} />
          <Radar
            name="Company Score"
            dataKey="company"
            stroke="#4cbb17"
            fill="#4cbb17"
            fillOpacity={0.45}
          />
          <Radar
            name="Industry Benchmark"
            dataKey="benchmark"
            stroke="#8fbf5e"
            fill="#8fbf5e"
            fillOpacity={0.3}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#253021',
              border: '1px solid #6a8b58',
              color: '#eef6e9',
            }}
          />
          <Legend wrapperStyle={{ color: '#e8f2df' }} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
