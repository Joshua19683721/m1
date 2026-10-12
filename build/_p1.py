# -*- coding: utf-8 -*-
"""逐字詞性分析核心（Alt+Z「單字結構與詞性對照」面板的資料來源）

每個 w-tap span 會得到：
  data-pos  片語中心詞的詞性（舊欄位，保留相容）
  data-func 片語在該句中的句法功能
  data-w    片語內每一個字的逐字分析  [[字, POS, 中文說明], ...]

說明文字採 108 課綱／國高中文法名詞。
"""
import re

TOKEN = re.compile(r"[A-Za-z]+(?:['\u2019][A-Za-z]+)?|\d+")


def tokens(s):
    return [t.replace('\u2019', "'") for t in TOKEN.findall(s or '')]


# ------------------------------------------------------------------ 基本集合
PREP_ALWAYS = set("""about above across along among around at beside between by
    during except for from in inside into near of off on onto out outside over
    past through throughout toward under with without unlike worth plus per via
    amid""".split())

CONJ = set(["and", "but", "or", "nor", "yet"])

DET = set("""a an the this that these those my your his her its our their
    every each all some any no another both either neither much many several
    few little such what which whose own whatever""".split())

NUM = set("""one two three four five six seven eight nine ten eleven twelve
    thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
    thirty forty fifty sixty seventy eighty ninety hundred thousand first
    second third fourth fifth sixth seventh eighth ninth tenth twelfth
    twentieth""".split())

PRON_SUBJ = set(["i", "you", "he", "she", "we", "they"])
PRON_OBJ = set(["me", "him", "her", "us", "them", "you"])
PRON_POSS = set(["mine", "yours", "hers", "ours", "theirs"])
PRON_REFL = set(["myself", "yourself", "himself", "herself", "itself",
                 "ourselves", "themselves"])
PRON_INDEF = set(["everyone", "everybody", "everything", "anyone", "anybody",
                  "anything", "nobody", "nothing", "somebody", "someone",
                  "something", "others"])

PROPN = set("""monday tuesday wednesday thursday friday saturday sunday january
    february march april may june july august september october november
    december english japan taipei ken lily mei nina tom lee chen wu mr mrs
    ms dr""".split())

MODAL = set(["can", "cannot", "could", "may", "might", "must", "shall",
             "should", "will", "would", "ought", "need", "dare"])
BE_FORMS = set(["am", "is", "are", "was", "were", "be", "been", "being"])
DO_FORMS = set(["do", "does", "did", "don't", "doesn't", "didn't"])
HAVE_FORMS = set(["have", "has", "had", "haven't", "hasn't", "hadn't"])

NEG = set(["not", "n't"])

LINKER_WORDS = set("""however therefore instead otherwise besides indeed also
    moreover anyway thus hence then next finally meanwhile second first
    afterwards moreover instead however therefore""".split())

# ---------------------------------------------------------------- 動詞形式表
IRREG = {
    "be": ("was", "been", "is", "being"),
    "become": ("became", "became", "becomes", "becoming"),
    "begin": ("began", "begun", "begins", "beginning"),
    "break": ("broke", "broken", "breaks", "breaking"),
    "bring": ("brought", "brought", "brings", "bringing"),
    "build": ("built", "built", "builds", "building"),
    "buy": ("bought", "bought", "buys", "buying"),
    "choose": ("chose", "chosen", "chooses", "choosing"),
    "come": ("came", "come", "comes", "coming"),
    "cut": ("cut", "cut", "cuts", "cutting"),
    "do": ("did", "done", "does", "doing"),
    "draw": ("drew", "drawn", "draws", "drawing"),
    "drink": ("drank", "drunk", "drinks", "drinking"),
    "eat": ("ate", "eaten", "eats", "eating"),
    "fall": ("fell", "fallen", "falls", "falling"),
    "feel": ("felt", "felt", "feels", "feeling"),
    "find": ("found", "found", "finds", "finding"),
    "fly": ("flew", "flown", "flies", "flying"),
    "forget": ("forgot", "forgotten", "forgets", "forgetting"),
    "get": ("got", "gotten", "gets", "getting"),
    "give": ("gave", "given", "gives", "giving"),
    "go": ("went", "gone", "goes", "going"),
    "grow": ("grew", "grown", "grows", "growing"),
    "have": ("had", "had", "has", "having"),
    "hear": ("heard", "heard", "hears", "hearing"),
    "hold": ("held", "held", "holds", "holding"),
    "keep": ("kept", "kept", "keeps", "keeping"),
    "know": ("knew", "known", "knows", "knowing"),
    "leave": ("left", "left", "leaves", "leaving"),
    "lend": ("lent", "lent", "lends", "lending"),
    "let": ("let", "let", "lets", "letting"),
    "lose": ("lost", "lost", "loses", "losing"),
    "make": ("made", "made", "makes", "making"),
    "mean": ("meant", "meant", "means", "meaning"),
    "meet": ("met", "met", "meets", "meeting"),
    "pay": ("paid", "paid", "pays", "paying"),
    "put": ("put", "put", "puts", "putting"),
    "read": ("read", "read", "reads", "reading"),
    "run": ("ran", "run", "runs", "running"),
    "say": ("said", "said", "says", "saying"),
    "see": ("saw", "seen", "sees", "seeing"),
    "sell": ("sold", "sold", "sells", "selling"),
    "send": ("sent", "sent", "sends", "sending"),
    "shine": ("shone", "shone", "shines", "shining"),
    "show": ("showed", "shown", "shows", "showing"),
    "sit": ("sat", "sat", "sits", "sitting"),
    "sleep": ("slept", "slept", "sleeps", "sleeping"),
    "speak": ("spoke", "spoken", "speaks", "speaking"),
    "spend": ("spent", "spent", "spends", "spending"),
    "stand": ("stood", "stood", "stands", "standing"),
    "take": ("took", "taken", "takes", "taking"),
    "teach": ("taught", "taught", "teaches", "teaching"),
    "tell": ("told", "told", "tells", "telling"),
    "think": ("thought", "thought", "thinks", "thinking"),
    "understand": ("understood", "understood", "understands", "understanding"),
    "wake": ("woke", "woken", "wakes", "waking"),
    "wear": ("wore", "worn", "wears", "wearing"),
    "win": ("won", "won", "wins", "winning"),
    "write": ("wrote", "written", "writes", "writing"),
}

V_BASE, V_PAST, V_PP, V_S3, V_ING = set(), set(), set(), set(), set()
for _b, (_p, _q, _t, _g) in IRREG.items():
    V_BASE.add(_b); V_PAST.add(_p); V_PP.add(_q); V_S3.add(_t); V_ING.add(_g)

# 規則變化動詞（原形）
REGULAR_VERBS = set("""
    add agree announce answer arrive ask borrow call carry change check cheer
    click close compare count dance decide delay describe drop earn email enjoy
    expect explain finish follow greet guess help hope imagine improve join
    jump laugh learn like listen love mark mention miss move notice offer
    organise pack paint pass plan practise prepare prevent pronounce reach
    receive recommend remember repair report return rush save share shout smile
    smell sound spell start stay stop suggest support talk taste thank travel
    try turn use visit wait walk want warn wash watch weigh wish worry
    practise cook fill pick pull play watch look discuss reply realise
    realise pronounce practise decide finish clean mention expect happen
""".split())
REGULAR_VERBS -= V_BASE


def verb_morph(w):
    """若是動詞形式，回傳 (POS, 中文說明, 類型)；否則 None。"""
    lw = (w or '').lower()
    if lw in IRREG:
        p, q, t, g = IRREG[lw]
        if lw == t and lw != p:
            return ('VERB', '動詞第三人稱單數現在式', 's3')
        if lw == g and lw not in V_BASE and lw != p:
            return ('VERB', '現在分詞／動名詞', 'ing')
        if lw == p and lw == q:
            return ('VERB', '動詞過去式／過去分詞', 'past')
        if lw == p:
            return ('VERB', '動詞過去式', 'past')
        if lw == q:
            return ('VERB', '動詞過去分詞', 'pp')
        if lw in V_BASE:
            return ('VERB', '動詞原形', 'base')
        return ('VERB', '動詞形式', 'base')
    if lw in V_BASE:
        return ('VERB', '動詞原形', 'base')
    if lw in V_PAST:
        return ('VERB', '動詞過去式', 'past')
    if lw in V_PP:
        return ('VERB', '動詞過去分詞', 'pp')
    if lw in V_S3:
        return ('VERB', '動詞第三人稱單數現在式', 's3')
    if lw in V_ING:
        return ('VERB', '現在分詞／動名詞', 'ing')
    if lw in REGULAR_VERBS:
        return ('VERB', '動詞原形', 'base')
    if lw.endswith('ed') and len(lw) > 3:
        return ('VERB', '動詞過去式／過去分詞', 'past')
    if lw.endswith('ing') and len(lw) > 5:
        return ('VERB', '現在分詞／動名詞', 'ing')
    if lw.endswith('s') and len(lw) > 3:
        return ('VERB', '動詞第三人稱單數現在式', 's3')
    return None

# ---- 補充不規則／規則動詞 ----
IRREG['shake'] = ('shook', 'shaken', 'shakes', 'shaking')
IRREG['hurt'] = ('hurt', 'hurt', 'hurts', 'hurting')
for _b2, (_p2, _q2, _t2, _g2) in (('shake', IRREG['shake']),
                                   ('hurt', IRREG['hurt'])):
    V_BASE.add(_b2)
    V_PAST.add(_p2)
    V_PP.add(_q2)
    V_S3.add(_t2)
    V_ING.add(_g2)

REGULAR_VERBS |= set("""answer break brush change check chat clean close colour
copy count end fit form help hope jump keep label link list look love mark
matter move need note order pack paint part pass pay phone plan place point
post practice quiz race rain repair rest review rule run share shift show
start step stop study support talk taste test train travel treat turn use
visit wait walk wash water work worry book coach park beat sound like excuse
rent download disappear hide disappear greet invite measure practise""".split())
REGULAR_VERBS -= V_BASE
