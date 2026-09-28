// AgroMind diagnosis client.
//
// The browser never talks to the protected AgroMind API directly.
// This Express server keeps the API key private.
//
// Final path:
//
// React UI
//   -> Express /api/diagnose
//   -> AgroMind /api/diagnose
//   -> agromind-diagnosis LoRA

export class ModelNotConfiguredError extends Error {
  constructor() {
    super('AGROMIND_API_URL is not configured.');
    this.name = 'ModelNotConfiguredError';
  }
}

export class ModelRequestError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ModelRequestError';
  }
}

function parseModelText(text) {
  const trimmed = (text || '').trim();

  const parts = trimmed
    .split(/[,，]/)
    .map((part) => part.trim())
    .filter(Boolean);

  if (parts.length >= 2) {
    const crop = parts[0];
    const disease = parts.slice(1).join(', ');

    const normalizedDisease = disease.toLowerCase();

    const healthyMarkers = [
      'healthy',
      'none',
      'no disease',
      '健康',
      '无',
      '无病害',
    ];

    const isHealthy = healthyMarkers.some((marker) =>
      normalizedDisease.includes(marker.toLowerCase())
    );

    return {
      crop,
      disease,
      isHealthy,
      modelResponse: trimmed,
    };
  }

  return {
    crop: null,
    disease: null,
    isHealthy: null,
    modelResponse: trimmed || null,
  };
}

export async function diagnose({
  imageBuffer,
  mimeType,
  language,
}) {
  const baseUrl = process.env.AGROMIND_API_URL;
  const apiKey = process.env.AGROMIND_API_KEY;

  if (!baseUrl) {
    throw new ModelNotConfiguredError();
  }

  if (!apiKey) {
    throw new ModelRequestError(
      'AGROMIND_API_KEY is not configured.'
    );
  }

  const endpoint =
    `${baseUrl.replace(/\/$/, '')}/api/diagnose`;

  const base64Image =
    imageBuffer.toString('base64');

  const dataUrl =
    `data:${mimeType};base64,${base64Image}`;

  let response;

  try {
    response = await fetch(endpoint, {
      method: 'POST',

      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`,
      },

      body: JSON.stringify({
        image: dataUrl,
        lang: language === 'zh' ? 'zh' : 'en',
      }),
    });
  } catch (err) {
    throw new ModelRequestError(
      `Could not reach AgroMind API: ${err.message}`
    );
  }

  if (!response.ok) {
    const body = await response
      .text()
      .catch(() => '');

    throw new ModelRequestError(
      `AgroMind API returned ${response.status}: ${body.slice(0, 300)}`
    );
  }

  let data;

  try {
    data = await response.json();
  } catch (err) {
    throw new ModelRequestError(
      `AgroMind API returned invalid JSON: ${err.message}`
    );
  }

  // The final FastAPI contract is:
  //
  // {
  //   "model": "agromind-diagnosis",
  //   "diagnosis": "葡萄，白粉病",
  //   "usage": {...}
  // }

  const text =
    typeof data?.diagnosis === 'string'
      ? data.diagnosis
      : '';

  return parseModelText(text);
}