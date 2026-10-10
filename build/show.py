# -*- coding: utf-8 -*-
"""Ad-hoc inspector: python show.py <lesson-number> [field] [index]"""
import sys
import re
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8")

import build  # noqa: E402

TAG = re.compile(r"<[^>]+>")


def plain(s):
    return re.sub(r"\s+", " ", TAG.sub("", s)).strip()


def main():
    n = int(sys.argv[1])
    L = build.load_lessons()[n - 1]
    what = sys.argv[2] if len(sys.argv) > 2 else "all"
    raw = "raw" in sys.argv

    def out(s):
        print(s if raw else plain(s))

    if what in ("all", "meta"):
        for k in ("file", "title_cn", "topic", "grammar", "story_title",
                  "sum_intro"):
            print("%-12s %s" % (k, L.get(k) if raw else plain(L.get(k))))
        for i, t in enumerate(L["sum_titles"], 1):
            print("%-12s [%d] %s" % ("sum_titles", i, t))
        print()

    if what in ("all", "pop"):
        for pi, para in enumerate(L["paragraphs"], 1):
            for si, s in enumerate(para, 1):
                print("=== %d.%d ===" % (pi, si))
                print("TEXT: %s" % s["text"])
                print("HTML: %s" % s["html"])
                print("POP : %s" % out(s["pop"]))
                print()

    if what in ("all", "sum"):
        for ci, card in enumerate(L["summary"], 1):
            print("--- CARD%d %s ---" % (ci, L["sum_titles"][ci - 1]))
            for li, item in enumerate(card, 1):
                print("%d) %s" % (li, out(item)))
            print()

    if what in ("all", "tr"):
        for i, t in enumerate(L["translation"], 1):
            print("T%d %s" % (i, t))
        for i, b in enumerate(L["bridges"], 1):
            print("BRIDGE%d %s" % (i, b))


if __name__ == "__main__":
    main()