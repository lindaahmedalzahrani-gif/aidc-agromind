import { API_BASE_URL } from './config';
import type { DiagnosisResult, Language } from '../types';

export const MAX_IMAGE_BYTES = 10 * 1024 * 1024; // 10 MB
const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png'];

export type DiagnosisErrorKind = 'network' | 'server';

export class DiagnosisServiceError extends Error {
  kind: DiagnosisErrorKind;
  constructor(kind: DiagnosisErrorKind, message: string) {
    super(message);
    this.name = 'DiagnosisServiceError';
    this.kind = kind;
  }
}

/** Client-side check only — the backend re-validates on its own. */
export function isImageFileValid(file: File): boolean {
  return ACCEPTED_TYPES.includes(file.type) && file.size > 0 && file.size <= MAX_IMAGE_BYTES;
}

export interface DiagnoseParams {
  image: File;
  language: Language;
}

/**
 * Sends the image to our backend's /api/diagnose. The backend is the only
 * place that knows about the real model API (MODEL_API_URL); this function
 * only needs to know our own contract, so the model's response schema can
 * change later without touching UI code.
 */
export async function requestDiagnosis({ image, language }: DiagnoseParams): Promise<DiagnosisResult> {
  const form = new FormData();
  form.append('image', image);
  form.append('language', language);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/diagnose`, {
      method: 'POST',
      body: form,
    });
  } catch {
    throw new DiagnosisServiceError('network', 'Could not reach the diagnosis service.');
  }

  if (!response.ok) {
    throw new DiagnosisServiceError('server', `Diagnosis service returned status ${response.status}.`);
  }

  let data: Record<string, unknown>;
  try {
    data = await response.json();
  } catch {
    throw new DiagnosisServiceError('server', 'Diagnosis service returned an unreadable response.');
  }

  // Normalize whatever shape the backend/model sends today. If that shape
  // changes later, only this mapping needs to change.
  const crop = typeof data.crop === 'string' && data.crop.trim() ? data.crop.trim() : null;
  const disease =
    typeof data.disease === 'string' && data.disease.trim()
      ? data.disease.trim()
      : typeof data.disease_or_pest === 'string' && data.disease_or_pest.trim()
        ? (data.disease_or_pest as string).trim()
        : null;
  const isHealthy = typeof data.is_healthy === 'boolean' ? data.is_healthy : null;
  const modelResponse =
    typeof data.model_response === 'string'
      ? data.model_response
      : typeof data.raw_response === 'string'
        ? (data.raw_response as string)
        : null;

  return { crop, disease, isHealthy, modelResponse };
}
