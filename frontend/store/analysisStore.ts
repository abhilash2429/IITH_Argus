'use client';

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AnalysisState {
  companyId: string;
  companyName: string;
  uploadedFileNames: string[];
  pipelineStatus: 'idle' | 'running' | 'hitl' | 'complete' | 'error';
  scoreResult: any | null;
  result: any | null;
  explanation: any | null;
  research: any[];
  setCompany: (id: string, name: string) => void;
  setUploadedFileNames: (names: string[]) => void;
  setPipelineStatus: (status: AnalysisState['pipelineStatus']) => void;
  setScoreResult: (score: any) => void;
  setResult: (result: any) => void;
  setExplanation: (explanation: any) => void;
  setResearch: (research: any[]) => void;
  reset: () => void;
}

const INITIAL: Pick<
  AnalysisState,
  'companyId' | 'companyName' | 'uploadedFileNames' | 'pipelineStatus' | 'scoreResult' | 'result' | 'explanation' | 'research'
> = {
  companyId: '',
  companyName: '',
  uploadedFileNames: [],
  pipelineStatus: 'idle',
  scoreResult: null,
  result: null,
  explanation: null,
  research: [],
};

export const useAnalysisStore = create<AnalysisState>()(
  persist(
    (set) => ({
      ...INITIAL,
      setCompany: (id, name) => set({ companyId: id, companyName: name }),
      setUploadedFileNames: (names) => set({ uploadedFileNames: names }),
      setPipelineStatus: (status) => set({ pipelineStatus: status }),
      setScoreResult: (score) => set({ scoreResult: score }),
      setResult: (result) => set({ result }),
      setExplanation: (explanation) => set({ explanation }),
      setResearch: (research) => set({ research }),
      reset: () => set(INITIAL),
    }),
    {
      name: 'ic-analysis-store',
    }
  )
);
