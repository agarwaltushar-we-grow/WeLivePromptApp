# Prompt Polisher — Vercel AI Ready Web Package

This repository is prepared for Vercel AI or a developer to deploy Prompt Polisher as a browser-based web app.

The previous product was a Python/Flet desktop package. This version adds a Next.js/Vercel web scaffold at the repository root so Vercel can deploy a live URL without requiring users to download a desktop app.

## What normal users should see

Users should only see a simple web page:

1. Paste a rough prompt.
2. Click **Analyze and optimize**.
3. If the prompt is too vague to reliably reach an 80/100 quality score, answer targeted questions across the five prompt-design categories.
4. Receive editable English and Japanese optimized prompts.
5. Copy the final prompt.

Users must never enter or see API keys, provider settings, model names, base URLs, Ollama settings, access codes, or developer/admin settings.

## Vercel environment variables

Set these in Vercel Project Settings → Environment Variables:

```text
AI_PROVIDER_API_KEY=your_server_side_key
AI_PROVIDER_BASE_URL=https://api.openai.com/v1
AI_PROVIDER_MODEL=gpt-4o-mini
```

The repository includes this obvious placeholder:

```text
AI_PROVIDER_API_KEY=PASTE_SERVER_SIDE_API_KEY_HERE
```

Do not deploy with the placeholder. Add the actual key only in Vercel/GitHub secrets or a local `.env.local` file that is not committed. Do not prefix secrets with `NEXT_PUBLIC_`.

## Development

```bash
npm install
npm run dev
```

Open the local URL shown by Next.js.

## Validation

```bash
npm run validate
```

The validation script checks the secure backend route, the no-access-code UI, rough-prompt reset behavior markers, editable/copyable optimized output, request validation, prompt parsing, and English/Japanese test prompts with a mocked provider.

## Legacy desktop source

The previous desktop/Flet source is preserved under:

```text
legacy-desktop-reference/prompt-polisher-flet/
```

It is included only for reference. Vercel should deploy the Next.js app at the repository root.
