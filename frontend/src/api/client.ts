import type { CaseBrief, GenerateBriefRequest } from '../types';

const API_BASE = '/api/v1';

export async function generateBrief(request: GenerateBriefRequest): Promise<CaseBrief> {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message =
      errorData?.detail ||
      `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch('/health');
    return response.ok;
  } catch {
    return false;
  }
}
