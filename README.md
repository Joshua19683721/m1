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
python build.py          # 產生 61 個 HTML 到 ../docs
./verify_all.ps1          # 10 項檢查全過才算完成
```

### `verify_all.ps1` 十項檢查

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
