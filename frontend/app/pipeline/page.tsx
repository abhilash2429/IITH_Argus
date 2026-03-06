/**
 * Pipeline Progress Page
 * Shows AgentProgressLog. When HITL reached, shows qualitative notes button.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import AgentProgressLog from '@/components/AgentProgressLog';

const FLOW_STEPS = [
  {
    title: '1. Document Understanding',
    subtitle: 'Reading uploaded files and extracting key data',
    color: 'from-lime-400 to-green-500',
  },
  {
    title: '2. Financial Consistency Checks',
    subtitle: 'GST, banking, and tax return cross-checks',
    color: 'from-green-500 to-emerald-500',
  },
  {
    title: '3. Public & Regulatory Research',
    subtitle: 'News, litigation, MCA, and compliance scan',
    color: 'from-emerald-500 to-green-600',
  },
  {
    title: '4. Risk Scoring',
    subtitle: 'Policy rules + model-based risk estimation',
    color: 'from-green-600 to-lime-500',
  },
  {
    title: '5. CAM Draft Generation',
    subtitle: 'Compiles decision rationale and recommendation',
    color: 'from-lime-500 to-emerald-500',
  },
];

export default function PipelinePage() {
  const [hitlReached, setHitlReached] = useState(false);
  const [complete, setComplete] = useState(false);
  const [companyId, setCompanyId] = useState('');
  const [companyName, setCompanyName] = useState('');
  const router = useRouter();

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
    setCompanyName(localStorage.getItem('companyName') || '');
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-cyan-900 via-blue-900 to-indigo-900 p-6 md:p-10">
      <div className="max-w-6xl mx-auto space-y-6">
        <section className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 md:p-8">
          <h1 className="text-4xl font-bold text-white mb-2">CAM Analysis in Progress</h1>
          <p className="text-cyan-100 text-lg">
            Company: <span className="font-semibold text-white">{companyName || 'Not selected'}</span>
          </p>
          <p className="text-cyan-200/90 mt-1">
            We are preparing a credit appraisal memo in clear stages.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-amber-200/40 bg-amber-400/20 px-4 py-1 text-amber-100 text-sm">
            <span className="h-2 w-2 rounded-full bg-amber-300" />
            Updated flow view: simplified stage language + cleaner progress tracking
          </div>
        </section>

        <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-3">
          {FLOW_STEPS.map((step) => (
            <article key={step.title} className="rounded-2xl border border-white/20 bg-white/10 p-4">
              <div className={`h-1.5 rounded-full bg-gradient-to-r ${step.color} mb-3`} />
              <h2 className="text-white font-semibold text-sm">{step.title}</h2>
              <p className="text-cyan-100/80 text-xs mt-1">{step.subtitle}</p>
            </article>
          ))}
        </section>

        <section className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-5">
        {companyId ? (
          <AgentProgressLog
            companyId={companyId}
            onHitlReached={() => setHitlReached(true)}
            onComplete={() => setComplete(true)}
          />
        ) : (
          <p className="text-red-200 bg-red-950/40 border border-red-400/40 rounded-xl p-4">
            No company found. Please start from the Upload page.
          </p>
        )}
        </section>

        <section className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-5">
          <p className="text-white font-semibold">Human-in-the-loop checkpoints</p>
          <p className="text-cyan-100/90 text-sm mt-2">
            Borrower-side inputs from upload and credit-officer notes from review are both added to the final CAM rationale.
          </p>
        </section>

        <div className="mt-2 flex flex-wrap gap-4">
          {hitlReached && !complete && (
            <button
              onClick={() => router.push('/notes')}
              className="py-3 px-6 bg-amber-400 hover:bg-amber-300 text-slate-900 font-semibold rounded-xl transition-all shadow-lg"
            >
              Add credit officer notes
            </button>
          )}

          {complete && (
            <>
              <button
                onClick={() => router.push('/results')}
                className="py-3 px-6 bg-green-500 hover:bg-green-400 text-slate-900 font-semibold rounded-xl transition-all shadow-lg"
              >
                View results
              </button>
              <button
                onClick={() => router.push('/explain')}
                className="py-3 px-6 bg-lime-500 hover:bg-lime-400 text-slate-900 font-semibold rounded-xl transition-all shadow-lg"
              >
                Why this decision
              </button>
              <button
                onClick={() => router.push('/cam')}
                className="py-3 px-6 bg-emerald-400 hover:bg-emerald-300 text-slate-900 font-semibold rounded-xl transition-all shadow-lg"
              >
                Open CAM report
              </button>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
