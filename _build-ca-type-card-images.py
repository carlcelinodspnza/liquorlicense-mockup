#!/usr/bin/env python3
"""
Give the five classification cards images. Adds a media slot to the card component
([CT]) and one image per licence type.

EVERY IMAGE WAS CHOSEN AGAINST WHAT THE CLASSIFICATION PERMITS, and every candidate
was checked by LOOKING at the file, not by reading its alt -- three of this
library's alts are demonstrably wrong.

  Type 20  Off-Sale Beer & Wine        inventory-shelves.jpg   sealed bottles, retail, OFF-premises
  Type 21  Off-Sale General            ind-liquor-stores.jpg   racked wine and spirits, off-sale store
  Type 41  On-Sale Beer & Wine, Eating restaurants.jpg         a laid table with wine glasses -- eating
                                                               place, no bar in frame
  Type 47  On-Sale General, Eating     ind-franchise.jpg       restaurant interior WITH a bar at the
                                                               back: eating place + full bar
  Type 48  On-Sale General, Public     ind-bars-nightclubs.jpg a bar counter under neon -- public premises

THE OFF-SALE RULE HOLDS: types 20 and 21 get retail interiors, never an
on-premises drinking scene. That rule was set when the type pages were illustrated.

TWO OBVIOUS CANDIDATES WERE REJECTED ON SIGHT, and this is why the contact sheet
matters:
  * ind-convenience.jpg is a photograph of a BRANDED 7-Eleven storefront. A real
    third party's trade dress does not belong on a client mockup -- and its alt
    calls it "a convenience store chiller", which it is not.
  * ind-grocery.jpg is a supermarket aisle carrying Norwegian shelf signage
    ("DRIKKE", "Gjor det billig!"). Wrong country for a California page.
Both are what the existing [CL] type-page mapping uses for types 20/21, so this
band deliberately departs from that mapping rather than inherit those two.

ind-franchise.jpg's site alt ("a branded fast-food franchise storefront") is also
wrong -- it is an interior. A correct alt is written here.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, struct, html as html_mod
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')
CSS  = os.path.join(ROOT, 'design-system', 'structural.css')

IMG = {
 'licence-type-20.html': ('inventory-shelves.jpg',
   'Shelves of sealed bottles in a retail store'),
 'licence-type-21.html': ('ind-liquor-stores.jpg',
   'Racked wine and spirits in an off-sale store'),
 'licence-type-41.html': ('ind-restaurants.jpg',
   'A restaurant table laid for service with wine glasses'),
 'licence-type-47.html': ('ind-franchise.jpg',
   'A restaurant dining room with booth seating and a bar along the back wall'),
 'licence-type-48.html': ('ind-bars-nightclubs.jpg',
   'A bar counter and stools under low neon light'),
}

def dims(p):
    d = io.open(p, 'rb').read(); i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF: i += 1; continue
        mk = d[i+1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack('>HH', d[i+5:i+9]); return w, h
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7: i += 2; continue
        i += 2 + struct.unpack('>H', d[i+2:i+4])[0]
    raise SystemExit('cannot read ' + p)

src = io.open(PAGE, encoding='utf-8').read()

assert len(set(f for f, _ in IMG.values())) == 5, 'the five images are not distinct'

if 'clc__media' in src:
    print('markup already applied')
else:
    # no image may ALREADY be on this page. Checked inside this branch on purpose --
    # run before the early-exit it would flag the generator's own output on a re-run.
    main = re.search(r'<main.*?</main>', src, re.S).group(0)
    existing = set(re.findall(r'<img[^>]*src="assets/([^"]+)"', main))
    for href, (f, _) in IMG.items():
        assert f not in existing, 'duplicate within page: %s already used' % f
    band = re.search(r'<section class="section section--dark" id="classifications">.*?</section>', src, re.S)
    assert band, 'classifications band not found'
    b = band.group(0)
    new = b
    for href, (f, alt) in IMG.items():
        p = os.path.join(ROOT, 'assets', f)
        assert os.path.exists(p), 'missing asset ' + f
        w, h = dims(p)
        media = ('<span class="clc__media"><img src="assets/%s" alt="%s" width="%d" height="%d"'
                 ' loading="lazy" decoding="async"></span>' % (f, alt, w, h))
        pat = '<li><a href="%s"><span class="clc__name">' % href
        assert new.count(pat) == 1, 'card for %s not found once' % href
        new = new.replace(pat, '<li><a href="%s">%s<span class="clc__name">' % (href, media), 1)
    out = src.replace(b, new, 1)

    # ---- guards ----
    def words(h):
        return Counter(re.findall(r"[A-Za-z0-9’'-]+", html_mod.unescape(re.sub(r'<[^>]+>', ' ', h))))
    m0 = re.search(r'<main.*?</main>', src, re.S).group(0)
    m1 = re.search(r'<main.*?</main>', out, re.S).group(0)
    assert words(m0) == words(m1), 'visible copy changed: %s / %s' % (
        dict(list((words(m0)-words(m1)).items())[:5]), dict(list((words(m1)-words(m0)).items())[:5]))
    imgs = re.findall(r'<img[^>]*src="assets/([^"]+)"', re.search(r'<main.*?</main>', out, re.S).group(0))
    assert len(imgs) == len(set(imgs)), 'duplicate image within <main>: %s' % [k for k,v in Counter(imgs).items() if v>1]
    assert out.count('clc__media') == 5
    assert re.findall(r'href="([^"]+)"', b) == re.findall(r'href="([^"]+)"', new), 'links changed'
    for t in re.findall(r'<img[^>]*>', out):
        assert 'alt="' in t, 'img without alt'
    t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S|re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
    assert '>' not in t, 'stray ">"'
    io.open(PAGE, 'w', encoding='utf-8').write(out)
    print('5 card images added, all distinct, copy unchanged')

# ---- CSS ----
css = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CT\].*?(?=\n\n/\* =|\Z)', css, re.S)
had = bool(prev)
if prev: css = css[:prev.start()] + css[prev.end():]
BLOCK = '''

/* ==========================================================================
   [CT] A MEDIA SLOT FOR THE LINK CARD (owner asked for images, 2026-09-03)
   --------------------------------------------------------------------------
   [CQ]'s card is text-only: a name and a "View ..." affordance. This adds an
   optional image above them. It is OPT-IN by markup -- a card with no
   .clc__media is untouched, so the 31 rails already shipped are unaffected.

   The card's anchor is display:flex/column with padding; the image has to sit
   flush to the card's top and side edges, so the media is pulled out by the
   anchor's own padding with negative margins rather than the padding being
   removed (which would break every text-only card sharing the rule).

   16/9 is fixed rather than intrinsic: the five assets are 900x562 up to
   1400x933, and without a fixed box the cards in a row would have different
   image heights and the names would stop aligning.
   ========================================================================== */
.cross-link-rail--cards .cross-link-rail__cards a:has(.clc__media) { padding-top: 0; }
.clc__media {
  display: block;
  margin: 0 -22px 4px;          /* cancels the card's 22px side padding */
  border-radius: var(--ds-r-lg, 10px) var(--ds-r-lg, 10px) 0 0;
  overflow: hidden;
  line-height: 0;
}
.clc__media img {
  width: 100%;
  aspect-ratio: 16 / 9;
  height: auto;                 /* aspect-ratio only derives the missing axis */
  object-fit: cover;
  display: block;
}
@media (max-width: 600px) {
  .clc__media { margin-inline: -15px; }   /* the card's small-screen padding */
}
'''
io.open(CSS, 'w', encoding='utf-8').write(css.rstrip('\n') + BLOCK)
print('[CT] %s' % ('regenerated' if had else 'appended'))
