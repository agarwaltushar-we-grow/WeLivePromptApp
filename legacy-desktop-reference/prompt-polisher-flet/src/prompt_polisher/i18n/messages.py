"""Configurable user-facing messages."""
MESSAGES = {
    "en": {"title":"Prompt Polisher","subtitle":"Rewrite unclear Japanese or English prompts into concise, structured prompts.","input":"Original prompt","clarifications":"Clarification answers (optional)","provider":"Provider","api_key":"API key","model":"Model","run":"Analyze and optimize","copy_en":"Copy English prompt","copy_ja":"Copy Japanese prompt","export":"Export","clear":"Clear","detected":"Detected language","analysis":"Analysis report","questions":"Clarification questions","optimized_en":"Optimized English prompt","optimized_ja":"Japanese translation","ready":"Ready."},
    "ja": {"title":"Prompt Polisher","subtitle":"曖昧な日本語・英語プロンプトを、構造化された使いやすいプロンプトに改善します。","input":"元のプロンプト","clarifications":"補足回答（任意）","provider":"プロバイダー","api_key":"APIキー","model":"モデル","run":"分析して最適化","copy_en":"英語プロンプトをコピー","copy_ja":"日本語プロンプトをコピー","export":"エクスポート","clear":"クリア","detected":"検出言語","analysis":"分析レポート","questions":"確認質問","optimized_en":"最適化された英語プロンプト","optimized_ja":"日本語訳","ready":"準備完了。"},
}
def t(locale: str, key: str) -> str:
    return MESSAGES.get(locale, MESSAGES["en"]).get(key, key)
