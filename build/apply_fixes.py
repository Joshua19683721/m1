import io, sys

NL = '~NL~'
LF = chr(10)

def load(path):
    raw = io.open(path, encoding='utf-8').read()
    files = {}
    for blk in raw.split('###FILE ')[1:]:
        head, rest = blk.split(LF, 1)
        fn = head.strip()
        rest = rest.replace('###END' + LF, '').replace('###END', '')
        recs = []
        for p in rest.split('###OLD' + LF)[1:]:
            o, n = p.split('###NEW' + LF, 1)
            if o.endswith(LF): o = o[:-1]
            if n.endswith(LF): n = n[:-1]
            recs.append((o.replace(NL, LF), n.replace(NL, LF)))
        files[fn] = recs
    return files

data = load(sys.argv[1])
ok_all = 0; n_all = 0
for fn in sorted(data):
    recs = data[fn]
    s = io.open(fn, encoding='utf-8').read()
    ok = 0
    for o, n in recs:
        n_all += 1
        if o in s:
            s = s.replace(o, n, 1); ok += 1
        else:
            print('  MISS in %s: %s' % (fn, repr(o[:60])))
    io.open(fn, 'w', encoding='utf-8').write(s)
    ok_all += ok
    print('%s -> %d/%d' % (fn, ok, len(recs)))
print('TOTAL %d/%d' % (ok_all, n_all))
