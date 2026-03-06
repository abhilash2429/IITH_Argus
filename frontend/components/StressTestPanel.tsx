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
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-2">Stress Test</h3>
      <p className="text-slate-300 text-sm mb-3">
        What if revenue drops by <span className="font-semibold">{revenueDrop}%</span>?
      </p>
      <input
        type="range"
        min={0}
        max={40}
        value={revenueDrop}
        onChange={(e) => setRevenueDrop(Number(e.target.value))}
        className="w-full accent-blue-500"
      />
      <p className="text-slate-200 mt-3">
        Simulated Credit Score: <span className="font-bold">{simulated.toFixed(0)}</span>
      </p>
      <button
        onClick={() => onSimulate?.(revenueDrop)}
        className="mt-3 px-3 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white text-sm"
      >
        Apply Scenario
      </button>
    </div>
  );
}

