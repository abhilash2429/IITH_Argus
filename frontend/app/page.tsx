'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAnalysisStore } from '@/store/analysisStore';

export default function HomePage() {
  const [companyName, setCompanyName] = useState('');
  const router = useRouter();
  const setCompany = useAnalysisStore((s) => s.setCompany);

  const handleStart = () => {
    if (companyName.trim()) {
      setCompany('', companyName.trim());
      router.push('/upload');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-56px)] bg-ic-page px-4" style={{ paddingTop: '15vh' }}>
      <div className="max-w-[480px] w-full flex flex-col gap-8 -mt-[15vh]">
        {/* Logo mark */}
        <div className="text-center">
          <span className="font-display text-sm tracking-widest text-ic-muted uppercase">InsightCredit</span>
        </div>

        {/* Heading */}
        <h1 className="font-display text-[44px] font-normal text-ic-text text-center leading-tight">
          Assess your borrower.
        </h1>

        {/* Subheading */}
        <p className="text-[15px] text-ic-muted text-center -mt-4">
          AI-powered credit appraisal for Indian corporate lending
        </p>

        {/* Input */}
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleStart()}
          placeholder="Enter company name"
          className="w-full px-4 py-3 bg-ic-surface border border-ic-border rounded-[10px] text-ic-text placeholder:text-ic-muted text-base focus:outline-none focus:ring-2 focus:ring-ic-accent/40 focus:border-transparent"
        />

        {/* CTA Button */}
        <button
          onClick={handleStart}
          disabled={!companyName.trim()}
          className="w-full py-3 px-6 bg-ic-accent text-white font-medium rounded-[10px] text-base transition-opacity hover:opacity-90 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Begin Assessment →
        </button>
      </div>
    </div>
  );
}
