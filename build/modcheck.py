# -*- coding: utf-8 -*-
"""modcheck: verify every lessons_part*.py imports and report ordering."""
import importlib, io, os, re, sys, glob
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PAT = re.compile(r"lessons_part(\d+)\.py$")
paths = sorted(glob.glob(os.path.join(HERE, "lessons_part*.py")), key=lambda p: int(PAT.search(p).group(1)))
total, files = 0, []
bad = 0
for path in paths:
    n = int(PAT.search(path).group(1))
    name = os.path.splitext(os.path.basename(path))[0]
    try:
        m = importlib.import_module(name)
        got = [L["file"] for L in m.LESSONS]
        total += len(got)
        files.extend(got)
        print("part%-3d OK   %d 課  %s" % (n, len(got), ", ".join(got)))
    except Exception as ex:
        bad += 1
        print("part%-3d IMPORT FAIL: %s: %s" % (n, type(ex).__name__, str(ex).split(chr(10))[0]))
print()
print("modules: %d | lessons: %d | failures: %d" % (len(paths), total, bad))
dup = sorted({f for f in files if files.count(f) > 1})
if dup:
    print("DUPLICATE FILES:", dup)
order_ok = all(f.startswith("%02d-" % (i + 1)) for i, f in enumerate(files))
print("numbering in order:", order_ok)
if not order_ok:
    for i, f in enumerate(files, 1):
        if not f.startswith("%02d-" % i):
            print("   position %d -> %s" % (i, f))
sys.exit(1 if (bad or dup or not order_ok) else 0)
