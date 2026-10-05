# -*- coding: utf-8 -*-
"""Per-module QA for the new lessons: structure + text/html + popup sanity."""
import importlib, os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
TAGS = re.compile(r"<[^>]+>")
PAT = re.compile(r"lessons_part(\d+)\.py$")
paths = [p for p in sorted(glob.glob(os.path.join(HERE, "lessons_part*.py")),
                           key=lambda q: int(PAT.search(q).group(1)))
         if int(PAT.search(p).group(1)) >= 17]
bad_total = 0
for path in paths:
    n = int(PAT.search(path).group(1))
    try:
        m = importlib.import_module(os.path.splitext(os.path.basename(path))[0])
    except Exception as ex:
        print("part%-3d SKIP (import error: %s)" % (n, str(ex).split(chr(10))[0]))
        continue
    probs = []
    for L in m.LESSONS:
        tag = L["file"][:2]
        if len(L.get("translation", [])) != 3:
            probs.append(tag + " translation!=3")
        if len(L.get("bridges", [])) != 2:
            probs.append(tag + " bridges!=2")
        paras = L.get("paragraphs", [])
        if len(paras) != 3:
            probs.append(tag + " paragraphs!=3")
        for pi, para in enumerate(paras, 1):
            if len(para) != 3:
                probs.append(tag + " P%d!=3 sentences" % pi)
            for s in para:
                plain = re.sub(r"\s+", " ", TAGS.sub("", s.get("html", ""))).strip()
                txt = re.sub(r"\s+", " ", s.get("text", "")).strip()
                if plain != txt:
                    probs.append(tag + " text/html mismatch: %r vs %r" % (plain[:40], txt[:40]))
                pop = s.get("pop", "")
                if "</li>" in pop:
                    probs.append(tag + " pop has </li>")
                if len(pop) < 100:
                    probs.append(tag + " pop too short")
                if not re.search(r'class="w-tap kw-(verb|colloc|link)"', s.get("html", "")):
                    probs.append(tag + " no highlighted word")
                wc = len([w for w in re.findall(r"[A-Za-z][A-Za-z\'-]*", txt)])
                if wc < 6 or wc > 22:
                    probs.append(tag + " sentence word count %d: %s" % (wc, txt[:50]))
        sums = L.get("summary", [])
        if len(sums) != 3:
            probs.append(tag + " summary!=3 cards")
        else:
            for ci, need in enumerate([4, 5, 3]):
                if len(sums[ci]) < need:
                    probs.append(tag + " summary card%d has %d (<%d)" % (ci+1, len(sums[ci]), need))
        if len(L.get("sum_titles", [])) != 3:
            probs.append(tag + " sum_titles!=3")
    status = "OK" if not probs else "ISSUES(%d)" % len(probs)
    print("part%-3d %s" % (n, status))
    for p in probs[:8]:
        print("      - " + p)
    if len(probs) > 8:
        print("      ... and %d more" % (len(probs) - 8))
    bad_total += len(probs)
print()
print("TOTAL PROBLEMS:", bad_total)
