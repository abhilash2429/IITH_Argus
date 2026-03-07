'use client';

import { useMemo, useState } from 'react';

export default function StressTestPanel({
  baseScore,
  onSimulate,
}: {
  baseScore: number;
  onSimulate?: (dropPct: number) => void;
}) {
  const [revenueDrop, setRevenueDrop] = useState(20);

  const simulated = useMemo(() => {
    const hit = revenueDrop * 1.6;
    return Math.max(300, Math.min(900, baseScore - hit));
  }, [baseScore, revenueDrop]);

  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Stress Test</p>
      <p className="text-ic-text text-[14px] mb-3">
        What if revenue drops by <span className="font-mono font-medium">{revenueDrop}%</span>?
      </p>
      <input
        type="range"
        min={0}
        max={40}
        value={revenueDrop}
        onChange={(e) => setRevenueDrop(Number(e.target.value))}
        className="w-full"
      />
      <p className="text-ic-text text-[14px] mt-3">
        Simulated Credit Score: <span className="font-mono font-medium">{simulated.toFixed(0)}</span>
      </p>
      <button
        onClick={() => onSimulate?.(revenueDrop)}
        className="mt-3 px-4 py-2 rounded-[6px] bg-ic-accent text-white text-[12px] font-medium transition-opacity hover:opacity-90"
      >
        Apply Scenario
      </button>
    </div>
  );
}
