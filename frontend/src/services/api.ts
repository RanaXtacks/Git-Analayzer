import type { AnalysisResponse } from '../types/guide';

const API_BASE = '/api';

export interface ProgressCallbackData {
  stage: string;
  status: string;
  detail?: string;
}

export async function checkHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) {
    throw new Error('Backend health check failed');
  }
  return res.json();
}

export async function analyzeRepositorySync(url: string): Promise<AnalysisResponse> {
  const res = await fetch(`${API_BASE}/analyze/sync`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || 'Failed to analyze repository');
  }

  return res.json();
}

export async function analyzeRepositoryStream(
  url: string,
  onProgress: (data: ProgressCallbackData) => void,
  onComplete: (response: AnalysisResponse) => void,
  onError: (error: string) => void,
  signal?: AbortSignal
): Promise<void> {
  try {
    const response = await fetch(`${API_BASE}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ url }),
      signal,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: 'Analysis connection failed' }));
      onError(err.detail || `Server returned HTTP ${response.status}`);
      return;
    }

    if (!response.body) {
      onError('Readable stream not supported by browser');
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const parts = buffer.split('\n\n');
      buffer = parts.pop() || '';

      for (const part of parts) {
        if (!part.trim()) continue;

        let eventType = 'message';
        let eventData = '';

        for (const line of part.split('\n')) {
          if (line.startsWith('event:')) {
            eventType = line.replace('event:', '').trim();
          } else if (line.startsWith('data:')) {
            eventData = line.replace('data:', '').trim();
          }
        }

        if (eventType === 'progress' && eventData) {
          try {
            const parsed = JSON.parse(eventData);
            onProgress(parsed);
          } catch {
            // ignore malformed chunk
          }
        } else if (eventType === 'complete' && eventData) {
          try {
            const parsed: AnalysisResponse = JSON.parse(eventData);
            onComplete(parsed);
            return;
          } catch (e) {
            onError(`Failed to parse complete guide response: ${e}`);
            return;
          }
        } else if (eventType === 'error' && eventData) {
          try {
            const errObj = JSON.parse(eventData);
            onError(errObj.error || 'Repository analysis failed');
            return;
          } catch {
            onError(eventData);
            return;
          }
        }
      }
    }
  } catch (err: unknown) {
    if (signal?.aborted) return;
    const msg = err instanceof Error ? err.message : String(err);
    onError(msg);
  }
}
