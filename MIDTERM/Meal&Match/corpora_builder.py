
import os
import csv
import json
import re

def simple_tokenize(s):
    """Lowercase + keep letters/digits/fractions/hyphen-as-space + split on whitespace.
    Accepts fractions like 1/2, 3/4, etc. as tokens."""
    if s is None:
        return []
    s = s.lower()
    # preserve fractions like 1/2, 3/4, etc.
    # replace all except a-z, 0-9, hyphen, and fractions (\d+/\d+)
    # First, temporarily replace fractions with a placeholder
    fraction_pattern = r"(\d+\/\d+)"
    fractions = re.findall(fraction_pattern, s)
    for i, frac in enumerate(fractions):
        s = s.replace(frac, f"__FRACTION_{i}__")
    # replace punctuation with spaces, keep alnum and hyphen
    s = re.sub(r"[^a-z0-9\-]+", " ", s)
    s = s.replace("-", " ")
    # restore fractions
    for i, frac in enumerate(fractions):
        s = s.replace(f"__FRACTION_{i}__", frac)
    return [tok for tok in s.split() if tok]


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
