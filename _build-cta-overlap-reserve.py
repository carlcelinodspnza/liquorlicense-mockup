#!/usr/bin/env python3
"""
The "Getting started" banner overlaps the band above it on the 8 service pages.

MEASURED on service-new-business.html at 1440 before writing anything:
  .cta-banner  margin-top   -172.8px      (the designed straddle)
  #next        padding-bottom  72px       (plain --ds-section-py, no reserve)
  -> 173px of overlap. The "The other seven services" heading (top 3826) and all
     seven links (3867-3933) sit UNDER the banner, which spans 3832-4213.

ROOT CAUSE. The lift is paired with a reserve, but the reserve is hard-coded to
ONE id (structural.css:3911):

    .cta-banner { margin-top: calc(-1 * clamp(140px, 12vw, 176px)); }
    #faq        { padding-bottom: calc(... + clamp(140px,12vw,176px) + ...); }

`.cta-banner` is a CLASS, so the lift applies wherever the suite goes; `#faq` is
an ID, so the reserve only ever applies to one band. That was fine while the
suite only ever followed the FAQ. It stopped being fine when the suite was added
to the 8 service pages, where it follows #next. Counted: 8 pages have the suite
after #next (no reserve), 1 has it after #faq (reserved).

THE FIX pairs the reserve to the same condition as the lift -- "whatever band the
suite actually follows" -- instead of to an id. Nothing about the intended
straddle changes; the band above simply stops being shorter than the lift.

IDEMPOTENT (regenerates its own block). FAILS CLOSED.
"""
import re, io, os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
CSS = os.path.join(ROOT, 'design-system', 'structural.css')

# --- preconditions ---------------------------------------------------------
def top_sections(main):
    out, last = [], 0
    for m in re.finditer(r'<section([^>]*)>', main):
        st = m.start()
        if st < last: continue
        d = 0
        for t in re.finditer(r'<(/?)section\b[^>]*>', main[st:]):
            d += 1 if not t.group(1) else -1
            if d == 0: en = st + t.end(); break
        else: en = len(main)
        out.append((m.group(1), st, en)); last = en
    return out

affected, reserved = [], []
for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
    base = os.path.basename(p)
    if base.startswith('_'): continue
    mm = re.search(r'<main.*?</main>', io.open(p, encoding='utf-8').read(), re.S)
    if not mm: continue
    t = top_sections(mm.group(0))
    for i, (attrs, _, _) in enumerate(t):
        if 'cta-suite' not in attrs or i == 0: continue
        prev = t[i-1][0]
        assert 'class="section' in prev, '%s: band before .cta-suite is not a .section: %s' % (base, prev[:70])
        (reserved if 'id="faq"' in prev else affected).append(base)

assert affected, 'nothing to fix -- expected the 8 service pages'
print('suite follows an UNRESERVED band on %d page(s): %s'
      % (len(affected), ', '.join(sorted(affected))))
print('suite follows #faq (already reserved) on %d page(s)' % len(reserved))

src = io.open(CSS, encoding='utf-8').read()
# the lift this reserve must match, read from the sheet rather than re-typed
# Read the EFFECTIVE lift, i.e. the LAST matching declaration -- these rules are all
# `.cta-banner` at equal specificity, so source order decides. Taking the first match
# silently picks a superseded value: the sheet carries an earlier mobile -60px that is
# overridden by a later -58px, and an earlier desktop clamp(150px,16vw,232px)
# overridden by clamp(140px,12vw,176px).
lifts = re.findall(r'\.cta-banner\s*\{[^}]*margin-top:\s*calc\(-1 \* (clamp\([^)]*\))\)', src)
assert lifts, 'no .cta-banner clamp lift found -- refusing to guess'
LIFT = lifts[-1]
mobs = re.findall(r'\.cta-banner\s*\{[^}]*margin-top:\s*-(\d+px)', src)
assert mobs, 'no mobile .cta-banner lift found -- refusing to guess'
MOB = mobs[-1]
print('effective lift (last declaration wins): %s desktop / %s mobile' % (LIFT, MOB))
print('  superseded desktop values ignored: %s' % (lifts[:-1] or 'none'))
print('  superseded mobile  values ignored: %s' % (['-'+m for m in mobs[:-1]] or 'none'))

prev_blk = re.search(r'\n*/\* =+\n   \[CP\].*?(?=\n\n/\* =|\Z)', src, re.S)
had = bool(prev_blk)
if prev_blk: src = src[:prev_blk.start()] + src[prev_blk.end():]

BLOCK = '''

/* ==========================================================================
   [CP] THE CTA BANNER'S OVERLAP RESERVE, PAIRED TO THE BAND IT ACTUALLY FOLLOWS
   --------------------------------------------------------------------------
   `.cta-banner` lifts itself by %(LIFT)s so it straddles the seam into the band
   above. That lift is a CLASS, so it follows the suite wherever the suite goes.
   Its matching reserve was written as `#faq { padding-bottom: ... }` -- an ID,
   so it only ever applied to one band on one page.

   That held while the suite only followed the FAQ. Adding the suite to the 8
   service pages, where it follows #next, broke it: measured on
   service-new-business at 1440, the banner lifted -172.8px into a band reserving
   only 72px, hiding the "The other seven services" heading and all seven links
   behind the banner.

   Pairing the reserve to `:has(+ .cta-suite)` ties it to the same condition as
   the lift, so the two cannot drift apart again when the suite is placed
   somewhere new. The straddle itself is unchanged -- this only stops the band
   above from being shorter than the lift that eats into it.

   The original #faq rule is left in place: it is an ID (1,0,0) and wins over
   this (0,2,0), but computes the identical value, so it is now redundant rather
   than conflicting. Every band before the suite is a .section (asserted by the
   generator), so padding-bottom is the right lever.
   ========================================================================== */
.section:has(+ .cta-suite) {
  padding-bottom: calc(var(--ds-section-py) + %(LIFT)s + var(--ds-space-lg));
}
@media (max-width: 860px) {
  .section:has(+ .cta-suite) {
    padding-bottom: calc(var(--ds-section-py) + %(MOB)s + var(--ds-space-lg));
  }
}
''' % {'LIFT': LIFT, 'MOB': MOB}

out = src.rstrip('\n') + BLOCK
assert out.count('[CP]') == 1
io.open(CSS, 'w', encoding='utf-8').write(out)
print('[CP] %s (%d bytes)' % ('regenerated' if had else 'appended', len(BLOCK)))
