#!/usr/bin/env python3
"""
_build-state-panels.py -- [BX] generate the STATE-tier panels on locations.html.

WHAT IT WRITES
    The Arizona / Florida / New Jersey / Ohio / Pennsylvania panels, plus the state rail,
    between sentinel comments in locations.html. California is NOT generated: its panel is
    the existing hand-authored fourteen-tab matrix and this script never touches it.

IDEMPOTENT
    Rewrites only what sits between LLA:STATE-RAIL:BEGIN/END and LLA:STATE-PANELS:BEGIN/END.
    Re-running against its own output is a no-op. (Generators here inject into files they
    also read -- see the idempotency lesson from _build-market-pages.py.)

HONESTY RULES BAKED IN
    * Every non-California state carries the zero-stock treatment. All nine licences on the
      board are Californian; no place name outside California may read as available stock.
    * Licence classifications are NAMED, never defined. licence-types.html owns definitions
      (claims C18-C20) and covers only the California types, so AZ/FL classes are not linked.
    * NJ/OH/PA publish no counties and no cities. The panel says exactly that instead of
      inventing markets.

SOURCE   _geography/geography.json (built from the client's own sitemaps)
"""
import json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
GEO = json.load(open(os.path.join(HERE, '_geography', 'geography.json'), encoding='utf-8'))
TARGET = os.path.join(HERE, 'locations.html')

# ALPHABETICAL. California is one of six, not the headline -- owner instruction. It is
# still the tab that ships selected, because it is the only state holding live stock and a
# rail that opens on an empty state hides the board; that is a stock fact, not a hierarchy.
# slug, label, code, and the state's OWN page. Every panel routes to its page — before
# this the panels dead-ended at contact.html and the state pages were reachable only
# from the header menu.
STATES = [
    ('arizona',      'Arizona',      'AZ', 'arizona-liquor-license.html'),
    ('california',   'California',   'CA', 'california-liquor-license-services.html'),
    ('florida',      'Florida',      'FL', 'florida-liquor-license.html'),
    ('new-jersey',   'New Jersey',   'NJ', 'new-jersey-liquor-license.html'),
    ('ohio',         'Ohio',         'OH', 'ohio-liquor-license.html'),
    ('pennsylvania', 'Pennsylvania', 'PA', 'pennsylvania-liquor-license.html'),
]
PAGE = {s[0]: s[3] for s in STATES}

REGULATOR = {
    'AZ': 'the Arizona Department of Liquor Licenses and Control',
    'FL': 'the Florida Division of Alcoholic Beverages and Tobacco',
}
CLASS_NOTE = {
    'AZ': 'Series 6, 7, 9, 10, 11 and 12 are the classifications published here.',
    'FL': '1COP, 2COP, 3PS, 4COP, 4COP-SFS and 6COP are the classifications published here.',
}


def esc(s):
    return html.escape(str(s), quote=False)


def by(code, tier_test, ns=None):
    out = []
    for p in GEO['places']:
        if p['tier'] == 'state' or code not in p['state']:
            continue
        if ns and not p['namespace'].startswith(ns):
            continue
        if tier_test(p['tier']):
            out.append(p)
    return sorted(out, key=lambda x: x['label'])


def counts(code):
    return (len(by(code, lambda t: t == 'county', '/counties/')),
            len(by(code, lambda t: t in ('city', 'city-county'))))


def geo_list(items, heading):
    lis = []
    for p in items:
        flag = ''
        if 'merged-slug-across-states' in p['flags']:
            flag = '<span class="loc-geo__flag" title="One slug on the client site serves this place in two states">shared slug</span>'
        lis.append('<li><span class="loc-geo__name">%s</span>%s</li>' % (esc(p['label']), flag))
    return ('<section class="loc-geo__col"><h4>%s <span class="loc-geo__n">%d</span></h4>'
            '<ul class="loc-geo__list" role="list">%s</ul></section>') % (
        esc(heading), len(items), ''.join(lis))


def rail():
    out = ['<div class="loc-staterail" role="tablist" aria-label="States we broker in">']
    for slug, label, code, _page in STATES:
        first = slug == 'california'   # selected on load: the only state with live stock
        nc, nci = counts(code)
        sub = ('%d counties &middot; %d cities' % (nc, nci)) if nc else 'No markets published'
        out.append(
            '<button class="loc-state" type="button" role="tab" id="locstate-%s" '
            'data-loc-state="%s" aria-controls="state-%s" aria-selected="%s" tabindex="%s">'
            '<span class="loc-state__name">%s</span>'
            '<span class="loc-state__sub"%s>%s</span></button>' % (
                slug, slug, slug, 'true' if first else 'false', '0' if first else '-1',
                esc(label), '' if nc else ' data-thin="1"', sub))
    out.append('</div>')
    return '\n        '.join(out)


def panel(slug, label, code):
    nc, nci = counts(code)
    head = ('<div class="loc-panel__head"><h3>%s</h3>' % esc(label))
    if nc:
        head += ('<p class="loc-panel__dek">%d counties and %d cities are published for %s, '
                 'licensed through %s. %s</p>' % (
                     nc, nci, esc(label), REGULATOR[code], CLASS_NOTE[code]))
        head += '</div>'
        empty = ('<p class="loc-empty"><b>No live listings in %s today.</b> Every licence on our '
                 'board right now is Californian. That is a stock position, not a coverage gap &mdash; '
                 'tell us the classification and the market you are working to and we go looking '
                 'off-market against it.</p>' % esc(label))
        body = ('<div class="loc-geo">%s%s</div>' % (
            geo_list(by(code, lambda t: t == 'county', '/counties/'), 'Counties'),
            geo_list(by(code, lambda t: t in ('city', 'city-county')), 'Cities')))
        foot = ('<p class="loc-panel__foot">These are the markets published for %s. What each '
                'classification authorises is set by %s, not by us &mdash; ask and we will put it in '
                'writing for your premises.</p>'
                '<div class="cta-row">'
                '<a class="btn btn-secondary" href="%s">Everything we broker in %s</a>'
                '<a class="btn btn-secondary" href="contact.html">Send a sourcing brief</a>'
                '</div>' % (esc(label), REGULATOR[code], PAGE[slug], esc(label)))
        inner = head + empty + body + foot
    else:
        head += '</div>'
        inner = head + (
            '<p class="loc-empty loc-empty--thin"><b>We broker in %s, and there is no market '
            'breakdown to show.</b> No counties and no cities are published for this state, and we '
            'would rather say so than list place names we cannot stand behind. Tell us the town and '
            'the licence you need and we will answer on the specifics.</p>'
            '<div class="cta-row">'
            '<a class="btn btn-secondary" href="%s">Everything we broker in %s</a>'
            '<a class="btn btn-secondary" href="contact.html">Send a sourcing brief</a>'
            '</div>' % (esc(label), PAGE[slug], esc(label)))
    return ('<div class="loc-panel loc-panel--state%s" id="state-%s" data-loc-statepanel="%s" '
            'role="tabpanel" aria-labelledby="locstate-%s" hidden>%s</div>' % (
                '' if nc else ' loc-panel--thin', slug, slug, slug, inner))


def splice(src, name, payload):
    b, e = 'LLA:%s:BEGIN' % name, 'LLA:%s:END' % name
    pat = re.compile(r'(<!-- %s -->)(.*?)(<!-- %s -->)' % (re.escape(b), re.escape(e)), re.S)
    if not pat.search(src):
        raise SystemExit('sentinel %s not found in locations.html -- add it first' % name)
    return pat.sub(lambda m: m.group(1) + '\n        ' + payload + '\n        ' + m.group(3),
                   src, count=1)


def main():
    src = open(TARGET, encoding='utf-8').read()
    panels = '\n\n        '.join(panel(s, l, c) for s, l, c, _p in STATES if s != 'california')
    src = splice(src, 'STATE-RAIL', rail())
    src = splice(src, 'STATE-PANELS', panels)
    open(TARGET, 'w', encoding='utf-8').write(src)
    for s, l, c, _p in STATES:
        nc, nci = counts(c)
        print('  %-14s %3d counties  %3d cities%s' % (l, nc, nci, '' if nc else '   (thin panel)'))
    print('-> locations.html state rail + %d generated panels' % (len(STATES) - 1))


if __name__ == '__main__':
    main()
