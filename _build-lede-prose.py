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
    edits = []
    for m in re.finditer(r'<p class="lede"([^>]*)>(.*?)</p>', main, re.S):
        words = len(re.sub(r'<[^>]+>', '', m.group(2)).split())
        host = next((a for a, st, en in secs if st <= m.start() < en), '')
        if 'hero' in host or words <= 80:
            continue
        edits.append(m)
    if not edits:
        continue
    new_main = main
    for m in reversed(edits):
        rep = '<p class="lede lede--prose"%s>%s</p>' % (m.group(1), m.group(2))
        new_main = new_main[:m.start()] + rep + new_main[m.end():]
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

if 'lede--prose' in io.open(os.path.join(ROOT, 'california-liquor-license-services.html'), encoding='utf-8').read():
    print('markup already applied')
else:
    for p, o in staged.items():
        io.open(p, 'w', encoding='utf-8').write(o)
    print('paragraphs re-sized: %d across %d page(s)' % (hits, len(pages)))
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
