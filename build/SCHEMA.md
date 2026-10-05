# 課文內容模組規格書（LESSON MODULE SPEC）

## 你的任務
撰寫「A2 Key 詞彙 × 108 課綱國中會考」互動教學課文模組，輸出為 Python 資料檔。

## 必讀參考
1. `C:\Users\joshu\Downloads\mkes1-6\build\a2key_topics.txt` — Cambridge A2 Key 詞彙表附錄 2 的 25 個主題分組與全部詞彙。**你負責的主題詞彙必須全部取自此檔案**，不可自創。
2. `C:\Users\joshu\Downloads\mkes1-6\build\lessons_part1.py` — 既有成品範例，**格式、深度、語氣照它模仿**。

## 輸出檔案
指定路徑的 Python 檔案，內容為 `LESSONS = []` 後接多個 `LESSONS.append({...})`。

## 每課字典欄位（缺一不可，順序不拘）
```python
LESSONS.append({
 "file": "11-appliance-repair.html",      # 英文檔名，kebab-case，兩位數字前綴
 "doctitle": "第11課 家電故障：故事與文法懸停解析｜A2 Key × 108課綱國中會考",
 "title_cn": "家電故障",                    # 6~10 字中文標題
 "subtitle": "Appliances",                 # A2 Key 主題（英���，逗號分隔）
 "story_title": "The Washing Machine Broke Down",   # 英文故事名
 "topic": "Appliances",                   # 同 subtitle
 "grammar": "should/shouldn't、too...to、there be 句型",  # 會考文法（中文，2~3 項）
 "translation": ["中文譯段一", "中文譯段二", "中文譯段三"],
 "bridges": ["第一段→第二段的銜接說明（80~120字）", "第二段→第三段的銜接說明（80~120字）"],
 "paragraphs": [[句,句,句], [句,句,句], [句,句,句]],   # 恰好 3 段，每段恰好 3 句
 "sum_intro": "本課故事聚焦……（40~60字）",
 "sum_titles": ["三個 summary box 的小標", "第二個", "第三個"],
 "summary": [[4個 <li> 字串], [5個 <li> 字串], [3個 <li> 字串]],
})
```

## 每個「句」物件
```python
{"text":  "純文字英文句子，與 html 去除標籤後必須完全一致（含標點）。",
 "html":  '同一句，但用 <span class="w-tap kw-VERB|COLLOC|LINK">關鍵詞</span> 包住 2~4 個重點。',
 "pop":   '''1. <b>文法點標題：</b>說明文字。<br>
2. <b>文法點標題：</b>說明文字。<br>
3. <b>文法點標題：</b>說明文字。'''}
```

### 三色標示對應（legend 已定義）
- `kw-verb`（綠）＝ 核心動詞、動詞片語、文法關鍵字
- `kw-colloc`（橙）＝ 高頻搭配詞 collocation
- `kw-link`（紫）＝ 轉折／承接／時間副詞或片語

### pop 的寫作規範
- 每句 **2~3 條**編號要點，以 `<br>` 分隔，開頭固定為：
  `          <strong>🔍 文法與句法結構分析：</strong><br>`（由模板自動加，你只寫要點本體）
- **每條必須具體**，格式：`<b>規則名稱：</b> 中文解釋 + 英文例句`
- 陷阱用 `<span style="color:#dc2626;">⚠️ 陷阱：</span>` 標示，錯誤示範用 `<s>✗ 錯的</s>`、正確用 `<u>✓ 對的</u>`
- **禁止**在 pop 裡出現 `</li>`

### summary 三卡內容
1. 文法句型卡：**4 條**，每條涵蓋一個可遷移的句型規則，附例句與陷阱
2. 搭配詞卡：**5 條**，來自本課故事的高頻 collocation
3. 詞彙辨析卡：**3 條**，成組易混詞（如 advice/advise、speak/talk）

## 品質紅線（務必自查）
1. **英文程度**：A2 Key 水準（約國中畢業程度），每句 8~16 詞，句型簡短清楚。用字須自然、地道，不可生硬。
2. **文法正確性是第一位**。每條 pop 的規則必須 100% 正確。若拿不準寧可換一個確定正確的點。
3. `text` 與 `html` 去標籤後**必須逐字相同**（包含逗號、句號、大小寫、撇號）。
4. 撇號直接打 `'`，不要跳脫。
5. **只寫純繁體中文**，不要用任何 `\uXXXX` 跳脫（會出錯）。
6. 故事需有完整起承轉合，三段之間要能銜接，bridges 要呼應段落實際內容。
7. 每課 `sub`/`topic` 對應的 A2 Key 主題詞彙，請明確散佈在故事句子中（每個目標詞至少出現一次）。

## 交付前自檢（務必執行）
在 `C:\Users\joshu\Downloads\mkes1-6\build` 目錄執行：
```
python -c "import lessons_part7; print(len(lessons_part7.LESSONS))"
```
必須成功 import 且筆數正確（無語法錯誤）。若 `Lessons_Part_7` 內的名稱不同請自行對應。
