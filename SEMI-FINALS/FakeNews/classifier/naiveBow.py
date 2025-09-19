import pandas as pd
import math, re, random
from collections import defaultdict

# === Load Dataset ===
dataset = pd.read_csv("news_dataset.csv")
news_data = list(zip(dataset["Text"], dataset["Label"].str.lower()))

# === Balance Data ===
# Separate data by class
real_news = [item for item in news_data if item[1] == 'real']
fake_news = [item for item in news_data if item[1] == 'fake']

# Find the minimum count between the two classes
min_count = min(len(real_news), len(fake_news))

# Calculate train size per class (80% of min_count)
train_size_per_class = int(min_count * 0.8)
test_size_per_class = min_count - train_size_per_class

# Sample training data
balanced_train = []
balanced_train.extend(random.sample(real_news, train_size_per_class))
balanced_train.extend(random.sample(fake_news, train_size_per_class))

# Sample test data from remaining
remaining_real = [item for item in real_news if item not in balanced_train]
remaining_fake = [item for item in fake_news if item not in balanced_train]
balanced_test = []
balanced_test.extend(random.sample(remaining_real, min(test_size_per_class, len(remaining_real))))
balanced_test.extend(random.sample(remaining_fake, min(test_size_per_class, len(remaining_fake))))

# Shuffle the data
random.shuffle(balanced_train)
random.shuffle(balanced_test)

train_data = balanced_train
test_data = balanced_test

# Print class distribution
train_real = sum(1 for _, label in train_data if label == 'real')
train_fake = sum(1 for _, label in train_data if label == 'fake')
print(f"Training data - Real: {train_real}, Fake: {train_fake}")

test_real = sum(1 for _, label in test_data if label == 'real')
test_fake = sum(1 for _, label in test_data if label == 'fake')
print(f"Test data - Real: {test_real}, Fake: {test_fake}")

# === Stopwords ===
stopwords = set([
    # Pronouns
    "i","me","my","myself","we","us","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers","herself",
    "it","its","itself","they","them","their","theirs","themselves",

    # Auxiliary verbs
    "am","is","are","was","were","be","been","being","have","has","had","having",
    "do","does","did","doing","will","would","shall","should","may","might","must",
    "can","could","ought",

    # Determiners
    "a","an","the","this","that","these","those","any","each","every","no","some",
    "many","much","several","all","both","few","half","either","neither","other",
    "another","such",

    # Prepositions
    "about","above","across","after","against","along","among","around","at","before",
    "behind","below","beneath","beside","between","beyond","by","despite","down",
    "during","except","for","from","in","inside","into","like","near","of","off",
    "on","onto","out","outside","over","past","since","through","throughout","to",
    "toward","under","underneath","until","up","upon","with","within","without",

    # Conjunctions
    "and","but","or","nor","for","yet","so","although","because","since","unless",
    "while","whereas","if","then","than","once","whether",

    # Adverbs
    "very","just","too","also","here","there","when","where","why","how","again",
    "already","always","never","sometimes","soon","often","once","today","tomorrow",
    "yesterday","now","then","still","yet","perhaps","maybe","about","almost","quite",
    "really","rather","somewhat","enough","even","exactly","indeed","simply",

    # Negations
    "not","no","nor","none","neither","never",

    # Interjections / filler
    "oh","ah","hmm","well","hey","hello","hi","huh","mm","aha","oops","ugh","wow","yay",

    # Miscellaneous common words
    "as","at","by","for","from","in","of","on","to","with","within","without","such",
    "each","other","any","both","either","enough","much","many","few","all"
])

# === Text Preprocessing ===
def normalize_text(text):
    text = text.lower()
    text = re.sub(r"\W", " ", text)
    return text.strip()

def tokenize_text(text):
    text = normalize_text(text)
    words = re.split(r"\s+", text)
    return [w for w in words if w and w not in stopwords]

# === Naïve Bayes=== 
def train_naive_bayes_model_with_logs(data):
    vocabulary = set()
    class_counts = defaultdict(int)            
    word_counts_per_class = defaultdict(lambda: defaultdict(int))

    print("\n=== Starting Training ===")
    print(f"Number of documents to process: {len(data)}")

    for text, label in data:
        tokens = tokenize_text(text)
        vocabulary.update(tokens)
        class_counts[label] += 1
        for token in tokens:
            word_counts_per_class[label][token] += 1

    # Verify the counts match the input data
    print("\n=== Training Data Summary ===")
    print(f"Total documents processed: {sum(class_counts.values())}")
    print("Documents per class:", dict(class_counts))
    print(f"Vocabulary size: {len(vocabulary)}")
    
    return class_counts, word_counts_per_class, len(vocabulary)

# === Prediction ===
def predict_news_with_logs(text, class_counts, word_counts_per_class, vocab_size, prior_boosts=None):
    tokens = tokenize_text(text)
    total_documents = sum(class_counts.values())
    class_scores = {}
    word_logs = {}

    #print("\n=== Predicting News ===")
    #print("Tokens:", tokens)

    if prior_boosts and isinstance(prior_boosts, dict):
        try:
            print(f"[Boost] Applying source-based boosts: {prior_boosts}")
        except Exception:
            pass

    # First pass: calculate raw scores without boosts
    raw_scores = {}
    for label in class_counts:
        score = math.log(class_counts[label] / total_documents)
        total_words_in_class = sum(word_counts_per_class[label].values())
        
        for token in tokens:
            token_count = word_counts_per_class[label].get(token, 0)
            token_prob = (token_count + 1) / (total_words_in_class + vocab_size)
            score += math.log(token_prob)
        
        raw_scores[label] = score
    
    # Print raw scores before boosting
    if prior_boosts and isinstance(prior_boosts, dict):
        try:
            print(f"[Boost] Raw scores (before boosts): { {k: round(v, 4) for k, v in raw_scores.items()} }")
        except Exception:
            pass

    # Second pass: apply boosts and track the difference
    for label in class_counts:
        base_prior = math.log(class_counts[label] / total_documents)
        boost_val = float(prior_boosts.get(label, 0.0)) if prior_boosts and isinstance(prior_boosts, dict) else 0.0
        
        # Raw Score (pre-calculated)
        score = raw_scores[label]
        
        # Only adjust by the boost difference
        if boost_val != 0.0:
            try:
                print(f"[Boost] Prior '{label}': base_prior={base_prior:.4f}, boost={boost_val:.4f}, boosted_prior={base_prior + boost_val:.4f}")
            except Exception:
                pass
            # Adjust score by the boost amount
            score += boost_val
        
        class_scores[label] = score
        word_logs[label] = {token: math.log((word_counts_per_class[label].get(token, 0) + 1) / 
                                         (sum(word_counts_per_class[label].values()) + vocab_size)) 
                          for token in tokens}

    predicted_class = max(class_scores, key=class_scores.get)
    if prior_boosts and isinstance(prior_boosts, dict):
        try:
            print(f"[Boost] Final class scores (with boosts): { {k: round(v, 4) for k, v in class_scores.items()} } -> predicted: {predicted_class}")
        except Exception:
            pass
    
    return predicted_class, class_scores, word_logs

def main():
    # Train the model
    class_counts, word_counts_per_class, vocab_size = train_naive_bayes_model_with_logs(train_data)
    
    # === Manual Input ===
    # while True:
    #     user_text = input("\nEnter news text (or type 'exit' to quit): ")
    #     if user_text.lower() == "exit":
    #         break
    #     predict_news_with_logs(user_text, class_counts, word_counts_per_class, vocab_size)
    
    # Return the trained model variables
    return class_counts, word_counts_per_class, vocab_size

# Only run the training if this script is executed directly
if __name__ == "__main__":
    class_counts, word_counts_per_class, vocab_size = main()
else:
    # When imported, these will be set by the first import of this module
    class_counts = None
    word_counts_per_class = None
    vocab_size = None