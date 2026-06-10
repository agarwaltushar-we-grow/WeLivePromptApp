export const MAX_PROMPT_CHARS = 6000;
export const MAX_CLARIFICATION_ANSWERS_CHARS = 5000;

export function normalizeString(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function normalizeClarificationAnswers(value) {
  if (!Array.isArray(value)) return [];

  return value
    .map((item) => {
      if (typeof item === 'string') {
        return { category: '', question: '', answer: normalizeString(item) };
      }

      return {
        category: normalizeString(item?.category),
        question: normalizeString(item?.question),
        answer: normalizeString(item?.answer)
      };
    })
    .filter((item) => item.answer || item.question || item.category)
    .slice(0, 5);
}

export function validateOptimizeRequest(body) {
  const prompt = normalizeString(body?.prompt);
  const uiLanguage = normalizeString(body?.uiLanguage) === 'ja' ? 'ja' : 'en';
  const clarificationAnswers = normalizeClarificationAnswers(body?.clarificationAnswers);
  const totalAnswerLength = clarificationAnswers.reduce((sum, item) => sum + item.category.length + item.question.length + item.answer.length, 0);

  if (!prompt) {
    return { ok: false, status: 400, error: 'EMPTY_PROMPT' };
  }

  if (prompt.length > MAX_PROMPT_CHARS) {
    return { ok: false, status: 413, error: 'PROMPT_TOO_LONG' };
  }

  if (totalAnswerLength > MAX_CLARIFICATION_ANSWERS_CHARS) {
    return { ok: false, status: 413, error: 'ANSWERS_TOO_LONG' };
  }

  return {
    ok: true,
    data: {
      prompt,
      uiLanguage,
      clarificationAnswers
    }
  };
}

export function userSafeError(code, language = 'en') {
  const messages = {
    en: {
      EMPTY_PROMPT: 'Please paste a rough prompt first.',
      PROMPT_TOO_LONG: 'The prompt is too long. Please shorten it and try again.',
      ANSWERS_TOO_LONG: 'The clarification answers are too long. Please shorten them and try again.',
      SETUP_INCOMPLETE: 'This app has not been fully set up yet. Please ask your WeLive helper to finish the setup.',
      PROVIDER_ERROR: 'The app could not create a final prompt. Please try again or ask your WeLive helper for help.',
      BAD_REQUEST: 'The request could not be read. Please refresh the page and try again.'
    },
    ja: {
      EMPTY_PROMPT: 'まず、整えたいプロンプトを貼り付けてください。',
      PROMPT_TOO_LONG: '入力が長すぎます。短くしてからもう一度お試しください。',
      ANSWERS_TOO_LONG: '確認質問への回答が長すぎます。短くしてからもう一度お試しください。',
      SETUP_INCOMPLETE: 'このアプリはまだ設定が完了していません。WeLiveの担当者に設定を依頼してください。',
      PROVIDER_ERROR: '最終プロンプトを作成できませんでした。もう一度試すか、WeLiveの担当者に確認してください。',
      BAD_REQUEST: 'リクエストを読み取れませんでした。ページを更新してからもう一度お試しください。'
    }
  };

  return messages[language]?.[code] || messages.en[code] || messages.en.PROVIDER_ERROR;
}
