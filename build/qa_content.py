# -*- coding: utf-8 -*-
"""Content audit of the per-lesson analysis panels (pops + summary cards).

The existing checks prove structure. This one reads the analysis *content* and
flags the ways it can drift from the SCHEMA contract or contradict the sentence
it explains. Findings are written to build/audit_report.txt for review.
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import build  # noqa: E402

TAG = re.compile(r"<[^>]+>")


def plain(s):
    return re.sub(r"\s+", " ", TAG.sub("", s)).strip()


def pop_items(pop):
    """Split a pop back into its numbered points."""
    body = pop
    body = re.sub(r"^\s*<strong>.*?</strong>\s*<br>\s*", "", body, flags=re.S)
    parts = [p.strip() for p in re.split(r"<br>\s*(?=\d+\.\s)", body)]
    parts = [p for p in parts if p.strip()]
    return parts


def main():
    lessons = build.load_lessons()
    out = []
    problems = []

    def flag(no, file, kind, detail):
        problems.append("L%-3d %-32s %-14s %s" % (no, file, kind, detail))

    for no, L in enumerate(lessons, 1):
        f = L["file"]
        all_text = []

        for pi, para in enumerate(L["paragraphs"], 1):
            for si, s in enumerate(para, 1):
                tag = "%d.%d" % (pi, si)
                text = s["text"]
                all_text.append(text)

                # -- 2~4 highlighted keywords per sentence (SCHEMA)
                taps = re.findall(r'<span class="w-tap[^"]*">', s["html"])
                if not 2 <= len(taps) <= 4:
                    flag(no, f, "w-tap", "%s has %d taps (spec: 2-4) | %s"
                         % (tag, len(taps), text))

                # -- pop structure
                items = pop_items(s["pop"])
                if not 2 <= len(items) <= 3:
                    flag(no, f, "pop-count", "%s has %d points (spec: 2-3)"
                         % (tag, len(items)))
                if "<li>" in s["pop"] or "</li>" in s["pop"]:
                    flag(no, f, "pop-tag", "%s pop contains <li>" % tag)

        # -- summary card sizes (SCHEMA: 4 / 5 / 3)
        want = (4, 5, 3)
        for ci, card in enumerate(L["summary"]):
            if len(card) != want[ci]:
                flag(no, f, "summary-size", "card %d has %d items (spec: %d)"
                     % (ci + 1, len(card), want[ci]))

        if len(L["translation"]) != 3 or len(L["bridges"]) != 2:
            flag(no, f, "shape", "translation=%d bridges=%d"
                 % (len(L["translation"]), len(L["bridges"])))

        # -- punctuation hygiene across everything shown on the page
        blob = plain(" ".join(all_text)) + " " + \
            plain(" ".join(L["translation"]) + " " + " ".join(L["bridges"]) + " " +
                  L["sum_intro"] + " " + " ".join(L["sum_titles"]) + " " +
                  " ".join(plain(i) for c in L["summary"] for i in c)) + " " + \
            " ".join(plain(s["pop"]) for para in L["paragraphs"] for s in para)

        # Typographic quotes must be gone; build.py normalises them to U+0027.
        for ch, name in (("’", "curly apostrophe"), ("‘", "curly quote"),
                         ("“", "curly quote"), ("”", "curly quote")):
            if ch in blob:
                flag(no, f, "punct", "%s U+%04X" % (name, ord(ch)))

        if re.search(r"[ \t]{2,}", blob):
            flag(no, f, "space", "double space")

        # -- every sentence ends with terminal punctuation (allowing quoted speech)
        for si, t in enumerate(all_text, 1):
            core = t.rstrip("\"'\u201d\u2019)]").rstrip()
            if not core.endswith((".", "!", "?")):
                flag(no, f, "ending", "sentence %d ends with %r" % (si, t[-35:]))

        out.append((no, f, L))

    # ---------------- report ----------------
    lines = []
    lines.append("=" * 100)
    lines.append("LESSON ANALYSIS PANELS - FULL DUMP (for content review)")
    lines.append("=" * 100)
    for no, f, L in out:
        lines.append("")
        lines.append("#" * 100)
        lines.append("### L%d  %s  |  %s" % (no, f, L["title_cn"]))
        lines.append("    topic=%s | grammar=%s" % (L["topic"], L["grammar"]))
        lines.append("    story=%s" % L["story_title"])
        lines.append("#" * 100)
        n = 0
        for pi, para in enumerate(L["paragraphs"], 1):
            lines.append("")
            lines.append("  [P%d]" % pi)
            for si, s in enumerate(para, 1):
                n += 1
                lines.append("    (%d.%d) %s" % (pi, si, s["text"]))
                for it in pop_items(s["pop"]):
                    lines.append("        . %s" % plain(it))
        lines.append("")
        lines.append("  TRANSLATION")
        for ti, t in enumerate(L["translation"], 1):
            lines.append("    T%d %s" % (ti, t))
        for bi, b in enumerate(L["bridges"], 1):
            lines.append("    BRIDGE%d %s" % (bi, b))
        lines.append("  SUMMARY INTRO: %s" % L["sum_intro"])
        for ci, card in enumerate(L["summary"]):
            lines.append("  CARD%d %s" % (ci + 1, L["sum_titles"][ci]))
            for li, item in enumerate(card, 1):
                lines.append("    %d) %s" % (li, plain(item)))

    open(os.path.join(HERE, "audit_dump.txt"), "w", encoding="utf-8").write(
        "\n".join(lines))

    # Split the dump into review chunks so the content can be read in parallel.
    blocks = []
    current = []
    for line in lines:
        if line.startswith("### L") and current:
            blocks.append(current)
            current = []
        current.append(line)
    if current:
        blocks.append(current)

    step = 10
    for n in range(0, len(blocks), step):
        chunk = [ln for b in blocks[n:n + step] for ln in b]
        open(os.path.join(HERE, "audit_chunk_%02d.txt" % (n // step + 1)), "w",
             encoding="utf-8").write("\n".join(chunk))
    print("chunks written: %d (up to %d lessons each)"
          % ((len(blocks) + step - 1) // step, step))

    print("=" * 100)
    print("MECHANICAL FINDINGS")
    print("=" * 100)
    if problems:
        for p in problems:
            print(p)
    else:
        print("none")
    print("")
    print("findings: %d" % len(problems))
    print("dump written: build/audit_dump.txt")
    open(os.path.join(HERE, "audit_findings.txt"), "w",
         encoding="utf-8").write("\n".join(problems))


if __name__ == "__main__":
    main()