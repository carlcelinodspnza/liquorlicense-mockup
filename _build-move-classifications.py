#!/usr/bin/env python3
"""
Move #classifications to sit directly after the hero on the CA services page.

It currently runs sixth, after the three .ca-fig prose bands. The owner wants the
five classifications up front, immediately under the hero.

SAFE TO MOVE: nothing on the site links to #classifications -- no same-page anchor
and no cross-page href to california-liquor-license-services.html#classifications
(checked before touching it), so no link breaks.

THE MOVE IS A SPLICE, NOT A REWRITE. The section's markup is lifted verbatim and
re-inserted; the generator asserts the extracted block is byte-identical to what
it re-inserts, and that the page's visible text is unchanged.

BACKGROUND ADJACENCY IS CHECKED, NOT ASSUMED. The hero and #classifications are
both .section--dark, so placing one under the other risks a single unbroken dark
field with no seam. The generator reports the resulting order so the rendered
grounds can be measured afterwards rather than guessed at here.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')

src = io.open(PAGE, encoding='utf-8').read()
main_m = re.search(r'<main.*?</main>', src, re.S)
main = main_m.group(0)

def top_sections(m):
    out, last = [], 0
    for x in re.finditer(r'<section([^>]*)>', m):
        st = x.start()
        if st < last: continue
        d = 0
        for t in re.finditer(r'<(/?)section\b[^>]*>', m[st:]):
            d += 1 if not t.group(1) else -1
            if d == 0: en = st + t.end(); break
        else: en = len(m)
        out.append((x.group(1), st, en)); last = en
    return out

secs = top_sections(main)
order = [(re.search(r'id="([^"]+)"', a).group(1) if re.search(r'id="([^"]+)"', a) else '(hero)') for a, _, _ in secs]
assert order[0] == '(hero)', 'first section is not the hero: %r' % order[:2]

if order[1] == 'classifications':
    print('already directly after the hero -- no-op'); raise SystemExit(0)

i = order.index('classifications')
_, cst, cen = secs[i]
block = main[cst:cen]
hero_end = secs[0][2]

# cut, then paste immediately after the hero
without = main[:cst] + main[cen:]
# the hero end offset is unchanged because the block sits after it
assert cst > hero_end, 'the band is already before the hero'
new_main = without[:hero_end] + '\n' + block + without[hero_end:]

out = src[:main_m.start()] + new_main + src[main_m.end():]

# ---------------- guards ----------------
def words(t): return Counter(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r'<[^>]+>', ' ', t)))
assert words(main) == words(new_main), 'visible copy changed by a move'
assert new_main.count(block) == 1, 'the moved block is not present exactly once'
assert len(top_sections(new_main)) == len(secs), 'section count changed'
new_order = [(re.search(r'id="([^"]+)"', a).group(1) if re.search(r'id="([^"]+)"', a) else '(hero)')
             for a, _, _ in top_sections(new_main)]
assert new_order[0] == '(hero)' and new_order[1] == 'classifications', 'unexpected new order: %r' % new_order
assert sorted(new_order) == sorted(order), 'a section was lost or gained'
assert out.count('<img') == src.count('<img'), 'image count changed'
assert out.count('<h1') == 1
t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
assert '>' not in t, 'stray ">" introduced'

# THE SEAM. Measured after the move: the hero and #classifications both computed
# rgb(23,18,15), i.e. one unbroken dark field with no boundary between them. The band
# drops --dark and takes the base .section ground (43,33,27), which is the only one of
# the three that does not collide with a neighbour: --warm (34,26,21) would have matched
# #services directly below it. Result, top to bottom:
#   23,18,15 / 43,33,27 / 34,26,21 / 43,33,27 / 23,18,15 / 43,33,27 / 34,26,21 / 43,33,27
# -- no two adjacent bands share a ground.
_old_cls = '<section class="section section--dark" id="classifications">'
assert out.count(_old_cls) == 1, 'the classifications band is not in the expected shape'
out = out.replace(_old_cls, '<section class="section" id="classifications">', 1)
assert 'section--dark" id="classifications"' not in out

io.open(PAGE, 'w', encoding='utf-8').write(out)
print('moved #classifications to position 2 and dropped --dark to keep a seam under the hero')
print('  was: ' + ' -> '.join(order))
print('  now: ' + ' -> '.join(new_order))
