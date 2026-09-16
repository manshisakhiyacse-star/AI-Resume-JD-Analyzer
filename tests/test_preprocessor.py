from app.services.text_preprocessor import TextPreprocessor

def test_clean_text_basic():
    raw_text = "Hello   World! \t This is “smart” quote."
    cleaned = TextPreprocessor.clean_text(raw_text)
    assert cleaned == "Hello World! This is \"smart\" quote."

def test_clean_text_pdf_hyphenation():
    raw_text = "We are looking for a senior dev-\neloper with Python experience."
    cleaned = TextPreprocessor.clean_text(raw_text)
    assert cleaned == "We are looking for a senior developer with Python experience."

def test_normalize_for_matching_variations():
    raw_text = "I have experience with SpringBoot, PostgreSQL, and restful APIs."
    normalized = TextPreprocessor.normalize_for_matching(raw_text)
    assert "spring boot" in normalized
    assert "postgresql" in normalized
    assert "rest api" in normalized

def test_normalize_for_matching_special_chars():
    # C++, C#, .NET, Node.js should be preserved properly in basic normalization
    raw_text = "Skills: C++, C#, .NET, Node.js"
    normalized = TextPreprocessor.normalize_for_matching(raw_text)
    assert "c++" in normalized
    assert "c#" in normalized
    assert ".net" in normalized
    assert "nodejs" in normalized
