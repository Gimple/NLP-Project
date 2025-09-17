from __future__ import annotations
import sys
import string
from typing import List, Set, Optional
import re


# =======================
# CLEANER SESSION
# =======================
def remove_emoji(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub('', text)


def preserve_punctuation(text: str, preserve: str = ".,!?:;\"'") -> str:
    to_remove = ''.join(ch for ch in string.punctuation if ch not in set(preserve))
    if not to_remove:
        return text
    pattern = '[' + re.escape(to_remove) + r']+'
    return re.sub(pattern, '', text)


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
# WASHING SESSION
# =======================
def clean_text(text: str, dictionary: Optional[Set[str]] = None, log: bool = False, logger=None) -> str:
    # Step 1: remove emoji
    step1 = remove_emoji(text)
    if log:
        _debug_print('after_remove_emoji', step1, logger)

    # Step 2: remove punctuation
    step2 = preserve_punctuation(step1)
    if log:
        _debug_print('after_preserving_punctuation', step2, logger)

    # Step 3: lowercase all
    step3 = step2.lower()
    if log:
        _debug_print('after_lowercase', step3, logger)

    # Step 4: tokenize
    tokens = simple_tokenize(step3)
    if log:
        _debug_print('tokenization', tokens, logger)

    joined = ' '.join(tokens)
    if log:
        _debug_print('final_cleaned_text', joined, logger)

    return joined


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print('Usage: python cleaner_auto.py "text to clean"')
        return 1
    text = ' '.join(argv)
    cleaned = clean_text(text, log=True)
    print(f"final output: {cleaned}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())