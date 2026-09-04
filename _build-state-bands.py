#!/usr/bin/env python3
"""
Three fixes to the state pages, all the same underlying problem: a single narrow
column of content with the right half of the band empty.

1. ARIZONA #markets -- pair the two lists side by side.
   G-C put Counties and Cities in one wide card, stacked. Arizona only has 15 and 10
   entries, so at six internal columns the names wrapped ("Apache County" over two
   lines) and the card was taller than it needed to be. Measured on the page:
       stacked, 6 internal columns   588px section
       paired,  3 internal columns   245px card, 0 wrapped names   <- chosen
   Florida is NOT paired: 66 counties beside 10 cities would put the counties back
   into a narrow column, and .loc-geo__list caps at max-height:340px, which is
   exactly how 54 of its 66 counties got hidden before G-C.

2. #classifications on BOTH pages -- copy left, image right.
   47 words (AZ) / 45 words (FL) sitting alone in a 633px column of a 1200px
   container. Neither state page had a single image in <main>.

3. FLORIDA #about-florida -- compact, and illustrated.
   300 words in 6 paragraphs, 1187px tall, 543px of the container unused to the
   right. The prose runs in two text columns beside the image, which is what makes
   it shorter rather than merely wider.

IMAGERY WAS CHOSEN BY OPENING EACH FILE, never by its alt or its name:
  compliance-gavel.jpg    a gavel on law books beside a document and a whisky glass
                          -> Arizona #classifications, which is about what the state
                             REGULATOR issues.
  hero-licence-types.jpg  five glasses in a row on a dark bar
                          -> Florida #classifications, which lists five COP codes.
  hero-bar-room.jpg       a long bar counter, back-bar bottles, warm light
                          -> Florida #about-florida, which is about opening a bar or
                             restaurant.

Fail-closed and idempotent. No copy is added, removed or reworded anywhere: every
change here is structural, and the word multiset is asserted unchanged.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

AZ, FL = 'arizona-liquor-license.html', 'florida-liquor-license.html'
GUARD = 'locations.html'

IMAGES = {
    (AZ, 'classifications'): ('assets/compliance-gavel.jpg', 512, 512,
        'A gavel resting on law books beside a printed document and a glass of whisky'),
    (FL, 'classifications'): ('assets/hero-licence-types.jpg', 2496, 1664,
        'Five brandy glasses lined up along a dark polished bar, each filled to a different level'),
    (FL, 'about-florida'): ('assets/hero-bar-room.jpg', 2496, 1664,
        'A long bar counter under warm pendant light with spirit bottles ranked on the back bar'),
}


def words(x):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', x, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return Counter(html.unescape(t).split())


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


def section_bounds(s, sid):
    i = s.find('id="%s"' % sid)
    if i < 0:
        return None
    i = s.rfind('<section', 0, i)
    d, j = 1, s.find('>', i) + 1
    while d and j < len(s):
        nx = re.search(r'<(/?)section\b[^>]*>', s[j:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        j += nx.end()
    return i, j


def fig(page, sid):
    src_, w, h, alt = IMAGES[(page, sid)]
    assert os.path.exists(src_), 'missing %s' % src_
    return ('<figure class="statefig__media"><img src="%s" alt="%s" width="%d" height="%d" '
            'loading="lazy" decoding="async"></figure>' % (src_, alt, w, h))


def split_band(page, sid, band, prose_cols=False):
    """Wrap a section's eyebrow+h2+prose as copy-left, image-right."""
    open_tag = re.match(r'<section\b[^>]*>', band).group(0)
    inner = band[len(open_tag):]
    inner = inner[:inner.rindex('</section>')]
    ci = inner.find('<div class="container">')
    assert ci >= 0, '%s #%s: no .container' % (page, sid)
    body = inner[ci + len('<div class="container">'):inner.rindex('</div>')]
    cls = 'statefig statefig--cols' if prose_cols else 'statefig'
    new_open = open_tag if 'statefig-host' in open_tag else \
        open_tag.replace('class="', 'class="statefig-host ', 1)
    return (new_open + '\n  <div class="container">\n'
            '    <div class="%s">\n'
            '      <div class="statefig__copy">%s</div>\n'
            '      %s\n'
            '    </div>\n  </div>\n</section>' % (cls, body.strip(), fig(page, sid)))


staged, notes = {}, []

for page in (AZ, FL):
    src = io.open(page, encoding='utf-8').read()
    orig = src
    changed = False

    # ---- 1. Arizona: pair the two market lists -----------------------------
    if page == AZ:
        b = section_bounds(src, 'markets')
        assert b, 'AZ: no #markets'
        band = src[b[0]:b[1]]
        assert 'geo--wide' in band, 'AZ: G-C not applied yet, run _build-geo-wide.py first'
        if 'geo--pair' not in band:
            nb = band.replace('geo geo--wide', 'geo geo--wide geo--pair', 1)
            assert nb != band, 'AZ: could not add geo--pair'
            src = src[:b[0]] + nb + src[b[1]:]
            changed = True

    # ---- 2 & 3. the copy+image bands ---------------------------------------
    for sid, prose_cols in (('classifications', False), ('about-florida', True)):
        if (page, sid) not in IMAGES:
            continue
        b = section_bounds(src, sid)
        assert b, '%s: no #%s' % (page, sid)
        band = src[b[0]:b[1]]
        if 'statefig' in band:
            continue
        nb = split_band(page, sid, band, prose_cols)
        src = src[:b[0]] + nb + src[b[1]:]
        changed = True

    if not changed:
        continue

    # ---- guards ------------------------------------------------------------
    ow, nw = words(orig), words(src)
    assert ow == nw, ('%s: visible copy changed\n  added=%s\n  lost=%s'
                      % (page, nw - ow, ow - nw))
    for tag in ('section', 'div', 'ul', 'li', 'p', 'span', 'figure', 'h2', 'h4'):
        o = len(re.findall(r'<%s\b' % tag, src))
        c = len(re.findall(r'</%s>' % tag, src))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)
    assert len(re.findall(r'<h1\b', src)) == len(re.findall(r'<h1\b', orig)), '%s: h1' % page
    assert not stray_gt(src), '%s: stray ">"' % page
    # SCOPE THE DUPLICATE CHECK TO <main>. Scanning the whole document counted the
    # header and footer logo three times and the mega-menu feature image once --
    # shared chrome, not content duplication -- and failed a page that was fine.
    _a, _b = src.find('<main'), src.find('</main>')
    main_imgs = re.findall(r'<img[^>]*src="(assets/[^"]+)"', src[_a:_b])
    assert len(main_imgs) == len(set(main_imgs)), \
        '%s: an image repeats inside <main>: %s' % (page, main_imgs)
    for i in set(re.findall(r'<img[^>]*src="(assets/[^"]+)"', src)):
        assert os.path.exists(i), '%s: missing %s' % (page, i)
    staged[page] = src

if not staged:
    print('no-op: both state pages already carry these bands')
    sys.exit(0)

guard_before = io.open(GUARD, encoding='utf-8').read()
for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)
assert io.open(GUARD, encoding='utf-8').read() == guard_before, '%s changed' % GUARD

print('updated %d state pages' % len(staged))
for f in staged:
    n = re.findall(r'<img[^>]*src="assets/([^"]+)"', staged[f])
    print('   %-32s images now: %s' % (f, ', '.join(n) or 'none'))
print('   %s verified byte-identical' % GUARD)
print('   copy unchanged on every page (word multiset asserted equal)')
