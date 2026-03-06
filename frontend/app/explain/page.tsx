'use client';

import { useEffect, useState } from 'react';
import { getExplainV1 } from '@/lib/api';

const INDIA_TOOLTIPS: Record<string, string> = {
  GSTR2A:
    'Auto-populated purchase data from supplier filings. Usually hard to manipulate at buyer side.',
  DSCR: 'Debt Service Coverage Ratio = cash available for debt service / debt obligations.',
  SARFAESI:
    'Indian law enabling secured creditors to enforce security interests without court intervention.',
  NCLT: 'National Company Law Tribunal; handles insolvency and corporate disputes.',
  CIRP: 'Corporate Insolvency Resolution Process under Insolvency and Bankruptcy Code.',
};

export default function ExplainPage() {
  const [explain, setExplain] = useState<any>(null);
  const [companyId, setCompanyId] = useState('');

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
  }, []);

  useEffect(() => {
    if (!companyId) return;
    getExplainV1(companyId).then((res) => setExplain(res.data)).catch(console.error);
  }, [companyId]);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h1 className="text-2xl font-bold text-white">Explainability Center</h1>
          <p className="text-slate-300 mt-2">
            Every score component below can be traced to explicit model inputs and rule logic.
          </p>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-3">Decision Narrative</h2>
          <p className="text-slate-200 whitespace-pre-wrap">
            {explain?.decision_narrative || 'No explanation found yet.'}
          </p>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-3">Top Positive Factors</h2>
          <ul className="space-y-2 text-green-300 text-sm">
            {(explain?.top_positive_factors || []).map((f: string, i: number) => (
              <li key={i}>• {f}</li>
            ))}
          </ul>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-3">Top Negative Factors</h2>
          <ul className="space-y-2 text-red-300 text-sm">
            {(explain?.top_negative_factors || []).map((f: string, i: number) => (
              <li key={i}>• {f}</li>
            ))}
          </ul>
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h2 className="text-white font-semibold mb-4">India Context Tooltips</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(INDIA_TOOLTIPS).map(([term, meaning]) => (
              <div key={term} className="p-3 rounded bg-slate-900/50 border border-slate-700">
                <p className="text-cyan-300 font-semibold">{term}</p>
                <p className="text-slate-300 text-sm mt-1">{meaning}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
