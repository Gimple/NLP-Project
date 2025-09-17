import pandas as pd
import math, re, random
from collections import defaultdict

# === Load Dataset ===
dataset = pd.read_csv("news_dataset.csv")
news_data = list(zip(dataset["Text"], dataset["Label"].str.lower()))

# Shuffle and Split
random.shuffle(news_data)
split_index = int(len(news_data) * 0.8)
train_data = news_data[:split_index]
test_data = news_data[split_index:]

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

    print("=== Training Naive Bayes with Bag of Words ===")

    for text, label in data:
        tokens = tokenize_text(text)
        vocabulary.update(tokens)
        class_counts[label] += 1
        for token in tokens:
            word_counts_per_class[label][token] += 1
        print(f"Processed document for class '{label}': tokens={tokens}")

    print("\nVocabulary:", vocabulary)
    print("\nWord counts per class:")
    for label in word_counts_per_class:
        print(f"Class '{label}': {dict(word_counts_per_class[label])}")
    print("\nTotal documents per class:", dict(class_counts))
    return class_counts, word_counts_per_class, len(vocabulary)

# === Prediction ===
def predict_news_with_logs(text, class_counts, word_counts_per_class, vocab_size):
    tokens = tokenize_text(text)
    total_documents = sum(class_counts.values())
    class_scores = {}
    word_logs = {}

    print("\n=== Predicting News ===")
    print("Tokens:", tokens)

    for label in class_counts:
        score = math.log(class_counts[label] / total_documents)
        print(f"\nClass '{label.upper()}' initial log prior: {score:.4f}")

        total_words_in_class = sum(word_counts_per_class[label].values())
        word_logs[label] = {}

        for token in tokens:
            token_count = word_counts_per_class[label].get(token, 0)
            token_prob = (token_count + 1) / (total_words_in_class + vocab_size)
            score += math.log(token_prob)
            word_logs[label][token] = math.log(token_prob)
            print(f"  Token '{token}': count={token_count}, log-prob={math.log(token_prob):.4f}")

        class_scores[label] = score
        print(f"Total log score for class '{label.upper()}': {score:.4f}")

    predicted_class = max(class_scores, key=class_scores.get)
    print(f"\nPredicted class: {predicted_class.upper()} (highest log score)\n")
    return predicted_class, class_scores, word_logs

# === Run ===
class_counts, word_counts_per_class, vocab_size = train_naive_bayes_model_with_logs(train_data)

# === Manual Input ===
while True:
    user_text = input("\nEnter news text (or type 'exit' to quit): ")
    if user_text.lower() == "exit":
        break

    predict_news_with_logs(user_text, class_counts, word_counts_per_class, vocab_size)