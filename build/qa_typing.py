# -*- coding: utf-8 -*-
"""Sanity-check the typing-practice wiring in every generated page."""
import os
import re
import sys
import ast

HERE = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.abspath(os.path.join(HERE, "..", "docs"))

problems = []
# reading.html 是獨立的 KET 閱讀練習頁，不屬於 60 課。
SKIP = {"index.html", "reading.html"}
files = sorted(f for f in os.listdir(DOCS)
               if f.endswith(".html") and f not in SKIP)

for f in files:
    html = open(os.path.join(DOCS, f), encoding="utf-8").read()
    p = []

    # one panel, one toggle button, one input
    if html.count('id="typePanel"') != 1:
        p.append("typePanel x%d" % html.count('id="typePanel"'))
    if html.count('id="btnType"') != 1:
        p.append("btnType x%d" % html.count('id="btnType"'))
    if html.count('id="typeInput"') != 1:
        p.append("typeInput x%d" % html.count('id="typeInput"'))
    if html.count('id="typeCount"') != 1:
        p.append("typeCount x%d" % html.count('id="typeCount"'))
    if html.count('id="typeTarget"') != 1:
        p.append("typeTarget x%d" % html.count('id="typeTarget"'))

    # the input listener + every handler function must exist
    for fn in ("function toggleType", "function typeWords", "function typeRender",
               "function typeOnInput", "function typeGo", "function typeRestart"):
        if fn not in html:
            p.append("missing " + fn)
    if "addEventListener('input', typeOnInput)" not in html:
        p.append("input not bound")

    # TYPE_SENTENCES must hold exactly the 9 displayed sentences, in order
    m = re.search(r"^\s*TYPE_SENTENCES = (\[[\s\S]*?\]);", html, re.M)
    if not m:
        p.append("TYPE_SENTENCES assignment missing")
    else:
        # The array literal uses \' escaping; turn it into a Python literal.
        # Extract each single-quoted string, honouring \' escapes inside.
        arr = []
        i = 1  # skip the opening [
        n = len(m.group(1))
        while i < n:
            if m.group(1)[i] != "'":
                i += 1
                continue
            i += 1
            buf = []
            while i < n:
                ch = m.group(1)[i]
                if ch == "\\" and i + 1 < n:
                    buf.append(m.group(1)[i + 1])
                    i += 2
                    continue
                if ch == "'":
                    i += 1
                    break
                buf.append(ch)
                i += 1
            arr.append("".join(buf))
        texts = []
        for block in html.split('<div class="paragraph-container">')[1:]:
            rx = re.compile(r'<div class="sentence-text"[^>]*>\s*\n(.*?)\n\s*</div>', re.S)
            texts += [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", x)).strip()
                      for x in rx.findall(block)]
        if len(arr) != 9:
            p.append("TYPE_SENTENCES has %d items" % len(arr))
        if [a for a in arr] != texts:
            diff = [(i, a, b) for i, (a, b) in enumerate(zip(arr, texts)) if a != b]
            p.append("sentences differ from page (%d mismatches): %s"
                     % (len(diff), diff[:2]))
        # them must survive JS evaluation
        if any(not isinstance(x, str) or not x for x in arr):
            p.append("non-string items")

    # the panel must be closed by default so it does not disturb readers
    if 'id="typePanel" hidden' not in html and 'id="typePanel"\n' not in html:
        p.append("panel not hidden by default")

    if p:
        problems.append((f, p))

for f, p in problems:
    print("FAIL %s" % f)
    for x in p:
        print("   - %s" % x)
print("")
print("checked %d pages, %d with problems" % (len(files), len(problems)))
print("RESULT:", "PASS" if not problems else "FAIL")
