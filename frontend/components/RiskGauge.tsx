/**
 * RiskGauge — SVG semi-circle gauge 0-100.
 * Color zones: 0-34 red, 35-54 orange, 55-74 yellow, 75-100 green.
 * Decision badge below.
 */

'use client';

interface RiskGaugeProps {
  score: number;
  decision: string;
  category: string;
}

export default function RiskGauge({ score, decision, category }: RiskGaugeProps) {
  const clampedScore = Math.min(100, Math.max(0, score));
  const angle = -90 + (clampedScore / 100) * 180;

  const getColor = (s: number) => {
    if (s < 35) return '#ef4444';
    if (s < 55) return '#f97316';
    if (s < 75) return '#eab308';
    return '#22c55e';
  };

  const getDecisionColor = (d: string) => {
    if (d === 'APPROVE') return 'bg-green-600';
    if (d === 'CONDITIONAL_APPROVE') return 'bg-yellow-600';
    if (d === 'REJECT' || d === 'HARD_REJECT') return 'bg-red-600';
    return 'bg-orange-600';
  };

  const needleX = 150 + 100 * Math.cos((angle * Math.PI) / 180);
  const needleY = 150 + 100 * Math.sin((angle * Math.PI) / 180);

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 300 180" className="w-72">
        {/* Background arcs */}
        <path d="M 30 150 A 120 120 0 0 1 72 55" stroke="#ef4444" strokeWidth="20" fill="none" strokeLinecap="round" />
        <path d="M 72 55 A 120 120 0 0 1 150 30" stroke="#f97316" strokeWidth="20" fill="none" strokeLinecap="round" />
        <path d="M 150 30 A 120 120 0 0 1 228 55" stroke="#eab308" strokeWidth="20" fill="none" strokeLinecap="round" />
        <path d="M 228 55 A 120 120 0 0 1 270 150" stroke="#22c55e" strokeWidth="20" fill="none" strokeLinecap="round" />

        {/* Needle */}
        <line
          x1="150"
          y1="150"
          x2={needleX}
          y2={needleY}
          stroke={getColor(clampedScore)}
          strokeWidth="3"
          strokeLinecap="round"
        />
        <circle cx="150" cy="150" r="6" fill={getColor(clampedScore)} />

        {/* Score text */}
        <text x="150" y="140" textAnchor="middle" className="text-3xl font-bold" fill="white" fontSize="32">
          {clampedScore.toFixed(1)}
        </text>
        <text x="150" y="165" textAnchor="middle" fill="#94a3b8" fontSize="14">
          {category}
        </text>
      </svg>

      {/* Decision badge */}
      <div className={`mt-2 px-4 py-2 rounded-full text-white font-bold text-sm ${getDecisionColor(decision)}`}>
        {decision.replace('_', ' ')}
      </div>
    </div>
  );
}
