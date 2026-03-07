'use client';

interface RiskGaugeProps {
  score: number;
  decision: string;
  category: string;
}

export default function RiskGauge({ score, decision, category }: RiskGaugeProps) {
  const clampedScore = Math.min(100, Math.max(0, score));
  const angle = -90 + (clampedScore / 100) * 180;

  const needleX = 150 + 100 * Math.cos((angle * Math.PI) / 180);
  const needleY = 150 + 100 * Math.sin((angle * Math.PI) / 180);

  const getDecisionStyle = (d: string) => {
    if (d === 'APPROVE') return 'bg-ic-accent-light text-ic-positive';
    if (d === 'CONDITIONAL_APPROVE') return 'bg-[#fdf0e8] text-ic-warning';
    if (d === 'REJECT' || d === 'HARD_REJECT') return 'bg-[#fde8e8] text-ic-negative';
    return 'bg-ic-surface-mid text-ic-muted';
  };

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 300 180" className="w-72">
        {/* Track arc */}
        <path
          d="M 30 150 A 120 120 0 0 1 270 150"
          stroke="var(--ic-surface-mid)"
          strokeWidth="20"
          fill="none"
          strokeLinecap="round"
        />
        {/* Filled arc — calculated based on score */}
        <path
          d="M 30 150 A 120 120 0 0 1 270 150"
          stroke="var(--ic-accent)"
          strokeWidth="20"
          fill="none"
          strokeLinecap="round"
          strokeDasharray={`${(clampedScore / 100) * 377} 377`}
        />

        {/* Needle */}
        <line
          x1="150"
          y1="150"
          x2={needleX}
          y2={needleY}
          stroke="var(--ic-accent)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />
        <circle cx="150" cy="150" r="5" fill="var(--ic-accent)" />

        {/* Score text */}
        <text
          x="150"
          y="138"
          textAnchor="middle"
          fill="var(--ic-text)"
          fontSize="32"
          fontFamily="Playfair Display, serif"
        >
          {clampedScore.toFixed(1)}
        </text>
        <text
          x="150"
          y="163"
          textAnchor="middle"
          fill="var(--ic-muted)"
          fontSize="12"
          fontFamily="DM Sans, sans-serif"
        >
          {category}
        </text>
      </svg>

      {/* Decision badge */}
      <div className={`mt-2 px-4 py-1.5 rounded text-[11px] uppercase tracking-wider font-medium ${getDecisionStyle(decision)}`}>
        {decision.replace('_', ' ')}
      </div>
    </div>
  );
}
