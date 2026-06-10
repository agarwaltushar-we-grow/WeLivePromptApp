# Deployment Guide for Vercel

## 1. Import repository

Use the designated WeLive/team Vercel account. Import this GitHub repository into Vercel.

Vercel should detect this as a Next.js project from the root `package.json`.

## 2. Add environment variables

In Vercel Project Settings → Environment Variables, add:

```text
AI_PROVIDER_API_KEY
AI_PROVIDER_BASE_URL
AI_PROVIDER_MODEL
```

Recommended initial values:

```text
AI_PROVIDER_API_KEY=PASTE_REAL_SERVER_SIDE_KEY_HERE
AI_PROVIDER_BASE_URL=https://api.openai.com/v1
AI_PROVIDER_MODEL=gpt-4o-mini
```

The API key belongs only in Vercel Environment Variables or another server-side secret store. Do not put a real key in `app/page.js`, browser code, localStorage, cookies, or any `NEXT_PUBLIC_` variable.

The visible access-code gate has been removed. Anyone who has the deployed URL can use the app while the backend key is configured.

## 3. Verify secure behavior

Open browser DevTools and confirm:

- The browser calls only `/api/optimize-prompt`.
- No API key appears in request payloads.
- No API key appears in response bodies.
- No API key appears in localStorage, sessionStorage, cookies, or client JavaScript.
- No access-code field appears on the page.

## 4. Test prompts

English:

```text
I am a junior software developer working on an AI-powered dashboard that summarizes customer support tickets. Help me create a clear plan for improving accuracy, reducing hallucinations, and making the output easier for non-technical managers to understand.
```

Japanese:

```text
私は、カスタマーサポートのチケットを要約するAI搭載ダッシュボードを開発しているジュニアソフトウェア開発者です。精度を高め、ハルシネーションを減らし、非エンジニアのマネージャーにも理解しやすい出力にするための改善計画を作ってください。
```

Short/vague prompt for clarification flow:

```text
Make my prompt better.
```

Expected behavior:

- Strong prompts return editable English and Japanese final prompts.
- Vague prompts return targeted questions first.
- Editing the original rough prompt after analysis clears the old result and highlights the analyze button.
- Editing the final optimized prompt does not trigger a reset.
