'use client';

import { useEffect, useMemo, useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  Cell,
} from 'recharts';

import {
  getExplainV1,
  getResearchV1,
  getResultsV1,
  getReportUrlV1,
} from '@/lib/api';
import FiveCsRadar from '@/components/FiveCsRadar';
import TimelineView from '@/components/TimelineView';
import ResearchFeed from '@/components/ResearchFeed';
import ShapChart from '@/components/ShapChart';
import AnomalyFlags from '@/components/AnomalyFlags';
import StressTestPanel from '@/components/StressTestPanel';
import FraudGraph from '@/components/FraudGraph';

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default function ResultsPage() {
  const [result, setResult] = useState<any>(null);
  const [explain, setExplain] = useState<any>(null);
  const [research, setResearch] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusMessage, setStatusMessage] = useState('Loading analysis results...');
  const [companyId, setCompanyId] = useState('');

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
  }, []);

  useEffect(() => {
    let cancelled = false;

    const load = async () => {
      if (!companyId) {
        setLoading(false);
        setStatusMessage('No company selected. Please upload documents first.');
        return;
      }

      try {
        let latestResult: any = null;
        for (let i = 0; i < 120; i += 1) {
          const res = await getResultsV1(companyId);
          latestResult = res.data;
          const runStatus = String(latestResult?.status || res.status || '').toLowerCase();
          if (runStatus === 'error') {
            setStatusMessage(latestResult?.error_message || 'Analysis failed.');
            break;
          }
          if (runStatus !== 'processing' && latestResult?.decision) {
            break;
          }
          setStatusMessage(`Analysis in progress: ${latestResult?.current_step || 'INITIALIZING'}...`);
          await sleep(1200);
        }

        if (!cancelled) {
          setResult(latestResult);
        }

        const explainRes = await getExplainV1(companyId).catch(() => null);
        const researchRes = await getResearchV1(companyId).catch(() => null);

        if (!cancelled) {
          setExplain(explainRes?.data || null);
          setResearch(researchRes?.data || []);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setStatusMessage('Unable to load analysis yet. Retrying from pipeline is recommended.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void load();
    return () => {
      cancelled = true;
    };
  }, [companyId]);

  const decision = result?.decision || {};
  const score = Number(decision.credit_score || 0);
  const dueDiligence = result?.due_diligence || {};
  const borrowerContext = dueDiligence?.borrower_context || {};
  const humanImpactPoints = Number(decision?.human_input_impact_points || 0);
  const hasBorrowerInput = Object.values(borrowerContext).some(
    (value) => String(value || '').trim().length > 0
  );
  const fiveC = useMemo(() => {
    const f = result?.features || {};
    return {
      character: Math.min(10, Math.max(0, Number(f.management_integrity_score || 6) / 1.2)),
      capacity: Math.min(10, Math.max(0, Number(f.dscr || 1.2) * 3)),
      capital: Math.min(10, Math.max(0, 8.5 - Number(f.debt_equity_ratio || 1.5))),
      collateral: Math.min(10, Math.max(0, Number(f.collateral_coverage_ratio || 1.1) * 4)),
      conditions: Math.min(
        10,
        Math.max(
          0,
          8 - Number(f.has_sector_headwinds || 0) * 2 - Number(f.has_revenue_inflation_signals || 0) * 2
        )
      ),
    };
  }, [result]);

  const gstBankData = [
    {
      month: 'FY',
      gst: Number(result?.gst_mismatch?.itc_inflation_percentage || 0) + 100,
      bank: 100,
    },
  ];

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8 text-slate-200">
        {statusMessage}
      </main>
    );
  }

  if (!result || !decision?.credit_score) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8 text-slate-200">
        {statusMessage || 'Results are being prepared. Please keep this page open.'}
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
          <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
          <p className="text-slate-300 mt-2">
            Credit Score: <span className="text-white font-bold">{score.toFixed(0)}</span> / 900
            {'  '}| Grade: <span className="font-bold text-cyan-300">{decision.risk_grade}</span>
            {'  '}| Decision: <span className="font-bold text-emerald-300">{decision.recommendation}</span>
          </p>
          <p className="text-slate-300">
            Recommended amount: ₹{Number(decision.recommended_loan_amount || 0).toFixed(2)} crore
            {'  '}| Interest: {Number(decision.recommended_interest_rate || 0).toFixed(2)}%
          </p>
          <p className="text-slate-300 mt-1">
            Human input impact:{' '}
            <span className={`font-semibold ${humanImpactPoints >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {humanImpactPoints >= 0 ? '+' : ''}
              {humanImpactPoints.toFixed(1)} score points
            </span>
            {'  '}| Borrower input status:{' '}
            <span className={hasBorrowerInput ? 'text-emerald-300 font-semibold' : 'text-amber-300 font-semibold'}>
              {hasBorrowerInput ? 'Captured and used' : 'Not provided'}
            </span>
          </p>
          {result?.cam_docx_path ? (
            <a
              href={getReportUrlV1(companyId)}
              className="inline-block mt-3 px-4 py-2 rounded bg-blue-600 hover:bg-blue-500 text-white"
            >
              Download CAM (.docx)
            </a>
          ) : (
            <p className="text-slate-300 mt-3">CAM generation in progress...</p>
          )}
        </div>

        <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-5">
          <h2 className="text-white text-lg font-semibold">Human Input Traceability</h2>
          {hasBorrowerInput ? (
            <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <p className="text-slate-300">
                Finance officer:{' '}
                <span className="text-white font-medium">
                  {String(borrowerContext.finance_officer_name || 'Not provided')}
                </span>
              </p>
              <p className="text-slate-300">
                Cooperation:{' '}
                <span className="text-white font-medium">
                  {String(borrowerContext.management_cooperation || 'Not provided')}
                </span>
              </p>
              <p className="text-slate-300">
                Capacity utilization:{' '}
                <span className="text-white font-medium">
                  {Number(dueDiligence.factory_capacity_utilization || 0).toFixed(0)}%
                </span>
              </p>
              <p className="text-slate-300">
                Integrity score:{' '}
                <span className="text-white font-medium">
                  {Number(dueDiligence.management_integrity_score || 0).toFixed(1)} / 10
                </span>
              </p>
              <p className="text-slate-300 md:col-span-2">
                Business highlights:{' '}
                <span className="text-white font-medium">
                  {String(borrowerContext.business_highlights || 'Not provided')}
                </span>
              </p>
              <p className="text-slate-300 md:col-span-2">
                Disclosed risks:{' '}
                <span className="text-white font-medium">
                  {String(borrowerContext.disclosed_risks || 'Not provided')}
                </span>
              </p>
            </div>
          ) : (
            <p className="text-slate-300 mt-2">
              No borrower/finance-officer inputs were captured, so score impact from human input is currently
              {` ${humanImpactPoints.toFixed(1)} `} points.
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <FiveCsRadar company={fiveC} />
          <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
            <h3 className="text-white font-semibold text-lg mb-3">GST vs Bank Reconciliation</h3>
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={gstBankData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#5f7752" />
                <XAxis dataKey="month" tick={{ fill: '#dce8d5' }} />
                <YAxis tick={{ fill: '#dce8d5' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#253021',
                    border: '1px solid #6a8b58',
                    color: '#eef6e9',
                  }}
                />
                <Bar dataKey="gst" name="GST Reported Revenue" fill="#8fbf5e">
                  {gstBankData.map((item, idx) => (
                    <Cell
                      key={idx}
                      fill={item.gst - item.bank > 5 ? '#dc2626' : '#8fbf5e'}
                    />
                  ))}
                </Bar>
                <Bar dataKey="bank" name="Bank Credits Received" fill="#4cbb17" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ShapChart
            data={Object.entries(explain?.shap_waterfall_data || {}).map(([feature, value]) => ({
              feature,
              value: Number(value),
              direction: Number(value) > 0 ? 'positive' : 'negative',
            }))}
          />
          <TimelineView
            items={(result?.audit_events || []).map((a: any) => ({
              timestamp: a.timestamp,
              title: a.message,
              severity: a.severity || 'INFORMATIONAL',
              details: a.step,
            }))}
          />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ResearchFeed findings={research} />
          <AnomalyFlags anomalies={result?.cross_validation?.anomalies || []} />
        </div>

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <FraudGraph
            nodes={[
              { id: 'Vardhman', type: 'company' },
              { id: 'Entity B', type: 'counterparty' },
              { id: 'Entity C', type: 'counterparty' },
            ]}
            links={[
              { source: 'Vardhman', target: 'Entity B', value: 40 },
              { source: 'Entity B', target: 'Entity C', value: 38 },
              { source: 'Entity C', target: 'Vardhman', value: 39 },
            ]}
          />
          <StressTestPanel baseScore={score} />
        </div>
      </div>
    </main>
  );
}
