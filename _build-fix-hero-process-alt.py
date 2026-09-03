#!/usr/bin/env python3
"""
hero-process.jpg is described wrongly across the site.

VERIFIED by opening the file: it is an empty panelled boardroom with a long polished
table and leather chairs, 2496x1664. The site calls it "paperwork and a pen on a
broker's desk" and declares it as 1024x576 or 512x512 -- three different wrong facts.

Fixes BOTH on every instance that still carries a wrong value:
  * alt  -> the true description (screen-reader users are currently misinformed)
  * w/h  -> the true intrinsic size

Layout safety: every wrong instance sits in `.tp-split__media`, whose CSS is
`width:100%; height:100%; object-fit:cover` -- the box is sized by the grid row, so
the attributes do not drive layout at desktop. Below 1000px the [CL] rule sets an
explicit `aspect-ratio:16/9`, which also overrides the intrinsic ratio. Measured
before/after to confirm rather than relying on that reasoning.

IDEMPOTENT. FAILS CLOSED. Leaves already-correct instances untouched.
"""
import re, io, os, glob, struct
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
FILE = 'hero-process.jpg'
TRUE_ALT = 'An empty panelled boardroom with a long polished table and leather chairs'

def jpeg_dims(path):
    d = io.open(path, 'rb').read(); i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF: i += 1; continue
        mk = d[i+1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack('>HH', d[i+5:i+9]); return w, h
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7: i += 2; continue
        i += 2 + struct.unpack('>H', d[i+2:i+4])[0]
    raise SystemExit('cannot read ' + path)

W, H = jpeg_dims(os.path.join(ROOT, 'assets', FILE))
assert (W, H) == (2496, 1664), 'asset changed: got %dx%d' % (W, H)

# an alt is acceptable if it names the room, not paperwork
def alt_is_true(a):
    a = a.lower()
    return ('boardroom' in a) and ('paperwork' not in a)

def set_attr(tag, name, value):
    if re.search(r'\b%s="[^"]*"' % name, tag):
        return re.sub(r'\b%s="[^"]*"' % name, '%s="%s"' % (name, value), tag, count=1)
    return tag[:-1].rstrip() + ' %s="%s">' % (name, value)

staged, fixed_tags, pages_touched, kept = {}, 0, [], 0
for page in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
    base = os.path.basename(page)
    if base.startswith('_'): continue
    src = io.open(page, encoding='utf-8').read()
    out, n = src, 0
    for tag in set(re.findall(r'<img[^>]*>', src)):
        if FILE not in tag: continue
        alt = re.search(r'alt="([^"]*)"', tag)
        cur = alt.group(1) if alt else ''
        w = re.search(r'width="([^"]*)"', tag)
        h = re.search(r'height="([^"]*)"', tag)
        ok_alt = alt_is_true(cur)
        ok_dim = (w and w.group(1) == str(W)) and (h and h.group(1) == str(H))
        if ok_alt and ok_dim:
            kept += src.count(tag); continue
        new = tag
        if not ok_alt: new = set_attr(new, 'alt', TRUE_ALT)
        if not ok_dim:
            new = set_attr(new, 'width', W); new = set_attr(new, 'height', H)
        assert new != tag
        c = out.count(tag); assert c > 0
        out = out.replace(tag, new); n += c
    if n:
        # guards
        assert out.count('<img') == src.count('<img'), base + ': img count changed'
        assert len(out) != len(src) or out == src
        for t in re.findall(r'<img[^>]*>', out):
            if FILE in t:
                a = re.search(r'alt="([^"]*)"', t)
                assert a and alt_is_true(a.group(1)), base + ': alt not repaired'
                assert 'width="%d"' % W in t and 'height="%d"' % H in t, base + ': dims not repaired'
        # nothing outside the <img> tags may change
        assert re.sub(r'<img[^>]*>', '', out) == re.sub(r'<img[^>]*>', '', src), base + ': collateral edit'
        staged[page] = out; fixed_tags += n; pages_touched.append(base)

for p, o in staged.items():
    io.open(p, 'w', encoding='utf-8').write(o)

print('tags fixed        : %d across %d page(s)' % (fixed_tags, len(pages_touched)))
print('already correct   : %d tag(s) left untouched' % kept)
print('true dims applied : %dx%d' % (W, H))
