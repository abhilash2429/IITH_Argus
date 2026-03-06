/**
 * CAM Report Page
 * Shows CAM narrative preview + v1 report download + Chat CTA.
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getReportPdfUrlV1, getReportUrlV1, getResultsV1 } from '@/lib/api';
import CamPreview from '@/components/CamPreview';

export default function CamPage() {
  const [camText, setCamText] = useState('');
  const [docxReady, setDocxReady] = useState(false);
  const [pdfReady, setPdfReady] = useState(false);
  const [loading, setLoading] = useState(true);
  const [companyId, setCompanyId] = useState('');
  const router = useRouter();

  useEffect(() => {
    setCompanyId(localStorage.getItem('companyId') || '');
  }, []);

  useEffect(() => {
    if (!companyId) return;
    getResultsV1(companyId)
      .then((res) => {
        setCamText(String(res.data?.explanation?.decision_narrative || ''));
        setDocxReady(Boolean(res.data?.cam_docx_path));
        setPdfReady(Boolean(res.data?.cam_pdf_path));
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [companyId]);

  if (loading) {
    return (
      <main className="min-h-screen bg-black flex items-center justify-center">
        <p className="text-[#D7F7C8] text-lg animate-pulse">Loading CAM report...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-black p-8">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-[#E9FFD9]">Credit Appraisal Memorandum</h1>
          <div className="flex gap-3">
            {docxReady ? (
              <>
                <a
                  href={getReportUrlV1(companyId)}
                  className="px-4 py-2 bg-[#4CBB17] hover:bg-[#66D42F] text-black rounded-lg text-sm font-medium transition-all"
                >
                  📥 Download CAM (.docx)
                </a>
                {pdfReady && (
                  <a
                    href={getReportPdfUrlV1(companyId)}
                    className="px-4 py-2 bg-[#48872B] hover:bg-[#4F9A31] text-[#E9FFD9] rounded-lg text-sm font-medium transition-all"
                  >
                    📥 Download CAM (.pdf)
                  </a>
                )}
              </>
            ) : (
              <span className="px-4 py-2 bg-[#293325] text-[#D7F7C8] rounded-lg text-sm border border-[#39542C]">
                CAM generation in progress...
              </span>
            )}
          </div>
        </div>

        {camText ? (
          <CamPreview camText={camText} />
        ) : (
          <p className="text-[#C8EAB8]">CAM text will appear once analysis is completed.</p>
        )}

        <div className="mt-8 text-center">
          <button
            onClick={() => router.push('/chat')}
            className="px-6 py-3 bg-[#4CBB17] hover:bg-[#66D42F] text-black font-semibold rounded-xl transition-all shadow-lg text-lg"
          >
            💬 Chat with CAM Report
          </button>
        </div>
      </div>
    </main>
  );
}
