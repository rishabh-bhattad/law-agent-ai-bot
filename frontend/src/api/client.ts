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

export async function generateBriefStream(
  request: GenerateBriefRequest,
  onStep: (stepName: string) => void,
  onComplete: (brief: CaseBrief) => void,
  onError: (error: string) => void
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/generate/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `Request failed with status ${response.status}`);
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('Streaming not supported by browser.');
    }

    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data: ')) {
          try {
            const payload = JSON.parse(trimmed.slice(6));
            if (payload.event === 'step_start' && payload.step) {
              onStep(payload.step);
            } else if (payload.event === 'complete' && payload.result) {
              onComplete(payload.result);
            }
          } catch {
            // Ignore partial JSON parse chunks
          }
        }
      }
    }
  } catch (err) {
    onError(err instanceof Error ? err.message : 'An unexpected error occurred');
  }
}

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await fetch('/health');
    return response.ok;
  } catch {
    return false;
  }
}
