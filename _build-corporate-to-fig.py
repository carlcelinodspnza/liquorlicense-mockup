#!/usr/bin/env python3
"""
Convert the last remaining ca-card (#corporate) into the .ca-fig split layout the
owner pointed at (#qualification): copy left, captioned figure right.

WHY IT ALSO TIDIES UP. #corporate was the third of three ca-cards. Coverage and
Classifications have already moved out to bands of their own, so this card was
alone in a grid built for three -- propped up by a `:has(:only-child)` rule added
when it was the last one standing. Converting it empties .ca-cards entirely, so
that section goes with it.

MATCHES ITS SIBLINGS EXACTLY. #qualification and #consulting are both
`<section class="ca-fig section">` with .ca-fig__copy (eyebrow, h2, prose) beside
a .ca-fig__figure (image + figcaption echoing the eyebrow). This becomes the third.

THREE THINGS CHANGE BEYOND THE LAYOUT, each stated rather than slipped in:
  * h3 -> h2. The other two ca-fig sections use h2; as a full-width section this
    is a section heading, not a card title.
  * the paragraph gains `lede lede--prose`, so it renders 16px like the prose in
    both sibling sections. Left as a plain <p> it would still be 16px but white
    and unconstrained, instead of the soft grey at a 506px measure they use.
  * the image declared 512x512 for a file that is 2496x1664. Corrected.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, struct
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'california-liquor-license-services.html')

def dims(p):
    d = io.open(p, 'rb').read(); i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF: i += 1; continue
        mk = d[i+1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack('>HH', d[i+5:i+9]); return w, h
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7: i += 2; continue
        i += 2 + struct.unpack('>H', d[i+2:i+4])[0]
    raise SystemExit('cannot read ' + p)

src = io.open(PAGE, encoding='utf-8').read()
if 'ca-fig section" id="corporate"' in src:
    print('already converted -- no-op'); raise SystemExit(0)

blk = re.search(r'\n?<section class="section ca-cards">.*?</section>\n?', src, re.S)
assert blk, 'the ca-cards section is not in the expected shape'
b = blk.group(0)
assert b.count('<article class="ca-card"') == 1, 'expected exactly one remaining card, found %d' % b.count('<article class="ca-card"')

eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', b, re.S).group(1).strip()
head    = re.search(r'<h3>(.*?)</h3>', b, re.S).group(1).strip()
body    = re.search(r'<h3>.*?</h3>\s*<p>(.*?)</p>', b, re.S).group(1).strip()
img     = re.search(r'<img[^>]*src="assets/([^"]+)"[^>]*alt="([^"]*)"', b)
assert img, 'no image in the card'
fn, alt = img.group(1), img.group(2)
w, h = dims(os.path.join(ROOT, 'assets', fn))

new = ('\n<section class="ca-fig section" id="corporate">\n'
       '  <div class="container">\n'
       '    <div class="ca-fig__copy">\n'
       '      <p class="eyebrow">%s</p>\n'
       '      <h2>%s</h2>\n'
       '        <p class="lede lede--prose">%s</p>\n'
       '    </div>\n'
       '    <figure class="ca-fig__figure">\n'
       '      <img src="assets/%s" alt="%s" width="%d" height="%d" loading="lazy" decoding="async">\n'
       '      <figcaption>%s</figcaption>\n'
       '    </figure>\n'
       '  </div>\n</section>\n' % (eyebrow, head, body, fn, alt, w, h, eyebrow))

out = src[:blk.start()] + new + src[blk.end():]

# ---------------- guards ----------------
def words(t): return Counter(re.findall(r"[A-Za-z0-9’'-]+", re.sub(r'<[^>]+>', ' ', t)))
m0 = re.search(r'<main.*?</main>', src, re.S).group(0)
m1 = re.search(r'<main.*?</main>', out, re.S).group(0)
missing = words(m0) - words(m1)
added   = words(m1) - words(m0)
assert not missing, 'WORDS LOST: %s' % dict(list(missing.items())[:8])
# the only new words are the figcaption, which repeats the eyebrow (as the siblings do)
assert added == words(eyebrow), 'unexpected new copy: %s' % dict(added)

assert 'ca-cards' not in out, 'the emptied ca-cards section survived'
assert 'ca-card' not in out, 'a ca-card survived'
# count the CLASS, not one exact string: #consulting is "ca-fig section section--dark",
# so an exact-string match saw 2 and refused. The new band stays on the default ground
# (no --dark/--warm) because it sits between two dark sections and the ca-cards it
# replaces did the same -- the alternation is unchanged.
_figs = len(re.findall(r'<section[^>]*class="[^"]*ca-fig[^"]*"', out))
assert _figs == 3, 'expected 3 ca-fig sections, got %d' % _figs
assert out.count('<h1') == 1
# one section is REPLACED by one section, so the count is unchanged -- the wrapper
# .ca-cards goes and the .ca-fig band takes its place at the same level.
assert out.count('<section') == src.count('<section'), 'section count moved'
assert out.count('</section>') == src.count('</section>'), 'section close count moved'
for t in re.findall(r'<img[^>]*>', out):
    assert 'alt="' in t, 'img without alt'
t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
assert '>' not in t, 'stray ">" introduced'

io.open(PAGE, 'w', encoding='utf-8').write(out)
print('#corporate converted to the .ca-fig split layout')
print('  h3 -> h2 | paragraph -> lede lede--prose | image %s 512x512 -> %dx%d' % (fn, w, h))
print('  the emptied .ca-cards section was removed (3 ca-fig sections now)')
