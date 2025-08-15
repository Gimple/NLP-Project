from corpora_builder import CorporaBuilder
from recommender import CookingRecommender
from ui import CookingUI
import os

def main():
    csv_path = "13k-recipes.csv"
    ing_file = "ingredients_corpus.txt"
    proc_file = "process_corpus.txt"
    ing_map = "ingredients_map.json"
    proc_map = "process_map.json"

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
