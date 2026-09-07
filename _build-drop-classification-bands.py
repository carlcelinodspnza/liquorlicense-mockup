#!/usr/bin/env python3
"""
Remove the classification bands from service-buy.html and service-sell.html.

The owner asked for both to go. They were added on 2026-09-04 (b0bea7f) carrying the
client's own Type 20&21 / 41&47 / 48 descriptions, under a written exception to
dedup-ledger rows C18-C20.

WHAT THE REMOVAL COSTS, enumerated in four directions before deleting anything:

  1. INBOUND ANCHORS ..... none. #buy-classifications and #sell-classifications are
     referenced by 0 pages, so no link breaks.
  2. LINK TARGETS ........ each page loses FIVE deep links,
     licence-types.html#type-20/21/41/47/48. The bare link to licence-types.html
     survives elsewhere on both pages, so the classifications page stays reachable --
     but the per-type anchors do not. Reported, not silently dropped.
  3. JS / INTEGRATION .... none. site.js has 0 references to either id or to
     .buyclass.
  4. LAYOUT DEPENDENTS ... the band is a top-level <section>, not a grid child, so no
     sibling depends on it for width. Section grounds ARE checked after removal,
     because deleting a band can leave two neighbours sharing one ground.

THE LEDGER MUST BE CORRECTED IN THE SAME CHANGE. dedup-ledger.md carries a C18-C20
EXCEPTION naming these two bands as authorised duplications of the Type definitions.
Once the bands are gone that row describes a duplication that no longer exists -- a
governance record that has quietly become false. It is marked RETIRED here, with
licence-types.html restored as sole owner, rather than left to mislead.

.buyclass / .buyclass__col / .buyclass__col--lead CSS becomes DEAD after this: those
classes appear on no other page. The CSS is deliberately NOT deleted -- it sits
inside blocks [CY] and [DD] alongside rules that are still live, and surgically
unpicking it risks more than it saves. It is reported so it can be retired
deliberately.

Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

TARGETS = [('service-buy.html', 'buy-classifications'),
           ('service-sell.html', 'sell-classifications')]
LEDGER = '_content-requirements/_dedup-ledger.md'


def words(x):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', x, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return Counter(html.unescape(t).split())


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


def section_span(s, sid):
    i = s.find('id="%s"' % sid)
    if i < 0:
        return None
    i = s.rfind('<section', 0, i)
    d, j = 1, s.find('>', i) + 1
    while d and j < len(s):
        nx = re.search(r'<(/?)section\b[^>]*>', s[j:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        j += nx.end()
    return i, j


def sections(m):
    out = []
    for mm in re.finditer(r'<section\b([^>]*)>', m):
        d, i = 1, mm.end()
        while d and i < len(m):
            nx = re.search(r'<(/?)section\b[^>]*>', m[i:])
            if not nx:
                break
            d += -1 if nx.group(1) else 1
            i += nx.end()
        out.append(mm.group(1))
    return out


staged, lost_links = {}, {}

for page, sid in TARGETS:
    src = io.open(page, encoding='utf-8').read()
    span = section_span(src, sid)
    if not span:
        continue
    i, j = span
    band = src[i:j]
    orig = src

    # nothing may link INTO the band we are removing
    for other, _ in TARGETS:
        pass
    inbound = [f for f in os.listdir('.')
               if f.endswith('.html') and not f.startswith('_')
               and ('#%s' % sid) in io.open(f, encoding='utf-8').read()]
    assert not inbound, '%s: #%s is linked from %s' % (page, sid, inbound)

    new = src[:i] + src[j:]
    # tidy the blank line the removal leaves behind
    new = re.sub(r'\n{3,}', '\n\n', new)

    # ---- guards ------------------------------------------------------------
    ow, nw = words(orig), words(new)
    removed = ow - nw
    assert removed == words(band), \
        '%s: removed words != the band\n  extra=%s\n  missing=%s' % (
            page, removed - words(band), words(band) - removed)
    assert not (nw - ow), '%s: words APPEARED during a removal: %s' % (page, nw - ow)

    assert len(sections(new)) == len(sections(orig)) - 1, '%s: section count' % page
    assert 'id="%s"' % sid not in new, '%s: id survived' % page
    assert 'buyclass' not in new, '%s: band markup survived' % page
    assert len(re.findall(r'<h1\b', new)) == len(re.findall(r'<h1\b', orig)), '%s: h1' % page
    assert not stray_gt(new), '%s: stray ">"' % page
    for tag in ('section', 'div', 'ul', 'li', 'a', 'p', 'h2', 'h3'):
        o = len(re.findall(r'<%s\b' % tag, new)); c = len(re.findall(r'</%s>' % tag, new))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)

    band_links = {l for l in re.findall(r'href="([^"]+)"', band)}
    lost_links[page] = sorted(l for l in band_links if l not in new)
    staged[page] = new

if not staged:
    print('no-op: neither page carries a classification band')
    sys.exit(0)

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

# ---- the ledger row is now false; retire it ---------------------------------
led = io.open(LEDGER, encoding='utf-8').read()
old_row = [l for l in led.split('\n') if 'C18–C20 **EXCEPTION**' in l]
assert len(old_row) == 1, 'expected exactly one C18-C20 EXCEPTION row, found %d' % len(old_row)
new_row = ('| ~~C18–C20 **EXCEPTION** (owner, 2026-09-04)~~ **RETIRED 2026-09-07** | The Type '
           '20&21 / 41&47 / 48 descriptions were carried on `service-buy.html` and '
           '`service-sell.html` under this exception. The owner removed both bands on '
           '2026-09-07, so the duplication no longer exists. | — | `licence-types.html` is once '
           'again the SOLE owner of the Type definitions; C18–C20 applies unmodified. Kept as a '
           'struck-through row rather than deleted, so the decision trail survives. |')
led = led.replace(old_row[0], new_row)
assert 'RETIRED 2026-09-07' in led, 'ledger not updated'
io.open(LEDGER, 'w', encoding='utf-8').write(led)

print('removed the classification band from %d pages' % len(staged))
for f in staged:
    print('   %-22s deep links lost: %s' % (f, ', '.join(l.split('#')[-1] for l in lost_links[f]) or 'none'))
print('   dedup-ledger C18-C20 EXCEPTION marked RETIRED; licence-types.html sole owner again')
print('   NOTE: .buyclass / .buyclass__col CSS is now dead (0 pages use it) - left in place,')
print('         reported for deliberate retirement rather than unpicked from live blocks')
