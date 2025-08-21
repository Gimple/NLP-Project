import dearpygui.dearpygui as dpg
from core.recommender import CookingRecommender
from core.corpora_builder import simple_tokenize
import os


class CookingUI:
    def __init__(self, recommender: CookingRecommender):
        self.recommender = recommender
        self.selected_ingredients = set()
        self.current_dish = None
        self.current_confidence = 0
        self.current_missing = []
        self.show_intro = True
        
        # Enhanced ingredient categories with emojis
        self.ingredient_categories = {
            " Meat & Protein": [
                "chicken", "beef", "pork", "fish", "shrimp", "egg", "tofu", 
                "salmon", "tuna", "bacon", "sausage", "duck", "lamb"
            ],
            " Vegetables": [
                "onion", "garlic", "tomato", "carrot", "potato", "bell pepper",
                "cabbage", "lettuce", "spinach", "broccoli", "corn", "peas",
                "mushroom", "eggplant", "cucumber", "celery"
            ],
            " Condiments & Seasonings": [
                "salt", "pepper", "soy sauce", "vinegar", "sugar", "oil",
                "ginger", "chili", "bay leaves", "basil", "oregano", "paprika",
                "cumin", "turmeric", "cinnamon", "sesame oil"
            ],
            " Rice & Grains": [
                "rice", "noodles", "pasta", "bread", "flour", "quinoa",
                "oats", "barley", "wheat", "corn meal"
            ],
            " Dairy & Others": [
                "milk", "cheese", "butter", "cream", "yogurt", "coconut milk",
                "coconut", "nuts", "beans", "lentils"
            ]
        }
        
        self.cuisine_types = [" Filipino", " Chinese", " Italian", " American", 
                             " Japanese", " Mexican", " Thai", " Indian"]
        self.selected_cuisine = " Filipino"
        
        self.setup_gui()

    def setup_gui(self):
        dpg.create_context()
        
        # Setup themes first
        self.setup_themes()
        
        if self.show_intro:
            self.create_intro_window()
        
        self.create_main_window()
        
        dpg.create_viewport(title="Meal&Match - Cooking Recommender", width=1200, height=800)
        
        # Set intro as primary if showing, otherwise main
        if self.show_intro:
            dpg.set_primary_window("Intro", True)
        else:
            dpg.set_primary_window("Main", True)

    def create_intro_window(self):
        with dpg.window(label="Welcome to Meal&Match", tag="Intro", width=800, height=600):
            
            # Header section with gradient-like effect
            with dpg.group():
                dpg.add_spacer(height=30)
                
                # Main title - using multiple lines and spacing for visual impact
                dpg.add_text("------", tag="intro_icons")
                dpg.bind_item_theme("intro_icons", self.title_theme)
                dpg.add_text("M E A L  &  M A T C H", tag="intro_title")
                dpg.bind_item_theme("intro_title", self.title_theme)
                dpg.add_text("------", tag="intro_icons2")
                dpg.bind_item_theme("intro_icons2", self.title_theme)
                
                dpg.add_text("Cooking Recommender", tag="intro_subtitle")
                dpg.bind_item_theme("intro_subtitle", self.subtitle_theme)
                
                dpg.add_spacer(height=20)
                
                # Decorative line
                dpg.add_separator()
                
                dpg.add_spacer(height=30)
                
                # Features section with attractive layout
                dpg.add_text("What can Meal&Match do for you?", tag="features_title")
                dpg.bind_item_theme("features_title", self.header_theme)
                
                dpg.add_spacer(height=15)
                
                # Feature cards simulation
                with dpg.group():
                    dpg.add_text("Recipe Matching", tag="feature1")
                    dpg.add_text("Find perfect recipes based on your available ingredients", tag="feature1_desc")
                    dpg.bind_item_theme("feature1", self.feature_theme)
                    dpg.bind_item_theme("feature1_desc", self.description_theme)
                    
                    dpg.add_spacer(height=10)
                    
                    dpg.add_text("Missing Ingredient Detection", tag="feature2")
                    dpg.add_text("Discover what you need to complete any recipe", tag="feature2_desc")
                    dpg.bind_item_theme("feature2", self.feature_theme)
                    dpg.bind_item_theme("feature2_desc", self.description_theme)
                    
                    dpg.add_spacer(height=10)
                    
                    dpg.add_text("Step-by-Step Cooking Guide", tag="feature3")
                    dpg.add_text("Get detailed instructions for every recipe", tag="feature3_desc")
                    dpg.bind_item_theme("feature3", self.feature_theme)
                    dpg.bind_item_theme("feature3_desc", self.description_theme)
                    
                    dpg.add_spacer(height=10)
                    
                    dpg.add_text("Multiple Cuisine Types", tag="feature4")
                    dpg.add_text("Explore recipes from around the world", tag="feature4_desc")
                    dpg.bind_item_theme("feature4", self.feature_theme)
                    dpg.bind_item_theme("feature4_desc", self.description_theme)
                
                dpg.add_spacer(height=40)
                
                # Call to action
                dpg.add_text("Ready to start cooking? Let's find your perfect meal!", tag="cta_text")
                dpg.bind_item_theme("cta_text", self.cta_theme)
                
                dpg.add_spacer(height=20)
                
                # Action buttons
                with dpg.group(horizontal=True):
                    dpg.add_spacer(width=200)  # Center the buttons
                    dpg.add_button(
                        label="Start Cooking!",
                        callback=self.start_main_app,
                        tag="start_button",
                        width=200,
                        height=50
                    )
                    dpg.add_spacer(width=50)
                    dpg.add_button(
                        label="ℹ Learn More",
                        callback=self.show_help,
                        tag="help_button",
                        width=150,
                        height=50
                    )
                
                dpg.add_spacer(height=30)
                
                # Footer
                dpg.add_separator()
                dpg.add_spacer(height=10)
                dpg.add_text("© 2024 Meal&Match - Making cooking easier, one ingredient at a time", tag="footer_text")
                dpg.bind_item_theme("footer_text", self.footer_theme)

    def create_main_window(self):
        with dpg.window(label="Meal&Match - Cooking Recommender", tag="Main", width=1200, height=800, show=False):
            
            # Header section
            with dpg.group():
                with dpg.group(horizontal=True):
                    dpg.add_text("M E A L & M A T C H", tag="main_title")
                    dpg.bind_item_theme("main_title", self.main_title_theme)
                    
                    dpg.add_spacer(width=600)
                    
                    # Back to intro button
                    dpg.add_button(
                        label="Home",
                        callback=self.back_to_intro,
                        tag="home_button",
                        width=100,
                        height=30
                    )
                
                dpg.add_separator()
                dpg.add_spacer(height=15)
            
            # Main content in columns
            with dpg.group(horizontal=True):
                
                # Left column - Ingredient Selection
                with dpg.child_window(width=500, height=650, tag="left_panel"):
                    dpg.add_text("Select Your Ingredients", tag="ingredient_header")
                    dpg.bind_item_theme("ingredient_header", self.section_header_theme)
                    dpg.add_spacer(height=10)
                    
                    # Cuisine Selection
                    with dpg.group(horizontal=True):
                        dpg.add_text("Cuisine Type:")
                        dpg.add_combo(
                            items=self.cuisine_types,
                            default_value=self.selected_cuisine,
                            callback=self.on_cuisine_change,
                            tag="cuisine_combo",
                            width=200
                        )
                    
                    dpg.add_spacer(height=15)
                    
                    # Quick selection buttons
                    with dpg.group(horizontal=True):
                        dpg.add_button(label="Clear All", callback=self.clear_all, width=80)
                        dpg.add_button(label="Popular", callback=self.select_popular, width=80)
                        dpg.add_button(label="Healthy", callback=self.select_healthy, width=80)
                    
                    dpg.add_spacer(height=10)
                    
                    # Ingredient categories in scrollable area
                    with dpg.child_window(height=450):
                        for category, ingredients in self.ingredient_categories.items():
                            with dpg.collapsing_header(label=category, default_open=True):
                                with dpg.group():
                                    # Create a grid layout for ingredients
                                    for i in range(0, len(ingredients), 3):
                                        with dpg.group(horizontal=True):
                                            for j in range(3):
                                                if i + j < len(ingredients):
                                                    ingredient = ingredients[i + j]
                                                    dpg.add_checkbox(
                                                        label=ingredient.title(),
                                                        callback=self.on_ingredient_toggle,
                                                        user_data=ingredient,
                                                        tag=f"check_{ingredient}"
                                                    )
                    
                    dpg.add_spacer(height=10)
                    
                    # Selected ingredients display
                    dpg.add_text("Selected Ingredients:", tag="selected_label")
                    dpg.bind_item_theme("selected_label", self.label_theme)
                    
                    with dpg.child_window(height=80, border=True):
                        dpg.add_text("None selected", tag="selected_display", wrap=480)
                
                dpg.add_spacer(width=20)
                
                # Right column - Results and Actions
                with dpg.child_window(width=650, height=650, tag="right_panel"):
                    dpg.add_text("Recipe Recommendations", tag="recipe_header")
                    dpg.bind_item_theme("recipe_header", self.section_header_theme)
                    dpg.add_spacer(height=15)
                    
                    # Action buttons
                    with dpg.group(horizontal=True):
                        dpg.add_button(
                            label="Find Perfect Recipe",
                            callback=self.find_recipes,
                            tag="find_button",
                            width=180,
                            height=40
                        )
                        dpg.add_button(
                            label="Show Alternatives",
                            callback=self.show_alternatives,
                            tag="alt_button",
                            width=160,
                            height=40
                        )
                    
                    dpg.add_spacer(height=20)
                    
                    # Results area
                    with dpg.child_window(height=200, border=True, tag="results_area"):
                        dpg.add_text("Select ingredients and click 'Find Perfect Recipe' to discover amazing dishes!", 
                                   tag="dish_suggestion", wrap=620)
                        dpg.add_text("", tag="missing_ingredients", wrap=620)
                    
                    dpg.add_spacer(height=15)
                    
                    # Confirmation buttons (initially hidden)
                    with dpg.group(horizontal=True, show=False, tag="confirm_group"):
                        dpg.add_button(
                            label="Cook This Recipe!",
                            callback=self.confirm_recipe,
                            tag="yes_button",
                            width=170,
                            height=35
                        )
                        dpg.add_button(
                            label="Try Different Recipe",
                            callback=self.reject_recipe,
                            tag="no_button",
                            width=170,
                            height=35
                        )
                    
                    dpg.add_spacer(height=20)
                    
                    # Recipe steps section
                    dpg.add_text("Cooking Instructions", tag="steps_header")
                    dpg.bind_item_theme("steps_header", self.section_header_theme)
                    dpg.add_spacer(height=10)
                    
                    with dpg.child_window(height=280, border=True, tag="steps_window"):
                        dpg.add_text("Recipe steps will appear here after you select a dish to cook.\n\n"
                                   "Tip: The more ingredients you select, the better matches you'll get!",
                                   tag="steps_text", wrap=600)

    def setup_themes(self):
        # Intro window themes
        with dpg.theme() as self.title_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [100, 200, 255, 255])
        
        with dpg.theme() as self.subtitle_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [150, 150, 150, 255])
        
        with dpg.theme() as self.header_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 200, 100, 255])
        
        with dpg.theme() as self.feature_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [100, 255, 150, 255])
        
        with dpg.theme() as self.description_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [180, 180, 180, 255])
        
        with dpg.theme() as self.cta_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 255, 100, 255])
        
        with dpg.theme() as self.footer_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [120, 120, 120, 255])
        
        # Main window themes
        with dpg.theme() as self.main_title_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [100, 200, 255, 255])
        
        with dpg.theme() as self.section_header_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [255, 200, 100, 255])
        
        with dpg.theme() as self.label_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Text, [200, 200, 200, 255])
        
        # Button themes
        with dpg.theme() as self.primary_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 150, 250, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [70, 170, 255, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [30, 130, 230, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
        
        with dpg.theme() as self.secondary_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [150, 100, 250, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [170, 120, 255, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [130, 80, 230, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
        
        with dpg.theme() as self.success_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [50, 200, 100, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [70, 220, 120, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [30, 180, 80, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
        
        with dpg.theme() as self.danger_button_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, [200, 80, 80, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, [220, 100, 100, 255])
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, [180, 60, 60, 255])
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
        
        # Apply themes to buttons
        self.apply_button_themes()
    
    def apply_button_themes(self):
        # This will be called after UI elements are created
        pass
    
    def finalize_themes(self):
        # Apply themes to specific buttons after they're created
        if dpg.does_item_exist("start_button"):
            dpg.bind_item_theme("start_button", self.primary_button_theme)
        if dpg.does_item_exist("help_button"):
            dpg.bind_item_theme("help_button", self.secondary_button_theme)
        if dpg.does_item_exist("find_button"):
            dpg.bind_item_theme("find_button", self.primary_button_theme)
        if dpg.does_item_exist("alt_button"):
            dpg.bind_item_theme("alt_button", self.secondary_button_theme)
        if dpg.does_item_exist("yes_button"):
            dpg.bind_item_theme("yes_button", self.success_button_theme)
        if dpg.does_item_exist("no_button"):
            dpg.bind_item_theme("no_button", self.danger_button_theme)

    def start_main_app(self):
        dpg.hide_item("Intro")
        dpg.show_item("Main")
        dpg.set_primary_window("Main", True)

    def back_to_intro(self):
        dpg.hide_item("Main")
        dpg.show_item("Intro")
        dpg.set_primary_window("Intro", True)

    def show_help(self):
        with dpg.window(label="Help & Tips", modal=True, show=True, tag="help_window", 
                       width=600, height=500, pos=[300, 150]):
            
            dpg.add_text("Meal&Match - How to Use", tag="help_title")
            dpg.bind_item_theme("help_title", self.header_theme)
            dpg.add_separator()
            dpg.add_spacer(height=15)
            
            help_text = """
🎯 Getting Started:
1. Select your cuisine type from the dropdown
2. Check the ingredients you have available
3. Click 'Find Perfect Recipe' to get suggestions

💡 Pro Tips:
• Select more ingredients for better matches
• Use 'Show Alternatives' to see other recipe options
• The confidence percentage shows how well your ingredients match
• Missing ingredients are highlighted to help you shop

🌟 Features:
• Smart matching algorithm finds the best recipes
• Step-by-step cooking instructions
• Multiple cuisine types supported
• Quick ingredient selection shortcuts

🔧 Quick Actions:
• 'Popular' - Selects commonly used ingredients
• 'Healthy' - Focuses on nutritious options
• 'Clear All' - Resets all selections

Need more help? The app is intuitive - just start selecting ingredients and explore!
            """
            
            dpg.add_text(help_text, wrap=550)
            
            dpg.add_spacer(height=20)
            dpg.add_separator()
            dpg.add_button(label="Got it! Let's cook!", callback=lambda: dpg.delete_item("help_window"), width=200)

    def select_popular(self):
        popular_ingredients = ["chicken", "onion", "garlic", "tomato", "rice", "egg", "salt", "pepper", "oil"]
        for ingredient in popular_ingredients:
            if dpg.does_item_exist(f"check_{ingredient}"):
                dpg.set_value(f"check_{ingredient}", True)
                self.selected_ingredients.add(ingredient)
        self.update_selected_display()

    def select_healthy(self):
        healthy_ingredients = ["spinach", "broccoli", "salmon", "quinoa", "tofu", "tomato", "carrot", "cucumber"]
        for ingredient in healthy_ingredients:
            if dpg.does_item_exist(f"check_{ingredient}"):
                dpg.set_value(f"check_{ingredient}", True)
                self.selected_ingredients.add(ingredient)
        self.update_selected_display()

    def on_cuisine_change(self, sender, app_data):
        self.selected_cuisine = app_data

    def on_ingredient_toggle(self, sender, app_data, user_data):
        ingredient = user_data
        if app_data:
            self.selected_ingredients.add(ingredient)
        else:
            self.selected_ingredients.discard(ingredient)
        self.update_selected_display()

    def update_selected_display(self):
        if self.selected_ingredients:
            ingredients_text = ", ".join(sorted([ing.title() for ing in self.selected_ingredients]))
            if len(ingredients_text) > 100:
                ingredients_text = ingredients_text[:97] + "..."
            dpg.set_value("selected_display", f" {ingredients_text}")
        else:
            dpg.set_value("selected_display", "No ingredients selected yet")

    def find_recipes(self):
        if not self.selected_ingredients:
            self.show_modern_popup("Please select at least one ingredient! ", "info")
            return
        
        ingredients_text = " ".join(self.selected_ingredients)
        dish, missing, confidence = self.recommender.find_missing_ingredients(ingredients_text)
        
        if dish:
            self.current_dish = dish
            self.current_confidence = confidence
            self.current_missing = missing
            
            # Clear previous results
            dpg.delete_item("dish_suggestion")
            dpg.delete_item("missing_ingredients")
            
            # Add new results
            dpg.add_text(f"Perfect Match Found!\n\n Dish: {dish}\nConfidence: {confidence}%", 
                        parent="results_area", tag="dish_suggestion", wrap=620)
            dpg.bind_item_theme("dish_suggestion", self.success_button_theme)
            
            if missing:
                missing_display = self.pretty_missing_display(missing, dish=dish)
                dpg.add_text(missing_display, 
                           parent="results_area", tag="missing_ingredients", wrap=620, color=[255, 200, 150])
            else:
                dpg.add_text("\nGreat! You have everything you need!", 
                           parent="results_area", tag="missing_ingredients", wrap=620, color=[150, 255, 150])
            
            dpg.show_item("confirm_group")
        else:
            dpg.delete_item("dish_suggestion")
            dpg.delete_item("missing_ingredients")
            dpg.add_text("No perfect matches found.\n\nTry:\n• Adding more ingredients\n• Using 'Show Alternatives' for similar recipes", 
                        parent="results_area", tag="dish_suggestion", wrap=620, color=[255, 150, 150])
            dpg.add_text("", parent="results_area", tag="missing_ingredients")
            dpg.hide_item("confirm_group")

    def format_missing_ingredients(self, missing):
        if len(missing) == 1:
            return missing[0]
        elif len(missing) == 2:
            return f"{missing[0]} and {missing[1]}"
        else:
            return ", ".join(missing[:-1]) + f", and {missing[-1]}"

    def pretty_missing_display(self, missing, dish=None):
        """
        Return a user-friendly, multi-line bullet list for missing ingredients.
        Keeps original phrases where available, collapses extra spaces, strips
        trailing punctuation, and capitalizes the first letter for readability.
        """
        if not missing:
            return "Great! You have everything you need!"

        # If the missing list looks tokenized (many single-word tokens), try to
        # recover original ingredient phrases from the recommender's stored
        # original_ingredients_phrases for the dish.
        tokens_only = all(isinstance(x, str) and len(x.split()) == 1 for x in missing)
        reconstructed = []
        covered = set()
        missing_set = set([m.lower() for m in missing if isinstance(m, str)])

        if dish and tokens_only:
            phrases = self.recommender.original_ingredients_phrases.get(dish, [])
            for phrase in phrases:
                toks = set(simple_tokenize(phrase))
                # intersection in lowercase
                if toks and (toks & missing_set):
                    reconstructed.append(phrase)
                    covered |= toks

        # Add any remaining tokens that weren't covered by phrases
        remaining = [t for t in missing if isinstance(t, str) and t.lower() not in covered]

        lines = []
        for p in reconstructed:
            s = ' '.join(p.split()).strip(' .,:;')
            if s:
                lines.append(f"- {s[0].upper() + s[1:] if len(s)>1 else s}")

        for item in remaining:
            s = ' '.join(str(item).split()).strip(' .,:;')
            if not s:
                continue
            lines.append(f"- {s[0].upper() + s[1:] if len(s)>1 else s}")

        if not lines:
            return "Great! You have everything you need!"

        return "You'll need:\n" + "\n".join(lines)

    def confirm_recipe(self):
        if not self.current_dish:
            return
        
        steps = self.recommender.get_recipe_steps(self.current_dish, max_steps=10)
        
        dpg.delete_item("steps_text")
        
        if not steps:
            dpg.add_text("ecipe steps are not available for this dish.\n\nBut you can still cook it using the ingredients listed above!", 
                        parent="steps_window", tag="steps_text", wrap=580)
            return
        
        steps_content = f"Instructions for {self.current_dish}:\n\n"
        step_num = 1
        for step in steps:
            # sanitize step text by removing parentheses characters
            step_text = step.strip()
            if not step_text:
                continue
            # remove literal '(' and ')' characters but keep their contents
            step_text = step_text.replace('(', '').replace(')', '')
            if not step_text.isdigit() and len(step_text) > 2:
                steps_content += f"Step {step_num}: {step_text}\n\n"
                step_num += 1
        
        if step_num == 1:
            steps_content += "Basic cooking steps are not detailed, but follow standard preparation methods for your selected ingredients!"
        
        dpg.add_text(steps_content, parent="steps_window", tag="steps_text", wrap=580)

    def reject_recipe(self):
        dpg.delete_item("dish_suggestion")
        dpg.delete_item("missing_ingredients")
        dpg.add_text("Let's find something else!\n\nTry 'Show Alternatives' or select different ingredients.", 
                    parent="results_area", tag="dish_suggestion", wrap=620)
        dpg.add_text("", parent="results_area", tag="missing_ingredients")
        dpg.hide_item("confirm_group")
        
        dpg.delete_item("steps_text")
        dpg.add_text("Recipe steps will appear here after you select a dish to cook.\n\nTip: The more ingredients you select, the better matches you'll get!", 
                    parent="steps_window", tag="steps_text", wrap=580)

    def show_alternatives(self):
        if not self.selected_ingredients:
            self.show_modern_popup("Please select at least one ingredient first!", "info")
            return
        
        ingredients_text = " ".join(self.selected_ingredients)
        alternatives = self.recommender.get_alternative_dishes(ingredients_text, top_k=8)
        
        if not alternatives:
            self.show_modern_popup("No alternative dishes found. Try selecting more ingredients!", "warning")
            return
        
        with dpg.window(label="Alternative Recipes", modal=True, show=True, tag="alternatives_window", 
                       width=700, height=500, pos=[250, 150]):
            
            dpg.add_text("Alternative Recipe Suggestions", tag="alt_title")
            dpg.bind_item_theme("alt_title", self.header_theme)
            dpg.add_separator()
            dpg.add_spacer(height=10)
            
            with dpg.child_window(height=380):
                for i, (dish, match_pct) in enumerate(alternatives):
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Select",
                                callback=self.select_alternative,
                                user_data=dish,
                                width=80,
                                tag=f"alt_btn_{i}"
                            )
                            dpg.add_text(f" {dish}")
                            dpg.add_spacer(width=50)
                            dpg.add_text(f" {match_pct}% match", color=[100, 255, 150])
                        dpg.add_spacer(height=8)
                        dpg.add_separator()
                        dpg.add_spacer(height=8)
            
            dpg.add_separator()
            dpg.add_spacer(height=10)
            dpg.add_button(label="Close", callback=lambda: dpg.delete_item("alternatives_window"), width=100)

    def select_alternative(self, sender=None, app_data=None, user_data=None):
        # Extract dish from DearPyGui callback user_data if present
        dish = user_data if user_data is not None else sender

        # Guard: ignore invalid selections
        if not dish:
            self.show_modern_popup("Please select a valid recipe from the alternatives list.", "warning")
            return

        # normalize dish
        if isinstance(dish, str):
            dish = dish.strip()

        user_tokens = set(self.recommender.ingredient_model.vocab & set(self.selected_ingredients))
        ing_list = self.recommender.ingredients_map.get(dish, [])
        missing = [i for i in ing_list if i not in user_tokens]
        
        match_count = len(set(self.selected_ingredients) & set(ing_list))
        confidence = int(round(match_count / max(1, len(ing_list)) * 100))
        
        self.current_dish = dish
        self.current_confidence = confidence
        self.current_missing = missing
        
        # Clear previous results
        dpg.delete_item("dish_suggestion")
        dpg.delete_item("missing_ingredients")
        
        # Add new results using the same format as Find Perfect Recipe
        dpg.add_text(f"Perfect Match Found!\n\n Dish: {dish}\nConfidence: {confidence}%", 
                     parent="results_area", tag="dish_suggestion", wrap=620)
        dpg.bind_item_theme("dish_suggestion", self.success_button_theme)

        if missing:
            missing_display = self.pretty_missing_display(missing, dish=dish)
            dpg.add_text(missing_display, 
                         parent="results_area", tag="missing_ingredients", wrap=620, color=[255, 200, 150])
        else:
            dpg.add_text("\nGreat! You have everything you need!", 
                         parent="results_area", tag="missing_ingredients", wrap=620, color=[150, 255, 150])
        
        dpg.show_item("confirm_group")
        dpg.delete_item("alternatives_window")

    def clear_all(self):
        for category, ingredients in self.ingredient_categories.items():
            for ingredient in ingredients:
                if dpg.does_item_exist(f"check_{ingredient}"):
                    dpg.set_value(f"check_{ingredient}", False)
        
        self.selected_ingredients.clear()
        self.update_selected_display()
        
        # Clear displays
        if dpg.does_item_exist("dish_suggestion"):
            dpg.delete_item("dish_suggestion")
        if dpg.does_item_exist("missing_ingredients"):
            dpg.delete_item("missing_ingredients")
        
        dpg.add_text("Select ingredients and click 'Find Perfect Recipe' to discover amazing dishes!", 
                   parent="results_area", tag="dish_suggestion", wrap=620)
        dpg.add_text("", parent="results_area", tag="missing_ingredients")
        
        dpg.hide_item("confirm_group")
        
        # Clear steps
        dpg.delete_item("steps_text")
        dpg.add_text("Recipe steps will appear here after you select a dish to cook.\n\n Tip: The more ingredients you select, the better matches you'll get!", 
                    parent="steps_window", tag="steps_text", wrap=580)

    def show_modern_popup(self, message, popup_type="info"):
        icon = "ℹ️" if popup_type == "info" else "⚠️" if popup_type == "warning" else "❌"
        color = [100, 200, 255] if popup_type == "info" else [255, 200, 100] if popup_type == "warning" else [255, 100, 100]
        # Ensure any previous popup with the same tag is removed to avoid DearPyGui alias/container errors
        try:
            if dpg.does_item_exist("popup_window"):
                dpg.delete_item("popup_window")
        except Exception:
            # If deletion fails for any reason, continue and create a fresh popup with a unique tag
            pass

        # Use a unique tag to be extra-safe in case deletion didn't fully clear internal state
        popup_tag = f"popup_window_{int(__import__('time').time()*1000)}"
        with dpg.window(label=f"{icon} Information", modal=True, show=True, tag=popup_tag, 
                       width=400, height=200, pos=[400, 300]):

            dpg.add_spacer(height=20)
            dpg.add_text(f"{icon} {message}", wrap=350, color=color)
            dpg.add_spacer(height=30)
            dpg.add_separator()
            dpg.add_spacer(height=10)

            with dpg.group(horizontal=True):
                dpg.add_spacer(width=150)
                dpg.add_button(label="OK", callback=lambda: dpg.delete_item(popup_tag), width=100)

    def run(self):
        dpg.setup_dearpygui()
        
        # Apply button themes after setup
        self.finalize_themes()
        
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()