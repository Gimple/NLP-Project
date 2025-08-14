import json
import re
import string
from typing import Dict, Any

class JejemonNormalizer:
    def __init__(self, dictionary_file: str = "TransJeje/jejemon.json"):
        self.dictionary_file = dictionary_file
        self.jejemon_dict = self.load_dictionary()
    
    def load_dictionary(self) -> Dict[str, str]:
        try:
            with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Dictionary file '{self.dictionary_file}' not found.")
            print("Using empty dictionary. Please ensure jejemon.json exists.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in '{self.dictionary_file}'")
            return {}
    
    def remove_repeated_letters(self, text: str) -> str:
        return re.sub(r'(\w)\1{2,}', r'\1', text)
    
    def is_proper_sentence_punctuation(self, text: str) -> str:
        # Characters to always exempt from removal
        always_exempt = '#@$¥'
        
        # Sentence punctuation that we want to preserve when used correctly
        sentence_punct = '.,!?'
        
        # Create a list to store the result
        result = []
        chars = list(text)
        
        for i, char in enumerate(chars):
            # Always keep exempt characters
            if char in always_exempt:
                result.append(char)
            # Handle sentence punctuation with context
            elif char in sentence_punct:
                if self._is_punctuation_proper(chars, i, char):
                    result.append(char)
                # If not proper, skip (remove) this punctuation
            # Handle apostrophes in contractions
            elif char == "'":
                if self._is_apostrophe_in_contraction(chars, i):
                    result.append(char)
            # Remove other punctuation
            elif char not in string.punctuation:
                result.append(char)
            # Skip other punctuation marks
        
        return ''.join(result)
    
    def _is_punctuation_proper(self, chars: list, index: int, punct: str) -> bool:
        text_length = len(chars)
        
        if punct == '.':
            # Period should be at end of sentence or after abbreviations
            # Check if it's at the end or followed by space/end
            if index == text_length - 1:  # At the very end
                return True
            if index < text_length - 1 and chars[index + 1] == ' ':
                # Check if there's text after the space (new sentence)
                remaining = ''.join(chars[index + 1:]).strip()
                if remaining and remaining[0].isupper():
                    return True
                # If at end after space, also valid
                if not remaining:
                    return True
            return False
            
        elif punct == ',':
            # Comma should be between words, not at start/end of text
            if index == 0 or index == text_length - 1:
                return False
            # Should have non-space characters before and after (eventually)
            has_word_before = any(c.isalnum() for c in chars[:index][::-1][:10])  # Check last 10 chars
            has_word_after = any(c.isalnum() for c in chars[index + 1:index + 11])  # Check next 10 chars
            return has_word_before and has_word_after
            
        elif punct in '!?':
            # Question mark and exclamation should be at end of sentence
            if index == text_length - 1:  # At the very end
                return True
            if index < text_length - 1 and chars[index + 1] == ' ':
                # Check if there's text after the space (new sentence)
                remaining = ''.join(chars[index + 1:]).strip()
                if remaining and remaining[0].isupper():
                    return True
                # If at end after space, also valid
                if not remaining:
                    return True
            return False
            
        return False
    
    def _is_apostrophe_in_contraction(self, chars: list, index: int) -> bool:
        text_length = len(chars)
        
        # Must have letters before and after
        if index == 0 or index == text_length - 1:
            return False
        
        # Check for letter before and after apostrophe
        has_letter_before = index > 0 and chars[index - 1].isalpha()
        has_letter_after = index < text_length - 1 and chars[index + 1].isalpha()
        
        return has_letter_before and has_letter_after
    
    def remove_punctuation(self, text: str) -> str:
        return self.is_proper_sentence_punctuation(text)
    
    def normalize_special_characters(self, text: str) -> str:

        # Dictionary mapping special characters to their base equivalents
        special_char_map = {
            # Accented vowels
            'á': 'a', 'à': 'a', 'â': 'a', 'ä': 'a', 'ā': 'a', 'ă': 'a', 'ą': 'a', 'ã': 'a', 'å': 'a',
            'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'ē': 'e', 'ĕ': 'e', 'ę': 'e', 'ė': 'e',
            'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i', 'ī': 'i', 'ĭ': 'i', 'į': 'i', 'ĩ': 'i',
            'ó': 'o', 'ò': 'o', 'ô': 'o', 'ö': 'o', 'ō': 'o', 'ŏ': 'o', 'ő': 'o', 'õ': 'o', 'ø': 'o',
            'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u', 'ū': 'u', 'ŭ': 'u', 'ů': 'u', 'ű': 'u', 'ũ': 'u',
            'ý': 'y', 'ỳ': 'y', 'ŷ': 'y', 'ÿ': 'y', 'ȳ': 'y', 'ỹ': 'y',
            
            # Uppercase accented vowels
            'Á': 'A', 'À': 'A', 'Â': 'A', 'Ä': 'A', 'Ā': 'A', 'Ă': 'A', 'Ą': 'A', 'Ã': 'A', 'Å': 'A',
            'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E', 'Ē': 'E', 'Ĕ': 'E', 'Ę': 'E', 'Ė': 'E',
            'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I', 'Ī': 'I', 'Ĭ': 'I', 'Į': 'I', 'Ĩ': 'I',
            'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Ö': 'O', 'Ō': 'O', 'Ŏ': 'O', 'Ő': 'O', 'Õ': 'O', 'Ø': 'O',
            'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U', 'Ū': 'U', 'Ŭ': 'U', 'Ů': 'U', 'Ű': 'U', 'Ũ': 'U',
            'Ý': 'Y', 'Ỳ': 'Y', 'Ŷ': 'Y', 'Ÿ': 'Y', 'Ȳ': 'Y', 'Ỹ': 'Y',
            
            # Special consonants
            'ç': 'c', 'ć': 'c', 'č': 'c', 'ĉ': 'c', 'ċ': 'c',
            'Ç': 'C', 'Ć': 'C', 'Č': 'C', 'Ĉ': 'C', 'Ċ': 'C',
            'ñ': 'n', 'ń': 'n', 'ň': 'n', 'ņ': 'n', 'ṅ': 'n',
            'Ñ': 'N', 'Ń': 'N', 'Ň': 'N', 'Ņ': 'N', 'Ṅ': 'N',
            'š': 's', 'ś': 's', 'ŝ': 's', 'ş': 's', 'ș': 's',
            'Š': 'S', 'Ś': 'S', 'Ŝ': 'S', 'Ş': 'S', 'Ș': 'S',
            'ž': 'z', 'ź': 'z', 'ż': 'z', 'ẑ': 'z',
            'Ž': 'Z', 'Ź': 'Z', 'Ż': 'Z', 'Ẑ': 'Z',
            'ř': 'r', 'ŕ': 'r', 'ṛ': 'r',
            'Ř': 'R', 'Ŕ': 'R', 'Ṛ': 'R',
            'ł': 'l', 'ĺ': 'l', 'ľ': 'l', 'ļ': 'l',
            'Ł': 'L', 'Ĺ': 'L', 'Ľ': 'L', 'Ļ': 'L',
            'đ': 'd', 'ď': 'd', 'ḍ': 'd',
            'Đ': 'D', 'Ď': 'D', 'Ḍ': 'D',
            'ť': 't', 'ţ': 't', 'ț': 't', 'ṭ': 't',
            'Ť': 'T', 'Ţ': 'T', 'Ț': 'T', 'Ṭ': 'T',
            'ğ': 'g', 'ģ': 'g', 'ġ': 'g',
            'Ğ': 'G', 'Ģ': 'G', 'Ġ': 'G',
            'ķ': 'k', 'ḳ': 'k',
            'Ķ': 'K', 'Ḳ': 'K',
            'ḥ': 'h', 'ĥ': 'h',
            'Ḥ': 'H', 'Ĥ': 'H',
            'ṃ': 'm', 'ṁ': 'm',
            'Ṃ': 'M', 'Ṁ': 'M',
            'ṇ': 'n', 'ṅ': 'n',
            'Ṇ': 'N', 'Ṅ': 'N',
            'ṗ': 'p', 'ṕ': 'p',
            'Ṗ': 'P', 'Ṕ': 'P',
            'ḅ': 'b', 'ḇ': 'b',
            'Ḅ': 'B', 'Ḇ': 'B',
            'ḟ': 'f', 'ḋ': 'd',
            'Ḟ': 'F', 'Ḋ': 'D',
            'ṽ': 'v', 'ṿ': 'v',
            'Ṽ': 'V', 'Ṿ': 'V',
            'ẇ': 'w', 'ẁ': 'w', 'ẃ': 'w', 'ẅ': 'w',
            'Ẇ': 'W', 'Ẁ': 'W', 'Ẃ': 'W', 'Ẅ': 'W',
            'ẋ': 'x', 'ẍ': 'x',
            'Ẋ': 'X', 'Ẍ': 'X',
            
            # Additional special characters
            'æ': 'ae', 'œ': 'oe', 'ß': 'ss', 'þ': 'th', 'ð': 'd',
            'Æ': 'AE', 'Œ': 'OE', 'Þ': 'TH', 'Ð': 'D',
            
            # Currency and symbols that might be used as letters
            '€': 'e', '£': 'l', '₱': 'p', '₩': 'w',
            
            # Mathematical and other symbols sometimes used
            'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'e', 'ζ': 'z', 'η': 'h', 'θ': 'th',
            'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
            'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'ch', 'ψ': 'ps', 'ω': 'w',
            
            # Common stylistic characters
            'ı': 'i', 'ȷ': 'j', 'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl',
            
            # Quotation marks and dashes
            '"': '"', '"': '"', ''': "'", ''': "'", '–': '-', '—': '-', '…': '...',
        }
        
        # Apply character replacements
        result = text
        for special_char, replacement in special_char_map.items():
            result = result.replace(special_char, replacement)
        
        # After replacements, remove any remaining non-standard characters
        # Keep only alphanumeric, spaces, and our exempt characters
        result = re.sub(r'[^a-zA-Z0-9\s#@\$¥.,!?\']', '', result)
        
        return result
    
    def normalize_jejemon_words(self, text: str) -> str:
        if not self.jejemon_dict:
            return text
            
        # Split text into words
        words = text.split()
        normalized_words = []
        
        for word in words:
            # Check for exact match (case-insensitive)
            word_lower = word.lower()
            
            # First check exact match
            if word_lower in self.jejemon_dict:
                normalized_words.append(self.jejemon_dict[word_lower])
            else:
                # Check for partial matches or character substitutions
                normalized_word = self.normalize_single_word(word)
                normalized_words.append(normalized_word)
        
        return ' '.join(normalized_words)
    
    def normalize_single_word(self, word: str) -> str:
        normalized = word.lower()
        
        # Check dictionary first
        if normalized in self.jejemon_dict:
            return self.jejemon_dict[normalized]
        
        # Apply common jejemon number-to-letter substitutions
        substitutions = {
            '0': 'o',
            '1': 'i',
            '2': 'to',
            '3': 'e',
            '4': 'a',
            '5': 's',
            '6': 'g',
            '7': 't',
            '8': 'b',
            '9': 'g',
            '@': 'a',
            '#': 'h',
            '$': 's',
            '¥': 'y', 
            #'!': 'i',
        }
        
        # Apply substitutions
        for num, letter in substitutions.items():
            normalized = normalized.replace(num, letter)
        
        # Check dictionary again after substitutions
        if normalized in self.jejemon_dict:
            return self.jejemon_dict[normalized]
        
        # Common jejemon patterns
        patterns = [
            ('q', 'k'),
            ('z', 's'),
            ('zz', 's'),
            ('ph', 'f'),
            ('gh', 'g'),
            ('ck', 'k'),
            ('poh', 'po'),
            ('nah', 'na'),
            ('kah', 'ka'),
            ('tah', 'ta'),
            ('dah', 'da'),
            ('bah', 'ba'),
            ('pah', 'pa'),
            ('noh', 'no'),
            ('koh', 'ko'),
            ('toh', 'to'),
            ('doh', 'do'),
            ('boh', 'bo'),
            ('wah', 'wa'),
            ('yah', 'ya'),
            ('hah', 'ha'),
            ('powh', 'po'),
            ('gah', 'ga'),
            ('moh', 'mo'),
            ('rah', 'ra'),
            ('yoh', 'yo'),
            ('meh', 'me'),
            ('lah', 'la'),
            ('loh', 'lo'),
            ('teh', 'te'),  
            ('sia', 'sya'),
            ('ieh', 'ie'),
            ('mah', 'ma'),
            ('rah', 'ra'),
            ('beh', 'be'),
            ('sah', 'sa'),
            ('soh', 'so'),
            ('leh', 'le'),
            ('mih', 'mi'),
            ("eeh", "ee"),
        ]
        #('x', 'ks'),
        
        for pattern, replacement in patterns:
            normalized = normalized.replace(pattern, replacement)
        
        # Check dictionary one more time
        if normalized in self.jejemon_dict:
            return self.jejemon_dict[normalized]
        
        return normalized
    
    def normalize_text(
        self,
        text: str,
        remove_punct: bool = True,
        remove_special: bool = True,
        remove_repeats: bool = True,
        leetspeak: bool = True,
        jejemon: bool = True,
        capitalize: bool = True
    ) -> Dict[str, Any]:
        
        steps = {}
        current = text
        steps['step_0_raw_text'] = current
        
        for i in range(3):  # Run the process
            print("")
            current = re.sub(r"(?<=\w)!(?=\w)", "i", current)

            if remove_punct:
                current = self.remove_punctuation(current)
            steps[f'step_1_smart_punctuation_{i}'] = current

            if remove_special:
                current = self.normalize_special_characters(current)
            steps[f'step_2_normalized_special_chars_{i}'] = current

            if remove_repeats:
                current = self.remove_repeated_letters(current)
            steps[f'step_3_no_repeated_letters_{i}'] = current

            if jejemon:
                current = self.normalize_jejemon_words(current)
            steps[f'step_4_jejemon_normalized_{i}'] = current

            # Clean up extra spaces while preserving sentence structure
            current = re.sub(r'\s+', ' ', current)  # Replace multiple spaces with single space
            current = re.sub(r'\s+([.,!?])', r'\1', current)  # Remove space before punctuation
            current = re.sub(r'([.,!?])\s*([.,!?])', r'\1\2', current)  # Remove space between punctuation
            current = current.strip()
            steps[f'step_5_clean_spaces_{i}'] = current

            if capitalize and current:
                # Capitalize first letter and letters after sentence-ending punctuation
                current = re.sub(r'(^|[.!?]\s+)([a-z])', 
                               lambda m: m.group(1) + m.group(2).upper(), current)
            steps[f'step_6_capitalized_{i}'] = current
            print("")

        steps['final_normalized'] = current
        return steps
    
    def add_word_mapping(self, jejemon_word: str, normal_word: str) -> bool:
        try:
            self.jejemon_dict[jejemon_word.lower()] = normal_word.lower()
            
            # Save to file
            with open(self.dictionary_file, 'w', encoding='utf-8') as f:
                json.dump(self.jejemon_dict, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding word mapping: {e}")
            return False
