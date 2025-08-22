import os
import json
from core.ngram_model import NGramModel
from core.corpora_builder import simple_tokenize

class CookingRecommender:
    def __init__(self, ingredients_file="ingredients_corpus.txt", process_file="process_corpus.txt", 
                 ing_map="ingredients_map.json", proc_map="process_map.json", ngram_order=4, csv_path="13k-recipes.csv"):

        if os.path.exists(ing_map):
            with open(ing_map, "r", encoding="utf-8") as f:
                self.ingredients_map = json.load(f)
        else:

            self.ingredients_map = self.parse_ingredients_file(ingredients_file)

        if os.path.exists(proc_map):
            with open(proc_map, "r", encoding="utf-8") as f:
                self.process_map = json.load(f)
        else:
            self.process_map = self.parse_process_file(process_file)


        # Tokenized view for matching (handles both phrase lists and token lists)
        self.ingredients_map_tokens = self._normalize_ingredients_map(self.ingredients_map)

        self.ingredient_model = NGramModel(corpus_file=ingredients_file, max_n=ngram_order)
        self.process_model = NGramModel(corpus_file=process_file, max_n=min(ngram_order, 3))


        self.original_ingredients_phrases = {}
        if os.path.exists(csv_path):
            import csv
            with open(csv_path, newline='', encoding='utf-8', errors='ignore') as fh:
                reader = csv.DictReader(fh)

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

                        try:
                            import ast
                            phrases = ast.literal_eval(raw_ing)
                            if isinstance(phrases, list):
                                self.original_ingredients_phrases[title] = [p.strip() for p in phrases if p.strip()]
                            else:
                                self.original_ingredients_phrases[title] = [raw_ing.strip()]
                        except Exception:
                            self.original_ingredients_phrases[title] = [raw_ing.strip()]

        # If we didn't populate phrases from CSV, fall back to phrases found in the map
        if not self.original_ingredients_phrases:
            for title, items in self.ingredients_map.items():
                # Heuristic: keep as phrases if items look like strings with spaces or punctuation
                phrases = []
                for it in (items or []):
                    s = str(it).strip()
                    if s:
                        phrases.append(s)
                if phrases:
                    self.original_ingredients_phrases[title] = phrases

    def parse_ingredients_file(self, path):
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

    def parse_process_file(self, path):
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

                mapping[title].append(sent)
        return mapping

    def _normalize_ingredients_map(self, mapping):
        """Return a dict[title] -> list of normalized tokens for matching.

        Accepts either:
        - list of phrases (strings) per title
        - list of tokens (strings) per title
        and always outputs tokens using simple_tokenize.
        Filters out numeric quantities and common unit/utility words.
        """
        norm = {}
        skip = {
            'tsp', 'tbsp', 'tablespoon', 'tablespoons', 'teaspoon', 'teaspoons',
            'cup', 'cups', 'ounce', 'ounces', 'oz', 'lb', 'lbs', 'pound', 'pounds',
            'gram', 'grams', 'kg', 'kilogram', 'ml', 'l', 'liter', 'liters',
            'pinch', 'dash', 'plus', 'more', 'divided', 'finely', 'chopped', 'room', 'temperature',
            'freshly', 'ground', 'about', 'such', 'as'
        }
        for title, items in (mapping or {}).items():
            toks = []
            if not items:
                norm[title] = toks
                continue
            for it in items:
                s = str(it)
                for t in simple_tokenize(s):
                    if t.isdigit():
                        continue
                    if t in skip:
                        continue
                    toks.append(t)
            norm[title] = toks
        return norm

    def get_ingredients_tokens(self, dish):
        return self.ingredients_map_tokens.get(dish, [])

    def get_suggestions(self, partial_text, top_k=5):

        preds = self.ingredient_model.predict_next_words(partial_text, top_k=top_k)
        return preds  

    def find_missing_ingredients(self, user_text, min_matches=2):

        user_tokens = [t for t in simple_tokenize(user_text)]
        if not user_tokens:
            return None, [], 0
        user_set = set(user_tokens)

        best_dish = None
        best_score = 0.0
        best_match_count = 0
        best_total = 1
        for title, ing_list in self.ingredients_map_tokens.items():
            if not ing_list:
                continue
            ing_set = set(ing_list)
            match_count = len(user_set & ing_set)
            if match_count == 0:
                continue
            score = match_count / max(1, len(ing_set))

            if score > best_score or (abs(score - best_score) < 1e-9 and match_count > best_match_count):
                best_score = score
                best_dish = title
                best_match_count = match_count
                best_total = len(ing_set)

        if best_dish and best_match_count >= min_matches:
            missing_phrases = self.missing_phrases_for_dish(best_dish, user_set)
            confidence = int(round(best_score * 100))
            return best_dish, missing_phrases, confidence
        return None, [], 0

    def missing_phrases_for_dish(self, dish, user_tokens_set):
        """Return human-friendly missing ingredient phrases for a given dish.

        This uses `original_ingredients_phrases` (when available) to group tokens
        like quantities and units into readable phrases. Falls back to tokens
        present in `ingredients_map`.
        """
        if dish not in self.ingredients_map_tokens:
            return []
        if not isinstance(user_tokens_set, set):
            user_tokens_set = set(user_tokens_set or [])

        missing_tokens = [i for i in self.ingredients_map_tokens[dish] if i not in user_tokens_set]

        phrases = self.original_ingredients_phrases.get(dish, [])
        missing_phrases = []
        used = set()
        # Prefer full phrases that include any missing token
        for phrase in phrases:
            phrase_tokens = set(simple_tokenize(phrase))
            if phrase_tokens & set(missing_tokens) and phrase not in used:
                missing_phrases.append(phrase)
                used.add(phrase)

        # Ensure all tokens are represented at least once
        covered = set()
        for phrase in missing_phrases:
            covered |= set(simple_tokenize(phrase))
        for token in missing_tokens:
            if token not in covered:
                missing_phrases.append(token)
        return missing_phrases

    def get_recipe_steps(self, dish, max_steps=6):

        if dish not in self.process_map:
            return []

        return self.process_map[dish][:max_steps]

    def get_alternative_dishes(self, user_text, top_k=3):
        # Backward-compatible wrapper around ranked backoff matcher
        ranked = self.get_ranked_matches(user_text, top_k=top_k)
        return [(title, int(round(score * 100))) for title, score, _cov, _miss in ranked]

    def get_ranked_matches(self, user_text, top_k=10, alpha=0.7):
        """Return a ranked list of dishes using coverage + n-gram backoff.

        - coverage: fraction of recipe ingredients matched by user tokens
        - seq_p: geometric-mean probability of matched token sequence under the
          ingredient n-gram model using simple backoff (via score_sequence)
        - combined score: alpha*coverage + (1-alpha)*seq_p

        Returns list of tuples: (title, combined_score, coverage, missing_phrases)
        """
        from math import exp
        user_tokens = [t for t in simple_tokenize(user_text)]
        if not user_tokens:
            return []
        user_set = set(user_tokens)

        results = []
        for title, ing_list in self.ingredients_map_tokens.items():
            if not ing_list:
                continue
            ing_set = set(ing_list)
            overlap = [tok for tok in ing_list if tok in user_set]
            if not overlap:
                continue
            coverage = len(overlap) / max(1, len(ing_set))
            # sequence probability of overlap in recipe order
            avg_logp = self.ingredient_model.score_sequence(overlap)
            seq_p = exp(avg_logp) if avg_logp != float('-inf') else 0.0
            combined = alpha * coverage + (1.0 - alpha) * seq_p
            missing_phrases = self.missing_phrases_for_dish(title, user_set)
            results.append((title, combined, coverage, missing_phrases))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
