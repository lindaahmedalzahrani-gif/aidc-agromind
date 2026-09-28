export type Language = 'en' | 'zh';

/**
 * Normalized shape the UI works with, regardless of what the backend's
 * /api/diagnose response actually looks like. Keep any mapping from the
 * raw API payload inside services/diagnosisService.ts so the rest of the
 * app never has to change if that payload shape changes later.
 */
export interface DiagnosisResult {
  crop: string | null;
  disease: string | null;
  isHealthy: boolean | null;
  modelResponse: string | null;
}

export type DiagnosePanelStatus =
  | 'idle'
  | 'ready'
  | 'analyzing'
  | 'success'
  | 'unknown'
  | 'error'
  | 'invalid';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  text: string;
  isMock?: boolean;
}

export interface DiagnosisContext {
  crop: string | null;
  disease: string | null;
}
