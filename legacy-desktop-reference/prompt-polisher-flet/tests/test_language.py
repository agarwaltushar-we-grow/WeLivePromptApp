from prompt_polisher.core.language import detect_language

def test_detect_japanese():
    assert detect_language("会議の議事録を要約して") == "ja"

def test_detect_english():
    assert detect_language("Summarize this meeting transcript.") == "en"

def test_detect_unsupported():
    assert detect_language("12345 !!!") == "unsupported"
