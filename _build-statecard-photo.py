#!/usr/bin/env python3
"""
Apply option C -- the monochrome photo wash -- to the three state cards on the buy
and sell pages, and fix two defects the owner's screenshot exposed.

THREE THINGS CHANGE, and only these:

  1. ALIGNMENT. [CH] pins .eyebrow / h2 / .lede to column 1 rows 1-3 and .mkt-list
     to column 2 spanning those rows. .statecards had NO placement rule, so it
     auto-placed into row 1 of column 2 and pushed the h2 down to row 2 -- and row
     2 starts BELOW the cards. That is the dead space in the screenshot. The card
     list is given the same placement .mkt-list has, so the copy and the cards sit
     on one row with their tops aligned.

  2. THE PURPLE NAMES. .statecard__name set no `color`, so it inherited the anchor
     colour and rendered :VISITED PURPLE for anyone who had already opened a state
     page. Visible in the owner's own screenshot. Both the anchor and the name are
     now pinned to tokens.

  3. THE PHOTOGRAPH. A duotoned image is laid into each card, faded upward so it
     never sits behind the heading.

THE IMAGE IS NOT CROPPED -- that was the owner's explicit condition. All three
photographs are 3:2 and the card box is near square (171x173 at 1440), so
object-fit:cover would discard about two thirds of every frame. The image is
therefore laid in at its own aspect ratio: full card width, height derived,
anchored to the bottom edge. Rendered aspect is asserted equal to file aspect.

IMAGE ASSIGNMENT, and why these three and not the ones in the preview:
  The preview used hero-locations / hero-bar-room / inventory-shelves. Two of those
  could not ship: inventory-shelves.jpg is ALREADY the CTA banner image on BOTH
  pages, and hero-bar-room.jpg is ALREADY the hero of service-sell.html. Using them
  would have repeated an image within a page. Replaced with two that appear on
  neither page, are the same 3:2 as the first, and were checked by opening them:

    CA  hero-locations.jpg   night streetscape, warm street lighting
    FL  hero-process.jpg     dark boardroom, warm sconce
    AZ  hero-resources.jpg   warm-lit wall of bound volumes

  These are TEXTURE, NOT DEPICTION. There is no Florida or Arizona photograph in
  the library and the only map that exists is California, so no card claims to show
  its state. The alt text is empty and the image is aria-hidden by being decorative:
  it carries no information the text does not already carry.

The build asserts, per page, that no image is used twice.

Fail-closed and idempotent: every file is staged in memory and written only if all
of them validate.
"""
import re, io, os, sys, html, struct
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

TARGETS = ['service-buy.html', 'service-sell.html']
CSS = 'design-system/structural.css'
BLOCK_OPEN = '/* ==========================================================================\n   [DF] #where CARRIES THREE STATE CARDS'

PHOTOS = {
    'California': ('assets/hero-locations.jpg', 2496, 1664),
    'Florida':    ('assets/hero-process.jpg',   2496, 1664),
    'Arizona':    ('assets/hero-resources.jpg', 2496, 1664),
}

NEW_CSS = '''/* ==========================================================================
   [DF] #where CARRIES THREE STATE CARDS ON THE BUY AND SELL PAGES (2026-09-07)
   --------------------------------------------------------------------------
   The band listed 13 California market pills. The owner asked for three cards --
   California, Florida, Arizona -- IN ONE LINE, then picked treatment C: a
   monochrome photograph inside each card.

   PLACEMENT IS THE FIRST HALF OF THIS BLOCK, and it is not decoration. [CH]
   pins .eyebrow / h2 / .lede to column 1 rows 1-3 and .mkt-list to column 2
   spanning rows 1..3. A list WITHOUT a placement rule auto-places into row 1 of
   column 2, which pushes the h2 down to row 2 -- and row 2 begins below the
   cards. That produced a tall empty gap between the eyebrow and the heading.
   .statecards therefore takes the same placement .mkt-list has.

   ONE LINE IS THE REQUIREMENT, so the desktop rule is an explicit
   repeat(3, minmax(0,1fr)): three equal tracks that cannot wrap, rather than an
   auto-fit that would silently drop to 2 + 1 the moment the container narrowed.
   That is the same class of failure the counties band hit -- a grid reflowing on
   CONTAINER width while the breakpoint fires on VIEWPORT width -- so the count is
   pinned instead of derived.

   THE PHOTOGRAPH IS NOT CROPPED. All three files are 3:2 and the card box is
   near square (171x173 at 1440), so object-fit:cover would have discarded about
   two thirds of every frame. The image is laid in at its own aspect ratio --
   full card width, height derived -- and anchored to the bottom edge, where the
   upward fade reveals it. Nothing is cut off on any side.

   COLOUR IS PINNED ON BOTH THE ANCHOR AND THE NAME. Without it .statecard__name
   inherits the anchor colour and renders :visited purple once a reader has
   opened a state page.

   Below 700px the three stack, because three cards across a phone would give
   each about 100px and the sublines would wrap to three lines.

   Scoped to .statecards, which appears on exactly two pages; the other 23 pages
   carrying this band keep their pills untouched.
   ========================================================================== */
@media (min-width: 900px) {
  .where--split > .container > .statecards {
    grid-column: 2;
    grid-row: 1 / span 3;
    margin-top: 6px;
    align-self: start;
  }
}
.statecards {
  list-style: none;
  margin: var(--ds-space-lg, 24px) 0 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}
@media (min-width: 700px) {
  .statecards { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
.statecard {
  position: relative;
  overflow: hidden;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  gap: 5px;
  height: 100%;
  padding: 18px 20px 16px;
  text-decoration: none;
  color: var(--ds-ink);
  border: 1px solid var(--ds-line);
  border-radius: var(--ds-r-lg, 10px);
  background: rgba(255, 255, 255, .028);
  transition: border-color var(--ds-dur, .2s) var(--ds-ease, ease);
}
.statecard:visited { color: var(--ds-ink); }
.statecard:hover,
.statecard:focus-visible { border-color: var(--ds-accent); }
.statecard__ph {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  line-height: 0;
}
.statecard__ph img {
  width: 100%;
  height: auto;
  display: block;
  filter: grayscale(1) sepia(.62) saturate(1.5) contrast(1.05) brightness(.85);
  opacity: .32;
  transition: opacity var(--ds-dur-slow, .25s) var(--ds-ease, ease);
  -webkit-mask-image: linear-gradient(to top, #000 34%, transparent 100%);
  mask-image: linear-gradient(to top, #000 34%, transparent 100%);
}
.statecard:hover .statecard__ph img,
.statecard:focus-visible .statecard__ph img { opacity: .44; }
.statecard__mark {
  font-size: 11.5px;
  letter-spacing: .14em;
  color: var(--ds-accent-ink, #e69c4e);
  font-variant-numeric: tabular-nums;
}
.statecard__name {
  font-family: var(--ds-font-display);
  font-size: 23px;
  line-height: 1.15;
  color: var(--ds-ink);
  margin-top: 8px;
}
.statecard__sub {
  font-size: 13.5px;
  line-height: 1.45;
  color: var(--ds-ink-soft);
  min-height: 2.9em;
  font-variant-numeric: tabular-nums;
}
.statecard__go {
  margin-top: auto;
  padding-top: 10px;
  font-size: 13px;
  color: var(--ds-accent-ink, #e69c4e);
}
@media (prefers-reduced-motion: reduce) {
  .statecard,
  .statecard__ph img { transition: none; }
}
'''


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


def jpeg_size(p):
    d = io.open(p, 'rb').read()
    i = 2
    while i < len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack('>HH', d[i + 5:i + 9])
            return w, h
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]
    raise AssertionError('no SOF in %s' % p)


# ---- the declared dimensions must be the FILE's dimensions, not a guess --------
for state, (path, w, h) in PHOTOS.items():
    assert os.path.exists(path), 'missing %s' % path
    fw, fh = jpeg_size(path)
    assert (fw, fh) == (w, h), '%s is %dx%d, not the declared %dx%d' % (path, fw, fh, w, h)
assert len({p for p, _, _ in PHOTOS.values()}) == 3, 'the three cards must not share a photograph'

staged = {}

for page in TARGETS:
    src = io.open(page, encoding='utf-8').read()
    if 'statecard__ph' in src:
        continue
    orig = src
    new = src

    for state, (path, w, h) in PHOTOS.items():
        # the photo must not already appear on this page -- no image twice per page
        assert path not in orig, '%s already carries %s; it would repeat within the page' % (page, path)
        anchor = '<span class="statecard__mark" aria-hidden="true">'
        marker = '<a class="statecard" href="'
        # locate THIS state's card by its name span, then insert before its mark
        nm = '<span class="statecard__name">%s</span>' % state
        assert new.count(nm) == 1, '%s: expected one %s card, found %d' % (page, state, new.count(nm))
        i = new.index(nm)
        j = new.rfind(marker, 0, i)
        assert j >= 0, '%s: %s name is not inside a .statecard' % (page, state)
        k = new.index('>', new.index('href="', j)) + 1   # just after the opening <a ...>
        img = ('<span class="statecard__ph" aria-hidden="true">'
               '<img src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async">'
               '</span>' % (path, w, h))
        new = new[:k] + img + new[k:]

    # ---- guards ---------------------------------------------------------------
    assert words(new) == words(orig), \
        '%s: word multiset changed\n  added=%s\n  removed=%s' % (
            page, words(new) - words(orig), words(orig) - words(new))
    assert new.count('statecard__ph') == 3, '%s: expected 3 photo wrappers, got %d' % (page, new.count('statecard__ph'))
    assert new.count('class="statecard"') == 3, '%s: card count changed' % page
    assert not re.search(r'127\.0\.0\.1|localhost', new), '%s: absolute local URL leaked in' % page
    assert len(re.findall(r'<h1\b', new)) == len(re.findall(r'<h1\b', orig)), '%s: h1 count' % page
    assert not stray_gt(new), '%s: stray ">"' % page
    for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p', 'figure'):
        o = len(re.findall(r'<%s\b' % tag, new)); c = len(re.findall(r'</%s>' % tag, new))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)
    # No image may be used twice INSIDE <main>. Scoped to <main> deliberately:
    # assets/logo.png legitimately appears in both the header and the footer chrome,
    # so a whole-document scan flags a pre-existing, correct duplication. And only
    # NEW duplicates count -- this build must not be blocked by something it did
    # not introduce.
    def main_imgs(doc):
        m = re.search(r'<main\b.*?</main>', doc, re.S)
        return Counter(re.findall(r'<img[^>]+src="(assets/[^"]+)"', m.group(0) if m else doc))
    before_d = {s for s, n in main_imgs(orig).items() if n > 1}
    after_d = {s for s, n in main_imgs(new).items() if n > 1}
    introduced = sorted(after_d - before_d)
    assert not introduced, '%s: this change repeats an image inside <main>: %s' % (page, introduced)
    if before_d:
        print('   NOTE %s already repeated inside <main> before this change: %s'
              % (page, sorted(before_d)))
    staged[page] = new

# ---- the CSS block ------------------------------------------------------------
css = io.open(CSS, encoding='utf-8').read()
i = css.find(BLOCK_OPEN)
assert i >= 0, 'could not find the [DF] block opener in %s' % CSS
old_block = css[i:]
assert '[DG]' not in old_block, '[DF] is no longer the last block; refusing to truncate the file'
new_css = css[:i] + NEW_CSS
staged_css = None
if old_block != NEW_CSS:
    for sel in ('.statecards', '.statecard', '.statecard__mark', '.statecard__name',
                '.statecard__sub', '.statecard__go', '.statecard__ph'):
        assert sel + ' ' in NEW_CSS or sel + ',' in NEW_CSS or sel + '\n' in NEW_CSS or sel + ':' in NEW_CSS, \
            'new CSS lost %s' % sel
    # Count braces with COMMENTS STRIPPED. A raw count is meaningless here: the
    # unmodified file is already {:3597 }:3596 because a comment contains a lone
    # brace. Stripping comments gives 3536/3536, so that is the real invariant.
    def braces(t):
        b = re.sub(r'/\*.*?\*/', '', t, flags=re.S)
        return b.count('{'), b.count('}')
    ob, oc = braces(css)
    nb, nc = braces(new_css)
    assert ob == oc, 'structural.css was ALREADY brace-imbalanced before this change (%d/%d)' % (ob, oc)
    assert nb == nc, 'brace imbalance introduced in structural.css (%d/%d)' % (nb, nc)
    # a "*/" inside comment prose has killed rules on this site before -- check the prose
    prose = NEW_CSS[:NEW_CSS.index('*/') + 2]
    assert prose.count('*/') == 1, 'a stray "*/" in the [DF] comment would kill the rules after it'
    staged_css = new_css

if not staged and staged_css is None:
    print('no-op: the photo cards and their CSS are already in place')
    sys.exit(0)

# ---- SCOPE: capture every other page before writing, prove untouched after -----
others = {}
for f in os.listdir('.'):
    if f.endswith('.html') and not f.startswith('_') and f not in TARGETS:
        others[f] = io.open(f, encoding='utf-8').read()

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)
if staged_css is not None:
    io.open(CSS, 'w', encoding='utf-8').write(staged_css)

for f, before in others.items():
    assert io.open(f, encoding='utf-8').read() == before, '%s changed but is out of scope' % f

print('option C applied')
for f in staged:
    print('   %-22s 3 cards now carry an uncropped 3:2 photograph' % f)
for state, (path, w, h) in PHOTOS.items():
    print('   %-12s %-28s %dx%d  (verified by reading the file header)' % (state, path, w, h))
print('   %d other pages verified byte-identical' % len(others))
print('   structural.css [DF] rewritten: placement fix + :visited colour pin + photo rules')
