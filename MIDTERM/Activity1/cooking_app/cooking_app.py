"""
cooking_app.py
Pure Python (built-ins only). Usage:
  1) Put 13k-recipes.csv (downloaded from the GitHub repo) in the same folder.
  2) Run: python cooking_app.py
  The script will build corpora files if missing, train simple n-gram models,
  then open the Tkinter UI.
"""

import os
import csv
import json
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

# -----------------------
# Utility tokenizer
# -----------------------
def simple_tokenize(s):
    """Lowercase + keep letters/digits/hyphen-as-space + split on whitespace."""
    if s is None:
        return []
    s = s.lower()
    # replace punctuation with spaces, keep alnum and hyphen
    s = re.sub(r"[^a-z0-9\-]+", " ", s)
    s = s.replace("-", " ")
    return [tok for tok in s.split() if tok]


# -----------------------
# CorporaBuilder (OOP)
# -----------------------
class CorporaBuilder:
    def __init__(self, csv_path="13k-recipes.csv"):
        self.csv_path = csv_path

    def parse_ingredient_field(self, ing_field):
        """
        Handles several common ingredient formats:
        - Python list-like: "['salt', 'pepper']"
        - comma-separated: "salt, pepper"
        - one-line: "salt pepper"
        Returns token list.
        """
        if not ing_field:
            return []
        text = ing_field.strip()
        # remove bracket wrappers if present
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        # drop quotes
        text = text.replace('"', " ").replace("'", " ")
        # split on commas then tokenize each part
        parts = [p.strip() for p in text.split(",") if p.strip()]
        tokens = []
        if parts:
            for p in parts:
                tokens.extend(simple_tokenize(p))
        else:
            tokens = simple_tokenize(text)
        return tokens

    def build_corpora(self,
                      out_ing="ingredients_corpus.txt",
                      out_proc="process_corpus.txt",
                      out_ing_map="ingredients_map.json",
                      out_proc_map="process_map.json"):
        """
        Reads CSV and writes:
          - ingredients_corpus.txt (lines: Title: token1 token2 ...)
          - process_corpus.txt     (lines: Title: tokenized sentence)
          - ingredients_map.json   (title -> [ingredient tokens])
          - process_map.json       (title -> [original sentence texts])
        """
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")

        ingredients_lines = []
        process_lines = []
        ingredients_map = {}
        process_map = {}

        with open(self.csv_path, newline="", encoding="utf-8", errors="ignore") as fh:
            reader = csv.DictReader(fh)
            # try to find expected column names
            fieldnames = [c.lower() for c in reader.fieldnames] if reader.fieldnames else []
            # determine keys
            title_key = None
            ing_key = None
            inst_key = None
            for k in reader.fieldnames:
                lk = k.lower()
                if lk in ("title", "name", "recipe"):
                    title_key = k
                if "ingredient" in lk:
                    ing_key = k
                if "instruction" in lk or "direction" in lk or "step" in lk:
                    inst_key = k
            # fallback: use common names
            if title_key is None and "title" in fieldnames:
                title_key = "title"
            if ing_key is None:
                # try exact "ingredients"
                for k in reader.fieldnames:
                    if k.lower() == "ingredients":
                        ing_key = k
            if inst_key is None:
                for k in reader.fieldnames:
                    if k.lower() == "instructions":
                        inst_key = k
            if ing_key is None or inst_key is None:
                raise RuntimeError("CSV missing expected columns. Look for columns named like 'ingredients' and 'instructions'.")

            for row in reader:
                title = row.get(title_key, "").strip() or ("untitled-" + str(len(ingredients_map)+1))
                raw_ing = row.get(ing_key, "")
                raw_inst = row.get(inst_key, "")

                # ingredients
                ing_tokens = self.parse_ingredient_field(raw_ing)
                if ing_tokens:
                    ingredients_lines.append(f"{title}: {' '.join(ing_tokens)}")
                    ingredients_map[title] = ing_tokens

                # instructions -> split into sentences and tokenize per sentence
                if raw_inst:
                    # normalize newlines and split by sentence punctuation
                    text = raw_inst.replace("\r", " ").replace("\n", " ").strip()
                    # split on .,!?; (keep sentences reasonably sized)
                    sentences = [s.strip() for s in re.split(r"[.!?;]+", text) if s.strip()]
                    steps_for_title = []
                    for s in sentences:
                        toks = simple_tokenize(s)
                        if toks:
                            process_lines.append(f"{title}: {' '.join(toks)}")
                            steps_for_title.append(s.strip())
                    if steps_for_title:
                        process_map[title] = steps_for_title

        # write outputs
        with open(out_ing, "w", encoding="utf-8") as f:
            f.write("\n".join(ingredients_lines))
        with open(out_proc, "w", encoding="utf-8") as f:
            f.write("\n".join(process_lines))
        with open(out_ing_map, "w", encoding="utf-8") as f:
            json.dump(ingredients_map, f, indent=2, ensure_ascii=False)
        with open(out_proc_map, "w", encoding="utf-8") as f:
            json.dump(process_map, f, indent=2, ensure_ascii=False)

        print(f"Built corpora: {out_ing} ({len(ingredients_lines)} lines), {out_proc} ({len(process_lines)} lines)")
        print(f"Saved mapping JSON: {out_ing_map}, {out_proc_map}")


# -----------------------
# NGramModel
# -----------------------
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


# -----------------------
# CookingRecommender
# -----------------------
class CookingRecommender:
    def __init__(self,
                 ingredients_file="ingredients_corpus.txt",
                 process_file="process_corpus.txt",
                 ing_map="ingredients_map.json",
                 proc_map="process_map.json",
                 ngram_order=4):
        # load maps if present (faster) else parse corpus files
        if os.path.exists(ing_map):
            with open(ing_map, "r", encoding="utf-8") as f:
                self.ingredients_map = json.load(f)
        else:
            # fallback parse file
            self.ingredients_map = self._parse_ingredients_file(ingredients_file)

        if os.path.exists(proc_map):
            with open(proc_map, "r", encoding="utf-8") as f:
                self.process_map = json.load(f)
        else:
            self.process_map = self._parse_process_file(process_file)

        # build n-gram models
        self.ingredient_model = NGramModel(corpus_file=ingredients_file, max_n=ngram_order)
        self.process_model = NGramModel(corpus_file=process_file, max_n=min(ngram_order, 3))

    def _parse_ingredients_file(self, path):
        mapping = {}
        if not os.path.exists(path):
            return mapping
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" not in line:
                    continue
                title, rest = line.split(":", 1)
                toks = [t for t in rest.strip().split() if t]
                mapping[title.strip()] = toks
        return mapping

    def _parse_process_file(self, path):
        mapping = {}
        if not os.path.exists(path):
            return mapping
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if ":" not in line:
                    continue
                title, rest = line.split(":", 1)
                title = title.strip()
                sent = rest.strip()
                if title not in mapping:
                    mapping[title] = []
                # keep sentence text as tokens joined (we store tokenized sentence)
                mapping[title].append(sent)
        return mapping

    def get_suggestions(self, partial_text, top_k=5):
        """Return list of suggested next words (strings) with scores."""
        preds = self.ingredient_model.predict_next_words(partial_text, top_k=top_k)
        return preds  # list of (word, prob)

    def find_missing_ingredients(self, user_text, min_matches=2):
        """
        user_text: free text the user typed (ingredients separated by spaces/commas)
        Returns: (best_dish_or_None, missing_list, confidence_percent)
        Confidence is match_count / total_ingredients_of_recipe * 100
        """
        user_tokens = [t for t in simple_tokenize(user_text)]
        if not user_tokens:
            return None, [], 0
        user_set = set(user_tokens)

        best_dish = None
        best_score = 0.0
        best_match_count = 0
        best_total = 1
        for title, ing_list in self.ingredients_map.items():
            if not ing_list:
                continue
            ing_set = set(ing_list)
            match_count = len(user_set & ing_set)
            if match_count == 0:
                continue
            score = match_count / max(1, len(ing_set))
            # prefer higher score, break ties by more exact match_count
            if score > best_score or (abs(score - best_score) < 1e-9 and match_count > best_match_count):
                best_score = score
                best_dish = title
                best_match_count = match_count
                best_total = len(ing_set)

        if best_dish and best_match_count >= min_matches:
            missing = [i for i in self.ingredients_map[best_dish] if i not in user_set]
            confidence = int(round(best_score * 100))
            return best_dish, missing, confidence
        return None, [], 0

    def get_recipe_steps(self, dish, max_steps=6):
        """Return the stored process sentences (tokenized) for the dish (first N)."""
        if dish not in self.process_map:
            return []
        # process_map stores tokenized sentences (strings). Return first N.
        return self.process_map[dish][:max_steps]

    def get_alternative_dishes(self, user_text, top_k=3):
        """Return top K matching dishes with their match percentage."""
        user_tokens = [t for t in simple_tokenize(user_text)]
        if not user_tokens:
            return []
        user_set = set(user_tokens)
        scores = []
        for title, ing_list in self.ingredients_map.items():
            if not ing_list:
                continue
            ing_set = set(ing_list)
            match_count = len(user_set & ing_set)
            if match_count == 0:
                continue
            score = match_count / max(1, len(ing_set))
            scores.append((title, int(round(score * 100))))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]


# -----------------------
# CookingUI (Tkinter)
# -----------------------
class CookingUI:
    def __init__(self, recommender: CookingRecommender):
        self.recommender = recommender
        self.root = tk.Tk()
        self.root.title("Simple Cooking Recommender")
        self._build_widgets()
        self._bind_events()

    def _build_widgets(self):
        frm_top = tk.Frame(self.root)
        frm_top.pack(fill="x", padx=8, pady=6)

        tk.Label(frm_top, text="Type ingredients (separate with spaces or commas):").pack(anchor="w")
        self.entry = tk.Entry(frm_top, width=70)
        self.entry.pack(fill="x", padx=2, pady=2)

        frm_mid = tk.Frame(self.root)
        frm_mid.pack(fill="x", padx=8, pady=4)
        tk.Label(frm_mid, text="Suggestions: (double-click to insert)").pack(anchor="w")
        self.suggestions_listbox = tk.Listbox(frm_mid, height=5, width=50)
        self.suggestions_listbox.pack(side="left", fill="x", expand=True)
        self.suggestions_scroll = tk.Scrollbar(frm_mid, orient="vertical", command=self.suggestions_listbox.yview)
        self.suggestions_scroll.pack(side="right", fill="y")
        self.suggestions_listbox.config(yscrollcommand=self.suggestions_scroll.set)

        frm_confirm = tk.Frame(self.root)
        frm_confirm.pack(fill="x", padx=8, pady=6)
        self.confirm_label = tk.Label(frm_confirm, text="", font=("Arial", 12, "bold"))
        self.confirm_label.pack(anchor="w")
        self.missing_text = tk.Text(frm_confirm, height=3, width=70)
        self.missing_text.pack(fill="x", pady=4)

        frm_buttons = tk.Frame(self.root)
        frm_buttons.pack(fill="x", padx=8, pady=4)
        self.yes_button = tk.Button(frm_buttons, text="Yes", state="disabled", width=10, command=self.on_yes)
        self.no_button = tk.Button(frm_buttons, text="No", state="disabled", width=10, command=self.on_no)
        self.alt_button = tk.Button(frm_buttons, text="Alternatives", width=12, command=self.show_alternatives)
        self.yes_button.pack(side="left", padx=4)
        self.no_button.pack(side="left", padx=4)
        self.alt_button.pack(side="left", padx=8)

        frm_steps = tk.Frame(self.root)
        frm_steps.pack(fill="both", expand=True, padx=8, pady=6)
        tk.Label(frm_steps, text="Suggested steps:").pack(anchor="w")
        self.steps_box = scrolledtext.ScrolledText(frm_steps, height=12, wrap="word")
        self.steps_box.pack(fill="both", expand=True)

    def _bind_events(self):
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.suggestions_listbox.bind("<Double-Button-1>", self.on_suggestion_double)
        # allow Enter to accept first suggestion
        self.entry.bind("<Return>", lambda e: self.accept_first_suggestion())

    # ---------- events ----------
    def on_key_release(self, event):
        text = self.entry.get().strip()
        # update suggestions
        preds = self.recommender.get_suggestions(text, top_k=6)
        self.suggestions_listbox.delete(0, tk.END)
        for w, p in preds:
            self.suggestions_listbox.insert(tk.END, f"{w}  ({p:.2f})")

        # attempt to detect dish
        dish, missing, confidence = self.recommender.find_missing_ingredients(text)
        if dish:
            self.confirm_label.config(text=f"Are you cooking {dish}?   Confidence: {confidence}%")
            self.missing_text.delete("1.0", tk.END)
            if missing:
                self.missing_text.insert(tk.END, "Missing: " + ", ".join(missing))
            else:
                self.missing_text.insert(tk.END, "No missing ingredients detected.")
            self.yes_button.config(state="normal")
            self.no_button.config(state="normal")
        else:
            self.confirm_label.config(text="")
            self.missing_text.delete("1.0", tk.END)
            self.yes_button.config(state="disabled")
            self.no_button.config(state="disabled")
            self.steps_box.delete("1.0", tk.END)

    def on_suggestion_double(self, event):
        sel = self.suggestions_listbox.get(tk.ACTIVE)
        if not sel:
            return
        # format "word  (0.23)" -> extract first token as word
        word = sel.split()[0]
        cur = self.entry.get().strip()
        if cur and not cur.endswith(" "):
            cur = cur + " "
        self.entry.delete(0, tk.END)
        self.entry.insert(0, cur + word + " ")
        # trigger immediate update
        self.on_key_release(None)

    def accept_first_suggestion(self):
        if self.suggestions_listbox.size() > 0:
            sel = self.suggestions_listbox.get(0)
            self.suggestions_listbox.selection_set(0)
            self.on_suggestion_double(None)

    def on_yes(self):
        # read dish from confirm label
        text = self.confirm_label.cget("text")
        if not text:
            return
        # parse "Are you cooking {dish}?   Confidence: {N}%"
        parts = text.split("?")[0]
        dish = parts.replace("Are you cooking", "").strip()
        if not dish:
            return
        steps = self.recommender.get_recipe_steps(dish, max_steps=10)
        self.steps_box.delete("1.0", tk.END)
        if not steps:
            self.steps_box.insert(tk.END, "No steps available for this dish in the corpus.")
            return
        # show steps (original sentences)
        for i, s in enumerate(steps, start=1):
            self.steps_box.insert(tk.END, f"Step {i}: {s}\n\n")

    def on_no(self):
        self.confirm_label.config(text="Okay — let's try another dish. Show alternatives or add more ingredients.")
        self.steps_box.delete("1.0", tk.END)

    def show_alternatives(self):
        text = self.entry.get().strip()
        alts = self.recommender.get_alternative_dishes(text, top_k=6)
        if not alts:
            messagebox.showinfo("Alternatives", "No close dish matches found. Try adding more ingredients.")
            return
        msg = "\n".join([f"{title} — match {pct}%" for title, pct in alts])
        messagebox.showinfo("Alternative dishes", msg)

    def run(self):
        self.root.mainloop()


# -----------------------
# Run everything
# -----------------------
def main():
    # filenames
    csv_path = "13k-recipes.csv"
    ing_file = "ingredients_corpus.txt"
    proc_file = "process_corpus.txt"
    ing_map = "ingredients_map.json"
    proc_map = "process_map.json"

    # if corpora not already created, build them
    if not (os.path.exists(ing_file) and os.path.exists(proc_file) and os.path.exists(ing_map) and os.path.exists(proc_map)):
        print("Building corpora from CSV (this runs once) ...")
        builder = CorporaBuilder(csv_path=csv_path)
        builder.build_corpora(out_ing=ing_file, out_proc=proc_file, out_ing_map=ing_map, out_proc_map=proc_map)
    else:
        print("Corpora and maps found. Skipping build step.")

    print("Loading recommender (this may take a few seconds)...")
    recommender = CookingRecommender(ingredients_file=ing_file, process_file=proc_file, ing_map=ing_map, proc_map=proc_map, ngram_order=4)
    print("Launching UI...")
    app = CookingUI(recommender)
    app.run()


if __name__ == "__main__":
    main()
