Task: Finalize and Deploy Prompt Polisher to Vercel with Secure Backend API Proxy

Context
This repository has been prepared as a Vercel-ready Prompt Polisher web app. The root of the repository is a Next.js app. The previous Python/Flet desktop version is preserved only for reference under `legacy-desktop-reference/prompt-polisher-flet/`. Do not deploy the legacy desktop app. Deploy the Next.js app at the repository root.

Objective
Deploy Prompt Polisher to Vercel so users can access it through a direct web URL with no download required. Users must never enter, see, or control API keys, model names, base URLs, provider settings, Ollama settings, environment variables, or developer/admin settings. All third-party AI calls must go through the server-side backend endpoint.

Current Intended Architecture
- Frontend: Next.js App Router page at `app/page.js`.
- Backend proxy: Next.js Route Handler at `app/api/optimize-prompt/route.js`.
- Server-only configuration: Vercel Environment Variables.
- Legacy desktop source: reference only, under `legacy-desktop-reference/`.

User-Facing Requirements
The web page must remain simple and bilingual. It should show only:
1. A large rough-prompt input.
2. An optional extra-details input.
3. An optional access-code field only if needed for private MVP use.
4. One main button: “Analyze and optimize”.
5. English and Japanese final prompt outputs.
6. Copy buttons.
7. Simple English/Japanese UI text.

The user-facing UI must not show:
- API key
- provider
- base URL
- model name
- Ollama
- admin settings
- developer settings
- environment variables
- stack traces or raw backend errors

Backend Proxy Requirements
Use the existing server-side endpoint:

POST /api/optimize-prompt

Do not create a generic open proxy.

The frontend may send only:
- prompt
- optionalNotes
- uiLanguage
- accessCode, if APP_ACCESS_CODE is enabled

The frontend must not send:
- API key
- provider URL
- model name
- arbitrary external URL
- third-party Authorization header

The backend endpoint must:
1. Validate the request body.
2. Reject empty prompts.
3. Reject overly long prompts and notes.
4. Reject client attempts to pass apiKey, provider, baseUrl, model, endpoint, url, or Authorization fields.
5. Read the API key only from `process.env.AI_PROVIDER_API_KEY`.
6. Read provider base URL only from `process.env.AI_PROVIDER_BASE_URL` or use the safe default.
7. Read model only from `process.env.AI_PROVIDER_MODEL` or use the safe default.
8. Call the third-party AI provider from the server only.
9. Return only user-safe output.
10. Never return the API key, raw provider headers, stack traces, or secret values.

Environment Variables
Configure these in Vercel Project Settings → Environment Variables:

AI_PROVIDER_API_KEY
AI_PROVIDER_BASE_URL
AI_PROVIDER_MODEL

Recommended initial values:

AI_PROVIDER_BASE_URL=https://api.openai.com/v1
AI_PROVIDER_MODEL=gpt-4o-mini

Optional:

APP_ACCESS_CODE

Important:
- Do not prefix secrets with `NEXT_PUBLIC_`.
- Do not commit `.env` files or real keys to GitHub.
- Do not hard-code any API key in frontend or backend source.

Deployment Requirements
1. Use the designated WeLive/team/intern Vercel account or workspace.
2. Import the existing GitHub repository into Vercel.
3. Confirm Vercel detects the root Next.js app.
4. Configure environment variables.
5. Deploy to a public Vercel URL.
6. Confirm pushes to the main branch trigger automatic deployments.
7. Add or update README/DEPLOYMENT notes only if needed.

Security Verification
Verify all of the following before marking done:
- Browser DevTools Network requests never show the API key.
- Browser JavaScript bundles do not contain the API key.
- The frontend calls only `/api/optimize-prompt` for optimization.
- The backend calls the third-party provider.
- Users cannot override model, base URL, endpoint, provider, or API key.
- No secret uses `NEXT_PUBLIC_`.
- Empty, malformed, and overly long inputs return safe user-facing messages.
- The API route does not expose raw stack traces or provider debug data.

Bilingual Testing
Test the web app with this English prompt:

I am a junior software developer working on an AI-powered dashboard that summarizes customer support tickets. Help me create a clear plan for improving accuracy, reducing hallucinations, and making the output easier for non-technical managers to understand.

Test the web app with this Japanese prompt:

私は、カスタマーサポートのチケットを要約するAI搭載ダッシュボードを開発しているジュニアソフトウェア開発者です。精度を高め、ハルシネーションを減らし、非エンジニアのマネージャーにも理解しやすい出力にするための改善計画を作ってください。

Both tests must return readable English and Japanese optimized prompts without asking the user for an API key.

Definition of Done
[ ] Repo deploys successfully on Vercel from the root Next.js app.
[ ] App is live at a direct Vercel URL.
[ ] Main branch auto-deploy is working or documented.
[ ] Vercel Environment Variables are configured.
[ ] User-facing UI contains no API/provider/admin/Ollama/developer wording.
[ ] Frontend calls only the internal backend endpoint.
[ ] Backend endpoint uses only server-side environment variables for API key/model/base URL.
[ ] API key is not exposed in DevTools, frontend bundles, localStorage, sessionStorage, cookies, or GitHub.
[ ] English and Japanese UI are readable.
[ ] English and Japanese test prompts work.
[ ] `npm run validate` passes.
