/**
 * Score Dashboard Page
 * Shows RiskGauge, SHAP chart, violations, strengths, loan limit, interest premium.
 */

'use client';

import { useEffect, useState } from 'react';
import { getScore, getShapValues, type RiskScore, type ShapEntry } from '@/lib/api';
import RiskGauge from '@/components/RiskGauge';
import ShapChart from '@/components/ShapChart';

export default function ScorePage() {
  const [score, setScore] = useState<RiskScore | null>(null);
  const [shap, setShap] = useState<ShapEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [companyId, setCompanyId] = useState('');

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
  }, []);

  useEffect(() => {
    if (!companyId) return;

    Promise.all([getScore(companyId), getShapValues(companyId)])
      .then(([scoreData, shapData]) => {
        setScore(scoreData);
        setShap(shapData);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [companyId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
        <p className="text-blue-300 text-lg animate-pulse">Loading score...</p>
      </main>
    );
  }

  if (!score) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8">
        <p className="text-red-400">Score not available.</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8">
      <div className="max-w-5xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Risk Assessment</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Gauge + Key Metrics */}
          <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <RiskGauge
              score={score.final_risk_score}
              decision={score.decision}
              category={score.risk_category}
            />

            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 text-xs">Recommended Limit</p>
                <p className="text-white text-xl font-bold">
                  ₹{score.recommended_limit_crore?.toFixed(1)} Cr
                </p>
              </div>
              <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 text-xs">Interest Premium</p>
                <p className="text-white text-xl font-bold">
                  +{score.interest_premium_bps} bps
                </p>
              </div>
              <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 text-xs">Rule Score</p>
                <p className="text-white text-xl font-bold">{score.rule_based_score?.toFixed(1)}</p>
              </div>
              <div className="text-center p-3 bg-slate-900/50 rounded-lg">
                <p className="text-slate-400 text-xs">ML Stress Prob.</p>
                <p className="text-white text-xl font-bold">
                  {(score.ml_stress_probability * 100)?.toFixed(1)}%
                </p>
              </div>
            </div>
          </div>

          {/* Violations & Strengths */}
          <div className="space-y-6">
            {/* Violations */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-red-400 font-semibold mb-3">⚠️ Rule Violations</h3>
              {score.rule_violations?.length ? (
                <ul className="space-y-2">
                  {score.rule_violations.map((v, i) => (
                    <li key={i} className="text-red-300 text-sm flex gap-2">
                      <span className="text-red-500">•</span> {v}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-400 text-sm">No violations found.</p>
              )}
            </div>

            {/* Strengths */}
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <h3 className="text-green-400 font-semibold mb-3">✅ Risk Strengths</h3>
              {score.risk_strengths?.length ? (
                <ul className="space-y-2">
                  {score.risk_strengths.map((s, i) => (
                    <li key={i} className="text-green-300 text-sm flex gap-2">
                      <span className="text-green-500">•</span> {s}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-400 text-sm">No strengths identified.</p>
              )}
            </div>
          </div>
        </div>

        {/* SHAP Chart */}
        <div className="mt-8">
          {shap.length > 0 && <ShapChart data={shap} />}
        </div>

        {/* Decision Rationale */}
        {score.decision_rationale && (
          <div className="mt-8 bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-white font-semibold mb-3">📝 Decision Rationale</h3>
            <p className="text-slate-300 text-sm whitespace-pre-wrap">{score.decision_rationale}</p>
          </div>
        )}
      </div>
    </main>
  );
}
