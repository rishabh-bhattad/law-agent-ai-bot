export interface CaseBrief {
  caseName: string;
  holding: string;
  reasoning: string;
  citation: string[];
}

export interface GenerateBriefRequest {
  query: string;
}

export type AppState = 'idle' | 'loading' | 'success' | 'error';
