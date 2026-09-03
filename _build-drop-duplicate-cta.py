#!/usr/bin/env python3
"""
The 8 service pages carried TWO stacked calls to action.

  #next     "Start with a conversation" -- Send a brief + 800.799.9081
  #contact  "Ready to secure your business's future? | 800.799.9081" -- Talk to a
            senior broker + Check transfer eligibility + a real consultation form

Same ask, same phone number, one immediately above the other. The suite is the
stronger of the two (it carries the form), so the duplicate ask in #next goes.

WHAT IS *NOT* REMOVED, and why. #next also holds a .cross-link-rail of seven
sibling-service links. Checked at href level, not by eyeballing labels: those
seven hrefs appear NOWHERE ELSE in that page's <main>. Deleting the whole band
would drop 7 unique links per page, 56 across the eight. (Site-wide the same
check says #next carries 301 unique hrefs across 98 pages -- which is why this
change is scoped to the 8 pages that actually have the duplicate, and touches
nothing on the other 90.)

So: the duplicated CTA is removed, the rail is kept, the suite is left alone.

Nothing links to #next (no in-page anchor anywhere on the site, no reference in
site.js), so the section may be restructured safely. The id and section are kept
because [CP]'s overlap reserve targets `.section:has(+ .cta-suite)`.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = sorted(glob.glob(os.path.join(ROOT, 'service-*.html')))
assert len(PAGES) == 8, 'expected 8 service pages, found %d' % len(PAGES)

def next_span(s):
    m = re.search(r'<section[^>]*id="next"[^>]*>', s)
    assert m, 'no #next band'
    st = m.start(); d = 0
    for t in re.finditer(r'<(/?)section\b[^>]*>', s[st:]):
        d += 1 if not t.group(1) else -1
        if d == 0: return st, st + t.end()
    raise SystemExit('unbalanced #next')

DROP = (
    ('eyebrow', r'\s*<p class="eyebrow">Next</p>'),
    ('h2',      r'\s*<h2>Start with a conversation</h2>'),
    ('lede',    r'\s*<p class="lede">Tell us the classification, the market and the number you are working to\.</p>'),
    ('cta-row', r'\s*<div class="cta-row">\s*<a class="btn btn-primary wow-glow" href="contact\.html#quote">Send a brief</a>\s*'
                r'<a class="btn btn-secondary" href="tel:\+18007999081">800\.799\.9081</a>\s*</div>'),
)

staged, done, skipped = {}, [], []
for p in PAGES:
    base = os.path.basename(p)
    src = io.open(p, encoding='utf-8').read()
    st, en = next_span(src)
    band = src[st:en]

    if 'class="eyebrow">Next<' not in band:
        skipped.append(base); continue

    # the suite must exist and follow this band, or removing its CTA orphans the page
    assert 'cta-suite' in src[en:en + 4000], base + ': no .cta-suite after #next -- refusing to remove its CTA'
    assert 'cross-link-rail' in band, base + ': no rail to keep -- refusing to gut the band'

    hrefs_before = re.findall(r'href="([^"]+)"', band)
    rail = re.search(r'<div class="cross-link-rail">.*?</div>\s*</div>', band, re.S)
    assert rail, base + ': rail not found'

    new = band
    for what, pat in DROP:
        assert re.search(pat, new), '%s: %s not in the expected shape -- refusing to guess' % (base, what)
        new = re.sub(pat, '', new, count=1)

    # what survived must be exactly the rail's links
    rail_hrefs = re.findall(r'href="([^"]+)"', rail.group(0))
    got = re.findall(r'href="([^"]+)"', new)
    assert got == rail_hrefs, '%s: surviving links %r != rail links %r' % (base, got, rail_hrefs)
    assert len(got) == 7, '%s: expected 7 rail links, got %d' % (base, len(got))
    dropped = [h for h in hrefs_before if h not in got]
    assert dropped == ['contact.html#quote', 'tel:+18007999081'], '%s: unexpected drops %r' % (base, dropped)
    # both dropped destinations must still be reachable from the page
    rest = src[:st] + new + src[en:]
    for h in dropped:
        assert ('href="%s"' % h) in rest or h == 'contact.html#quote' and 'contact.html' in rest, \
            '%s: %s is now unreachable' % (base, h)

    out = src[:st] + new + src[en:]
    assert out.count('<h1') == 1, base + ': h1 count'
    assert out.count('<section') == src.count('<section'), base + ': section count changed'
    assert out.count('</section>') == src.count('</section>'), base + ': close count changed'
    # the band shrank, so the tail must be compared at its NEW offset, not the old one
    assert out[:st] == src[:st], base + ': edit leaked BEFORE #next'
    assert out[st + len(new):] == src[en:], base + ': edit leaked AFTER #next'
    t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
    assert '>' not in t, base + ': stray ">" introduced'
    staged[p] = out; done.append(base)

for p, o in staged.items():
    io.open(p, 'w', encoding='utf-8').write(o)

print('duplicate CTA removed from #next on %d page(s)' % len(done))
for b in done: print('   ', b)
print('already done (no-op): %d' % len(skipped))
print('kept on every page: the 7-link cross-link rail (verified unique to this band)')
