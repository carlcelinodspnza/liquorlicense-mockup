#!/usr/bin/env python3
"""
Owner picked W-B (pills) for the "Where" band, 2026-09-03.

CSS-ONLY. The markup does not change: every one of the 25 pages already carries
`<ul class="mkt-list">` inside a `.where--split` band, so restyling reaches all 25
and nothing else. Counted before writing a line of this:

  pages with .mkt-list        25
  pages with .where--split    25
  pages with BOTH             25      <- exact 1:1, no stragglers either way

Scoped to `.where--split .mkt-list` rather than bare `.mkt-list`, so if a market
list is ever dropped into some other band it keeps the old treatment until someone
decides otherwise -- the same discipline [CA] used for this band.

WHY PILLS. `.mkt-list a` is `display:block` with a `border-bottom`, so the rule runs
the full 258px column even under "Fresno": thirteen rules of identical length
regardless of label. A pill is sized by its own text, so that failure mode stops
being possible rather than being tuned away.

IDEMPOTENT: appends [CO] once. FAILS CLOSED.
"""
import re, io, os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(ROOT, 'design-system', 'structural.css')

# --- preconditions, asserted not assumed -----------------------------------
pages = [p for p in glob.glob(os.path.join(ROOT, '*.html'))
         if not os.path.basename(p).startswith('_')]
mkt = {os.path.basename(p) for p in pages if 'mkt-list' in io.open(p, encoding='utf-8').read()}
spl = {os.path.basename(p) for p in pages if 'where--split' in io.open(p, encoding='utf-8').read()}
assert mkt == spl, 'mkt-list and where--split do not coincide: %s' % (mkt ^ spl)
assert len(mkt) == 25, 'expected 25 pages carrying the band, found %d' % len(mkt)

src = io.open(CSS, encoding='utf-8').read()

# strip any previous [CO] so the block is regenerated rather than skipped --
# idempotent by REPLACEMENT, which lets the block be corrected on a re-run.
prev = re.search(r'\n*/\* =+\n   \[CO\].*?(?=\n\n/\* =|\Z)', src, re.S)
had_prev = bool(prev)
if prev:
    src = src[:prev.start()] + src[prev.end():]

# the rules being overridden must still exist, or the override is aimed at nothing
for needed in ('.mkt-list {', '.mkt-list a {', '.mkt-list a:hover'):
    assert needed in src, 'expected base rule missing: ' + needed

BLOCK = '''

/* ==========================================================================
   [CO] "WHERE" BAND -- MARKETS AS PILLS (owner picked W-B, 2026-09-03)
   --------------------------------------------------------------------------
   THE DEFECT THIS FIXES. [CA] made the markets a real <ul> in two columns, and
   `.mkt-list a` is display:block with a border-bottom. Measured on the live page:
   the columns are 258px, so the rule under "Fresno" is exactly as long as the one
   under "San Bernardino County" -- thirteen identical rules that read as an empty
   table. 13 items over 2 columns also strands one item alone on the last row.

   A pill is sized by its own label, so a trailing empty rule is not something to
   tune -- it becomes structurally impossible. Wrapping also absorbs any list
   length (the band carries 13 markets on 21 pages and 8 on the other 4).

   SCOPED TO `.where--split .mkt-list`, NOT bare `.mkt-list`. They coincide 1:1
   today (25 pages each, asserted by the generator), but the scope keeps a market
   list dropped into some other band on the old treatment until that is a decision
   rather than a side effect. Same reasoning [CA] used for this band.

   NOT `.chip`. That component already exists but is built for the light ground
   (border var(--ds-line), color var(--ds-ink)); this band is .section--dark, so
   its colours would fail here.

   Hover moves colour and background only. The base rule animates `padding-left`,
   which on a pill would resize the box and shove every later pill sideways
   mid-transition, so it is explicitly reset to 0.
   ========================================================================== */
.where--split .mkt-list {
  display: flex;
  flex-wrap: wrap;
  gap: 9px;
}
.where--split .mkt-list > li { min-width: 0; }
.where--split .mkt-list a {
  display: inline-block;
  padding: 8px 15px;
  border: 1px solid var(--ds-glass-border, rgba(230, 156, 78, .18));
  border-radius: var(--ds-r-pill, 999px);
  background: rgba(255, 255, 255, .03);
  color: var(--ds-accent-ink, #eba459);
  text-decoration: none;
  transition: color .16s ease, background .16s ease, border-color .16s ease;
}
.where--split .mkt-list a:hover,
.where--split .mkt-list a:focus-visible {
  padding-left: 15px;                    /* cancels the base rule's 6px nudge */
  color: var(--ds-ink-on-dark, #fff);
  border-color: var(--ds-accent, #e69c4e);
  background: color-mix(in srgb, var(--ds-accent, #e69c4e) 14%, transparent);
}
@media (prefers-reduced-motion: reduce) {
  .where--split .mkt-list a { transition: none; }
}

/* THE UNDERLINE. An accessibility rule further up this sheet --
     .section :is(p, li, dd, td, blockquote, .lede, .data-proof__sub) a:not([class])
   -- underlines every classless link inside a .section, at specificity (0,3,1).
   `.where--split .mkt-list a` is only (0,2,1), so the pills inherited an underline
   INSIDE their border: two affordances doing one job. (This predates the pills --
   the two-column list was underlined too.)

   Removing it here is safe, and is not a defeat of that rule's purpose: the rule
   exists because a bare UA link on a dark band fails contrast on colour alone.
   The pill keeps that rule's exact colour (--ds-accent-ink) AND adds a border and
   background, which is a stronger non-colour affordance than an underline. Scope
   is these 25 bands only; every other classless link on the site keeps its underline.

   Specificity, deliberately, not !important: adding `li` and `:not([class])` makes
   this (0,3,2), which beats (0,3,1) outright rather than relying on source order. */
.where--split .mkt-list li a:not([class]) {
  text-decoration: none;
}
'''

out = src.rstrip('\n') + BLOCK
assert out.count('[CO]') == 1
io.open(CSS, 'w', encoding='utf-8').write(out)
print('[CO] %s (%d bytes) -- applies to %d pages, no markup changed'
      % ('regenerated' if had_prev else 'appended', len(BLOCK), len(mkt)))
