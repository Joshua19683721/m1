# -*- coding: utf-8 -*-
"""check_vocab2: does each lesson actually USE its declared A2 Key topics?"""
import os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build

BASE = ["Appliances", "Clothes and Accessories", "Colours",
        "Communication and Technology", "Documents and Texts", "Education",
        "Entertainment and Media", "Family and Friends", "Food and Drink",
        "Health, Medicine and Exercise", "Hobbies and Leisure", "House and Home",
        "Measurements", "Places: Buildings", "Places: Countryside",
        "Places: Town and City", "Services", "Shopping", "Sport",
        "The Natural World", "Time", "Travel and Transport", "Weather",
        "Work and Jobs"]
# canonical name -> the exact heading line as it appears in the PDF text
ALIAS = {h: h for h in BASE}
ALIAS["Personal Feelings, Opinions and Experiences"] = "Personal Feelings, Opinions and Experiences (adjectives)"

HEAD2CANON = {v: k for k, v in ALIAS.items()}
raw = open(os.path.join(HERE, "a2key_topics.txt"), encoding="utf-8").read().split(chr(10))
GROUPS, cur, words = {}, None, []
PAREN = re.compile(r"\s*\(.*?\)")
WORD = re.compile(r"^[A-Za-z][A-Za-z\-]*$")
for line in raw:
    s = line.strip()
    if not s or s in ("Topic Lists", "Schools"):
        continue
    if s in ALIAS.values():
        if cur:
            GROUPS[cur] = sorted(set(words))
        cur, words = HEAD2CANON[s], []
        continue
    if cur:
        for tok in s.split():
            tok = PAREN.sub("", tok).strip().strip(",")
            if tok and WORD.match(tok):
                words.append(tok.lower())
if cur:
    GROUPS[cur] = sorted(set(words))

print("topic groups parsed: %d" % len(GROUPS))
for k in sorted(GROUPS):
    if len(GROUPS[k]) < 8:
        print("  !! %s has only %d words" % (k, len(GROUPS[k])))
print()
ALL = build.load_lessons()
TOK = re.compile(r"[a-z][a-z\-]*")
SPLIT = re.compile("\uff0f|/")
print("%-3s %-30s %s" % ("L", "declared topic", "topic words actually used in the story"))
print("-" * 112)
zero = []
for i, L in enumerate(ALL, 1):
    story = " ".join(s["text"] for para in L["paragraphs"] for s in para).lower()
    sw = set(TOK.findall(story))
    cols = []
    for t in [x.strip() for x in SPLIT.split(L["topic"]) if x.strip()]:
        pool = GROUPS.get(t, [])
        hit = sorted(w for w in pool if w in sw)
        cols.append("%s: %d/%d [%s]" % (t.split(":")[0][:14], len(hit), len(pool), ", ".join(hit[:6])))
        if len(hit) == 0:
            zero.append((i, L["file"], t))
    print("%-3d %-30s %s" % (i, L["title_cn"][:14], "  ||  ".join(cols)[:100]))
print()
if zero:
    print("TOPICS DECLARED BUT ZERO VOCABULARY USED:")
    for i, f, t in zero:
        print("  L%d %s -> %s" % (i, f, t))
else:
    print("OK: every declared topic has vocabulary actually used in its story")

