#!/usr/bin/env python3
"""
Rebuild the Locations mega menu so it is THREE ROWS PER STATE, and write the block
that _build-mega-apply.py swaps into every page.

WHY THREE ROWS -- the owner asked for two things that turn out to be one thing:

  "shorten the mega menu only up until below 'Arizona 15 counties'"
  "this tab should show 'Services we provide' ... including the type of licences
   on the 3rd column"

  Measured on the live panel: the Arizona button's bottom edge is at 253px and the
  panel starts at 68px, so the target height is ~196px. The panes column carries
  14px of padding top and bottom, leaving 168px, and a row is exactly 56px. THREE
  ROWS IS 168px. Four rows is 224px and overshoots by 27px. So the height request
  can only be met if the row count comes down to three -- which is precisely what
  moving the licence types into the detail column achieves.

WHAT EACH PANE BECOMES:

  california   counties · services · markets      (was 8 rows)
  florida      counties · services · all          (was 7 rows)
  arizona      counties · services · all          (was 8 rows)

WHAT IS REMOVED, and what it costs -- counted, not asserted:

  1. "Cities we broker in" (California). The owner asked for this row to become
     "Services we provide". Its detail listed 171 city names as <span>, NOT links,
     so ZERO links are lost. All 171 remain published on
     california-liquor-license-services.html, verified.

  2. The five california:type-NN detail panels. These held the only menu route to
     the 50 market x type pages -- ten each. Checked before removing: all 50 are
     linked from FIVE non-menu pages each (min 5, median 5, max 5), so none is
     orphaned. The five licence-type PAGES themselves stay in the menu, moved into
     the new services panel as links.

  3. The Florida and Arizona classification rows. All five/six pointed at the same
     #classifications anchor on the state page, which the services panel still
     carries. No target lost.

THE NEW PANEL lists the eight services and then the state's own classifications,
which is what the owner asked for. Service titles are the <h1> of each service page,
read from the files rather than retyped.

Fail-closed: the block is validated in memory and written only if every check passes.
"""
import re, io, os, sys, glob, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SRC = 'service-buy.html'
OUT = '_mm-new-block-classifications.html'

SERVICES = [
    'service-buy.html', 'service-sell.html', 'service-transfer.html',
    'service-valuation.html', 'service-cup.html', 'service-compliance.html',
    'service-escrow.html', 'service-new-business.html',
]

CLASSIFICATIONS = {
    'california': [('20', 'Type 20', 'licence-type-20.html'),
                   ('21', 'Type 21', 'licence-type-21.html'),
                   ('41', 'Type 41', 'licence-type-41.html'),
                   ('47', 'Type 47', 'licence-type-47.html'),
                   ('48', 'Type 48', 'licence-type-48.html')],
    'florida':    [('1', '1COP', 'florida-liquor-license.html#classifications'),
                   ('2', '2COP', 'florida-liquor-license.html#classifications'),
                   ('3', '3PS', 'florida-liquor-license.html#classifications'),
                   ('4', '4COP', 'florida-liquor-license.html#classifications'),
                   ('6', '6COP', 'florida-liquor-license.html#classifications')],
    'arizona':    [('6', 'Series 6', 'arizona-liquor-license.html#classifications'),
                   ('7', 'Series 7', 'arizona-liquor-license.html#classifications'),
                   ('9', 'Series 9', 'arizona-liquor-license.html#classifications'),
                   ('10', 'Series 10', 'arizona-liquor-license.html#classifications'),
                   ('11', 'Series 11', 'arizona-liquor-license.html#classifications'),
                   ('12', 'Series 12', 'arizona-liquor-license.html#classifications')],
}

STATE_NOTE = {
    'california': 'Eight services. California ABC issues Types 20, 21, 41, 47 and 48.',
    'florida':    'Eight services. Florida issues 1COP, 2COP, 3PS, 4COP and 6COP.',
    'arizona':    'Eight services. Arizona issues Series 6, 7, 9, 10, 11 and 12.',
}

# The three <p class="mm-casc__note"> lines that lived at the foot of the old panes.
# They are CARRIED FORWARD, not dropped: the California one holds the only menu link
# to licence-types.html, and the Florida and Arizona ones state a real fact about
# stock that exists nowhere else in the menu.
PANE_NOTE = {
    'california': ('What each classification authorises is set out under '
                   '<a href="licence-types.html">Licensing</a>.'),
    'florida':    'No live listings in Florida today &mdash; a stock position, not a coverage gap.',
    'arizona':    'No live listings in Arizona today &mdash; a stock position, not a coverage gap.',
}

# The third row of each pane.
#
# THE COPY IS BOUNDED BY A MEASURED BOX, NOT BY TASTE. A row's text column is
# 175px wide (the panes column is a fixed 292px at every viewport; the mark, gaps
# and padding take the rest), and .mm-casc__row .s is nowrap + ellipsis. Anything
# wider silently truncates, and a title wider than 175px wraps to a second line,
# which makes that ONE row 75px tall against its neighbours' 56px. That is the
# broken spacing the owner photographed.
#
# The inherited strings all overflowed -- measured in the browser at the real
# font, not estimated:
#     "All 14 California markets"              187px   over by 12
#     "Statewide plus thirteen named markets"  229px   over by 54
#     "Everything we broker in Florida"        239px   over by 64
#     "Everything we broker in Arizona"        244px   over by 69
# Widening the column instead was rejected: fitting the 244px title needs
# +69px, which takes the details column below the 153px per column that
# "San Luis Obispo County" needs, so the 52-county list would start wrapping.
#
# Replacements, with their measured width and headroom inside the 175px box.
# The state name is dropped from the California title and the Florida/Arizona
# sublines because the rail button and the card beside them already name the
# state twice over. Do NOT lengthen these without re-measuring.
THIRD_ROW = {
    'california': ('markets', 'locations.html#state-california', '&rarr;',
                   'All 14 markets',            # 108px, 67 spare
                   'Statewide plus 13 named'),  # 145px, 30 spare
    'florida':    ('all', 'florida-liquor-license.html', '&rarr;',
                   'All of Florida',            #  98px, 77 spare
                   'The state page'),           #  87px, 88 spare
    'arizona':    ('all', 'arizona-liquor-license.html', '&rarr;',
                   'All of Arizona',            # 103px, 72 spare
                   'The state page'),           #  87px, 88 spare
}

FIRST_ROW = {
    'california': ('counties', 'california-liquor-license-services.html', 'CA',
                   'Counties we broker in', '52 counties published'),
    'florida':    ('counties', 'florida-liquor-license.html#markets', 'FL',
                   'Counties we broker in', '66 counties published'),
    'arizona':    ('counties', 'arizona-liquor-license.html#markets', 'AZ',
                   'Counties we broker in', '15 counties published'),
}


def block_of(doc):
    i = doc.find('mm-casc')
    assert i >= 0, 'no mm-casc'
    i = doc.rfind('<div', 0, i)
    d, j = 1, doc.find('>', i) + 1
    while d and j < len(doc):
        nx = re.search(r'<(/?)div\b[^>]*>', doc[j:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        j += nx.end()
    return doc[i:j]


def detail_of(blk, key):
    """Lift an existing detail panel out verbatim -- depth-matched on <div>."""
    m = re.search(r'<div class="mm-casc__detail" data-mmdetail="%s"' % re.escape(key), blk)
    assert m, 'no detail panel for %s' % key
    i = m.start()
    d, j = 1, blk.find('>', i) + 1
    while d and j < len(blk):
        nx = re.search(r'<(/?)div\b[^>]*>', blk[j:])
        if not nx:
            break
        d += -1 if nx.group(1) else 1
        j += nx.end()
    return blk[i:j]


def service_labels():
    """The site's OWN short name for each service, lifted from the Services mega
    menu in index.html.

    Not the <h1>, and not invented. The h1s are sentence-length ("Licensing
    compliance consulting", "Escrow and transaction guidance") and wrapped to two
    lines in a 155px column, which is most of why the first build of this panel
    overflowed its box by 154px. The Services menu already carries a short form of
    every one of them -- "Licensing compliance", "Escrow guidance" -- so this reads
    those rather than coining new ones, and the two menus stay in step by
    construction."""
    doc = io.open('index.html', encoding='utf-8').read()
    i = doc.find('data-disclosure="services"')
    assert i >= 0, 'no Services disclosure in index.html'
    seg = doc[i:i + 7000]
    out = {}
    for m in re.finditer(r'href="(service-[a-z-]+\.html)"(.*?)</a>', seg, re.S):
        spans = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()
                 for t in re.findall(r'<span class="[^"]*"[^>]*>(.*?)</span>', m.group(2), re.S)]
        spans = [t for t in spans if t and not re.fullmatch(r'\d{2}', t)]
        if spans and m.group(1) not in out:
            out[m.group(1)] = spans[0]
    return out


# SOURCE THE OLD BLOCK FROM GIT, NOT FROM DISK. The working tree may already carry
# this rebuild, in which case reading service-buy.html would compare the new block
# against itself and every "what did we drop" assertion below would silently pass on
# an empty diff. 359ba58 is the last commit before this change. Falls back to disk
# only if git cannot be read, and says so.
PRE = '359ba58'
try:
    import subprocess
    src = subprocess.run(['git', 'show', '%s:%s' % (PRE, SRC)],
                         capture_output=True, text=True, check=True).stdout
    _src_from = 'git %s' % PRE
except Exception as _e:
    src = io.open(SRC, encoding='utf-8').read()
    _src_from = 'DISK (git unavailable: %s)' % _e
blk = block_of(src)

# ---- pieces kept verbatim from the shipped menu -------------------------------
cards = ''.join(re.findall(r'<a class="mm-casc__card".*?</a>', blk, re.S))
assert cards.count('mm-casc__card"') == 3, 'expected 3 state cards, got %d' % cards.count('mm-casc__card"')

KEEP_DETAILS = ['california:counties', 'california:markets',
                'florida:counties', 'florida:all',
                'arizona:counties', 'arizona:all']
def close_grid(panel):
    """Pad every dlist so its last row is FULL, and the grid closes.

    A CSS grid only draws rules where there are cells. Eight services in three
    columns leaves the third cell of the last row empty, so the rule stops short
    and the box reads as broken -- which is what the owner photographed. The same
    happens to California's 52 counties in three columns (52 = 3x17 + 1) and to
    five classifications in six columns.

    Column count cannot fix this in general (52 has no useful divisor near three),
    so the fix is structural and count-agnostic: append empty <li> fillers until
    the item count is a multiple of the column count. A filler carries no text, so
    it adds no words and no links; it exists only to carry the two hairlines.
    """
    out, added = panel, 0
    for m in list(re.finditer(r'<ul class="mm-casc__dlist" data-cols="(\d)"[^>]*>(.*?)</ul>',
                              out, re.S))[::-1]:
        cols = int(m.group(1))
        n = m.group(2).count('<li')
        pad = (-n) % cols
        if not pad:
            continue
        fill = '<li class="mm-casc__dlist__pad" aria-hidden="true"></li>' * pad
        out = out[:m.end(2)] + fill + out[m.end(2):]
        added += pad
    return out, added


def normalise_items(panel):
    """Wrap bare-text <li> items in a <span>.

    THIS IS THE ACTUAL CAUSE of the owner's "these texts are quite big". Every type
    rule on these lists is written as `.mm-casc__dlist a` / `.mm-casc__dlist span`,
    so an item shaped `<li>Alachua County</li>` matches NOTHING -- no font-size, no
    line-height, no padding -- and renders at the ambient size. Measured: 66 of 66
    Florida county items and 15 of 15 Arizona ones are bare, while all 52 California
    ones are already wrapped, which is why only two of the three lists looked wrong.

    A <span> here is exactly what the California list already uses, and the CSS
    already documents it as "a published place with no page of its own -- deliberately
    not a link". Wrapping adds no words and no links; it only lets the existing rules
    apply.
    """
    out, n = re.subn(r'<li>(?!\s*<)([^<]+)</li>', r'<li><span>\1</span></li>', panel)
    return out, n


kept, _wrapped = {}, 0
for k in KEEP_DETAILS:
    _p, _n = normalise_items(detail_of(blk, k))
    kept[k] = _p
    _wrapped += _n

# ---- the rail -----------------------------------------------------------------
RAIL_SUB = {'california': '52 counties &middot; 172 cities',
            'florida': '66 counties', 'arizona': '15 counties'}
CHEV = ('<svg class="mm-casc__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M9 6l6 6-6 6"/></svg>')
rail = ['<div class="mm-casc__rail" role="tablist" aria-label="Where we broker">']
for n, st in enumerate(['california', 'florida', 'arizona']):
    rail.append(
        '<button class="mm-casc__state" type="button" role="tab" id="mmstate-%s" data-mmstate="%s" '
        'data-mmdefault="%s:services" aria-controls="mmst-%s" aria-selected="%s" tabindex="%s">'
        '<span class="mm-casc__name">%s</span><span class="mm-casc__sub">%s</span>%s</button>'
        % (st, st, st, st, 'true' if n == 0 else 'false', '0' if n == 0 else '-1',
           st.capitalize(), RAIL_SUB[st], CHEV))
rail.append('</div>')
rail = '\n'.join(rail)

# ---- the panes: exactly three rows each ---------------------------------------
def row(state, key, href, mark, title, sub):
    s = '<span class="s">%s</span>' % sub if sub else ''
    return ('<a class="mm-casc__row" role="menuitem" href="%s" data-mmopt="%s:%s">'
            '<span class="mm-casc__mark">%s</span><span class="mm-casc__txt">'
            '<span class="t">%s</span>%s</span></a>' % (href, state, key, mark, title, s))


panes = ['<div class="mm-casc__panes">']
for n, st in enumerate(['california', 'florida', 'arizona']):
    k1, h1_, m1, t1, s1 = FIRST_ROW[st]
    k3, h3, m3, t3, s3 = THIRD_ROW[st]
    body = (row(st, k1, h1_, m1, t1, s1)
            + row(st, 'services', 'services.html', '&sect;', 'Services we provide',
                  '%d services &middot; %d classifications'
                  % (len(SERVICES), len(CLASSIFICATIONS[st])))
            + row(st, k3, h3, m3, t3, s3))
    panes.append('<div class="mm-casc__pane" id="mmst-%s" data-mmpane="%s" role="tabpanel" '
                 'aria-labelledby="mmstate-%s"%s>%s</div>'
                 % (st, st, st, '' if n == 0 else ' hidden', body))
panes.append('</div>')
panes = '\n'.join(panes)

# ---- the new services detail panels -------------------------------------------
_lab = service_labels()
missing = [p for p in SERVICES if p not in _lab]
assert not missing, 'the Services menu has no short label for %s' % missing
svc_titles = [(p, _lab[p]) for p in SERVICES]
assert max(len(t) for _, t in svc_titles) <= 26, \
    'a service label is too long for a 155px column: %s' % max(svc_titles, key=lambda x: len(x[1]))[1]
details = ['<div class="mm-casc__details">']
for st in ['california', 'florida', 'arizona']:
    details.append(kept['%s:counties' % st])
    # The sub-heading carries the link the removed footnote used to hold. California
    # points at licence-types.html (what each classification authorises); Florida and
    # Arizona point at their own #classifications section, which is where their series
    # are actually defined.
    CLS_HEAD_HREF = {'california': 'licence-types.html',
                     'florida': 'florida-liquor-license.html#classifications',
                     'arizona': 'arizona-liquor-license.html#classifications'}
    cls_head = ('<a href="%s">%s classifications</a>'
                % (CLS_HEAD_HREF[st], st.capitalize()))
    svc_items = ''.join('<li><a href="%s">%s</a></li>' % (p, t) for p, t in svc_titles)
    cls_items = ''.join('<li><a href="%s">%s</a></li>' % (href, label)
                        for _, label, href in CLASSIFICATIONS[st])
    details.append(
        # THREE COLUMNS, and no dnote. The panel has to live inside a menu capped at
        # the rail's own height, so every avoidable line costs visible content. Two
        # columns put the eight services on four rows; three puts them on three. The
        # dnote ("Eight services. California ABC issues...") was cut because the ROW
        # that opens this panel already reads "8 services - 5 classifications", so it
        # said the same thing twice for ~29px.
        '<div class="mm-casc__detail" data-mmdetail="%s:services" hidden>\n'
        '              <p class="mm-casc__dhead">Services we provide</p>%.0s\n'
        # TWO columns for the services. At three (155px) "Conditional Use Permits"
        # and "New business planning" both wrapped to a second line, which is the
        # other half of the ragged look in the owner's screenshot. Two columns give
        # 244px, every label sits on one line, and 8 divides by 2 so the grid closes
        # without any filler at all.
        '              <ul class="mm-casc__dlist" data-cols="2" role="list">%s</ul>\n'
        # SIX COLUMNS for the classifications. They are the shortest labels on the
        # page ("Type 20", "1COP", "Series 10"), and at three columns they took two
        # rows -- which pushed the footnote out of a panel that has 219px to work
        # with. Six puts California's five, Florida's five and Arizona's six all on
        # ONE row, in an 81px column that comfortably holds "Series 10" at 13px.
        '              <p class="mm-casc__dhead mm-casc__dhead--sub">%s</p>\n'
        # NO FOOTNOTE. It was carried forward from the old pane footers on 2026-09-07
        # and the owner removed it the same day -- the "No live listings in Florida
        # today" line in particular. The only thing it held that mattered was the
        # California link to licence-types.html, and that is preserved by making the
        # classifications sub-heading itself the link (see cls_head below), so no
        # target is lost by dropping the paragraph.
        '              <ul class="mm-casc__dlist" data-cols="%d" role="list">%s</ul>\n'
        '            </div>' % (st, STATE_NOTE[st], svc_items, cls_head,
                                len(CLASSIFICATIONS[st]), cls_items))
    third = THIRD_ROW[st][0]
    details.append(kept['%s:%s' % (st, third)])
details.append('</div>')
details = '\n'.join(details)

NEW = ('<div class="mm-mega__layout mm-casc" data-mm-cascade>\n'
       + cards + '\n' + rail + '\n' + panes + '\n' + details + '\n</div>')

# ================================ GUARDS ======================================
opts = set(re.findall(r'data-mmopt="([^"]+)"', NEW))
dets = set(re.findall(r'data-mmdetail="([^"]+)"', NEW))
assert opts == dets, 'rows/panels mismatch: %s' % (opts ^ dets)
assert len(opts) == 9, 'expected 9 distinct options (3 states x 3 rows), got %d' % len(opts)
for st in ['california', 'florida', 'arizona']:
    pane = re.search(r'data-mmpane="%s".*?(?=<div class="mm-casc__pane"|</div>\s*<div class="mm-casc__details")' % st, NEW, re.S).group(0)
    n = len(re.findall(r'class="mm-casc__row"', pane))
    assert n == 3, '%s pane has %d rows, must be 3 for the height target' % (st, n)
assert len(re.findall(r'data-mmstate=', NEW)) == 3
assert len(re.findall(r'data-mmcard=', NEW)) == 3
assert len(re.findall(r'data-mmpane=', NEW)) == 3
for d in re.findall(r'data-mmdefault="([^"]+)"', NEW):
    assert d in dets, 'rail default %s has no panel' % d

# every link target must exist
links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', NEW)}
for h in sorted(links):
    if h and not h.startswith(('http', 'tel:', 'mailto:')):
        assert os.path.exists(h), 'menu points at missing %s' % h

# the eight service pages and the five CA type pages must all be present
for p in SERVICES:
    assert 'href="%s"' % p in NEW, 'services panel lost %s' % p
for _, _, href in CLASSIFICATIONS['california']:
    assert 'href="%s"' % href in NEW, 'lost %s' % href

# WHAT THIS BLOCK DELIBERATELY DROPS, re-proved here rather than trusted:
old_links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', blk)}
dropped = sorted(l for l in old_links - links if l)
mt = sorted(l for l in dropped if re.match(r'liquor-license-.*-type-\d+\.html$', l))
other = sorted(set(dropped) - set(mt))
assert not other, 'links dropped that are NOT market x type pages: %s' % other
assert len(mt) == 50, 'expected exactly the 50 market x type links to drop, got %d' % len(mt)
# and each of those 50 must be reachable from a page OUTSIDE the menu
pages = [f for f in sorted(glob.glob('*.html')) if not f.startswith('_')]
for t in mt:
    inb = 0
    for p in pages:
        s = io.open(p, encoding='utf-8').read()
        b = block_of(s) if 'mm-casc' in s else ''
        body = s.replace(b, '') if b else s
        if re.search(r'href="%s(?:#[^"]*)?"' % re.escape(t), body):
            inb += 1
    assert inb >= 1, 'ORPHANED: %s has no inbound link outside the mega menu' % t

# structural
for tag in ('div', 'a', 'span', 'ul', 'li', 'p', 'button'):
    o = len(re.findall(r'<%s\b' % tag, NEW)); c = len(re.findall(r'</%s>' % tag, NEW))
    assert o == c, 'unbalanced <%s> %d/%d' % (tag, o, c)
t = re.sub(r'<[^<>]*>', '', NEW)
assert '>' not in t, 'stray ">"'
assert '<h1' not in NEW, 'the menu must not contain an h1'
# no item may be left bare: a bare <li> matches none of the .mm-casc__dlist type rules
_bare = re.findall(r'<li>(?!\s*<)([^<]+)</li>', NEW)
assert not _bare, '%d list items are still bare text and would render unstyled: %s' % (
    len(_bare), _bare[:4])
# The footnotes are deliberately absent (owner, 2026-09-07). What must NOT be absent
# is the link one of them carried.
assert 'mm-casc__dfoot' not in NEW, 'a footnote survived; the owner asked for none'
for st, note in PANE_NOTE.items():
    assert note not in NEW, 'pane note for %s is still present' % st
assert NEW.count('href="licence-types.html"') == 1, \
    'the licence-types link the footnote carried was not preserved on the sub-heading'

NEW, _padded = close_grid(NEW)
for m in re.finditer(r'<ul class="mm-casc__dlist" data-cols="(\d)"[^>]*>(.*?)</ul>', NEW, re.S):
    cols, n = int(m.group(1)), m.group(2).count('<li')
    assert n % cols == 0, 'grid still ragged: %d items in %d columns' % (n, cols)

io.open(OUT, 'w', encoding='utf-8').write(NEW)
print('wrote %s  %d bytes (was %d)' % (OUT, len(NEW), len(blk)))
print('   baseline read from: %s' % _src_from)
print('   bare <li> items wrapped in <span> so the type rules apply: %d' % _wrapped)
print('   empty cells added to close ragged grid rows: %d' % _padded)
print('   panes            : 3 rows each  (california, florida, arizona)')
print('   distinct options : %d   detail panels: %d' % (len(opts), len(dets)))
print('   services panel   : %d services + per-state classifications' % len(SERVICES))
print('   rail default     : <state>:services on all three')
print('   DROPPED          : the "Cities we broker in" row (171 city names, 0 links),')
print('                      the 5 california:type-NN panels and with them the 50 menu')
print('                      routes to market x type pages -- each of those 50 proved')
print('                      reachable from at least one non-menu page before dropping')
print('   NO OTHER LINK LOST: asserted against the shipped menu\'s full href set')
