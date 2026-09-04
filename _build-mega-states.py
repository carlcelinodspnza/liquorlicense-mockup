#!/usr/bin/env python3
"""
Rebuild the Locations mega-menu rail as THREE STATES: California / Florida / Arizona.

WHY. The rail currently mixes levels: California sits beside San Francisco, Los
Angeles, San Diego, Orange and Ventura -- a state next to five of its own markets.
The owner asked for states in the rail, California kept as is, with Florida and
Arizona mimicking the California sub-mega.

THE 10-MARKET DECISION, AND THE TRAP IT AVOIDS. The obvious nesting -- move the five
RAIL markets under California -- silently drops 25 links. The current
"<market>:type-NN" detail panels are NOT market-specific: all five markets share one
panel per classification which lists ALL TEN markets that publish that type
(verified: 25 panels collapse to 5 distinct). So the menu today reaches all 50
market x type pages and all 10 market pages. Nesting only the five rail markets
would reach 25. This nests ALL TEN markets that carry classification pages, so the
full set survives -- asserted below, not assumed.

FLORIDA AND ARIZONA CANNOT BE MIRRORED LITERALLY. Measured: each has exactly ONE
page. Florida names 66 counties as plain text with zero links and issues 1COP, 2COP,
3PS, 4COP, 6COP; Arizona names 15 counties and issues Series 6, 7, 9, 10, 11, 12.
Neither has a market page or a classification page. So their sub-mega mirrors the
SHAPE and points every row at an anchor that actually exists on the state page --
#markets, #classifications, #stock -- and their detail panels carry the real county
lists and the real classification codes lifted from those pages. No row links to a
page that does not exist.

SUBLABELS INVENT NOTHING. The rail's per-market stock claims ("San Francisco -- 1
live listing") disagree with the market pages themselves, which show nothing live in
all six rows. Rather than propagate a number this repo contradicts, every nested
market row is labelled "Five classifications", which is structurally true for all ten
(10 markets x 5 type pages = the 50 that exist). The mismatch is reported, not copied.

Everything reused from the current menu -- the California counties / cities / markets
panels, the card markup, the fallback -- is lifted VERBATIM rather than retyped.
"""
import re, io, os, sys, glob, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

# MODE decides what the California pane nests beneath its three standing rows.
#   markets         -- one row per market (10). Matches the owner's chosen shape but
#                      measures 870px against a 560px panel: 5 rows clip, and the only
#                      rescue is a scrollbar inside a hover menu.
#   classifications -- one row per classification (5), reusing the EXISTING type panels
#                      verbatim. Each already lists all ten markets, so the same 50
#                      market x type links survive in 8 rows instead of 13.
MODE = sys.argv[1] if len(sys.argv) > 1 else 'markets'
assert MODE in ('markets', 'classifications'), 'MODE must be markets|classifications'

SRC = 'california-liquor-license-services.html'
TYPES = ['20', '21', '41', '47', '48']
TYPE_NAME = {
    '20': 'Type 20 &mdash; Off-Sale Beer &amp; Wine',
    '21': 'Type 21 &mdash; Off-Sale General',
    '41': 'Type 41 &mdash; On-Sale Beer &amp; Wine, Eating Place',
    '47': 'Type 47 &mdash; On-Sale General, Eating Place',
    '48': 'Type 48 &mdash; On-Sale General, Public Premises',
}
STATES = {
    'florida': dict(
        mark='FL', name='Florida', page='florida-liquor-license.html',
        cardt='Florida Liquor Licences',
        cardd='Counties across the state, and what Florida issues',
        codes=['1COP', '2COP', '3PS', '4COP', '6COP'],
        issuer='The Florida Division of Alcoholic Beverages and Tobacco'),
    'arizona': dict(
        mark='AZ', name='Arizona', page='arizona-liquor-license.html',
        cardt='Arizona Liquor Licences',
        cardd='Counties across the state, and what Arizona issues',
        codes=['Series 6', 'Series 7', 'Series 9', 'Series 10', 'Series 11', 'Series 12'],
        issuer='The Arizona Department of Liquor Licenses and Control'),
}


def block_bounds(s):
    """Depth-matched bounds of the outermost <div> containing the cascade."""
    i = s.find('mm-casc')
    assert i > 0, 'no mm-casc'
    i = s.rfind('<div', 0, i)
    depth, j = 1, s.find('>', i) + 1
    while depth and j < len(s):
        nx = re.search(r'<(/?)div\b[^>]*>', s[j:])
        if not nx:
            break
        depth += -1 if nx.group(1) else 1
        j += nx.end()
    return i, j


def grab_detail(s, key):
    i = s.find('data-mmdetail="%s"' % key)
    assert i > 0, 'missing detail %s' % key
    i = s.rfind('<', 0, i)
    depth, j = 1, s.find('>', i) + 1
    while depth and j < len(s):
        nx = re.search(r'<(/?)div\b[^>]*>', s[j:])
        if not nx:
            break
        depth += -1 if nx.group(1) else 1
        j += nx.end()
    return s[i:j]


def counties_of(page):
    s = io.open(page, encoding='utf-8').read()
    i = s.find('id="markets"')
    assert i > 0, '%s: no #markets' % page
    i = s.rfind('<section', 0, i)
    j = s.find('</section>', i)
    out = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', x)).strip()
           for x in re.findall(r'<li[^>]*>(.*?)</li>', s[i:j], re.S)]
    out = [x for x in out if x]
    assert out, '%s: no counties' % page
    return out


src = io.open(SRC, encoding='utf-8').read()
b0, b1 = block_bounds(src)
OLD = src[b0:b1]

# ---- harvest the pieces we reuse verbatim -----------------------------------
ca_card = re.search(r'<a class="mm-casc__card"[^>]*data-mmcard="california".*?</a>', OLD, re.S).group(0)
d_counties = grab_detail(OLD, 'california:counties')
d_cities = grab_detail(OLD, 'california:cities')
d_markets = grab_detail(OLD, 'california:markets')
fallback = re.search(r'<div class="mm-casc__dfall".*?(?=</div>\s*</div>\s*$)', OLD, re.S)
fallback = fallback.group(0) if fallback else ''
ca_note = re.search(r'<p class="mm-casc__note">.*?</p>', OLD, re.S).group(0)

# the ten markets that publish classification pages, named by the markets panel
markets = re.findall(r'<li><a href="(liquor-license-([a-z-]+)\.html)">([^<]+)</a></li>', d_markets)
markets = [(h, slug, name) for h, slug, name in markets
           if os.path.exists('liquor-license-%s-type-20.html' % slug)]
assert len(markets) == 10, 'expected 10 classification markets, got %d' % len(markets)
for _, slug, _ in markets:
    for t in TYPES:
        assert os.path.exists('liquor-license-%s-type-%s.html' % (slug, t)), 'missing %s %s' % (slug, t)

# ---- build ------------------------------------------------------------------
# NOTE: no esc() helper here on purpose. The classification codes carry no '&' of
# their own, and the ' &middot; ' separator is already an entity -- escaping it once
# more rendered the literal text "1COP &middot; 2COP" in the menu.

cards = [ca_card]
for slug, st in STATES.items():
    assert os.path.exists(st['page']), 'missing %s' % st['page']
    cards.append(
        '<a class="mm-casc__card" role="menuitem" data-mmcard="%s" href="%s" hidden>'
        '<span class="mm-casc__cardmark" aria-hidden="true">%s</span>'
        '<span class="mm-casc__cardt">%s</span>'
        '<span class="mm-casc__cardd">%s</span>'
        '<span class="mm-casc__cardgo" aria-hidden="true">&rarr;</span></a>'
        % (slug, st['page'], st['mark'], st['cardt'], st['cardd']))

rail = ['<div class="mm-casc__rail" role="tablist" aria-label="Where we broker">']
railspec = [('california', 'California', '52 counties &middot; 172 cities', 'california:markets', True)]
for slug, st in STATES.items():
    n = len(counties_of(st['page']))
    railspec.append((slug, st['name'], '%d counties' % n, '%s:counties' % slug, False))
for slug, name, sub, dflt, sel in railspec:
    rail.append(
        '<button class="mm-casc__state" type="button" role="tab" id="mmstate-%s" data-mmstate="%s" '
        'data-mmdefault="%s" aria-controls="mmst-%s" aria-selected="%s" tabindex="%s">'
        '<span class="mm-casc__name">%s</span><span class="mm-casc__sub">%s</span>'
        '<svg class="mm-casc__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M9 6l6 6-6 6"/></svg></button>'
        % (slug, slug, dflt, slug, 'true' if sel else 'false', '0' if sel else '-1', name, sub))
rail.append('</div>')

def row(href, opt, mark, t, sub):
    return ('<a class="mm-casc__row" role="menuitem" href="%s" data-mmopt="%s">'
            '<span class="mm-casc__mark">%s</span><span class="mm-casc__txt">'
            '<span class="t">%s</span><span class="s">%s</span></span></a>' % (href, opt, mark, t, sub))

panes = ['<div class="mm-casc__panes">']
ca_rows = [
    row('california-liquor-license-services.html', 'california:counties', 'CA',
        'Counties we broker in', '52 counties published'),
    row('california-liquor-license-services.html', 'california:cities', 'CA',
        'Cities we broker in', '172 cities published'),
    row('locations.html#state-california', 'california:markets', '&rarr;',
        'All 14 California markets', 'Statewide plus thirteen named markets'),
]
if MODE == 'markets':
    for href, slug, name in markets:
        ca_rows.append(row(href, 'california:%s' % slug, '&rarr;', name, 'Five classifications'))
else:
    for t in TYPES:
        ca_rows.append(row('licence-type-%s.html' % t, 'california:type-%s' % t, t,
                           re.sub(r' &mdash;.*', '', TYPE_NAME[t]),
                           TYPE_NAME[t].split('&mdash; ')[1]))
panes.append('<div class="mm-casc__pane" id="mmst-california" data-mmpane="california" '
             'role="tabpanel" aria-labelledby="mmstate-california">%s%s</div>'
             % (''.join(ca_rows), ca_note))
for slug, st in STATES.items():
    rows = [
        row('%s#markets' % st['page'], '%s:counties' % slug, st['mark'],
            'Counties we broker in', '%d counties published' % len(counties_of(st['page']))),
        row('%s#classifications' % st['page'], '%s:classifications' % slug, st['mark'],
            'What %s issues' % st['name'], ' &middot; '.join(st['codes'])),
        row(st['page'], '%s:all' % slug, '&rarr;',
            'Everything we broker in %s' % st['name'], 'The state page'),
    ]
    rows.append('<p class="mm-casc__note">No live listings in %s today &mdash; that is a stock '
                'position, not a coverage gap. Tell us the classification and the market and we go '
                'looking off-market against it.</p>' % st['name'])
    panes.append('<div class="mm-casc__pane" id="mmst-%s" data-mmpane="%s" role="tabpanel" '
                 'aria-labelledby="mmstate-%s" hidden>%s</div>' % (slug, slug, slug, ''.join(rows)))
panes.append('</div>')

details = ['<div class="mm-casc__details">', d_counties, d_cities, d_markets]
if MODE == 'markets':
    for href, slug, name in markets:
        lis = ''.join('<li><a href="liquor-license-%s-type-%s.html">%s</a></li>'
                      % (slug, t, TYPE_NAME[t]) for t in TYPES)
        lis += '<li><a href="%s">Everything we broker in %s</a></li>' % (href, name)
        details.append(
            '<div class="mm-casc__detail" data-mmdetail="california:%s" hidden>'
            '<p class="mm-casc__dhead">%s</p>'
            '<p class="mm-casc__dnote">The five classifications we publish for this market.</p>'
            '<ul class="mm-casc__dlist" data-cols="1" role="list">%s</ul></div>' % (slug, name, lis))
else:
    # REUSED VERBATIM: the existing per-type panels already list all ten markets, so
    # nothing here is retyped and nothing is invented.
    for t in TYPES:
        panel = grab_detail(OLD, 'san-francisco:type-%s' % t)
        details.append(panel.replace('data-mmdetail="san-francisco:type-%s"' % t,
                                     'data-mmdetail="california:type-%s"' % t))
for slug, st in STATES.items():
    cs = counties_of(st['page'])
    details.append(
        '<div class="mm-casc__detail" data-mmdetail="%s:counties" hidden>'
        '<p class="mm-casc__dhead">%s counties</p>'
        '<p class="mm-casc__dnote">%d published. No page exists for an individual county here.</p>'
        '<ul class="mm-casc__dlist" data-cols="3" role="list">%s</ul></div>'
        % (slug, st['name'], len(cs), ''.join('<li>%s</li>' % c for c in cs)))
    details.append(
        '<div class="mm-casc__detail" data-mmdetail="%s:classifications" hidden>'
        '<p class="mm-casc__dhead">What %s issues</p>'
        '<p class="mm-casc__dnote">%s issues these. What each authorises is set by the state, '
        'not by us.</p><ul class="mm-casc__dlist" data-cols="2" role="list">%s</ul></div>'
        % (slug, st['name'], st['issuer'], ''.join('<li>%s</li>' % c for c in st['codes'])))
    details.append(
        '<div class="mm-casc__detail" data-mmdetail="%s:all" hidden>'
        '<p class="mm-casc__dhead">%s</p>'
        '<p class="mm-casc__dnote">The state page, and the board.</p>'
        '<ul class="mm-casc__dlist" data-cols="1" role="list">'
        '<li><a href="%s">Open the %s page</a></li>'
        '<li><a href="inventory.html">See the live board</a></li></ul></div>'
        % (slug, st['name'], st['page'], st['name']))
details.append(fallback)
details.append('</div>')

open_tag = re.match(r'<div[^>]*>', OLD).group(0)
NEW = open_tag + '\n' + '\n'.join(
    [''.join(cards)] + rail + panes + details) + '\n</div>'

# ---- guards -----------------------------------------------------------------
old_links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', OLD)}
new_links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', NEW)}
lost = {l for l in old_links - new_links if l}
assert not lost, 'links lost from the menu: %s' % sorted(lost)

for t in TYPES:
    for _, slug, _ in markets:
        tgt = 'liquor-license-%s-type-%s.html' % (slug, t)
        assert tgt in new_links, 'missing %s' % tgt
assert len(re.findall(r'data-mmstate=', NEW)) == 3, 'rail must have exactly 3 states'
assert len(re.findall(r'data-mmpane=', NEW)) == 3, 'must have exactly 3 panes'
assert len(re.findall(r'data-mmcard=', NEW)) == 3, 'must have exactly 3 cards'

opts = set(re.findall(r'data-mmopt="([^"]+)"', NEW))
dets = set(re.findall(r'data-mmdetail="([^"]+)"', NEW))
orphan_opt = opts - dets
assert not orphan_opt, 'rows with no detail panel: %s' % sorted(orphan_opt)
orphan_det = dets - opts
assert not orphan_det, 'detail panels no row can reach: %s' % sorted(orphan_det)

for slug, _, _ in [(s, 0, 0) for s in ('california',) + tuple(STATES)]:
    assert 'data-mmpane="%s"' % slug in NEW, 'no pane for %s' % slug
for tag in ('div', 'a', 'span', 'ul', 'li', 'p', 'button'):
    o = len(re.findall(r'<%s\b' % tag, NEW))
    c = len(re.findall(r'</%s>' % tag, NEW))
    assert o == c, 'unbalanced <%s>: %d open / %d close' % (tag, o, c)

for h in sorted(new_links):
    if h and not h.startswith(('http', 'tel:', 'mailto:', '#')):
        assert os.path.exists(h), 'menu points at a missing page: %s' % h

print('NEW mega-menu block built and validated  [MODE=%s]' % MODE)
print('  rail          : %s' % ', '.join(re.findall(r'data-mmstate="([^"]+)"', NEW)))
print('  panes         : 3   cards: 3')
print('  option rows   : %d' % len(opts))
print('  detail panels : %d' % len(dets))
print('  distinct link targets: %d old -> %d new  (0 lost)' % (len(old_links), len(new_links)))
print('  market x type reachable: %d' % len([l for l in new_links if re.match(r'liquor-license-.*-type-\d+\.html$', l)]))
print('  size: %d bytes -> %d bytes (%+d)' % (len(OLD), len(NEW), len(NEW) - len(OLD)))

io.open('_mm-new-block-%s.html' % MODE, 'w', encoding='utf-8').write(NEW)
print('  wrote _mm-new-block-%s.html (gitignored preview source)' % MODE)
