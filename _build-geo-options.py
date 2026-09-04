#!/usr/bin/env python3
"""
Layout options for the #markets "Counties and cities" band on the STATE pages
(arizona-liquor-license.html, florida-liquor-license.html).

THE BUG, MEASURED ON THE LIVE PAGE (1440 viewport, 1200px container):
  eyebrow   y=0     x=24    w=633
  cards     y=78    x=722   w=429      (Counties 15, then Cities 10 stacked)
  h2        y=585   x=24    w=633      <- BELOW the cards
  => 698px of empty left column, and the heading reads LAST.

IT IS A SCOPING BUG, NOT A DESIGN CHOICE. Block [MRAIL] makes
"#markets > .container" a two-column grid (1.32fr / 1fr) with explicit placement --
.eyebrow to column 1 row 1, h2 to column 1 row 2 -- and that was written for
locations.html's master/detail rail. The two state pages reuse the same #markets id
for a different band whose .loc-geo child has NO placement, so it auto-flows into
column 2, spans the height of 25 list items, and pushes the h2 down to row 2 of a
now-585px-tall row. locations.html itself is unaffected and is not touched by any of
these options.

Every option therefore has to do two things: place the heading before the cards, and
use the left column. They differ in how.

Rendered inside a copy of the real page so the heights are live-accurate -- a
standalone mock has mispredicted this build every time.

Writes _geo-layouts.html, which is gitignored.
"""
import re, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
# Both state pages carry this band, and they stress it very differently: Arizona has
# 15 counties, Florida 66. Pass a page to build the preview against it.
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'arizona-liquor-license.html'
OUT = '_geo-layouts-%s.html' % PAGE.split('-')[0]

src = io.open(PAGE, encoding='utf-8').read()
i = src.find('id="markets"')
assert i > 0, 'no #markets'
i = src.rfind('<section', 0, i)
# DEPTH-MATCH THE SECTION TOO. #markets contains nested <section class="loc-geo__col">
# elements, so a plain find('</section>') closes on the first INNER one and truncates
# the band before its lists -- which is exactly how the extraction below came back empty.
_d, j = 1, src.find('>', i) + 1
while _d and j < len(src):
    _nx = re.search(r'<(/?)section\b[^>]*>', src[j:])
    if not _nx:
        break
    _d += -1 if _nx.group(1) else 1
    j += _nx.end()
BAND = src[i:j]
assert BAND.count('loc-geo__list') >= 1, 'band truncated: %d lists' % BAND.count('loc-geo__list')

EYEBROW = re.search(r'<p class="eyebrow">(.*?)</p>', BAND, re.S).group(1)
H2 = re.search(r'<h2[^>]*>(.*?)</h2>', BAND, re.S).group(1)
# DEPTH-MATCH, don't regex. .loc-geo wraps two <section class="loc-geo__col">
# elements, each with its own nested markup, so a lazy .*?</div> stops at the first
# close tag it meets and returns a fragment.
_g = BAND.find('<div class="loc-geo"')
assert _g > 0, 'no .loc-geo in the band'
_depth, _k = 1, BAND.find('>', _g) + 1
while _depth and _k < len(BAND):
    _nx = re.search(r'<(/?)div\b[^>]*>', BAND[_k:])
    if not _nx:
        break
    _depth += -1 if _nx.group(1) else 1
    _k += _nx.end()
GEO = BAND[_g:_k]
assert GEO.count('loc-geo__list') >= 1, 'expected at least one list, got %d' % GEO.count('loc-geo__list')
assert GEO.rstrip().endswith('</div>'), 'loc-geo extraction is not well-formed'

# a short lede, built ONLY from counts already on the page -- nothing invented
counts = re.findall(r'<h4>([A-Za-z]+)\s*<span class="loc-geo__n">(\d+)</span>', GEO)
assert counts, 'no counts found'
# counts comes back as [('Counties','15'), ('Cities','10')] -- number SECOND.
LEDE = ('We publish %s. Tell us the market and the classification and we source '
        'against it.' % ' and '.join('%s %s' % (num, name.lower())
                                     for name, num in counts))
assert re.match(r'We publish \d+ [a-z]+', LEDE), 'lede reads wrong: %r' % LEDE

OPTIONS = [
    ('G-A', 'Heading block left, cards right',
     'Keeps the two-column shape but places the heading properly: eyebrow, heading and a '
     'one-line lede fill the left column, the cards sit in the right. Nothing else moves.',
     '<div class="geo geo--split">'
     '<div class="geo__head"><p class="eyebrow">%s</p><h2>%s</h2>'
     '<p class="lede lede--prose">%s</p></div>'
     '<div class="geo__body">%s</div></div>' % (EYEBROW, H2, LEDE, GEO)),

    ('G-B', 'Full-width heading, cards two-up beneath',
     'The heading spans the band, then Counties and Cities sit side by side across the full '
     'width. Shortest of the four, and the closest to how the other bands on this page read.',
     '<div class="geo geo--stack"><p class="eyebrow">%s</p><h2>%s</h2>'
     '<p class="lede lede--prose">%s</p>%s</div>' % (EYEBROW, H2, LEDE, GEO)),

    ('G-C', 'Full-width heading, one wide card',
     'Heading spans, then the counties and the cities run as columns inside a single card '
     'rather than two. Fewest boxes, and the list reads as one set.',
     '<div class="geo geo--wide"><p class="eyebrow">%s</p><h2>%s</h2>'
     '<p class="lede lede--prose">%s</p>%s</div>' % (EYEBROW, H2, LEDE, GEO)),

    ('G-D', 'Heading left, cards right, sticky heading',
     'Same split as G-A, but the heading block stays put while a long county list scrolls '
     'past it. Built for Florida, where the list is 66 items rather than 15.',
     '<div class="geo geo--split geo--sticky">'
     '<div class="geo__head"><p class="eyebrow">%s</p><h2>%s</h2>'
     '<p class="lede lede--prose">%s</p></div>'
     '<div class="geo__body">%s</div></div>' % (EYEBROW, H2, LEDE, GEO)),
]

CSS = """
<style>
/* preview chrome only */
.optlabel{position:sticky;top:0;z-index:40;background:#e6994e;color:#231a14;
  font:600 13px/1.4 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;
  padding:8px 16px;display:flex;gap:14px;align-items:baseline;}
.optlabel .note{text-transform:none;letter-spacing:0;font-weight:400;opacity:.85;}
.optwrap{position:relative;}

/* NEUTRALISE the [MRAIL] grid for these option bands only. That block pins
   #markets > .container children to fixed grid cells, which is the bug. */
.optwrap #markets > .container{display:block !important;}
.optwrap #markets > .container > *{grid-column:auto !important;grid-row:auto !important;}

.geo .loc-geo{margin-bottom:0;}

/* G-A / G-D: heading left, cards right */
@media (min-width:1001px){
  .geo--split{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);
    gap:clamp(28px,4vw,64px);align-items:start;}
  .geo--sticky .geo__head{position:sticky;top:24px;}
}
.geo__head h2{margin-top:6px;}
.geo__head .lede--prose{max-width:none;}

/* G-B: full-width heading, cards two-up */
.geo--stack .loc-geo{grid-template-columns:repeat(auto-fit,minmax(320px,1fr));
  margin-top:var(--ds-space-lg,24px);}
.geo--stack .lede--prose{max-width:70ch;}

/* G-C: one wide card, lists as columns inside it */
.geo--wide .loc-geo{display:block;margin-top:var(--ds-space-lg,24px);
  background:var(--ds-bg-surface-2);border:1px solid var(--ds-hairline);
  border-radius:var(--ds-r-lg,10px);box-shadow:var(--ds-shadow-card);
  padding:var(--ds-space-md) var(--ds-space-lg);}
.geo--wide .loc-geo__col{background:none;border:0;box-shadow:none;padding:0;}
.geo--wide .loc-geo__col + .loc-geo__col{margin-top:var(--ds-space-lg,24px);
  padding-top:var(--ds-space-md);border-top:1px solid var(--ds-hairline);}
@media (min-width:700px){
  .geo--wide .loc-geo__list{columns:3;column-gap:var(--ds-space-lg,24px);}
  .geo--wide .loc-geo__list li{break-inside:avoid;}
}
@media (min-width:1200px){ .geo--wide .loc-geo__list{columns:4;} }
.geo--wide .lede--prose{max-width:70ch;}
</style>
"""

JS = """
<script>
addEventListener('load', function(){
  document.querySelectorAll('.optwrap').forEach(function(w){
    var sec=w.querySelector('section#markets');
    var c=sec.querySelector('.container');
    var cr=c.getBoundingClientRect();
    var h2=w.querySelector('h2'), lists=w.querySelectorAll('.loc-geo__list');
    var nodes=[].slice.call(c.querySelectorAll('p,h2,h4,ul'))
      .filter(function(e){var r=e.getBoundingClientRect();return r.width>0&&r.height>0;});
    var maxR=Math.max.apply(null,nodes.map(function(e){return e.getBoundingClientRect().right;}));
    var b=document.createElement('div');
    b.className='optlabel';
    b.style.background='#231a14'; b.style.color='#e6994e'; b.style.position='static';
    b.textContent='measured: '+Math.round(sec.getBoundingClientRect().height)+'px tall  |  '
      +'heading before cards: '+(h2.getBoundingClientRect().top<lists[0].getBoundingClientRect().top)
      +'  |  unused right gutter: '+Math.round(cr.right-maxR)+'px';
    w.appendChild(b);
  });
});
</script>
"""

blocks = []
grounds = ['section', 'section section--warm', 'section', 'section section--warm']
for (code, title, note, body), g in zip(OPTIONS, grounds):
    blocks.append(
        '<div class="optwrap">'
        '<div class="optlabel"><b>%s</b> <span>%s</span> <span class="note">%s</span></div>'
        '<section class="%s" id="markets"><div class="container">%s</div></section>'
        '</div>' % (code, title, note, g, body))

a, b = src.find('<main'), src.find('</main>')
head_end = src.find('</head>')
main_open = src[a:src.find('>', a) + 1]
out = (src[:head_end] + CSS + src[head_end:a] + main_open + '\n' + '\n'.join(blocks) + '\n'
       + src[b:].replace('</body>', JS + '</body>', 1))

for code, _, _, _ in OPTIONS:
    assert '<b>%s</b>' % code in out, 'missing %s' % code
assert out.count('<main') == 1, 'main duplicated'
# COUNT THE MARKUP, NOT THE STRING. The preview's own stylesheet mentions
# .loc-geo__list three times, so a bare substring count never matches.
_want = len(OPTIONS) * GEO.count('<ul class="loc-geo__list"')
_got = out.count('<ul class="loc-geo__list"')
assert _got == _want, 'lists lost: %d rendered, %d expected' % (_got, _want)
_items = out.count('<li><span class="loc-geo__name">')
assert _items == len(OPTIONS) * GEO.count('<li><span class="loc-geo__name">'), \
    'list items lost: %d' % _items

io.open(OUT, 'w', encoding='utf-8').write(out)
print('wrote %s with %d options: %s' % (OUT, len(OPTIONS), ', '.join(o[0] for o in OPTIONS)))
print('  lede built from the page\'s own counts: %r' % LEDE)
print('  source band: %s #markets (%d counties + cities lists)'
      % (PAGE, GEO.count('loc-geo__list')))
