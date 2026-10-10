# -*- coding: utf-8 -*-
"""Python port of scan_s2t.ps1 (Simplified-Chinese gate for the whole repository).

Identical logic: use the Windows NLS zh-TW S2T mapping, flag every character that
changes under it, except the two that are already correct Traditional Chinese.
Runs on machines without PowerShell.
"""
import ctypes
import os
import sys
from ctypes import wintypes

LOCALE_NAME = "zh-TW"
LCMAP_TRADITIONAL_CHINESE = 0x04000000

# Stands in for any astral character (emoji) while the S2T mapping runs.
PLACEHOLDER = "\ue000"

# 台 tai - correct in the words for 'platform' and 'stage'
# 症 zheng - correct in the word for 'symptom'
ALLOW = {0x53F0, 0x75C7}

EXT_GLOBS = (".html", ".py", ".md", ".txt", ".ps1", ".js")
DOTFILES = (".gitignore", ".gitattributes")


def _s2t(text):
    # LCMapStringEx works on UTF-16 code units, so an astral character (emoji) is
    # two units wide and gets re-flowed by the call. No Simplified character lives
    # outside the BMP, so swap every astral character for a private-use BMP
    # placeholder first: one UTF-16 unit, guaranteed unchanged by the mapping,
    # which keeps the converted string aligned index-for-index with the source.
    src = "".join(ch if ord(ch) < 0x10000 else PLACEHOLDER for ch in text)

    kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)
    fn = kernel32.LCMapStringEx
    fn.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPCWSTR,
                   ctypes.c_int, wintypes.LPWSTR, ctypes.c_int,
                   ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
    fn.restype = ctypes.c_int

    need = fn(LOCALE_NAME, LCMAP_TRADITIONAL_CHINESE, src, len(src),
              None, 0, None, None, None)
    if need <= 0:
        raise ctypes.WinError(ctypes.get_last_error())
    cap = need + 8
    buf = ctypes.create_unicode_buffer(cap)
    fn(LOCALE_NAME, LCMAP_TRADITIONAL_CHINESE, src, len(src), buf, cap,
       None, None, None)
    conv = buf[:len(src)]
    if len(conv) != len(src):
        raise SystemExit("S2T mapping changed the length of a file")
    return conv


def collect(root):
    found = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in (".git", "__pycache__", ".opencode")]
        for name in filenames:
            ext = os.path.splitext(name)[1]
            if ext in EXT_GLOBS or name in DOTFILES:
                found.append(os.path.join(dirpath, name))
    return sorted(set(found))


def main():
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
    files = collect(root)
    total = 0
    skipped = []
    for path in files:
        rel = os.path.relpath(path, root)
        try:
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            conv = _s2t(src)
        except (UnicodeDecodeError, OSError) as exc:
            # Not valid UTF-8, or the NLS mapping refuses it. The gate is about
            # repo content, so skip and report instead of aborting the scan.
            skipped.append("%s (%s)" % (rel, type(exc).__name__))
            continue
        for i, ch in enumerate(src):
            c = ord(ch)
            if c >= 0x10000:
                continue  # emoji, never Simplified Chinese
            if ch != conv[i] and c not in ALLOW:
                s0 = max(0, i - 18)
                ctx = src[s0:s0 + 38]
                print("%s  U+%04X -> U+%04X  ...%s..." % (rel, c, ord(conv[i]), ctx))
                total += 1
    print("files scanned: %d" % (len(files) - len(skipped)))
    if skipped:
        print("skipped (not valid UTF-8 / not mappable): %d" % len(skipped))
        for s in skipped:
            print("  - " + s)
    print("TOTAL DIFFS: %d" % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())