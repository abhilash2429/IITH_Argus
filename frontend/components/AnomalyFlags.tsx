'use client';

interface Anomaly {
  title: string;
  details: string;
  severity: string;
}

const getTagStyle = (severity: string) => {
  if (severity === 'CRITICAL' || severity === 'HIGH')
    return 'bg-[#fdf0e8] text-ic-warning border border-[#f3d5bc]';
  if (severity === 'LOW' || severity === 'POSITIVE')
    return 'bg-ic-accent-light text-ic-positive border border-[#b8d9bf]';
  return 'bg-ic-surface-mid text-ic-muted border border-ic-border';
};

export default function AnomalyFlags({ anomalies }: { anomalies: Anomaly[] }) {
  if (!anomalies.length) {
    return (
      <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
        <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Anomaly Flags</p>
        <p className="text-ic-muted text-[13px]">No critical anomalies detected.</p>
      </div>
    );
  }

  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-4">Anomaly Flags</p>
      <div className="space-y-3">
        {anomalies.map((a, idx) => (
          <div key={`${a.title}-${idx}`} className="py-2.5 border-b border-ic-border last:border-0">
            <p className="text-[13px] font-medium text-ic-text">{a.title}</p>
            <p className="text-ic-muted text-[12px] mt-1">{a.details}</p>
            <span className={`inline-block mt-2 text-[10px] px-2 py-0.5 rounded font-medium ${getTagStyle(a.severity)}`}>
              {a.severity}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
