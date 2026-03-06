/**
 * Intelli-Credit Landing Page
 * Company name input with "Start New Appraisal" CTA.
 * Professional dark blue banking aesthetic.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const [companyName, setCompanyName] = useState('');
  const router = useRouter();

  const handleStart = () => {
    if (companyName.trim()) {
      localStorage.setItem('companyName', companyName.trim());
      router.push('/upload');
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 flex items-center justify-center">
      <div className="max-w-2xl w-full mx-4">
        {/* Logo / Title */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-3">
            Intelli-<span className="text-blue-400">Credit</span>
          </h1>
          <p className="text-blue-200 text-lg">
            AI-Powered Credit Appraisal Engine for Indian Corporate Lending
          </p>
          <p className="text-slate-400 text-sm mt-2">
            IIT Hyderabad × Vivriti Capital
          </p>
        </div>

        {/* Input Card */}
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-2xl p-8 border border-slate-700 shadow-2xl">
          <label className="block text-slate-300 text-sm font-medium mb-2">
            Company Name
          </label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            placeholder="e.g. Sharma Textiles Pvt Ltd"
            className="w-full px-4 py-3 bg-slate-900/60 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
          />

          <button
            onClick={handleStart}
            disabled={!companyName.trim()}
            className="w-full mt-6 py-3 px-6 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold rounded-xl transition-all duration-200 text-lg shadow-lg shadow-blue-600/25"
          >
            Start New Appraisal →
          </button>
        </div>

        {/* Features */}
        <div className="grid grid-cols-3 gap-4 mt-8">
          {[
            { icon: '📄', label: 'Multi-format OCR', desc: '22 Indian languages' },
            { icon: '🔍', label: 'Web Research', desc: 'MCA21 + eCourts + RBI' },
            { icon: '📊', label: 'SHAP Explainability', desc: 'Every decision traced' },
          ].map((f, i) => (
            <div key={i} className="text-center p-4 bg-slate-800/30 rounded-xl border border-slate-700/50">
              <div className="text-2xl mb-2">{f.icon}</div>
              <div className="text-white text-sm font-medium">{f.label}</div>
              <div className="text-slate-400 text-xs">{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
