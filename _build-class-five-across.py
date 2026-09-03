#!/usr/bin/env python3
"""
K-A: the five classification cards on one row (owner picked 2026-09-03), with the
type and spacing re-tuned for the narrower card.

WHY THE TUNING IS THE ACTUAL WORK. [CQ]'s card is sized for a 278px column: 22px
of side padding, a 16px name at line-height 1.35, and a 10px gap. Dropping to five
across makes the card 219px, which leaves only 175px of text measure -- the longest
name ("Type 41 - On-Sale Beer & Wine, Eating Place") went from 4 lines to 5 and the
card started to read cramped. So this block reduces the padding to buy measure back
and steps the type down with it, rather than just changing the column count.

SCOPED TO #classifications ONLY. The 31 link-card rails elsewhere keep [CQ]'s
sizing untouched -- they are 4-up at 278px and nothing here reaches them.

DESKTOP ONLY. Below 1001px the band is already 2-up (and 2-up again under 600px via
[CQ]'s small-screen arm), where 219px columns would not exist and the tighter
padding would be wrong.
"""
import re, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
CSS  = os.path.join(ROOT, 'design-system', 'structural.css')

css = io.open(CSS, encoding='utf-8').read()
# the rules this block depends on must still exist
for need in ('.cross-link-rail--cards .cross-link-rail__cards > li',
             '.cross-link-rail--cards .clc__name',
             '.cross-link-rail--cards .clc__go'):
    assert need in css, 'missing base rule: ' + need

prev = re.search(r'\n*/\* =+\n   \[CU\].*?(?=\n\n/\* =|\Z)', css, re.S)
had = bool(prev)
if prev: css = css[:prev.start()] + css[prev.end():]

BLOCK = '''

/* ==========================================================================
   [CU] THE FIVE CLASSIFICATIONS ON ONE ROW (owner picked K-A, 2026-09-03)
   --------------------------------------------------------------------------
   Five cards previously wrapped 4 + 1, leaving 875px of empty width beside the
   lone card on row two. The card was centred; the GAP was the imbalance. One row
   removes it by construction and takes the band 834px -> ~545px.

   THE RE-TUNE IS THE POINT, NOT THE COLUMN COUNT. [CQ]'s card is sized for a
   278px column -- 22px side padding, a 16px name at 1.35, a 10px gap. At 219px
   that leaves 175px of text measure, and the longest name
   ("Type 41 - On-Sale Beer & Wine, Eating Place") ran to five tight lines.
   Padding comes down to buy measure back, and the type steps down with it so the
   line count does not simply move the cramping somewhere else.

   SCOPED TO THIS BAND. The 31 link-card rails elsewhere stay on [CQ]'s sizing.
   DESKTOP ONLY: below 1001px this band is 2-up, where 219px columns do not exist.
   ========================================================================== */
/* THREE-UP THROUGH THE NARROW DESKTOP RANGE. Five across only holds while the
   card stays wide enough for a two-line name. Measured: 219px at 1440 and 215px at
   1180 give two lines on all five, but 199px at 1100 and 184px at 1024 break the
   longest names to three -- and unevenly (2/2/3/3/3), which reads as an accident
   rather than a rhythm. Between 1001 and 1179 the band therefore goes 3 + 2 on
   wider cards instead, which keeps every name at two lines. [CQ]'s 4-up would
   re-introduce the 4 + 1 gap this change exists to remove. */
@media (min-width: 1001px) and (max-width: 1179px) {
  #classifications .cross-link-rail__cards > li {
    flex-basis: calc((100% - 2 * 14px) / 3);
  }
}
@media (min-width: 1180px) {
  #classifications .cross-link-rail__cards > li {
    flex-basis: calc((100% - 4 * 14px) / 5);
  }
}
@media (min-width: 1001px) {
  #classifications .cross-link-rail__cards a {
    padding: 0 16px 16px;        /* the media is flush to the top, so no top pad */
    gap: 7px;
  }
  #classifications .clc__media {
    margin-inline: -16px;        /* re-cancel: the side padding changed */
    margin-bottom: 14px;
  }
  #classifications .clc__name {
    font-size: 15px;
    line-height: 1.32;
  }
  #classifications .clc__go {
    font-size: 12.5px;
    padding-top: 2px;
  }
}
'''
io.open(CSS, 'w', encoding='utf-8').write(css.rstrip('\n') + BLOCK)
assert io.open(CSS, encoding='utf-8').read().count('[CU]') == 1
print('[CU] %s (%d bytes)' % ('regenerated' if had else 'appended', len(BLOCK)))
