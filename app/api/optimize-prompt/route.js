import { buildOptimizerMessages, fallbackResult, parseProviderContent } from '../../../lib/promptBuilder.js';
import { userSafeError, validateOptimizeRequest } from '../../../lib/validation.js';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const API_KEY_PLACEHOLDER = 'PASTE_SERVER_SIDE_API_KEY_HERE';

function json(payload, status = 200) {
  return Response.json(payload, {
    status,
    headers: {
      'Cache-Control': 'no-store'
    }
  });
}

function cleanBaseUrl(value) {
  const base = typeof value === 'string' && value.trim() ? value.trim() : 'https://api.openai.com/v1';
  return base.replace(/\/+$/, '');
}

function assertNoClientControlledProviderFields(body) {
  const forbidden = ['apiKey', 'api_key', 'authorization', 'Authorization', 'provider', 'baseUrl', 'base_url', 'model', 'url', 'endpoint'];
  return !forbidden.some((key) => Object.prototype.hasOwnProperty.call(body || {}, key));
}

async function readJson(request) {
  try {
    return await request.json();
  } catch {
    return null;
  }
}

function readServerApiKey() {
  // Developer setup: put the real server-side provider key in Vercel Environment Variables as AI_PROVIDER_API_KEY.
  // For a local-only quick test, this placeholder shows exactly where the key belongs, but it is treated as unset.
  const key = process.env.AI_PROVIDER_API_KEY?.trim() || API_KEY_PLACEHOLDER;
  return key === API_KEY_PLACEHOLDER ? '' : key;
}

export async function GET() {
  return json({ ok: false, error: 'POST only.' }, 405);
}

export async function POST(request) {
  const body = await readJson(request);
  const language = body?.uiLanguage === 'ja' ? 'ja' : 'en';

  if (!body || !assertNoClientControlledProviderFields(body)) {
    return json({ ok: false, error: userSafeError('BAD_REQUEST', language) }, 400);
  }

  const validation = validateOptimizeRequest(body);
  if (!validation.ok) {
    return json({ ok: false, error: userSafeError(validation.error, language) }, validation.status);
  }

  const apiKey = readServerApiKey();
  const model = process.env.AI_PROVIDER_MODEL?.trim() || 'gpt-4o-mini';
  const baseUrl = cleanBaseUrl(process.env.AI_PROVIDER_BASE_URL);

  if (!apiKey) {
    return json({ ok: false, error: userSafeError('SETUP_INCOMPLETE', language) }, 500);
  }

  const fallback = fallbackResult(validation.data);

  try {
    const providerResponse = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model,
        messages: buildOptimizerMessages(validation.data),
        temperature: 0.2,
        response_format: { type: 'json_object' }
      })
    });

    if (!providerResponse.ok) {
      return json({ ok: false, error: userSafeError('PROVIDER_ERROR', language) }, 502);
    }

    const providerJson = await providerResponse.json();
    const content = providerJson?.choices?.[0]?.message?.content;
    const result = parseProviderContent(content, fallback);

    return json({ ok: true, result });
  } catch {
    return json({ ok: false, error: userSafeError('PROVIDER_ERROR', language) }, 502);
  }
}
