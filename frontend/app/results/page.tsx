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
import { useAnalysisStore } from '@/store/analysisStore';
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
  const { companyId, uploadedFileNames, setResult: storeResult } = useAnalysisStore();

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
          if (runStatus !== 'processing' && latestResult?.decision) break;
          setStatusMessage(`Analysis in progress: ${latestResult?.current_step || 'INITIALIZING'}...`);
          await sleep(1200);
        }

        if (!cancelled) {
          setResult(latestResult);
          storeResult(latestResult);
        }

        const explainRes = await getExplainV1(companyId).catch(() => null);
        const researchRes = await getResearchV1(companyId).catch(() => null);

        if (!cancelled) {
          setExplain(explainRes?.data || null);
          setResearch(researchRes?.data || []);
        }
      } catch (err) {
        console.error(err);
        if (!cancelled) setStatusMessage('Unable to load analysis yet. Retrying from pipeline is recommended.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    void load();
    return () => { cancelled = true; };
  }, [companyId, storeResult]);

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
      conditions: Math.min(10, Math.max(0, 8 - Number(f.has_sector_headwinds || 0) * 2 - Number(f.has_revenue_inflation_signals || 0) * 2)),
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
      <div className="bg-ic-page py-10 px-8 min-h-[calc(100vh-56px)]">
        <p className="text-ic-muted animate-pulse">{statusMessage}</p>
      </div>
    );
  }

  if (!result || !decision?.credit_score) {
    return (
      <div className="bg-ic-page py-10 px-8 min-h-[calc(100vh-56px)]">
        <p className="text-ic-muted">{statusMessage || 'Results are being prepared. Please keep this page open.'}</p>
      </div>
    );
  }

  const chartTooltipStyle = {
    backgroundColor: 'var(--ic-surface)',
    border: '1px solid var(--ic-border)',
    color: 'var(--ic-text)',
    borderRadius: '8px',
  };

  return (
    <div className="bg-ic-page py-10 px-4 md:px-8">
      <div className="max-w-[1200px] mx-auto">
        {/* CSS Grid layout */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
          {/* Score summary — spans 2 cols */}
          <div className="xl:col-span-2 bg-ic-surface border border-ic-border rounded-[10px] p-5">
            <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Analysis Results</p>
            <div className="flex flex-wrap gap-4 items-baseline">
              <span className="font-display text-[32px] text-ic-text">{score.toFixed(0)}</span>
              <span className="text-ic-muted text-[14px]">/ 900</span>
              <span className="font-mono text-[13px] bg-ic-accent-light text-ic-accent px-2 py-0.5 rounded">{decision.risk_grade}</span>
              <span className="font-mono text-[13px] bg-ic-accent-light text-ic-positive px-2 py-0.5 rounded">{decision.recommendation}</span>
            </div>
            <p className="text-ic-muted text-[13px] mt-2">
              Recommended: <span className="font-mono text-ic-text">₹{Number(decision.recommended_loan_amount || 0).toFixed(2)} Cr</span>
              {' · '}Interest: <span className="font-mono text-ic-text">{Number(decision.recommended_interest_rate || 0).toFixed(2)}%</span>
            </p>
            <div className="flex flex-wrap gap-4 mt-2 text-[12px]">
              <span className="text-ic-muted">
                Human input: <span className={`font-mono font-medium ${humanImpactPoints >= 0 ? 'text-ic-positive' : 'text-ic-negative'}`}>
                  {humanImpactPoints >= 0 ? '+' : ''}{humanImpactPoints.toFixed(1)} pts
                </span>
              </span>
              <span className="text-ic-muted">
                Borrower input: <span className={`font-medium ${hasBorrowerInput ? 'text-ic-positive' : 'text-ic-warning'}`}>
                  {hasBorrowerInput ? 'Captured' : 'Not provided'}
                </span>
              </span>
            </div>
            {result?.cam_docx_path && (
              <a
                href={getReportUrlV1(companyId)}
                className="inline-block mt-3 px-4 py-2 rounded-[6px] bg-ic-accent text-white text-[12px] font-medium no-underline hover:opacity-90"
              >
                Download CAM (.docx)
              </a>
            )}
          </div>

          {/* Anomaly flags */}
          <div className="xl:col-span-1">
            <AnomalyFlags anomalies={result?.cross_validation?.anomalies || []} />
          </div>

          {/* Five Cs Radar + GST chart — spans 2 cols */}
          <div className="xl:col-span-2 space-y-5">
            <FiveCsRadar company={fiveC} />

            <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
              <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">GST vs Bank Reconciliation</p>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={gstBankData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--ic-border)" />
                  <XAxis dataKey="month" tick={{ fill: 'var(--ic-muted)', fontSize: 12, fontFamily: 'DM Mono' }} />
                  <YAxis tick={{ fill: 'var(--ic-muted)', fontSize: 12, fontFamily: 'DM Mono' }} />
                  <Tooltip contentStyle={chartTooltipStyle} />
                  <Bar dataKey="gst" name="GST Reported Revenue" fill="var(--ic-accent)">
                    {gstBankData.map((item, idx) => (
                      <Cell key={idx} fill={item.gst - item.bank > 5 ? 'var(--ic-negative)' : 'var(--ic-accent)'} />
                    ))}
                  </Bar>
                  <Bar dataKey="bank" name="Bank Credits Received" fill="var(--ic-tan)" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* SHAP + Timeline */}
            <ShapChart
              data={Object.entries(explain?.shap_waterfall_data || {}).map(([feature, value]) => ({
                feature,
                value: Number(value),
                direction: Number(value) > 0 ? 'positive' : 'negative',
              }))}
            />

            <StressTestPanel baseScore={score} />
          </div>

          {/* Right sidebar — sticky */}
          <div className="xl:col-span-1 space-y-5 xl:sticky xl:top-[72px] xl:self-start">
            {/* Human input traceability */}
            <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
              <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Human Input Traceability</p>
              {hasBorrowerInput ? (
                <div className="space-y-2 text-[12px]">
                  <p className="text-ic-muted">Finance officer: <span className="text-ic-text font-medium">{String(borrowerContext.finance_officer_name || 'N/A')}</span></p>
                  <p className="text-ic-muted">Cooperation: <span className="text-ic-text font-medium">{String(borrowerContext.management_cooperation || 'N/A')}</span></p>
                  <p className="text-ic-muted">Capacity: <span className="font-mono text-ic-text">{Number(dueDiligence.factory_capacity_utilization || 0).toFixed(0)}%</span></p>
                  <p className="text-ic-muted">Integrity: <span className="font-mono text-ic-text">{Number(dueDiligence.management_integrity_score || 0).toFixed(1)}/10</span></p>
                </div>
              ) : (
                <p className="text-ic-muted text-[12px]">No borrower inputs captured.</p>
              )}
            </div>

            {/* Documents card */}
            {uploadedFileNames.length > 0 && (
              <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
                <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Documents</p>
                <div className="space-y-1.5">
                  {uploadedFileNames.map((name, i) => (
                    <div key={i} className="flex items-center gap-2 text-[12px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-ic-positive flex-shrink-0" />
                      <span className="font-mono text-ic-text truncate">{name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <TimelineView
              items={(result?.audit_events || []).map((a: any) => ({
                timestamp: a.timestamp,
                title: a.message,
                severity: a.severity || 'INFORMATIONAL',
                details: a.step,
              }))}
            />

            <ResearchFeed findings={research} />
          </div>
        </div>

        {/* Full width: Fraud Graph */}
        <div className="mt-5">
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
        </div>
      </div>
    </div>
  );
}
