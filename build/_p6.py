
# ------------------------------------------------------- 第二階段：前後文精修
_DET_AFTER_THAT = set("""a an the this these those my your his her its our
their every each no another such whose some any""".split())

# 所有格（可作限定詞）：her answers / our class …
_POSS_PRON = set("""my your his her its our their whose""".split())

_ADJ_ADV_WORDS = set("""late fast hard long early close high low far straight
slow quick deep wide free soft loud bright right wrong warm cool open left
light empty full still just only""".split())

# 傳達／報導動詞：其後的 NOUN + that 通常是「that 引導名詞子句」
# （The teacher showed the class that ...），而非關係子句。
_CONTENT_VERB = set("""say said says tell told tells show showed shows show
explain explained explains ask asked asks warn warned warns remind reminded
reminds inform informed informs teach taught teaches promise promised
promises answer answered answers reply replied replies write wrote writes
report reported reports mention mentioned mentions indicate indicated
indicates suggest suggested suggests reveal revealed reveals declare declared
declares announce announced announces admit admitted admits complain
complained complains""".split())

_PARTICLE = set("""up down off out away back apart together ahead""".split())


def refine(res, low, n):
    """依前後一個字的詞性，修正容易誤判的詞性。"""

    def P(i):
        return res[i][0] if 0 <= i < n else None

    def W(i):
        return low[i] if 0 <= i < n else None

    def pp(i, skip_adv=True):
        j = i - 1
        if skip_adv:
            while j >= 0 and res[j][0] == 'ADV':
                j -= 1
        return j

    def nx(i, skip_adv=True):
        j = i + 1
        if skip_adv:
            while j < n and res[j][0] == 'ADV':
                j += 1
        return j

    def kind(w):
        vm = verb_morph(w)
        return vm[2] if vm else None

    def NEARL(i):
        j = pp(i, True)
        return P(j) if j >= 0 else None

    def quoted_ahead(i):
        # 後面緊接著引號或主格代名詞 → 處在引述話語裡，
        # -s 字是動詞不是名詞複數（'I am busy' becomes 'He said …'）
        j = i + 1
        if j >= n:
            return False
        if low[j][:1] in ("'", '"', '\u201c', '\u2018', '\u300c'):
            return True
        return low[j] in ('i', 'you', 'he', 'she', 'we', 'they')

    # --- 1. a / an 永遠是限定詞（不可被「單一字母」規則吃掉） ---
    for i in range(n):
        if low[i] in ('a', 'an'):
            res[i] = ('DET', '限定詞（修飾後面的名詞）')

    # --- 2. V-ing：介系詞／動詞後的動名詞 ---
    for i in range(n):
        if kind(low[i]) != 'ing':
            continue
        j = i - 1
        if j < 0:
            continue
        pj = res[j][0]
        if pj == 'PREP' and res[i][0] == 'VERB':
            res[i] = ('VERB', '動名詞（介系詞後接 V-ing 作受詞）')
        elif pj == 'VERB':
            res[i] = ('VERB', '動名詞／現在分詞')

    # --- 3. 限定詞／形容詞／專有名詞／介系詞 後面的字 ---
    for i in range(n):
        if res[i][0] not in ('VERB', 'AUX'):
            continue
        lw = low[i]
        j = pp(i, False)
        if j < 0:
            continue
        pj = res[j][0]
        if pj not in ('DET', 'ADJ', 'PROPN', 'NUM', 'PREP', 'NOUN') \
                and low[j] not in _POSS_PRON:
            continue
        k = kind(lw)
        if pj in ('PROPN', 'NUM'):
            if k == 'ing':
                # 專有名詞／數字後的 V-ing：Monday morning / two running …
                res[i] = ('NOUN', '名詞')
            elif k == 's3' and not quoted_ahead(i):
                res[i] = ('NOUN', '名詞' if lw in MASS_SINGULAR
                          else '名詞（複數）')      # forty tickets
            elif k == 'base' and (lw in NOUN_SET or
                                  (lw in AMBIG and 'NOUN' in AMBIG[lw])):
                nk2 = res[i + 1][0] if i + 1 < n else None
                if nk2 in ('PREP', 'NOUN', 'PROPN', 'DET', 'ADJ', 'CONJ') \
                        or nk2 is None:
                    res[i] = ('NOUN', '名詞')
            continue
        if pj == 'NOUN':
            # 名詞 + 名詞 → 複合名詞（a music show）
            if k == 'base' and lw in AMBIG and 'NOUN' in AMBIG[lw]:
                nk2 = res[i + 1][0] if i + 1 < n else None
                if nk2 in ('ADJ', 'CONJ', 'ADV') or nk2 is None:
                    res[i] = ('NOUN', '名詞（複合名詞的後半）')
            continue
        if pj == 'PREP':
            if k == 'ing':
                continue
            if lw in AMBIG and 'NOUN' in AMBIG[lw]:
                res[i] = ('NOUN', '名詞（介系詞後的受詞）')
            elif k == 's3' and not quoted_ahead(i):
                res[i] = ('NOUN', '名詞' if lw in MASS_SINGULAR
                          else '名詞（複數）')
            elif k in ('past', 'pp'):
                res[i] = ('ADJ', '分詞形容詞（修飾後面的名詞）')
            elif k is None and lw in NOUN_SET:
                res[i] = ('NOUN', '名詞')
            continue
        # DET / ADJ 前面
        if res[i][0] == 'AUX':
            res[i] = ('NOUN', '名詞')
            continue
        if k in ('past', 'pp'):
            res[i] = ('ADJ', '分詞形容詞（修飾後面的名詞）')
        elif k == 'ing':
            # 後面直接接名詞 → 名詞修飾語（a cleaning day / swimming pool）；
            # 後面接冠詞等 → 分詞補語（was busy preparing a play）
            if i + 1 < n and res[i + 1][0] in ('NOUN', 'PROPN'):
                res[i] = ('NOUN', '名詞（動名詞作定語）')
            else:
                res[i] = ('VERB', '現在分詞／動名詞')
        elif k == 's3' and not quoted_ahead(i):
            res[i] = ('NOUN', '名詞' if lw in MASS_SINGULAR
                      else '名詞（複數）')
        elif lw in AMBIG and 'NOUN' in AMBIG[lw]:
            res[i] = ('NOUN', '名詞')
        elif lw in NOUN_SET:
            res[i] = ('NOUN', '名詞')

    # --- 3b. so + 形容詞／分詞 → 程度副詞 ---
    for i in range(n):
        if low[i] != 'so' or i + 1 >= n:
            continue
        nk = res[i + 1][0]
        if nk == 'ADJ' or (nk == 'VERB'
                           and kind(low[i + 1]) in ('past', 'pp', 'ing')):
            res[i] = ('ADV', '副詞（so 如此，修飾後面的形容詞）')

    # --- 3c. 形容詞後面的感嘆詞其實是名詞（loud cheers） ---
    for i in range(n):
        if res[i][0] == 'INTJ' and i > 0 and res[i - 1][0] == 'ADJ':
            res[i] = ('NOUN', '名詞')

    # --- 4. have / has / had：助動詞 vs 主要動詞 ---
    for i in range(n):
        if low[i] not in ('have', 'has', 'had'):
            continue
        j = i + 1
        while j < n and (res[j][0] == 'ADV'
                         or low[j] in ('all', 'both', 'ever', 'often',
                                       'usually', 'already', 'always')):
            j += 1
        if j >= n:
            res[i] = ('VERB', '動詞（have 有、吃、從事）')
            continue
        njw, njt = low[j], res[j][0]
        if njt == 'TO' or njw == 'to':
            res[i] = ('AUX', '助動詞（have to＝must 必須）')
            continue
        if njt in ('PRON',) and njw in PRON_SUBJ:
            res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）')
            continue
        if njt in ('BE', 'AUX'):
            res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）')
            continue
        if njt == 'VERB':
            if kind(njw) in ('pp', 'past') or njw in V_PP:
                res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）')
            else:
                res[i] = ('VERB', '動詞（have 有、吃、從事）')
            continue
        # 後面是限定詞／名詞：往後找有無過去分詞（遇代名詞即停止）
        got = False
        for t in range(j, min(n, j + 5)):
            if res[t][0] in ('BE', 'AUX', 'PRON', 'CONJ', 'SCONJ'):
                break
            kw = kind(low[t])
            if kw in ('pp', 'past') or low[t] in V_PP:
                got = True
                break
        res[i] = ('AUX', '助動詞 have（完成式：have + 過去分詞）') if got \
            else ('VERB', '動詞（have 有、吃、從事）')

    # --- 5. do / does / did：助動詞 vs 主要動詞 ---
    for i in range(n):
        if low[i] not in ('do', 'does', 'did'):
            continue
        if i > 0 and (low[i - 1] == 'than' or
                      (i > 1 and low[i - 2] == 'than'
                       and res[i - 1][0] == 'PRON')):
            # than I did last year：did 代替前面的動詞
            res[i] = ('AUX', '助動詞 did（代替前面的動詞，避免重複）')
            continue
        j = i + 1
        while j < n and (res[j][0] == 'ADV') and low[j] != 'not':
            j += 1
        if j >= n:
            continue
        if low[j] == 'not':
            res[i] = ('AUX', '助動詞 do 系（幫助構成否定句）')
            continue
        if low[j] in PRON_SUBJ:
            res[i] = ('AUX', '助動詞 do 系（幫助構成疑問句或加強語氣）')
            continue
        if res[j][0] == 'VERB' and kind(low[j]) == 'base':
            res[i] = ('AUX', '助動詞 do 系（幫助構成疑問句或加強語氣）')
            continue
        res[i] = ('VERB', '動詞（do 作主要動詞，後接受詞）')

    # --- 6. need：名詞／主要動詞／情態動詞 ---
    for i in range(n):
        if low[i] != 'need':
            continue
        j = pp(i, False)
        pj = P(j) if j >= 0 else None
        k = i + 1
        nk = P(k) if k < n else None
        if pj in ('DET', 'NUM', 'ADJ'):
            res[i] = ('NOUN', '名詞（需要；需求）')
        elif nk == 'TO' or (k < n and low[k] == 'to'):
            res[i] = ('VERB', '動詞（need 需要，後接不定詞作受詞）')
        elif nk == 'VERB' and kind(low[k]) == 'base':
            res[i] = ('AUX', '情態動詞 need（need 後直接接原形動詞）')
        else:
            res[i] = ('VERB', '動詞（need 需要）')

    # --- 7. 片語動詞的小品詞 ---
    for i in range(n):
        if low[i] not in _PARTICLE:
            continue
        j = i - 1
        if j >= 0 and res[j][0] == 'VERB':
            res[i] = ('ADV', '副詞（與前面的動詞構成片語動詞）')

    # --- 8. like：介系詞 vs 動詞 ---
    for i in range(n):
        if low[i] != 'like':
            continue
        j = i - 1
        k = i + 1
        if j < 0 or k >= n:
            continue
        if res[j][0] in ('VERB', 'NOUN', 'PROPN') and \
                res[k][0] in ('DET', 'PRON', 'PROPN', 'NUM'):
            res[i] = ('PREP', '介系詞（like 像…一樣）')

    # --- 9. that：指示限定詞／關係代名詞／從屬連接詞 ---
    def _rel(i):
        """that 後面是否是一個關係子句（有主詞＋限定動詞）"""
        for t in range(i + 1, min(n, i + 6)):
            rt = res[t][0]
            if rt == 'PRON':
                if low[t] in PRON_SUBJ:
                    return True
                continue
            if rt in ('BE', 'AUX', 'VERB'):
                return True
            if rt in ('CONJ', 'SCONJ'):
                return False
        return False

    def _clause(i):
        """that 後面是否是一個（名詞）子句：先有名詞片語，再出現限定動詞"""
        t = i + 1
        if t >= n:
            return False
        rt = res[t][0]
        if rt == 'PRON':
            return low[t] in PRON_SUBJ          # that he left / that I know
        if rt == 'VERB':
            return False                        # that + 動詞 → that 作主詞
        if rt in ('BE', 'AUX') and low[t] != 'being':
            return False                        # that is ... → that 作主詞
        for t in range(i + 1, min(n, i + 7)):
            rt = res[t][0]
            if rt == 'PRON':
                if low[t] in PRON_SUBJ:
                    return True
                return False
            if rt in ('BE', 'AUX') and low[t] != 'being':
                return True
            if rt == 'VERB':
                return kind(low[t]) in ('past', 's3', 'base', 'pp', 'ing') \
                    and t > i + 1
            if rt in ('CONJ', 'SCONJ'):
                return False
        return False

    def _clause_after(t):
        """t 之後是否還有子句的限定動詞／主詞"""
        for u in range(t + 1, min(n, t + 7)):
            rt = res[u][0]
            if rt == 'PRON':
                if low[u] in PRON_SUBJ:
                    return True
                return False
            if rt in ('BE', 'AUX') and low[u] != 'being':
                return True
            if rt == 'VERB':
                if kind(low[u]) == 'ing':
                    continue
                return True
            if rt in ('CONJ', 'SCONJ'):
                return False
        return False

    # that + V-ing 且後面沒有子句 → 指示形容詞 + 名詞（that evening）
    for i in range(n):
        if low[i] != 'that' or i + 1 >= n:
            continue
        if res[i + 1][0] == 'VERB' and kind(low[i + 1]) == 'ing' \
                and not _clause_after(i + 1):
            res[i + 1] = ('NOUN', '名詞')

    for i in range(n):
        if low[i] != 'that':
            continue
        if i > 0 and low[i - 1] == 'order':
            res[i] = ('SCONJ', '從屬連接詞（in order that 為了，引導子句）')
            continue
        j = i - 1
        while j >= 0 and res[j][0] == 'ADV':
            j -= 1
        k = i + 1
        pj = P(j) if j >= 0 else None
        nk = P(k) if k < n else None
        nw = low[k] if k < n else None
        if pj in ('NOUN', 'PROPN') and _rel(i) and not (
                (j >= 1 and res[j - 1][0] == 'DET' and j >= 2
                 and res[j - 2][0] in ('VERB', 'AUX')
                 and low[j - 2] in _CONTENT_VERB) or
                (j >= 1 and res[j - 1][0] in ('VERB', 'AUX')
                 and low[j - 1] in _CONTENT_VERB)):
            res[i] = ('PRON', '代名詞（關係代名詞，引導關係子句）')
        elif nw == 'one':
            res[i] = ('DET', '限定詞（指示形容詞 that 那個，修飾後面的名詞）')
        elif _clause(i):
            res[i] = ('SCONJ', '從屬連接詞（that 引導名詞子句，本身不作成分）')
        elif nk in ('NOUN', 'PROPN', 'ADJ', 'NUM'):
            res[i] = ('DET', '限定詞（指示形容詞 that 那個，修飾後面的名詞）')
        elif nk == 'BE':
            res[i] = ('PRON', '指示代名詞（that 那個，作主詞或補語）')
        elif pj in ('BE', 'AUX'):
            res[i] = ('PRON', '指示代名詞（that 那個，作主詞或補語）')
        elif pj == 'PREP':
            res[i] = ('PRON', '指示代名詞（that 那個，作介系詞的受詞）')
        elif j < 0:
            res[i] = ('PRON', '指示代名詞（that 那個）')
        elif k >= n:
            res[i] = ('PRON', '指示代名詞（that 那個）')
        else:
            res[i] = ('SCONJ', '從屬連接詞（that 引導名詞子句，本身不作成分）')

    # --- 10. before / after / since / until / while：介系詞 vs 從屬連接詞 ---
    for i in range(n):
        if low[i] not in ('before', 'after', 'since', 'until', 'till',
                          'while'):
            continue
        k = i + 1
        nk = P(k) if k < n else None
        nw = low[k] if k < n else None
        if nk in ('DET', 'NUM', 'NOUN', 'PROPN'):
            res[i] = ('PREP', '介系詞（後接名詞片語作受詞）')
        elif nk == 'PRON' and i >= 2 and res[i - 1][0] in ('NOUN', 'NUM') \
                and low[i - 2] in ('many', 'some', 'several', 'few', 'more',
                                   'most', 'about', 'over', 'almost', 'last',
                                   'next', 'two', 'three', 'four', 'five',
                                   'six', 'seven', 'eight', 'nine', 'ten'):
            # many times before, I had ...
            res[i] = ('ADV', '副詞（表時間：…以前／…之後）')
        elif nk == 'PRON':
            res[i] = ('SCONJ', '從屬連接詞（引導副詞子句）')
        elif nk is None or (nw and nw[0] in ',.;'):
            res[i] = ('ADV', '副詞（表時間：…以前／…之後）')

    # --- 11. be / 連綴動詞 後的分詞、形容詞 ---
    PREP_NEXT = set("""by with at in on to for from into under over during
without about of without through""".split())
    for i in range(n):
        lw = low[i]
        j = pp(i, True)
        pj = P(j) if j >= 0 else None
        plw = low[j] if j >= 0 else ''
        k = nx(i, True)
        nk = P(k) if k < n else None
        nw = low[k] if k < n else None
        if res[i][0] == 'VERB':
            if pj == 'BE' or plw in LINKING:
                if nk == 'PREP' or nw in PREP_NEXT:
                    continue          # 被動語態 be + V-ed + by
                kk = kind(lw)
                if kk in ('past', 'pp'):
                    res[i] = ('ADJ', '過去分詞作形容詞（be + V-ed 作補語）')
                elif kk is None and lw in AMBIG and 'ADJ' in AMBIG[lw]:
                    res[i] = ('ADJ', '形容詞')
        elif res[i][0] == 'NOUN':
            if pj == 'BE' and nk not in ('DET', 'NUM', 'ADJ', 'PROPN'):
                res[i] = ('ADJ', '形容詞（be 後作主詞補語）')

    # --- 12. 比較級／最高級 ---
    for i in range(n):
        if low[i] not in COMPARATIVE:
            continue
        j = pp(i, True)
        pj = P(j) if j >= 0 else None
        plw = low[j] if j >= 0 else ''
        k = i + 1
        nk = P(k) if k < n else None
        if nk == 'NOUN' or pj in ('DET', 'NUM', 'BE', 'PRON') or \
                plw in LINKING:
            res[i] = ('ADJ', '形容詞（比較級／最高級）')
        elif pj in ('ADV', 'VERB', 'AUX', 'TO', 'PREP', None):
            res[i] = ('ADV', '副詞（比較級／最高級）')

    # --- 13. 形容詞／副詞兩可的字出現在錯誤位置 ---
    for i in range(n):
        if res[i][0] not in ('VERB', 'ADJ', 'ADV'):
            continue
        if low[i] not in _ADJ_ADV_WORDS:
            continue
        if i + 1 < n and low[i + 1] == 'as':        # as fast as ...
            res[i] = ('ADJ', '形容詞')
            continue
        if i > 0 and low[i - 1] == 'how':           # how hard her job is
            res[i] = ('ADJ', '形容詞（how + 形容詞）')
            continue
        # stayed up late：前面是片語動詞的小品詞 → 副詞
        if i > 0 and res[i - 1][0] == 'ADV' and low[i - 1] in _PARTICLE:
            res[i] = ('ADV', '副詞')
            continue
        j = pp(i, True)
        pj = P(j) if j >= 0 else None
        plw = low[j] if j >= 0 else ''
        # turn left / turn right：方向副詞（turn 在此不是連綴動詞）
        if low[i] in ('left', 'right', 'straight') and pj in ('VERB', 'AUX') \
                and plw in ('turn', 'go', 'move', 'come', 'head', 'point',
                            'lean', 'bend'):
            res[i] = ('ADV', '副詞')
            continue
        k = nx(i, True)
        nk = P(k) if k < n else None
        adj_pos = adv_pos = False
        if pj == 'BE' or plw in LINKING:
            # be + still/just/only 永遠是副詞；其餘為主詞補語
            adv_pos = low[i] in ('still', 'just', 'only')
            adj_pos = not adv_pos
        elif i + 1 < n and low[i + 1] in _PARTICLE:
            # a short warm-up（複合名詞）／to warm up（片語動詞，維持原判）
            if pj in ('DET', 'ADJ', 'NUM'):
                adj_pos = True
        elif nk in ('NOUN', 'PROPN', 'ADJ'):
            adj_pos = True                      # 修飾後面的名詞
        elif nk in ('VERB', 'AUX', 'NUM'):
            adv_pos = True                      # 修飾後面的動詞／數量
        elif pj in ('DET', 'NUM', 'ADJ', 'PROPN'):
            adj_pos = True
        elif pj == 'PRON':
            if plw in PRON_SUBJ and plw not in PRON_OBJ:
                adv_pos = True
            else:
                adj_pos = True
        elif pj in ('ADV', 'VERB'):
            adv_pos = True
        # AUX / TO / CONJ / SCONJ / PREP / 句首 → 維持原判定
        if adj_pos:
            res[i] = ('ADJ', res[i][1] if res[i][0] == 'ADJ' else '形容詞')
        elif adv_pos:
            res[i] = ('ADV', res[i][1] if res[i][0] == 'ADV' else '副詞')

    # --- 14. left ---
    for i in range(n):
        if low[i] != 'left':
            continue
        k = i + 1
        nk = P(k) if k < n else None
        j = i - 1
        pj = P(j) if j >= 0 else None
        if nk in ('DET', 'NOUN', 'PROPN', 'PRON', 'NUM'):
            res[i] = ('VERB', '動詞過去式（leave 離開／留下）')
        elif k >= n and pj in ('DET', 'PRON') and j - 1 >= 0 \
                and P(j - 1) in ('VERB', 'AUX', 'BE'):
            res[i] = ('ADJ', '形容詞（剩下的）')
        elif pj == 'PREP':
            res[i] = ('NOUN', '名詞（左邊）')
        elif k >= n:
            res[i] = ('ADV', '副詞（向左）')

    # --- 15. one ---
    for i in range(n):
        if low[i] != 'one':
            continue
        k = i + 1
        if k < n and res[k][0] == 'ADJ':
            k += 1                              # one short text
        if k < n:
            nk = res[k][0]
            nouny = nk in ('NOUN', 'PROPN') or (
                nk in ('VERB', 'AUX') and
                (low[k] in NOUN_SET or
                 (low[k] in AMBIG and 'NOUN' in AMBIG[low[k]])))
            if nouny:                           # one day / one step
                res[i] = ('NUM', '數詞（一個）')
                continue
        if res[i][0] != 'NUM':
            continue
        j = pp(i, False)
        pj = P(j) if j >= 0 else None
        if pj in ('DET', 'ADJ', 'ADV'):
            res[i] = ('PRON', '代名詞（one 代替前面提到的名詞）')

    # --- 16. 不定代名詞的所有格 everyone's ... ---
    for i in range(n):
        lw = low[i]
        if not lw.endswith("'s") or res[i][0] != 'NOUN':
            continue
        base = lw[:-2]
        if base in PRON_INDEF:
            res[i] = ('PRON', '不定代名詞所有格（' + base + chr(39) +
                      's 的）')

    # --- 17. 限定詞／形容詞後面的動詞原形其實是名詞 ---
    # （On the play night / My wish is simple / a big smile / the notice board）
    for i in range(n):
        if res[i][0] != 'VERB' or kind(low[i]) != 'base':
            continue
        j = i - 1
        if j < 0:
            continue
        if res[j][0] not in ('DET', 'ADJ') and low[j] not in _POSS_PRON:
            continue
        res[i] = ('NOUN', _note_noun(low[i]))

    # --- 18. to 後面的動詞原形（asked us to report a short news story） ---
    for i in range(n):
        if res[i][0] not in ('NOUN', 'ADJ', 'ADV') or kind(low[i]) != 'base':
            continue
        j = i - 1
        if j >= 0 and res[j][0] == 'TO':
            res[i] = ('VERB', '動詞原形')

    # --- 19. 情態動詞後面的動詞原形（a newspaper must report …） ---
    for i in range(n):
        if res[i][0] not in ('NOUN', 'ADJ', 'ADV') or kind(low[i]) != 'base':
            continue
        j = i - 1
        if j >= 0 and res[j][0] == 'AUX' and low[j] in MODAL:
            res[i] = ('VERB', '動詞原形')

    # --- 20. 主要動詞後面的 -s 字通常是受詞名詞複數 ---
    # （We printed forty tickets and left a form / I check answers）
    for i in range(n):
        if res[i][0] != 'VERB' or kind(low[i]) != 's3':
            continue
        if quoted_ahead(i):
            continue
        j = i - 1
        if j < 0 or res[j][0] != 'VERB':
            continue
        res[i] = ('NOUN', '名詞（複數）')
    return res
