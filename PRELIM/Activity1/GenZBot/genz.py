import random
import re
import random
from .responses import load_responses, load_positive_responses, load_negative_responses


class GenZChatbot: 
    def tokenize_input(self, user_input):
        #Tokenization
        return re.findall(r"\b\w+\b", user_input.lower())

    def extract_keywords_from_pattern(self, pattern):
        return set(re.findall(r"\w+", pattern.lower()))
        
    def __init__(self, name="ZenBot"):
        self.name = name
        self.responses = load_responses()
        self.positive_responses = load_positive_responses()
        self.negative_responses = load_negative_responses()
    
    def analyze_sentiment(self, user_input):
        #Analyze sentiment of user input and return sentiment type
        user_input = user_input.lower()
        tokens = self.tokenize_input(user_input)
        #Positive patterns 1st
        positive_patterns = self.positive_responses.get('sentiment', {}).get('positive', {}).get('patterns', [])
        for pattern in positive_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return 'positive'

        #Negative patterns 2nd
        negative_patterns = self.negative_responses.get('sentiment', {}).get('negative', {}).get('patterns', [])
        for pattern in negative_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return 'negative'
        
        # Check neutral patterns (now in positive responses)
        neutral_patterns = self.positive_responses.get('neutral', {}).get('patterns', [])
        for pattern in neutral_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return 'neutral'

        return 'neutral'
    
    def get_sentiment_response(self, sentiment_type):
        #Get a response based on sentiment type
        if sentiment_type == 'positive':
            sentiment_responses = self.positive_responses.get('sentiment', {}).get('positive', {}).get('responses', [])
        elif sentiment_type == 'negative':
            sentiment_responses = self.negative_responses.get('sentiment', {}).get('negative', {}).get('responses', [])
        elif sentiment_type == 'neutral':
            sentiment_responses = self.positive_responses.get('neutral', {}).get('responses', [])
        else:
            return None
        
        if sentiment_responses:
            return random.choice(sentiment_responses)
        return None
    
    def find_best_category_match(self, tokens, responses_dict):
        best_match = None
        max_score = 0
        for category, data in responses_dict.items():
            if category in ['sentiment']:
                continue
            if 'patterns' in data:
                score = 0
                for pattern in data['patterns']:#Category List
                    #print(f"Category: {category}")
                    if re.search(pattern, ' '.join(tokens), re.IGNORECASE): #Regex Pattern
                        #print(f"  [Regex] Category '{category} = {pattern}'(+10)")
                        score += 10
                    pattern_keywords = self.extract_keywords_from_pattern(pattern)
                    for token in tokens:
                        if token in pattern_keywords: #Token Pattern
                            #print(f"    [Token] Token '{token} = {pattern}'(+2)")
                            score += 2
                if score > max_score:
                    max_score = score
                    best_match = (category, data)
        if best_match and max_score > 0: #Chosen Category Match (In testing)
            #print(f"\n[Chosen Category]: {best_match[0]} (Score: {max_score})\n")
            #print(f"-------------------------------------------------------------")
            return (best_match[0], best_match[1], max_score)
        return None

    def find_response(self, user_input):
        #Analyze sentiment
        user_input = user_input.lower()
        tokens = self.tokenize_input(user_input)
        
        sentiment = self.analyze_sentiment(user_input)
        sentiment_response = self.get_sentiment_response(sentiment)

        # Always prioritize best category match from the main sentiment responses
        if sentiment == 'positive' or sentiment == 'neutral':
            search_responses = self.positive_responses
        else:
            search_responses = self.negative_responses

        best_match = self.find_best_category_match(tokens, search_responses)
        if best_match:
            category, data, score = best_match
            return category, score, random.choice(data['responses'])

        # If no category match, fallback to sentiment response (for positive/negative/neutral)
        if sentiment in ['positive', 'negative'] and sentiment_response:
            return None, None, sentiment_response

        # If still nothing, try fallback to the other sentiment's categories
        other_responses = self.negative_responses if sentiment == 'positive' else self.positive_responses
        best_match = self.find_best_category_match(tokens, other_responses)
        if best_match:
            category, data, score = best_match
            return category, score, random.choice(data['responses'])

        # If still nothing, fallback to neutral sentiment response
        if sentiment == 'neutral' and sentiment_response:
            return None, None, sentiment_response

        # Default fallback
        default_responses = self.negative_responses.get('default', {}).get('responses', [])
        if default_responses:
            return None, None, random.choice(default_responses)

        return None, None, "I'm not sure what you mean, but you're giving mysterious vibes!"
    
    def get_welcome_message(self):
        welcome = f"\n🤖 {self.name}: Yooo! I'm {self.name}, your Pinoy Gen Z Tropa! ✨\n"
        welcome += "I speak fluent Gen Z slang AND Taglish! Tara na, let's chat! 🇵🇭\n"
        welcome += "Type 'quit' or 'exit' to leave. Ready na ba? No cap! 💯\n"
        return welcome
    
    def get_goodbye_message(self):
        return f"\n🤖 {self.name}: Bye bro! Salamat sa chat! Stay iconic! ✨👑🇵🇭"
    
    def get_empty_input_message(self):
        return f"\n🤖 {self.name}: pre, may sasabihin ka ba? I'm here to chat! 💬"
    
    def get_interrupt_message(self):
       # Get the message for keyboard interrupt
        
        return f"\n\n🤖 {self.name}: Caught you trying to escape! Bye tol! Ingat ka! 👋✨"
    
    def get_error_message(self, error):
       # Get the error message with encouragement
        message = f"\n🤖 {self.name}: Oops! May mali: {error}\n"
        message += "But I'm still here for you Tropa! Laban lang! 💪"
        return message
    
    def is_quit_command(self, user_input):
       # Check if user input is a quit command
        quit_commands = ['quit', 'exit', 'bye bye', 'paalam', 'sige na']
        return user_input.lower().strip() in quit_commands
    
    def format_response(self, response):
       # Format the chatbot's response with proper styling
        return f"\n🤖 {self.name}: {response}\n"
    
    def chat(self):
        # Main chat loop - handles user interaction
        print(self.get_welcome_message())
        
        while True:
            user_input = input("You: ").strip()
            
            # Check for quit commands
            if self.is_quit_command(user_input):
                print(self.get_goodbye_message())
                break
            
            # Handle empty input
            if not user_input:
                print(self.get_empty_input_message())
                continue
#---------------------------------------------------------------------------  #Debugging Response Category
            # Generate and display response
            category, score, response = self.find_response(user_input)
            #if category and score is not None:
                #print(f"[Chosen Category]: {category} (Score: {score})")
            print(self.format_response(response))
#---------------------------------------------------------------------------
if __name__ == "__main__":
    bot = GenZChatbot()
    test_inputs = [
        "Sheesh, that's so fire!", #Slay
        "I'm so sad and tired.",
        "Uy, ang ganda mo today!",
        "No cap, you are awesome!",
        "Mid lang yung movie, bro.",
        "Bet! Tara na.",
        "I'm just okay.",
        "That was sus, not gonna lie."
    ]
    for user_input in test_inputs:
        print(f"\nUser input: {user_input}")
        tokens = bot.tokenize_input(user_input)
        print(f"Tokens: {tokens}")
        bot.find_best_category_match(tokens, bot.positive_responses)
        bot.find_best_category_match(tokens, bot.negative_responses)