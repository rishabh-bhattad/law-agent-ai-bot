export interface CitationItem {
  citation: string;
  url?: string;
}

export interface CaseBrief {
  caseName: string;
  holding: string;
  reasoning: string;
  citation: string[];
  citationDetails?: CitationItem[];
}

export interface GenerateBriefRequest {
  query: string;
}

export interface RepairBriefRequest {
  currentBrief: CaseBrief;
  targetField: 'holding' | 'reasoning';
  instruction: string;
}

export type AppState = 'idle' | 'loading' | 'success' | 'error';

