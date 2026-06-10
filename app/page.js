'use client';

import { useMemo, useState } from 'react';

const examples = [
  {
    title: { en: 'Marketing email', ja: 'マーケティングメール' },
    category: { en: 'Copy', ja: '文章作成' },
    emoji: '✉️',
    text: {
      en: 'Write a launch email for a new AI feature. Make it clear, friendly, benefit-led, and suitable for busy business users.',
      ja: '新しいAI機能のローンチメールを書いてください。忙しいビジネスユーザー向けに、わかりやすく、親しみやすく、メリットが伝わる内容にしてください。'
    }
  },
  {
    title: { en: 'Code review', ja: 'コードレビュー' },
    category: { en: 'Dev', ja: '開発' },
    emoji: '💻',
    text: {
      en: 'Review my Python function and suggest improvements for readability, edge cases, performance, and maintainability.',
      ja: 'このPython関数をレビューし、読みやすさ、エッジケース、性能、保守性の観点で改善案を出してください。'
    }
  },
  {
    title: { en: 'Blog outline', ja: 'ブログ構成' },
    category: { en: 'Content', ja: 'コンテンツ' },
    emoji: '📝',
    text: {
      en: 'Create a blog outline about remote work productivity for team managers. Include headline options, sections, key arguments, and examples.',
      ja: 'チームマネージャー向けに、リモートワークの生産性に関するブログ構成を作ってください。見出し案、章立て、主張、具体例を含めてください。'
    }
  },
  {
    title: { en: 'Business proposal', ja: '事業提案' },
    category: { en: 'Strategy', ja: '戦略' },
    emoji: '📊',
    text: {
      en: 'Create a persuasive business proposal for a new AI service targeting mid-sized companies. Include problem, solution, benefits, pricing logic, implementation plan, and CTA.',
      ja: '中堅企業向けの新しいAIサービスについて、説得力のある事業提案を作ってください。課題、解決策、メリット、価格設計、導入計画、CTAを含めてください。'
    }
  }
];

const flowStepsByLanguage = {
  en: [
    ['01', 'Rough prompt', 'Draft input', 'Drop your raw idea, however messy.'],
    ['02', 'Gap analysis', 'Missing details', 'We spot missing audience, format, intent, and quality criteria.'],
    ['03', 'Clarify', 'Focused questions', 'A few focused questions appear only when the prompt needs them.'],
    ['04', 'Polished!', 'Ready to use', 'A structured, AI-ready prompt comes back editable and copy-ready.']
  ],
  ja: [
    ['01', 'ラフな入力', 'まずは下書き', 'まとまっていないアイデアでも、そのまま入力できます。'],
    ['02', '不足情報の分析', 'ギャップ確認', '対象者、形式、目的、品質基準など足りない要素を確認します。'],
    ['03', '確認質問', '必要な時だけ', 'プロンプトに不足がある場合だけ、短い質問を表示します。'],
    ['04', '完成！', 'すぐ使える形に', '編集・コピーできるAI向けの構造化プロンプトを返します。']
  ]
};

const qualityMetricsByLanguage = {
  en: [
    ['SF', 'Style Fidelity', 'Keeps your vibe', '≥ 80', '%'],
    ['DMR', 'Detail Match', 'Catches the context', '≥ 70–80', '%'],
    ['BC', 'Boundary Compliance', 'Stays on task', '≥ 98', '%']
  ],
  ja: [
    ['SF', 'スタイル再現性', '雰囲気を保つ', '≥ 80', '%'],
    ['DMR', '詳細一致率', '文脈を拾う', '≥ 70–80', '%'],
    ['BC', '条件遵守率', '依頼から外れない', '≥ 98', '%']
  ]
};

const qualityCardsByLanguage = {
  en: [
    ['01', 'Objective clarity', 'Does the AI know exactly what success looks like?'],
    ['02', 'Context fit', 'Does the AI understand the audience, situation, and background?'],
    ['03', 'Requirements', 'Are constraints, must-haves, and boundaries clear?'],
    ['04', 'Output format', 'Is the final answer structure specified?'],
    ['05', 'Quality bar', 'Does the prompt define what good means?']
  ],
  ja: [
    ['01', '目的の明確さ', 'AIが「成功状態」を正しく理解できるか。'],
    ['02', '文脈の適合', '対象者、状況、背景が十分に伝わっているか。'],
    ['03', '条件・要件', '必須条件、制約、避けるべきことが明確か。'],
    ['04', '出力形式', '最終回答の構成や形式が指定されているか。'],
    ['05', '品質基準', '何をもって「良い」とするかが定義されているか。']
  ]
};



const clarificationCategoryLabelsJa = {
  Objective: '目的',
  'Context & Audience': '文脈・対象者',
  Requirements: '要件',
  'Output Format': '出力形式',
  'Quality Bar': '品質基準',
  Context: '文脈',
  Audience: '対象者',
  Constraints: '制約',
  Format: '形式',
  Quality: '品質'
};

function localizeClarificationCategory(category, language) {
  if (language !== 'ja') return category;
  return clarificationCategoryLabelsJa[category] || category;
}

const labels = {
  en: {
    switchTo: '日本語',
    brand: 'WeLive Prompt Studio',
    navService: 'service',
    navServiceJp: 'サービス',
    navAbout: 'about us',
    navAboutJp: '会社情報',
    navMore: 'more',
    navMoreJp: 'その他',
    footerService: 'service',
    footerAbout: 'about us',
    footerMore: 'more',
    footerInquiry: 'inquiry',
    headerCta: "Let’s go!",
    heroBadge: 'WeLive Prompt Studio',
    heroBadgeJp: 'AI Prompt Polisher',
    titleLead: 'Turn messy ideas into',
    titleEmphasis: 'prompts that pop.',
    subtitle: 'Toss in a half-baked thought. We’ll spot what is missing, ask a couple of friendly questions, and hand you back a crisp, AI-ready prompt.',
    primaryHeroCta: 'Start polishing',
    noSetup: 'No code. No setup. Just fun.',
    chips: ['No access code needed', 'Editable output', 'Copy-ready', 'English & Japanese'],
    previewRoughLabel: 'Rough prompt',
    previewRoughText: 'write a tweet about our launch 🚀',
    previewPolishedLabel: 'Polished prompt',
    previewPolishedText: 'Act as a launch copywriter. Create 3 concise posts with audience, tone, CTA, and success criteria...',
    target: 'target',
    targetBadge: '80+ target',
    workspaceTitle: 'Prompt workspace',
    workspaceJp: 'Workspace',
    workspaceHelp: 'Type your rough idea below, then hit optimize. We’ve got you.',
    promptLabel: 'Paste your rough prompt here',
    promptPlaceholder: 'e.g. write a tweet about our launch 🚀',
    optimize: 'Analyze and optimize',
    optimizeDisplay: 'Optimize!',
    reoptimize: 'Prompt changed — analyze again',
    workingRead: 'Reading…',
    working: 'Optimizing...',
    reset: 'Reset',
    clear: 'Clear',
    charCount: 'characters',
    changedWarning: 'Your draft changed. Optimize again to refresh the result.',
    questionsTitle: 'A couple quick questions',
    questionsJp: 'Clarification',
    questionsIntro: 'Answer what you can — blanks are okay. This sharpens the result.',
    answerPlaceholder: 'Your answer...',
    submitAnswers: 'Make my prompt',
    editRough: 'Edit rough prompt instead',
    score: 'Strict prompt score',
    rationale: 'Why',
    loadingAnalyze: 'Reading your idea and checking for gaps…',
    loadingOptimize: 'Crafting your shiny new prompt…',
    resultTitle: 'Your polished prompt',
    resultJp: 'Output',
    editable: 'editable',
    english: 'EN',
    japanese: '日本語',
    notes: 'What improved',
    copyEnglish: 'Copy English prompt',
    copyJapanese: 'Copy Japanese prompt',
    copy: 'Copy',
    copied: 'Copied!',
    freeEditHint: 'Free-edit the result, then copy it into your AI tool.',
    emptyResult: 'Your improved prompt will appear here after optimization.',
    examplesTitle: 'Try an example',
    examplesJp: 'Samples',
    examplesSubtitle: 'Tap a rough prompt and watch it glow up.',
    useExample: 'Polish this',
    logicBadge: 'How the studio works',
    logicBadgeJp: 'Logic',
    logicTitle: 'Smart logic behind every glow-up.',
    footerSubtitle: 'Turning rough ideas into prompts that pop.'
  },
  ja: {
    switchTo: 'English',
    brand: 'WeLive Prompt Studio',
    navService: 'サービス',
    navServiceJp: 'service',
    navAbout: '会社情報',
    navAboutJp: 'about us',
    navMore: 'その他',
    navMoreJp: 'more',
    footerService: 'サービス',
    footerAbout: '会社情報',
    footerMore: 'その他',
    footerInquiry: 'お問い合わせ',
    headerCta: '始める',
    heroBadge: 'WeLive Prompt Studio',
    heroBadgeJp: 'AIプロンプト最適化',
    titleLead: 'ラフなアイデアを',
    titleEmphasis: '輝くプロンプトに。',
    subtitle: '途中の考えでも大丈夫です。不足している情報だけ確認し、AIに伝わりやすいプロンプトに整えます。',
    primaryHeroCta: '磨き始める',
    noSetup: 'コード不要。すぐ使えます。',
    chips: ['すぐ使える', '出力を編集可能', 'コピー対応', '英語・日本語対応'],
    previewRoughLabel: 'ラフなプロンプト',
    previewRoughText: '新サービスのローンチについて投稿文を書きたい 🚀',
    previewPolishedLabel: '整えたプロンプト',
    previewPolishedText: 'あなたはローンチ専門のコピーライターです。対象者、トーン、CTA、成功基準を含む短い投稿文を3案作成してください...',
    target: '目標',
    targetBadge: '80点以上目標',
    workspaceTitle: '作業スペース',
    workspaceJp: 'Prompt workspace',
    workspaceHelp: 'ラフなアイデアを入力して、最適化ボタンを押してください。',
    promptLabel: '整えたいプロンプトをここに貼り付けてください',
    promptPlaceholder: '例：新サービスのローンチについて投稿文を書きたい 🚀',
    optimize: '分析して最適化する',
    optimizeDisplay: '最適化する',
    reoptimize: '入力が変更されました — 再分析してください',
    workingRead: '確認中…',
    working: '最適化中...',
    reset: 'リセット',
    clear: 'クリア',
    charCount: '文字',
    changedWarning: '入力内容が変更されました。結果を更新するには、もう一度最適化してください。',
    questionsTitle: '少しだけ確認します',
    questionsJp: 'Clarification',
    questionsIntro: '答えられる範囲で大丈夫です。回答があるほど、結果がシャープになります。',
    answerPlaceholder: '回答を入力...',
    submitAnswers: 'プロンプトを作る',
    editRough: '元の入力を編集する',
    score: '厳格なプロンプト評価',
    rationale: '理由',
    loadingAnalyze: '入力内容と不足情報を確認しています…',
    loadingOptimize: 'プロンプトを仕上げています…',
    resultTitle: '完成プロンプト',
    resultJp: '出力',
    editable: '編集可能',
    english: '英語',
    japanese: '日本語',
    notes: '改善された点',
    copyEnglish: '英語プロンプトをコピー',
    copyJapanese: '日本語プロンプトをコピー',
    copy: 'コピー',
    copied: 'コピーしました！',
    freeEditHint: '結果は自由に編集できます。整えたらAIツールにコピーしてください。',
    emptyResult: '最適化後のプロンプトがここに表示されます。',
    examplesTitle: 'サンプルを試す',
    examplesJp: 'Examples',
    examplesSubtitle: 'サンプルを選ぶと、すぐに試せます。',
    useExample: 'この例を使う',
    logicBadge: 'スタジオの仕組み',
    logicBadgeJp: 'Logic',
    logicTitle: '良いプロンプトに仕上げるためのロジック。',
    footerSubtitle: 'ラフなアイデアを、輝くプロンプトに。'
  }
};

async function copyTextToClipboard(text) {
  if (!text) return false;

  if (navigator?.clipboard?.writeText) {
    await navigator.clipboard.writeText(text);
    return true;
  }

  return false;
}

function createBlankAnswers(questions = []) {
  return questions.map((question) => ({
    category: question.category || '',
    question: question.question || '',
    answer: ''
  }));
}

export default function Home() {
  const [language, setLanguage] = useState('en');
  const [prompt, setPrompt] = useState('');
  const [lastAnalyzedPrompt, setLastAnalyzedPrompt] = useState('');
  const [hasAnalyzed, setHasAnalyzed] = useState(false);
  const [result, setResult] = useState(null);
  const [clarification, setClarification] = useState(null);
  const [clarificationAnswers, setClarificationAnswers] = useState([]);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);
  const [roughPromptChanged, setRoughPromptChanged] = useState(false);
  const [activeOutputLanguage, setActiveOutputLanguage] = useState('english');

  const t = labels[language];
  const currentExamples = examples.map((example) => ({
    title: example.title[language],
    category: example.category[language],
    emoji: example.emoji,
    text: example.text[language]
  }));
  const currentFlowSteps = flowStepsByLanguage[language];
  const currentQualityMetrics = qualityMetricsByLanguage[language];
  const currentQualityCards = qualityCardsByLanguage[language];
  const canSubmit = useMemo(() => prompt.trim().length > 0 && !loading, [prompt, loading]);
  const shouldUseAnswers = clarification?.questions?.length > 0 && !roughPromptChanged;
  const activeOutputText = activeOutputLanguage === 'english' ? result?.optimizedEnglish : result?.optimizedJapanese;

  function handlePromptChange(value) {
    setPrompt(value);
    setError('');
    setStatus('');

    if (hasAnalyzed && value !== lastAnalyzedPrompt) {
      setRoughPromptChanged(true);
      setResult(null);
      setClarification(null);
      setClarificationAnswers([]);
    } else if (hasAnalyzed && value === lastAnalyzedPrompt) {
      setRoughPromptChanged(false);
    }
  }

  function updateClarificationAnswer(index, answer) {
    setClarificationAnswers((current) => current.map((item, itemIndex) => (
      itemIndex === index ? { ...item, answer } : item
    )));
  }

  function updateOptimizedPrompt(field, value) {
    setResult((current) => current ? { ...current, [field]: value } : current);
  }

  function scrollToWorkspace() {
    document.getElementById('prompt-workspace')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function selectExample(exampleText) {
    clearAll();
    setPrompt(exampleText);
    window.setTimeout(scrollToWorkspace, 40);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError('');
    setStatus('');
    setLoading(true);

    const answers = shouldUseAnswers ? clarificationAnswers : [];

    try {
      const response = await fetch('/api/optimize-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt, clarificationAnswers: answers, uiLanguage: language })
      });
      const data = await response.json();
      if (!response.ok || !data.ok) {
        setError(data?.error || (language === 'ja' ? '処理できませんでした。' : 'Something went wrong.'));
        setResult(null);
        setClarification(null);
        return;
      }

      setHasAnalyzed(true);
      setLastAnalyzedPrompt(prompt);
      setRoughPromptChanged(false);

      if (data.result?.needsClarification) {
        const questions = data.result.clarifyingQuestions || [];
        setClarification({
          questions,
          strictScore: data.result.strictScore,
          scoreRationale: data.result.scoreRationale
        });
        setClarificationAnswers(createBlankAnswers(questions));
        setResult(null);
        window.setTimeout(() => document.getElementById('clarification-panel')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
        return;
      }

      setResult(data.result);
      setActiveOutputLanguage('english');
      setClarification(null);
      setClarificationAnswers([]);
      window.setTimeout(() => document.getElementById('optimized-output')?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 80);
    } catch {
      setError(language === 'ja' ? '接続できませんでした。もう一度お試しください。' : 'Could not connect. Please try again.');
      setResult(null);
      setClarification(null);
    } finally {
      setLoading(false);
    }
  }

  async function copyPrompt(text) {
    const copied = await copyTextToClipboard(text);
    if (copied) {
      setStatus(t.copied);
      window.setTimeout(() => setStatus(''), 1600);
    }
  }

  function clearAll() {
    setPrompt('');
    setLastAnalyzedPrompt('');
    setHasAnalyzed(false);
    setResult(null);
    setClarification(null);
    setClarificationAnswers([]);
    setError('');
    setStatus('');
    setRoughPromptChanged(false);
    setActiveOutputLanguage('english');
  }

  return (
    <main className="app-root wave-bg" id="top">
      <header className="site-header">
        <a className="brand-mark" href="#top" aria-label="WeLive Prompt Studio">
          <img className="welive-logo" src="/welive-logo.svg" alt="WeLive" />
          <span className="brand-text">
            <strong>Prompt Studio</strong>
            <em>by WeLive</em>
          </span>
        </a>

        <nav className="header-nav" aria-label="Primary navigation">
          <a href="#examples"><span>{t.navService}</span><small>{t.navServiceJp}</small></a>
          <a href="#quality-rules"><span>{t.navAbout}</span><small>{t.navAboutJp}</small></a>
          <a href="#footer"><span>{t.navMore}</span><small>{t.navMoreJp}</small></a>
        </nav>

        <div className="header-actions">
          <button className="language-button" onClick={() => setLanguage(language === 'en' ? 'ja' : 'en')} type="button">
            {t.switchTo}
          </button>
          <button className="btn-aqua header-cta" onClick={scrollToWorkspace} type="button">
            ✨ {t.headerCta}
          </button>
        </div>
      </header>

      <section className="hero-section">
        <div className="hero-copy">
          <p className="hero-badge"><span className="sparkle-dot">✦</span>{t.heroBadge}<span>・{t.heroBadgeJp}</span></p>
          <h1>{t.titleLead} <span>{t.titleEmphasis}</span></h1>
          <p className="hero-subtitle">{t.subtitle}</p>
          <div className="hero-actions">
            <button className="btn-aqua hero-button" onClick={scrollToWorkspace} type="button">🪄 {t.primaryHeroCta}</button>
            <p className="no-setup"><span>★</span>{t.noSetup}</p>
          </div>
          <div className="trust-chips">
            {t.chips.map((chip) => <span key={chip}>✓ {chip}</span>)}
          </div>
        </div>

        <aside className="hero-preview-card" aria-label="Prompt transformation preview">
          <div className="floating-blob blob-one" />
          <div className="preview-mini-card rough-card">
            <span>{t.previewRoughLabel}</span>
            <p>{t.previewRoughText}</p>
          </div>
          <div className="preview-arrow">↓</div>
          <div className="preview-mini-card polished-card">
            <span>{t.previewPolishedLabel}</span>
            <p>{t.previewPolishedText}</p>
          </div>
          <div className="hero-sticker">80+<small>{t.target}</small></div>
        </aside>
      </section>

      <section ref={null} className="workspace-section" id="prompt-workspace">
        <form onSubmit={handleSubmit} className="workspace-card">
          <div className="workspace-heading">
            <div>
              <h2>{t.workspaceTitle} <span>{t.workspaceJp}</span></h2>
              <p>{t.workspaceHelp}</p>
            </div>
            <span className="quality-pill">{t.targetBadge}</span>
          </div>

          <label className="prompt-label" htmlFor="rough-prompt">
            <span>{t.promptLabel}</span>
          </label>
          <textarea
            id="rough-prompt"
            value={prompt}
            onChange={(event) => handlePromptChange(event.target.value)}
            placeholder={t.promptPlaceholder}
            rows={6}
            className="rough-textarea"
          />

          {roughPromptChanged && <p className="notice-box">{t.changedWarning}</p>}
          {error && <p className="error-box">{error}</p>}
          {status && <p className="success-box stamp">{status}</p>}

          <div className="workspace-actions">
            <span className="character-count">{prompt.trim().length} {t.charCount}</span>
            <div className="button-row">
              {(prompt || hasAnalyzed) && (
                <button className="ghost-button" type="button" onClick={clearAll}>↻ {t.reset}</button>
              )}
              <button className={`btn-aqua ${roughPromptChanged ? 'attention-button' : ''}`} disabled={!canSubmit} type="submit">
                ✨ {loading ? t.workingRead : roughPromptChanged ? t.reoptimize : shouldUseAnswers ? t.submitAnswers : t.optimizeDisplay}
              </button>
            </div>
          </div>

          {loading && (
            <aside className="loading-card" aria-live="polite">
              <div className="loading-dots"><span /> <span /> <span /></div>
              <p>{shouldUseAnswers ? t.loadingOptimize : t.loadingAnalyze}</p>
            </aside>
          )}

          {clarification && (
            <section className="clarification-panel pop-in" id="clarification-panel">
              <div className="mini-heading">
                <span className="mini-icon">✨</span>
                <h3>{t.questionsTitle}</h3>
                <em>{t.questionsJp}</em>
              </div>
              <p>{t.questionsIntro}</p>
              <div className="score-strip">
                <strong>{t.score}: {clarification.strictScore ?? '-'}/100</strong>
                {clarification.scoreRationale && <span>{clarification.scoreRationale}</span>}
              </div>
              <div className="question-stack">
                {clarification.questions.map((item, index) => (
                  <label className="question-card" key={`${item.category}-${item.question}`}>
                    <span className="question-category">{localizeClarificationCategory(item.category, language)}</span>
                    <strong>{item.question}</strong>
                    <input
                      value={clarificationAnswers[index]?.answer || ''}
                      onChange={(event) => updateClarificationAnswer(index, event.target.value)}
                      placeholder={t.answerPlaceholder}
                    />
                  </label>
                ))}
              </div>
              <div className="clarification-actions">
                <button className="ghost-button" type="button" onClick={scrollToWorkspace}>{t.editRough}</button>
                <button className="btn-aqua" disabled={!canSubmit} type="submit">{t.submitAnswers} →</button>
              </div>
            </section>
          )}

          {result && (
            <section className="output-panel pop-in" id="optimized-output">
              <div className="output-header">
                <div className="mini-heading">
                  <span className="mini-icon success">✓</span>
                  <h3>{activeOutputLanguage === 'english' ? t.resultTitle : t.resultJp}</h3>
                  <em>✎ {t.editable}</em>
                </div>
                <span className="quality-pill green">{t.score}: {result.strictScore ?? '-'}/100</span>
              </div>

              {result.scoreRationale && <p className="result-rationale"><strong>{t.rationale}:</strong> {result.scoreRationale}</p>}

              <div className="tab-row" role="tablist" aria-label="Optimized prompt language">
                <button className={activeOutputLanguage === 'english' ? 'active' : ''} onClick={() => setActiveOutputLanguage('english')} type="button">{t.english}</button>
                <button className={activeOutputLanguage === 'japanese' ? 'active' : ''} onClick={() => setActiveOutputLanguage('japanese')} type="button">{t.japanese}</button>
              </div>

              <textarea
                className="optimized-textarea"
                value={activeOutputText || ''}
                onChange={(event) => updateOptimizedPrompt(activeOutputLanguage === 'english' ? 'optimizedEnglish' : 'optimizedJapanese', event.target.value)}
                rows={Math.min(16, Math.max(7, (activeOutputText || '').split('\n').length + 1))}
              />

              <div className="workspace-actions output-actions">
                <p>{t.freeEditHint}</p>
                <button className="btn-sun" type="button" onClick={() => copyPrompt(activeOutputText)}>
                  {status ? `✓ ${t.copied}` : activeOutputLanguage === 'english' ? t.copyEnglish : t.copyJapanese}
                </button>
              </div>

              {result.improvementNotes?.length > 0 && (
                <div className="improvement-card">
                  <h4>{t.notes}</h4>
                  <ul>{result.improvementNotes.map((item) => <li key={item}>{item}</li>)}</ul>
                </div>
              )}
            </section>
          )}
        </form>
      </section>

      {!result && !clarification && !loading && !error && (
        <section className="empty-state-card" aria-live="polite">
          <p>{t.emptyResult}</p>
        </section>
      )}

      <section className="examples-section" id="examples">
        <h2>{t.examplesTitle} <span>{t.examplesJp}</span></h2>
        <p>{t.examplesSubtitle}</p>
        <div className="example-grid">
          {currentExamples.map((example) => (
            <button className="example-card" key={example.title} type="button" onClick={() => selectExample(example.text)}>
              <div className="example-top"><span className="example-emoji">{example.emoji}</span><em>{example.category}</em></div>
              <strong>{example.title}</strong>
              <p>“{example.text}”</p>
              <span className="example-cta">{t.useExample} →</span>
            </button>
          ))}
        </div>
      </section>

      <section className="quality-section" id="quality-rules">
        <div className="quality-inner">
          <p className="dark-badge">✨ {t.logicBadge}<span>{t.logicBadgeJp}</span></p>
          <h2>{t.logicTitle}</h2>

          <div className="flow-grid">
            {currentFlowSteps.map(([number, title, jp, text], index) => (
              <article className="flow-card" key={title}>
                <span>{number}</span>
                <h3>{title}</h3>
                <em>{jp}</em>
                <p>{text}</p>
                {index < currentFlowSteps.length - 1 && <b aria-hidden="true">→</b>}
              </article>
            ))}
          </div>

          <div className="metric-grid">
            {currentQualityMetrics.map(([code, label, title, metric, unit], index) => (
              <article className={`metric-card ${index === 2 ? 'sun' : ''}`} key={code}>
                <span>{label} ({code})</span>
                <h3>{title}</h3>
                <strong>{metric}<small>{unit}</small></strong>
              </article>
            ))}
          </div>

          <div className="quality-grid">
            {currentQualityCards.map(([number, title, text]) => (
              <article className="quality-card" key={title}>
                <span>{number}</span>
                <h3>{title}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <footer className="site-footer" id="footer">
        <div>
          <span className="footer-brand"><img src="/welive-logo.svg" alt="WeLive" /><strong>Prompt Studio</strong></span>
          <p>{t.footerSubtitle}</p>
        </div>
        <nav>
          <a href="https://www.welive-inc.co.jp/">{t.footerService}</a>
          <a href="#quality-rules">{t.footerAbout}</a>
          <a href="#top">{t.footerMore}</a>
          <a href="#prompt-workspace">{t.footerInquiry}</a>
        </nav>
      </footer>
    </main>
  );
}
