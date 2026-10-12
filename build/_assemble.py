# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
order = ['_p1.py', '_p0.py', '_p2.py', '_p3.py', '_p4.py', '_p5.py',
         '_p6.py']
parts = []
for f in order:
    p = os.path.join(HERE, f)
    if not os.path.exists(p):
        print('MISSING', f)
        sys.exit(1)
    parts.append(open(p, encoding='utf-8').read().rstrip('\n'))
out = '\n\n'.join(parts) + '\n'
dest = os.path.join(HERE, 'poslib.py')
open(dest, 'w', encoding='utf-8', newline='\n').write(out)
print('wrote poslib.py', len(out), 'chars')
try:
    compile(out, 'poslib.py', 'exec')
    print('compiles OK')
except SyntaxError as e:
    print('SyntaxError line', e.lineno, ':', e.msg)
    lines = out.splitlines()
    for k in range(max(0, e.lineno - 4), min(len(lines), e.lineno + 3)):
        print('%5d| %s' % (k + 1, lines[k]))
