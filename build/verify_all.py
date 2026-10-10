# -*- coding: utf-8 -*-
"""Run every content check in one go and write a readable report.

PowerShell is unavailable in this environment, so this mirrors verify_all.ps1:
1 BUILD    2 MODULE  3 AUDIT   4 VOCAB    5 FUNCTIONAL (node)
6 SIMPLIFIED (scan_s2t.py, Python port of scan_s2t.ps1)
7 QA       8 LINKS    9 CLAIMS  10 TOPICS

    python verify_all.py
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)

STEPS = [
    ("1.  BUILD", "build.py"),
    ("2.  MODULE", "modcheck.py"),
    ("3.  AUDIT", "audit.py"),
    ("4.  VOCAB", "check_vocab2.py"),
    ("5.  FUNCTIONAL", "verify.js"),
    ("6.  SIMPLIFIED", "scan_s2t.py"),
    ("7.  QA", "qa_new.py"),
    ("8.  LINKS", "check_links.py"),
    ("9.  CLAIMS", "qa_claims.py"),
    ("10. TOPICS", "qa_topics.py"),
    ("11. TYPING WIRING", "qa_typing.py"),
    ("12. TYPING BEHAVIOUR", "test_typing.js"),
]

NODE = ["verify.js", "test_typing.js"]
results = []
for label, script in STEPS:
    if script in NODE:
        cmd = ["node", script]
    elif script == NODE:
        cmd = ["node", NODE]
    else:
        cmd = [sys.executable, script]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=600)
        out = (proc.stdout + proc.stderr).decode("utf-8", "replace")
        lines = [l for l in out.replace("\r", "").split("\n") if l.strip()]
        ok = proc.returncode == 0
        results.append((label, ok, lines))
    except Exception as exc:  # noqa: BLE001
        results.append((label, False, ["ERROR: %s" % exc]))

report = []
for label, ok, lines in results:
    report.append("=" * 70)
    report.append("%s   %s" % (label, "PASS" if ok else "FAIL"))
    report.append("-" * 70)
    report.extend(lines[-8:])
    report.append("")

report.append("#" * 70)
failed = [l for l, ok, _ in results if not ok]
report.append("SUMMARY: %d/%d checks passed" % (len(results) - len(failed),
                                                len(results)))
if failed:
    report.append("FAILED: " + ", ".join(failed))
    text = "\n".join(report)
    print(text)
    sys.exit(1)
report.append("ALL CHECKS PASS")
print("\n".join(report))
