

# ------------------------------------------------------- 歧義字的裁決規則
def _vm(w):
    if not w:
        return None
    return verb_morph(w)


def _is_nounish(w):
    if not w:
        return False
    return w in NOUN_SET or w in PROPN


def _is_det(w):
    return bool(w) and (w in DET_ONLY or w in DET or w in NUM_ONLY
                        or w in ('my', 'your', 'his', 'her', 'its', 'our',
                                 'their', 'a', 'an', 'the'))


def _note_noun(w):
    return '名詞（複數）' if w in NOUN_PLURAL else '名詞'


def _note_verb(w):
    v = _vm(w)
    return v[1] if v else '動詞原形'


def _disambig(lw, i, low, cls_of, at_span_start):
    n = len(low)
    prev = low[i - 1] if i > 0 else None
    nxt = low[i + 1] if i + 1 < n else None
    nxt2 = low[i + 2] if i + 2 < n else None
    cls = cls_of[i]
    cands = AMBIG.get(lw, ())

    pv = _vm(prev)
    nv = _vm(nxt)
    prev_is_verb = bool(pv) or (prev in BE_FORMS) or (prev in MODAL) \
        or (prev in DO_FORMS) or (prev in HAVE_FORMS)
    prev_is_aux_ish = (prev in BE_FORMS) or (prev in MODAL) \
        or (prev in DO_FORMS) or (prev in HAVE_FORMS) or prev == 'to'

    # ---- 新增候選組合 ----
    if lw == 'practice':
        return ('NOUN', '名詞（練習）')
    if lw == 'practise':
        return ('VERB', _note_verb(lw))

    if cands == ('ADJ', 'ADV'):
        note = '形容詞（比較級）' if lw in COMPARATIVE else '形容詞'
        if _is_nounish(nxt):
            return ('ADJ', note)
        if prev in BE_FORMS or _is_det(prev) or prev in ('more', 'most',
                                                         'very', 'so'):
            return ('ADJ', note)
        if cls == 'kw-colloc' and (_is_nounish(prev) or prev in DET_ONLY):
            return ('ADJ', note)
        anote = '副詞（比較級）' if lw in COMPARATIVE else '副詞'
        return ('ADV', anote)

    if cands == ('ADJ', 'NOUN'):
        if _is_nounish(nxt) or nxt in ADJ_SET or nxt in DET_ONLY:
            return ('ADJ', '形容詞')
        return ('NOUN', _note_noun(lw))

    if cands == ('NOUN', 'ADV'):
        if prev in PREP_ALWAYS or _is_det(prev):
            return ('NOUN', _note_noun(lw))
        if nxt in BE_FORMS or (nxt and verb_morph(nxt)):
            return ('NOUN', _note_noun(lw))
        return ('ADV', '副詞（今天；現在）')

    if cands == ('VERB', 'ADJ'):
        if _is_nounish(nxt):
            return ('ADJ', '形容詞')
        return ('VERB', _note_verb(lw))

    # ---- VERB / NOUN 兩選 ----
    if cands == ('VERB', 'NOUN'):
        if prev_is_aux_ish:
            return ('VERB', _note_verb(lw))
        if prev in PRON_SUBJ:
            # 主格代名詞後面一定是動詞（I check answers / we plan a trip）
            return ('VERB', _note_verb(lw))
        if _is_det(prev) or (prev and prev.endswith("'s")):
            return ('NOUN', _note_noun(lw))
        if _is_det(nxt) or nxt in NUM_ONLY or nxt in ('me', 'him', 'us',
                                                     'them', 'you', 'it',
                                                     'someone', 'everyone'):
            return ('VERB', _note_verb(lw))
        if cls == 'kw-verb':
            return ('VERB', _note_verb(lw))
        if cls == 'kw-colloc':
            return ('NOUN', _note_noun(lw))
        if nv and (nv[2] in ('base', 's3', 'past') or nxt in BE_FORMS):
            return ('NOUN', _note_noun(lw))      # 作主詞
        if nxt is None or nxt in ('and', 'or', 'but', 'of', 'for', 'in',
                                  'at', 'on', 'to', 'with'):
            return ('NOUN', _note_noun(lw))
        return ('VERB', _note_verb(lw))

    # ---- ADJ / VERB / ADV 三選 ----
    if cands == ('ADJ', 'VERB', 'ADV'):
        if prev_is_aux_ish:
            return ('VERB', _note_verb(lw))
        if _is_det(prev) or (prev in ADJ_SET and _is_nounish(nxt)) \
                or (prev and prev.endswith("'s")):
            if _is_nounish(nxt) or nv and nv[2] == 'base':
                return ('ADJ', '形容詞')
            return ('NOUN' if False else 'NOUN', _note_noun(lw)) \
                if lw in NOUN_SET and _is_det(prev) and not _is_nounish(nxt) \
                else ('ADJ', '形容詞')
        if prev in BE_FORMS or prev in ('become', 'became', 'seem', 'seemed',
                                        'feel', 'felt', 'look', 'looked',
                                        'taste', 'tasted', 'sound',
                                        'sounded'):
            return ('ADJ', '形容詞（作主詞補語）')
        if _is_nounish(nxt):
            # 後面直接接名詞＝形容詞位（one short text / clean clothes）
            return ('ADJ', '形容詞')
        if cls == 'kw-verb':
            return ('VERB', _note_verb(lw))
        if cls == 'kw-colloc':
            return ('ADJ', '形容詞')
        return ('ADJ', '形容詞')

    # ---- 個別字裁決 ----
    if lw == 'left':
        if cls == 'kw-verb':
            return ('VERB', _note_verb(lw))
        if _is_det(prev):
            if _is_nounish(nxt):
                return ('ADJ', '形容詞（左邊的）')
            return ('NOUN', '名詞（左邊）')
        return ('ADV', '副詞（向左）')

    if lw == 'right':
        if cls == 'kw-verb' or prev_is_aux_ish:
            return ('ADV', '副詞（向右／立刻）')
        if _is_det(prev):
            if _is_nounish(nxt):
                return ('ADJ', '形容詞（右邊的、正確的）')
            return ('NOUN', '名詞（右邊）')
        if nxt is None and prev in BE_FORMS:
            return ('INTJ', '感嘆詞（That is right 對了）')
        if _is_nounish(nxt):
            return ('ADJ', '形容詞（正確的、右邊的）')
        return ('ADV', '副詞（立刻、正好）')

    if lw == 'light':
        if cls == 'kw-verb':
            return ('VERB', _note_verb(lw))
        if _is_det(prev) and not _is_nounish(nxt):
            return ('NOUN', '名詞（光；燈）')
        if _is_nounish(nxt) or (prev in ADJ_SET):
            return ('ADJ', '形容詞（淺色的、輕的）')
        return ('NOUN', '名詞（光；燈）')

    if lw == 'back':
        if _is_det(prev) or (prev in ADJ_SET):
            return ('NOUN', '名詞（背面、後面）')
        if prev in PREP_ALWAYS:
            return ('NOUN', '名詞（後面）')
        return ('ADV', '副詞（回來、往後）')

    if lw == 'home':
        if prev in PREP_ALWAYS or _is_det(prev):
            return ('NOUN', '名詞（家）')
        return ('ADV', '副詞（回家、在家）')

    if lw == 'well':
        if at_span_start and prev is None:
            return ('INTJ', '感嘆詞（Well,… 嗯）')
        if prev in BE_FORMS:
            return ('ADJ', '形容詞（健康的）')
        if _is_nounish(nxt) and _is_det(prev):
            return ('NOUN', '名詞（井）')
        return ('ADV', '副詞（好好地）')

    if lw == 'enough':
        if _is_nounish(nxt):
            return ('DET', '限定詞（enough 足夠的，修飾名詞）')
        if prev and prev in ADJ_SET:
            return ('ADV', '副詞（足夠地，修飾形容詞／副詞）')
        return ('ADV', '副詞（足夠地）')

    if lw == 'one':
        if nxt == 'of':
            return ('PRON', '代名詞（代替上文提過的名詞）')
        if _is_nounish(nxt) or nxt in ADJ_SET:
            return ('NUM', '數詞（一個）')
        if _is_det(prev) or prev in ADJ_SET:
            return ('PRON', '代名詞（代替上文提過的名詞）')
        return ('NUM', '數詞（一個）')

    if lw == 'half':
        if nxt == 'of':
            return ('PRON', '代名詞（一半）')
        if _is_nounish(nxt) or _is_det(nxt):
            return ('NUM', '數詞（一半）')
        return ('NOUN', '名詞（一半）')

    if lw == 'quarter':
        if _is_nounish(nxt):
            return ('NUM', '數詞（四分之一）')
        return ('NOUN', '名詞（一刻鐘、四分之一）')

    if lw == 'first':
        if _is_nounish(nxt):
            return ('ADJ', '序數形容詞（第一的）')
        if prev in PREP_ALWAYS or prev in ('the', 'at', 'in'):
            return ('ADV', '副詞（起初、首先）')
        if nxt is None and at_span_start:
            return ('ADV', '副詞（首先、第一步）')
        return ('ADJ', '序數形容詞（第一的）')

    if lw == 'second':
        if _is_nounish(nxt):
            return ('ADJ', '序數形容詞（第二的）')
        if _is_det(prev):
            return ('NOUN', '名詞（秒）')
        return ('NUM', '數詞（第二）')

    if lw == 'fifth':
        if _is_nounish(nxt):
            return ('ADJ', '序數形容詞（第五的）')
        return ('NUM', '序數（第五）')

    if lw == 'last':
        if _is_nounish(nxt) or nxt in ('summer', 'night', 'week', 'year',
                                       'month', 'term', 'saturday', 'sunday',
                                       'monday', 'friday', 'morning',
                                       'evening', 'afternoon', 'time',
                                       'winter', 'autumn', 'spring'):
            return ('ADJ', '形容詞（上一個的、最近的）')
        if prev in PREP_ALWAYS:
            return ('ADV', '副詞（最後）')
        if nxt is None or nxt in ('day', 'but', 'finally'):
            return ('ADJ', '形容詞（最後的）')
        return ('ADJ', '形容詞（最近的、上一個的）')

    if lw == 'next':
        if nxt == 'to':
            return ('PREP', '介系詞（next to 緊鄰、在…旁邊）')
        if _is_nounish(nxt) or nxt in ('monday', 'friday', 'saturday',
                                       'sunday', 'week', 'month', 'year',
                                       'summer', 'term', 'time', 'morning',
                                       'evening', 'night', 'day'):
            return ('ADJ', '形容詞（下一個的）')
        if nxt is None:
            return ('ADV', '副詞（接下來）')
        return ('ADV', '副詞（接下來）')

    if lw == 'only':
        if _is_nounish(nxt):
            return ('ADJ', '形容詞（唯一的）')
        return ('ADV', '副詞（只、僅僅）')

    if lw == 'best':
        if _is_nounish(nxt):
            return ('ADJ', '形容詞最高級（最好的）')
        return ('ADV', '副詞（最）')

    if lw == 'better':
        if _is_nounish(nxt):
            return ('ADJ', '形容詞比較級（較好的）')
        if prev in BE_FORMS or prev in ('much', 'a', 'bit', 'far'):
            return ('ADJ', '形容詞比較級（較好的）')
        return ('ADV', '副詞（較好地）')

    if lw in ('more', 'most', 'less'):
        if _is_nounish(nxt):
            return ('DET', '限定詞（較多的／最多的）')
        if prev in ('the', 'a', 'an') and nxt is None:
            return ('PRON', '代名詞（較多的人或事物）')
        return ('ADV', '副詞（更、最）')

    if lw in ('all', 'some', 'any', 'both', 'each', 'either', 'neither',
              'many', 'few', 'no', 'other', 'whole', 'such'):
        if nxt == 'of':
            return ('PRON', '代名詞（指前面提過的人或事物）')
        if lw == 'no' and at_span_start and nxt is None:
            return ('INTJ', '感嘆詞（No 不）')
        if _is_nounish(nxt) or nxt in ADJ_SET or _is_det(nxt) or nxt in NUM_ONLY:
            return ('DET', '限定詞（修飾後面的名詞）')
        if lw == 'such':
            return ('DET', '限定詞（such 這樣的）')
        if lw in ('many', 'few', 'both', 'each', 'either', 'neither'):
            return ('DET', '限定詞（修飾後面的名詞）')
        return ('PRON', '代名詞（指不特定的人或事物）')

    if lw in ('little', 'much'):
        if _is_nounish(nxt):
            return ('DET', '限定詞（少的／多的，修飾名詞）')
        if prev in ('too', 'so', 'very', 'as', 'more'):
            return ('ADV', '副詞（太、很）')
        return ('ADV', '副詞（後置修飾形容詞／副詞）')

    if lw == 'own':
        if _is_det(prev) or prev in ('my', 'your', 'his', 'her', 'its',
                                     'our', 'their'):
            return ('ADJ', '形容詞（自己的）')
        return ('VERB', _note_verb(lw))

    if lw == 'plenty':
        if nxt == 'of':
            return ('PRON', '代名詞（plenty of 中的先行詞）')
        return ('ADV', '副詞（足夠地）')

    # ---- 介系詞／連接詞／副詞的裁決 ----
    if lw in ('after', 'before', 'since', 'until'):
        if nxt in PRON_SUBJ:
            return ('SCONJ', '從屬連接詞（引導副詞子句）')
        if nv and nv[2] in ('ing', 'pp', 'past'):
            return ('PREP', '介系詞（後接動名詞片語）')
        if nv and nv[2] in ('base', 's3', 'past', 'pp'):
            if nxt in NOUN_SET:   # 也可能是名詞
                pass
            else:
                return ('SCONJ', '從屬連接詞（引導副詞子句）')
        if nxt2 and (nxt2 in PRON_SUBJ
                     or (_vm(nxt2) and _vm(nxt2)[2] in ('base', 's3', 'past'))):
            return ('SCONJ', '從屬連接詞（引導副詞子句）')
        return ('PREP', '介系詞（後接名詞片語）')

    if lw in ('down', 'up', 'out', 'off', 'over', 'past', 'inside',
              'outside', 'about', 'around', 'along'):
        if _is_det(nxt) or _is_nounish(nxt) or nxt in NUM_ONLY:
            return ('PREP', '介系詞（後接名詞片語）')
        return ('ADV', '副詞（與動詞形成片語動詞）')

    if lw == 'near':
        if _is_det(nxt) or _is_nounish(nxt):
            return ('PREP', '介系詞（near 在…附近）')
        return ('ADJ', '形容詞（近的）')

    if lw == 'so':
        if nxt and nxt in ADJ_SET:
            return ('ADV', '副詞（so 如此、這麼）')
        if nxt and nxt in ADV_SET:
            return ('ADV', '副詞（so 那麼）')
        return ('CONJ', '對等連接詞（so 所以）')

    if lw == 'as':
        if at_span_start:
            return ('SCONJ', '從屬連接詞（as 當…時／一…就…）')
        if prev and (prev in ADJ_SET or prev in ADV_SET or _vm(prev)):
            if nxt and (nxt in NOUN_SET or nxt in DET or nxt in PROPN):
                return ('PREP', '介系詞（as 作為）')
            return ('SCONJ', '從屬連接詞（as…as 中第二個 as）')
        if nxt and (nxt in NOUN_SET or nxt in DET or nxt in PROPN):
            return ('PREP', '介系詞（as 作為、當作）')
        return ('ADV', '副詞（as…as 中第一個 as）')

    if lw == 'that':
        if nxt in DET_ONLY or _is_nounish(nxt):
            return ('DET', '限定詞（that 那個）')
        if prev in REPORT_VERB:
            return ('SCONJ', '從屬連接詞（引導名詞子句）')
        if prev in ('is', 'was', 'are', 'were', 'am', 'be', 'very', 'so'):
            return ('SCONJ', '從屬連接詞（引導名詞子句）')
        if prev and (_is_nounish(prev) or prev in PRON_SUBJ
                     or prev in PRON_OBJ or prev in ('its', 'their', 'my',
                                                     'your', 'his', 'her',
                                                     'our')):
            return ('PRON', '代名詞（關係代名詞，引導關係子句）')
        if at_span_start:
            return ('SCONJ', '從屬連接詞（引導名詞子句）')
        return ('PRON', '代名詞（指示代名詞）')

    if lw in ('this', 'these', 'those'):
        if _is_nounish(nxt) or nxt in ADJ_SET or nxt in NUM_ONLY:
            return ('DET', '限定詞（指示形容詞，修飾後面的名詞）')
        return ('PRON', '代名詞（指示代名詞）')

    if lw == 'what':
        if _is_nounish(nxt) or nxt in ADJ_SET:
            return ('DET', '限定詞（what 什麼樣的）')
        return ('PRON', '代名詞（疑問代名詞／名詞子句的主詞）')

    if lw == 'which':
        if _is_nounish(nxt) or nxt in ADJ_SET or nxt in NUM_ONLY:
            return ('DET', '限定詞（which 哪一個）')
        return ('PRON', '代名詞（關係代名詞／疑問代名詞）')

    if lw == 'there':
        if nxt in BE_FORMS:
            return ('PRON', '引詞（there is/are 句型中的虛主詞）')
        return ('ADV', '副詞（there 在那裡）')

    if lw in AMBIG:
        if cands:
            c = cands[0]
            if lw in ('spare', 'enough', 'plenty'):
                return (c, '形容詞（多餘的、備用的）' if c == 'ADJ'
                        else {'DET': '限定詞（足夠的，修飾後面的名詞）',
                              'ADV': '副詞（足夠地）'}.get(c, '詞語'))
            if lw == 'whatever':
                return (c, '限定詞（whatever 無論什麼，修飾後面的名詞）'
                        if c == 'DET' else '代名詞（whatever 無論什麼）')
            return (c, {'ADJ': '形容詞', 'NOUN': '名詞', 'VERB': '動詞原形',
                        'DET': '限定詞（修飾後面的名詞）', 'ADV': '副詞',
                        'PRON': '代名詞', 'PREP': '介系詞',
                        'NUM': '數詞', 'AUX': '助動詞'}.get(c, '詞語'))
    return ('X', '未標記')
