"""
Comprehensive POS tagging for all w-tap spans.
This script reads all lesson files, finds all w-tap spans, and adds
data-pos and data-func attributes based on the kw-* class.
"""

import os
import re

BASE = r"C:\Users\joshu\Downloads\mkes1-6\build"

# POS and function mapping based on kw-* class
CLASS_INFO = {
    'kw-verb': {'pos': 'VERB', 'func': 'predicate'},
    'kw-colloc': {'pos': 'NOUN', 'func': 'object'},  # default for collocations
    'kw-link': {'pos': 'ADV', 'func': 'adjunct'},    # default for linking expressions
}

# Special overrides for specific words/phrases
SPECIAL_CASES = {
    # (word_lower, current_class): {'pos': ..., 'func': ..., 'new_class': ...}
    ("ms. chen", "kw-colloc"): {"pos": "PROPN", "func": "appositive", "new_class": "kw-link"},
    ("at first", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("by friday", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("at the beginning of", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("in the mountains", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near our home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("in the waiting room", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("after school", "kw-link"): {"pos": "PREP", "func": "prep_phrase"},
    ("next to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near", "kw-colloc"): {"pos": "PREP", "func": "prep"},
    ("about", "kw-colloc"): {"pos": "PREP", "func": "prep"},
    ("near our home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("in the waiting room", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("three times a day", "kw-colloc"): {"pos": "NUM", "func": "adv_phrase"},
    ("by friday", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("at the beginning of", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("if we had checked the weather report", "kw-colloc"): {"pos": "SCONJ", "func": "adv_clause"},
    ("if you go camping", "kw-colloc"): {"pos": "SCONJ", "func": "adv_clause"},
    ("if it didn't rain", "kw-colloc"): {"pos": "SCONJ", "func": "adv_clause"},
    ("ms. chen", "kw-colloc"): {"pos": "PROPN", "func": "appositive", "new_class": "kw-link"},
    ("at first", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("by friday", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("at the beginning of", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("in the mountains", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near our home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("in the waiting room", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("after school", "kw-link"): {"pos": "PREP", "func": "prep_phrase"},
    ("next to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near", "kw-colloc"): {"pos": "PREP", "func": "prep"},
    ("about", "kw-colloc"): {"pos": "PREP", "func": "prep"},
    ("near our home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("in the waiting room", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("three times a day", "kw-colloc"): {"pos": "NUM", "func": "adv_phrase"},
    ("by friday", "kw-colloc"): {"pos": "ADV", "func": "adv_phrase", "new_class": "kw-link"},
    ("at the beginning of", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase", "new_class": "kw-link"},
    ("in the mountains", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near our home", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("in the waiting room", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("on the way to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("after school", "kw-link"): {"pos": "PREP", "func": "prep_phrase"},
    ("next to", "kw-colloc"): {"pos": "PREP", "func": "prep_phrase"},
    ("near", "kw-colloc"): {"pos": "PREP", "func": "prep"},
    ("about", "kw-colloc"): {"pos": "PREP", "func": "prep"},
}

def classify_phrase(word, current_class):
    """Determine POS and function for a word/phrase."""
    word_lower = word.lower().strip()
    
    # Check special cases first
    if (word_lower, current_class) in SPECIAL_CASES:
        return SPECIAL_CASES[(word_lower, current_class)]
    if word_lower in SPECIAL_CASES:
        return SPECIAL_CASES[word_lower]
    
    # Default based on class
    info = CLASS_INFO.get(current_class, {'pos': 'X', 'func': 'unknown'})
    return {
        'pos': info['pos'],
        'func': info['func'],
        'new_class': current_class
    }

def process_lesson_file(filepath):
    """Process a single lesson file, adding POS/func to all w-tap spans."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # Pattern to match w-tap spans
    pattern = r'(<span class="w-tap (kw-(verb|colloc|link))"[^>]*>)([^<]+)(</span>)'
    
    def replace_match(match):
        nonlocal changes
        full_tag = match.group(1)
        current_class = match.group(2)
        kw_class = match.group(3)
        word = match.group(4)
        closing = match.group(5)
        
        # Check if already has data-pos
        if 'data-pos' in full_tag:
            return match.group(0)
        
        word_lower = word.lower().strip()
        info = classify_phrase(word, kw_class)
        
        # Build new tag with data attributes
        new_class = info.get('new_class', current_class)
        pos = info['pos']
        func = info['func']
        
        # Replace class if changed
        new_tag = full_tag.replace(f'class="w-tap {current_class}"', f'class="w-tap {new_class}"')
        
        # Add data attributes before the closing >
        new_tag = new_tag.replace('>', f' data-pos="{pos}" data-func="{func}">')
        
        changes += 1
        return new_tag + word + closing
    
    new_content = re.sub(pattern, replace_match, content)
    
    if changes > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(filepath)}: {changes} spans tagged")
    else:
        print(f"No changes: {os.path.basename(filepath)}")
    
    return changes

def main():
    lesson_files = [
        "lessons_part1.py", "lessons_part2.py", "lessons_part3.py", "lessons_part4.py",
        "lessons_part5.py", "lessons_part6.py", "lessons_part7.py", "lessons_part8.py",
        "lessons_part9.py", "lessons_part10.py",
    ]
    
    total = 0
    for f in lesson_files:
        path = os.path.join(BASE, f)
        if os.path.exists(path):
            total += process_lesson_file(path)
    
    print(f"\nTotal spans tagged: {total}")

if __name__ == "__main__":
    main()