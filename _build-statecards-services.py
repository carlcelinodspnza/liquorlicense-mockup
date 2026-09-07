#!/usr/bin/env python3
"""
Put the three state cards into the #where band on the SIX remaining Services pages.

The owner asked to apply the buy/sell treatment to "other pages from the Services
tab where applicable". Applicable was counted, not guessed:

  8 pages sit under the Services tab. TWO already have the cards (buy, sell).
  SIX carry the old 13-pill .mkt-list inside a #where band -- compliance, cup,
  escrow, new-business, transfer, valuation -- and get the cards here.
  ONE, services.html, has NO #where band at all and is therefore left alone.

  17 further pages carry .mkt-list (four guides, eight industries, and others).
  They are NOT under the Services tab, so they keep their pills, and this build
  asserts all 17 are byte-identical afterwards.

PHOTOGRAPHS ARE ASSIGNED PER PAGE, NOT GLOBALLY, because the default trio
collides with imagery two of these pages already carry:

  service-cup.html       already uses hero-locations.jpg  -> California needs another
  service-transfer.html  already uses hero-process.jpg
                         and hero-resources.jpg           -> Florida and Arizona do

Reusing them would repeat an image inside one page. Each page therefore takes the
default where it is free and the next unused ALTERNATE where it is not. Every
alternate is 3:2 like the defaults, appears on none of these pages, and was checked
by opening the file rather than by trusting its name:

  hero-services.jpg   dark wood cabinetry under a warm spot
  hero-faq.jpg        two leather armchairs under a brass lamp
  hero-contact.jpg    a leather chair at a desk, brass lamp

As on buy and sell these are TEXTURE, NOT DEPICTION -- there is no Florida or
Arizona photograph in the library -- so alt is empty and the wrapper aria-hidden.

Fail-closed and idempotent.
"""
import re, io, os, sys, html, struct, glob
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

TARGETS = ['service-compliance.html', 'service-cup.html', 'service-escrow.html',
           'service-new-business.html', 'service-transfer.html', 'service-valuation.html']

STATES = [
    ('CA', 'California', 'california-liquor-license-services.html', '52 counties &middot; 172 cities',
     'assets/hero-locations.jpg'),
    ('FL', 'Florida', 'florida-liquor-license.html', '66 counties',
     'assets/hero-process.jpg'),
    ('AZ', 'Arizona', 'arizona-liquor-license.html', '15 counties',
     'assets/hero-resources.jpg'),
]
ALTERNATES = ['assets/hero-services.jpg', 'assets/hero-faq.jpg', 'assets/hero-contact.jpg']


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


def jpeg_size(p):
    d = io.open(p, 'rb').read()
    i = 2
    while i < len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack('>HH', d[i + 5:i + 9])
            return w, h
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
            i += 2
            continue
        i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]
    raise AssertionError('no SOF in %s' % p)


def main_of(doc):
    m = re.search(r'<main\b.*?</main>', doc, re.S)
    return m.group(0) if m else doc


# every photograph, default or alternate, must exist and be 3:2 like the others
SIZES = {}
for p in [s[4] for s in STATES] + ALTERNATES:
    assert os.path.exists(p), 'missing %s' % p
    w, h = jpeg_size(p)
    assert abs(w / h - 1.5) < 0.02, '%s is %dx%d (%.3f), not 3:2 like the rest' % (p, w, h, w / h)
    SIZES[p] = (w, h)

staged, assigned, dropped = {}, {}, {}

for page in TARGETS:
    src = io.open(page, encoding='utf-8').read()
    if 'statecards' in src:
        continue
    orig = src
    body = main_of(src)

    # ---- per-page photo assignment ------------------------------------------
    used = set(re.findall(r'assets/[A-Za-z0-9._-]+\.(?:jpg|jpeg|png)', body))
    pool = [a for a in ALTERNATES if a not in used]
    picks, swaps = [], []
    for mark, name, href, sub, default in STATES:
        if default not in used:
            photo = default
        else:
            assert pool, '%s: no free alternate left for %s' % (page, name)
            photo = pool.pop(0)
            swaps.append('%s %s -> %s' % (name, default.split('/')[-1], photo.split('/')[-1]))
        used.add(photo)
        picks.append((mark, name, href, sub, photo))
    assert len({p for *_, p in picks}) == 3, '%s: two cards share a photograph' % page
    assigned[page] = swaps

    cards = '\n'.join(
        '      <li><a class="statecard" href="%s">'
        '<span class="statecard__ph" aria-hidden="true">'
        '<img src="%s" alt="" width="%d" height="%d" loading="lazy" decoding="async"></span>'
        '<span class="statecard__mark" aria-hidden="true">%s</span>'
        '<span class="statecard__name">%s</span>'
        '<span class="statecard__sub">%s</span>'
        '<span class="statecard__go" aria-hidden="true">&rarr;</span></a></li>'
        % (href, photo, SIZES[photo][0], SIZES[photo][1], mark, name, sub)
        for mark, name, href, sub, photo in picks)
    NEW_LIST = '<ul class="statecards" role="list">\n%s\n    </ul>' % cards

    m = re.search(r'<ul class="mkt-list">.*?</ul>', src, re.S)
    assert m, '%s: no .mkt-list found' % page
    old_list = m.group(0)
    old_links = re.findall(r'href="([^"]+)"', old_list)
    assert len(old_links) == 13, '%s: expected 13 pills, found %d' % (page, len(old_links))
    new = src[:m.start()] + NEW_LIST + src[m.end():]

    # ---- guards --------------------------------------------------------------
    for _, _, href, _, _ in picks:
        assert os.path.exists(href), 'missing target %s' % href
        assert 'href="%s"' % href in new, '%s: card link %s not rendered' % (page, href)
    assert not re.search(r'127\.0\.0\.1|localhost', new), '%s: absolute local URL' % page

    ow, nw = words(orig), words(new)
    assert (nw - ow) == words(NEW_LIST), \
        '%s: unexpected words added: %s' % (page, (nw - ow) - words(NEW_LIST))
    assert (ow - nw) == (words(old_list) - words(NEW_LIST)), \
        '%s: removed words are not exactly the pill labels: %s' % (page, ow - nw)

    assert 'mkt-list' not in new, '%s: pill list survived' % page
    assert new.count('statecards') == 1 and new.count('class="statecard"') == 3, '%s: card count' % page
    assert new.count('statecard__ph') == 3, '%s: photo wrappers' % page
    assert len(re.findall(r'<h1\b', new)) == len(re.findall(r'<h1\b', orig)), '%s: h1' % page
    assert not stray_gt(new), '%s: stray ">"' % page
    for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p', 'figure'):
        o = len(re.findall(r'<%s\b' % tag, new)); c = len(re.findall(r'</%s>' % tag, new))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)

    # no image may be repeated inside <main>, and none may be NEWLY repeated
    def dupes(doc):
        return {s for s, n in Counter(
            re.findall(r'<img[^>]+src="(assets/[^"]+)"', main_of(doc))).items() if n > 1}
    introduced = sorted(dupes(new) - dupes(orig))
    assert not introduced, '%s: this change repeats an image inside <main>: %s' % (page, introduced)

    dropped[page] = [l for l in old_links if l not in new]
    staged[page] = new

if not staged:
    print('no-op: all six pages already carry the state cards')
    sys.exit(0)

# SCOPE: the 17 non-Services pages with .mkt-list must not move
others = {}
for f in sorted(glob.glob('*.html')):
    if f.startswith('_') or f in TARGETS:
        continue
    t = io.open(f, encoding='utf-8').read()
    if 'mkt-list' in t:
        others[f] = t

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

for f, before in others.items():
    assert io.open(f, encoding='utf-8').read() == before, '%s changed but is out of scope' % f

print('state cards applied to %d Services pages' % len(staged))
for f in sorted(staged):
    print('   %-28s 13 pills -> 3 cards%s' % (f, '' if not assigned[f] else '   photo swaps: ' + '; '.join(assigned[f])))
    if dropped[f]:
        print('   %-28s market links unreachable FROM THIS PAGE: %s'
              % ('', ', '.join(x.replace('liquor-license-', '').replace('.html', '') for x in dropped[f])))
print('   %d other pages carrying .mkt-list verified byte-identical' % len(others))
print('   services.html has no #where band and was not touched')
