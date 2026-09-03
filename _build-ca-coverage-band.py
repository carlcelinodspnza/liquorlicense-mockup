#!/usr/bin/env python3
"""
Replace the "Where we broker in California" ca-card on
california-liquor-license-services.html with the homepage's coverage band layout
(map + copy + market chips + one route), as the owner asked.

REUSES id="coverage" DELIBERATELY, so ZERO new CSS is needed. The .cv-* components
are global, but their spacing is tuned by #coverage-scoped rules inside media
queries, and structural.css:15326 documents a specificity trap there
(`#coverage .cv-map` is (1,0,1) and beats a plain `.cv-map`). Writing a parallel
set of rules for #where would have to re-win that fight and could drift; adopting
the id inherits the tuning as-is. The page has no #coverage today and nothing on
the site links to its #where, so the id is free to take.

THE PAGE KEEPS ITS OWN WORDS. The homepage band's sentences ("Local experts in
every major market", "We work every county in the state...") are NOT copied --
that would duplicate a claim the dedup ledger governs. The card's own eyebrow,
heading, line and CTA carry over verbatim; only the layout changes.

THIRTEEN CHIPS, NOT TWELVE. The card's own copy says "Thirteen named markets",
and the canonical list used by the 25 .mkt-list bands has 13. The homepage shows
only 12 -- it omits San Bernardino County. Copying the homepage's 12 would have
put "Thirteen named markets" directly above twelve chips on the same page.

Chips stay INERT <span>s, matching the homepage and for the reason recorded there:
a bare anchor in a div is not reached by the [AC] prose-link relight and falls back
to UA blue.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')

# canonical 13, taken from the .mkt-list the other 25 pages carry
MARKETS = ['Los Angeles County', 'Orange County', 'Riverside County', 'Sacramento County',
           'San Bernardino County', 'San Diego County', 'San Francisco County', 'Fresno',
           'Napa Valley', 'Palm Springs', 'San Jose', 'Santa Barbara', 'Ventura']

src = io.open(PAGE, encoding='utf-8').read()

# verify the canonical list against a page that actually carries it
ref = io.open(os.path.join(ROOT, 'service-buy.html'), encoding='utf-8').read()
ref_ul = re.search(r'<ul class="mkt-list">(.*?)</ul>', ref, re.S).group(1)
ref_names = [re.sub(r'<[^>]+>', '', n).strip()
             for _, n in re.findall(r'<a href="([^"]+)">(.*?)</a>', ref_ul)]
assert ref_names == MARKETS, 'market list drifted from the site canon:\n %r\n %r' % (ref_names, MARKETS)

if 'id="coverage"' in src:
    print('already applied -- no-op')
    raise SystemExit(0)

# ---- pull the existing card out ----
card = re.search(r'\s*<article class="ca-card" id="where">.*?</article>', src, re.S)
assert card, 'the #where ca-card is not in the expected shape'
c = card.group(0)
eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', c, re.S).group(1).strip()
head    = re.search(r'<h3>(.*?)</h3>', c, re.S).group(1).strip()
line    = re.search(r'<h3>.*?</h3>\s*<p>(.*?)</p>', c, re.S).group(1).strip()
cta     = re.search(r'<a class="btn[^"]*" href="([^"]+)">(.*?)</a>', c, re.S)
img_alt = re.search(r'<img[^>]*alt="([^"]*)"', c).group(1)
assert cta, 'no CTA in the card'

chips = ''.join('<span class="cv-chip">%s</span>' % m for m in MARKETS)
band = ('\n<section class="section service-pillars section--warm" id="coverage">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">%s</p>\n'
        '    <h2>%s</h2>\n'
        '    <div class="cv-map wow-reveal"><img src="assets/coverage-california-map.jpg" alt="%s"'
        ' width="1400" height="933" loading="lazy" decoding="async"></div>\n'
        '    <div class="cv-copy">\n'
        '      <div class="cv-copy__intro">\n'
        '        <p>%s</p>\n'
        '        <div class="cta-row"><a class="btn btn-primary wow-glow" href="%s">%s</a></div>\n'
        '      </div>\n'
        '      <div class="cv-markets wow-stagger">%s</div>\n'
        '    </div>\n'
        '  </div>\n</section>\n'
        % (eyebrow, head, img_alt, line, cta.group(1), cta.group(2).strip(), chips))

out = src.replace(c, '', 1)                       # drop the card
# place the new band immediately after the ca-cards section
m = re.search(r'<section class="section ca-cards">', out)
assert m, 'no ca-cards section'
st = m.start(); d = 0
for t in re.finditer(r'<(/?)section\b[^>]*>', out[st:]):
    d += 1 if not t.group(1) else -1
    if d == 0: en = st + t.end(); break
out = out[:en] + band + out[en:]

# ---------------- guards ----------------
def words(h): return Counter(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r'<[^>]+>', ' ', h)))
main0 = re.search(r'<main.*?</main>', src, re.S).group(0)
main1 = re.search(r'<main.*?</main>', out, re.S).group(0)
missing = words(main0) - words(main1)
added   = words(main1) - words(main0)
assert not missing, 'WORDS LOST from the page: %s' % dict(list(missing.items())[:8])
# the ONLY new words allowed are the market names -- no new sentences
allowed = Counter()
for m_ in MARKETS: allowed.update(re.findall(r"[A-Za-z0-9’'-]+", m_))
stray = added - allowed
assert not stray, 'INVENTED COPY (not a market name): %s' % dict(stray)

assert out.count('<article class="ca-card"') == 2, 'expected 2 remaining cards, got %d' % out.count('<article class="ca-card"')
assert out.count('cv-chip') == 13, 'expected 13 chips, got %d' % out.count('cv-chip')
assert out.count('id="coverage"') == 1 and 'id="where"' not in out
assert out.count('<h1') == 1
assert out.count('<section') == src.count('<section') + 1
assert out.count('</section>') == src.count('</section>') + 1
t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
assert '>' not in t, 'stray ">" introduced'

io.open(PAGE, 'w', encoding='utf-8').write(out)

# ---- CSS: the card grid hard-coded THREE columns for "the three short bands" ----
CSS = os.path.join(ROOT, 'design-system', 'structural.css')
css = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CS\].*?(?=\n\n/\* =|\Z)', css, re.S)
if prev: css = css[:prev.start()] + css[prev.end():]
BLOCK = '''

/* ==========================================================================
   [CS] .ca-cards__grid ADAPTS TO ITS CARD COUNT
   --------------------------------------------------------------------------
   The rule above is `repeat(3, minmax(0, 1fr))` and its comment says "the three
   short bands as one row of cards" -- true when it was written, and it hard-codes
   the count. Moving the Coverage card out to its own band left TWO cards in a
   three-column grid, i.e. a 373px hole on the right at 1440: the same short-row
   defect just fixed on the link rails, arriving by a different route.

   auto-fit collapses the empty track, so the grid now follows however many cards
   the page actually has -- two today, three again if one comes back, without
   another edit. Used on one page (california-liquor-license-services.html), and
   the <=860px single-column override further up still applies.
   ========================================================================== */
.ca-cards__grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}
'''
io.open(CSS, 'w', encoding='utf-8').write(css.rstrip('\n') + BLOCK)

print('coverage band built. ca-cards 3 -> 2, new #coverage section with 13 chips.')
print('[CS] appended -- card grid now auto-fit (was hard-coded 3 columns)')
print('  kept verbatim: eyebrow %r / h2 %r' % (eyebrow, head))
print('  new words added: market names only (%d)' % sum(added.values()))
