# -*- coding: utf-8 -*-
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

TEMPLATE = os.path.join(HERE, "template", "gemini-code.html")
OUTDIR   = os.path.abspath(os.path.join(HERE, os.pardir, "docs"))

src    = open(TEMPLATE, encoding="utf-8").read()
STYLE  = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
SCRIPT = re.search(r"<script>(.*?)</script>", src, re.S).group(1)

CN = ["一", "二", "三"]
Q  = chr(39)




EXTRA_CSS = r'''/* ---- 附加樣式：列印版面 + 全文複習模式 ---- */
.tool-row{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:14px;}
.btn-tool{background:#0f766e;color:#fff;border:none;padding:7px 14px;border-radius:18px;
  cursor:pointer;font-size:0.85rem;}
.btn-tool:hover{background:#115e59;}
.btn-tool.ghost{background:#fff;color:#0f766e;border:1px solid #99f6e4;}
body.review .sentence-grammar-pop{display:block;}
body.review .sentence-block{background:#f0f9ff;}

@media print {
  @page { margin: 14mm; }
  body { background:#fff; padding:0; font-size: 11.5pt; line-height:1.6; }
  .container { max-width: 100%; }
  .audio-panel, .legend-bar, .tool-row, .btn-speak,
  #backIndex { display:none !important; }
  header { box-shadow:none; border-top:3px solid #1e3a8a; padding:12px; }
  .story-card, .summary-card { box-shadow:none; border:1px solid #cbd5e1;
    break-inside:avoid; page-break-inside:avoid; margin-bottom:10px; }
  .sentence-block { break-inside:avoid; page-break-inside:avoid; background:#fff; }
  .translation-card { border-color:#86efac; }
  .summary-grid { grid-template-columns:1fr; }
  a[href]:after { content:""; }
  .w-tap { background:none !important; font-weight:600; }
}
'''


def flat(x):
    """Accept a list of <li> strings, or a list of such lists."""
    out = []
    for it in x:
        if isinstance(it, list):
            out.extend(flat(it))
        else:
            out.append(it)
    return out



IDX_JS = r'''
  function filterLessons() {
    var q = (document.getElementById('idxSearch').value || '').toLowerCase().trim();
    var cards = document.querySelectorAll('.idx-card');
    var secs = document.querySelectorAll('.idx-section');
    for (var i = 0; i < cards.length; i++) {
      var hit = !q || cards[i].textContent.toLowerCase().indexOf(q) !== -1;
      cards[i].classList.toggle('hidden', !hit);
    }
    for (var j = 0; j < secs.length; j++) {
      var any = secs[j].querySelector('.idx-card:not(.hidden)');
      secs[j].classList.toggle('hidden', !any);
    }
    var n = document.querySelectorAll('.idx-card:not(.hidden)').length;
    var h = document.getElementById('idxCount');
    if (h) { h.textContent = n; }
  }

'''

EXTRA_JS = r'''  /* ---- 列印與複習模式 ---- */
  function toggleReview() {
    document.body.classList.toggle("review");
    var b = document.getElementById('btnReview');
    if (b) {
      b.textContent = document.body.classList.contains("review")
        ? "\u2500\u2576 \u6536\u8d77\u5168\u90e8\u89e3\u6790" : "\u25bc \u5c55\u958b\u5168\u90e8\u89e3\u6790";
    }
  }
  function printPage() { window.print(); }
'''


def clean_pop(s):
    """Grammar popups are plain <br>-separated text, never list items."""
    return s.replace("</li>", "").replace("\n", " ").strip()


def jsq(s):
    """Escape a sentence for a single-quoted JS string inside a double-quoted HTML attribute."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


BLOCK_OPEN = (
    '      <div class="sentence-block" onclick="speakText('
    "this.querySelector('.sentence-text').innerText)\">\n"
)

FOOTER = """  <div class="summary-card" style="margin-top:25px;">
    <h2 class="section-title">📚 資料來源與使用說明</h2>
    <ul class="summary-list" style="color:#475569;">
      <li><b>詞彙來源：</b>Cambridge English, <i>A2 Key / A2 Key for Schools Vocabulary List</i>（對應的版本，詳附錄 2 Topic Lists）。本課目標詞彙均取自該清單之主題分組。
        <a href="https://www.cambridgeenglish.org/Images/506886-a2-key-2020-vocabulary-list.pdf" target="_blank" style="color:var(--primary-light);">[下載原始 PDF]</a></li>
      <li><b>文法維度：</b>對照 108 課綱國中英文程綱內容，聚焦國中會考英語科高頻句型、比較級與情態動詞等測驗命題原則。</li>
      <li><b>文件結構：</b>沿用相同模板：懸停解讀、句中精準解說、Web Speech API 語音朗讀功能。</li>
      <li><b>使用方式：</b>使用已設定 Web Speech API 的瀏覽器開啟本檔案，點擊任一句子即可進行語音朗讀與對應發音示範。</li>
    </ul>
    <div style="margin-top:15px;"><a href="index.html" style="color:var(--primary);font-weight:bold;">⬅ 回到總結果索引</a></div>
  </div>
</div>
"""

IDX_HEAD = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>A2 Key 與 108 課綱會考英文：__N__ 課索引</title>
  <style>__STYLE__
  .idx-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:18px;margin-top:20px;}
  .idx-card{display:flex;gap:15px;background:#fff;border-radius:14px;padding:20px;text-decoration:none;box-shadow:0 4px 15px rgba(0,0,0,.06);border-left:5px solid var(--primary);transition:all .25s ease;}
  .idx-card:hover{transform:translateY(-3px);box-shadow:0 8px 22px rgba(0,0,0,.12);border-left-color:var(--accent-orange);}
  .idx-no{font-size:2.2rem;font-weight:800;color:#cbd5e1;line-height:1;}
  .idx-body h3{margin:0 0 4px 0;color:var(--primary);font-size:1.1rem;}
  .idx-en{color:var(--text-muted);font-size:.9rem;margin-bottom:8px;font-style:italic;}
  .idx-meta{margin-top:6px;font-size:.82rem;color:#334155;}
  .cov-table{width:100%;border-collapse:collapse;font-size:.88rem;}
  .cov-table td{padding:7px 10px;border-bottom:1px solid #e2e8f0;vertical-align:top;}
  .cov-table tr:nth-child(even){background:#f8fafc;}
  .cov-topic{font-weight:600;color:#0f172a;width:44%;}
  .cov-point{font-weight:600;color:#0f172a;width:52%;}
  .cov-pill{display:inline-block;min-width:26px;text-align:center;margin:2px 3px 2px 0;padding:2px 7px;
    border-radius:12px;background:#1e3a8a;color:#fff;font-size:.78rem;text-decoration:none;font-weight:600;}
  .cov-pill:hover{background:#f59e0b;color:#fff;}
  .idx-section{margin:26px 0 12px;padding-bottom:8px;border-bottom:2px solid #1e3a8a;
    display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;}
  .idx-section h2{margin:0;color:#1e3a8a;font-size:1.25rem;}
  .idx-section span{color:#64748b;font-size:.86rem;}
  .idx-tools{position:sticky;top:0;z-index:5;background:#f8fafc;padding:12px 0 6px;}
  .idx-tools input{width:100%;max-width:380px;padding:9px 14px;border-radius:20px;
    border:1px solid #cbd5e1;font-size:.95rem;outline:none;}
  .idx-tools input:focus{border-color:#3b82f6;box-shadow:0 0 0 3px rgba(59,130,246,.15);}
  .idx-tools .hint{display:block;color:#64748b;font-size:.82rem;margin-top:6px;}
  .hidden{display:none !important;}

  .cov-pending{background:#cbd5e1;color:#64748b;}
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1>📚 A2 Key 與 108 課綱會考英文：__N__ 課</h1>
    <div class="sub-title">滑鼠解讀・句中精準解析・中文全文翻譯・可朗讀的單字與句型</div>
  </header>
  <div class="summary-card">
    <p style="color:#475569;margin-top:0;">本設計以 <b>Cambridge A2 Key Vocabulary List</b> 主題清單為詞彙骨架，搭配 <b>108 課綱國中會考</b> 文法單元的命題前提；每課一篇完整故事（三段・逐句解讀）互為體系化清卡，前30課為基礎謚法，後30課為延美句型與議題融入。</p>
    <div class="idx-tools">
      <input id="idxSearch" type="search" placeholder="搜尋課次、主題或文法點（例：露營、A2 Key、if）..." oninput="filterLessons()">
      <span class="hint">搜尋無限制。按「清除」顯示全部。</span>
    </div>
<div class="idx-grid">
"""

IDX_FOOT = """    </div>
  </div>
  <div class="summary-card" style="margin-top:25px;">
    <h2 class="section-title">📚 資料來源</h2>
    <ul class="summary-list" style="color:#475569;">
      <li><b>詞彙來源：</b>Cambridge English, <i>A2 Key / A2 Key for Schools Vocabulary List</i>（對應的版本），詳附錄 2 Topic Lists：Education、Food and Drink、Health Medicine and Exercise、Sport、Shopping、Weather、The Natural World、Hobbies and Leisure、Entertainment and Media、Communication and Technology、Work and Jobs、Travel and Transport、Places、Time。</li>
      <li><b>文法維度：</b>108 課綱國中英文程綱內容，對應國中段考與國中會考英語的常見測驗型態，可作為教學時的編排與複習依據。</li>
      <li><b>下載：</b><a href="https://www.cambridgeenglish.org/Images/506886-a2-key-2020-vocabulary-list.pdf" target="_blank" style="color:var(--primary-light);">A2 Key Vocabulary List (PDF)</a></li>
    </ul>
  </div>
</div>
</body>
</html>
"""


def render(L, idx):
    t = L
    P = []
    P.append('<!DOCTYPE html>\n<html lang="zh-TW">\n<head>\n'
             '  <meta charset="UTF-8">\n'
             '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
             '  <title>' + t["doctitle"] + '</title>\n'
             '  <style>' + STYLE + EXTRA_CSS + '  </style>\n</head>\n<body>\n')

    P.append('<div class="container">\n  <header>\n'
             '    <h1>📘 第 ' + str(idx) + ' 課｜' + t["title_cn"] + '</h1>\n'
             '    <div class="sub-title">' + t["subtitle"] +
             '｜滑鼠移至句子看文法解說・點擊單字聽標準發音・附中文全文翻譯</div>\n'
             '    <div class="audio-panel">\n'
             '      <div class="control-group">\n'
             '        <label for="voiceSelect"><b>🎙️ 發音語音引擎:</b></label>\n'
             '        <select id="voiceSelect"></select>\n'
             '      </div>\n'
             '      <div class="control-group">\n'
             '        <label for="rateRange"><b>⚡ 朗讀語速:</b> <span id="rateVal">0.8x</span></label>\n'
             '        <input type="range" id="rateRange" min="0.5" max="1.5" step="0.1" value="0.8" oninput="updateRateLabel(this.value)">\n'
             '      </div>\n'
             '    </div>\n'
             '    <div class="legend-bar">\n'
             '      <div class="legend-item"><span class="dot" style="background:#10b981;"></span> 核心動詞／動詞片語</div>\n'
             '      <div class="legend-item"><span class="dot" style="background:#f59e0b;"></span> 高頻搭配詞 (Collocation)</div>\n'
             '      <div class="legend-item"><span class="dot" style="background:#8b5cf6;"></span> 轉折／承接副詞 (Transition)</div>\n'
             '      <div class="legend-item">💡 <b>滑鼠移至句子上方</b>：即可顯示文法結構解析</div>\n'
             '    </div>\n'
             '    <div class="tool-row">\n'
             '      <button class="btn-tool" id="btnReview" onclick="toggleReview()">\u25bc \u5c55\u958b\u5168\u90e8\u89e3\u6790</button>\n'
             '      <button class="btn-tool ghost" onclick="printPage()">\U0001F5A8 \u5217\u5370\u672c\u7bc0</button>\n'
             '    </div>\n  </header>\n')

    P.append('  <div class="story-card">\n'
             '    <h2 class="section-title">📖 ' + t["story_title"] + '</h2>\n'
             '    <div style="margin-bottom:18px;font-size:0.9rem;">\n'
             '      <span class="badge badge-vocab">A2 Key 主題</span> ' + t["topic"] +
             ' &nbsp;｜&nbsp;\n'
             '      <span class="badge badge-grammar">108 課綱會考</span> ' + t["grammar"] + '\n'
             '    </div>\n')

    tr = []
    for i, p in enumerate(t["translation"], 1):
        tr.append('        <div class="translation-p">\n          <b>【第' +
                  CN[i-1] + '段】</b> ' + p + '\n        </div>')
    P.append('    <div class="translation-card">\n'
             '      <h3>🇨🇳 故事中文全文對照翻譯 (Story Chinese Translation)</h3>\n'
             '      <div class="translation-content">\n' + "\n".join(tr) +
             '\n      </div>\n    </div>\n')

    for i, para in enumerate(t["paragraphs"], 1):
        if i > 1:
            P.append('    <div class="context-bridge">\n'
                     '      <strong>🌉 段落文意銜接（第' + CN[i-2] +
                     '段 ➔ 第' + CN[i-1] + '段）：</strong><br>\n'
                     '      【情境說明】' + t["bridges"][i-2] + '\n    </div>\n')
        P.append('    <!-- Paragraph ' + str(i) + ' -->\n')
        P.append('    <div class="paragraph-container">\n')
        for j, s in enumerate(para, 1):
            P.append('      <!-- Sentence ' + str(i) + '.' + str(j) + ' -->\n')
            P.append(BLOCK_OPEN)
            P.append('        <div class="sentence-text">\n          ' + s["html"] + '\n        </div>\n')
            P.append('        <div class="sentence-grammar-pop">\n'
                     '          <strong>🔍 文法與句法結構分析：</strong><br>\n'
                     '          ' + clean_pop(s["pop"]) + '\n        </div>\n      </div>\n')
        arr = ", ".join(Q + jsq(s["text"]) + Q for s in para)
        P.append('      <button class="btn-speak" onclick="speakParagraph([' + arr + '])">🔊 朗讀第' +
                 CN[i-1] + '段全文</button>\n')
        P.append('    </div>\n')

    P.append('  </div>\n')

    boxes = []
    boxes.append('      <div class="summary-box">\n'
                 '        <h3><span class="badge badge-grammar">文法句型</span> ' + t["sum_titles"][0] + '</h3>\n'
                 '        <ul class="summary-list">\n' + "\n".join(flat(t["summary"][0])) + '\n        </ul>\n      </div>')
    boxes.append('      <div class="summary-box" style="border-left-color: var(--accent-orange);">\n'
                 '        <h3><span class="badge badge-colloc">搭配詞</span> ' + t["sum_titles"][1] + '</h3>\n'
                 '        <ul class="summary-list">\n' + "\n".join(flat(t["summary"][1])) + '\n        </ul>\n      </div>')
    boxes.append('      <div class="summary-box" style="border-left-color: var(--accent-green);">\n'
                 '        <h3><span class="badge badge-vocab">詞彙辨析</span> ' + t["sum_titles"][2] + '</h3>\n'
                 '        <ul class="summary-list">\n' + "\n".join(flat(t["summary"][2])) + '\n        </ul>\n      </div>')

    P.append('  <div class="summary-card">\n'
             '    <h2 class="section-title">📝 第 ' + str(idx) + ' 課 核心重點解析總整理 (Mastery Summary)</h2>\n'
             '    <p style="color: var(--text-muted); font-size: 0.95rem;">' + t["sum_intro"] + '</p>\n'
             '    <div class="summary-grid">\n' + "\n\n".join(boxes) + '\n    </div>\n  </div>\n')

    P.append(FOOTER)
    P.append("<script>" + SCRIPT + EXTRA_JS + "</script>\n\n</body>\n</html>\n")
    return "".join(P)


def build_index(lessons):
    import coverage
    coverage.LESSON_FILES = [L["file"] for L in lessons]
    SECTIONS = [(1, 10, '基礎篇｜段考常見句型'),
                (11, 30, '主題詞彙｜中級句型深化'),
                (31, 60, '進階句型、寫作升級與議題融入')]
    cur = None
    cards = []
    for i, L in enumerate(lessons, 1):
        cards.append(
            '      <a class="idx-card" href="' + L["file"] + '">\n'
            '        <div class="idx-no">' + ("0" + str(i))[-2:] + '</div>\n'
            '        <div class="idx-body">\n'
            '          <h3>' + L["title_cn"] + '</h3>\n'
            '          <div class="idx-en">' + L["story_title"] + '</div>\n'
            '          <div class="idx-meta"><span class="badge badge-vocab">' + L["topic"] + '</span></div>\n'
            '          <div class="idx-meta"><span class="badge badge-grammar">' + L["grammar"] + '</span></div>\n'
            '        </div>\n      </a>')
        for lo, hi, label in SECTIONS:
            if lo <= i <= hi and cur != lo:
                cur = lo
                cards.append(
                    '      <div class="idx-section"><h2>' + label + '</h2><span>第 '
                    + str(lo) + chr(0x2013) + str(min(hi, len(lessons))) + ' 課（第 '
                    + str(hi - lo + 1) + ' 課）</span></div>')
                break
    body = IDX_HEAD + "\n".join(cards) + "\n" + coverage.cover_tables() + IDX_FOOT
    out = body.replace("__STYLE__", STYLE)
    out = out.replace("__N__", str(len(lessons)))
    return out.replace("</body>", "<script>" + IDX_JS + "</script>" + chr(10) + "</body>")



def load_lessons():
    """Discover content modules, apply the rendering contract, and return lessons in order."""
    import glob, importlib
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    def part_no(path):
        m = re.search(r"lessons_part(\d+)\.py$", os.path.basename(path))
        return int(m.group(1)) if m else 0

    # Normalise typographic quotation marks to the ASCII apostrophe (U+0027).
    # The whole corpus, the TTS arrays and the printed page must use one character,
    # otherwise words such as wasn't / anyone's render inconsistently.
    QUOTES = {0x2018: 0x27, 0x2019: 0x27, 0x02BC: 0x27, 0x201C: 0x27, 0x201D: 0x27}

    def dequote(v):
        if isinstance(v, str):
            for k, c in QUOTES.items():
                v = v.replace(chr(k), chr(c))
        elif isinstance(v, list):
            return [dequote(x) for x in v]
        elif isinstance(v, dict):
            return dict((k, dequote(x)) for k, x in v.items())
        return v

    lessons = []
    paths = sorted(glob.glob(os.path.join(here, "lessons_part*.py")), key=part_no)
    for path in paths:
        mod = importlib.import_module(os.path.splitext(os.path.basename(path))[0])
        for L in mod.LESSONS:
            L.update(dequote(dict(L)))
            for para in L.get("paragraphs", []):
                for s in para:
                    s["pop"] = clean_pop(s.get("pop", ""))
                    s["html"] = re.sub(r"\s+", " ", s.get("html", "")).strip()
                    # 顯示（html）是唯一真實來源；朗讀文字由它推導，確保點擊朗讀與顯示一致
                    s["text"] = re.sub(r"<[^>]+>", "", s["html"])
                    s["text"] = re.sub(r"\s+", " ", s["text"]).strip()
            for ci, card in enumerate(L.get("summary", [])):
                L["summary"][ci] = flat(card)
        lessons.extend(mod.LESSONS)
    files = [L["file"] for L in lessons]
    if len(files) != len(set(files)):
        dupes = sorted({f for f in files if files.count(f) > 1})
        raise SystemExit("duplicate lesson filenames: %s" % dupes)
    partial = os.environ.get("DSH_PARTIAL") == "1"
    for i, L in enumerate(lessons, 1):
        if not L["file"].startswith("%02d-" % i):
            msg = "lesson %d out of order: %s" % (i, L["file"])
            if partial:
                print("PARTIAL: " + msg)
            else:
                raise SystemExit(msg)
    return lessons


def main():
    import glob
    ALL = load_lessons()
    print("loaded %d lessons from %d modules" % (len(ALL), len(glob.glob(os.path.join(HERE, "lessons_part*.py")))))
    os.makedirs(OUTDIR, exist_ok=True)
    made = []
    p = os.path.join(OUTDIR, "index.html")
    open(p, "w", encoding="utf-8").write(build_index(ALL))
    made.append("index.html")
    for i, L in enumerate(ALL, 1):
        p = os.path.join(OUTDIR, L["file"])
        open(p, "w", encoding="utf-8").write(render(L, i))
        made.append(L["file"])
    print("BUILT %d files in %s" % (len(made), OUTDIR))
    for m in made:
        print("  - " + m)


if __name__ == "__main__":
    main()
