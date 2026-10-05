# -*- coding: utf-8 -*-
import os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.abspath(os.path.join(HERE, os.pardir, "docs"))
files = set(os.path.basename(p) for p in glob.glob(os.path.join(D, "*.html")))
HREF = re.compile(r'href="([^"#:]+?\.html)"')
bad = total = 0
for f in sorted(files):
    s = open(os.path.join(D, f), encoding="utf-8").read()
    for m in HREF.finditer(s):
        total += 1
        if m.group(1) not in files:
            print("  BROKEN %s -> %s" % (f, m.group(1)))
            bad += 1
print("internal links: %d checked, %d broken" % (total, bad))
sys.exit(1 if bad else 0)
