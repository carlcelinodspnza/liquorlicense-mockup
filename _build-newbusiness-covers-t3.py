#!/usr/bin/env python3
"""
Owner picked N-A + T-3 for service-new-business.html's #covers band (2026-09-03).

N-A : the flat 13-row list becomes two LABELLED columns -- Services (7) and Markets (6).
      The split is real, verified against the hrefs (services.html#* vs locations.html#*),
      not the labels. Photo stays.
T-3 : the heading goes 44px -> 42px so "Services and markets on this site" sits on ONE
      line (measured: it needs 694px at 44px and the column is 669px -- it missed by 25px),
      plus a supporting lede so the text block is not 137px of copy beside a 606px photo.

THE LEDE IS MOVED, NOT WRITTEN. It is the page's own sentence, currently the second
paragraph of #detail's sv-body, and it is literally about this list. Verified it ALSO
exists on services.html, so taking it out of #detail loses nothing site-wide. The
generator asserts the sentence appears exactly ONCE on the page afterwards -- moved, not
duplicated -- and that the page's total word count is unchanged.

FLAGGED, not hidden: the sentence says "every service" while this band also carries six
markets, so it under-describes the second column. The owner accepted that in the preview.

ONE PAGE. This is the only #covers band of its kind: the other seven hold 4-5 plain scope
items with zero links; this one holds 13 links and is a navigation index.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'service-new-business.html')
CSS  = os.path.join(ROOT, 'design-system', 'structural.css')

LEDE = ('Every service here ends at a question this page deliberately does not answer twice. '
        'This is where each one is answered in full.')
DETAIL_P = '      <p>%s</p>\n' % LEDE

src = io.open(PAGE, encoding='utf-8').read()
words = lambda h: Counter(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r'<[^>]+>', ' ', h)))
main0 = re.search(r'<main.*?</main>', src, re.S).group(0)

if 'covers__groups' in src:
    print('markup already applied -- skipping to CSS')
else:
    # ---- 1. lift the lede out of #detail ----
    assert src.count(DETAIL_P) == 1, 'the #detail paragraph is not in the expected shape'
    out = src.replace(DETAIL_P, '', 1)

    # ---- 2. split the covers list by href ----
    m = re.search(r'(<section class="tp-split section" id="covers">.*?</section>)', out, re.S)
    assert m, 'no tp-split #covers band'
    band = m.group(1)
    items = re.findall(r'<li><a href="([^"]+)">(.*?)</a></li>', band, re.S)
    assert len(items) == 13, 'expected 13 items, found %d' % len(items)
    svc = [i for i in items if 'locations.html' not in i[0]]
    mkt = [i for i in items if 'locations.html' in i[0]]
    assert len(svc) == 7 and len(mkt) == 6, 'unexpected split %d/%d' % (len(svc), len(mkt))

    li = lambda L: ''.join('\n            <li><a href="%s">%s</a></li>' % (h, n) for h, n in L)
    groups = (
      '<div class="covers__groups">\n'
      '        <div>\n          <p class="covers__gh">Services</p>\n'
      '          <ul class="sv-list covers__one">%s\n          </ul>\n        </div>\n'
      '        <div>\n          <p class="covers__gh">Markets</p>\n'
      '          <ul class="sv-list covers__one">%s\n          </ul>\n        </div>\n'
      '      </div>' % (li(svc), li(mkt)))

    old_ul = re.search(r'<ul class="sv-list">.*?</ul>', band, re.S)
    assert old_ul, 'no sv-list in the band'
    new_band = band.replace(old_ul.group(0), groups, 1)

    # ---- 3. put the lede in the copy block ----
    old_copy = ('      <h2>Services and markets on this site</h2>\n'
                '    </div>')
    assert new_band.count(old_copy) == 1, 'copy block not in the expected shape'
    new_band = new_band.replace(old_copy,
        '      <h2>Services and markets on this site</h2>\n'
        '      <p class="lede">%s</p>\n    </div>' % LEDE, 1)

    out = out.replace(band, new_band, 1)

    # ---- guards ----
    main1 = re.search(r'<main.*?</main>', out, re.S).group(0)
    # The ONLY permitted difference is the two group headings N-A introduces. Nothing may
    # go missing, and nothing else may appear -- the lede must MOVE, not be re-typed.
    missing = words(main0) - words(main1)
    added   = words(main1) - words(main0)
    assert not missing, 'WORDS LOST: %s' % dict(list(missing.items())[:8])
    assert added == Counter({'Services': 1, 'Markets': 1}), \
        'unexpected new words (only the two group headings are allowed): %s' % dict(added)
    assert out.count(LEDE) == 1, 'the sentence was duplicated rather than moved (%d)' % out.count(LEDE)
    hrefs_before = re.findall(r'href="([^"]+)"', band)
    hrefs_after  = re.findall(r'href="([^"]+)"', new_band)
    assert hrefs_before == hrefs_after, 'link order or set changed'
    assert out.count('<h1') == 1 and out.count('<section') == src.count('<section')
    assert out.count('</section>') == src.count('</section>')
    t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
    assert '>' not in t, 'stray ">" introduced'
    io.open(PAGE, 'w', encoding='utf-8').write(out)
    print('markup applied: 13 links -> 7 services + 6 markets, lede moved out of #detail')

# ---- 4. CSS ----
css = io.open(CSS, encoding='utf-8').read()
prev = re.search(r'\n*/\* =+\n   \[CR\].*?(?=\n\n/\* =|\Z)', css, re.S)
had = bool(prev)
if prev: css = css[:prev.start()] + css[prev.end():]

BLOCK = '''

/* ==========================================================================
   [CR] NEW-BUSINESS "SERVICES AND MARKETS" BAND (owner picked N-A + T-3)
   --------------------------------------------------------------------------
   ONE band on ONE page, and it is the odd one out by construction: the other
   seven #covers bands carry 4-5 plain scope items, this one carries 13 LINKS
   and is really a navigation index sitting in the [CL] .tp-split shell.

   Measured before: 1016px tall -- nearly double every sibling -- with the 13
   links in a single 713px column and the heading breaking 268px / 417px.

   TWO LABELLED COLUMNS, because the split is true rather than decorative: the
   13 are 7 services (services.html#*) and 6 markets (locations.html#*), which
   the generator asserts by href rather than by reading the labels.

   THE 42px HEADING IS NOT A STYLE PREFERENCE, IT IS ARITHMETIC. "Services and
   markets on this site" needs 694px on one line at 44px and the copy column is
   669px, so it missed by 25px and broke to a short orphan first line. 42px
   clears it at 663px.

   DESKTOP-ONLY, DELIBERATELY. [CL] collapses .tp-split to a single column at
   <=1000px, where the heading is already responsive and the columns already
   stack. An unscoped 42px leaked into that layout and forced the phone heading
   to three lines, so everything here sits above the breakpoint and the mobile
   band is byte-for-byte what it was.
   ========================================================================== */
.covers__groups {
  display: grid;
  grid-template-columns: 1fr;
  row-gap: 22px;
}
.covers__gh {
  margin: 0 0 10px;
  font-size: 11.5px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: .14em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--ds-ink-on-dark, #fff) 50%, transparent);
}
/* .sv-list runs its own auto-fit grid; inside a group it must be one column --
   the same override [CN] makes for .tp-split__list, for the same reason. */
.covers__groups .sv-list.covers__one {
  grid-template-columns: 1fr;
  margin-top: 0;
}
@media (min-width: 1001px) {
  .covers__groups {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    column-gap: 36px;
    row-gap: 0;
  }
  #covers.tp-split .tp-split__copy h2 { font-size: 42px; }
  #covers.tp-split .tp-split__copy .lede { margin-top: 14px; max-width: 58ch; }
}
'''
out = css.rstrip('\n') + BLOCK
assert out.count('[CR]') == 1
io.open(CSS, 'w', encoding='utf-8').write(out)
print('[CR] %s (%d bytes)' % ('regenerated' if had else 'appended', len(BLOCK)))
