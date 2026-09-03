#!/usr/bin/env python3
"""
Give the 50 market TYPE pages the classification card band.

WHY. The owner pointed at the mega-menu panel that lists a market's five
classification pages and asked for the card component "for these pages as well".
Those 50 pages (10 markets x 5 types) carry ZERO links to their sibling
classifications -- measured, not assumed: 0 hrefs matching
liquor-license-<market>-type-NN.html anywhere in <main>. The mega menu is
currently the only path from Fresno Type 20 to Fresno Type 21.

FOUR CARDS, NOT FIVE. The band excludes the page's own classification, so a
Type 20 page shows 21/41/47/48. Self-linking is the alternative and it is wrong.
This follows the precedent already in the library: licence-type-20.html's rail is
titled "The other four classifications" and carries four siblings.

MARKET-SCOPED TARGETS. Cards link to liquor-license-<market>-type-NN.html, not the
generic licence-type-NN.html, so a visitor stays in the market they arrived in --
which is exactly what the menu panel the owner screenshotted does.

THE MARKET LABEL IS READ FROM THE PAGE, NEVER INVENTED. It comes from the page's
own <h1> ("Fresno County Type 20 Liquor License ..." -> "Fresno County"). That rule
parses 50/50. An earlier attempt read the #authorizes h2 and failed on 10 pages
(Los Angeles and San Diego phrase it differently), which is why the h1 is used.

IMAGERY, AND THE ONE SUBSTITUTION. The five card images are the ones already
verified on california-liquor-license-services.html. On a Type 47 page,
ind-restaurants.jpg is already the body image, so the Type 41 card would repeat it;
those 10 pages use ind-franchise.jpg for Type 41 instead. That file was OPENED to
check it, not trusted by its alt: it is a restaurant dining room with booth seating
and a bar along the back -- an eating place, which is what Type 41 authorises.

KNOWN AND DELIBERATE, 4 PAGES. On fresno / san-diego / santa-barbara / ventura
Type 21, inventory-shelves.jpg is the HERO BACKDROP, so the Type 20 card repeats it
as a small thumbnail. The library has no other off-sale retail photo:
hero-inventory.jpg was opened and is a back-bar with spirits and glassware (on-sale,
wrong for an off-sale classification), and ind-grocery.jpg was opened and is a
Norwegian supermarket -- "DRIKKE", "Gjor det billig!", kroner prices. Rather than
break the row or invent a mapping, the row stays consistent and this is reported.

PLACEMENT. Between #faqs and #next. Those two ALREADY share a ground (both
rgb(43,33,27)) on every type page -- a pre-existing merge -- so a --warm band
between them separates them as a side effect.

FAIL-CLOSED. Every page is built and validated in memory; nothing is written unless
all 50 pass. Idempotent: a second run is a no-op.
"""
import re, io, os, glob, html, sys
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

TYPES = ['20', '21', '41', '47', '48']
NAME = {
    '20': 'Off-Sale Beer &amp; Wine',
    '21': 'Off-Sale General',
    '41': 'On-Sale Beer &amp; Wine, Eating Place',
    '47': 'On-Sale General, Eating Place',
    '48': 'On-Sale General, Public Premises',
}
# (src, width, height, alt) -- lifted verbatim from the verified reference band
IMG = {
    '20': ('assets/inventory-shelves.jpg', 1400, 933,
           'Shelves of sealed bottles in a retail store'),
    '21': ('assets/ind-liquor-stores.jpg', 512, 512,
           'Racked wine and spirits in an off-sale store'),
    '41': ('assets/ind-restaurants.jpg', 512, 512,
           'A restaurant table laid for service with wine glasses'),
    '47': ('assets/ind-franchise.jpg', 1024, 1024,
           'A restaurant dining room with booth seating and a bar along the back wall'),
    '48': ('assets/ind-bars-nightclubs.jpg', 512, 512,
           'A bar counter and stools under low neon light'),
}
ALT_41 = IMG['47']   # the verified stand-in when ind-restaurants.jpg is taken

MARK = 'id="classifications"'


def main_span(s):
    a = s.find('<main')
    b = s.find('</main>')
    assert a >= 0 and b > a, 'no <main>'
    return a, b


def words(fragment):
    """Visible words: strip script/style, comments and tags, unescape entities."""
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return Counter(html.unescape(t).split())


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


def section_bounds(m):
    """(start, end, attrs) for every top-level <section> in the main fragment."""
    out = []
    for mm in re.finditer(r'<section\b([^>]*)>', m):
        depth, i = 1, mm.end()
        while depth and i < len(m):
            nx = re.search(r'<(/?)section\b[^>]*>', m[i:])
            if not nx:
                break
            depth += -1 if nx.group(1) else 1
            i += nx.end()
        out.append((mm.start(), i, mm.group(1)))
    return out


def build_band(market, self_type, label, used_imgs):
    cards = []
    for t in TYPES:
        if t == self_type:
            continue
        src, w, h, alt = IMG[t]
        if t == '41' and src in used_imgs:
            src, w, h, alt = ALT_41
        href = 'liquor-license-%s-type-%s.html' % (market, t)
        assert os.path.exists(href), 'missing target %s' % href
        cards.append(
            '        <li><a href="%s"><span class="clc__media">'
            '<img src="%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">'
            '</span><span class="clc__name"><strong>Type %s</strong> &mdash; %s</span>'
            '<span class="clc__go">View classification &rarr;</span></a></li>'
            % (href, src, alt, w, h, t, NAME[t]))
    srcs = re.findall(r'src="([^"]+)"', '\n'.join(cards))
    assert len(srcs) == 4 and len(set(srcs)) == 4, 'duplicate image in the row'
    return (
        '<section class="section section--warm" id="classifications">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">By classification</p>\n'
        '    <h2>The other four classifications in %s</h2>\n'
        '    <div class="cross-link-rail cross-link-rail--cards">\n'
        '      <ul class="cross-link-rail__cards cross-link-rail__cards--four" role="list">\n'
        '%s\n'
        '      </ul>\n'
        '    </div>\n'
        '    <p class="tp-note">What each classification authorises is set out on the '
        '<a href="licence-types.html">classifications page</a>, which owns those definitions.</p>\n'
        '  </div>\n'
        '</section>\n\n' % (label, '\n'.join(cards)))


pages = sorted(glob.glob('liquor-license-*-type-*.html'))
assert len(pages) == 50, 'expected 50 type pages, found %d' % len(pages)

staged, skipped, notes = {}, [], []

for f in pages:
    src_text = io.open(f, encoding='utf-8').read()
    mm = re.match(r'liquor-license-(.+)-type-(\d+)\.html$', f)
    market, self_type = mm.group(1), mm.group(2)
    a, b = main_span(src_text)
    m = src_text[a:b]

    if MARK in m:
        skipped.append(f)
        continue

    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', m, re.S)
    assert h1, '%s: no <h1>' % f
    h1t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html.unescape(h1.group(1)))).strip()
    lab = re.match(r'^(.*?)\s+Type\s+\d+\b', h1t)
    assert lab, '%s: market label not derivable from h1 %r' % (f, h1t)
    label = lab.group(1).strip()

    used = set(re.findall(r'src="(assets/[^"]+)"', m))
    band = build_band(market, self_type, label, used)

    secs = section_bounds(m)
    faqs = [i for i, s in enumerate(secs) if 'id="faqs"' in s[2]]
    nxt = [i for i, s in enumerate(secs) if 'id="next"' in s[2]]
    assert len(faqs) == 1 and len(nxt) == 1, '%s: need exactly one #faqs and one #next' % f
    assert nxt[0] == faqs[0] + 1, '%s: #next does not directly follow #faqs' % f

    ins = secs[nxt[0]][0]
    new_m = m[:ins] + band + m[ins:]
    new_text = src_text[:a] + new_m + src_text[b:]

    # ---- guards -------------------------------------------------------------
    ow, nw = words(m), words(new_m)
    assert all(nw[k] >= v for k, v in ow.items()), '%s: existing words lost' % f
    added = nw - ow
    expected = words(band)
    assert added == expected, ('%s: unexpected word delta\n  extra=%s\n  missing=%s'
                               % (f, added - expected, expected - added))

    assert len(section_bounds(new_m)) == len(secs) + 1, '%s: section count' % f
    assert new_m.count(MARK) == 1, '%s: #classifications not exactly once' % f
    assert new_m.count('cross-link-rail__cards--four') == 1, '%s: variant class' % f
    assert new_m.count('clc__media') == 4, '%s: expected 4 card images' % f
    assert len(re.findall(r'<h1\b', new_m)) == 1, '%s: h1 count' % f
    assert 'type-%s.html' % self_type not in band, '%s: self-link in band' % f
    assert not stray_gt(new_text), '%s: stray ">"' % f
    for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p'):
        o = len(re.findall(r'<%s\b' % tag, band))
        c = len(re.findall(r'</%s>' % tag, band))
        assert o == c, '%s: unbalanced <%s> in band (%d/%d)' % (f, tag, o, c)

    if IMG['20'][0] in used and self_type != '20':
        notes.append((f, 'Type 20 card repeats the hero backdrop inventory-shelves.jpg'))
    staged[f] = new_text

# ---- nothing is written until every page has passed ------------------------
if not staged:
    print('no-op: all %d type pages already carry the band' % len(skipped))
    sys.exit(0)

assert len(staged) + len(skipped) == 50, 'accounting: %d staged + %d skipped' % (
    len(staged), len(skipped))

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

print('wrote the band to %d type pages (%d already had it)' % (len(staged), len(skipped)))
mk = sorted({re.match(r'liquor-license-(.+)-type-\d+\.html$', f).group(1) for f in staged})
print('markets covered (%d): %s' % (len(mk), ', '.join(mk)))
print('cards per page: 4 (self excluded) | images per page: 4')
n41 = sum(1 for f in staged if ALT_41[0] in staged[f].split(MARK)[1][:2600])
print('flagged, hero-backdrop repeat on the Type 20 card: %d pages' % len(notes))
for f, why in notes:
    print('   %-46s %s' % (f, why))
