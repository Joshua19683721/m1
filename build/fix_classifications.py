"""
Comprehensive fix for:
1. Fix existing kw-verb/colloc/link misclassifications
2. Add proper "詞性與功能" (POS + syntactic function) analysis

This script will:
- Fix misclassified kw-verb/colloc/link tags
- Add data-pos and data-func attributes to each w-tap span
- Update all lesson part files
"""

import os
import re
import json

# The base directory
BASE = r"C:\Users\joshu\Downloads\mkes1-6\build"

# Fix mapping for misclassifications
# Format: (lesson_file, old_class, word, new_class, pos, function)
FIXES = [
    # Lesson 1
    ("lessons_part1.py", "colloc", "Ms. Chen", "link", "PROPN", "appositive"),  # proper noun, appositive
    ("lessons_part1.py", "colloc", "next to", "colloc", "PREP", "prep_phrase"),  # preposition phrase - keep colloc but add pos
    
    # Lesson 2
    ("lessons_part2.py", "colloc", "near", "colloc", "PREP", "prep"),  # preposition
    ("lessons_part2.py", "colloc", "about", "colloc", "PREP", "prep"),  # preposition
    ("lessons_part2.py", "colloc", "which was quite cheap", "colloc", "SCONJ", "rel_clause"),  # relative clause
    ("lessons_part2.py", "colloc", "how much money", "colloc", "PRON", "obj"),  # wh-phrase as object
    ("lessons_part2.py", "colloc", "fifty yuan", "colloc", "NUM", "obj"),  # numeral phrase
    ("lessons_part2.py", "colloc", "a bowl of noodles", "colloc", "NOUN", "obj"),  # noun phrase
    ("lessons_part2.py", "colloc", "next to", "colloc", "PREP", "prep_phrase"),
    ("lessons_part2.py", "colloc", "took a lot of photos", "colloc", "VERB", "verb_phrase"),
    
    # Lesson 3
    ("lessons_part3.py", "colloc", "At first", "link", "ADV", "adv_phrase"),  # adverbial phrase
    ("lessons_part3.py", "colloc", "told us to keep our eyes on", "colloc", "VERB", "verb_phrase"),
    ("lessons_part3.py", "colloc", "practice games", "colloc", "NOUN", "obj"),
    ("lessons_part3.py", "colloc", "Winning the trophy", "colloc", "VERB", "subj"),  # gerund as subject
    ("lessons_part3.py", "colloc", "sore throat", "colloc", "NOUN", "obj"),
    ("lessons_part3.py", "colloc", "headache", "colloc", "NOUN", "obj"),
    ("lessons_part3.py", "colloc", "near our home", "colloc", "PREP", "prep_phrase"),
    ("lessons_part3.py", "colloc", "in the waiting room", "colloc", "PREP", "prep_phrase"),
    ("lessons_part3.py", "colloc", "three times a day", "colloc", "NUM", "adv_phrase"),
    ("lessons_part3.py", "colloc", "shouldn't eat any ice cream for a week", "colloc", "VERB", "verb_phrase"),
    ("lessons_part3.py", "colloc", "By Friday", "link", "ADV", "adv_phrase"),
    
    # Lesson 4
    ("lessons_part4.py", "colloc", "At the beginning of", "link", "PREP", "prep_phrase"),
    ("lessons_part4.py", "colloc", "some new stationery", "colloc", "NOUN", "obj"),
    ("lessons_part4.py", "colloc", "near", "colloc", "PREP", "prep"),
    ("lessons_part4.py", "colloc", "many kinds of", "colloc", "DET", "det_phrase"),
    ("lessons_part4.py", "colloc", "couldn't decide which one was the best", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "should ask the shop assistant for help", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "cost only fifteen yuan", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "could have bought", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "the most expensive one", "colloc", "NOUN", "obj"),
    ("lessons_part4.py", "colloc", "didn't need", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "On the way home", "link", "PREP", "prep_phrase"),
    ("lessons_part4.py", "colloc", "counted our money", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "found that", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "still had some left", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "had saved some money for", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "in the mountains", "colloc", "PREP", "prep_phrase"),
    ("lessons_part4.py", "colloc", "if it didn't rain", "colloc", "SCONJ", "adv_clause"),
    ("lessons_part4.py", "colloc", "would go hiking", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "appeared above", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "became stronger", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "If we had checked the weather report", "colloc", "SCONJ", "adv_clause"),
    ("lessons_part4.py", "colloc", "would have stayed in", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "suggested that", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "put our food into boxes", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "move the tents to", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "rained heavily for about two hours", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "got wet", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "were safe", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "If you go camping", "colloc", "SCONJ", "adv_clause"),
    ("lessons_part4.py", "colloc", "should always take", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "some warm clothes", "colloc", "NOUN", "obj"),
    ("lessons_part4.py", "colloc", "smelled fresh", "colloc", "VERB", "verb_phrase"),
    ("lessons_part4.py", "colloc", "felt relaxed", "colloc", "VERB", "verb_phrase"),
]

# POS tag mapping for function tags
POS_MAP = {
    'verb': 'VERB',
    'colloc': 'NOUN',  # default for collocations
    'link': 'ADV',     # default for linking expressions
}

# Syntactic function mapping
FUNC_MAP = {
    'verb': 'predicate',
    'colloc': 'object',
    'link': 'adjunct',
}

def apply_fixes():
    """Apply all fixes to lesson files."""
    for lesson_file, old_class, word, new_class, pos, func in FIXES:
        path = os.path.join(BASE, lesson_file)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        with open(path, encoding="utf-8") as f:
            content = f.read()
        
        # Find and replace the specific w-tap span
        escaped_word = re.escape(word)
        # Match: <span class="w-tap kw-old_class">word</span>
        pattern = rf'(<span class="w-tap kw-){re.escape(old_class)}(">{re.escape(word)}</span>)'
        
        # Replacement with new class and pos/func attributes
        replacement = rf'\1{new_class}\2 data-pos="{pos}" data-func="{func}"'
        
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Fixed: {lesson_file} | {old_class} -> {new_class} | {word} | POS={pos} FUNC={func}")
        else:
            # Try alternative pattern (maybe with escaped quotes)
            alt_pattern = rf'<span class="w-tap kw-{old_class}">{escaped_word}</span>'
            if alt_pattern in content:
                content = content.replace(
                    f'<span class="w-tap kw-{old_class}">{word}</span>',
                    f'<span class="w-tap kw-{new_class}" data-pos="{pos}" data-func="{func}">{word}</span>'
                )
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Fixed (alt): {lesson_file} | {old_class} -> {new_class} | {word}")
            else:
                print(f"NOT FOUND: {lesson_file} | {old_class} | {word}")

if __name__ == "__main__":
    apply_fixes()
    print("Done applying fixes.")