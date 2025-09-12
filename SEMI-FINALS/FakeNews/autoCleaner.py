from __future__ import annotations

import csv
import os
import sys
import string
from typing import List, Set, Tuple


# =======================
# CLEANER SESSION
# =======================
def remove_special_chars(text: str) -> str:
    allowed_punct = set(".,!?")
    out_chars: List[str] = []
    for ch in text:
        # Whitespace (letters/digits)
        if ch.isprintable() and (ch.isalnum() or ch.isspace() or ch in allowed_punct):
            out_chars.append(ch)
        else:
            out_chars.append(' ')
    return ''.join(out_chars)


def simple_tokenize(text: str) -> List[str]:
    # Tokenize
    parts = text.split()
    return parts


def _debug_print(stage: str, value: object, logger=None) -> None:
    msg = f"[pipeline] {stage}: {value}"
    if logger:
        try:
            logger(msg)
        except Exception:
            print(msg)
    else:
        print(msg)

# =======================
# EXECUTING & MATCHING
# =======================
def load_wordlist(csv_path: str | List[str]) -> Set[str]:
    if isinstance(csv_path, str):
        paths = [csv_path]
    else:
        paths = list(csv_path)

    words: Set[str] = set()
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p, newline='', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            for row in reader:
                if not row:
                    continue
                w = row[0].strip()
                if not w:
                    continue
                words.add(w.lower())
    return words


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if la == 0:
        return lb
    if lb == 0:
        return la
    prev = list(range(lb + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i] + [0] * lb
        for j, cb in enumerate(b, start=1):
            add = prev[j] + 1
            delete = cur[j - 1] + 1
            change = prev[j - 1] + (0 if ca == cb else 1)
            cur[j] = min(add, delete, change)
        prev = cur
    return prev[lb]


def best_match(token: str, dictionary: Set[str], max_distance: int = 2) -> Tuple[str, int]:
    token_l = token.lower()
    if token_l in dictionary:
        return token, 0

    candidates = [w for w in dictionary if w.startswith(token_l[:3])] if len(token_l) >= 3 else []
    if candidates:
        best = min(candidates, key=lambda w: (levenshtein(token_l, w), len(w)))
        dist = levenshtein(token_l, best)
        if dist <= max_distance:
            return best, dist

    best_word = None
    best_dist = max_distance + 1
    for w in dictionary:
        if abs(len(w) - len(token_l)) > max_distance:
            continue
        d = levenshtein(token_l, w)
        if d < best_dist:
            best_dist = d
            best_word = w
            if d == 0:
                break
    if best_word is not None and best_dist <= max_distance:
        return best_word, best_dist

    return token, -1

# =======================
# WASHING SESSION
# =======================
def clean_text(text: str, dictionary: Set[str], log: bool = False, logger=None) -> str:
    cleaned = remove_special_chars(text)
    if log:
        _debug_print('after_remove_special_chars', cleaned, logger)

    tokens = simple_tokenize(cleaned)
    if log:
        _debug_print('tokenization', tokens, logger)

    out_tokens: List[str] = []
    for tok in tokens:
        # PrePunc
        stripped = tok.strip(string.punctuation)
        if not stripped:
            out_tokens.append(tok)
            continue

        match, dist = best_match(stripped, dictionary)
        prefix = tok[:tok.find(stripped)] if tok.find(stripped) != -1 else ''
        suffix = tok[tok.find(stripped) + len(stripped):] if tok.find(stripped) != -1 else ''
        result_token = prefix + (match if dist != -1 else stripped) + suffix
        if dist == 0:
            out_tokens.append(result_token)
        elif dist > 0:
            out_tokens.append(result_token)
        else:
            out_tokens.append(prefix + stripped + suffix)

        if log:
            _debug_print(f"per_token: '{tok}'", {'stripped': stripped, 'match': match, 'dist': dist, 'result': result_token}, logger)

    joined = ' '.join(out_tokens)
    if log:
        _debug_print('joined_before_punct_fix', joined, logger)

    for p in '.,!?:;':
        joined = joined.replace(' ' + p, p)

    if log:
        _debug_print('final_cleaned_text', joined, logger)

    return joined


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print('Usage: python cleaner_auto.py "text to clean"')
        return 1
    text = ' '.join(argv)
    base_dir = os.path.dirname(__file__)
    csv_path = os.path.join(base_dir, 'english_words.csv')
    dictionary = load_wordlist(csv_path)
    cleaned = clean_text(text, dictionary, log=True)
    print(f"final output: {cleaned}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())