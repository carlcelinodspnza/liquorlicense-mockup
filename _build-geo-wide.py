#!/usr/bin/env python3
"""
Apply layout G-C to the #markets band on the two STATE pages.

WHAT WAS WRONG, measured on the live page (1440 viewport, 1200px container):
  eyebrow  y=0    cards y=78   h2 y=585   -> the heading rendered BELOW the cards,
  with 698px of empty left column.

IT WAS A SCOPING BUG. Block [MRAIL] makes "#markets > .container" a two-column grid
(1.32fr / 1fr) and pins .eyebrow to column 1 row 1 and h2 to column 1 row 2. That was
written for locations.html's master/detail rail. arizona-liquor-license.html and
florida-liquor-license.html reuse the same #markets id for a different band whose
.loc-geo child has no placement, so it auto-flowed into column 2, grew to the height
of its lists, and pushed the h2 into a 585px-tall row 2.

WHY G-C AND NOT THE NARROWER SPLITS. .loc-geo__list carries max-height:340px with
overflow-y:auto, so any layout that squeezes it hides items behind a scrollbar with
no affordance. Measured on FLORIDA (66 counties), which is the real stress case:

    G-A heading left, cards right      1 grid column   54 of 66 hidden
    G-B full-width heading, two cards  3 grid columns  30 of 66 hidden
    G-C full-width heading, one card   6 grid columns   0 hidden   <- chosen
    G-D G-A + sticky heading           1 grid column   54 of 66 hidden

Arizona hides only 2 items under G-A, which is exactly why the narrow options look
fine there and fail on Florida. G-C is the only one that fits the list under the
340px cap, so nothing scrolls and nothing is hidden.

THE OVERRIDE IS SCOPED TO A NEW CLASS ON THESE TWO SECTIONS, not to #markets. A bare
"#markets > .container { display:block }" would have reached locations.html and
destroyed the rail that [MRAIL] exists to build. The section gains markets--geo and
the CSS keys off that, so locations.html cannot be affected -- asserted below by
checking its markup is untouched.

The lede is assembled from the counts already printed on the page. Nothing invented.

Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

PAGES = ['arizona-liquor-license.html', 'florida-liquor-license.html']
GUARD = 'locations.html'   # must NOT change
MARK = 'markets--geo'


def words(fragment):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return Counter(html.unescape(t).split())


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


def band_bounds(s):
    """Depth-matched. #markets contains nested <section class="loc-geo__col">."""
    i = s.find('id="markets"')
    assert i > 0, 'no #markets'
    i = s.rfind('<section', 0, i)
    d, j = 1, s.find('>', i) + 1
    while d and j < len(s):
        nx = re.search(r'<(/?)section\b[^>]*>', s[j:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        j += nx.end()
    return i, j


def geo_bounds(band):
    g = band.find('<div class="loc-geo"')
    assert g > 0, 'no .loc-geo'
    d, k = 1, band.find('>', g) + 1
    while d and k < len(band):
        nx = re.search(r'<(/?)div\b[^>]*>', band[k:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        k += nx.end()
    return g, k


guard_before = io.open(GUARD, encoding='utf-8').read()
staged, skipped = {}, []

for f in PAGES:
    src = io.open(f, encoding='utf-8').read()
    bi, bj = band_bounds(src)
    band = src[bi:bj]
    if MARK in band:
        skipped.append(f)
        continue

    gi, gj = geo_bounds(band)
    geo = band[gi:gj]
    eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', band, re.S).group(1)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', band, re.S).group(1)

    counts = re.findall(r'<h4>([A-Za-z]+)\s*<span class="loc-geo__n">(\d+)</span>', geo)
    assert counts, '%s: no counts on the cards' % f
    lede = ('We publish %s. Tell us the market and the classification and we source '
            'against it.' % ' and '.join('%s %s' % (n, name.lower()) for name, n in counts))
    assert re.match(r'We publish \d+ [a-z]+', lede), '%s: lede reads wrong: %r' % (f, lede)

    sec_open = re.match(r'<section\b[^>]*>', band).group(0)
    assert 'class="' in sec_open, '%s: section has no class' % f
    new_open = sec_open.replace('class="', 'class="%s ' % MARK, 1)

    new_band = (new_open + '\n  <div class="container">\n'
                '    <div class="geo geo--wide">\n'
                '      <p class="eyebrow">%s</p>\n'
                '      <h2>%s</h2>\n'
                '      <p class="lede lede--prose">%s</p>\n'
                '      %s\n'
                '    </div>\n  </div>\n</section>' % (eyebrow, h2, lede, geo))

    new_src = src[:bi] + new_band + src[bj:]

    # ---- guards ------------------------------------------------------------
    ow, nw = words(src), words(new_src)
    assert all(nw[k] >= v for k, v in ow.items()), '%s: existing words lost' % f
    added, expected = nw - ow, words('<p>%s</p>' % lede)
    assert added == expected, ('%s: unexpected word delta\n  extra=%s\n  missing=%s'
                               % (f, added - expected, expected - added))

    # every place name survives, in order
    before_names = re.findall(r'<span class="loc-geo__name">(.*?)</span>', band)
    after_names = re.findall(r'<span class="loc-geo__name">(.*?)</span>', new_band)
    assert before_names == after_names, '%s: place names changed' % f
    assert len(before_names) == sum(int(n) for _, n in counts), \
        '%s: %d names vs %d claimed by the headings' % (f, len(before_names),
                                                        sum(int(n) for _, n in counts))

    assert new_src.count(MARK) == 1, '%s: marker not exactly once' % f
    assert new_band.count('<div class="loc-geo"') == 1, '%s: loc-geo duplicated' % f
    assert new_band.index('<h2') < new_band.index('<div class="loc-geo"'), \
        '%s: heading still after the cards in source order' % f
    assert len(re.findall(r'<h1\b', new_src)) == len(re.findall(r'<h1\b', src)), '%s: h1' % f
    assert not stray_gt(new_src), '%s: stray ">"' % f
    for tag in ('section', 'div', 'ul', 'li', 'p', 'span', 'h2', 'h4'):
        o = len(re.findall(r'<%s\b' % tag, new_band))
        c = len(re.findall(r'</%s>' % tag, new_band))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (f, tag, o, c)

    staged[f] = new_src

if not staged:
    print('no-op: both state pages already carry G-C')
    sys.exit(0)

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

# locations.html must be byte-identical -- it owns the [MRAIL] rail this override
# deliberately does not touch.
assert io.open(GUARD, encoding='utf-8').read() == guard_before, \
    '%s changed, which this build must never do' % GUARD

print('applied G-C to %d state pages (%d already had it)' % (len(staged), len(skipped)))
for f in staged:
    n = re.findall(r'<h4>([A-Za-z]+)\s*<span class="loc-geo__n">(\d+)</span>', staged[f])
    print('   %-32s %s' % (f, ', '.join('%s %s' % (a, b) for a, b in n)))
print('   %s verified byte-identical' % GUARD)
