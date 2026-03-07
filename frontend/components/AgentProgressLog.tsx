'use client';

import { useEffect, useRef, useState } from 'react';
import { getStatusStreamV1 } from '@/lib/api';

interface LogEntry {
  timestamp: string;
  message: string;
  step?: string;
}

interface AgentProgressLogProps {
  companyId: string;
  onHitlReached: () => void;
  onComplete: () => void;
}

const STEP_LABELS: Record<string, string> = {
  DOCUMENTS_RECEIVED: 'Documents received',
  OCR_EXTRACTION: 'Reading uploaded files',
  GST_PARSING: 'Tax and bank checks',
  RESEARCH_AGENT: 'Public record and news research',
  ML_SCORING: 'Risk scoring and policy checks',
  CAM_GENERATION: 'Preparing credit memo',
  HITL: 'Waiting for human review',
};

export default function AgentProgressLog({
  companyId,
  onHitlReached,
  onComplete,
}: AgentProgressLogProps) {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [isHitl, setIsHitl] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('Initializing');
  const logEndRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);
  const seenMessageKeysRef = useRef<Set<string>>(new Set());

  useEffect(() => {
    setLogs([]);
    setIsComplete(false);
    setIsHitl(false);
    setProgress(0);
    setCurrentStep('Initializing');
    seenMessageKeysRef.current.clear();
  }, [companyId]);

  useEffect(() => {
    const url = getStatusStreamV1(companyId);
    if (eventSourceRef.current) eventSourceRef.current.close();
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'log') {
          const rawTimestamp = String(data.timestamp || '');
          const rawMessage = String(data.message || data.data || '');
          const rawStep = String(data.step || '');
          const normalizedMessage = rawMessage.trim().toLowerCase().replace(/\s+/g, ' ');
          const dedupeKey = `${rawStep}|${normalizedMessage}`;
          if (seenMessageKeysRef.current.has(dedupeKey)) return;
          seenMessageKeysRef.current.add(dedupeKey);

          setLogs((prev) => [...prev, {
            timestamp: new Date(rawTimestamp || Date.now()).toLocaleTimeString(),
            message: rawMessage,
            step: data.step,
          }]);
        }

        if (data.type === 'status') {
          setProgress(Number(data.progress_pct || 0));
          const rawStep = String(data.step || 'Processing');
          setCurrentStep(STEP_LABELS[rawStep] || rawStep.replaceAll('_', ' ').toLowerCase());
        }

        if (data.type === 'hitl_pause' || data.message?.includes('HITL') || data.step === 'HITL') {
          setIsHitl(true);
          onHitlReached();
        }

        if (data.type === 'complete' || data.type === 'done') {
          setIsComplete(true);
          onComplete();
          eventSource.close();
        }
      } catch {
        const normalizedMessage = String(event.data || '').trim().toLowerCase().replace(/\s+/g, ' ');
        if (seenMessageKeysRef.current.has(`plain|${normalizedMessage}`)) return;
        seenMessageKeysRef.current.add(`plain|${normalizedMessage}`);
        setLogs((prev) => [
          ...prev,
          { timestamp: new Date().toLocaleTimeString(), message: event.data },
        ]);
      }
    };

    eventSource.onerror = () => { eventSource.close(); };

    return () => {
      eventSource.close();
      if (eventSourceRef.current === eventSource) eventSourceRef.current = null;
    };
  }, [companyId, onHitlReached, onComplete]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getLogColor = (message: string) => {
    if (message.includes('ERROR')) return 'text-ic-negative';
    if (message.includes('✅') || message.includes('Complete')) return 'text-ic-positive';
    if (message.includes('HITL')) return 'text-ic-warning';
    return 'text-ic-text';
  };

  return (
    <div>
      {/* HITL Banner */}
      {isHitl && !isComplete && (
        <div className="mb-4 p-4 bg-[#fdf0e8] border border-[#f3d5bc] rounded-[10px]">
          <p className="text-ic-warning font-medium text-[14px]">
            Human-in-the-Loop — Awaiting Qualitative Input
          </p>
          <p className="text-ic-muted text-[12px] mt-1">
            Enter your site visit notes and management assessment to continue.
          </p>
        </div>
      )}

      {/* Completion Banner */}
      {isComplete && (
        <div className="mb-4 p-4 bg-ic-accent-light border border-[#b8d9bf] rounded-[10px]">
          <p className="text-ic-positive font-medium text-[14px]">
            Pipeline Complete — Credit Appraisal Ready
          </p>
        </div>
      )}

      {/* Progress bar */}
      <div className="mb-3">
        <div className="flex justify-between text-[11px] text-ic-muted mb-1">
          <span>{currentStep}</span>
          <span className="font-mono">{progress.toFixed(0)}%</span>
        </div>
        <div className="h-1.5 bg-ic-surface-mid rounded-full overflow-hidden">
          <div
            className="h-full bg-ic-accent transition-all duration-500 rounded-full"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Log Lines */}
      <div className="bg-ic-surface-mid rounded-[10px] border border-ic-border p-4 max-h-96 overflow-y-auto font-mono text-[12px]">
        {logs.length === 0 && (
          <p className="text-ic-muted animate-pulse">Connecting to pipeline...</p>
        )}
        {logs.map((log, i) => (
          <div key={i} className="flex gap-3 py-0.5">
            <span className="text-ic-muted shrink-0">{log.timestamp}</span>
            <span className={getLogColor(log.message)}>
              {log.step ? `[${STEP_LABELS[String(log.step)] || String(log.step)}] ` : ''}
              {log.message}
            </span>
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
    </div>
  );
}
