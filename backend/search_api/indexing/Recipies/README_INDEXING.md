# Indexing Documentation

This directory contains the data and scripts used to build a text search index for Moroccan recipes.

## Overview
- `recipes/`: Raw recipe JSON files (one per recipe).
- `PythonScripts/`: Scripts that prepare and index the recipe corpus.
- `inverted_index.json`: The final inverted index mapping terms → document IDs and positions.
- `term_statistics.json`: Corpus-level statistics per term (e.g., DF, IDF).
- `document_metadata.json`: Per-document stats and metadata (e.g., length, title).

## Pipeline
1. Split/normalize input recipes if needed (`split_recipes.py`).
2. Build the inverted index and statistics (`build_inverted_index.py`).

## Quickstart (Windows PowerShell)
```powershell
# From this folder:
# Optional: split or normalize recipes (adjust paths/args as your script expects)
python .\PythonScripts\split_recipes.py -i .\recipes -o .\recipes

# Build inverted index and term stats
python .\PythonScripts\build_inverted_index.py -i .\recipes \
    -o . \
    --index inverted_index.json \
    --stats term_statistics.json \
    --docs document_metadata.json
```

Notes:
- If your scripts do not support the shown CLI flags, run them with their default behavior (open the files to confirm supported options).
- Ensure the Python environment is set up and that required packages are installed.

## Data Files
- `inverted_index.json`
  - `term`: String token.
  - `postings`: Array of `{ doc_id: string, positions: number[] }` entries.
- `term_statistics.json`
  - `term`: String token.
  - `df`: Document frequency (count of documents containing the term).
  - `idf`: Inverse document frequency (if computed).
  - `cf`: Collection frequency (total term occurrences across corpus).
- `document_metadata.json`
  - `doc_id`: Unique identifier (matches recipe filename stem).
  - `title`: Human-readable recipe title.
  - `length`: Token count for normalization.
  - `fields`: Optional per-field lengths (e.g., `ingredients`, `instructions`).

## Implementation Tips
- Tokenization: normalize case, strip punctuation, optionally apply stemming.
- Stopwords: consider excluding very common function words.
- Positions: store token positions to support phrase queries and proximity scoring.
- Scoring: use TF-IDF or BM25; `term_statistics.json` and `document_metadata.json` provide needed stats.

## Updating the Index
- Add or edit recipes under `recipes/`.
- Re-run `build_inverted_index.py` to regenerate `inverted_index.json`, `term_statistics.json`, and `document_metadata.json`.

## Troubleshooting
- Verify paths: use absolute or relative paths from this folder.
- Check JSON integrity: large files should be valid JSON; use a linter or viewer.
- Encoding: ensure recipes are UTF-8 encoded.