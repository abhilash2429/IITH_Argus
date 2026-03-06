'use client';

interface TimelineItem {
  timestamp: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFORMATIONAL';
  details?: string;
}

const colorMap: Record<TimelineItem['severity'], string> = {
  CRITICAL: 'bg-red-500',
  HIGH: 'bg-orange-500',
  MEDIUM: 'bg-yellow-500',
  LOW: 'bg-sky-500',
  INFORMATIONAL: 'bg-blue-500',
};

export default function TimelineView({ items }: { items: TimelineItem[] }) {
  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-4">Risk Flag Timeline</h3>
      <div className="space-y-3">
        {items.map((item, idx) => (
          <div key={`${item.timestamp}-${idx}`} className="flex gap-3 items-start">
            <div className={`w-3 h-3 rounded-full mt-2 ${colorMap[item.severity]}`} />
            <div className="flex-1">
              <p className="text-sm text-slate-300">{new Date(item.timestamp).toLocaleString()}</p>
              <p className="text-white font-medium">{item.title}</p>
              {item.details && <p className="text-slate-400 text-sm">{item.details}</p>}
            </div>
            <span className="text-xs px-2 py-1 rounded bg-slate-700 text-slate-200">
              {item.severity}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

