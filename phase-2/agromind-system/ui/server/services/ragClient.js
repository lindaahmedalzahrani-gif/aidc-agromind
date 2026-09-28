// AgroMind RAG client.
//
// Final flow:
//
// React UI
//   -> Express /api/chat
//   -> AgroMind FastAPI /api/chat
//   -> AgroMind RAG
//   -> ChromaDB
//   -> base Qwen for grounded answer generation
//
// The browser never receives or knows the AgroMind API key.


/*
 * ------------------------------------------------------------
 * Detect one of the four structured RAG question types.
 *
 * These correspond to the RAG API's supported values:
 *
 *   cause
 *   symptoms
 *   management
 *   crop_info
 *
 * If the message does not clearly match one of these intents,
 * null is returned and the original user question is sent as a
 * free-text grounded question instead.
 * ------------------------------------------------------------
 */

function detectQuestionType(message, language) {
  const text =
    String(message || '')
      .trim()
      .toLowerCase();


  if (!text) {
    return null;
  }


  if (language === 'zh') {
    if (
      text.includes('病因') ||
      text.includes('原因') ||
      text.includes('为什么')
    ) {
      return 'cause';
    }


    if (
      text.includes('症状') ||
      text.includes('表现') ||
      text.includes('迹象')
    ) {
      return 'symptoms';
    }


    if (
      text.includes('防治') ||
      text.includes('管理') ||
      text.includes('治疗') ||
      text.includes('预防') ||
      text.includes('怎么办') ||
      text.includes('怎么处理')
    ) {
      return 'management';
    }


    if (
      text.includes('作物') ||
      text.includes('介绍') ||
      text.includes('更多信息')
    ) {
      return 'crop_info';
    }


    return null;
  }


  /*
   * English
   */

  if (
    text.includes('cause') ||
    text.includes('reason') ||
    text.includes('why does') ||
    text.includes('why is')
  ) {
    return 'cause';
  }


  if (
    text.includes('symptom') ||
    text.includes('sign')
  ) {
    return 'symptoms';
  }


  if (
    text.includes('manage') ||
    text.includes('management') ||
    text.includes('treat') ||
    text.includes('treatment') ||
    text.includes('control') ||
    text.includes('prevent') ||
    text.includes('prevention') ||
    text.includes('what should i do')
  ) {
    return 'management';
  }


  if (
    text.includes('tell me more about this crop') ||
    text.includes('crop information') ||
    text.includes('about this crop')
  ) {
    return 'crop_info';
  }


  return null;
}


/*
 * ------------------------------------------------------------
 * Validate diagnosis context.
 *
 * RAG follow-up questions should be tied to an existing
 * AgroMind diagnosis rather than being used as a general
 * unrestricted chatbot.
 * ------------------------------------------------------------
 */

function getDiagnosisContext(context) {
  const crop =
    context &&
    typeof context.crop === 'string'
      ? context.crop.trim()
      : '';


  const disease =
    context &&
    typeof context.disease === 'string'
      ? context.disease.trim()
      : '';


  if (!crop || !disease) {
    throw new Error(
      'A crop diagnosis is required before asking AgroMind follow-up questions.'
    );
  }


  return {
    crop,
    disease,
  };
}


/*
 * ------------------------------------------------------------
 * Call the final AgroMind API.
 * ------------------------------------------------------------
 */

async function chatWithRag({
  message,
  language,
  context,
}) {
  const baseUrl =
    process.env.AGROMIND_API_URL;

  const apiKey =
    process.env.AGROMIND_API_KEY;


  if (!baseUrl) {
    throw new Error(
      'AGROMIND_API_URL is not configured.'
    );
  }


  if (!apiKey) {
    throw new Error(
      'AGROMIND_API_KEY is not configured.'
    );
  }


  const diagnosis =
    getDiagnosisContext(context);


  const questionType =
    detectQuestionType(
      message,
      language
    );


  const endpoint =
    `${baseUrl.replace(/\/$/, '')}/api/chat`;


  /*
   * Structured quick-button request:
   *
   * {
   *   crop: "Pepper",
   *   disease: "Anthracnose",
   *   question_type: "management",
   *   lang: "en"
   * }
   */

  let payload;


  if (questionType) {
    payload = {
      crop:
        diagnosis.crop,

      disease:
        diagnosis.disease,

      question_type:
        questionType,

      lang:
        language === 'zh'
          ? 'zh'
          : 'en',
    };
  } else {

    /*
     * Free-text follow-up.
     *
     * Keep the crop/disease context with the request so the
     * RAG system knows which diagnosis the user is discussing.
     */

    payload = {
      crop:
        diagnosis.crop,

      disease:
        diagnosis.disease,

      question:
        message.trim(),

      lang:
        language === 'zh'
          ? 'zh'
          : 'en',
    };
  }


  let response;


  try {
    response = await fetch(
      endpoint,
      {
        method: 'POST',

        headers: {
          'Content-Type':
            'application/json',

          Authorization:
            `Bearer ${apiKey}`,
        },

        body:
          JSON.stringify(payload),
      }
    );
  } catch (err) {
    throw new Error(
      `Could not reach the AgroMind RAG API: ${
        err.message
      }`
    );
  }


  if (!response.ok) {
    const body =
      await response
        .text()
        .catch(() => '');


    throw new Error(
      `AgroMind RAG API returned ${
        response.status
      }: ${
        body.slice(0, 300)
      }`
    );
  }


  let data;


  try {
    data =
      await response.json();
  } catch (err) {
    throw new Error(
      `AgroMind RAG API returned invalid JSON: ${
        err.message
      }`
    );
  }


  const reply =
    typeof data.answer === 'string'
      ? data.answer.trim()
      : '';


  if (!reply) {
    throw new Error(
      'AgroMind RAG API returned an empty answer.'
    );
  }


  return {
    reply,

    // The final system is using the real RAG.
    mock: false,

    // Preserve useful metadata even though the current React
    // UI does not need to display it yet.
    supported:
      typeof data.supported === 'boolean'
        ? data.supported
        : null,

    sourcesCount:
      typeof data.sources_count === 'number'
        ? data.sources_count
        : null,

    question:
      typeof data.question === 'string'
        ? data.question
        : null,
  };
}


/*
 * ------------------------------------------------------------
 * Public service function used by server/index.js
 * ------------------------------------------------------------
 */

export async function chat({
  message,
  language,
  context,
}) {
  const cleanMessage =
    typeof message === 'string'
      ? message.trim()
      : '';


  if (!cleanMessage) {
    throw new Error(
      'A question is required.'
    );
  }


  return chatWithRag({
    message:
      cleanMessage,

    language:
      language === 'zh'
        ? 'zh'
        : 'en',

    context:
      context || null,
  });
}