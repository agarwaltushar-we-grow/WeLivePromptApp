# Co-Developer API Setup

The API key is configured only in Vercel, not in the browser and not in GitHub.

## Required variables

Set the following in Vercel Project Settings → Environment Variables:

```text
AI_PROVIDER_API_KEY=the_valid_paid_or_working_key
AI_PROVIDER_BASE_URL=https://api.openai.com/v1
AI_PROVIDER_MODEL=gpt-4o-mini
```

For another OpenAI-compatible provider, replace the base URL and model with that provider's documented values.

## Important rules

- Never commit a real API key to GitHub.
- Never use `NEXT_PUBLIC_` for a secret.
- The frontend must call only `/api/optimize-prompt`.
- The backend route injects the key server-side.
- Users must never input a key.

## Changing the key later

Open Vercel Project Settings → Environment Variables, update `AI_PROVIDER_API_KEY`, save, then redeploy if Vercel requests it.

## Optional access gate

Set `APP_ACCESS_CODE` if this should be private during testing. Users will need the access code, but they still will not see or enter the API key.
