#!/usr/bin/env python3
"""
Alternate the three .ca-fig bands: text-image, image-text, text-image.

The page now has three of them in a row -- Qualification, Consulting, Corporate
applications -- and all three put copy left and the figure right, so the eye
tracks down one straight edge for three full sections. Flipping the middle one
breaks that.

MIDDLE BAND ONLY, by an explicit class rather than :nth-of-type. The three are not
adjacent siblings (#classifications and #coverage sit between them), so an
nth-based rule would count the wrong things. One modifier on the one band that
flips is honest about what it does.

THE TRACK WIDTHS SWAP TOO, not just the columns. .ca-fig is a 1.5fr / 1fr grid --
the wide track carries the prose. Moving the copy to column 2 without swapping the
ratio would squeeze 200 words into the narrow column and stretch a square photo
across the wide one.

DESKTOP ONLY. Below 1000px .ca-fig already collapses to a single column with the
copy first, and it must stay that way: on a phone the reading order is
heading-then-prose-then-picture regardless of which side the figure sits on at
full width.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')
CSS  = os.path.join(ROOT, 'design-system', 'structural.css')

src = io.open(PAGE, encoding='utf-8').read()

# the three bands, in document order
figs = re.findall(r'<section class="([^"]*ca-fig[^"]*)" id="([^"]+)">', src)
assert len(figs) == 3, 'expected 3 ca-fig bands, found %d: %r' % (len(figs), figs)
order = [i for _, i in figs]
assert order == ['qualification', 'consulting', 'corporate'], 'band order changed: %r' % order

if 'ca-fig--reverse' in src:
    print('markup already alternating -- no-op')
else:
    old = '<section class="ca-fig section section--dark" id="consulting">'
    assert src.count(old) == 1, 'the middle band is not in the expected shape'
    out = src.replace(old, '<section class="ca-fig section section--dark ca-fig--reverse" id="consulting">', 1)

    # ---- guards ----
    def words(t): return Counter(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r'<[^>]+>', ' ', t)))
    m0 = re.search(r'<main.*?</main>', src, re.S).group(0)
    m1 = re.search(r'<main.*?</main>', out, re.S).group(0)
    assert words(m0) == words(m1), 'visible copy changed'
    assert out.count('ca-fig--reverse') == 1, 'more than one band flipped'
    assert out.count('<section') == src.count('<section')
    assert out.count('<img') == src.count('<img')
    t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
    assert '>' not in t, 'stray ">" introduced'
    io.open(PAGE, 'w', encoding='utf-8').write(out)
    print('#consulting flipped -> text-image / image-text / text-image')

css = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CW\].*?(?=\n\n/\* =|\Z)', css, re.S)
had = bool(prev)
if prev: css = css[:prev.start()] + css[prev.end():]
BLOCK = '''

/* ==========================================================================
   [CW] ALTERNATE THE .ca-fig BANDS (owner asked, 2026-09-03)
   --------------------------------------------------------------------------
   Three .ca-fig bands now run consecutively on the CA services page and all put
   copy left, figure right -- the eye tracks one straight edge for three sections.
   The middle band flips.

   BY MODIFIER, NOT :nth-of-type. The three are not adjacent siblings
   (#classifications and #coverage sit between them), so an nth rule would count
   the wrong elements.

   THE TRACK RATIO SWAPS WITH THE COLUMNS. .ca-fig is 1.5fr / 1fr and the WIDE
   track carries the prose. Moving the copy to column 2 without reversing the
   ratio would put 200 words in the narrow track and stretch a square photo across
   the wide one.

   DESKTOP ONLY -- below 1000px .ca-fig already collapses to one column with the
   copy first, and the reading order there is heading, prose, picture regardless
   of which side the figure takes at full width.
   ========================================================================== */
@media (min-width: 1001px) {
  .ca-fig--reverse > .container {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.5fr);
  }
  .ca-fig--reverse .ca-fig__copy   { grid-column: 2; }
  .ca-fig--reverse .ca-fig__figure { grid-column: 1; }
}
'''
io.open(CSS, 'w', encoding='utf-8').write(css.rstrip('\n') + BLOCK)
print('[CW] %s' % ('regenerated' if had else 'appended'))
