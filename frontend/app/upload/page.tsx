'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import UploadZone from '@/components/UploadZone';
import {
  createCompanyV1,
  getIntegrationHealthV1,
  previewDueDiligenceV1,
  submitDueDiligenceV1,
  triggerAnalysisV1,
  uploadDocumentsV1,
} from '@/lib/api';

const UPLOAD_STAGES = [
  'Documents received',
  'Reading files',
  'Tax and bank checks',
];

export default function UploadPage() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [companyName, setCompanyName] = useState('Vardhman Agri Processing Pvt. Ltd.');
  const [sector, setSector] = useState('agri_processing');
  const [loanAmount, setLoanAmount] = useState(50);
  const [loanPurpose, setLoanPurpose] = useState('working_capital');
  const [loading, setLoading] = useState(false);
  const [activeStage, setActiveStage] = useState<number>(-1);
  const [error, setError] = useState('');
  const [optionalOpen, setOptionalOpen] = useState(true);
  const [integrationHealth, setIntegrationHealth] = useState<any | null>(null);
  const [integrationLoading, setIntegrationLoading] = useState(false);
  const [integrationError, setIntegrationError] = useState('');
  const [duePreview, setDuePreview] = useState<any | null>(null);
  const [duePreviewLoading, setDuePreviewLoading] = useState(false);

  // Optional finance officer inputs (borrower-side context)
  const [financeOfficerName, setFinanceOfficerName] = useState('');
  const [financeOfficerRole, setFinanceOfficerRole] = useState('Finance Officer');
  const [financeOfficerEmail, setFinanceOfficerEmail] = useState('');
  const [financeOfficerPhone, setFinanceOfficerPhone] = useState('');
  const [capacityPct, setCapacityPct] = useState(70);
  const [inventoryLevel, setInventoryLevel] = useState('ADEQUATE');
  const [managementCooperation, setManagementCooperation] = useState('COOPERATIVE');
  const [businessHighlights, setBusinessHighlights] = useState('');
  const [keyRisksDisclosed, setKeyRisksDisclosed] = useState('');
  const [majorCustomers, setMajorCustomers] = useState('');
  const [contingentLiabilities, setContingentLiabilities] = useState('');
  const [plannedCapex, setPlannedCapex] = useState('');

  useEffect(() => {
    setCompanyName(localStorage.getItem('companyName') || 'Vardhman Agri Processing Pvt. Ltd.');
  }, []);

  const checkIntegrations = async (liveChecks: boolean) => {
    setIntegrationLoading(true);
    setIntegrationError('');
    try {
      const res = await getIntegrationHealthV1(liveChecks);
      setIntegrationHealth(res.data);
    } catch (err: any) {
      setIntegrationError(err?.response?.data?.detail || err?.message || 'Unable to fetch integration health');
    } finally {
      setIntegrationLoading(false);
    }
  };

  useEffect(() => {
    void checkIntegrations(false);
  }, []);

  const hasOptionalInputs = Boolean(
    financeOfficerName.trim() ||
      financeOfficerEmail.trim() ||
      financeOfficerPhone.trim() ||
      businessHighlights.trim() ||
      keyRisksDisclosed.trim() ||
      majorCustomers.trim() ||
      contingentLiabilities.trim() ||
      plannedCapex.trim() ||
      capacityPct !== 70 ||
      inventoryLevel !== 'ADEQUATE' ||
      managementCooperation !== 'COOPERATIVE'
  );

  const buildDueDiligenceNotes = () => {
    const lines = [
      `Borrower finance officer name: ${financeOfficerName || 'Not provided'}`,
      `Role: ${financeOfficerRole || 'Not provided'}`,
      `Email: ${financeOfficerEmail || 'Not provided'}`,
      `Phone: ${financeOfficerPhone || 'Not provided'}`,
      `Business highlights: ${businessHighlights || 'Not provided'}`,
      `Key risks disclosed by borrower: ${keyRisksDisclosed || 'Not provided'}`,
      `Major customers and concentration: ${majorCustomers || 'Not provided'}`,
      `Contingent liabilities: ${contingentLiabilities || 'Not provided'}`,
      `Planned capex / expansion: ${plannedCapex || 'Not provided'}`,
    ];
    return lines.join('\n');
  };

  useEffect(() => {
    let cancelled = false;

    if (!hasOptionalInputs) {
      setDuePreview(null);
      return;
    }

    const timer = setTimeout(async () => {
      setDuePreviewLoading(true);
      try {
        const response = await previewDueDiligenceV1(
          companyName || 'Borrower',
          buildDueDiligenceNotes()
        );
        if (!cancelled) {
          setDuePreview(response.data);
        }
      } catch {
        if (!cancelled) {
          setDuePreview(null);
        }
      } finally {
        if (!cancelled) {
          setDuePreviewLoading(false);
        }
      }
    }, 450);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
  }, [
    hasOptionalInputs,
    companyName,
    financeOfficerName,
    financeOfficerRole,
    financeOfficerEmail,
    financeOfficerPhone,
    capacityPct,
    inventoryLevel,
    managementCooperation,
    businessHighlights,
    keyRisksDisclosed,
    majorCustomers,
    contingentLiabilities,
    plannedCapex,
  ]);

  const startAnalysis = async () => {
    if (!files.length || !companyName.trim()) return;
    setLoading(true);
    setError('');
    let failedStep = 'starting analysis';
    try {
      setActiveStage(0);
      failedStep = 'creating company profile';
      const companyRes = await createCompanyV1({
        name: companyName,
        sector,
        loan_amount_requested: loanAmount,
        loan_tenor_months: 36,
        loan_purpose: loanPurpose,
      });
      const companyId = companyRes.data.company_id;
      localStorage.setItem('companyId', companyId);
      localStorage.setItem('companyName', companyName);

      // Optional borrower-side qualitative context for CAM
      if (hasOptionalInputs) {
        failedStep = 'submitting borrower context';
        await submitDueDiligenceV1(companyId, {
          capacity_utilization_percent: capacityPct,
          inventory_levels: inventoryLevel,
          management_cooperation: managementCooperation,
          free_text_notes: buildDueDiligenceNotes(),
          key_management_persons: financeOfficerName.trim()
            ? [
                {
                  name: financeOfficerName.trim(),
                  role: financeOfficerRole.trim() || 'Finance Officer',
                  notes: 'Borrower representative input captured at application time.',
                },
              ]
            : [],
          borrower_finance_officer_name: financeOfficerName || undefined,
          borrower_finance_officer_role: financeOfficerRole || undefined,
          borrower_finance_officer_email: financeOfficerEmail || undefined,
          borrower_finance_officer_phone: financeOfficerPhone || undefined,
          borrower_business_highlights: businessHighlights || undefined,
          borrower_major_customers: majorCustomers || undefined,
          borrower_contingent_liabilities: contingentLiabilities || undefined,
          borrower_planned_capex: plannedCapex || undefined,
          borrower_disclosed_risks: keyRisksDisclosed || undefined,
        });
      }

      setActiveStage(1);
      failedStep = 'uploading documents';
      await uploadDocumentsV1(companyId, files);

      setActiveStage(2);
      failedStep = 'triggering pipeline';
      await triggerAnalysisV1(companyId);
      setActiveStage(3);
      await new Promise((resolve) => setTimeout(resolve, 250));

      router.push('/pipeline');
    } catch (err: any) {
      const rawMessage = String(err?.response?.data?.detail || err?.message || 'Upload failed');
      if (rawMessage.toLowerCase().includes('network error')) {
        setError(
          `Network error while ${failedStep}. Backend API is not reachable on localhost:8001/8000. Start backend and retry.`
        );
      } else {
        setError(rawMessage);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-cyan-900 via-blue-900 to-indigo-900 p-6 md:p-10">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 md:p-8">
          <h1 className="text-4xl font-bold text-white">Loan Application Upload</h1>
          <p className="text-cyan-50 mt-2 text-lg">
            Add company details, upload documents, and start CAM preparation.
          </p>
          <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-cyan-200/40 bg-cyan-400/20 px-4 py-1 text-cyan-100 text-sm">
            <span className="h-2 w-2 rounded-full bg-cyan-300" />
            UX refresh active: finance officer input is included in CAM context
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="text-white text-xl font-semibold">Tool connectivity</p>
              <p className="text-cyan-100/90 text-sm">
                Databricks, Qwen OCR, Gemini/LLM, and Firecrawl readiness for this run.
              </p>
            </div>
            <button
              type="button"
              onClick={() => checkIntegrations(true)}
              className="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold disabled:bg-slate-600"
              disabled={integrationLoading}
            >
              {integrationLoading ? 'Checking...' : 'Run live check'}
            </button>
          </div>
          {integrationError && (
            <p className="text-red-200 text-sm bg-red-950/40 border border-red-400/40 rounded-lg p-3">
              {integrationError}
            </p>
          )}
          {integrationHealth?.integrations && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(integrationHealth.integrations).map(([tool, info]: [string, any]) => (
                <div key={tool} className="rounded-lg border border-cyan-300/30 bg-slate-900/50 p-3">
                  <p className="text-cyan-100 font-semibold capitalize">{tool.replace('_', ' ')}</p>
                  <p className="text-sm text-cyan-50/90">
                    Configured: {info.configured ? 'Yes' : 'No'} | Status: {info.ok ? 'OK' : 'Issue'}
                  </p>
                  {(info.provider || info.model || info.method || info.ping !== undefined) && (
                    <p className="text-xs text-cyan-100/80 mt-1">
                      {info.provider ? `Provider: ${info.provider}. ` : ''}
                      {info.model ? `Model: ${info.model}. ` : ''}
                      {info.method ? `Method: ${info.method}. ` : ''}
                      {info.ping !== undefined ? `Ping: ${String(info.ping)}.` : ''}
                    </p>
                  )}
                  {info.hint && (
                    <p className="text-xs text-amber-100 mt-1 break-words">Hint: {String(info.hint)}</p>
                  )}
                  {info.error && (
                    <p className="text-xs text-red-200 mt-1 break-words">Error: {String(info.error)}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 space-y-4">
          <p className="text-white text-xl font-semibold">Basic application details</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="md:col-span-2 text-cyan-50 text-sm">
              Company name
              <input
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="Example: Vizag Steel Works Pvt Ltd"
                className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
              />
            </label>

            <label className="text-cyan-50 text-sm">
              Requested loan amount (INR crore)
              <input
                type="number"
                value={loanAmount}
                onChange={(e) => setLoanAmount(Number(e.target.value))}
                className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                placeholder="Example: 50"
              />
              <span className="mt-1 block text-cyan-100/80 text-xs">
                This is the requested facility amount, not a risk score.
              </span>
            </label>

            <label className="text-cyan-50 text-sm md:col-span-2">
              Sector
              <select
                value={sector}
                onChange={(e) => setSector(e.target.value)}
                className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
              >
                {['agri_processing', 'manufacturing', 'nbfc', 'real_estate', 'textiles', 'it_services'].map((s) => (
                  <option key={s} value={s}>
                    {s.replace('_', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </label>

            <label className="text-cyan-50 text-sm">
              Loan purpose
              <select
                value={loanPurpose}
                onChange={(e) => setLoanPurpose(e.target.value)}
                className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
              >
                <option value="working_capital">Working Capital</option>
                <option value="term_loan">Term Loan</option>
                <option value="capex">Capex</option>
                <option value="refinance">Refinance</option>
              </select>
            </label>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6">
          <UploadZone onFilesReady={setFiles} />
        </div>

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 space-y-4">
          <button
            type="button"
            onClick={() => setOptionalOpen((prev) => !prev)}
            className="w-full flex items-center justify-between text-left text-white font-semibold text-lg"
          >
            <span>Optional borrower input (Finance Officer)</span>
            <span>{optionalOpen ? 'Hide' : 'Add details'}</span>
          </button>
          {optionalOpen && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="text-cyan-50 text-sm">
                Finance officer name
                <input
                  value={financeOfficerName}
                  onChange={(e) => setFinanceOfficerName(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Role
                <input
                  value={financeOfficerRole}
                  onChange={(e) => setFinanceOfficerRole(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Email
                <input
                  type="email"
                  value={financeOfficerEmail}
                  onChange={(e) => setFinanceOfficerEmail(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Phone
                <input
                  value={financeOfficerPhone}
                  onChange={(e) => setFinanceOfficerPhone(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Capacity utilization ({capacityPct}%)
                <input
                  type="range"
                  min={0}
                  max={100}
                  value={capacityPct}
                  onChange={(e) => setCapacityPct(Number(e.target.value))}
                  className="mt-2 w-full accent-cyan-400"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Inventory situation
                <select
                  value={inventoryLevel}
                  onChange={(e) => setInventoryLevel(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                >
                  <option value="ADEQUATE">Adequate</option>
                  <option value="LOW">Low</option>
                  <option value="EXCESS">Excess</option>
                  <option value="SUSPICIOUS">Needs review</option>
                </select>
              </label>
              <label className="text-cyan-50 text-sm">
                Management cooperation
                <select
                  value={managementCooperation}
                  onChange={(e) => setManagementCooperation(e.target.value)}
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                >
                  <option value="COOPERATIVE">Cooperative</option>
                  <option value="EVASIVE">Evasive</option>
                  <option value="REFUSED">Refused key clarifications</option>
                </select>
              </label>
              <label className="text-cyan-50 text-sm">
                Major customers (optional)
                <input
                  value={majorCustomers}
                  onChange={(e) => setMajorCustomers(e.target.value)}
                  placeholder="Top buyers and concentration"
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm md:col-span-2">
                Business highlights
                <textarea
                  value={businessHighlights}
                  onChange={(e) => setBusinessHighlights(e.target.value)}
                  rows={3}
                  placeholder="Orders, seasonal trends, plant utilization, operational updates"
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm md:col-span-2">
                Risks disclosed by borrower
                <textarea
                  value={keyRisksDisclosed}
                  onChange={(e) => setKeyRisksDisclosed(e.target.value)}
                  rows={2}
                  placeholder="Any expected disruptions, legal matters, receivable delays"
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Contingent liabilities
                <input
                  value={contingentLiabilities}
                  onChange={(e) => setContingentLiabilities(e.target.value)}
                  placeholder="Guarantees, LC obligations, pending claims"
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
              <label className="text-cyan-50 text-sm">
                Planned capex or expansion
                <input
                  value={plannedCapex}
                  onChange={(e) => setPlannedCapex(e.target.value)}
                  placeholder="Next 12-24 month plans"
                  className="mt-1 w-full rounded-lg bg-slate-900/70 border border-cyan-300/40 px-4 py-2 text-white"
                />
              </label>
            </div>
          )}
          <p className="text-cyan-100/80 text-sm">
            These fields are optional. If provided, they are used as borrower clarifications in risk scoring and CAM.
          </p>
          {hasOptionalInputs && (
            <div className="rounded-xl border border-cyan-300/40 bg-slate-900/45 p-4">
              <p className="text-cyan-100 font-semibold">Estimated borrower-input score adjustment</p>
              <p className="text-cyan-50 text-sm mt-1">
                {duePreviewLoading
                  ? 'Calculating expected impact...'
                  : `${Number(duePreview?.score_adjustment || 0) >= 0 ? '+' : ''}${Number(
                      duePreview?.score_adjustment || 0
                    ).toFixed(1)} raw adjustment (applied in risk scoring and CAM narrative).`}
              </p>
              {!!duePreview?.risk_factors?.length && (
                <p className="text-red-200 text-xs mt-2">
                  Risk cues: {duePreview.risk_factors.slice(0, 4).join(', ')}
                </p>
              )}
              {!!duePreview?.positive_factors?.length && (
                <p className="text-emerald-200 text-xs mt-1">
                  Positive cues: {duePreview.positive_factors.slice(0, 4).join(', ')}
                </p>
              )}
            </div>
          )}
        </div>

        {hasOptionalInputs && (
          <div className="bg-emerald-900/30 border border-emerald-400/40 rounded-2xl p-5">
            <p className="text-emerald-100 font-semibold text-lg">Borrower clarifications ready for CAM</p>
            <p className="text-emerald-50/90 text-sm mt-1">
              Finance officer details and business notes will be merged into qualitative assessment and recommendation narrative.
            </p>
          </div>
        )}

        <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6">
          <p className="text-white text-xl font-semibold mb-3">Upload progress</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {UPLOAD_STAGES.map((stage, idx) => {
              const completed = idx < activeStage;
              const active = idx === activeStage && loading;
              return (
                <div
                  key={stage}
                  className={`rounded-lg px-3 py-2 text-sm border ${
                    completed
                      ? 'bg-emerald-900/40 border-emerald-500/50 text-emerald-200'
                      : active
                        ? 'bg-cyan-900/50 border-cyan-400/70 text-cyan-100 animate-pulse'
                        : 'bg-slate-900/40 border-slate-500/40 text-slate-200/70'
                  }`}
                >
                  {completed ? '✓ ' : active ? '⏳ ' : '○ '} {stage}
                </div>
              );
            })}
          </div>
          <p className="mt-3 text-cyan-100/80 text-xs">
            Public web checks, risk assessment, and CAM draft progress continue on the Pipeline page.
          </p>
        </div>

        {error && <p className="text-red-200 text-sm bg-red-950/40 border border-red-400/40 rounded-lg p-3">{error}</p>}

        <button
          onClick={startAnalysis}
          disabled={loading || files.length === 0}
          className="w-full py-4 rounded-xl bg-cyan-500 hover:bg-cyan-400 disabled:bg-slate-600 text-slate-950 font-bold text-lg shadow-lg shadow-cyan-900/40"
        >
          {loading ? 'Starting your CAM analysis...' : `Start analysis (${files.length} files)`}
        </button>
      </div>
    </main>
  );
}
