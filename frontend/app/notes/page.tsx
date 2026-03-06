'use client';

import { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { previewDueDiligenceV1, submitDueDiligenceV1 } from '@/lib/api';

function useDebounce<T>(value: T, delay = 600): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const id = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(id);
  }, [value, delay]);
  return debounced;
}

export default function DueDiligencePage() {
  const router = useRouter();
  const [companyId, setCompanyId] = useState('');
  const [companyName, setCompanyName] = useState('Unknown Company');

  const [factoryVisitDate, setFactoryVisitDate] = useState('');
  const [capacity, setCapacity] = useState(68);
  const [factoryCondition, setFactoryCondition] = useState('GOOD');
  const [inventoryLevels, setInventoryLevels] = useState('ADEQUATE');
  const [managementCooperation, setManagementCooperation] = useState('COOPERATIVE');
  const [notes, setNotes] = useState('');
  const [interviewRating, setInterviewRating] = useState(3);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
    setCompanyName(localStorage.getItem('companyName') || 'Unknown Company');
  }, []);

  const debouncedNotes = useDebounce(notes, 650);
  const charCount = notes.length;

  useEffect(() => {
    if (!debouncedNotes.trim()) return;
    previewDueDiligenceV1(companyName, debouncedNotes)
      .then((res) => setPreview(res.data))
      .catch(() => setPreview(null));
  }, [companyName, debouncedNotes]);

  const handleSubmit = async () => {
    if (!notes.trim() || !companyId) return;
    setLoading(true);
    setError('');
    try {
      await submitDueDiligenceV1(companyId, {
        factory_visit_date: factoryVisitDate || undefined,
        capacity_utilization_percent: capacity,
        factory_condition: factoryCondition,
        inventory_levels: inventoryLevels,
        management_cooperation: managementCooperation,
        free_text_notes: notes,
        management_interview_rating: interviewRating,
        key_management_persons: [],
      });
      router.push('/pipeline');
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8">
      <div className="max-w-5xl mx-auto grid grid-cols-1 xl:grid-cols-3 gap-6">
        <section className="xl:col-span-2 bg-slate-800/50 border border-slate-700 rounded-xl p-6">
          <h1 className="text-3xl font-bold text-white mb-2">Due Diligence Portal</h1>
          <p className="text-slate-300 mb-6">
            Credit Officer input for <span className="font-semibold text-white">{companyName}</span>
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="text-slate-300 text-sm">
              Factory Visit Date
              <input
                type="date"
                value={factoryVisitDate}
                onChange={(e) => setFactoryVisitDate(e.target.value)}
                className="mt-1 w-full rounded-lg bg-slate-900/70 border border-slate-600 px-3 py-2 text-white"
              />
            </label>

            <label className="text-slate-300 text-sm">
              Management Interview Rating ({interviewRating}/5)
              <input
                type="range"
                min={1}
                max={5}
                value={interviewRating}
                onChange={(e) => setInterviewRating(Number(e.target.value))}
                className="mt-2 w-full accent-blue-500"
              />
            </label>
          </div>

          <div className="mt-4">
            <label className="block text-slate-300 text-sm mb-2">
              Capacity Utilization ({capacity}%)
            </label>
            <input
              type="range"
              min={0}
              max={100}
              value={capacity}
              onChange={(e) => setCapacity(Number(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <select
              value={factoryCondition}
              onChange={(e) => setFactoryCondition(e.target.value)}
              className="rounded-lg bg-slate-900/70 border border-slate-600 px-3 py-2 text-white"
            >
              {['EXCELLENT', 'GOOD', 'FAIR', 'POOR'].map((x) => (
                <option key={x} value={x}>{x}</option>
              ))}
            </select>
            <select
              value={inventoryLevels}
              onChange={(e) => setInventoryLevels(e.target.value)}
              className="rounded-lg bg-slate-900/70 border border-slate-600 px-3 py-2 text-white"
            >
              {['ADEQUATE', 'LOW', 'EXCESS', 'SUSPICIOUS'].map((x) => (
                <option key={x} value={x}>{x}</option>
              ))}
            </select>
            <select
              value={managementCooperation}
              onChange={(e) => setManagementCooperation(e.target.value)}
              className="rounded-lg bg-slate-900/70 border border-slate-600 px-3 py-2 text-white"
            >
              {['COOPERATIVE', 'EVASIVE', 'REFUSED'].map((x) => (
                <option key={x} value={x}>{x}</option>
              ))}
            </select>
          </div>

          <div className="mt-4">
            <label className="block text-slate-300 text-sm mb-2">Free-text Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={8}
              placeholder="Mention production, order-book, utilization, inventory quality, management behavior..."
              className="w-full rounded-xl bg-slate-900/70 border border-slate-600 px-4 py-3 text-white"
            />
            <p className="text-xs text-slate-400 mt-1">{charCount} characters</p>
          </div>

          {error && <p className="text-red-300 text-sm mt-3">{error}</p>}

          <button
            onClick={handleSubmit}
            disabled={loading || !notes.trim()}
            className="w-full mt-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-600 text-white font-semibold"
          >
            {loading ? 'Submitting...' : 'Submit Due Diligence'}
          </button>
        </section>

        <aside className="bg-slate-800/50 border border-slate-700 rounded-xl p-6 h-fit">
          <h2 className="text-white font-semibold mb-3">Live AI Analysis</h2>
          {!preview ? (
            <p className="text-slate-400 text-sm">
              Start typing notes to see extracted risk flags in real-time.
            </p>
          ) : (
            <div className="space-y-3 text-sm">
              <p className="text-slate-200">
                Sentiment: <span className="font-semibold">{preview.sentiment}</span>
              </p>
              <p className="text-red-300 font-medium">Risk Factors</p>
              <ul className="text-red-200 space-y-1">
                {(preview.risk_factors || []).map((x: string, i: number) => (
                  <li key={i}>• {x}</li>
                ))}
              </ul>
              <p className="text-green-300 font-medium">Positive Factors</p>
              <ul className="text-green-200 space-y-1">
                {(preview.positive_factors || []).map((x: string, i: number) => (
                  <li key={i}>• {x}</li>
                ))}
              </ul>
              <p className="text-slate-200">
                Suggested Adjustment:{' '}
                <span className="font-semibold">{Number(preview.score_adjustment).toFixed(1)}</span>
              </p>
            </div>
          )}
        </aside>
      </div>
    </main>
  );
}
