import 'dotenv/config';

import express from 'express';
import cors from 'cors';
import multer from 'multer';
import path from 'path';
import { fileURLToPath } from 'url';

import {
  diagnose,
  ModelNotConfiguredError,
  ModelRequestError,
} from './services/modelClient.js';

import { chat } from './services/ragClient.js';


const app = express();

const PORT = process.env.PORT || 8787;

const __filename = fileURLToPath(
  import.meta.url
);

const __dirname = path.dirname(
  __filename
);

const frontendDist = path.resolve(
  __dirname,
  '../frontend/dist'
);


/*
 * ============================================================
 * CORS
 * ============================================================
 */

const allowedOrigins = (
  process.env.ALLOWED_ORIGINS || ''
)
  .split(',')
  .map((origin) => origin.trim())
  .filter(Boolean);


app.use(
  cors(
    allowedOrigins.length
      ? {
          origin: allowedOrigins,
        }
      : undefined
  )
);


app.use(
  express.json()
);


/*
 * ============================================================
 * Image upload
 * ============================================================
 */

const upload = multer({
  storage:
    multer.memoryStorage(),

  limits: {
    fileSize:
      10 * 1024 * 1024,
  },

  fileFilter: (
    _req,
    file,
    cb
  ) => {

    const allowedTypes = [
      'image/jpeg',
      'image/jpg',
      'image/png',
    ];

    const valid =
      allowedTypes.includes(
        file.mimetype
      );

    cb(
      null,
      valid
    );
  },
});


/*
 * ============================================================
 * Health
 *
 * /api/*
 *   Local-development compatibility
 *
 * /ui-api/*
 *   Production browser routes
 * ============================================================
 */

function healthHandler(
  _req,
  res
) {

  return res.json({
    status:
      'ok',

    service:
      'agromind-ui',

    apiConnected:
      Boolean(
        process.env.AGROMIND_API_URL
      ),

    apiKeyConfigured:
      Boolean(
        process.env.AGROMIND_API_KEY
      ),
  });
}


app.get(
  [
    '/api/health',
    '/ui-api/health',
  ],
  healthHandler
);


/*
 * ============================================================
 * Diagnosis
 *
 * Browser
 *   -> /ui-api/diagnose
 *   -> Express
 *   -> AgroMind FastAPI
 *   -> agromind-diagnosis LoRA
 * ============================================================
 */

async function diagnoseHandler(
  req,
  res
) {

  if (!req.file) {

    return res.status(
      400
    ).json({
      error:
        'invalid_image',

      message:
        'No valid JPG or PNG image was provided.',
    });
  }


  const language =
    req.body.language === 'zh'
      ? 'zh'
      : 'en';


  try {

    const result =
      await diagnose({
        imageBuffer:
          req.file.buffer,

        mimeType:
          req.file.mimetype,

        language,
      });


    return res.json({
      crop:
        result.crop,

      disease:
        result.disease,

      is_healthy:
        result.isHealthy,

      model_response:
        result.modelResponse,
    });

  } catch (err) {

    if (
      err instanceof
      ModelNotConfiguredError
    ) {

      return res.status(
        503
      ).json({
        error:
          'model_not_connected',

        message:
          err.message,
      });
    }


    if (
      err instanceof
      ModelRequestError
    ) {

      return res.status(
        502
      ).json({
        error:
          'model_error',

        message:
          err.message,
      });
    }


    console.error(
      'Unexpected diagnosis error:',
      err
    );


    return res.status(
      500
    ).json({
      error:
        'internal_error',

      message:
        'Unexpected server error.',
    });
  }
}


app.post(
  [
    '/api/diagnose',
    '/ui-api/diagnose',
  ],

  upload.single(
    'image'
  ),

  diagnoseHandler
);


/*
 * ============================================================
 * RAG assistant
 *
 * Browser
 *   -> /ui-api/chat
 *   -> Express
 *   -> AgroMind FastAPI
 *   -> RAG
 * ============================================================
 */

async function chatHandler(
  req,
  res
) {

  const {
    message,
    language,
    context,
  } = req.body || {};


  if (
    typeof message !==
      'string'
    ||
    !message.trim()
  ) {

    return res.status(
      400
    ).json({
      error:
        'invalid_message',

      message:
        'message is required.',
    });
  }


  try {

    const result =
      await chat({
        message:
          message.trim(),

        language:
          language === 'zh'
            ? 'zh'
            : 'en',

        context:
          context || null,
      });


    return res.json(
      result
    );

  } catch (err) {

    console.error(
      'Unexpected chat error:',
      err
    );


    return res.status(
      502
    ).json({
      error:
        'rag_error',

      message:
        'Could not reach the AgroMind assistant service.',
    });
  }
}


app.post(
  [
    '/api/chat',
    '/ui-api/chat',
  ],

  chatHandler
);


/*
 * ============================================================
 * Upload errors
 * ============================================================
 */

app.use(
  (
    err,
    _req,
    res,
    next
  ) => {

    if (
      err instanceof
        multer.MulterError
      ||
      (
        err
        &&
        err.message
        &&
        err.message.includes(
          'image'
        )
      )
    ) {

      return res.status(
        400
      ).json({
        error:
          'invalid_image',

        message:
          'Please upload a JPG or PNG image under 10 MB.',
      });
    }


    return next(
      err
    );
  }
);


/*
 * ============================================================
 * React production frontend
 * ============================================================
 */

app.use(
  express.static(
    frontendDist
  )
);


/*
 * React SPA fallback.
 *
 * Routes that are not API endpoints return index.html.
 */

app.get(
  '*',
  (_req, res) => {

    return res.sendFile(
      path.join(
        frontendDist,
        'index.html'
      )
    );
  }
);


/*
 * ============================================================
 * Start
 * ============================================================
 */

app.listen(
  PORT,
  () => {

    console.log(
      `AgroMind UI listening on http://0.0.0.0:${PORT}`
    );

    console.log(
      `  AGROMIND_API_URL: ${
        process.env.AGROMIND_API_URL
        ||
        '(not configured)'
      }`
    );

    console.log(
      `  AGROMIND_API_KEY: ${
        process.env.AGROMIND_API_KEY
          ? '(configured)'
          : '(not configured)'
      }`
    );

    console.log(
      '  Production API prefix: /ui-api'
    );
  }
);