'use client';

import ReactMarkdown from 'react-markdown';

interface CamPreviewProps {
  camText: string;
}

export default function CamPreview({ camText }: CamPreviewProps) {
  return (
    <div className="prose max-w-none prose-headings:font-display prose-headings:text-ic-accent prose-h1:text-[22px] prose-h2:text-[16px] prose-p:text-ic-text prose-p:text-[14px] prose-p:leading-[1.75] prose-li:text-ic-text prose-li:text-[14px] prose-strong:text-ic-text prose-a:text-ic-accent prose-a:no-underline hover:prose-a:underline prose-table:border-ic-border prose-th:bg-ic-surface-mid prose-th:text-ic-text prose-td:border-ic-border prose-td:font-mono prose-td:text-[13px]">
      <ReactMarkdown>{camText}</ReactMarkdown>
    </div>
  );
}
