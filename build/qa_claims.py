# qa_claims.py - deterministic checks on grammar CLAIMS in the lesson data
import io, re, glob, importlib.util, sys

NF = chr(10)

def load_modules():
    fs = sorted(glob.glob('lessons_part*.py'), key=lambda x: int(re.findall(r'[0-9]+', x)[0]))
    lessons = []
    for f in fs:
        spec = importlib.util.spec_from_file_location(f[:-3], f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for L in m.LESSONS:
            L['__mod'] = f
            lessons.append(L)
    return lessons

LESSONS = load_modules()
BY_NUM = {}
for L in LESSONS:
    n = int(re.match(r'[0-9]+', L['file']).group(0))
    BY_NUM[n] = L
    L['__num'] = n

def blob(L):
    parts = [L.get('title_cn',''), L.get('subtitle',''), L.get('grammar',''), L.get('topic','')]
    parts += list(L.get('translation', [])) + list(L.get('bridges', []))
    for pg in L.get('paragraphs', []):
        for s in pg:
            parts.append(s.get('text',''))
            parts.append(s.get('html',''))
            parts.append(s.get('pop','') or '')
    parts.append(L.get('sum_intro',''))
    parts += list(L.get('sum_titles', []))
    for g in L.get('summary', []):
        parts += list(g)
    return NF.join(str(x) for x in parts)

BLOB = {L['__num']: blob(L) for L in LESSONS}
BLOBLC = {k: v.lower() for k, v in BLOB.items()}

ALLOWED_TRIPLES = {('get', 'got', 'got'): 'American English variant, explicitly labelled as such in lesson 59'}

KNOWN_IDENTICAL = set(['put','cut','set','let','read','win','shut','cast','hit',
                       'cost','burst','spread','kneel','leap','sweat','weave',
                       'wring','beset','re-set','offset','upset','broadcast','forecast',
                       'rebuild','unwrap','overcome'])

problems = []

# ---------- CHECK 1: dangling lesson cross-references ----------
REF = re.compile(u'\u7b2c\s*([0-9]{1,2})\s\u8ab2')
TAG = re.compile(u'\u7b2c\s*[0-9]{1,2}\s\u8ab2\u7684')
for L in LESSONS:
    b = blob(L)
    for m in REF.finditer(b):
        n = int(m.group(1))
        if n not in BLOB:
            problems.append(('REF-MISSING', L['__num'], L['__mod'], 'refers to lesson %d which does not exist' % n))
for L in LESSONS:
    b = blob(L)
    for m in TAG.finditer(b):
        n = int(re.search(r'([0-9]{1,2})', m.group(0)).group(1))
        if n not in BLOB:
            continue
        tail = b[m.end():m.end()+60]
        w = re.match(r'[ \u3000]*([A-Za-z][A-Za-z\u2019\']{1,24})', tail)
        if not w:
            continue
        word = w.group(1).lower()
        target = BLOBLC[n]
        if word in target:
            continue
        stems = [word, word.rstrip('s'), word+'e', word[:-1] if word.endswith('y') else word]
        if any(s in target for s in stems):
            continue
        problems.append(('REF-WORD', L['__num'], L['__mod'], 'says "\u7b2c%d\u8ab2\u7684%s" but lesson %d never uses it' % (n, w.group(1), n)))

# ---------- CHECK 2: three-form verb triples ----------
IRREG = {}
for triple in [
 'go went gone','be was been','am was been','do did done','have had had',
 'say said said','make made made','take took taken','come came come',
 'see saw seen','get got gotten','give gave given','know knew known',
 'think thought thought','become became become','leave left left',
 'lose lost lost','run ran run','put put put','cut cut cut','read read read',
 'buy bought bought','bring brought brought','find found found',
 'teach taught taught','eat ate eaten','drink drank drunk','fall fell fallen',
 'sit sat sat','lie lay lain','stand stood stood','hear heard heard',
 'hold held held','write wrote written','sleep slept slept',
 'buy bought bought','sell sold sold','build built built','send sent sent',
 'spend spent spent','meet met met','run ran run','sit sat sat',
 'wear wore worn','ride rode ridden','fly flew flown','draw drew drawn',
 'sing sang sung','swim swam swum','begin began begun','break broke broken',
 'choose chose chosen','speak spoke spoken','forget forgot forgotten',
 'lose lost lost','mean meant meant','keep kept kept','leave left left',
 'feel felt felt','win won won','eat ate eaten','throw threw thrown',
 'catch caught caught','teach taught taught','fight fought fought',
 'stop stopped stopped','look looked looked','play played played',
 'damage damaged damaged','mix mixed mixed','walk walked walked',
 'clap clapped clapped','practise practised practised','laugh laughed laughed',
 'check checked checked','count counted counted','apologise apologised apologised',
 'organise organised organised','realise realised realised','use used used',
 'call called called','visit visited visited','arrive arrived arrived',
 'appear appeared appeared','smell smelled smelled','climb climbed climbed',
 'enjoy enjoyed enjoyed','prefer preferred preferred','travel travelled travelled',
 'email emailed emailed','water watered watered','plan planned planned',
 'laugh laughed laughed','borrow borrowed borrowed','return returned returned',
]:
    p = triple.split()
    IRREG[p[0]] = tuple(p)

def ends_e(s):
    return s.endswith('e')

def regular(base):
    last = base[-1]
    if last in 'aeiouwxy':
        return (base + 'ed', base + 'd')
    if last == 'y' and len(base) > 1 and base[-2] not in 'aeiou':
        b = base[:-1] + 'ies'
        return (b + 'ed', b + 'd')
    if len(base) > 1 and base[-2] in 'aeiou' and last not in 'aeiouwxy':
        return (base + base[-1] + 'ed', base + base[-1] + 'ed')
    return (base + 'ed', base + 'ed')

TRIPLE = re.compile(r'([A-Za-z]{2,})\s*\u2013\s*([A-Za-z]{2,})\s*\u2013\s*([A-Za-z]{2,})')
for L in LESSONS:
    b = blob(L)
    for m in TRIPLE.finditer(b):
        t = (m.group(1), m.group(2), m.group(3))
        base = t[0].lower()
        if base in IRREG:
            exp = IRREG[base]
            if exp != t and t not in ALLOWED_TRIPLES:
                problems.append(('VERB3', L['__num'], L['__mod'], 'writes %s but the correct three-form set is %s' % ('-'.join(t), '-'.join(exp))))
        else:
            r = regular(base)
            if r != (t[1].lower(), t[2].lower()):
                pass  # unknown irregular verb, skip
        all_same = (t[0].lower() == t[1].lower() == t[2].lower())
        ctx = b[max(0, m.start()-45):m.end()+45]
        if u'\u4e09\u614b\u540c\u5f62' in ctx and not all_same:
            problems.append(('VERB3-WORDING', L['__num'], L['__mod'],
                'calls ' + '-'.join(t) + ' identical in all three forms, but only past and past participle match : ' + ctx))
        if all_same and base in IRREG and IRREG[base] != t:
            problems.append(('VERB3-SAME', L['__num'], L['__mod'], 'shows ' + '-'.join(t) + ' as all three identical, which is wrong'))
KNOWN_IDENTICAL = set(['put','cut','set','let','read','win','shut','cast','hit',
                       'cost','burst','spread','kneel','leap','sweat','weave',
                       'wring','beset','re-set','offset','upset','broadcast','forecast',
                       'rebuild','unwrap','overcome'])

# ---------- CHECK 3: markdown artefacts inside HTML ----------
MD = re.compile(r'\*[A-Za-z][^*\n]{1,40}\*')
for L in LESSONS:
    b = blob(L)
    for m in MD.finditer(b):
        problems.append(('MD-ARTEFACT', L['__num'], L['__mod'], 'residual markdown asterisks: ' + m.group(0)))

# ---------- CHECK 4: non-ASCII quotation marks / apostrophes ----------
BAD_QUOTES = {0x2018: 'left single quote', 0x2019: 'right single quote', 0x02BC: 'modifier apostrophe',
              0x201C: 'left double quote', 0x201D: 'right double quote', 0x2032: 'prime'}
for L in LESSONS:
    b = blob(L)
    for code, name in BAD_QUOTES.items():
        c = b.count(chr(code))
        if c:
            i = b.index(chr(code))
            problems.append(('QUOTE-CHAR', L['__num'], L['__mod'],
                '%d x U+%04X (%s), e.g. ...%s...' % (c, code, name, b[max(0, i-25):i+25])))
seen = set()
uniq = []
for p in problems:
    k = (p[0], p[3])
    if k in seen:
        continue
    seen.add(k)
    uniq.append(p)

for p in uniq:
    print('%-14s L%02d %s | %s' % p)
print('TOTAL PROBLEMS: %d' % len(uniq))