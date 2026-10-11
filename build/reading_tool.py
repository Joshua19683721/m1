# -*- coding: utf-8 -*-
"""KET 閱讀理解練習（獨立頁 docs/reading.html）。

由 build.py 讀取本檔、原樣輸出，所以內容是一個完整、自給自足的 HTML。
刻意不引用 template/gemini-code.html：這一頁要能單獨在新視窗開啟，
不依賴 60 課的任何資產。排版與配色沿用同一套設計語言（同字體、圓角、
陰影、按鈕、badge、header 結構），所以看起來像同一個系列。

⚠️ 文章、考題、音標、文法拆解全部由 Groq AI 即時生成，未經人工檢核。
   API Key 只存在使用者自己的瀏覽器 localStorage。
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "reading_src.html")


def build():
    with open(SRC, encoding="utf-8") as fh:
        return fh.read()
