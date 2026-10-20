export interface CitationItem {
  citation: string;
  url?: string;
}

export interface RevisionEntry {
  targetField: 'holding' | 'reasoning';
  originalText: string;
  revisedText: string;
  critique: string;
  timestamp: string;
}

export interface CaseBrief {
  caseName: string;
  holding: string;
  reasoning: string;
  citation: string[];
  citationDetails?: CitationItem[];
  revisionHistory?: RevisionEntry[];
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

