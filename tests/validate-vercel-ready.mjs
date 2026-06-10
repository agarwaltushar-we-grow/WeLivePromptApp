import assert from 'node:assert/strict';
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { POST, GET } from '../app/api/optimize-prompt/route.js';
import { buildOptimizerMessages, fallbackResult, parseProviderContent } from '../lib/promptBuilder.js';
import { validateOptimizeRequest } from '../lib/validation.js';

const root = new URL('..', import.meta.url).pathname;
const results = [];

async function test(name, fn) {
  try {
    await fn();
    results.push({ name, ok: true });
  } catch (error) {
    results.push({ name, ok: false, error: error?.stack || String(error) });
  }
}

function walk(dir) {
  return readdirSync(dir).flatMap((entry) => {
    const full = join(dir, entry);
    if (entry === 'node_modules' || entry === '.next' || entry === 'legacy-desktop-reference') return [];
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

function read(rel) {
  return readFileSync(join(root, rel), 'utf8');
}

async function callRoute(body) {
  const request = new Request('http://localhost/api/optimize-prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const response = await POST(request);
  return { status: response.status, json: await response.json() };
}

await test('Root Next.js files exist', () => {
  for (const file of ['package.json', 'next.config.mjs', 'app/page.js', 'app/layout.js', 'app/api/optimize-prompt/route.js', '.env.example', 'vercel.json']) {
    assert.ok(statSync(join(root, file)).isFile(), `${file} missing`);
  }
});

await test('No public secret prefix appears in env example', () => {
  assert.equal(read('.env.example').includes('NEXT_PUBLIC_AI_PROVIDER_API_KEY'), false);
});

await test('User UI is bilingual and readable', () => {
  const page = read('app/page.js');
  for (const text of ['Paste your rough prompt here', '整えたいプロンプトをここに貼り付けてください', 'Analyze and optimize', '分析して最適化する', 'Copy English prompt', '日本語プロンプトをコピー']) {
    assert.ok(page.includes(text), `Missing UI text: ${text}`);
  }
});

await test('User UI has no visible access-code or extra-details field', () => {
  const page = read('app/page.js');
  for (const removed of ['accessCode', 'Access code', 'アクセスコード', 'Optional: add extra details', 'optionalNotes', 'notesPlaceholder']) {
    assert.equal(page.includes(removed), false, `Removed UI field still present: ${removed}`);
  }
});

await test('User UI includes clarification, reset, editable output, and copy behavior markers', () => {
  const page = read('app/page.js');
  for (const expected of ['clarificationAnswers', 'roughPromptChanged', 'Prompt changed — analyze again', 'optimized-textarea', 'navigator.clipboard.writeText']) {
    assert.ok(page.includes(expected), `Missing expected behavior marker: ${expected}`);
  }
});

await test('User UI does not expose forbidden developer words in rendered label strings', () => {
  const page = read('app/page.js');
  const forbidden = ['API key', 'OpenAI', 'Ollama', 'provider', 'base URL', 'Admin Settings', 'Developer Settings', 'environment variable'];
  for (const term of forbidden) {
    assert.equal(page.includes(term), false, `Forbidden term found in user page: ${term}`);
  }
});

await test('Backend rejects client-controlled provider fields', async () => {
  process.env.AI_PROVIDER_API_KEY = 'test-key';
  global.fetch = async () => new Response('{}', { status: 500 });
  const response = await callRoute({ prompt: 'hello', apiKey: 'evil', model: 'expensive-model' });
  assert.equal(response.status, 400);
});

await test('Backend rejects empty prompt', async () => {
  const response = await callRoute({ prompt: '   ' });
  assert.equal(response.status, 400);
});

await test('Backend rejects overly long prompt', async () => {
  const response = await callRoute({ prompt: 'x'.repeat(6001) });
  assert.equal(response.status, 413);
});

await test('Backend rejects overly long clarification answers', async () => {
  const response = await callRoute({
    prompt: 'Build a prompt for improving an AI dashboard.',
    clarificationAnswers: [{ category: 'Objective', question: 'What result?', answer: 'x'.repeat(6000) }]
  });
  assert.equal(response.status, 413);
});

await test('GET returns 405', async () => {
  const response = await GET();
  assert.equal(response.status, 405);
});

await test('Missing API key or placeholder key returns safe setup message only', async () => {
  delete process.env.AI_PROVIDER_API_KEY;
  let response = await callRoute({ prompt: 'Build a prompt for an AI dashboard.', uiLanguage: 'en' });
  assert.equal(response.status, 500);
  assert.match(response.json.error, /WeLive helper/);
  assert.equal(JSON.stringify(response.json).includes('AI_PROVIDER_API_KEY'), false);

  process.env.AI_PROVIDER_API_KEY = 'PASTE_SERVER_SIDE_API_KEY_HERE';
  response = await callRoute({ prompt: 'Build a prompt for an AI dashboard.', uiLanguage: 'en' });
  assert.equal(response.status, 500);
  assert.equal(JSON.stringify(response.json).includes('PASTE_SERVER_SIDE_API_KEY_HERE'), false);
});

await test('English prompt succeeds with mocked optimized provider', async () => {
  process.env.AI_PROVIDER_API_KEY = 'test-key';
  process.env.AI_PROVIDER_BASE_URL = 'https://api.openai.com/v1';
  process.env.AI_PROVIDER_MODEL = 'gpt-4o-mini';
  let outgoing;
  global.fetch = async (url, options) => {
    outgoing = { url, options };
    return Response.json({
      choices: [{
        message: {
          content: JSON.stringify({
            status: 'optimized',
            strictScore: 88,
            scoreRationale: 'The task, context, constraints, output format, and quality criteria are sufficiently clear.',
            optimizedEnglish: 'Act as a senior AI product engineer. Improve an AI support-ticket dashboard by reducing hallucinations, increasing accuracy, and making manager-facing summaries clear.',
            optimizedJapanese: 'シニアAIプロダクトエンジニアとして、サポートチケット用AIダッシュボードの精度を高め、ハルシネーションを減らし、管理者向け要約をわかりやすくしてください。',
            clarifyingQuestions: [],
            improvementNotes: ['Clarified role, goal, and output audience.']
          })
        }
      }]
    });
  };
  const response = await callRoute({
    prompt: 'I am a junior software developer working on an AI-powered dashboard that summarizes customer support tickets. Help me create a clear plan for improving accuracy, reducing hallucinations, and making the output easier for non-technical managers to understand.',
    uiLanguage: 'en'
  });
  assert.equal(response.status, 200);
  assert.equal(response.json.ok, true);
  assert.equal(response.json.result.needsClarification, false);
  assert.equal(response.json.result.strictScore, 88);
  assert.match(response.json.result.optimizedEnglish, /AI support-ticket dashboard/);
  assert.match(response.json.result.optimizedJapanese, /サポートチケット/);
  assert.equal(outgoing.options.headers.Authorization, 'Bearer test-key');
  assert.equal(JSON.stringify(response.json).includes('test-key'), false);
  assert.ok(JSON.stringify(outgoing.options.body).includes('response_format'));
});

await test('Vague prompt returns clarification questions with mocked provider', async () => {
  process.env.AI_PROVIDER_API_KEY = 'test-key';
  global.fetch = async () => Response.json({
    choices: [{
      message: {
        content: JSON.stringify({
          status: 'needs_clarification',
          strictScore: 52,
          scoreRationale: 'The prompt lacks objective, audience, constraints, output format, and success criteria.',
          optimizedEnglish: '',
          optimizedJapanese: '',
          clarifyingQuestions: [
            { category: 'Objective', question: 'What exact output do you want?' },
            { category: 'Output format', question: 'What format should the final answer use?' }
          ],
          improvementNotes: []
        })
      }
    }]
  });
  const response = await callRoute({ prompt: 'Make it better.', uiLanguage: 'en' });
  assert.equal(response.status, 200);
  assert.equal(response.json.ok, true);
  assert.equal(response.json.result.needsClarification, true);
  assert.equal(response.json.result.optimizedEnglish, '');
  assert.equal(response.json.result.clarifyingQuestions.length, 2);
  assert.equal(response.json.result.clarifyingQuestions[0].category, 'Objective');
});

await test('Clarification answers are sent to provider and can produce final result', async () => {
  process.env.AI_PROVIDER_API_KEY = 'test-key';
  let outgoingBody;
  global.fetch = async (_url, options) => {
    outgoingBody = JSON.parse(options.body);
    return Response.json({
      choices: [{
        message: {
          content: JSON.stringify({
            status: 'optimized',
            strictScore: 86,
            scoreRationale: 'The added answers clarify the missing requirements.',
            optimizedEnglish: 'Create a concise landing-page prompt for a Japanese B2B AI service targeting HR managers, with a headline, section outline, proof points, and CTA.',
            optimizedJapanese: '日本の人事責任者向けB2B AIサービスのLP作成プロンプトを、見出し、構成、根拠、CTAを含めて作成してください。',
            clarifyingQuestions: [],
            improvementNotes: ['Used the clarification answers to define audience and output format.']
          })
        }
      }]
    });
  };
  const response = await callRoute({
    prompt: 'Make an LP prompt.',
    uiLanguage: 'en',
    clarificationAnswers: [
      { category: 'Context and audience', question: 'Who is the audience?', answer: 'Japanese HR managers at mid-sized companies.' },
      { category: 'Output format', question: 'What should it include?', answer: 'Headline, section outline, proof points, and CTA.' }
    ]
  });
  assert.equal(response.status, 200);
  assert.equal(response.json.result.needsClarification, false);
  assert.match(response.json.result.optimizedEnglish, /landing-page prompt/);
  assert.ok(outgoingBody.messages.some((message) => message.content.includes('Japanese HR managers')));
});

await test('Japanese prompt succeeds with mocked provider', async () => {
  process.env.AI_PROVIDER_API_KEY = 'test-key';
  global.fetch = async () => Response.json({
    choices: [{
      message: {
        content: JSON.stringify({
          status: 'optimized',
          strictScore: 87,
          scoreRationale: '依頼内容は十分に具体的です。',
          optimizedEnglish: 'Create a practical improvement plan for an AI support-ticket dashboard, focusing on accuracy, hallucination reduction, and manager-friendly output.',
          optimizedJapanese: 'AI搭載サポートチケット要約ダッシュボードについて、精度向上、ハルシネーション削減、非エンジニア向けのわかりやすさを重視した改善計画を作成してください。',
          clarifyingQuestions: [],
          improvementNotes: ['目的と評価観点を明確化しました。']
        })
      }
    }]
  });
  const response = await callRoute({
    prompt: '私は、カスタマーサポートのチケットを要約するAI搭載ダッシュボードを開発しているジュニアソフトウェア開発者です。精度を高め、ハルシネーションを減らし、非エンジニアのマネージャーにも理解しやすい出力にするための改善計画を作ってください。',
    uiLanguage: 'ja'
  });
  assert.equal(response.status, 200);
  assert.equal(response.json.ok, true);
  assert.match(response.json.result.optimizedEnglish, /AI support-ticket dashboard/);
  assert.match(response.json.result.optimizedJapanese, /ハルシネーション/);
});

await test('Prompt parser handles fenced optimized JSON, clarification JSON, and malformed provider output', () => {
  const fallback = fallbackResult({ prompt: 'Improve a code review prompt.', uiLanguage: 'en' });
  const parsed = parseProviderContent('```json\n{"status":"optimized","strictScore":82,"scoreRationale":"Good enough.","optimizedEnglish":"Better EN","optimizedJapanese":"より良い日本語","clarifyingQuestions":[],"improvementNotes":[]}\n```', fallback);
  assert.equal(parsed.needsClarification, false);
  assert.equal(parsed.optimizedEnglish, 'Better EN');
  assert.equal(parsed.optimizedJapanese, 'より良い日本語');

  const clarification = parseProviderContent('{"status":"needs_clarification","strictScore":45,"scoreRationale":"Too vague.","optimizedEnglish":"","optimizedJapanese":"","clarifyingQuestions":[{"category":"Objective","question":"What result do you want?"}],"improvementNotes":[]}', fallback);
  assert.equal(clarification.needsClarification, true);
  assert.equal(clarification.clarifyingQuestions[0].category, 'Objective');

  const malformed = parseProviderContent('not json', fallback);
  assert.ok(typeof malformed.needsClarification === 'boolean');
});

await test('Request validator handles broad best/worst-case inputs', () => {
  const samples = [
    'Create a code review checklist for a junior developer.',
    'Help me explain vector databases to a non-technical manager.',
    'クラウド移行プロジェクトのリスクを整理してください。',
    'Generate a prompt for debugging a failing API route.',
    'Write a prompt for comparing LLM evaluation methods.',
    '   ',
    'x'.repeat(7000)
  ];
  const statuses = samples.map((prompt) => validateOptimizeRequest({ prompt }));
  assert.equal(statuses.filter((item) => item.ok).length, 5);
  assert.equal(statuses.filter((item) => !item.ok).length, 2);
});

await test('Prompt builder explicitly uses five prompt-design categories', () => {
  const messages = buildOptimizerMessages({ prompt: 'Make this better.', uiLanguage: 'en' });
  const joined = messages.map((message) => message.content).join('\n');
  for (const category of ['Objective', 'Context and audience', 'Constraints and requirements', 'Output format', 'Quality criteria']) {
    assert.ok(joined.includes(category), `Missing category: ${category}`);
  }
});

await test('No obvious committed secret values in source files', () => {
  const files = walk(root);
  const suspicious = [];
  for (const file of files) {
    const content = readFileSync(file, 'utf8');
    if (/sk-[A-Za-z0-9_-]{16,}/.test(content)) suspicious.push(file);
  }
  assert.deepEqual(suspicious, []);
});

const failed = results.filter((item) => !item.ok);
for (const item of results) {
  console.log(`${item.ok ? 'PASS' : 'FAIL'} ${item.name}`);
  if (!item.ok) console.log(item.error);
}

console.log(`\n${results.length - failed.length} PASS, ${failed.length} FAIL`);
if (failed.length) process.exit(1);
