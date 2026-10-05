# qa_topics.py - verify every "A2 Key <topic>" attribution against the official topic list
import io, re, glob

NF = chr(10)

TOPICS = {}
cur = None
for line in io.open('a2key_topics.txt', encoding='utf-8').read().split(NF):
    raw = line.strip()
    if not raw:
        continue
    if raw.lower().startswith('appendix') or raw.lower() == 'topic lists':
        continue
    if not re.search(r'  +', line):
        cur = raw
        TOPICS[cur] = []
        continue
    if cur:
        TOPICS[cur].extend(line.split())

def norm(w):
    return w.lower().strip().split('(')[0].strip().replace('/', '').strip()

OFFICIAL = sorted(TOPICS)
POOL = {}
ALL = set()
for k, vs in TOPICS.items():
    POOL[k] = set(norm(v) for v in vs)
    ALL |= POOL[k]

STOP = set(['pop','html','text','key','file','for','in','if','and','or','not','none',
            'true','false','kw','class','span','br','li','app','main','div','sub',
            'strings','verb','colloc','link','tap','the','a','an','is','was',
            'are','be','of','to','it','they','we','he','she','this','that','these','those'])

WORD = re.compile(r"[A-Za-z][A-Za-z'-]{1,20}")
CLAIM = re.compile('A2 Key[^\\u300c\\u300d\\n]{0,6}\\u300c([^\\u300d\\n]+)\\u300d\\u4e3b\\u984c')

def match_topic(name):
    n = name.strip().lower()
    if not n:
        return None
    for o in OFFICIAL:
        if o.lower() == n:
            return o
    for o in OFFICIAL:
        if n and (o.lower().startswith(n) or n.startswith(o.lower())):
            return o
    return None

def nearest_words(s, pos, back=60):
    seg = s[max(0, pos-back):pos]
    cut = seg.rfind(chr(39) * 3)
    for sep in (chr(0xFF0C) + chr(1), ',' + chr(1), chr(0x3002) + chr(1), ';' + chr(1), '<br>' + chr(1)):
        c2 = seg.rfind(sep)
        if c2 > cut:
            cut = c2 + 1
    seg = seg[cut + 3:]
    return [w for w in WORD.findall(seg) if w.lower() not in STOP][-6:]

problems = []
for f in sorted(glob.glob('lessons_part*.py'), key=lambda x: int(re.findall(r'[0-9]+', x)[0])):
    t = io.open(f, encoding='utf-8').read()
    ls = re.findall(r'"file": "([0-9]+)-', t)
    for m in CLAIM.finditer(t):
        raw = m.group(1)
        if match_topic(raw):
            parts = [raw]
        else:
            parts = re.split('[/;]|' + chr(0x3001), raw)
        pools, bad = [], []
        for p in parts:
            p = p.strip()
            if not p:
                continue
            o = match_topic(p)
            if o is None:
                bad.append(p)
            else:
                pools.append(POOL[o])
        for b in bad:
            if re.search('[A-Za-z]', b):
                problems.append(('TOPIC-UNKNOWN', ls, f, '"' + b + '" is not one of the %d official A2 Key topic names' % len(OFFICIAL)))
            else:
                problems.append(('TOPIC-NOT-EN', ls, f, 'uses a Chinese topic name "' + b + '" instead of the official English one'))
        if bad:
            continue
        union = set()
        for p in pools:
            union |= p
        cands = nearest_words(t, m.start())
        hit = [w for w in cands if norm(w) in union]
        if hit:
            continue
        for w in cands:
            n = norm(w)
            if len(n) < 3 or n in union or n not in ALL:
                continue
            problems.append(('TOPIC-MISMATCH', ls, f, 'word "' + w + '" belongs to a different A2 Key topic, not "' + raw + '"'))

seen, uniq = set(), []
for p in problems:
    if p[3] in seen:
        continue
    seen.add(p[3])
    uniq.append(p)
for p in uniq:
    print('%-14s L%s %s | %s' % p)
print('TOTAL PROBLEMS: %d' % len(uniq))
