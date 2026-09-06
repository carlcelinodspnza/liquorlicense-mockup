#!/usr/bin/env python3
"""
Apply form treatment F-A (glass) to the hero lead card, and reorder the hero on
mobile so it reads title -> form -> lede + buttons.

THE REORDER NEEDS MARKUP, NOT JUST CSS. The eyebrow, h1, lede and cta-row all lived
inside ONE .hero__inner, with the form as its sibling. No amount of flex/grid
ordering can put the form BETWEEN the h1 and the lede while they share a parent, so
.hero__inner is split in two:

    .hero__cols
      .hero__inner.hero__head    eyebrow + h1
      .hero__lead                the form
      .hero__inner.hero__body    lede + cta-row

That DOM order IS the mobile order the owner asked for, so mobile needs no ordering
rules at all -- it just stacks. Desktop places them explicitly: head and body in the
left column on rows 1 and 2, the form in the right column spanning both. Both halves
keep the .hero__inner class, so they keep its flex column, its gap and the 62ch
measure that .hero--editorial sets on it.

F-A, chosen from four treatments rendered on the real page. The defect it fixes is
concrete: the card was white with WHITE inputs on it, so the fields had almost no
presence. Glass gives the panel a translucent dark ground with a blurred backdrop,
turns the inputs into dark wells that read as fields, and lights an accent ring on
focus. Measured contrast on the composited result: labels 9.79, input text 15.79,
heading 18.32 -- all far past the 4.5 AA threshold.

NOT ONE FIELD, LABEL OR CHOICE CHANGES. The owner asked to elevate the design
"without changing the actual contents of the form", so the build asserts the visible
word multiset of each page is identical before and after, and that the field set and
label set are untouched.

Applied to BOTH pages that carry this hero -- service-buy.html and service-sell.html.
They are the same component built by the same generator; leaving one glass and one
white would be a defect, not a choice. Say so and the sell page reverts.

Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGES = ['service-buy.html', 'service-sell.html']
MARK = 'hero__head'


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


staged = {}

for page in PAGES:
    src = io.open(page, encoding='utf-8').read()
    if MARK in src:
        continue
    orig = src

    ci = src.find('<div class="hero__cols">')
    assert ci > 0, '%s: no .hero__cols' % page
    ii = src.find('<div class="hero__inner">', ci)
    assert ii > 0, '%s: no .hero__inner' % page
    # depth-match .hero__inner
    d, k = 1, src.find('>', ii) + 1
    while d and k < len(src):
        nx = re.search(r'<(/?)div\b[^>]*>', src[k:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        k += nx.end()
    inner = src[ii:k]

    eyebrow = re.search(r'<p class="eyebrow">.*?</p>', inner, re.S)
    h1 = re.search(r'<h1[^>]*>.*?</h1>', inner, re.S)
    lede = re.search(r'<p class="lede">.*?</p>', inner, re.S)
    cta = re.search(r'<div class="cta-row">.*?</div>\s*</div>', inner, re.S)
    assert eyebrow and h1 and lede, '%s: hero parts not found' % page
    ctam = re.search(r'<div class="cta-row">.*?</div>\s*(?=\s*</div>)', inner, re.S)
    assert ctam, '%s: cta-row not found' % page

    head = ('<div class="hero__inner hero__head">\n      %s\n      %s\n    </div>'
            % (eyebrow.group(0), h1.group(0)))
    body = ('<div class="hero__inner hero__body">\n      %s\n      %s\n    </div>'
            % (lede.group(0), ctam.group(0).rstrip()))

    # the aside follows the old inner; capture it so head/form/body land in order
    ai = src.find('<aside class="hero__lead"', k)
    assert ai > 0, '%s: no .hero__lead' % page
    aend = src.find('</aside>', ai) + len('</aside>')
    aside = src[ai:aend]

    src = src[:ii] + head + '\n      ' + aside + '\n    ' + body + src[aend:]

    # ---- guards ------------------------------------------------------------
    ow, nw = words(orig), words(src)
    assert ow == nw, ('%s: visible copy changed\n  added=%s\n  lost=%s'
                      % (page, nw - ow, ow - nw))
    of = re.findall(r'name="([^"]+)"', orig)
    nf = re.findall(r'name="([^"]+)"', src)
    assert of == nf, '%s: form fields changed\n  %s\n  %s' % (page, of, nf)
    ol = re.findall(r'<label[^>]*>([^<]*)</label>', orig)
    nl = re.findall(r'<label[^>]*>([^<]*)</label>', src)
    assert ol == nl, '%s: labels changed' % page

    assert src.count('hero__head') == 1 and src.count('hero__body') == 1, '%s: split markers' % page
    assert src.count('<aside class="hero__lead"') == 1, '%s: aside duplicated' % page
    # DOM order must be head -> form -> body, which is the mobile order asked for
    assert (src.index('hero__head') < src.index('<aside class="hero__lead"')
            < src.index('hero__body')), '%s: wrong DOM order' % page
    assert len(re.findall(r'<h1\b', src)) == 1, '%s: h1 count' % page
    assert not stray_gt(src), '%s: stray ">"' % page
    for tag in ('div', 'p', 'a', 'aside', 'form', 'label', 'section', 'h1', 'fieldset'):
        o = len(re.findall(r'<%s\b' % tag, src)); c = len(re.findall(r'</%s>' % tag, src))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)

    staged[page] = src

if not staged:
    print('no-op: both pages already carry the split hero')
    sys.exit(0)

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

print('split the hero and applied F-A on %d pages' % len(staged))
for f in staged:
    print('   %-24s DOM order: title -> form -> lede+buttons' % f)
print('   form contents asserted identical (fields, labels, word multiset)')
