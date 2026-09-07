#!/usr/bin/env python3
"""
Replace the 13 market pills in #where with three STATE cards, on the buy and sell
pages only.

SCOPE IS DELIBERATE AND NARROW. 25 pages carry this .mkt-list band; the owner asked
for buy and sell only. The other 23 keep their pills, and the build asserts that --
a scope slip here would silently restyle a quarter of the site.

THE LINKS ARE RELATIVE, NOT THE URLS AS GIVEN. The owner supplied
http://127.0.0.1:8792/... targets, which are their local preview server. Hardcoding
those would break every card on the deployed site. The relative hrefs resolve to
exactly the same three pages locally AND live.

WHAT THE REPLACEMENT COSTS, enumerated before deleting:
  inbound anchors ... none. #where is linked from 0 pages.
  link targets ...... the band drops 13 links to California market pages. TEN of
                      them remain linked from these pages via the header mega menu
                      and the footer. THREE do not -- napa-valley, palm-springs and
                      san-jose, the three markets with no classification pages, which
                      is why neither the menu nor the footer carries them. They stay
                      reachable from 32 other pages each, so nothing is orphaned
                      site-wide, but they lose their only route from buy and sell.
                      Reported, not hidden.
  JS / integration .. none.
  layout ............ the band keeps section--dark, so the ground rhythm is
                      unchanged; verified after.

SUBLINES ARE THE MENU'S OWN NUMBERS, not new claims: California 52 counties and 172
cities, Florida 66 counties, Arizona 15 counties -- the same figures the Locations
rail carries, which were themselves read off each state page. Nothing is invented.

Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

TARGETS = ['service-buy.html', 'service-sell.html']

CARDS = [
    ('CA', 'California', 'california-liquor-license-services.html',
     '52 counties &middot; 172 cities'),
    ('FL', 'Florida', 'florida-liquor-license.html', '66 counties'),
    ('AZ', 'Arizona', 'arizona-liquor-license.html', '15 counties'),
]


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


cards_html = '\n'.join(
    '      <li><a class="statecard" href="%s">'
    '<span class="statecard__mark" aria-hidden="true">%s</span>'
    '<span class="statecard__name">%s</span>'
    '<span class="statecard__sub">%s</span>'
    '<span class="statecard__go" aria-hidden="true">&rarr;</span></a></li>'
    % (href, mark, name, sub) for mark, name, href, sub in CARDS)
NEW_LIST = '<ul class="statecards" role="list">\n%s\n    </ul>' % cards_html

staged, dropped = {}, {}

for page in TARGETS:
    src = io.open(page, encoding='utf-8').read()
    if 'statecards' in src:
        continue
    orig = src

    m = re.search(r'<ul class="mkt-list">.*?</ul>', src, re.S)
    assert m, '%s: no .mkt-list found' % page
    old_list = m.group(0)
    old_links = re.findall(r'href="([^"]+)"', old_list)
    assert len(old_links) == 13, '%s: expected 13 pills, found %d' % (page, len(old_links))

    new = src[:m.start()] + NEW_LIST + src[m.end():]

    # ---- guards ------------------------------------------------------------
    for _, _, href, _ in CARDS:
        assert os.path.exists(href), 'missing target %s' % href
        assert 'href="%s"' % href in new, '%s: card link %s not rendered' % (page, href)
    assert not re.search(r'127\.0\.0\.1|localhost', new), \
        '%s: an absolute local URL leaked in -- links must be relative' % page

    ow, nw = words(orig), words(new)
    added, removed = nw - ow, ow - nw
    assert added == words(NEW_LIST), \
        '%s: unexpected words added\n  extra=%s' % (page, added - words(NEW_LIST))
    assert removed == words(old_list) - words(NEW_LIST) or True, 'noop'
    # every pill label must be gone, and only pill labels may be gone
    assert removed == (words(old_list) - words(NEW_LIST)), \
        '%s: removed words are not exactly the pill labels\n  %s' % (page, removed)

    assert new.count('mkt-list') == 0, '%s: pill list survived' % page
    assert new.count('statecards') == 1, '%s: card list not exactly once' % page
    assert new.count('statecard__name') == 3, '%s: expected 3 cards' % page
    assert 'section--dark' in re.search(r'<section[^>]*id="where"', new).group(0) or \
        'where--split' in new, '%s: band ground changed' % page
    assert len(re.findall(r'<h1\b', new)) == len(re.findall(r'<h1\b', orig)), '%s: h1' % page
    assert not stray_gt(new), '%s: stray ">"' % page
    for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p'):
        o = len(re.findall(r'<%s\b' % tag, new)); c = len(re.findall(r'</%s>' % tag, new))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (page, tag, o, c)

    rest = new
    dropped[page] = [l for l in old_links if l not in rest]
    staged[page] = new

if not staged:
    print('no-op: both pages already carry the state cards')
    sys.exit(0)

# SCOPE CONTAINMENT: capture the other 23 pages before writing, prove them untouched after.
others = {f: io.open(f, encoding='utf-8').read()
          for f in os.listdir('.')
          if f.endswith('.html') and not f.startswith('_') and f not in TARGETS
          and 'mkt-list' in io.open(f, encoding='utf-8').read()}

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

for f, before in others.items():
    assert io.open(f, encoding='utf-8').read() == before, '%s changed but is out of scope' % f

print('replaced the market pills with three state cards on %d pages' % len(staged))
for f in staged:
    print('   %-22s 13 pills -> 3 cards (California, Florida, Arizona)' % f)
    print('   %-22s market links now unreachable FROM THIS PAGE: %s'
          % ('', ', '.join(x.replace('liquor-license-', '').replace('.html', '')
                           for x in dropped[f]) or 'none'))
print('   %d other pages carrying .mkt-list verified byte-identical' % len(others))
print('   all card hrefs are RELATIVE (no 127.0.0.1), asserted')
