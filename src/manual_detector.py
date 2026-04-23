import re

def manual_ai_feature_detector(extracted_text):
    if not extracted_text:
        return []
    pattern_features = pattern_counter(extracted_text)
    whitespace_features = white_space_formatting(extracted_text)
    ai_feature = [is_ai_statement_included(extracted_text)]
    # concat ALL features into one vector
    return pattern_features + whitespace_features + ai_feature

# Patterns
def pattern_counter(extracted_text):
    text = extracted_text.lower()
    features = []
    #  em dash usage
    em_dash_count = len(re.findall(r"—|--", text))
    features.append(min(em_dash_count / 5.0, 1.0))  # normalize
    # not X, but Y
    not_but_count = len(re.findall(
        r"\bnot\s+[^,.]{1,40},\s*but\s+[^,.]{1,40}", text
    ))
    features.append(min(not_but_count / 3.0, 1.0))
    #  rule-of-three pattern
    rule_three_count = len(re.findall(
        r"\b\w+,\s*\w+,\s*\w+,\s*and\s*\w+", text
    ))
    features.append(min(rule_three_count / 2.0, 1.0))
    return features

# Whitespace
def white_space_formatting(extracted_text):
    features = []
    # excessive line breaks
    newline_spikes = len(re.findall(r"\n{3,}", extracted_text))
    features.append(min(newline_spikes / 3.0, 1.0))
    # bullet density
    bullets = len(re.findall(r"^\s*[-•*]\s+", extracted_text, re.MULTILINE))
    features.append(min(bullets / 10.0, 1.0))
    # paragraph structure uniformity
    paragraphs = re.split(r"\n\s*\n", extracted_text.strip())
    paragraph_score = min(len(paragraphs) / 8.0, 1.0)
    features.append(paragraph_score)
    return features

#AI statement
def is_ai_statement_included(extracted_text):
    if not extracted_text:
        return 0.0
    positive_present = False
    negative_present = False
    text = extracted_text.lower()
    negative_patterns = [
        r"\bno\s+(gen|generative)?\s*ai\s+(was|were)\s+used\b",
        r"\bno\s+(gen|generative)?\s*ai\s+tools?\s+(were|was)\s+used\b",
        r"\bno\s+artificial\s+intelligence\s+(was|were)\s+used\b",
        r"\bdid\s+not\s+use\s+(gen|generative)?\s*ai\b",
        r"\bwithout\s+using\s+(gen|generative)?\s*ai\b",
        r"\bdeclare\s+that\s+no\s+(gen|generative)?\s*ai\s+was\s+used\b"
    ]
    for p in negative_patterns:
        if re.search(p, text):
            negative_present = True
    positive_patterns = [
    r"\bai[- ]assisted\b",
    r"\bai[- ]generated\b",
    r"\busing\s+(gen|generative)?\s*ai\b",
    r"\bused\s+(gen|generative)?\s*ai\b",
    r"\bchatgpt\s+was\s+used\b",
    r"\busing\s+chatgpt\b",
    r"\bgenerated\s+with\s+chatgpt\b",
    r"\busing\s+gpt[- ]?\d\b",
    r"\bcontent\s+generated\s+by\s+ai\b",
    re.compile(
        r"the\s+author(?:\(s\)|s)?\s+declare\s+that\s+"
        r"(generative|gen)\s*ai\s+was\s+used\s+"
        r"in\s+the\s+creation\s+of\s+this\s+manuscript",
        re.IGNORECASE
    )
    ]  
    for p in positive_patterns:
        if re.search(p, text):
            positive_present = True
    if negative_present and positive_present:
        return 0.0
    elif positive_present:
        return 1.0
    else:
        return 0.0