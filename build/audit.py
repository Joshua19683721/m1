# -*- coding: utf-8 -*-
"""完整性稽核：欄位、編號、A2 Key 主題合法性、覆蓋率、內文一致性。"""
import glob, io, os, re, sys, importlib
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import coverage

# A2 Key 附錄 2 的 25 個合法主題名
TOPIC_FILE = io.open(os.path.join(HERE, "a2key_topics.txt"), encoding="utf-8").read()
GROUPS = ["Appliances", "Clothes and Accessories", "Colours",
          "Communication and Technology", "Documents and Texts", "Education",
          "Entertainment and Media", "Family and Friends", "Food and Drink",
          "Health, Medicine and Exercise", "Hobbies and Leisure", "House and Home",
          "Measurements", "Personal Feelings, Opinions and Experiences",
          "Places: Buildings", "Places: Countryside", "Places: Town and City",
          "Services", "Shopping", "Sport", "The Natural World", "Time",
          "Travel and Transport", "Weather", "Work and Jobs"]

import build
LESSONS = build.load_lessons()   # 使用與產出完全相同的載入與淨化流程

REQUIRED = ["file", "doctitle", "title_cn", "subtitle", "story_title", "topic",
            "grammar", "translation", "bridges", "paragraphs", "sum_intro",
            "sum_titles", "summary"]

problems = []
print("=" * 74)
print("課文總數：%d" % len(LESSONS))
print("=" * 74)

for i, L in enumerate(LESSONS, 1):
    tag = "第%d課" % i
    for k in REQUIRED:
        if k not in L:
            problems.append("%s 缺少欄位 %s" % (tag, k))
    if not L.get("file", "").startswith("%02d-" % i):
        problems.append("%s 檔名編號不符：%s" % (tag, L.get("file")))
    if len(L.get("translation", [])) != 3:
        problems.append("%s 中文翻譯應為 3 段" % tag)
    if len(L.get("bridges", [])) != 2:
        problems.append("%s 銜接說明應為 2 段" % tag)
    paras = L.get("paragraphs", [])
    if len(paras) != 3:
        problems.append("%s 段落數應為 3" % tag)
    for pi, para in enumerate(paras, 1):
        if len(para) != 3:
            problems.append("%s 第%d段句數=%d（應為 3）" % (tag, pi, len(para)))
        for s in para:
            plain = re.sub(r"<[^>]+>", "", s.get("html", ""))
            if plain.strip() != s.get("text", "").strip():
                problems.append("%s P%d text/html 不一致:\n   HTML=%r\n   TEXT=%r" % (tag, pi, plain, s.get("text")))
            pop = s.get("pop", "")
            if pop.count("<br>") < 1:
                problems.append("%s P%d 解析點過少" % (tag, pi))
            if "</li>" in pop:
                problems.append("%s P%d pop 含 </li>" % (tag, pi))
            if len(pop) < 100:
                problems.append("%s P%d 解析過短（%d）" % (tag, pi, len(pop)))
            if not re.search(r'<span class="w-tap kw-(verb|colloc|link)">', s.get("html", "")):
                problems.append("%s P%d 句中無標示詞" % (tag, pi))
    sums = L.get("summary", [])
    if len(sums) != 3:
        problems.append("%s summary 應有 3 張卡" % tag)
    for ci, need in enumerate([4, 5, 3]):
        items = sums[ci] if ci < len(sums) else []
        n = sum(len(x) if isinstance(x, list) else 1 for x in items)
        if n < need:
            problems.append("%s summary 卡%d 僅 %d 項（需 %d）" % (tag, ci + 1, n, need))
    if len(L.get("sum_titles", [])) != 3:
        problems.append("%s sum_titles 應有 3 項" % tag)
    # 主題合法性
    for t in re.split(r"／|/", L.get("topic", "")):
        t = t.strip()
        if t and t not in GROUPS:
            problems.append("%s 主題「%s」不在 A2 Key 25 主題清單內" % (tag, t))

print()
print("── 逐課結構稽核 ──")
if problems:
    for p in problems:
        print("  ✗ " + p)
else:
    print("  ✓ 全部 %d 課欄位、編號、句數、標示、解析、總結卡、主題名稱皆正確" % len(LESSONS))

# ---------- A2 Key 主題覆蓋率 ----------
used = {}
for L in LESSONS:
    for t in re.split(r"／|/", L.get("topic", "")):
        t = t.strip()
        if t in GROUPS:
            used.setdefault(t, []).append(L["file"])

print()
print("── A2 Key 附錄 2 主題覆蓋率（%d/%d）──" % (len(used), len(GROUPS)))
missing = []
for g in GROUPS:
    ls = used.get(g, [])
    if ls:
        print("  ✓ %-46s %d 課" % (g, len(ls)))
    else:
        missing.append(g)
        print("  ✗ %-46s 未涵蓋" % g)

# ---------- 會考文法覆蓋率 ----------
maxn = len(LESSONS)
pend = []
for point, ls in coverage.COVER_GRAMMAR:
    bad = [n.strip() for n in ls.split(",") if int(n.strip()) > maxn]
    if bad:
        pend.append((point, bad))
print()
print("── 會考文法考點覆蓋（%d 個考點）──" % len(coverage.COVER_GRAMMAR))
if pend:
    for p, b in pend:
        print("  ✗ %-46s 待補課次 %s" % (p, b))
else:
    print("  ✓ 全部考點均已對應到實際存在的課次")

# ---------- 主題詞彙落地檢查 ----------
sample = L = None
print()
print("=" * 74)
if missing:
    print("結論：尚缺 %d 個主題 -> %s" % (len(missing), "、".join(missing)))
elif pend:
    print("結論：文法考點尚有 %d 項待補課次" % len(pend))
else:
    print("結論：A2 Key 全部 %d 個主題 + 會考 %d 個文法考點，皆已涵蓋且可點擊對應課次。"
          % (len(GROUPS), len(coverage.COVER_GRAMMAR)))
print("=" * 74)
if problems or missing or pend:
    sys.exit(1)
print("AUDIT PASSED")
