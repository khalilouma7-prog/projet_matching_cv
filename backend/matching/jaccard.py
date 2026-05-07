import re

def text_to_word_set(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return set(words)

def compute_jaccard_similarity(text1, text2):
    set1 = text_to_word_set(text1)
    set2 = text_to_word_set(text2)

    if not set1 or not set2:
        return 0.0

    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    return intersection / union if union != 0 else 0.0