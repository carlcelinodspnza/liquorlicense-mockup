#!/usr/bin/env python3
"""
Owner picked H-A + C-A (2026-09-03) for the 8 service pages.

  H-A  hero  -> the existing site-wide `hero--photo` pattern (media + scrim + hero__inner)
  C-A  #covers -> the existing `.tp-split` pattern from [CL] (copy / list / full-height media)

Neither introduces a new component. The ONLY new CSS is block [CN], which stops `.sv-list`
from running its own auto-fit grid once it sits inside a `.tp-split__list` column.

IDEMPOTENT: re-running is a no-op. FAILS CLOSED: every page is transformed in memory and
must pass all guards before ANY file is written.

Imagery: every assignment below was verified by LOOKING at the file (a contact sheet), not by
grepping alt text -- three of this library's alts are demonstrably wrong (see ALT_FIX).
"""
import re, io, os, sys, struct
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))

def jpeg_dims(path):
    d = io.open(path, 'rb').read(); i = 2
    while i < len(d) - 9:
        if d[i] != 0xFF: i += 1; continue
        mk = d[i+1]
        if mk in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack('>HH', d[i+5:i+9]); return w, h
        if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7: i += 2; continue
        i += 2 + struct.unpack('>H', d[i+2:i+4])[0]
    raise SystemExit('cannot read dimensions: ' + path)

# --- imagery, verified visually -------------------------------------------------
# hero image per service, then the covers-band image. A value of None for covers
# means "the page already owns one -- reuse it, do not assign".
HERO = {
 'service-buy.html':          'hero-inventory.jpg',
 'service-sell.html':         'hero-bar-room.jpg',
 'service-transfer.html':     'hero-process.jpg',
 'service-valuation.html':    'valuation-appraisal.jpg',
 'service-compliance.html':   'hero-faq.jpg',
 'service-cup.html':          'hero-locations.jpg',
 'service-escrow.html':       'hero-contact.jpg',
 'service-new-business.html': 'hero-services.jpg',
}
COVERS = {
 'service-buy.html':          'hero-licence-types.jpg',
 'service-sell.html':         'hero-about.jpg',
 'service-transfer.html':     'hero-resources.jpg',
 'service-valuation.html':    'hero-banner.jpg',
 'service-new-business.html': 'ind-franchise.jpg',
 'service-compliance.html':   None,   # keeps compliance-gavel.jpg
 'service-cup.html':          None,   # keeps zoning-blueprints.jpg
 'service-escrow.html':       None,   # keeps escrow-signing.jpg
}

ALT = {
 'hero-inventory.jpg':      'Rows of amber and clear spirit bottles on tiered wooden back-bar shelving lit by concealed warm strip lights above an empty bar counter',
 'hero-bar-room.jpg':       'A bar room set for service',
 'hero-process.jpg':        'An empty panelled boardroom with a long polished table and leather chairs',
 'valuation-appraisal.jpg': 'An appraiser making notes beside glasses of white wine',
 'hero-faq.jpg':            'Two empty tufted leather club chairs facing each other across a small round table',
 'hero-locations.jpg':      'A city skyline at night seen from above, its streets lit amber to the horizon',
 'hero-contact.jpg':        'A tufted brown leather chair drawn up to a polished wood desk, with a lit table lamp',
 'hero-services.jpg':       'Panelled dark walnut cabinetry with slim brass pulls, lit from above',
 'hero-licence-types.jpg':  'Five stemmed glasses in a row on a dark wooden bar counter',
 'hero-about.jpg':          'A brass wall sconce lighting dark wood panelling above a leather armchair',
 'hero-resources.jpg':      'A long library aisle of tall dark wood shelves packed with uniform gold-lettered volumes',
 'hero-banner.jpg':         'A rocks glass of spirits on a dark polished table under low light',
 'ind-franchise.jpg':       'A warm restaurant interior with booth seating and pendant lighting',
}
# alts this library gets WRONG elsewhere; we write the true one on the instances we create.
ALT_FIX = {'hero-process.jpg', 'hero-locations.jpg', 'hero-licence-types.jpg', 'ind-franchise.jpg'}

HERO_OPEN = 'section hero hero--editorial section--dark wow-bloom'

def words(html):
    t = re.sub(r'<[^>]+>', ' ', html)
    for a, b in (('&mdash;','—'),('&rsaquo;','›'),('&amp;','&'),('&nbsp;',' '),
                 ('&rsquo;','’'),('&ldquo;','“'),('&rdquo;','”')):
        t = t.replace(a, b)
    return Counter(re.findall(r"[A-Za-z0-9’'-]+", t))

def section_span(hay, start):
    """end offset of the <section> that opens at `start`, by depth counting.

    The pattern MUST consume the trailing '>'. A bare `<(/?)section\b` matches
    `</section` only, so the span ends one character short and the orphaned '>'
    is left behind as visible text -- which is exactly what shipped in ab74bde.
    """
    depth = 0
    for t in re.finditer(r'<(/?)section\b[^>]*>', hay[start:]):
        depth += 1 if not t.group(1) else -1
        if depth == 0:
            return start + t.end()
    raise SystemExit('unbalanced <section> at offset %d' % start)

def img_tag(fn, *, hero):
    assert fn in ALT, 'no verified alt for ' + fn
    p = os.path.join(ROOT, 'assets', fn)
    assert os.path.exists(p), 'missing asset: ' + fn
    w, h = jpeg_dims(p)
    load = 'fetchpriority="high"' if hero else 'loading="lazy"'
    return ('<img src="assets/%s" alt="%s" width="%d" height="%d" %s decoding="async">'
            % (fn, ALT[fn], w, h, load))

def build_hero(body, fn):
    """editorial hero -> hero--photo. Returns None if already converted."""
    if 'hero--photo' in body:
        return None
    m = re.match(r'<section class="' + re.escape(HERO_OPEN) + r'"([^>]*)>', body)
    assert m, 'hero open tag not in the expected shape'
    rest = body[m.end():]
    cm = re.search(r'<div class="container">', rest)
    assert cm, 'no .container in hero'
    cend = rest.rindex('</div>')                      # closes .container
    inner = rest[cm.end():cend].strip()
    assert '<h1' in inner, 'hero has no h1'
    tail = rest[cend:]
    return ('<section class="%s hero--photo"%s>\n'
            '  <div class="hero__media">%s</div>\n'
            '  <div class="hero__scrim"></div>\n'
            '  <div class="container">\n'
            '    <div class="hero__inner">\n      %s\n    </div>\n  %s'
            % (HERO_OPEN, m.group(1), img_tag(fn, hero=True), inner, tail))

def build_covers(body, fn):
    """#covers -> .tp-split. Returns None if already converted."""
    if 'tp-split' in body:
        return None
    m = re.match(r'<section class="section" id="covers">', body)
    assert m, 'covers open tag not in the expected shape'
    eb = re.search(r'<p class="eyebrow">.*?</p>', body, re.S); assert eb, 'no eyebrow'
    h2 = re.search(r'<h2[^>]*>.*?</h2>',        body, re.S); assert h2, 'no h2'
    ul = re.search(r'<ul class="sv-list">.*?</ul>', body, re.S); assert ul, 'no sv-list'
    note = re.search(r'<p class="sv-note">.*?</p>', body, re.S); assert note, 'no sv-note'

    existing = re.search(r'<div class="sv-media[^"]*">\s*(<img[^>]*>)\s*</div>', body)
    if fn is None:
        assert existing, 'page was expected to already own a covers image'
        media = existing.group(1)
    else:
        assert not existing, 'page already owns an image but a new one was assigned'
        media = img_tag(fn, hero=False)

    return ('<section class="tp-split section" id="covers">\n'
            '  <div class="container">\n'
            '    <div class="tp-split__copy">\n      %s\n      %s\n    </div>\n'
            '    <div class="tp-split__list">\n      %s\n      %s\n    </div>\n'
            '    <figure class="tp-split__media">%s</figure>\n'
            '  </div>\n</section>' % (eb.group(0), h2.group(0), ul.group(0), note.group(0), media))

# ---------------------------------------------------------------- run
staged, changed, skipped = {}, [], []
for page in sorted(HERO):
    path = os.path.join(ROOT, page)
    src = io.open(path, encoding='utf-8').read()
    mm = re.search(r'<main.*?</main>', src, re.S); assert mm, page + ': no <main>'
    main0 = mm.group(0)
    main = main0
    touched = False

    # repair the ab74bde off-by-one: a '>' orphaned after a rebuilt </section>
    if '</section>>' in main:
        main = main.replace('</section>>', '</section>')
        touched = True

    hm = re.search(r'<section class="' + re.escape(HERO_OPEN) + r'"', main)
    if hm:
        end = section_span(main, hm.start())
        new = build_hero(main[hm.start():end], HERO[page])
        if new: main = main[:hm.start()] + new + main[end:]; touched = True
    else:
        assert 'hero--photo' in main, page + ': hero neither editorial nor already photo'

    cm = re.search(r'<section class="section" id="covers">', main)
    if cm:
        end = section_span(main, cm.start())
        new = build_covers(main[cm.start():end], COVERS[page])
        if new: main = main[:cm.start()] + new + main[end:]; touched = True
    else:
        assert 'tp-split' in main, page + ': covers band missing and not already converted'
        # already converted -- reconcile the media image against the mapping
        want = COVERS[page]
        if want:
            cs = re.search(r'<section class="tp-split section" id="covers">', main)
            assert cs, page + ': converted covers band not found'
            ce = section_span(main, cs.start())
            band = main[cs.start():ce]
            fm = re.search(r'(<figure class="tp-split__media">)(<img[^>]*>)(</figure>)', band)
            assert fm, page + ': no media figure in the converted band'
            cur = re.search(r'src="assets/([^"]+)"', fm.group(2)).group(1)
            if cur != want:
                band = band[:fm.start()] + fm.group(1) + img_tag(want, hero=False) + fm.group(3) + band[fm.end():]
                main = main[:cs.start()] + band + main[ce:]
                touched = True

    if not touched:
        skipped.append(page); continue

    # ---- guards, all must hold before anything is written ----
    w0, w1 = words(main0), words(main)
    assert w0 == w1, '%s: WORD LOSS  missing=%s  extra=%s' % (
        page, dict(list((w0 - w1).items())[:8]), dict(list((w1 - w0).items())[:8]))
    imgs = re.findall(r'<img[^>]*src="assets/([^"]+)"', main)
    assert len(imgs) == len(set(imgs)), '%s: DUPLICATE image within page: %s' % (
        page, [k for k, v in Counter(imgs).items() if v > 1])
    n0 = len(re.findall(r'<img[^>]*src="assets/([^"]+)"', main0))
    added = (0 if 'hero--photo' in main0 else 1) + (0 if 'tp-split' in main0 else (1 if COVERS[page] else 0))
    assert len(imgs) == n0 + added, '%s: image count %d != %d+%d' % (page, len(imgs), n0, added)
    assert main.count('<h1') == 1, page + ': h1 count != 1'
    assert main.count('<section') == main.count('</section>'), page + ': section imbalance'
    _t = re.sub(r'<(script|style)\b.*?</\1>', '', main, flags=re.S | re.I)
    _t = re.sub(r'<!--.*?-->', '', _t, flags=re.S)
    _t = re.sub(r'<[^<>]*>', '', _t)
    assert '>' not in _t, '%s: stray ">" left in text near %r' % (
        page, _t[max(0, _t.find('>') - 60):_t.find('>') + 20])
    assert 'hero--photo' in main and 'tp-split' in main, page + ': transform incomplete'
    # only the COVERS band must be free of sv-media; new-business legitimately keeps one
    # in its #detail band, which this generator does not touch.
    _c = re.search(r'<section class="tp-split section" id="covers">', main)
    assert _c, page + ': covers band not in tp-split form'
    assert 'sv-media' not in main[_c.start():section_span(main, _c.start())], \
        page + ': stale sv-media left inside the covers band'
    for t in re.findall(r'<img[^>]*>', main):
        assert 'alt="' in t, page + ': img without alt'
    staged[path] = src.replace(main0, main, 1)
    changed.append(page)

for path, out in staged.items():
    io.open(path, 'w', encoding='utf-8').write(out)

print('converted : %d  -> %s' % (len(changed), ', '.join(p.replace('service-','').replace('.html','') for p in changed) or '(none)'))
print('already ok: %d  (idempotent no-op)' % len(skipped))
print('alts corrected on the instances written: %s' % ', '.join(sorted(ALT_FIX)))
