#!/usr/bin/env python3
"""
Owner picked R-C (cards) for the cross-link rails, applied to all 31 matching ones.

WHY R-C, from the stress test: it is the only treatment that balances all three shapes
the 31 rails come in -- 7 links wrap 4+3, 12 wrap 4+4+4, and the four long
classification labels fit on ONE row (they orphan 3+1 under every other option).
Tap target goes 25px -> 94px. Cost: it is the tallest, +147px on a seven-link rail.

SCOPE, counted not assumed: 58 `.cross-link-rail__rail` exist across 44 pages. Exactly
31 use the `label + rail` pair with one of four known labels ("The other seven services",
"Other markets we cover", "The other seven business types", "The other four
classifications"). Those 31 are converted -- one per page, 31 pages. The other 27 sit in
different structures (process, contact, about, faq, ...) and are left untouched; the
generator asserts both counts.

The converted rails get a MODIFIER class, `cross-link-rail--cards`, so [CQ] styles only
what was actually converted rather than the component as a whole.

COPY: each card carries a "View <noun> ->" affordance. The noun is DERIVED from the rail's
own existing label, not invented -- services->service, markets->market, business types->
business type, classifications->classification. The middot separators are dropped; they
were punctuation between links, not content.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, glob
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
CSS  = os.path.join(ROOT, 'design-system', 'structural.css')

NOUN = {
    'The other seven services':       'service',
    'Other markets we cover':         'market',
    'The other seven business types': 'business type',
    'The other four classifications': 'classification',
}
PAT = re.compile(
    r'<div class="cross-link-rail">\s*'
    r'<p class="cross-link-rail__label">(.*?)</p>\s*'
    r'<p class="cross-link-rail__rail">(.*?)</p>', re.S)

pages = [p for p in sorted(glob.glob(os.path.join(ROOT, '*.html')))
         if not os.path.basename(p).startswith('_')]

# ---------------- pass 1: markup ----------------
staged, converted, per_shape = {}, 0, Counter()
total_rails = other_rails = 0
for p in pages:
    base = os.path.basename(p)
    src = io.open(p, encoding='utf-8').read()
    total_rails += len(re.findall(r'cross-link-rail__rail', src))
    if 'cross-link-rail--cards' in src:
        continue                                   # already converted

    out, n = src, 0
    for m in list(PAT.finditer(src)):
        label = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if label not in NOUN:
            continue
        anchors = re.findall(r'<a\b[^>]*>.*?</a>', m.group(2), re.S)
        assert anchors, base + ': rail with no anchors'
        noun = NOUN[label]
        cards = ''.join(
            re.sub(r'>(.*?)</a>$',
                   lambda t: '><span class="clc__name">%s</span>'
                             '<span class="clc__go">View %s &rarr;</span></a>' % (t.group(1), noun),
                   a, flags=re.S)
            for a in anchors)
        cards = ''.join('<li>%s</li>' % c for c in re.findall(r'<a\b[^>]*>.*?</a>', cards, re.S))
        new = ('<div class="cross-link-rail cross-link-rail--cards">\n'
               '      <p class="cross-link-rail__label">%s</p>\n'
               '      <ul class="cross-link-rail__cards" role="list">%s</ul>'
               % (m.group(1), cards))
        assert out.count(m.group(0)) == 1, base + ': rail block not unique'
        out = out.replace(m.group(0), new)
        n += 1; per_shape[(label, len(anchors))] += 1

        # ---- per-rail guards ----
        before = re.findall(r'href="([^"]+)"', m.group(2))
        after  = re.findall(r'href="([^"]+)"', new)
        assert before == after, '%s: hrefs changed %r -> %r' % (base, before, after)
        names_before = [re.sub(r'<[^>]+>', '', a).strip() for a in anchors]
        names_after  = re.findall(r'<span class="clc__name">(.*?)</span>', new, re.S)
        assert names_before == names_after, base + ': link text changed'
    if n:
        assert out.count('<a ') == src.count('<a '), base + ': anchor count changed'
        assert out.count('<h1') == src.count('<h1'), base + ': h1 changed'
        t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
        t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
        assert '>' not in t, base + ': stray ">" introduced'
        staged[p] = out; converted += n

for p in pages:
    s = staged.get(p) or io.open(p, encoding='utf-8').read()
    # count the CLASS, not one exact tag spelling -- the 27 untouched rails are not
    # all written as `<p class="cross-link-rail__rail">`, so the strict form undercounts
    other_rails += len(re.findall(r'cross-link-rail__rail', s))

for p, o in staged.items():
    io.open(p, 'w', encoding='utf-8').write(o)

print('rails converted this run : %d across %d page(s)' % (converted, len(staged)))
for (l, n), v in per_shape.most_common():
    print('    %-40s %2d links  x%d' % (l, n, v))
print('rails LEFT as prose rails: %d  (the non-matching structures)' % other_rails)
assert converted == 0 or converted + other_rails == 58, \
    'rail total drifted: %d converted + %d prose != 58' % (converted, other_rails)

# ---------------- pass 2: CSS ----------------
src = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CQ\].*?(?=\n\n/\* =|\Z)', src, re.S)
had = bool(prev)
if prev: src = src[:prev.start()] + src[prev.end():]

BLOCK = '''

/* ==========================================================================
   [CQ] CROSS-LINK RAILS AS CARDS (owner picked R-C, 2026-09-03)
   --------------------------------------------------------------------------
   Replaces a centred, middot-separated, underlined run of links. Measured on
   the live page first: the seven-service rail was 106px, wrapped 5 + 2 leaving
   an orphan line, and its tap targets were 25px tall.

   R-C WON ON THE STRESS TEST, not on looks. These rails come in three shapes,
   and it is the only treatment that balances all of them:
       7 links  -> 4 + 3      (pills and columns both orphan)
       12 links -> 4 + 4 + 4
       4 links  -> one row    (every other option orphans 3 + 1, because the
                               classification labels are ~340px wide)
   Tap target 25px -> 94px. The cost is height: +147px on a seven-link rail.

   FLEX, NOT GRID, and that is the owner's centring request (2026-09-03). CSS Grid places
   leftover items from the start of the row, so seven cards in a four-column grid left the
   last three hard against the left edge with a card-sized hole on the right. Grid has no
   way to centre only the leftover items. Flex with `justify-content: center` does it for
   free, and because each item's basis still divides the row exactly, a FULL row is
   unchanged -- centring a row that already spans the container is a no-op. Equal heights
   survive: flex items stretch by default, and the inner <a> is height:100%.

   SCOPED BY MODIFIER, not by component. 58 rails exist site-wide; only the 31
   that are "other N things" lists were converted, and only those carry
   `--cards`. The other 27 keep the prose rail untouched.

   The underline override is the same (0,3,1) fight as [CO]: the sheet's a11y
   rule `.section :is(p,li,...) a:not([class])` underlines every classless link
   in a section and beats a plain `.cross-link-rail__cards a` (0,2,1). Adding
   `li` and `:not([class])` makes this (0,3,2) and wins outright. The card frame
   is the non-colour affordance in the underline's place, and the link keeps the
   same accent colour that rule sets.
   ========================================================================== */
.cross-link-rail--cards .cross-link-rail__label {
  margin: 0 0 18px;
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--ds-ink-on-dark, #fff) 50%, transparent);
}
.cross-link-rail--cards .cross-link-rail__cards {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;             /* NOT grid -- see the note above about centring short rows */
  flex-wrap: wrap;
  justify-content: center;
  gap: 14px;
  text-align: left;          /* the band is .closing-cta (centred); the cards are not */
}
/* One card per "column", sized so a full row still spans the container exactly. The
   column counts and their breakpoints were MEASURED off the previous auto-fit grid
   (2-up below 830px, 3-up 830-1089, 4-up from 1090) so the layout is unchanged at every
   width -- the only difference is that a short final row now centres. */
.cross-link-rail--cards .cross-link-rail__cards > li {
  flex: 0 1 calc((100% - 14px) / 2);
  min-width: 0;
}
@media (min-width: 830px) {
  .cross-link-rail--cards .cross-link-rail__cards > li { flex-basis: calc((100% - 2 * 14px) / 3); }
}
@media (min-width: 1090px) {
  .cross-link-rail--cards .cross-link-rail__cards > li { flex-basis: calc((100% - 3 * 14px) / 4); }
}
.cross-link-rail--cards .cross-link-rail__cards a {
  display: flex;
  flex-direction: column;
  gap: 10px;
  height: 100%;
  padding: 20px 22px;
  border: 1px solid color-mix(in srgb, var(--ds-ink-on-dark, #fff) 10%, transparent);
  border-radius: var(--ds-r-lg, 10px);
  background: color-mix(in srgb, var(--ds-ink-on-dark, #fff) 3%, transparent);
  transition: border-color .16s ease, background .16s ease;
}
.cross-link-rail--cards .cross-link-rail__cards li a:not([class]) { text-decoration: none; }
.cross-link-rail--cards .cross-link-rail__cards a:hover,
.cross-link-rail--cards .cross-link-rail__cards a:focus-visible {
  border-color: var(--ds-accent, #e69c4e);
  background: color-mix(in srgb, var(--ds-accent, #e69c4e) 8%, transparent);
}
.cross-link-rail--cards .clc__name {
  color: var(--ds-ink-on-dark, #fff);
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
}
.cross-link-rail--cards .clc__go {
  margin-top: auto;
  color: var(--ds-accent-ink, #eba459);
  font-size: 13px;
}
@media (prefers-reduced-motion: reduce) {
  .cross-link-rail--cards .cross-link-rail__cards a { transition: none; }
}

/* TWO-UP ON SMALL SCREENS (owner asked, 2026-09-03, after seeing the one-up cost).
   auto-fit with a 250px floor drops to a single column below ~560px, which made the
   twelve-market rail 1308px tall on a 375px phone and the seven-link rail 770px.
   Forcing two columns halves that.

   600px, and the number was MEASURED rather than assumed. My first attempt used 560px on
   the theory that auto-fit was already giving two columns there. It was not: at a 561px
   viewport the container is 513px and two 250px tracks plus the 14px gap need 514px, so
   auto-fit fell back to ONE column and the twelve-market rail sprang back to 1308px in a
   one-pixel-wide dead zone. 600px clears it with margin -- at 601px the container is 553px,
   comfortably over the 514px needed -- so the two-column run is continuous from 320px up.
   Padding and the name size step down with it, because a ~156px card cannot carry 22px
   of side padding and a 16px name without the longest labels -- "San Bernardino County",
   "Type 41 - On-Sale Beer & Wine, Eating Place" -- running to five or six lines. */
@media (max-width: 600px) {
  .cross-link-rail--cards .cross-link-rail__cards { gap: 10px; }
  .cross-link-rail--cards .cross-link-rail__cards > li { flex-basis: calc((100% - 10px) / 2); }
  .cross-link-rail--cards .cross-link-rail__cards a { padding: 14px 15px; gap: 8px; }
  .cross-link-rail--cards .clc__name { font-size: 14.5px; line-height: 1.3; }
  .cross-link-rail--cards .clc__go   { font-size: 12px; }
}
'''
out = src.rstrip('\n') + BLOCK
assert out.count('[CQ]') == 1
io.open(CSS, 'w', encoding='utf-8').write(out)
print('[CQ] %s (%d bytes)' % ('regenerated' if had else 'appended', len(BLOCK)))
