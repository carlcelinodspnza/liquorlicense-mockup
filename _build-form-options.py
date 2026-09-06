#!/usr/bin/env python3
"""
Visual treatments for the buy page's hero lead form.

THE BRIEF: elevate it WITHOUT changing what the form contains. Every option below
carries the identical field set, in the identical order, with identical labels and
identical radio choices -- asserted, not assumed. What changes is surface, depth,
input treatment, focus behaviour and rhythm.

WHAT IS ACTUALLY DULL, measured on the live page (1440):
  card      460 x 642, plain white, 10px radius, 77% of the hero's height
  inputs    44px tall, WHITE on a WHITE card, 1px #cfccca border, 6px radius
  layout    8 rows in one column, no pairing, no grouping
  focus     border-colour change only
The fields have almost no presence because they are white on white, and the panel
reads as a form pasted onto the photo rather than belonging to it.

  F-A  Glass on the photo   translucent dark panel, blurred backdrop, light labels,
                            inputs as dark wells, accent focus ring
  F-B  Refined light        stays white but inputs get a tinted well so they read as
                            fields, an accent rule at the top, a real focus ring
  F-C  Dark, underlined     dark card, no input boxes at all -- a bottom rule per
                            field that lights up on focus
  F-D  Paired rows          F-B's surface, but short fields share rows and the radio
                            sets go inline. ARRANGEMENT, not content: same fields,
                            same order, fewer rows.

Rendered as four real copies of the actual hero in a copy of the real page, so the
photo, the scrim and the inherited type are all the live ones.

Writes _form-layouts.html, which is gitignored.
"""
import re, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGE = 'service-buy.html'
OUT = '_form-layouts.html'

src = io.open(PAGE, encoding='utf-8').read()

# depth-matched hero section
i = src.find('<section class="section hero')
assert i > 0, 'no hero'
d, j = 1, src.find('>', i) + 1
while d and j < len(src):
    nx = re.search(r'<(/?)section\b[^>]*>', src[j:])
    if not nx:
        break
    d += -1 if nx.group(1) else 1
    j += nx.end()
HERO = src[i:j]
assert 'buy-lead' in HERO, 'hero does not contain the lead form'

FIELDS = re.findall(r'name="([^"]+)"', HERO)
LABELS = re.findall(r'<label[^>]*>([^<]+)</label>', HERO)

OPTIONS = [
    ('F-A', 'Glass on the photo',
     'A translucent dark panel with a blurred backdrop, so the form sits IN the hero instead of '
     'on top of it. Inputs become dark wells that actually read as fields, focus lights an accent '
     'ring.'),
    ('F-B', 'Refined light card',
     'Stays a white card, but the inputs get a tinted well so they stop being white-on-white, an '
     'accent rule runs along the top, and focus draws a real ring rather than recolouring a border.'),
    ('F-C', 'Dark card, underlined fields',
     'No input boxes at all &mdash; each field is a bottom rule that lights up on focus. The most '
     'editorial of the four and the least form-like.'),
    ('F-D', 'Paired rows',
     'F-B&rsquo;s surface with the rhythm fixed: short fields share a row and the radio sets run '
     'inline. Same fields, same order &mdash; fewer rows.'),
]

CSS = """
<style>
.optlabel{position:sticky;top:0;z-index:40;background:#e6994e;color:#231a14;
  font:600 13px/1.4 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;
  padding:8px 16px;display:flex;gap:14px;align-items:baseline;}
.optlabel .note{text-transform:none;letter-spacing:0;font-weight:400;opacity:.85;}
.optbadge{background:#231a14;color:#e6994e;font:600 12px/1 ui-monospace,monospace;
  padding:8px 16px;}

/* ---------- F-A glass ---------- */
.fx-a .cta-formcard{
  background:rgba(28,20,16,.62);
  -webkit-backdrop-filter:blur(18px) saturate(1.2);
  backdrop-filter:blur(18px) saturate(1.2);
  border:1px solid rgba(255,255,255,.14);
  box-shadow:0 24px 60px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10);
}
.fx-a .hero__leadh{color:#fff;}
.fx-a .form label,.fx-a .form legend{color:rgba(255,255,255,.72);}
.fx-a .form input:not([type=radio]),.fx-a .form textarea{
  background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.16);color:#fff;}
.fx-a .form input::placeholder{color:rgba(255,255,255,.4);}
.fx-a .form input:not([type=radio]):focus{
  border-color:var(--ds-accent);box-shadow:0 0 0 3px rgba(230,156,78,.25);outline:none;}
.fx-a .form .choice span{color:rgba(255,255,255,.86);}

/* ---------- F-B refined light ---------- */
.fx-b .cta-formcard{position:relative;overflow:hidden;
  box-shadow:0 18px 44px rgba(10,4,4,.42);}
.fx-b .cta-formcard::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;
  background:linear-gradient(90deg,var(--ds-accent),#ad1e1e);}
.fx-b .form input:not([type=radio]),.fx-b .form textarea{
  background:#f4f1ee;border:1px solid #e0dbd6;}
.fx-b .form input:not([type=radio]):focus{
  background:#fff;border-color:var(--ds-accent);
  box-shadow:0 0 0 3px rgba(230,156,78,.2);outline:none;}
.fx-b .form label,.fx-b .form legend{font-weight:600;letter-spacing:.01em;}

/* ---------- F-C dark, underlined ---------- */
.fx-c .cta-formcard{background:#1c1410;border:1px solid rgba(255,255,255,.10);
  box-shadow:0 20px 50px rgba(0,0,0,.5);}
.fx-c .hero__leadh{color:#fff;}
.fx-c .form label,.fx-c .form legend{color:rgba(255,255,255,.6);font-size:12px;
  letter-spacing:.08em;text-transform:uppercase;}
.fx-c .form input:not([type=radio]){
  background:transparent;border:0;border-bottom:1px solid rgba(255,255,255,.22);
  border-radius:0;padding-left:0;padding-right:0;color:#fff;}
.fx-c .form input:not([type=radio]):focus{
  border-bottom-color:var(--ds-accent);box-shadow:0 1px 0 0 var(--ds-accent);outline:none;}
.fx-c .form .choice span{color:rgba(255,255,255,.86);}

/* ---------- F-D paired rows (F-B surface) ---------- */
.fx-d .cta-formcard{position:relative;overflow:hidden;box-shadow:0 18px 44px rgba(10,4,4,.42);}
.fx-d .cta-formcard::before{content:"";position:absolute;inset:0 0 auto 0;height:3px;
  background:linear-gradient(90deg,var(--ds-accent),#ad1e1e);}
.fx-d .form input:not([type=radio]){background:#f4f1ee;border:1px solid #e0dbd6;}
.fx-d .form input:not([type=radio]):focus{background:#fff;border-color:var(--ds-accent);
  box-shadow:0 0 0 3px rgba(230,156,78,.2);outline:none;}
.fx-d .form{display:grid;grid-template-columns:1fr 1fr;gap:0 14px;}
.fx-d .form > *{grid-column:1/-1;}
.fx-d .form .field:nth-of-type(2),
.fx-d .form .field:nth-of-type(3){grid-column:span 1;}
.fx-d .form .field--choice{grid-column:span 1;}
.fx-d .form .field:nth-last-of-type(2),
.fx-d .form .field:nth-last-of-type(1){grid-column:span 1;}
.fx-d .form .choice-row{gap:8px 12px;}
</style>
"""

JS = """
<script>
addEventListener('load', function(){
  document.querySelectorAll('.optwrap').forEach(function(w){
    var card=w.querySelector('.cta-formcard');
    var hero=w.querySelector('.hero');
    var ins=w.querySelectorAll('.form input:not([type=radio])');
    var b=document.createElement('div');
    b.className='optbadge';
    b.textContent='card '+Math.round(card.getBoundingClientRect().width)+' x '
      +Math.round(card.getBoundingClientRect().height)+'px  |  hero '
      +Math.round(hero.getBoundingClientRect().height)+'px  |  '
      +ins.length+' text inputs, 2 radio groups  |  input bg '
      +getComputedStyle(ins[0]).backgroundColor;
    w.appendChild(b);
  });
});
</script>
"""

blocks = []
for code, title, note in OPTIONS:
    cls = 'fx-' + code.split('-')[1].lower()
    blocks.append(
        '<div class="optwrap %s">'
        '<div class="optlabel"><b>%s</b> <span>%s</span> <span class="note">%s</span></div>'
        '%s</div>' % (cls, code, title, note, HERO))

a, b = src.find('<main'), src.find('</main>')
head_end = src.find('</head>')
main_open = src[a:src.find('>', a) + 1]
out = (src[:head_end] + CSS + src[head_end:a] + main_open + '\n' + '\n'.join(blocks) + '\n'
       + src[b:].replace('</body>', JS + '</body>', 1))

# ---- guards: the FORM'S CONTENTS must be identical in every option -----------
for code, _, _ in OPTIONS:
    assert '<b>%s</b>' % code in out, 'missing %s' % code
n = len(OPTIONS)
assert re.findall(r'name="([^"]+)"', out).count(FIELDS[0]) >= n, 'fields lost'
for f in set(FIELDS):
    got = len(re.findall(r'name="%s"' % re.escape(f), out))
    want = FIELDS.count(f) * n
    assert got == want, 'field %s appears %d times, expected %d' % (f, got, want)
for lbl in set(LABELS):
    got = len(re.findall(re.escape('>%s</label>' % lbl), out))
    want = LABELS.count(lbl) * n
    assert got == want, 'label %r appears %d times, expected %d' % (lbl, got, want)
assert out.count('id="buy-lead"') == n, 'lead card count'
assert out.count('<main') == 1, 'main duplicated'

io.open(OUT, 'w', encoding='utf-8').write(out)
print('wrote %s with %d options: %s' % (OUT, n, ', '.join(o[0] for o in OPTIONS)))
print('  form contents held identical across all four:')
print('    fields : %s' % ', '.join(FIELDS))
print('    labels : %s' % ' | '.join(LABELS))
