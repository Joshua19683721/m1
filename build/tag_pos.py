# -*- coding: utf-8 -*-
"""把逐字詞性分析結果寫回 lessons_part*.py 的每個 w-tap span。

同時產生 _pos_report.txt 供逐筆檢視。
"""
import io, sys, os, re, json, ast
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import poslib

KEY = re.compile(r'"html"\s*:\s*')
OPEN = re.compile(r'<span ((?:[^>]|&(?!gt;))*?)>')


def extract_literals(src):
    """yield (start, end, delim) — start..end 覆蓋含定界符的字面值。"""
    out = []
    for m in KEY.finditer(src):
        i = m.end()
        q3 = src[i:i + 3]
        if q3 in ("'''", '"""'):
            e = src.find(q3, i + 3)
            if e < 0:
                continue
            out.append((i, e + 3, q3))
        else:
            c = src[i]
            if c not in ("'", '"'):
                continue
            j = i + 1
            while j < len(src):
                if src[j] == '\\':
                    j += 2
                    continue
                if src[j] == c:
                    break
                j += 1
            else:
                continue
            out.append((i, j + 1, c))
    return out


def encode_data_w(rows):
    s = json.dumps(rows, ensure_ascii=False, separators=(',', ':'))
    s = s.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;')
    return s


def build_attrs(attrs, res, needs_escape):
    """回傳新的 span 標籤（含 data-pos/data-func/data-w）。"""
    if needs_escape:
        rest = re.sub(r'\s*data-(?:pos|func|w)=\\"[^"\\]*\\"', '', attrs)
        q = '\\"'
    else:
        rest = re.sub(r'\s*data-(?:pos|func|w)="[^"]*"', '', attrs)
        q = '"'
    dw = encode_data_w(res['rows'])
    return ('<span ' + rest + ' data-pos=' + q + res['pos'] + q
            + ' data-func=' + q + res['func'] + q
            + ' data-w=' + q + dw + q + '>')


def process_file(path, report):
    src = open(path, encoding='utf-8').read()
    lits = extract_literals(src)
    if not lits:
        return 0, {}
    pieces = []
    last = 0
    total = 0
    delim_stat = {}
    for (s, e, delim) in lits:
        body = src[s + len(delim):e - len(delim)]
        needs = (delim == '"')
        body_norm = body.replace('\\"', '"') if needs else body
        literal = src[s:e]
        try:
            value = ast.literal_eval(literal)
        except Exception as ex:
            report.append('!! %s literal eval failed: %s' % (
                os.path.basename(path), ex))
            continue
        results = poslib.analyze_sentence(value)
        if len(results) == 0:
            continue
        delim_stat[delim] = delim_stat.get(delim, 0) + 1

        n = [0]

        def repl(m):
            attrs = m.group(1)
            if 'w-tap' not in attrs:
                return m.group(0)
            i = n[0]
            n[0] += 1
            if i >= len(results):
                return m.group(0)
            r = results[i]
            report.append('%s\t%s\t%s\t%s\t%s' % (
                os.path.basename(path), r['cls'], r['text'],
                r['pos'] + '|' + r['func'],
                ' / '.join('%s(%s:%s)' % (a, b, c) for a, b, c in r['rows'])))
            return build_attrs(attrs, r, needs)

        new_norm = OPEN.sub(repl, body_norm)
        total += n[0]
        if n[0] != len(results):
            report.append('!! %s tag/result mismatch %d vs %d in %s' % (
                os.path.basename(path), n[0], len(results), r['text'][:40]))
        new_body = new_norm.replace('"', '\\"') if needs else new_norm
        pieces.append(src[last:s])
        pieces.append(delim)
        pieces.append(new_body)
        pieces.append(delim)
        last = e
    pieces.append(src[last:])
    if total:
        open(path, 'w', encoding='utf-8', newline='').write(''.join(pieces))
    return total, delim_stat


def main():
    report = []
    grand = 0
    stats = {}
    for part in range(1, 27):
        p = os.path.join(HERE, 'lessons_part%d.py' % part)
        n, ds = process_file(p, report)
        grand += n
        for k, v in ds.items():
            stats[k] = stats.get(k, 0) + v
        print('part %2d: %4d spans' % (part, n))
    print('TOTAL rewritten:', grand)
    print('delimiters:', stats)
    with open(os.path.join(HERE, '_pos_report.txt'), 'w',
              encoding='utf-8') as f:
        f.write('\n'.join(report))
    print('report lines:', len(report))


if __name__ == '__main__':
    main()
