import os
import json
import re
from collections import defaultdict, Counter

# Hardcoded English stopwords (concise but effective set)
STOPWORDS = set(
    [
        "a","an","the","and","or","but","if","then","than","too","very","so","such","not","no",
        "of","at","by","for","with","about","against","between","into","through","during","before","after",
        "to","from","in","on","over","under","again","further","once","here","there","when","where","why","how",
        "is","are","was","were","be","been","being","do","does","did","doing","have","has","had","having",
        "i","you","he","she","it","we","they","me","him","her","us","them","my","your","his","hers","its","our","their",
        "this","that","these","those","as","can","could","should","would","will","just","only","own","same","both","each","other",
        "which","who","whom","until","while","also","per","per","up","down","out","off","again","few","more","most","some","such"
    ]
)


def porter_stem(word: str) -> str:
    """A simple, compact Porter Stemmer implementation sufficient for recipe terms.
    Note: This is a minimal adaptation of the algorithm based on public descriptions.
    It is not a full-featured stemmer but works well for common English words.
    """
    vowels = "aeiou"

    def is_vowel(ch, i):
        if ch in vowels:
            return True
        if ch == 'y' and i > 0 and word[i-1] not in vowels:
            return True
        return False

    def measure(stem):
        m = 0
        prev_vowel = False
        for i, ch in enumerate(stem):
            v = ch in vowels
            if not prev_vowel and v:
                prev_vowel = True
            elif prev_vowel and not v:
                m += 1
                prev_vowel = False
        return m

    w = word
    if len(w) <= 2:
        return w

    # Step 1a
    if w.endswith("sses"):
        w = w[:-2]
    elif w.endswith("ies"):
        w = w[:-2]
    elif w.endswith("ss"):
        pass
    elif w.endswith("s"):
        w = w[:-1]

    # Step 1b
    flag = False
    for suf in ("eed",):
        if w.endswith(suf):
            stem = w[:-len(suf)]
            if measure(stem) > 0:
                w = w[:-1]
            flag = True
            break
    if not flag:
        for suf in ("ed", "ing"):
            if w.endswith(suf):
                stem = w[:-len(suf)]
                if any(is_vowel(ch, i) for i, ch in enumerate(stem)):
                    w = stem
                    if w.endswith("at") or w.endswith("bl") or w.endswith("iz"):
                        w += "e"
                    elif re.search(r"([a-z])\1$", w) and not re.search(r"(l|s|z)\1$", w):
                        w = w[:-1]
                    elif measure(w) == 1 and not re.search(r"^[^aeiou][^aeiouy][a-z]$", w):
                        w += "e"
                break

    # Step 1c
    if w.endswith("y") and any(is_vowel(ch, i) for i, ch in enumerate(w[:-1])):
        w = w[:-1] + "i"

    # Step 2 (subset)
    step2_map = {
        "ational": "ate",
        "tional": "tion",
        "enci": "ence",
        "anci": "ance",
        "izer": "ize",
        "abli": "able",
        "alli": "al",
        "entli": "ent",
        "ousli": "ous",
        "ization": "ize",
        "ation": "ate",
        "ator": "ate",
        "alism": "al",
        "iveness": "ive",
        "fulness": "ful",
        "ousness": "ous",
        "aliti": "al",
        "iviti": "ive",
        "biliti": "ble",
    }
    for suf, rep in step2_map.items():
        if w.endswith(suf):
            stem = w[:-len(suf)]
            if measure(stem) > 0:
                w = stem + rep
            break

    # Step 3 (subset)
    step3_map = {
        "icate": "ic",
        "ative": "",
        "alize": "al",
        "iciti": "ic",
        "ical": "ic",
        "ful": "",
        "ness": "",
    }
    for suf, rep in step3_map.items():
        if w.endswith(suf):
            stem = w[:-len(suf)]
            if measure(stem) > 0:
                w = stem + rep
            break

    # Step 4 (subset)
    step4_set = [
        "al", "ance", "ence", "er", "ic", "able", "ible", "ant", "ement",
        "ment", "ent", "ion", "ou", "ism", "ate", "iti", "ous", "ive", "ize"
    ]
    for suf in step4_set:
        if w.endswith(suf):
            stem = w[:-len(suf)]
            if measure(stem) > 1:
                if suf == "ion" and not (stem.endswith("s") or stem.endswith("t")):
                    break
                w = stem
            break

    # Step 5 (subset)
    if measure(w[:-1]) > 1 and w.endswith("e"):
        w = w[:-1]
    if measure(w) > 1 and re.search(r"([a-z])\1$", w) and w.endswith("l"):
        w = w[:-1]

    return w


def normalize_text(text: str) -> list:
    # Lowercase
    text = text.lower()
    # Remove punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    # Tokenize by whitespace
    tokens = [t for t in text.split() if t]
    # Remove stopwords and numeric-only tokens
    tokens = [t for t in tokens if t not in STOPWORDS and not t.isdigit()]
    # Stem
    tokens = [porter_stem(t) for t in tokens]
    return tokens


def extract_tokens(recipe: dict) -> list:
    fields = []
    # Title
    title = recipe.get("title") or recipe.get("name") or ""
    if isinstance(title, str):
        fields.append(title)
    # Ingredients (can be list or string)
    ing = recipe.get("ingredients") or recipe.get("ingredient") or []
    if isinstance(ing, list):
        fields.extend([str(x) for x in ing])
    elif isinstance(ing, str):
        fields.append(ing)
    # Steps / Instructions
    steps = recipe.get("steps") or recipe.get("instructions") or []
    if isinstance(steps, list):
        fields.extend([str(x) for x in steps])
    elif isinstance(steps, str):
        fields.append(steps)
    # Tags
    tags = recipe.get("tags") or []
    if isinstance(tags, list):
        fields.extend([str(x) for x in tags])
    elif isinstance(tags, str):
        fields.append(tags)
    # Category
    cat = recipe.get("category") or ""
    if isinstance(cat, str):
        fields.append(cat)

    combined = " \n ".join(fields)
    return normalize_text(combined)


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    recipes_dir = os.path.join(base_dir, "recipes")

    inverted_index = defaultdict(set)
    term_freq = Counter()
    ingredient_freq = Counter()
    doc_token_counts = {}
    malformed_files = []

    if not os.path.isdir(recipes_dir):
        raise SystemExit(f"Recipes directory not found: {recipes_dir}")

    for fname in sorted(os.listdir(recipes_dir)):
        if not fname.lower().endswith('.json'):
            continue
        fpath = os.path.join(recipes_dir, fname)
        doc_id = fname  # Use filename as unique doc_id
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception:
            malformed_files.append(doc_id)
            continue

        # Extract tokens
        tokens = extract_tokens(data)
        doc_token_counts[doc_id] = len(tokens)

        # Update inverted index and term frequencies
        for tok in tokens:
            inverted_index[tok].add(doc_id)
            term_freq[tok] += 1

        # Ingredient statistics (unnormalized strings to capture ingredient names better)
        ing = data.get("ingredients") or []
        if isinstance(ing, list):
            # Normalize ingredient phrases to tokens and count nouns-like words
            ing_tokens = []
            for item in ing:
                ing_tokens.extend(normalize_text(str(item)))
            for t in ing_tokens:
                ingredient_freq[t] += 1
        elif isinstance(ing, str):
            for t in normalize_text(ing):
                ingredient_freq[t] += 1

    # Convert sets to sorted lists
    inverted_index_out = {term: sorted(list(doc_ids)) for term, doc_ids in inverted_index.items()}

    # Statistics
    total_unique_terms = len(inverted_index_out)
    top20_terms = term_freq.most_common(20)
    top10_ingredients = ingredient_freq.most_common(10)
    avg_tokens = (sum(doc_token_counts.values()) / len(doc_token_counts)) if doc_token_counts else 0.0

    # Outputs
    inverted_path = os.path.join(base_dir, 'inverted_index.json')
    stats_path = os.path.join(base_dir, 'term_statistics.json')
    metadata_path = os.path.join(base_dir, 'document_metadata.json')

    with open(inverted_path, 'w', encoding='utf-8') as f:
        json.dump(inverted_index_out, f, ensure_ascii=False, indent=2)

    stats_out = {
        "total_unique_terms": total_unique_terms,
        "top_20_terms": [{"term": t, "count": c} for t, c in top20_terms],
        "top_10_ingredients": [{"term": t, "count": c} for t, c in top10_ingredients],
        "average_tokens_per_recipe": avg_tokens,
        "malformed_files": malformed_files,
    }
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats_out, f, ensure_ascii=False, indent=2)

    # Document metadata (token count per recipe)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(doc_token_counts, f, ensure_ascii=False, indent=2)

    print(f"Wrote: {inverted_path}")
    print(f"Wrote: {stats_path}")
    print(f"Wrote: {metadata_path}")
    if malformed_files:
        print("Malformed files:", ", ".join(malformed_files))


if __name__ == "__main__":
    main()
