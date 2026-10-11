# A2 Key 與 108 課綱會考｜60 課互動英文教學

Cambridge **A2 Key Vocabulary List** 主題清單為詞彙骨架，搭配 **108 課綱國中會考** 文法單元的前置概念，
每一課都是完整故事（三段，逐句可點擊朗讀＋懸停文法解析）＋中文全文對照翻譯＋核心重點整理盒。

## 目錄結構

```
docs/                     產出成果：61 個 .html（index.html + 60 課）
build/                    產生器與檢查工具（改內容才用得到）
  template/               版面樣板（style/script 由此注入）
  lessons_part1..26.py     課程內容資料（LESSONS 清單）
  build.py                產生器：python build.py -> docs/
  verify_all.ps1          一次跑完 10 項檢查
source/                   詞彙來源（Cambridge PDF 與純文字版）
```

## 直接看課

`docs/` 是純靜態 HTML，沒有任何外部相依（樣式、腳本、TTS 都在頁內），
下載後直接用瀏覽器開啟 `docs/index.html` 即可，不需要 Python。

在線閱讀則把本 repo 開 GitHub Pages，來源分支選 `main`、資料夾選 `/docs`。

## 改內容後重新產生

```bash
cd build
python build.py          # 產生 62 個 HTML 到 ../docs
./verify_all.ps1          # 14 項檢查全過才算完成
```

`verify_all.ps1` 需要 PowerShell。若環境沒有 PowerShell，改用 Python 版：

```bash
python verify_all.py      # 同樣的 14 項檢查，產出相同結果
```

### `verify_all.ps1` 十四項檢查

| # | 檢查 | 內容 |
|---|------|------|
| 1 | BUILD | 60 課可由 26 個模組組裝 |
| 2 | MODULE | 每個模組可匯入、課次順序正確 |
| 3 | AUDIT | A2 Key 25 主題 + 會考 67 考點全涵蓋且可點擊 |
| 4 | VOCAB | 每課宣告的主題詞確實出現在故事中 |
| 5 | FUNCTIONAL | `node verify.js`：TTS 陣列、彈窗、點擊、引用皆可執行 |
| 6 | SIMPLIFIED | 無簡體字（掃描原始碼 + 產出 HTML） |
| 7 | QA | 段落／句型／彈窗結構 |
| 8 | LINKS | 內部連結無斷鏈 |
| 9 | CLAIMS | 跨課引用、動詞三態、引號字元 |
| 10 | TOPICS | 「A2 Key『X』主題」比對官方 25 個主題表 |
| 11 | TYPING WIRING | `python qa_typing.py`：60 頁的打字練習面板、監聽、句庫都正確 |
| 12 | TYPING BEHAVIOUR | `node test_typing.js`：按空白鍵唸單字、整句完成換下一句等互動規則 |
| 13 | RATE PRESETS | `node test_rate.js`：慢／正常／快三個語速預設，並確認朗讀真的套用 |
| 14 | READING PAGE | `node test_reading.js`：KET 閱讀練習頁的結構、AI 標注與出題流程 |

### 內容層檢查（結構之外）

第 6 項的 `scan_s2t.py` 是 `scan_s2t.ps1` 的 Python 版（同樣呼叫 Windows NLS 的
zh-TW 簡繁對應，邏輯相同）。

`qa_content.py` 另外從**內容面**檢查每課的解析面板，找出只驗結構抓不到的問題：

```bash
python qa_content.py     # 結果寫入 audit_findings.txt
python show.py 7 pop raw # 看第 7 課每句的解析原始碼（meta/pop/sum/tr）
```

它會檢查：每句標示詞數量（SCHEMA 規定 2–4 個）、每句解析點數量（2–3 個）、
三張重點卡的條目數（4／5／3）、結尾標點、彎引號與簡體字、多餘空白。
已知的良性偏離：第 2、3 課的「詞彙辨析」卡有 4 條（規格為 3）。

## KET 閱讀理解練習（`docs/reading.html`）

每課頁首控制列有一個 **📖 KET 閱讀練習** 按鈕，`target="_blank"` **開新視窗**獨立開啟。
排版、配色、圓角、按鈕、header 結構都沿用 60 課的同一套設計語言。

功能：輸入 Groq API Key → 選難度與題數 → AI 生成一篇中英對照的文章與考題 →
逐題作答（含選項逐一分析、詞彙音標、文法重點）→ 每一句可點擊發音 → 句旁的「🧩 拆解」
把句子一步步拆開講。語速控制與朗讀全文／停止和 60 課一致。

API Key 只存在使用者自己的瀏覽器（localStorage）；按「拆解」時才會呼叫 Groq，生成後快取。

作答後會直接在選項上標示對錯：**你選的那個答案不對時是紅框 ✗，正確答案是綠框 ✓**，
兩者都會鎖定不可再改。這需要 `answer()` 把題目卡定位在 `#questions` 裡 ——
頁面上還有 API Key 卡、`#articleCard`、`#scoreCard` 也都帶 `.card` 類別，
若用 `document.querySelectorAll('.card')[qi]` 會抓到設定卡而不是題目卡，
迴圈裡找不到 `.option`，紅綠框就永遠不會出現。`test_reading.js` 有針對這點的回歸測試。

⚠️ **文章、考題、音標、文法拆解全部由 AI 即時生成，未經人工檢核。**
頁面頂部、每題解析、拆解彈窗、頁尾都有標示。它不應被當成審定教材使用
——這也正是 `qa_content.py` 當初從 60 課裡修掉的那類內容。

## 朗讀語速

每課頁首與閱讀頁都有 **⚡ 朗讀語速** 滑桿，可在 **0.5x – 1.5x** 之間自由拖曳
（每格 0.1x），預設 0.9x。四種朗讀（點句子、朗讀整段、點單字、打字練習的單字發音）
都用同一組設定，超出範圍的值會被夾在 0.5–1.5 之間。

滑桿與端點標籤包在 `.rate-wrap` 直向容器裡 —— `.control-group` 是橫向 flex，
不包起來的話三個元素會被並排擠在一起。

注意：60 課的 `:root` **沒有定義 `--teal`**（`build.py` 的 `EXTRA_CSS` 直接寫色碼），
所以滑桿用字面值 `#0f766e`，寫 `var(--teal)` 會失效並掉回瀏覽器預設藍色。

## 打字練習

每課頁首的控制列有一個 **⌨️ 開啟打字練習** 按鈕，預設收起（列印時也會隱藏），
展開後：

- 打完一個單字按 <kbd>空白鍵</kbd> → 唸出那個單字的發音
- 整句打完再按一次 <kbd>空白鍵</kbd> → 輸入框清空、跳到下一句開頭
- 句庫與畫面上顯示的英文**完全一致**（由 `html` 推導，點擊朗讀與顯示同源）

比對採**寬鬆比對**：忽略大小寫、標點與多餘空白，只比對英文單字與順序，
所以 `I couldn't open` 打成 `i couldnt open` 一樣算完成。

## 目錄結構（補充）

```
docs/reading.html        獨立的 KET 閱讀理解練習頁（AI 出題，開新視窗）
build/reading_src.html   上一頁的來源；build.py 原樣輸出，所以它是自給自足的
build/reading_tool.py    讀取來源並交給 build.py
```

## 內容資料格式

見 `build/SCHEMA.md`。每課一個 dict：
`file / doctitle / title_cn / subtitle / story_title / topic / grammar /`
`translation[3] / bridges[2] / paragraphs[3][3] / sum_intro / sum_titles[3] / summary[3]`；
每個句子是 `{text, html, pop}`，`text` 由 `html` 自動推導，確保顯示與朗讀永遠一致。

## 文字規範

- 撇號一律 U+0027（`don't`），不使用彎引號；`build.py` 會強制正規化。
- 中文一律正體；`scan_s2t.ps1` 會阻擋簡體字。
（「台」保留於月台、舞台；「症」保留於症狀 — 兩者本來就是正字，轉換會變成錯字。）

## 授權與來源

詞彙表來源：[Cambridge English, A2 Key / A2 Key for Schools Vocabulary List](https://www.cambridgeenglish.org/Images/506886-a2-key-2020-vocabulary-list.pdf)
（原檔存於 `source/`）。文法範圍依據台灣 108 課綱國中會考。
英文例句、故事與中文解析為本專案原創。
