def classify_topic(problem_text: str) -> str | None:
    """Classify a math problem into a topic via keyword matching.

    Args:
        problem_text (str): The text of the math problem to classify.

    Returns:
        str | None: The topic key (e.g., "algebra") if classified with at least
                    2 matching keywords, or None if uncertain.

    Note:
        Blindspot: Simple keyword matching is highly brittle. Words like 'variable'
        might appear in geometry or combinatorics problems, leading to misclassification.
    """
    text_lower = problem_text.lower()
    scores = {}
    for topic, keywords in _TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[topic] = score

    if not scores:
        return None

