/**
 * UploadZone — react-dropzone multi-format upload component.
 * Shows document type badge per file after classification.
 */

'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

interface UploadedFile {
  file: File;
  type?: string;
}

interface UploadZoneProps {
  onFilesReady: (files: File[]) => void;
}

export default function UploadZone({ onFilesReady }: UploadZoneProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      const newFiles = acceptedFiles.map((file) => ({
        file,
        type: guessDocType(file.name),
      }));
      const all = [...uploadedFiles, ...newFiles];
      setUploadedFiles(all);
      onFilesReady(all.map((f) => f.file));
    },
    [uploadedFiles, onFilesReady]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/csv': ['.csv'],
      'application/json': ['.json'],
      'application/xml': ['.xml'],
      'text/xml': ['.xml'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
    },
    multiple: true,
  });

  const removeFile = (index: number) => {
    const updated = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(updated);
    onFilesReady(updated.map((f) => f.file));
  };

  return (
    <div>
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${isDragActive
            ? 'border-blue-400 bg-blue-900/20'
            : 'border-slate-600 hover:border-blue-500 bg-slate-800/30'
          }`}
      >
        <input {...getInputProps()} />
        <div className="text-4xl mb-3">📄</div>
        <p className="text-slate-300 text-lg">
          {isDragActive
            ? 'Drop files here...'
            : 'Drag & drop PDF/DOCX/CSV/XML/Excel/JPEG files, or click to browse'}
        </p>
        <p className="text-slate-500 text-sm mt-2">
          Annual reports, scanned pages (JPEG), bank statements, GST filings, audit reports, ITR, GSTR-3B
        </p>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="mt-4 space-y-2">
          {uploadedFiles.map((uf, i) => (
            <div
              key={i}
              className="flex items-center justify-between bg-slate-800/60 rounded-lg px-4 py-3 border border-slate-700"
            >
              <div className="flex items-center gap-3">
                <span className="text-blue-400">📎</span>
                <span className="text-white text-sm truncate max-w-xs">
                  {uf.file.name}
                </span>
                {uf.type && (
                  <span className="px-2 py-0.5 text-xs rounded-full bg-blue-900/50 text-blue-300 border border-blue-700/50">
                    {uf.type}
                  </span>
                )}
              </div>
              <button
                onClick={() => removeFile(i)}
                className="text-slate-400 hover:text-red-400 text-sm"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function guessDocType(filename: string): string {
  const lower = filename.toLowerCase();
  if (lower.endsWith('.jpg') || lower.endsWith('.jpeg') || lower.endsWith('.png')) return 'Scanned Image';
  if (lower.endsWith('.docx')) return 'Word Financial Document';
  if (lower.endsWith('.csv') || lower.endsWith('.xlsx') || lower.endsWith('.xls')) return 'Bank Statement';
  if (lower.endsWith('.xml')) return 'GST XML';
  if (lower.endsWith('.json') && lower.includes('itr')) return 'ITR JSON';
  if (lower.includes('gst') || lower.includes('gstr')) return 'GSTR-3B';
  if (lower.includes('bank') || lower.includes('statement')) return 'Bank Statement';
  if (lower.includes('annual') || lower.includes('report')) return 'Annual Report';
  if (lower.includes('audit')) return 'Audit Report';
  if (lower.includes('itr') || lower.includes('tax')) return 'ITR';
  if (lower.includes('balancesheet') || lower.includes('balance')) return 'Balance Sheet';
  return 'Document';
}
