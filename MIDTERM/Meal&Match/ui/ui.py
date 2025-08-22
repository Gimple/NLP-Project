import dearpygui.dearpygui as dpg
from core.recommender import CookingRecommender
from core.corpora_builder import simple_tokenize



class CookingUI:
    def __init__(self, recommender: CookingRecommender):
        self.recommender = recommender
        self.selected_ingredients = set()
        self.current_dish = None
        self.current_confidence = 0
        self.current_missing = []
        self.show_intro = True

        self.ingredient_categories = {
            "Meat & Protein": ["chicken", "beef", "pork", "fish", "shrimp", "egg", "turkey", "sausage", "bacon", "ham", "lamb"],
            "Vegetables": ["onion", "garlic", "tomato", "carrot", "potato", "spinach", "broccoli", "bell pepper", "mushroom", "cabbage", "lettuce", "cucumber", "celery", "zucchini", "corn", "peas", "green beans", "eggplant", "cauliflower", "asparagus", "brussels sprouts"],
            "Condiments & Seasonings": ["salt", "black pepper", "red pepper flakes", "cayenne pepper", "soy sauce", "vinegar", "sugar", "oil", "mustard", "ketchup", "mayonnaise", "honey", "cinnamon", "ginger", "basil", "oregano", "thyme", "rosemary", "hot sauce", "olive oil", "coconut oil", "sesame oil", "peanut oil"],
            "Rice & Grains": ["rice", "noodles", "pasta", "bread", "quinoa", "couscous", "barley", "oats", "cornmeal", "flour", "polenta", "bulgur", "millet", "buckwheat", "farro", "wild rice", "soba noodles", "udon noodles", "spaghetti", "macaroni"],
            "Fruits": ["apple", "banana", "orange", "grape", "strawberry", "blueberry", "peach", "pear", "kiwi", "pineapple", "mango", "watermelon", "lemon", "lime", "avocado", "pomegranate", "coconut", "plum", "cherry", "apricot", "fig"],
            "Herbs & Spices": ["parsley", "cilantro", "mint", "dill", "chili powder", "cumin", "paprika", "turmeric", "curry powder", "bay leaf", "cardamom", "cloves", "nutmeg", "allspice", "fennel", "coriander", "sage", "tarragon", "lemongrass", "chervil"],
            "Dairy & Others": ["milk", "cheese", "butter", "yogurt", "cream", "sour cream", "coconut milk", "almond milk", "peanut butter", "jam", "nuts", "seeds", "beans", "lentils", "chickpeas", "hummus", "salsa", "pesto", "sriracha"]
        }

        self.setup_gui()

    # ---------------- Fonts & Themes ----------------
    def setup_fonts(self):
        with dpg.font_registry():
            self.big_font = dpg.add_font("fonts/ATOP.ttf", 42)
            self.header_font = dpg.add_font("fonts/ATOP.ttf", 28)
            self.normal_font = dpg.add_font("fonts/ATOP.ttf", 20)

    def setup_themes(self):
        with dpg.theme() as self.global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, [30, 30, 30, 255])   # dark background
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 255, 255])   # white text
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, [60, 60, 60, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 12)

        # Section headers
        with dpg.theme() as self.section_header_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 180, 100, 255])  # orange-yellow

        # Title (tomato red)
        with dpg.theme() as self.title_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 90, 90, 255])

        # Subtitle (grey)
        with dpg.theme() as self.subtitle_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [180, 180, 180, 255])  # grey

        # Buttons
        with dpg.theme() as self.primary_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [255, 160, 70, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [255, 190, 110, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [230, 120, 40, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 8)

        with dpg.theme() as self.secondary_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [140, 180, 250, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [170, 200, 255, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [100, 140, 220, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 14, 8)

        with dpg.theme() as self.success_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [120, 200, 140, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [150, 220, 160, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [90, 170, 110, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)

        with dpg.theme() as self.danger_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [230, 120, 120, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [250, 140, 140, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [200, 90, 90, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 15)

        dpg.bind_theme(self.global_theme)

    # ---------------- GUI Setup ----------------
    def setup_gui(self):
        dpg.create_context()
        self.setup_fonts()
        self.setup_themes()

        if self.show_intro:
            self.create_intro_window()
        self.create_main_window()

        dpg.create_viewport(title="Meal&Match - Cooking Recommender", width=1200, height=800)

        if self.show_intro:
            dpg.set_primary_window("Intro", True)
        else:
            dpg.set_primary_window("Main", True)


    def create_intro_window(self):
        with dpg.window(label="Welcome", tag="Intro", width=1200, height=800, no_scrollbar=True):
            with dpg.group(horizontal=True):
                # Left content (centered with spacer)
                with dpg.child_window(width=600, height=800, no_scrollbar=True):
                    dpg.add_spacer(height=150)  
                    with dpg.group(horizontal=True):
                        dpg.add_spacer(width=120)  
                        with dpg.group():  
                            dpg.add_text("MEAL & MATCH", tag="intro_title")
                            dpg.bind_item_theme("intro_title", self.title_theme)
                            dpg.bind_item_font("intro_title", self.big_font)

                            dpg.add_spacer(height=20)
                            dpg.add_text("Cooking Recommender", tag="intro_subtitle")
                            dpg.bind_item_font("intro_subtitle", self.header_font)
                            dpg.bind_item_theme("intro_subtitle", self.subtitle_theme)

                            dpg.add_spacer(height=40)
                            dpg.add_text(
                                "Find recipes from your ingredients.\n"
                                "See missing items.\n"
                                "Follow easy cooking steps.",
                                wrap=400
                            )

                            dpg.add_spacer(height=60)
                            dpg.add_button(
                                label="Start Cooking!",
                                callback=self.start_main_app,
                                tag="start_button", width=250, height=60
                            )
                            dpg.bind_item_theme("start_button", self.primary_button_theme)

                tex = dpg.load_image("burger.png")
                if tex:
                    width, height, channels, data = tex
                    with dpg.texture_registry(show=False):
                        dpg.add_static_texture(width, height, data, tag="burger_texture")

                    with dpg.child_window(width=580, height=800, no_scrollbar=True):
                        dpg.add_spacer(height=100)  # push image down
                        with dpg.group(horizontal=True):
                            dpg.add_spacer(width=100)
                            scale = min(300 / width, 300 / height)
                            dpg.add_image("burger_texture", width=int(width * scale), height=int(height * scale))
                else:
                    with dpg.child_window(width=580, height=800, no_scrollbar=True):
                        dpg.add_text("burger.png not found")


    def create_main_window(self):
        with dpg.window(label="Meal&Match", tag="Main", width=1200, height=800, show=False):
            dpg.add_button(label="Home", callback=self.go_home, tag="home_button", pos=[1120, 10], width=70)

            dpg.add_text("MEAL & MATCH - Cooking Recommender", tag="main_title")
            dpg.bind_item_theme("main_title", self.title_theme)
            dpg.bind_item_font("main_title", self.header_font)
            dpg.add_separator()

            with dpg.group(horizontal=True):
                # Left - Ingredients
                with dpg.child_window(width=600, height=650):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Select Your Ingredients", tag="ingredient_header")
                        dpg.bind_item_theme("ingredient_header", self.section_header_theme)
                        dpg.add_spacer(width=20)
                        dpg.add_button(label="Clear All", callback=self.clear_all, tag="clear_button")
                        dpg.bind_item_theme("clear_button", self.danger_button_theme)

                    dpg.add_spacer(height=10)
                    dpg.add_text("Selected Ingredients:", tag="selected_label")
                    dpg.add_text("None selected", tag="selected_display", wrap=580)

                    for category, ingredients in self.ingredient_categories.items():
                        with dpg.collapsing_header(label=category, default_open=True):
                            dpg.bind_item_theme(dpg.last_item(), self.section_header_theme)
                            # sort ingredients alphabetically
                            sorted_ingredients = sorted(ingredients, key=lambda x: x.lower())
                            # 6 checkboxes per row
                            for i in range(0, len(sorted_ingredients), 6):
                                with dpg.group(horizontal=True):
                                    for j in range(6):
                                        if i + j < len(sorted_ingredients):
                                            ing = sorted_ingredients[i + j]
                                            dpg.add_checkbox(
                                                label=ing.title(),
                                                callback=self.on_ingredient_toggle,
                                                user_data=ing,
                                                tag=f"check_{ing}"
                                            )

                # Right - Results
                # Right - Results
                with dpg.child_window(width=600, height=650):
                    dpg.add_text("Recipe Recommendations", tag="recipe_header")
                    dpg.bind_item_theme("recipe_header", self.section_header_theme)

                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Show Match Recipe", callback=self.show_alternatives,
                                    tag="alt_button", width=180)
                        dpg.bind_item_theme("alt_button", self.secondary_button_theme)

                    dpg.add_spacer(height=10)

                    # text area for recipe suggestion
                    dpg.add_input_text(
                        multiline=True,
                        readonly=True,
                        tag="dish_suggestion",
                        default_value="Select ingredientsd to find perfect recipe.",
                        width=550,
                        height=40
                    )

                    # text area for missing ingredients
                    dpg.add_input_text(
                        multiline=True,
                        readonly=True,
                        tag="missing_ingredients",
                        default_value="",
                        width=550,
                        height=120
                    )

                    with dpg.group(horizontal=True, show=False, tag="confirm_group"):
                        dpg.add_button(label="Cook This Recipe!", callback=self.confirm_recipe, tag="yes_button")
                        dpg.bind_item_theme("yes_button", self.success_button_theme)
                        dpg.add_button(label="Try Different Recipe", callback=self.reject_recipe, tag="no_button")
                        dpg.bind_item_theme("no_button", self.danger_button_theme)

                    dpg.add_spacer(height=15)
                    dpg.add_text("Cooking Instructions", tag="steps_header")
                    dpg.bind_item_theme("steps_header", self.section_header_theme)

                    # plain text for steps (instead of text area)
                    dpg.add_text("Steps will appear here.", tag="steps_text", wrap=550)



    # ---------------- Helpers ----------------
    def _format_missing(self, missing):
        if not missing:
            return "You have everything you need!"
        fixed, buffer = [], []
        for m in missing:
            if m.isdigit():
                if buffer:
                    fixed.append(" ".join(buffer))
                    buffer = []
                buffer.append(m)
            else:
                buffer.append(m)
        if buffer:
            fixed.append(" ".join(buffer))
        return "Missing:\n" + "\n".join([f"- {m}" for m in fixed])

    def _calculate_confidence(self, dish, selected):
        ing_list = self.recommender.ingredients_map.get(dish, [])
        matched = len(set(selected) & set(ing_list))
        total = len(ing_list) if ing_list else 1
        return int(round(matched / total * 100))

    # ---------------- Logic ----------------
    def start_main_app(self):
        dpg.hide_item("Intro")
        dpg.show_item("Main")
        dpg.set_primary_window("Main", True)

    def go_home(self):
        dpg.hide_item("Main")
        dpg.show_item("Intro")
        dpg.set_primary_window("Intro", True)

    def on_ingredient_toggle(self, sender, app_data, user_data):
        if app_data:
            self.selected_ingredients.add(user_data)
        else:
            self.selected_ingredients.discard(user_data)
        self.update_selected_display()

    def update_selected_display(self):
        if self.selected_ingredients:
            dpg.set_value("selected_display", ", ".join(sorted(self.selected_ingredients)))
        else:
            dpg.set_value("selected_display", "None selected")

    def clear_all(self):
        for category, ingredients in self.ingredient_categories.items():
            for ing in ingredients:
                if dpg.does_item_exist(f"check_{ing}"):
                    dpg.set_value(f"check_{ing}", False)
        self.selected_ingredients.clear()
        self.update_selected_display()
        dpg.set_value("dish_suggestion", "Select ingredients to find perfect recipe.")
        dpg.set_value("steps_text", "Steps will appear here.")
        dpg.set_value("missing_ingredients", "")
        dpg.hide_item("confirm_group")

    def find_recipes(self):
        if not self.selected_ingredients:
            dpg.set_value("dish_suggestion", "Please select at least one ingredient!")
            return

        dish, missing, _ = self.recommender.find_missing_ingredients(
            " ".join(simple_tokenize(" ".join(self.selected_ingredients)))
        )
        if dish:
            confidence = self._calculate_confidence(dish, self.selected_ingredients)
            self.current_dish = dish
            self.current_confidence = confidence
            self.current_missing = missing
            dpg.set_value("dish_suggestion", f"Dish: {dish}\nConfidence: {confidence}%")
            dpg.set_value("missing_ingredients", self._format_missing(missing))
            dpg.show_item("confirm_group")
        else:
            dpg.set_value("dish_suggestion", "No perfect matches found.\nTry 'Show Alternatives'.")
            dpg.set_value("missing_ingredients", "")
            dpg.hide_item("confirm_group")

    def confirm_recipe(self):
        if not self.current_dish:
            return
        steps = self.recommender.get_recipe_steps(self.current_dish, max_steps=10)
        if steps:
            cleaned = []
            for s in steps:
                s = str(s).strip()
                if s.isdigit() or s == "":
                    continue
                cleaned.append(f"Step {len(cleaned)+1}: {s}")
            dpg.set_value("steps_text", "\n\n".join(cleaned) if cleaned else "No valid steps available.")
        else:
            dpg.set_value("steps_text", "No steps available for this dish.")

    def reject_recipe(self):
        dpg.set_value("dish_suggestion", "Let's try something else.\nClick 'Show Alternatives' or pick other ingredients.")
        dpg.set_value("missing_ingredients", "")
        dpg.set_value("steps_text", "Steps will appear here.")
        dpg.hide_item("confirm_group")

    def show_alternatives(self):
        if not self.selected_ingredients:
            dpg.set_value("dish_suggestion", "Please select at least one ingredient!")
            return
        alternatives = self.recommender.get_alternative_dishes(
            " ".join(simple_tokenize(" ".join(self.selected_ingredients))), top_k=5
        )
        if not alternatives:
            dpg.set_value("dish_suggestion", "No alternative dishes found.")
            return
        if dpg.does_item_exist("alt_window"):
            dpg.delete_item("alt_window")

        with dpg.window(label="Alternative Recipes", modal=True, width=600, height=400,
                        tag="alt_window", pos=[200, 150]):
            for dish, _ in alternatives:
                confidence = self._calculate_confidence(dish, self.selected_ingredients)
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Select", callback=self.select_alternative,
                                   user_data=dish, width=80)
                    dpg.add_text(f"{dish} ({confidence}% match)")
            dpg.add_spacer(height=10)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("alt_window"))

    def select_alternative(self, sender, app_data, user_data):
        dish = user_data
        self.current_dish = dish
        ing_list = self.recommender.ingredients_map.get(dish, [])
        missing = [i for i in ing_list if i not in self.selected_ingredients]
        confidence = self._calculate_confidence(dish, self.selected_ingredients)

        self.current_confidence = confidence
        self.current_missing = missing
        dpg.set_value("dish_suggestion", f"Dish: {dish}\nConfidence: {confidence}%")
        dpg.set_value("missing_ingredients", self._format_missing(missing))
        dpg.show_item("confirm_group")
        dpg.delete_item("alt_window")

    def run(self):
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
