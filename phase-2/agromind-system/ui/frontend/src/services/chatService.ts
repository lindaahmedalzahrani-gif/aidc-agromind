import { API_BASE_URL } from './config';
import type { DiagnosisContext, Language } from '../types';

export class ChatServiceError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ChatServiceError';
  }
}

export interface SendChatMessageParams {
  message: string;
  language: Language;
  context: DiagnosisContext | null;
}

export interface ChatReply {
  reply: string;
  isMock: boolean;
}

/**
 * Sends a chat message to our backend's /api/chat. The backend decides
 * whether to forward this to the real RAG API (RAG_API_URL) or return a
 * clearly marked mock reply — the frontend just renders whatever comes
 * back and flags it as a preview when isMock is true.
 */
export async function sendChatMessage({ message, language, context }: SendChatMessageParams): Promise<ChatReply> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message,
        language,
        context: context ?? undefined,
      }),
    });
  } catch {
    throw new ChatServiceError('Could not reach the assistant service.');
  }

  if (!response.ok) {
    throw new ChatServiceError(`Assistant service returned status ${response.status}.`);
  }

  const data = await response.json();
  const reply = typeof data.reply === 'string' ? data.reply : '';
  const isMock = Boolean(data.mock);

  return { reply, isMock };
}
