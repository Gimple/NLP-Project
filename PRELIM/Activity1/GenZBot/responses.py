import json
import os

POSITIVE_RESPONSES = None
NEGATIVE_RESPONSES = None

def load_positive_responses():
    global POSITIVE_RESPONSES
    if POSITIVE_RESPONSES is None:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(dir_path, 'positive_responses.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            POSITIVE_RESPONSES = json.load(f)
    return POSITIVE_RESPONSES

def load_negative_responses():
    global NEGATIVE_RESPONSES
    if NEGATIVE_RESPONSES is None:
        dir_path = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(dir_path, 'negative_responses.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            NEGATIVE_RESPONSES = json.load(f)
    return NEGATIVE_RESPONSES

def load_responses():
    """Load and combine both positive and negative responses for backward compatibility"""
    positive = load_positive_responses()
    negative = load_negative_responses()
    
    combined = {}
    combined.update(positive)
    combined.update(negative)
    
   
    combined['sentiment'] = {}
    if 'sentiment' in positive:
        combined['sentiment'].update(positive['sentiment'])
    if 'sentiment' in negative:
        combined['sentiment'].update(negative['sentiment'])
    
    return combined