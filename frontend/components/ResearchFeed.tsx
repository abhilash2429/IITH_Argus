'use client';

import { useMemo, useState } from 'react';

interface Finding {
  source_url: string;
  source_name: string;
  finding_type: string;
  summary: string;
  severity: string;
  date_of_finding?: string | null;
  raw_snippet: string;
}

const FILTERS = ['ALL', 'CRITICAL', 'FRAUD', 'LITIGATION', 'SECTOR'] as const;

export default function ResearchFeed({ findings }: { findings: Finding[] }) {
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>('ALL');

  const filtered = useMemo(() => {
    if (filter === 'ALL') return findings;
    if (filter === 'CRITICAL') return findings.filter((f) => f.severity === 'CRITICAL');
    if (filter === 'FRAUD') return findings.filter((f) => f.finding_type === 'FRAUD_ALERT');
    if (filter === 'LITIGATION') return findings.filter((f) => f.finding_type === 'LITIGATION');
    if (filter === 'SECTOR') return findings.filter((f) => f.finding_type === 'SECTOR');
    return findings;
  }, [filter, findings]);

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-white font-semibold text-lg">Research Feed</h3>
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-2 py-1 rounded text-xs ${
                filter === f ? 'bg-blue-600 text-white' : 'bg-slate-700 text-slate-300'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3 max-h-[420px] overflow-auto pr-2">
        {filtered.map((f, idx) => (
          <div key={`${f.source_url}-${idx}`} className="p-3 rounded-lg bg-slate-900/60 border border-slate-700">
            <div className="flex justify-between items-start gap-2">
              <p className="text-white font-medium">{f.source_name}</p>
              <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-100">
                {f.severity}
              </span>
            </div>
            <p className="text-slate-300 text-sm mt-1">{f.summary}</p>
            <p className="text-slate-500 text-xs mt-2">
              {f.date_of_finding ? new Date(f.date_of_finding).toLocaleDateString() : 'No date'}
            </p>
            <a
              href={f.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-sky-400 text-xs mt-1 inline-block"
            >
              Source link
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}

