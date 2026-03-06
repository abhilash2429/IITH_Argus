/**
 * CamPreview — react-markdown renderer with Tailwind prose styling.
 */

'use client';

import ReactMarkdown from 'react-markdown';

interface CamPreviewProps {
  camText: string;
}

export default function CamPreview({ camText }: CamPreviewProps) {
  return (
    <div className="bg-black rounded-xl border border-[#39542C] p-8 text-[#D7F7C8] prose max-w-none prose-h1:text-2xl prose-h2:text-xl prose-p:text-[#C8EAB8] prose-li:text-[#C8EAB8] prose-headings:text-[#E9FFD9] prose-strong:text-[#F1FFE8] prose-a:text-[#A6F46C]">
      <ReactMarkdown>{camText}</ReactMarkdown>
    </div>
  );
}
