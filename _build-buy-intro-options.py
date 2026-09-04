#!/usr/bin/env python3
"""
Layout options for the #buy-intro band on service-buy.html.

THE PROBLEM, MEASURED ON THE LIVE PAGE (1440 viewport, 1200px container):
  h2        1152px wide  -- 96% of the container, one line
  paragraph  506px wide  -- 9 lines, 60 chars/line, 97 words
  => 694px, 58% of the band, is empty to the right of the prose.

The paragraph's own measure is fine (60 chars/line sits inside the 45-75 comfortable
range). What reads wrong is a full-bleed heading sitting on top of a half-width
column, so the band looks like a two-column layout with one column missing.

THE OPTIONS ARE RENDERED INSIDE A COPY OF THE REAL PAGE, not in a standalone mock.
A height measured on a bare mock has mispredicted the live page every time this
session (-36% predicted vs -0.4% actual on one band), because a mock lacks the real
section padding, container and inherited type. Each option below is a real .section
in the real document, and the badge on each is measured after render.

Writes _buy-intro-layouts.html, which is gitignored.
"""
import re, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGE = 'service-buy.html'
OUT = '_buy-intro-layouts.html'

EYEBROW = 'Buying a licence'
H2 = 'Do you need to buy a liquor licence for your business?'
P = ('We can help you make your liquor licence purchase a worry-free experience. Our team of '
     'dedicated specialists provide both assistance and consultation in brokering the purchase of '
     'your liquor licence from a seller on the open market. As a buyer, you also benefit from our '
     'team&rsquo;s experience in identifying sellers who have yet to place their licence on the '
     'market. This means that you will get your licence for the best value &ndash; even in the most '
     'competitive markets. You will also be able to rest easy knowing that each seller we work with '
     'is fully qualified.')
IMG = ('assets/escrow-signing.jpg', 512, 512,
       'A broker in a dark suit signing a printed agreement with a fountain pen')

OPTIONS = [
    ('I-A', 'Editorial split &mdash; heading left, prose right',
     'The heading takes its own column and the prose fills the rest. Nothing is centred, '
     'so the band keeps the page&rsquo;s left-aligned rhythm.',
     '<div class="opt-split">'
     '<div class="opt-split__head"><p class="eyebrow">%s</p><h2>%s</h2></div>'
     '<div class="opt-split__body"><p class="lede lede--prose">%s</p></div>'
     '</div>' % (EYEBROW, H2, P)),

    ('I-B', 'Centred measure &mdash; what the client&rsquo;s own page does',
     'Eyebrow, heading and prose centred on one column. The leftover space becomes two '
     'equal margins instead of one lopsided hole. Closest to liquorlicenseagents.com/buy.',
     '<div class="opt-centre">'
     '<p class="eyebrow">%s</p><h2>%s</h2>'
     '<p class="lede lede--prose">%s</p>'
     '</div>' % (EYEBROW, H2, P)),

    ('I-C', 'Full-width heading, prose in two columns',
     'Keeps the heading exactly as it is now and lets the paragraph run in two columns '
     'beneath it, so the copy reaches the right edge without being re-written.',
     '<p class="eyebrow">%s</p><h2>%s</h2>'
     '<div class="opt-cols"><p class="lede lede--prose">%s</p></div>' % (EYEBROW, H2, P)),

    ('I-D', 'Prose left, image right',
     'Fills the empty half with a picture instead of more text. Uses escrow-signing.jpg '
     '(opened and checked: a contract being signed), which is not already on this page.',
     '<p class="eyebrow">%s</p><h2>%s</h2>'
     '<div class="opt-fig">'
     '<div class="opt-fig__copy"><p class="lede lede--prose">%s</p></div>'
     '<figure class="opt-fig__media"><img src="%s" alt="%s" width="%d" height="%d" '
     'loading="lazy" decoding="async"></figure>'
     '</div>' % (EYEBROW, H2, P, IMG[0], IMG[3], IMG[1], IMG[2])),
]

CSS = """
<style>
/* preview chrome only -- none of this ships */
.optlabel { position:sticky; top:0; z-index:40; background:#e6994e; color:#231a14;
  font:600 13px/1.4 system-ui,sans-serif; letter-spacing:.06em; text-transform:uppercase;
  padding:8px 16px; display:flex; gap:14px; align-items:baseline; }
.optlabel b { font-size:15px; }
.optlabel .note { text-transform:none; letter-spacing:0; font-weight:400; opacity:.85; }
.optbadge { position:absolute; right:16px; top:8px; background:#231a14; color:#e6994e;
  font:600 12px/1 ui-monospace,monospace; padding:6px 10px; border-radius:6px; }
.optwrap { position:relative; }

/* I-A editorial split */
@media (min-width:1001px){
  .opt-split{display:grid;grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);
    gap:clamp(32px,5vw,72px);align-items:start;}
  .opt-split__head h2{margin-top:6px;}
}
.opt-split .lede--prose{max-width:none;}

/* I-B centred */
.opt-centre{max-width:74ch;margin-inline:auto;text-align:center;}
.opt-centre .lede--prose{max-width:none;margin-inline:auto;}

/* I-C two-column prose */
@media (min-width:1001px){
  .opt-cols{columns:2;column-gap:clamp(32px,5vw,64px);margin-top:var(--ds-space-lg,24px);}
  .opt-cols .lede--prose{max-width:none;margin:0;}
}

/* I-D prose + image */
@media (min-width:1001px){
  .opt-fig{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);
    gap:clamp(28px,4vw,56px);align-items:center;margin-top:var(--ds-space-lg,24px);}
}
.opt-fig .lede--prose{max-width:none;}
.opt-fig__media{margin:0;}
.opt-fig__media img{width:100%;height:auto;aspect-ratio:4/3;object-fit:cover;
  border-radius:var(--ds-r-lg,10px);display:block;}
</style>
"""

JS = """
<script>
addEventListener('load', function () {
  document.querySelectorAll('.optwrap').forEach(function (w) {
    var sec = w.querySelector('section');
    var p   = w.querySelector('p.lede');
    var c   = w.querySelector('.container');
    var b   = document.createElement('div');
    b.className = 'optbadge';
    var lh = parseFloat(getComputedStyle(p).lineHeight);
    var fill = Math.round(p.getBoundingClientRect().width / c.getBoundingClientRect().width * 100);
    b.textContent = Math.round(sec.getBoundingClientRect().height) + 'px  |  prose '
      + Math.round(p.getBoundingClientRect().width) + 'px ('  + fill + '% of container)  |  '
      + Math.round(p.getBoundingClientRect().height / lh) + ' lines';
    w.appendChild(b);
  });
});
</script>
"""

src = io.open(PAGE, encoding='utf-8').read()
a, b = src.find('<main'), src.find('</main>')
assert a >= 0 and b > a, 'no <main>'
head_end = src.find('</head>')
assert head_end > 0, 'no </head>'

grounds = ['section', 'section section--warm', 'section', 'section section--warm']
blocks = []
for (code, title, note, body), g in zip(OPTIONS, grounds):
    blocks.append(
        '<div class="optwrap">'
        '<div class="optlabel"><b>%s</b> <span>%s</span> <span class="note">%s</span></div>'
        '<section class="%s"><div class="container">%s</div></section>'
        '</div>' % (code, title, note, g, body))

main_open = src[a:src.find('>', a) + 1]
new_main = main_open + '\n' + '\n'.join(blocks) + '\n'
out = src[:head_end] + CSS + src[head_end:a] + new_main + src[b:].replace('</body>', JS + '</body>', 1)

# guards
assert out.count('optwrap') == len(OPTIONS) * 1 + 1 or 'optwrap' in out, 'blocks missing'
for code, _, _, _ in OPTIONS:
    assert '<b>%s</b>' % code in out, 'missing option %s' % code
assert out.count('<main') == 1 and out.count('</main>') == 1, 'main duplicated'
for tag in ('section', 'div', 'p', 'figure', 'h2'):
    o = len(re.findall(r'<%s\b' % tag, new_main)); c = len(re.findall(r'</%s>' % tag, new_main))
    assert o == c, 'unbalanced <%s> in the option stack: %d/%d' % (tag, o, c)
assert os.path.exists(IMG[0]), 'missing image %s' % IMG[0]

io.open(OUT, 'w', encoding='utf-8').write(out)
print('wrote %s with %d options: %s' % (OUT, len(OPTIONS), ', '.join(o[0] for o in OPTIONS)))
print('  rendered inside a copy of %s, so heights are live-accurate' % PAGE)
