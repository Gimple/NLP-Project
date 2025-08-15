
import os
import json
from ngram_model import NGramModel
from corpora_builder import simple_tokenize

class CookingRecommender:
    def __init__(self,
                 ingredients_file="ingredients_corpus.txt",
                 process_file="process_corpus.txt",
                 ing_map="ingredients_map.json",
                 proc_map="process_map.json",
                 ngram_order=4,
                 csv_path="13k-recipes.csv"):
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

        # Load original ingredient phrases for each recipe title
        self.original_ingredients_phrases = {}
        if os.path.exists(csv_path):
            import csv
            with open(csv_path, newline='', encoding='utf-8', errors='ignore') as fh:
                reader = csv.DictReader(fh)
                # find title and ingredient columns
                title_key = None
                ing_key = None
                for k in reader.fieldnames:
                    lk = k.lower()
                    if lk in ("title", "name", "recipe"):
                        title_key = k
                    if "ingredient" in lk:
                        ing_key = k
                for row in reader:
                    title = row.get(title_key, "").strip() if title_key else None
                    raw_ing = row.get(ing_key, "") if ing_key else None
                    if title and raw_ing:
                        # Try to parse as Python list, fallback to string
                        try:
                            import ast
                            phrases = ast.literal_eval(raw_ing)
                            if isinstance(phrases, list):
                                self.original_ingredients_phrases[title] = [p.strip() for p in phrases if p.strip()]
                            else:
                                self.original_ingredients_phrases[title] = [raw_ing.strip()]
                        except Exception:
                            self.original_ingredients_phrases[title] = [raw_ing.strip()]

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
        Returns: (best_dish_or_None, missing_phrases, confidence_percent)
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
            missing_tokens = [i for i in self.ingredients_map[best_dish] if i not in user_set]
            # Try to map missing tokens to original ingredient phrases
            phrases = self.original_ingredients_phrases.get(best_dish, [])
            missing_phrases = []
            used = set()
            for phrase in phrases:
                phrase_tokens = set(simple_tokenize(phrase))
                if phrase_tokens & set(missing_tokens) and phrase not in used:
                    missing_phrases.append(phrase)
                    used.add(phrase)
            # If any missing tokens are not covered, add them as fallback
            covered = set()
            for phrase in missing_phrases:
                covered |= set(simple_tokenize(phrase))
            for token in missing_tokens:
                if token not in covered:
                    missing_phrases.append(token)
            confidence = int(round(best_score * 100))
            return best_dish, missing_phrases, confidence
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
