

import os
from core.corpora_builder import simple_tokenize

class NGramModel:
    def __init__(self, corpus_file=None, corpus_lines=None, max_n=4):
        self.max_n = max_n

        self.context_counts = {n: {} for n in range(1, max_n + 1)}

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

        for line in lines:

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

        uni = self.context_counts[1].get("", {})
        if not uni:
            return []
        total = sum(uni.values())
        sorted_items = sorted(uni.items(), key=lambda kv: kv[1], reverse=True)
        return [(w, cnt / total) for w, cnt in sorted_items[:top_k]]
