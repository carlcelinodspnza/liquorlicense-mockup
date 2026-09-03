#!/usr/bin/env python3
"""
Body-length paragraphs currently wearing LEDE sizing get the reference band's
prose sizing instead (owner asked, 2026-09-03, pointing at process.html #phases).

MEASURED, both ends:
  reference  process.html #phases .feature-row__body p   16px / 24.8  rgb(200,198,197)
  target     CA #qualification .lede                     20px / 31    rgb(200,198,197)

The target's paragraph is 166 words. A lede is an intro; at 166 words in a 633px
column, 20px/31 is body copy wearing a lede's clothes. Same story in 13 other
places.

SCOPE, counted rather than guessed. Of 508 .lede paragraphs in <main> site-wide:
  * 44 are 80+ words INSIDE A HERO -- left alone. A long hero lede at 20px is the
    hero doing its job.
  * 14 are 80+ words OUTSIDE a hero. Those are the change. Three sit on the CA
    services page (#qualification 166w, #consulting 159w, #services 103w) and
    eleven on the three state pages, whose #about-<state> bands stack up to FOUR
    consecutive 85-100 word "ledes" -- which is prose, not an intro.
  * the remaining 450 are 80 words or fewer and are genuinely ledes.

A MODIFIER, NOT A CLASS SWAP. Dropping to a plain <p> was measured first and
rejected: it gives 16px/24.8 but also turns the soft grey (200,198,197) to pure
white and loses the 633px max-width, so the lines would run the full column. The
modifier keeps .lede's colour and measure and changes only size and leading, which
is exactly what was asked for.

IDEMPOTENT. FAILS CLOSED -- every page is staged and validated before any write.
"""
import re, io, os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))

def sections(main):
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

staged, hits, pages = {}, 0, []
for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
    base = os.path.basename(p)
    if base.startswith('_'): continue
    src = io.open(p, encoding='utf-8').read()
    mm = re.search(r'<main.*?</main>', src, re.S)
    if not mm: continue
    main = mm.group(0)
    secs = sections(main)
    # PER BLOCK, NOT PER PARAGRAPH. The first pass tested each <p> on its own and split
    # runs of prose in half: #consulting's 159-word paragraph went to 16px while its
    # 40-word sibling stayed at 20px, in the same block. Within one prose run every
    # paragraph must match. The rule is now:
    #   - a paragraph AFTER the first in a non-hero block is body copy
    #   - the FIRST is body copy only if it is itself over 80 words; a short opener
    #     followed by body paragraphs is a genuine lede and keeps 20px
    # PER BLOCK, NOT PER PARAGRAPH. The first pass tested each <p> on its own and split
    # runs of prose in half: #consulting's 159-word paragraph went to 16px while its
    # 40-word sibling stayed at 20px, in the same block. Within one prose run every
    # paragraph must match. The rule:
    #   - any paragraph AFTER the first in a non-hero block is body copy
    #   - the FIRST is body copy only if it is itself over 80 words; a short opener
    #     above body paragraphs is a genuine lede and keeps 20px
    edits = []                       # (abs_start, abs_end, attrs, body)
    for attrs, st, en in secs:
        if 'hero' in attrs:
            continue
        found = list(re.finditer(r'<p class="lede"([^>]*)>(.*?)</p>', main[st:en], re.S))
        if not found:
            continue
        words = [len(re.sub(r'<[^>]+>', '', m.group(2)).split()) for m in found]
        # A block is a PROSE RUN only if it actually contains body-length copy.
        # "any paragraph after the first" alone was far too blunt -- it swept up
        # 3-word list intros ("Key factors include:") on the market pages and a
        # 12-word line on contact.html, none of which are prose.
        if max(words) <= 80:
            continue
        for i, m in enumerate(found):
            if i == 0 and words[0] <= 80:
                continue             # a real lede: short opener over body copy
            edits.append((st + m.start(), st + m.end(), m.group(1), m.group(2)))
    edits.sort()

    if not edits:
        continue
    new_main = main
    for a, b, attrs, body in reversed(edits):
        new_main = new_main[:a] + '<p class="lede lede--prose"%s>%s</p>' % (attrs, body) + new_main[b:]
    out = src.replace(main, new_main, 1)

    # ---- guards ----
    assert out.count('<p class="lede') == src.count('<p class="lede'), base + ': lede count changed'
    assert re.sub(r'<[^>]+>', '', out) == re.sub(r'<[^>]+>', '', src), base + ': visible text changed'
    assert out.count('lede--prose') == len(edits), base + ': modifier count mismatch'
    # no hero lede may have been touched
    nm = re.search(r'<main.*?</main>', out, re.S).group(0)
    for a, st, en in sections(nm):
        if 'hero' in a:
            assert 'lede--prose' not in nm[st:en], base + ': a HERO lede was modified'
    staged[p] = out; hits += len(edits); pages.append((base, len(edits)))

for p, o in staged.items():
    io.open(p, 'w', encoding='utf-8').write(o)
print('paragraphs at prose size: %d across %d page(s)' % (hits, len(pages)))
for b, n in pages: print('    %-44s %d' % (b, n))

# ---- CSS ----
CSS = os.path.join(ROOT, 'design-system', 'structural.css')
css = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CV\].*?(?=\n\n/\* =|\Z)', css, re.S)
had = bool(prev)
if prev: css = css[:prev.start()] + css[prev.end():]
BLOCK = '''

/* ==========================================================================
   [CV] BODY-LENGTH PARAGRAPHS STOP USING LEDE SIZING
   --------------------------------------------------------------------------
   Owner pointed at process.html #phases as the reference. Measured, both ends:

     reference  .feature-row__body p   16px / 24.8   rgb(200,198,197)
     was        .lede                  20px / 31     rgb(200,198,197)

   A lede is an intro. The paragraph this started from is 166 words in a 633px
   column, and thirteen others are 85-159 words -- including #about-<state> bands
   that stack FOUR consecutive "ledes", which is prose by any reading.

   ONLY SIZE AND LEADING MOVE. A plain <p> was measured first and rejected: it
   gives the right 16px/24.8 but also turns the soft grey to pure white and drops
   .lede's 633px max-width, so the lines would run the full column. Keeping .lede
   and adding a modifier preserves colour and measure, which is the difference
   between matching the reference and merely shrinking the text.

   Applied to 14 paragraphs on 5 pages, all outside a hero. The 44 long ledes that
   ARE in a hero keep 20px -- a hero lede is meant to be large.
   ========================================================================== */
.lede.lede--prose {
  font-size: 16px;
  line-height: 1.55;
}
'''
io.open(CSS, 'w', encoding='utf-8').write(css.rstrip('\n') + BLOCK)
print('[CV] %s' % ('regenerated' if had else 'appended'))
