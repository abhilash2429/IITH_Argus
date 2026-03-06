'use client';

interface Anomaly {
  title: string;
  details: string;
  severity: string;
}

export default function AnomalyFlags({ anomalies }: { anomalies: Anomaly[] }) {
  if (!anomalies.length) {
    return (
      <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
        <h3 className="text-white font-semibold text-lg mb-2">Anomaly Flags</h3>
        <p className="text-slate-400 text-sm">No critical anomalies detected.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-4">Anomaly Flags</h3>
      <div className="space-y-3">
        {anomalies.map((a, idx) => (
          <div key={`${a.title}-${idx}`} className="p-3 rounded-lg bg-slate-900/60 border border-slate-700">
            <p className="text-white font-medium">{a.title}</p>
            <p className="text-slate-400 text-sm mt-1">{a.details}</p>
            <span className="inline-block mt-2 text-xs px-2 py-1 rounded bg-red-900/50 text-red-300">
              {a.severity}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

