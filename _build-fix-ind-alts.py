#!/usr/bin/env python3
"""
Correct the alt text (and the wrong intrinsic sizes) on ind-convenience.jpg and
ind-grocery.jpg.

BOTH WERE OPENED AND LOOKED AT, not read from their alt:

  ind-convenience.jpg (900x562) is a photograph of a BRANDED 7-Eleven storefront
  shot from the street at night, with JAPANESE window signage. The site called it
  "A convenience store chiller stocked with beer and wine" on 20 of its 22
  instances -- wrong three times over: it is an exterior, not a chiller; no beer or
  wine is visible; and nothing in frame is a chiller.

  ind-grocery.jpg (900x600) is a supermarket DRINKS aisle under Norwegian signage
  ("DRIKKE", "Gjor det billig!") with kroner pricing. The site called it "A
  neighbourhood market aisle with a packaged beer and wine set" on 10 of its 12
  instances -- it is a large supermarket rather than a neighbourhood market, and
  what is stocked is chilled beer, soft drinks and bottled water, not wine.

The new alts describe what is actually in frame and name no brand.

SIZES: only the .tp-split__media instances were wrong (1024x576 and 512x512 for
files that are 900x562 and 900x600). The .category-card and .ind-media instances
already declared the truth and are corrected on alt only. That matters because
.ind-media renders with object-fit:fill and height:auto, so its intrinsic ratio
DOES drive layout there -- measured 558x348 from a 900x562 declaration. The
.tp-split__media instances are width/height:100% + object-fit:cover, where the
attributes never drive layout.

SEPARATE ISSUE, NOT FIXED HERE: ind-convenience.jpg shows a real company's trade
dress and Japanese signage, on 22 pages of a California mockup. That is an image
choice for the owner, not an alt fix.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, glob, struct
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
FIX = {
 'ind-convenience.jpg': 'A brightly lit convenience store on a street corner at night',
 'ind-grocery.jpg':     'A supermarket drinks aisle lined with chilled beer and bottled soft drinks',
}

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

TRUE = {f: dims(os.path.join(ROOT, 'assets', f)) for f in FIX}
assert TRUE['ind-convenience.jpg'] == (900, 562) and TRUE['ind-grocery.jpg'] == (900, 600), \
    'asset sizes changed: %r' % TRUE

def set_attr(tag, name, value):
    if re.search(r'\b%s="[^"]*"' % name, tag):
        return re.sub(r'\b%s="[^"]*"' % name, '%s="%s"' % (name, value), tag, count=1)
    return tag[:-1].rstrip() + ' %s="%s">' % (name, value)

staged, alts_fixed, dims_fixed, pages = {}, 0, 0, set()
for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
    base = os.path.basename(p)
    if base.startswith('_'): continue
    src = io.open(p, encoding='utf-8').read()
    out = src
    for tag in set(re.findall(r'<img[^>]*>', src)):
        f = next((k for k in FIX if k in tag), None)
        if not f: continue
        w, h = TRUE[f]
        new = tag
        cur = re.search(r'alt="([^"]*)"', tag)
        if not cur or cur.group(1) != FIX[f]:
            new = set_attr(new, 'alt', FIX[f]); alts_fixed += out.count(tag)
        if not (('width="%d"' % w) in new and ('height="%d"' % h) in new):
            new = set_attr(new, 'width', w); new = set_attr(new, 'height', h)
            dims_fixed += out.count(tag)
        if new != tag:
            out = out.replace(tag, new); pages.add(base)
    if out != src:
        # nothing outside the <img> tags may change
        assert re.sub(r'<img[^>]*>', '', out) == re.sub(r'<img[^>]*>', '', src), base + ': collateral edit'
        assert out.count('<img') == src.count('<img'), base + ': img count changed'
        staged[p] = out

for p, o in staged.items():
    io.open(p, 'w', encoding='utf-8').write(o)

print('alt corrections : %d tag instance(s)' % alts_fixed)
print('size corrections: %d tag instance(s)' % dims_fixed)
print('pages touched   : %d' % len(pages))
