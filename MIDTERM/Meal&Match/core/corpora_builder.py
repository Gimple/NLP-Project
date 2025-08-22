import os
import os
import csv
import json
import re

class CorporaBuilder:
    def __init__(self, csv_path="13k-recipes.csv"):
        self.csv_path = csv_path

    def build_corpora(self,
                      out_ing="ingredients_corpus.txt",
                      out_proc="process_corpus.txt",
                      out_ing_map="ingredients_map.json",
                      out_proc_map="process_map.json"):

        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"CSV not found: {self.csv_path}")

        ingredients_lines = []
        process_lines = []
        ingredients_map = {}
        process_map = {}

        with open(self.csv_path, newline="", encoding="utf-8", errors="ignore") as fh:
            reader = csv.DictReader(fh)

            fieldnames = [c.lower() for c in reader.fieldnames] if reader.fieldnames else []

            title_key = None
            ing_key = None
            inst_key = None
            image_key = None
            cleaned_ing_key = None

            for k in reader.fieldnames:
                lk = k.lower()
                if lk in ("title", "name", "recipe"):
                    title_key = k
                if "ingredient" in lk:
                    ing_key = k
                if "instruction" in lk or "direction" in lk or "step" in lk:
                    inst_key = k
                if "image" in lk:
                    image_key = k
                if "cleaned" in lk and "ingredient" in lk:
                    cleaned_ing_key = k

            if title_key is None and "title" in fieldnames:
                title_key = "title"
            if ing_key is None:
                for k in reader.fieldnames:
                    if k.lower() == "ingredients":
                        ing_key = k
            if inst_key is None:
                for k in reader.fieldnames:
                    if k.lower() == "instructions":
                        inst_key = k
            
            for row in reader:
                title = row.get(title_key, "").strip() or ("untitled-" + str(len(ingredients_map)+1))
                raw_ing = row.get(ing_key, "")
                raw_inst = row.get(inst_key, "")
                image_name = row.get(image_key, "")
                cleaned_ingredients = row.get(cleaned_ing_key, "")


                if raw_ing:
                    ingredients_lines.append(f"{title}: {raw_ing}")
                    ingredients_map[title] = raw_ing

                if raw_inst:
                    text = raw_inst.replace("\r", " ").replace("\n", " ").strip()
                    sentences = [s.strip() for s in re.split(r"[.!?;]+", text) if s.strip()]
                    steps_for_title = sentences
                    if steps_for_title:
                        process_map[title] = steps_for_title
                

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
