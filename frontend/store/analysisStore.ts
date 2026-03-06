'use client';

import { create } from 'zustand';

interface AnalysisState {
  companyId: string;
  companyName: string;
  result: any | null;
  explanation: any | null;
  research: any[];
  setCompany: (id: string, name: string) => void;
  setResult: (result: any) => void;
  setExplanation: (explanation: any) => void;
  setResearch: (research: any[]) => void;
}

export const useAnalysisStore = create<AnalysisState>((set) => ({
  companyId: '',
  companyName: '',
  result: null,
  explanation: null,
  research: [],
  setCompany: (id, name) => set({ companyId: id, companyName: name }),
  setResult: (result) => set({ result }),
  setExplanation: (explanation) => set({ explanation }),
  setResearch: (research) => set({ research }),
}));

