
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
