

# ------------------------------------------------------------ 句子結構解析
SPAN_RE = re.compile(r'<span class="(w-tap[^"]*)"([^>]*)>(.*?)</span>', re.S)
TAG_RE = re.compile(r'<[^>]+>')

_ENTS = (('&nbsp;', ' '), ('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'),
         ('&quot;', '"'), ('&#39;', "'"), ('&ldquo;', '"'), ('&rdquo;', '"'),
         ('&lsquo;', "'"), ('&rsquo;', "'"))


def _plain(s):
    s = TAG_RE.sub(' ', s or '')
    for a, b in _ENTS:
        s = s.replace(a, b)
    return s


CONTRACTION_ROWS = {
    "i'm": [("I", 'PRON', '主格代名詞（I，作主詞）'),
            ("'m", 'BE', "be 動詞 am 的縮寫")],
    "i've": [("I", 'PRON', '主格代名詞（I，作主詞）'),
             ("'ve", 'AUX', '助動詞 have 的縮寫')],
    "i'll": [("I", 'PRON', '主格代名詞（I，作主詞）'),
             ("'ll", 'AUX', '助動詞 will 的縮寫')],
    "i'd": [("I", 'PRON', '主格代名詞（I，作主詞）'),
            ("'d", 'AUX', '助動詞 would 的縮寫')],
    "we're": [("we", 'PRON', '主格代名詞（we，作主詞）'),
              ("'re", 'BE', 'be 動詞 are 的縮寫')],
    "you're": [("you", 'PRON', '主格代名詞（you，作主詞）'),
               ("'re", 'BE', 'be 動詞 are 的縮寫')],
    "they're": [("they", 'PRON', '主格代名詞（they，作主詞）'),
                ("'re", 'BE', 'be 動詞 are 的縮寫')],
    "let's": [("let", 'VERB', '動詞原形（let 讓）'),
              ("'s", 'PRON', "us 的縮寫：受格代名詞（we 的受格）")],
}
_SIMPLE_CONTR = {
    'he': ('PRON', '主格代名詞（he，作主詞）'),
    'she': ('PRON', '主格代名詞（she，作主詞）'),
    'it': ('PRON', '代名詞（it，主格／受格同形）'),
    'that': ('PRON', '代名詞（that 那個）'),
    'there': ('PRON', '引詞（there is/are 句型的虛主詞）'),
    'who': ('PRON', '代名詞（疑問代名詞，指人）'),
    'what': ('PRON', '代名詞（疑問代名詞）'),
}
_CONTR_SUFFIX = {
    "'s": ('BE', 'be 動詞 is 的縮寫'),
    "'re": ('BE', 'be 動詞 are 的縮寫'),
    "'ve": ('AUX', '助動詞 have 的縮寫'),
    "'ll": ('AUX', '助動詞 will 的縮寫'),
    "'d": ('AUX', '助動詞 would 的縮寫'),
    "'m": ('BE', 'be 動詞 am 的縮寫'),
}


def expand_rows(word, pos, note):
    """把縮寫拆成逐字列。"""
    w = word
    if w in CONTRACTION_ROWS:
        return list(CONTRACTION_ROWS[w])
    if w in PRON_CONTRACTION and "'" in w:
        base, suf = w.split("'", 1)
        suf = "'" + suf
        if base in _SIMPLE_CONTR and suf in _CONTR_SUFFIX:
            bp, bn = _SIMPLE_CONTR[base]
            sp, sn = _CONTR_SUFFIX[suf]
            return [(base, bp, bn), (suf, sp, sn)]
    return [(word, pos, note)]


HEAD_ORDER = ('VERB', 'AUX', 'BE', 'TO')


def head_pos(pos_seq):
    for want in HEAD_ORDER:
        for p in pos_seq:
            if p == want:
                return p
    for want in ('NOUN', 'PROPN', 'PRON'):
        for p in pos_seq:
            if p == want:
                return want
    for want in ('ADJ', 'NUM', 'DET', 'PREP', 'SCONJ', 'CONJ', 'ADV',
                'INTJ'):
        for p in pos_seq:
            if p == want:
                return want
    return 'X'


def _is_finite(res, low, i):
    """第 i 個字是否為限定動詞（可作述語）。"""
    if i > 0 and low[i - 1] == 'to' and res[i - 1][0] == 'TO':
        return False
    p = res[i][0]
    if p in ('BE', 'AUX'):
        return True
    if p != 'VERB':
        return False
    vm = verb_morph(low[i])
    kind = vm[2] if vm else 'base'
    return kind in ('past', 's3', 'base')


def span_function(pos_seq, word_seq, cls, sent_initial, appositive,
                  precedes_finite, finite_in_span, prev_is_linking,
                  follows_report, prev_word, has_verb, there_be=False):
    first_pos = pos_seq[0] if pos_seq else 'X'
    first_word = (word_seq[0] or '').lower() if word_seq else ''
    pw = (prev_word or '').lower()

    if appositive:
        return 'appositive'
    if there_be:
        return 'subject'
    if first_pos == 'PREP':
        return 'prep_phrase'
    if first_pos == 'CONJ':
        return 'linker'
    if first_pos == 'SCONJ':
        if first_word in ('that', 'what', 'whether') or follows_report \
                or pw in REPORT_VERB:
            return 'clause_noun'
        return 'clause_adv'
    if first_word in ('what', 'who', 'whom', 'which', 'whose') \
            and first_pos in ('PRON', 'DET') and has_verb:
        if first_word != 'what' and (pw in NOUN_SET or pw in PROPN
                                     or pw in PRON_INDEF
                                     or pw.endswith("'s")):
            return 'clause_rel'
        return 'clause_noun'
    if first_word == 'that' and first_pos == 'PRON' and has_verb \
            and not sent_initial:
        if pw in NOUN_SET or pw in PROPN or pw in PRON_INDEF \
                or pw.endswith("'s"):
            return 'clause_rel'
        return 'clause_noun'
    if 'SCONJ' in pos_seq and cls == 'kw-link':
        # even if / only if 等：連接詞不在字首
        if follows_report or pw in REPORT_VERB or pw in ('', 'is', 'was',
                                                         'are', 'were'):
            return 'clause_noun'
        return 'clause_adv'
    if cls == 'kw-link' and sent_initial and has_verb:
        return 'clause_adv'
    if finite_in_span:
        return 'predicate'
    if prev_is_linking and not has_verb:
        return 'complement'
    if 'TO' in pos_seq:
        if precedes_finite:
            return 'subject'
        return 'complement' if prev_is_linking else 'object'
    if has_verb:
        return 'subject' if precedes_finite else 'object'
    if cls == 'kw-link' and not sent_initial:
        return 'adjunct'
    if first_pos == 'ADV':
        if any(p in ('NOUN', 'PRON', 'DET', 'PROPN', 'NUM') for p in pos_seq):
            if precedes_finite:
                return 'subject'
            if prev_is_linking:
                return 'complement'
            if cls == 'kw-link' and sent_initial:
                return 'adjunct'
            return 'object'
        if first_word in LINKER_WORDS:
            return 'linker'
        if len(pos_seq) == 1:
            return 'adjunct'
        return 'adjunct' if cls == 'kw-link' else 'adv_phrase'
    if first_pos == 'INTJ':
        return 'interjection'
    if first_pos in ('NOUN', 'PROPN', 'PRON', 'DET', 'NUM', 'ADJ'):
        if cls == 'kw-link' and sent_initial:
            return 'adjunct'
        if precedes_finite:
            return 'subject'
        if prev_is_linking:
            return 'complement'
        if cls == 'kw-link':
            return 'adjunct'
        return 'object'
    return 'unknown'


def _flatten(html):
    """把句子切成 token 序列，同時記錄每個 token 所屬的 span。

    回傳 (flat, cls_of, span_first, ranges, meta, groups)：
      flat       = 全句所有字（含 span 外的一般文字）
      cls_of     = 每個字所屬的 span 類別（不屬於任何 span 則為 None）
      span_first = 每個 span 第一個字的 index
      ranges     = 每個 span 在 flat 中的 (起, 止)
      meta       = 每個 span 的 (cls, attrs, inner, 起始字元, 結束字元)
      groups     = (起, 止, group_id)，group_id = -1 表示不屬於任何 span
    """
    segs = []
    meta = []
    p = 0
    for m in SPAN_RE.finditer(html):
        segs.append(('text', html[p:m.start()]))
        segs.append(('span', len(meta)))
        _c = m.group(1).replace('w-tap', '', 1).strip()
        meta.append((_c, m.group(2), m.group(3), m.start(), m.end()))
        p = m.end()
    segs.append(('text', html[p:]))

    flat, cls_of = [], []
    span_first = set()
    ranges = [None] * len(meta)
    groups = []
    for item in segs:
        if item[0] == 'text':
            st = len(flat)
            for t in tokens(_plain(item[1])):
                flat.append(t)
                cls_of.append(None)
            if len(flat) > st:
                groups.append((st, len(flat), -1))
        else:
            sid = item[1]
            cls, attrs, inner, hs, he = meta[sid]
            st = len(flat)
            for k, t in enumerate(tokens(_plain(inner))):
                flat.append(t)
                cls_of.append(cls)
                if k == 0:
                    span_first.add(len(flat) - 1)
            ranges[sid] = (st, len(flat))
            if len(flat) > st:
                groups.append((st, len(flat), sid))
    return flat, cls_of, span_first, ranges, meta, groups


def analyze_full(html):
    """分析句子裡【每一個字】（包含 span 外面的一般文字）。

    回傳 (rows, funcs)：
      rows  = [(字, 詞性, 中文說明, group_id), ...]，依句子裡的先後順序
      funcs = [該 span 的句法功能 key, ...]，以 span index 索引
      group_id = -1 表示這個字不屬於任何已標註的片語
    """
    spans = analyze_sentence(html)
    flat, cls_of, span_first, ranges, meta, groups = _flatten(html)
    if not meta or not flat:
        return [], []
    res = tag_all(flat, span_first, cls_of)
    rows = []
    for st, en, g in groups:
        for k in range(st, en):
            for w, p_, n_ in expand_rows(flat[k], res[k][0], res[k][1]):
                rows.append((w, p_, n_, g))
    funcs = [s.get('func') or '' for s in spans]
    return rows, funcs


def analyze_sentence(html):
    """分析一個句子的 HTML，回傳 span 分析結果 list。"""
    flat, cls_of, span_first, ranges, meta, groups = _flatten(html)
    if not meta:
        return []

    res = tag_all(flat, span_first, cls_of)
    low = [t.lower() for t in flat]
    n = len(flat)

    finite_idx = None
    for i in range(n):
        if _is_finite(res, low, i):
            finite_idx = i
            break

    out = []
    for sid, (cls, attrs, inner, hs, he) in enumerate(meta):
        start, end = ranges[sid]
        if end <= start:
            out.append({'cls': cls, 'text': '', 'pos': 'X',
                        'func': 'unknown', 'rows': [], 'sent': html})
            continue
        pos_seq = [res[k][0] for k in range(start, end)]
        note_seq = [res[k][1] for k in range(start, end)]
        word_seq = flat[start:end]

        rows = []
        for k in range(start, end):
            rows.extend(expand_rows(flat[k], res[k][0], res[k][1]))

        pre_txt = _plain(html[:hs]).rstrip()
        post_txt = _plain(html[he:]).lstrip()
        appositive = pre_txt.endswith(',') and post_txt.startswith(',')
        sent_initial = pre_txt.strip() == '' or \
            re.sub(r'[\s,;:.!\-–—?\'"]+', '', pre_txt) == ''
        prev_word = low[start - 1] if start > 0 else ''
        follows_report = prev_word in REPORT_VERB
        precedes_finite = finite_idx is None or end <= finite_idx
        finite_in_span = any(_is_finite(res, low, k)
                             for k in range(start, end))
        has_verb = any(p in ('VERB', 'BE', 'AUX') for p in pos_seq)
        j = start - 1
        while j >= 0 and res[j][0] == 'ADV':
            j -= 1
        prev_is_linking = (j >= 0 and low[j] in LINKING)

        func = span_function(pos_seq, word_seq, cls, sent_initial,
                             appositive, precedes_finite, finite_in_span,
                             prev_is_linking, follows_report, prev_word,
                             has_verb,
                             start >= 2 and low[start - 2] == 'there'
                             and low[start - 1] in BE_FORMS)
        out.append({
            'cls': cls,
            'text': _plain(inner).strip(),
            'pos': head_pos(pos_seq),
            'func': func,
            'rows': rows,
            'sent': html,
        })
    return out


FUNC_LABEL = {
    'subject': '主詞',
    'predicate': '述語（主要動詞）',
    'object': '受詞',
    'complement': '主詞補語',
    'adjunct': '狀語（修飾語）',
    'appositive': '同位語',
    'prep_phrase': '介系詞片語',
    'adv_phrase': '副詞片語',
    'clause_adv': '副詞子句（從屬子句）',
    'clause_noun': '名詞子句',
    'clause_rel': '關係子句',
    'linker': '連接語（轉折／承接）',
    'interjection': '感嘆語',
    'unknown': '未標記',
}
