
# ---------------------------------------------------------- 逐字標註（句子級）
def _is_verbish(w):
    if not w:
        return False
    if w in BE_FORMS or w in MODAL or w in DO_FORMS or w in HAVE_FORMS:
        return True
    return verb_morph(w) is not None


def tag_all(toks, span_first, cls_of=None):
    """toks：句子所有 token；span_first：某 span 第一個字的 index set；
    cls_of：每個 token 所屬 span 的 kw- 類別。回傳 [(POS, 說明), ...]"""
    n = len(toks)
    low = [t.lower() for t in toks]
    if cls_of is None:
        cls_of = [None] * n
    res = [(None, None)] * n

    def g(i):
        return low[i] if 0 <= i < n else None

    for i in range(n):
        lw = low[i]
        prev, prev2 = g(i - 1), g(i - 2)
        nxt, nxt2 = g(i + 1), g(i + 2)
        at_start = i in span_first

        # --- 縮寫 ---
        if lw in NEG_CONTRACTION:
            if lw in ("isn't", "aren't", "wasn't", "weren't"):
                res[i] = ('BE', 'be 動詞 + not 的否定縮寫')
            else:
                res[i] = ('AUX', '助動詞 + not 的否定縮寫')
            continue
        if lw in PRON_CONTRACTION:
            if lw == "i'm":
                res[i] = ('BE', "I am 的縮寫（I＝主格代名詞、'm＝be 動詞）")
            elif lw == "let's":
                res[i] = ('VERB',
                          '動詞（let us 的縮寫；let 後接受詞＋原形動詞）')
            elif lw in ("there's", "it's", "that's", "he's", "she's", "who's",
                        "what's"):
                res[i] = ('BE', lw.split("'")[0] + ' is 的縮寫')
            else:
                res[i] = ('BE', lw.replace("'", ' + ') + ' 的縮寫')
            continue
        if lw.endswith("'s") and lw[:-2] in NOUN_SET:
            res[i] = ('NOUN', '名詞所有格（' + lw[:-2] + chr(39) + 's 的）')
            continue
        if lw.endswith("'s") and lw[:-2] in PRON_INDEF:
            res[i] = ('PRON', '不定代名詞所有格（' + lw[:-2] + chr(39) +
                      's 的）')
            continue
        if lw == "o'clock":
            res[i] = ('ADV', '時間副詞（…點鐘）')
            continue

        # --- 情態動詞 ---
        if lw in MODAL:
            note = {
                'can': '情態動詞（can 能、可以）',
                'cannot': '情態動詞（can not 的完整寫法，不能）',
                "can't": '情態動詞（can not 的縮寫，不能）',
                'could': '情態動詞（could 能夠；亦表客氣請求）',
                'may': '情態動詞（may 可以、也許）',
                'might': '情態動詞（might 或許、可能）',
                'must': '情態動詞（must 必須）',
                'shall': '情態動詞（shall 將…、要不要…）',
                'should': '情態動詞（should 應該）',
                "shouldn't": '情態動詞（should not 的縮寫，不應該）',
                'will': '情態動詞（will 將來式助動詞，將、會）',
                "won't": '情態動詞（will not 的縮寫，不會）',
                'would': '情態動詞（would 會、願意；表客氣）',
                "wouldn't": '情態動詞（would not 的縮寫，不願意）',
                'ought': '情態動詞（ought to 應該）',
                'need': '情態動詞（need 需要）',
                'dare': '情態動詞（dare 敢）',
            }.get(lw, '情態動詞（Modal）')
            res[i] = ('AUX', note)
            continue

        # --- be 動詞 ---
        if lw in BE_FORMS:
            base = {'am': 'am', 'is': 'is', 'are': 'are', 'was': 'was',
                    'were': 'were', 'be': 'be（原形）',
                    'been': 'be（過去分詞）', 'being': 'be（現在分詞）'}[lw]
            nv = verb_morph(nxt)
            if nv and nv[2] == 'ing':
                note = 'be 動詞（進行式：be + V-ing）'
            elif nv and nv[2] in ('pp', 'past') and nxt in V_PP:
                note = 'be 動詞（被動語態：be + 過去分詞）'
            elif nxt in NOUN_SET or nxt in PROPN:
                note = 'be 動詞（連綴動詞：後接名詞作主詞補語）'
            else:
                note = 'be 動詞（連綴動詞：後接形容詞作主詞補語）'
            res[i] = ('BE', base + '　' + note)
            continue

        # --- do 系 ---
        if lw in DO_FORMS:
            neg = lw in ("don't", "doesn't", "didn't")
            if neg or nxt == 'not':
                res[i] = ('AUX', '助動詞 do 系（幫助構成否定句）')
            elif nxt is None:
                res[i] = ('VERB', '動詞（do 作主要動詞）')
            elif nxt in PRON_SUBJ or nxt in V_BASE or nxt in REGULAR_VERBS:
                res[i] = ('AUX', '助動詞 do 系（幫助構成疑問句或加強語氣）')
            elif nxt in DET_ONLY or nxt in NUM_ONLY or nxt in NOUN_SET \
                    or nxt in PROPN or nxt in ('me', 'him', 'us', 'them',
                                               'mine', 'yours'):
                res[i] = ('VERB', '動詞（do 作主要動詞，後接受詞）')
            else:
                res[i] = ('AUX', '助動詞 do 系')
            continue

        # --- have 系 ---
        if lw in HAVE_FORMS:
            nv = verb_morph(nxt)
            if nxt == 'to':
                res[i] = ('AUX', '助動詞（have to＝must 必須）')
            elif nv and nv[2] in ('pp', 'past'):
                res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）')
            elif nv and nv[2] == 'base' and nxt in V_BASE:
                res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）')
            elif nxt in DET_ONLY or nxt in NUM_ONLY or nxt in PROPN \
                    or nxt in NOUN_SET or nxt in ADJ_SET \
                    or nxt in PRON_OBJ or nxt in PRON_SUBJ:
                res[i] = ('VERB', '動詞（have 有、吃、從事）')
            else:
                res[i] = ('VERB', '動詞（have 有）')
            continue
        if lw == 'having':
            res[i] = ('VERB', '現在分詞／動名詞')
            continue

        # --- to ---
        if lw == 'to':
            nv = verb_morph(nxt)
            inf = bool(nv and nv[2] == 'base') or (nxt in V_BASE)
            if inf and nxt in NOUN_SET and prev in MOTION_VERBS:
                res[i] = ('PREP', '介系詞（to 後接名詞片語）')
            elif inf:
                res[i] = ('TO', '不定詞標記 to（to + 動詞原形）')
            else:
                res[i] = ('PREP', '介系詞（to 後接名詞片語）')
            continue

        # --- 否定 ---
        if lw in NEG:
            res[i] = ('ADV', '否定副詞 not')
            continue

        # --- 對等連接詞 ---
        if lw in CONJ:
            res[i] = ('CONJ', '對等連接詞（連接地位相等的字、片語或子句）')
            continue

        # --- 固定介系詞 ---
        if lw in PREP_ALWAYS or lw in PREP_BEHIND:
            res[i] = ('PREP', '介系詞（後接名詞片語作受詞）')
            continue

        # --- 固定從屬連接詞 ---
        if lw in ('although', 'because', 'if', 'unless', 'whether',
                  'whenever', 'whereas', 'though'):
            res[i] = ('SCONJ', '從屬連接詞（引導副詞子句）')
            continue
        if lw == 'than':
            res[i] = ('SCONJ', '比較用從屬連接詞（A 比 B…）')
            continue

        # --- 從屬連接詞 或 介系詞 ---
        if lw in ('after', 'before', 'since', 'until', 'till', 'while'):
            nv = verb_morph(nxt)
            if nxt in PRON_SUBJ:
                res[i] = ('SCONJ', '從屬連接詞（引導副詞子句）')
            elif nv and nv[2] == 'ing':
                res[i] = ('PREP', '介系詞（後接動名詞片語）')
            elif nv and nv[2] in ('base', 's3', 'past', 'pp'):
                res[i] = ('SCONJ', '從屬連接詞（引導副詞子句）')
            elif nxt2 and (nxt2 in PRON_SUBJ
                           or (verb_morph(nxt2) and verb_morph(nxt2)[2]
                               in ('base', 's3', 'past'))):
                res[i] = ('SCONJ', '從屬連接詞（引導副詞子句）')
            else:
                res[i] = ('PREP', '介系詞（後接名詞片語）')
            continue
        if lw == 'as':
            if at_start:
                res[i] = ('SCONJ', '從屬連接詞（as 當…時／一…就…）')
            elif prev and (prev in ADJ_SET or prev in ADV_SET or _is_verbish(prev)):
                res[i] = ('SCONJ', '從屬連接詞（as…as 中第二個 as）')
            elif nxt and (nxt in NOUN_SET or nxt in DET_ONLY or nxt in PROPN):
                res[i] = ('PREP', '介系詞（as 作為、當作）')
            else:
                res[i] = ('ADV', '副詞（as…as 中第一個 as，「和…一樣」）')
            continue
        if lw == 'so':
            if nxt and (nxt in ADJ_SET or nxt in ADV_SET):
                res[i] = ('ADV', '副詞（so 如此、這麼）')
            else:
                res[i] = ('CONJ', '對等連接詞（so 所以）')
            continue

        # --- 疑問／連接副詞 ---
        if lw in WH_ADV:
            if at_start:
                res[i] = ('SCONJ', '從屬連接詞（引導子句）')
            else:
                # 後面 4 個字內若出現限定動詞，即引導名詞子句
                has_v = False
                for t in range(i + 1, min(n, i + 5)):
                    vm = verb_morph(low[t])
                    kk = vm[2] if vm else None
                    if kk in ('past', 's3', 'base', 'pp', 'ing') \
                            or low[t] in BE_FORMS:
                        has_v = True
                        break
                if has_v or prev in REPORT_VERB or prev in PREP_ALWAYS:
                    res[i] = ('SCONJ', '從屬連接詞（引導子句）')
                else:
                    res[i] = ('ADV', '連接副詞（引導子句，本身作狀語）')
            continue

        # --- 關係／疑問代名詞 ---
        if lw in ('who', 'whom'):
            res[i] = ('PRON', '代名詞（關係代名詞／疑問代名詞，指人）')
            continue
        if lw == 'whose':
            res[i] = ('DET', '所有格限定詞（whose 誰的，引導關係子句）')
            continue
        if lw == 'which':
            if nxt in NOUN_SET or nxt in ADJ_SET or nxt in NUM_ONLY:
                res[i] = ('DET', '限定詞（which 哪一個）')
            else:
                res[i] = ('PRON', '代名詞（關係代名詞／疑問代名詞，指事物）')
            continue
        if lw == 'what':
            if nxt in NOUN_SET or nxt in ADJ_SET:
                res[i] = ('DET', '限定詞（what 什麼樣的）')
            else:
                res[i] = ('PRON', '代名詞（疑問代名詞／名詞子句的成分）')
            continue
        if lw == 'that':
            if nxt in DET_ONLY or (nxt in NOUN_SET and nxt not in V_BASE):
                res[i] = ('DET', '限定詞（that 那個）')
            elif prev in REPORT_VERB or prev in BE_FORMS:
                res[i] = ('SCONJ', '從屬連接詞（引導名詞子句，本身不作成分）')
            elif prev and (prev in NOUN_SET or prev in PROPN
                           or prev in PRON_SUBJ or prev in PRON_OBJ
                           or prev in ('its', 'their', 'my', 'your', 'his',
                                       'her', 'our')):
                res[i] = ('PRON', '代名詞（關係代名詞，引導關係子句）')
            elif at_start:
                res[i] = ('SCONJ', '從屬連接詞（引導名詞子句）')
            else:
                res[i] = ('PRON', '代名詞（指示代名詞）')
            continue
        if lw in ('this', 'these', 'those'):
            if nxt in NOUN_SET or nxt in ADJ_SET or nxt in NUM_ONLY \
                    or nxt in PROPN:
                res[i] = ('DET', '限定詞（指示形容詞，修飾後面的名詞）')
            else:
                res[i] = ('PRON', '代名詞（指示代名詞）')
            continue

        # --- there ---
        if lw == 'there':
            if nxt in BE_FORMS:
                res[i] = ('PRON', '引詞（there is/are 句型中的虛主詞）')
            else:
                res[i] = ('ADV', '副詞（there 在那裡）')
            continue

        # --- 所有格 ---
        if lw in ('my', 'your', 'our', 'their'):
            res[i] = ('DET', '所有格限定詞（' + lw + ' 的）')
            continue
        if lw == 'its':
            res[i] = ('DET', '所有格限定詞（its 它的）')
            continue
        if lw == 'his':
            if nxt in NOUN_SET or nxt in ADJ_SET or nxt in PROPN:
                res[i] = ('DET', '所有格限定詞（his 他的）')
            else:
                res[i] = ('PRON', '所有格代名詞（his 他的）')
            continue
        if lw == 'her':
            if nxt in NOUN_SET or nxt in ADJ_SET or nxt in PROPN:
                res[i] = ('DET', '所有格限定詞（her 她的）')
            else:
                res[i] = ('PRON', '受格代名詞（her 她）')
            continue
        if lw in PRON_POSS:
            res[i] = ('PRON', '所有格代名詞（後面不接名詞）')
            continue
        if lw in PRON_REFL:
            res[i] = ('PRON', '反身代名詞（…自己）')
            continue

        # --- 主格代名詞 ---
        if lw in PRON_SUBJ:
            if lw in ('i', 'he', 'she', 'we', 'they'):
                res[i] = ('PRON', '主格代名詞（作主詞）')
            elif nxt and (nxt in BE_FORMS or _is_verbish(nxt)):
                res[i] = ('PRON', '主格代名詞（you 主格、受格同形，此處作主詞）')
            elif prev and (prev in PREP_ALWAYS or _is_verbish(prev)):
                res[i] = ('PRON', '受格代名詞（you 主格、受格同形，此處作受詞）')
            else:
                res[i] = ('PRON', '代名詞（you 主格、受格同形）')
            continue
        if lw in PRON_OBJ:
            note = {'me': '受格代名詞（I 的受格）',
                    'him': '受格代名詞（he 的受格）',
                    'us': '受格代名詞（we 的受格）',
                    'them': '受格代名詞（they 的受格）'}.get(lw,
                                                             '受格代名詞')
            res[i] = ('PRON', note)
            continue
        if lw == 'it':
            if nxt and (nxt in BE_FORMS or _is_verbish(nxt)):
                res[i] = ('PRON', '主格代名詞（it 主格、受格同形，此處作主詞）')
            elif prev and (prev in PREP_ALWAYS or _is_verbish(prev)):
                res[i] = ('PRON', '受格代名詞（it 主格、受格同形，此處作受詞）')
            else:
                res[i] = ('PRON', '代名詞（it 主格、受格同形）')
            continue
        if lw in PRON_INDEF:
            res[i] = ('PRON', '不定代名詞（指不特定的人或事物）')
            continue

        # --- 感嘆詞 ---
        if lw in INTJ_SET:
            if lw == 'please':
                # please 修飾祈使句的動詞 → 副詞，不是感嘆詞
                res[i] = ('ADV', '副詞（please 請，修飾祈使句的動詞）')
            else:
                res[i] = ('INTJ', '感嘆詞（表示驚訝、感謝、招呼等）')
            continue

        # --- 單一字母（如 T-shirt 中的 T；a 是限定詞不可誤判） ---
        if len(lw) == 1 and lw.isalpha() and lw != 'a':
            res[i] = ('NOUN', '名詞（單一字母）')
            continue

        # --- 限定詞 ---
        if lw in DET_ONLY or lw in ('every', 'each', 'both', 'either',
                                    'neither', 'such', 'another', 'own'):
            res[i] = ('DET', '限定詞（修飾後面的名詞）')
            continue

        # --- 數詞 ---
        if lw in NUM_ONLY:
            res[i] = ('NUM', '數詞（修飾後面的名詞）')
            continue
        if lw.isdigit():
            res[i] = ('NUM', '數詞')
            continue

        # --- 專有名詞 ---
        if lw in PROPN:
            res[i] = ('PROPN', '專有名詞（人名／地名／星期，首字母大寫）')
            continue

        # --- 歧義字 ---
        if lw in AMBIG:
            out = _disambig(lw, i, low, cls_of, at_start)
            if out and out[0] is not None:
                res[i] = out
                continue

        # --- 一般字 ---
        if lw in NOUN_SET:
            res[i] = ('NOUN', '名詞（複數）' if lw in NOUN_PLURAL else '名詞')
            continue
        if lw in ADJ_SET:
            res[i] = ('ADJ', '形容詞')
            continue
        if lw in ADV_SET:
            res[i] = ('ADV', '副詞')
            continue
        vm = verb_morph(lw)
        if vm:
            if vm[2] == 'ing' and nxt in NOUN_SET:
                if i == 0:
                    # 句首的動名詞片語＝主詞（Playing music has made me braver）
                    res[i] = ('NOUN', '動名詞（作主詞）')
                else:
                    res[i] = ('NOUN', '動名詞作定語（修飾後面的名詞）')
            else:
                res[i] = (vm[0], vm[1])
            continue
        res[i] = ('X', '未標記')

    # 第二輪：所有格 his / her / its 依「下一個字」的詞性決定
    for i in range(n):
        lw = low[i]
        if lw not in ('his', 'her', 'its'):
            continue
        pos = res[i][0]
        if pos is None:
            continue
        npos = res[i + 1][0] if i + 1 < n else None
        if npos in ('ADJ', 'NOUN', 'PROPN', 'NUM', 'DET'):
            gen = {'his': 'his 他的', 'her': 'her 她的', 'its': 'its 它的'}[lw]
            res[i] = ('DET', '所有格限定詞（' + gen + '）')
        elif pos == 'DET':
            res[i] = ('PRON', '所有格代名詞（' + lw + '）')

    # 第三輪修正
    for i in range(n):
        pos, note = res[i]
        if pos == 'VERB' and note and '現在分詞' in note \
                and i > 0 and res[i - 1][0] in ('DET', 'NOUN', 'ADJ',
                                                'PROPN', 'NUM'):
            if g(i + 1) in NOUN_SET:
                res[i] = ('NOUN', '動名詞作定語（修飾後面的名詞）')
    # 第四輪：依前後文精修
    res = refine(res, low, n)
    return res
