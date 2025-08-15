

import os
from corpora_builder import simple_tokenize

class NGramModel:
    def __init__(self, corpus_file=None, corpus_lines=None, max_n=4):
        """
        corpus_file: path to file with one tokenized line per recipe/sentence.
        corpus_lines: optional list of lines (strings).
        max_n: max order of n-gram (4 = up to 4-grams).
        """
        self.max_n = max_n
        # context_counts[n][history] = {word: count, ...}
        self.context_counts = {n: {} for n in range(1, max_n + 1)}
        # unigram counts can be read from context_counts[1]['']
        self.vocab = set()

        lines = []
        if corpus_file and os.path.exists(corpus_file):
            with open(corpus_file, "r", encoding="utf-8", errors="ignore") as f:
                lines = [l.strip() for l in f if l.strip()]
        elif corpus_lines:
            lines = [l.strip() for l in corpus_lines if l.strip()]

        if lines:
            self.train(lines)

    def train(self, lines):
        """Populate context_counts from tokenized lines.
           Each line may be 'Title: token1 token2 ...' or just 'token1 token2 ...'."""
        for line in lines:
            # if "Title: tokens..." split; keep tokens part
            if ":" in line:
                _, rest = line.split(":", 1)
                text = rest.strip()
            else:
                text = line
            tokens = [t for t in text.split() if t]
            for t in tokens:
                self.vocab.add(t)
            L = len(tokens)
            for n in range(1, self.max_n + 1):
                if L < n:
                    continue
                for i in range(L - n + 1):
                    ngram = tokens[i : i + n]
                    history = " ".join(ngram[:-1]) if n > 1 else ""
                    word = ngram[-1]
                    ctx = self.context_counts[n].setdefault(history, {})
                    ctx[word] = ctx.get(word, 0) + 1

    def predict_next_words(self, current_text, top_k=3):
        """
        Backoff prediction:
        Try history length max_n-1 down to 0:
           if there is a context_counts[n] for that history, use it and return top_k words
        Returns list of tuples: (word, probability)
        """
        tokens = [t for t in simple_tokenize(current_text)]
        for n in range(self.max_n, 0, -1):
            history_len = n - 1
            if len(tokens) < history_len:
                continue
            history = " ".join(tokens[-history_len:]) if history_len > 0 else ""
            ctx_dict = self.context_counts.get(n, {}).get(history)
            if ctx_dict:
                total = sum(ctx_dict.values())
                sorted_items = sorted(ctx_dict.items(), key=lambda kv: kv[1], reverse=True)
                return [(w, cnt / total) for w, cnt in sorted_items[:top_k]]
        # fallback: top unigrams
        uni = self.context_counts[1].get("", {})
        if not uni:
            return []
        total = sum(uni.values())
        sorted_items = sorted(uni.items(), key=lambda kv: kv[1], reverse=True)
        return [(w, cnt / total) for w, cnt in sorted_items[:top_k]]
