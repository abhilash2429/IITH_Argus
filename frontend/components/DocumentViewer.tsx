'use client';

import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function DocumentViewer({ url }: { url: string }) {
  const [pages, setPages] = useState<number>(1);
  const [page, setPage] = useState(1);

  return (
    <div className="bg-ic-surface border border-ic-border rounded-[10px] p-5">
      <p className="text-[10px] font-medium tracking-[0.12em] uppercase text-ic-muted mb-2.5">Document Viewer</p>
      <div className="overflow-auto rounded-[10px] bg-ic-surface-mid p-3">
        <Document file={url} onLoadSuccess={(d) => setPages(d.numPages)}>
          <Page pageNumber={page} width={620} />
        </Document>
      </div>
      <div className="mt-3 flex gap-3 items-center">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          className="px-3 py-1 rounded-[6px] bg-ic-surface-mid border border-ic-border text-ic-text text-[12px] disabled:opacity-40"
        >
          Prev
        </button>
        <span className="text-ic-muted text-[12px] font-mono">
          {page} / {pages}
        </span>
        <button
          disabled={page >= pages}
          onClick={() => setPage((p) => p + 1)}
          className="px-3 py-1 rounded-[6px] bg-ic-surface-mid border border-ic-border text-ic-text text-[12px] disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}
