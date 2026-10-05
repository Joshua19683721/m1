
# ============================================================
# 涵蓋範圍對照表（A2 Key 25 個主題分組 + 108 課綱會考文法全範圍）
# ============================================================

COVER_TOPICS = [
    ("Appliances", "11"),
    ("Clothes and Accessories", "12"),
    ("Colours", "13"),
    ("Communication and Technology", "9"),
    ("Documents and Texts", "9, 30"),
    ("Education", "1, 23, 27"),
    ("Entertainment and Media", "8"),
    ("Family and Friends", "19"),
    ("Food and Drink", "2, 28"),
    ("Health, Medicine and Exercise", "5, 24"),
    ("Hobbies and Leisure", "7, 8, 29"),
    ("House and Home", "18, 24"),
    ("Measurements", "14"),
    ("Personal Feelings, Opinions and Experiences", "10, 20, 23, 25, 29"),
    ("Places: Buildings", "1, 21"),
    ("Places: Countryside", "7, 15, 26"),
    ("Places: Town and City", "2, 22, 26"),
    ("Services", "16"),
    ("Shopping", "2, 6"),
    ("Sport", "4, 25"),
    ("The Natural World", "7, 15"),
    ("Time", "3, 17"),
    ("Travel and Transport", "3"),
    ("Weather", "7"),
    ("Work and Jobs", "10"),
]

COVER_GRAMMAR = [
    ("名詞、冠詞與所有格", "2, 5, 6, 12, 18, 19"),
    ("代詞（人稱／物主／不定／疑問）", "6, 19, 28"),
    ("數量詞（many/much/a lot of/a few/a little/enough）", "6, 14, 18, 28"),
    ("介系詞（時間 in/on/at、地點 at/in/on/next to）", "1, 3, 15, 16, 17, 18, 21"),
    ("形容詞與副詞（位置、順序）", "4, 12, 13, 20, 25"),
    ("比較級與最高級", "4, 12, 14, 25"),
    ("比較結構 as...as / not as...as", "25"),
    ("一般現在式", "1, 17, 22"),
    ("現在進行式", "1, 7"),
    ("一般過去式（規則／不規則）", "2, 3, 6, 15"),
    ("過去進行式", "3, 7"),
    ("現在完成式（since/for/already/yet）", "8"),
    ("過去完成式", "3, 6"),
    ("未來式 will / be going to", "10, 17"),
    ("間接引語的時態一致", "30"),
    ("情態動詞 can/could/may/must/should/have to", "5, 6, 11, 21, 51"),
    ("動名詞與不定詞", "4, 8, 10, 20"),
    ("連綴動詞（be／get／make／keep＋形容詞）", "2, 3, 7, 10"),
    ("祈使句與建議句型", "16, 21, 23, 29"),
    ("建議句型 Let's / Why don't / How about", "23, 29"),
    ("間接敘述與間接問句", "1, 6, 9, 10, 30, 35"),
    ("條件句 if（第一類／第二類）", "7, 10, 29, 49"),
    ("限定關係子句 who/which/that", "1, 2, 21"),
    ("關係副詞 where/when/why", "26"),
    ("名詞性從句", "26"),
    ("並列句與連接詞（and/but/or/so/because）", "1, 2, 9, 40"),
    ("讓步與轉折（although/however/while）", "9, 10, 49"),
    ("目的與結果 so that/in order that/too...to/so...that", "11, 27, 41"),
    ("使役動詞 make/have/let sb do", "24"),
    ("感官動詞 see/hear/smell sb do/doing", "24"),
    ("強調句 It is...that", "30, 47"),
    ("反意疑問句", "23, 30"),
    ("附加問句", "23"),
    ("願望句 wish / if I were", "29"),
    ("被動語態", "3"),
    ("主謂一致", "1, 11, 21, 45"),
    ("否定句與疑問句", "23, 28"),
    ("倒裝句（Not only...but also／Here comes／Only then）", "31"),
    ("分詞片語（Having done／Walking／Being）", "32"),
    ("所有格的兩種表示法（N's／of N、複合名詞）", "33"),
    ("五大句型與句型擴展", "34"),
    ("間接引語完整規則與報導動詞選擇", "35"),
    ("完成式被動與情態動詞完成式 should have done", "36"),
    ("比較的省略與倍數（twice as...as／no more than）", "37"),
    ("不定代詞複合詞（some-／any-／no-／every-）", "38"),
    ("替代與省略（one／ones／so／there／such）", "39"),
    ("連詞總整理（unless／until／as soon as／even if）", "40"),
    ("so that／in order to／so as to 的完整家族", "41"),
    ("形容詞語序（意見／大小／年齡／形狀／顏色／產地）", "42"),
    ("會考標點符號規範", "43"),
    ("too／enough／so...that 三種句型互轉", "44"),
    ("主謂一致與數的處理", "45"),
    ("懸空修飾語（Dangling Modifiers）的辨識與修正", "46"),
    ("強調句 It is...that 與 What...is 的比較", "47"),
    ("立場表達（In my opinion／It seems to me）", "48"),
    ("進階條件連接詞（provided that／as long as／otherwise）", "49"),
    ("摘要改寫（paraphrase）技巧", "50"),
    ("提供建議的情態動詞句型", "51"),
    ("科技倫理的論述句型（because／so 的因果與讓步）", "52"),
    ("環境議題的描述與建議句型", "53"),
    ("天氣預報與氣候描述句型", "54"),
    ("邀請、接受與感謝句型", "55"),
    ("消息來源與可信度判讀", "56"),
    ("健康建議與防護句型", "57"),
    ("營養標示的比較判讀", "58"),
    ("勞動權益與職業探索", "59"),
    ("反霸凌與求助句型", "60"),
]


LESSON_FILES = []


def pills(ls):
    """Render lesson-number links, tolerating lessons that are not generated yet."""
    out = []
    for n in [x.strip() for x in ls.split(",")]:
        i = int(n)
        if 1 <= i <= len(LESSON_FILES):
            out.append('<a class="cov-pill" href="%s">%s</a>' % (LESSON_FILES[i - 1], n))
        else:
            out.append('<span class="cov-pill cov-pending">%s</span>' % n)
    return "".join(out)


def cover_tables():
    t1 = []
    for topic, ls in COVER_TOPICS:
        nums = pills(ls)
        t1.append("      <tr><td class=\"cov-topic\">%s</td><td>%s</td></tr>" % (topic, nums))

    t2 = []
    for point, ls in COVER_GRAMMAR:
        nums = pills(ls)
        t2.append("      <tr><td class=\"cov-point\">%s</td><td>%s</td></tr>" % (point, nums))

    return (
        '  <div class="summary-card" style="margin-top:25px;">\n'
        '    <h2 class="section-title">📗 涵蓋範圍對照表（一）A2 Key 詞彙表附錄 2 全部 25 個主題分組</h2>\n'
        '    <p style="color:#475569;font-size:0.92rem;">下列為 Cambridge A2 Key / A2 Key for Schools Vocabulary List '
        '附錄 2 的 <b>全部 25 個 Topic Lists</b>，每個主題皆已指定對應課次，無遺漏。</p>\n'
        '    <table class="cov-table">\n      <tbody>\n' + "\n".join(t1) + '\n      </tbody>\n    </table>\n'
        '  </div>\n\n'
        '  <div class="summary-card" style="margin-top:25px;">\n'
        '    <h2 class="section-title">📘 涵蓋範圍對照表（二）108 課綱國中會考文法全範圍</h2>\n'
        '    <p style="color:#475569;font-size:0.92rem;">依國中九年一貫英語學習內容之文法與句型範圍，'
        '共歸納 <b>%d 個考點</b>，每個考點皆可由對應課次的「核心重點解析總整理」複習。</p>\n'
        '    <table class="cov-table">\n      <tbody>\n' % len(COVER_GRAMMAR) + "\n".join(t2) + '\n      </tbody>\n    </table>\n'
        '  </div>\n'
    )

