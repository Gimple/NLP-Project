
import tkinter as tk
from tkinter import scrolledtext, messagebox
from recommender import CookingRecommender

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
                # Human-readable list: a, b, and c (now using phrases)
                if len(missing) == 1:
                    missing_str = missing[0]
                elif len(missing) == 2:
                    missing_str = f"{missing[0]} and {missing[1]}"
                else:
                    missing_str = ", ".join(missing[:-1]) + f", and {missing[-1]}"
                self.missing_text.insert(tk.END, f"Missing: {missing_str}")
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

        alt_win = tk.Toplevel(self.root)
        alt_win.title("Alternative Dishes")
        tk.Label(alt_win, text="Select a dish:", font=("Arial", 12, "bold")).pack(padx=10, pady=8)

        for title, pct in alts:
            btn = tk.Button(alt_win, text=f"{title} — match {pct}%", width=50, anchor="w",
                            command=lambda t=title: self._select_alternative_dish(t, alt_win))
            btn.pack(fill="x", padx=10, pady=3)

    def _select_alternative_dish(self, dish, win):
        # Update the confirm label and missing ingredients for the selected dish
        # Find missing ingredients for this dish (simulate as if user entered the right ingredients for this dish)
        # We'll use the current entry text to determine what the user has
        user_text = self.entry.get().strip()
        # Use the same logic as find_missing_ingredients, but force the dish
        user_tokens = set(self.recommender.ingredient_model.vocab & set(user_text.split()))
        ing_list = self.recommender.ingredients_map.get(dish, [])
        missing = [i for i in ing_list if i not in user_tokens]
        # Use the original phrases for this dish
        phrases = self.recommender.original_ingredients_phrases.get(dish, [])
        missing_phrases = []
        used = set()
        from corpora_builder import simple_tokenize
        for phrase in phrases:
            phrase_tokens = set(simple_tokenize(phrase))
            if phrase_tokens & set(missing) and phrase not in used:
                missing_phrases.append(phrase)
                used.add(phrase)
        covered = set()
        for phrase in missing_phrases:
            covered |= set(simple_tokenize(phrase))
        for token in missing:
            if token not in covered:
                missing_phrases.append(token)
        # Calculate confidence
        match_count = len(set(user_text.split()) & set(ing_list))
        confidence = int(round(match_count / max(1, len(ing_list)) * 100))
        # Update main window
        self.confirm_label.config(text=f"Are you cooking {dish}?   Confidence: {confidence}%")
        self.missing_text.delete("1.0", tk.END)
        if missing_phrases:
            if len(missing_phrases) == 1:
                missing_str = missing_phrases[0]
            elif len(missing_phrases) == 2:
                missing_str = f"{missing_phrases[0]} and {missing_phrases[1]}"
            else:
                missing_str = ", ".join(missing_phrases[:-1]) + f", and {missing_phrases[-1]}"
            self.missing_text.insert(tk.END, f"Missing: {missing_str}")
        else:
            self.missing_text.insert(tk.END, "No missing ingredients detected.")
        self.yes_button.config(state="normal")
        self.no_button.config(state="normal")
        self.steps_box.delete("1.0", tk.END)
        win.destroy()

    def run(self):
        self.root.mainloop()
