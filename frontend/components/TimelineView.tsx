'use client';

interface TimelineItem {
  timestamp: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';
  details?: string;
}

const severityStyle: Record<TimelineItem['severity'], { dot: string; badge: string }> = {
  CRITICAL: { dot: 'bg-ic-negative', badge: 'bg-[#fde8e8] text-ic-negative border border-[#f3bcbc]' },
  HIGH: { dot: 'bg-ic-warning', badge: 'bg-[#fdf0e8] text-ic-warning border border-[#f3d5bc]' },
  MEDIUM: { dot: 'bg-ic-tan', badge: 'bg-ic-surface-mid text-ic-muted border border-ic-border' },
  LOW: { dot: 'bg-ic-accent', badge: 'bg-ic-accent-light text-ic-positive border border-[#b8d9bf]' },
  INFORMATIONAL: { dot: 'bg-ic-muted', badge: 'bg-ic-surface-mid text-ic-muted border border-ic-border' },
};

export default function TimelineView({ items }: { items: TimelineItem[] }) {
  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-4">Risk Flag Timeline</p>
      <div className="space-y-0">
        {items.map((item, idx) => {
          const styles = severityStyle[item.severity] || severityStyle.INFORMATIONAL;
          return (
            <div key={`${item.timestamp}-${idx}`} className="flex gap-3 py-2.5 border-b border-ic-border last:border-0">
              <div className={`w-2.5 h-2.5 rounded-full mt-1 flex-shrink-0 ${styles.dot}`} />
              <div className="flex-1 min-w-0">
                <p className="font-mono text-[11px] text-ic-muted">{new Date(item.timestamp).toLocaleString()}</p>
                <p className="text-[13px] font-medium text-ic-text mt-0.5">{item.title}</p>
                {item.details && <p className="text-ic-muted text-[12px] mt-0.5">{item.details}</p>}
              </div>
              <span className={`text-[10px] px-2 py-0.5 rounded font-medium h-fit flex-shrink-0 ${styles.badge}`}>
                {item.severity}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
