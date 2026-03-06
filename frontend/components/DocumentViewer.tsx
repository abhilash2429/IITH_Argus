'use client';

import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function DocumentViewer({ url }: { url: string }) {
  const [pages, setPages] = useState<number>(1);
  const [page, setPage] = useState(1);

  return (
    <div className="bg-slate-800/50 rounded-xl border border-slate-700 p-5">
      <h3 className="text-white font-semibold text-lg mb-3">Document Viewer</h3>
      <div className="overflow-auto rounded bg-slate-900 p-3">
        <Document file={url} onLoadSuccess={(d) => setPages(d.numPages)}>
          <Page pageNumber={page} width={620} />
        </Document>
      </div>
      <div className="mt-3 flex gap-3 items-center">
        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          className="px-3 py-1 rounded bg-slate-700 text-white disabled:opacity-40"
        >
          Prev
        </button>
        <span className="text-slate-300 text-sm">
          Page {page} / {pages}
        </span>
        <button
          disabled={page >= pages}
          onClick={() => setPage((p) => p + 1)}
          className="px-3 py-1 rounded bg-slate-700 text-white disabled:opacity-40"
        >
          Next
        </button>
      </div>
    </div>
  );
}

