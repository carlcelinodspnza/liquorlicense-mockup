#!/usr/bin/env python3
"""
Give "The five we are asked for most" its own row on
california-liquor-license-services.html, with the five classifications as cards.

REUSES THE CARD COMPONENT THE OWNER APPROVED TODAY -- .cross-link-rail--cards /
.cross-link-rail__cards / .clc__name / .clc__go, shipped in [CQ] to 31 rails. It
is now the site's generic "list of links as cards" treatment: it needs no images,
it centres a short final row (five cards land 4 + 1), and reusing it means ZERO
new CSS.

POINTER CARDS, NO DEFINITIONS -- and that is the dedup ledger, not a style choice.
Rows C18-C20 give the Type 21/47/48 definitions to licence-types.html, and the
band's own closing note already says the classifications page "owns those
definitions". index.html's .lic-card carries a definition sentence in its body;
copying that shape here would have duplicated an owned claim, or forced me to
write five definitions. The cards carry the classification name and route, nothing
more.

THE PHOTO IS DROPPED, deliberately and worth stating: hero-licence-types.jpg was a
single decorative image at the head of a narrow card. Across a full-width row of
five cards there is no natural place for one shared photo, and each card now
carries its own identity. Nothing else about the band changes.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, html as html_mod
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')

src = io.open(PAGE, encoding='utf-8').read()
if 'id="classifications"' in src and 'cross-link-rail__cards' in src:
    print('already applied -- no-op'); raise SystemExit(0)

card = re.search(r'\s*<article class="ca-card" id="classifications">.*?</article>', src, re.S)
assert card, 'the #classifications ca-card is not in the expected shape'
c = card.group(0)

eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', c, re.S).group(1).strip()
head    = re.search(r'<h3>(.*?)</h3>', c, re.S).group(1).strip()
note    = re.search(r'<p class="tp-note">(.*?)</p>', c, re.S).group(1).strip()
items   = re.findall(r'<li><a href="([^"]+)"><strong>(.*?)</strong>(.*?)</a></li>', c, re.S)
assert len(items) == 5, 'expected 5 classifications, found %d' % len(items)

cards = ''.join(
    '\n        <li><a href="%s"><span class="clc__name"><strong>%s</strong>%s</span>'
    '<span class="clc__go">View classification &rarr;</span></a></li>' % (h, num, rest)
    for h, num, rest in items)

band = ('\n<section class="section section--dark" id="classifications">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">%s</p>\n'
        '    <h2>%s</h2>\n'
        '    <div class="cross-link-rail cross-link-rail--cards">\n'
        '      <ul class="cross-link-rail__cards" role="list">%s\n      </ul>\n'
        '    </div>\n'
        '    <p class="tp-note">%s</p>\n'
        '  </div>\n</section>\n' % (eyebrow, head, cards, note))

out = src.replace(c, '', 1)
m = re.search(r'<section class="section ca-cards">', out)
assert m, 'no ca-cards section'
st = m.start(); d = 0
for t in re.finditer(r'<(/?)section\b[^>]*>', out[st:]):
    d += 1 if not t.group(1) else -1
    if d == 0: en = st + t.end(); break
out = out[:en] + band + out[en:]

# ---------------- guards ----------------
def words(h):
    # decode entities BEFORE tokenising -- otherwise "&rarr;" counts as the word
    # "rarr" and an arrow glyph reads as invented copy
    return Counter(re.findall(r"[A-Za-z0-9’'-]+",
                              html_mod.unescape(re.sub(r'<[^>]+>', ' ', h))))
main0 = re.search(r'<main.*?</main>', src, re.S).group(0)
main1 = re.search(r'<main.*?</main>', out, re.S).group(0)
missing = words(main0) - words(main1)
added   = words(main1) - words(main0)
assert not missing, 'WORDS LOST: %s' % dict(list(missing.items())[:8])
# only the repeated card affordance may be new -- no definitions, no new prose
assert added == Counter({'View': 5, 'classification': 5}), \
    'unexpected new copy (only the card affordance is allowed): %s' % dict(added)

hrefs_before = re.findall(r'href="([^"]+)"', c)
hrefs_after  = re.findall(r'href="([^"]+)"', band)
assert hrefs_before == hrefs_after, 'links changed:\n %r\n %r' % (hrefs_before, hrefs_after)
assert out.count('<article class="ca-card"') == 1, 'expected 1 remaining ca-card, got %d' % out.count('<article class="ca-card"')
assert out.count('clc__name') == 5 and out.count('clc__go') == 5
assert out.count('<h1') == 1
assert out.count('<section') == src.count('<section') + 1
assert out.count('</section>') == src.count('</section>') + 1
t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
assert '>' not in t, 'stray ">" introduced'

io.open(PAGE, 'w', encoding='utf-8').write(out)
print('classifications band built: own row, 5 pointer cards, no new CSS.')
print('  kept verbatim: eyebrow %r / heading %r' % (eyebrow, head))
print('  ca-cards left: 1 (#corporate)')
