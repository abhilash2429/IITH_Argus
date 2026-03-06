/**
 * Chat Page — ChatInterface with company name header.
 */

'use client';

import { useEffect, useState } from 'react';
import ChatInterface from '@/components/ChatInterface';

const UUID_REGEX =
  /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export default function ChatPage() {
  const [companyId, setCompanyId] = useState('');
  const [companyName, setCompanyName] = useState('Company');
  const [isValidSession, setIsValidSession] = useState(false);

  useEffect(() => {
    const storedCompanyId = localStorage.getItem('companyId') || '';
    setCompanyId(storedCompanyId);
    setCompanyName(localStorage.getItem('companyName') || 'Company');
    setIsValidSession(UUID_REGEX.test(storedCompanyId));
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-2">
          💬 Chat with CAM
        </h1>
        <p className="text-blue-200 mb-6">
          Ask questions about <span className="font-semibold text-white">{companyName}</span>&apos;s credit appraisal
        </p>

        {companyId && isValidSession ? (
          <ChatInterface companyId={companyId} companyName={companyName} />
        ) : (
          <p className="text-red-300 bg-red-950/40 border border-red-400/40 rounded-xl p-4">
            No valid appraisal session found. Please run analysis from Upload first.
          </p>
        )}
      </div>
    </main>
  );
}
