import re
import pyphen
from collections import Counter

# Initialize dictionary for hyphenation (English)
dic = pyphen.Pyphen(lang='en_US')

# Common consonant clusters that are often difficult for dyslexic readers
DIFFICULT_CLUSTERS = ['str', 'spl', 'sch', 'thr', 'squ', 'chr', 'phth']
# Mirror letters that cause confusion
MIRROR_LETTERS = ['b', 'd', 'p', 'q', 'm', 'n']

class NLPEngine:
    def __init__(self):
        pass
        
    def count_syllables(self, word):
        """Estimate syllable count based on hyphenation."""
        hyphenated = dic.inserted(word)
        return len(hyphenated.split('-'))

    def get_syllables(self, word):
        """Return the syllables of a word."""
        hyphenated = dic.inserted(word)
        return hyphenated.split('-')

    def is_difficult_word(self, word):
        """
        Determine if a word is likely difficult for a dyslexic reader.
        Criteria:
        1. Length > 7 characters
        2. Contains 3 or more syllables
        3. Contains complex consonant clusters
        4. High concentration of mirror letters
        """
        word = word.lower()
        word = re.sub(r'[^a-z]', '', word) # Clean punctuation
        
        if len(word) == 0:
            return False

        # Criteria 1: Length
        if len(word) > 8:
            return True
            
        # Criteria 2: Syllable count
        syllable_count = self.count_syllables(word)
        if syllable_count >= 3:
            return True

        # Criteria 3: Difficult clusters
        for cluster in DIFFICULT_CLUSTERS:
            if cluster in word:
                return True

        # Criteria 4: High concentration of mirror letters
        mirror_count = sum(1 for char in word if char in MIRROR_LETTERS)
        if len(word) > 4 and mirror_count >= 3:
            return True

        return False

    def analyze_text(self, text):
        """
        Analyze a paragraph of text, find difficult words and their syllables.
        """
        # Split text into words keeping basic structure
        words = re.findall(r'\b[A-Za-z]+\b', text)
        
        difficult_words_list = []
        # Use a set to avoid duplicating work on the same word
        seen = set()
        
        for w in words:
            word_lower = w.lower()
            if word_lower in seen:
                continue
            seen.add(word_lower)
            
            if self.is_difficult_word(w):
                syllables = self.get_syllables(w)
                # Fallback if pyphen fails
                if not syllables or len(syllables) == 1:
                    syllables = [w]
                    
                difficult_words_list.append({
                    "word": w,
                    "syllables": syllables
                })
                
        return difficult_words_list

nlp_engine = NLPEngine()
