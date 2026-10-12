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


# -------------------------------------------------- 名詞／形容詞／副詞詞庫
NOUN_SET = set("""
address advertisement advice afternoon album ambulance apartment app armchairs
article assistant aunt bag bags bank basket basketball bathroom beach bed
bedrooms beginning bill bin birds board book books boss bottle bottles bowl box
boxes breakfast bridge brother bus cafe cake camera campsite card centre chat
child childhood cinema city class classmate classmates classroom clock cloth
clothes clouds club coach coast coat coffee colours computer cooker corner
costumes country course cousin cream cup cups curtains customer danger date
daughter day days difference dining dinner door draft drama driver egg
electricity effort end ending exam example eyes fact facts family farm farmer
father festival fever fields file floor floors flour food foot forest forks
form front fruit game games gas gate gift girl glasses grandfather grandmother
grandparents group groups guest gym hall handbag hands handwriting headache
heating hobby home homework hospital hotel hour hours house idea information
ingredients island item jacket jeans job journey juice keyboard kind kinds
kitchen knife label lake lamp lesson lessons library list litre locker lunch
machine magazine manager map market maths member members message milk
millilitres minutes mirror mistake mistakes moment money monitor month months
mountain mountains mouse museum music name names necklace news newspaper night
noise noodles noon note notebook notebooks notes number nurse ocean office
opinion oven page pain paper parents part partner password path patients
patterns people petrol photo photograph photographs photography photos picnic
pictures pilot place plate platform player players pocket points police pool post
postcards pounds practice presentation price prize problem progress project quiz
race railway rain raincoat repairman report responsibility result river rivers
room rubbish rule ruler rules sale sandwich sandwiches scale scarf scene school
science scientist screen sea sentence sentences shape shelves shift shirt
sister size skirt sky sofa software source speech stairs staircase staff stomach
storm story street subject summer sun supermarket table taxi teacher team
teenager temperature tent tents term test text textbook throat time times tool
tools top town traffic train trainers training trip trophy trousers unit
university uniform village voice voices volunteer wall walls water way web
website week weekend weekends weeks weight window windows winter winner winners
word words work worker year years yuan stomachache
""".split())
NOUN_PLURAL = set(w for w in NOUN_SET if w.endswith('s'))

ADJ_SET = set("""
afraid angry asleep bare big black blue bored boring brave bright brilliant
busy careful cheap clear cloudy cold comfortable cool dangerous dark delicious
different dirty easy expensive excited exciting fine fresh friendly full funny
glad golden good great green grey happy heavy high hot hungry important
interesting ill kind large late local long loud lovely lucky main meaningful
narrow nervous new nice noisy old pale pink polite poor pretty proud quiet
ready rich rude sad safe same scared short shy simple small soft sore special
strange strong successful sure sweet tall terrible thin tight tired true ugly
uncomfortable unhappy unkind useful warm white wide windy wonderful wrong
young youngest yellow extra flat round sunny cloudy empty tasty tidy
""".split())

ADV_SET = set("""
actually again almost alone aloud already also always away badly carefully
completely exactly extremely far heavily here however loudly never now often
politely quite rather really slowly sometimes soon still straight suddenly
together twice upstairs usually very instead then even further earlier sooner
later together elsewhere ago ago indeed certainly probably perhaps obviously
clearly simply merely ever meanwhile therefore hence otherwise besides
""".split())

# 比較級／最高級：形容詞或副詞兩可
COMPARATIVE = set("""faster easier harder higher smaller slower lighter
stronger faster quicker nearer cheaper wider shorter longer darker clearer
sooner further better best worse worst least closer deeper quicker fatter
""".split())

# ---- 補充詞庫（逐字檢視後補入） ----
NOUN_SET |= set("""age comma competition dentist desk diary dictionary doctor
exercise fridge friend future hat ice internet key letter lot medicine mother
neighbour pair question recipe restaurant road schedule shop song station
stationery student sugar survey television tourist tree uncle weather wood
cartoon cabbage shelf corner chance memory journey garden letter""".split())
NOUN_PLURAL |= set(w for w in NOUN_SET if w.endswith('s'))

ADJ_SET |= set("""calm direct favourite final mobile real sorry single weak wet
wooden likely silver comfortable delicious delicious""".split())

ADV_SET |= set("""proudly quietly too furthermore moreover"""
                .split())

INTJ_SET = set("""yes please oh wow hello hi goodbye thanks cheers""".split())

PREP_BEHIND = set("""behind below beyond opposite toward via""".split())
COMPARATIVE |= set("""braver brighter cleaner clearest easier faster happiest
harder higher lighter slower smaller stronger taller thicker worse""".split())

# ---- 第二批補入 ----
NOUN_SET |= set('sundays'.split())

# 被 verb_morph 誤判成動名詞的純名詞（building a tall building …）
NOUN_SET |= set("""building evening morning""".split())

# 本語料裡 email 一律是名詞（email address …），不是動詞
NOUN_SET |= set('email'.split())
NOUN_PLURAL |= set(['sundays'])

# 字尾是 s，但其實是單數或不可數的名詞（絕不可標成「複數」）
MASS_SINGULAR = set("""address boss bus class gas maths news progress
series species""".split())
NOUN_PLURAL -= MASS_SINGULAR

# 少數純形容詞未收進 ADJ_SET，卻會被 verb_morph 誤判成第三人稱單數
ADJ_SET |= set("""serious famous curious generous mysterious obvious various
previous obvious useful harmful nervous""".split())
PROPN |= set('ben'.split())


# -------------------------------------------------------------- 歧義字候選表
AMBIG = {}


def _amb(w, *p):
    AMBIG[w] = tuple(p)


for w in """answer back break brush change check chat clean close colour copy
    count cost damages end fit form help hope jump keep label left light link
    list look love mark matter move need note order pack paint part pass pay
    phone plan place point post practice quiz race rain repair rest review
    rule run share shift show start step stop study support talk taste test
    train travel treat turn use visit wait walk warm wash water work worry
    beat coach park sound like book""".split():
    _amb(w, 'VERB', 'NOUN')
for w in """warm fit open cool fast hard late long short high low own free
    clean clear close light slow straight just even still only""".split():
    _amb(w, 'ADJ', 'VERB', 'ADV')
_amb('left', 'VERB', 'NOUN', 'ADJ')
_amb('right', 'ADJ', 'NOUN', 'ADV', 'INTJ')
_amb('light', 'NOUN', 'ADJ', 'VERB')
_amb('near', 'PREP', 'ADJ')
_amb('back', 'ADV', 'NOUN', 'ADJ')
_amb('home', 'ADV', 'NOUN')
_amb('well', 'ADV', 'ADJ', 'INTJ')
_amb('enough', 'ADV', 'DET', 'ADJ')
_amb('one', 'NUM', 'PRON')
_amb('half', 'NUM', 'NOUN', 'PRON')
_amb('quarter', 'NUM', 'NOUN')
_amb('first', 'ADJ', 'NUM', 'ADV', 'NOUN')
_amb('second', 'NUM', 'ADJ', 'NOUN')
_amb('fifth', 'NUM', 'NOUN')
_amb('last', 'ADJ', 'ADV', 'NOUN')
_amb('next', 'ADJ', 'ADV', 'PREP')
_amb('only', 'ADV', 'ADJ')
_amb('best', 'ADJ', 'ADV', 'NOUN')
_amb('better', 'ADJ', 'ADV')
_amb('more', 'DET', 'ADJ', 'ADV', 'PRON')
_amb('most', 'DET', 'ADJ', 'ADV', 'PRON')
_amb('less', 'DET', 'ADJ', 'ADV')
_amb('all', 'DET', 'PRON', 'ADV')
_amb('some', 'DET', 'PRON')
_amb('any', 'DET', 'PRON')
_amb('no', 'DET', 'INTJ')
_amb('both', 'DET', 'PRON')
_amb('each', 'DET', 'PRON')
_amb('either', 'DET', 'ADV', 'CONJ')
_amb('neither', 'DET', 'PRON', 'CONJ')
_amb('much', 'DET', 'ADV', 'PRON')
_amb('many', 'DET', 'PRON')
_amb('few', 'DET', 'PRON')
_amb('little', 'DET', 'ADJ', 'ADV')
_amb('other', 'ADJ', 'NOUN')
_amb('whole', 'ADJ', 'DET')
_amb('own', 'ADJ', 'VERB')
_amb('plenty', 'PRON', 'ADV')
_amb('such', 'DET')
_amb('so', 'ADV', 'CONJ')
_amb('as', 'SCONJ', 'PREP', 'ADV')
_amb('after', 'SCONJ', 'PREP', 'ADV')
_amb('before', 'SCONJ', 'PREP', 'ADV')
_amb('since', 'SCONJ', 'PREP')
_amb('until', 'SCONJ', 'PREP')
_amb('while', 'SCONJ', 'PREP')
_amb('when', 'SCONJ', 'ADV')
_amb('where', 'SCONJ', 'ADV')
_amb('that', 'SCONJ', 'PRON', 'DET')
_amb('this', 'DET', 'PRON')
_amb('these', 'DET', 'PRON')
_amb('those', 'DET', 'PRON')
_amb('what', 'DET', 'PRON', 'ADV')
_amb('which', 'DET', 'PRON')
_amb('whose', 'DET', 'PRON')
_amb('there', 'ADV', 'PRON')
_amb('down', 'PREP', 'ADV')
_amb('up', 'PREP', 'ADV')
_amb('out', 'PREP', 'ADV')
_amb('off', 'PREP', 'ADV')
_amb('over', 'PREP', 'ADV')
_amb('past', 'PREP', 'NOUN', 'ADJ')
_amb('inside', 'PREP', 'ADV', 'NOUN')
_amb('outside', 'PREP', 'ADV', 'NOUN')
_amb('about', 'PREP', 'ADV')
_amb('around', 'PREP', 'ADV')
_amb('along', 'PREP', 'ADV')
AMBIG.pop('', None)

DET_ONLY = set("""a an the every each no another such my your our their its
    whose""".split())
NUM_ONLY = set("""two three four five six seven eight nine ten eleven twelve
    thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty
    thirty forty fifty sixty seventy eighty ninety hundred thousand third
    fourth sixth seventh eighth ninth tenth twelfth twentieth""".split())

WH_REL = set(['who', 'whom', 'whose', 'which', 'that'])
WH_CLAUSE = set(['what', 'who', 'whom', 'which', 'whose', 'that'])
WH_ADV = set(['when', 'where', 'why', 'how'])

REPORT_VERB = set("""said say told tell thought think knew know hoped hope
    decided decide announced announce explained explain suggested suggest
    reported report described describe warned warn mentioned mention noticed
    notice agreed agree promised promise realised realize learned learn found
    find asked answer shouted shout replied reply wrote write felt feel
    believed believe expected expect showed show meant mean wanted want
    remembered remember realised realized understand understood
    discovered discover wondered wonder supposed suppose guessed guess""".split())

LINKING = set(['be', 'am', 'is', 'are', 'was', 'were', 'become', 'became',
               'becomes', 'seem', 'seemed', 'seems', 'look', 'looks',
               'looked', 'feel', 'feels', 'felt', 'taste', 'tastes',
               'tasted', 'sound', 'sounds', 'sounded', 'smell', 'smells',
               'smelled', 'turn', 'turned', 'turns', 'get', 'got', 'gets',
               'grow', 'grew', 'stay', 'stayed', 'remain', 'remained',
               'keep', 'kept'])

NEG_CONTRACTION = set(["don't", "doesn't", "didn't", "can't", "couldn't",
                       "won't", "wouldn't", "shouldn't", "haven't", "hasn't",
                       "hadn't", "mustn't", "needn't", "shan't", "isn't",
                       "aren't", "wasn't", "weren't"])

PRON_CONTRACTION = set(["i'm", "he's", "she's", "it's", "that's", "there's",
                        "what's", "who's", "let's", "you're", "we're",
                        "they're", "i've", "we've", "you've", "i'll", "we'll",
                        "he'll", "she'll", "they'll", "i'd", "we'd"])

# ---- 補充歧義字 ----
for _w in ('excuse rent download'.split()):
    _amb(_w, 'VERB', 'NOUN')
_amb('live', 'VERB', 'ADJ')
for _w in """braver brighter cleaner clearest easier faster happiest harder
higher lighter slower smaller stronger taller thicker""".split():
    _amb(_w, 'ADJ', 'ADV')
_amb('square', 'ADJ', 'NOUN')
_amb('spare', 'ADJ', 'VERB')
_amb('underground', 'ADJ', 'NOUN')
_amb('today', 'NOUN', 'ADV')
_amb('whatever', 'DET', 'PRON')
_amb('direct', 'ADJ', 'ADV')
_amb('online', 'ADJ', 'ADV')
_amb('favourite', 'ADJ', 'NOUN')

MOTION_VERBS = set("""go went come came return returned get got head walk
walked drive drove move moved be am is are was were been being travel
travelled""".split())

# even 幾乎都是副詞（even if / even the …）
AMBIG.pop('even', None)


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
