#!/usr/bin/env python3
"""
_build-locations-menu.py -- [CA] the LOCATIONS cascade menu, stamped into the shared header.

RAIL MATCHES THE CLIENT'S LIVE NAV, exactly and in their order:
    California · San Francisco · Los Angeles · San Diego · Orange County · Ventura County
That is one state plus three cities and two counties -- their nav, not a taxonomy. Every
other state and market stays reachable through "All locations" and locations.html; this
column mirrors what the client actually publishes in their header.

FOUR COLUMNS
  1 card     the place's general info -> its own page
  2 rail     the six places above
  3 options  GEOGRAPHY under the state (counties / cities / markets), CLASSIFICATIONS
             under a market -- because at market level the question IS which class, and
             the owner asked for types to show at county/city level. Never both.
  4 detail   what sits under the hovered option. Opens on each place's default, so the
             column is never an empty "hover something" prompt.

Ventura carries five classification pages here where the client publishes only an
overview -- ours go deeper, and that is stated rather than hidden.

IDEMPOTENT -- detects its own marker id and skips.
"""
import io, os, re, glob, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
_GEO = json.load(io.open(os.path.join(HERE, '_geography', 'geography.json'), encoding='utf-8'))

MARKER = 'mm-mega-locations'
OLD_NAV = '      <li><a class="mm-navlink" href="locations.html">Locations</a></li>\n'
OLD_DRAWER = '    <a class="mm-drawer__link" href="locations.html">Locations</a>\n'
CARET = ('<svg class="mm-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
         'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
         '<path d="M6 9l6 6 6-6"/></svg>')
CHEV = ('<svg class="mm-casc__chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<path d="M9 6l6 6-6 6"/></svg>')

TYPES = [('20', 'Off-Sale Beer &amp; Wine'), ('21', 'Off-Sale General'),
         ('41', 'On-Sale Beer &amp; Wine, Eating Place'), ('47', 'On-Sale General, Eating Place'),
         ('48', 'On-Sale General, Public Premises')]

# all ten markets that carry a page per classification — used by the shared column-4 panels
MARKETS = ['fresno', 'los-angeles', 'orange', 'riverside', 'sacramento', 'san-bernardino',
           'san-diego', 'san-francisco', 'santa-barbara', 'ventura']
MARKET_LABEL = {'fresno': 'Fresno County', 'los-angeles': 'Los Angeles County',
                'orange': 'Orange County', 'riverside': 'Riverside County',
                'sacramento': 'Sacramento County', 'san-bernardino': 'San Bernardino County',
                'san-diego': 'San Diego County', 'san-francisco': 'San Francisco County',
                'santa-barbara': 'Santa Barbara County', 'ventura': 'Ventura County'}

# THE CLIENT'S NAV, in their order. label is theirs, not our county-formal version.
PLACES = [
    dict(slug='california', label='California', code='CA', kind='state',
         page='california-liquor-license-services.html',
         cardt='California Liquor Licence Services',
         cardd='Brokerage, qualification, consulting and corporate applications',
         counties=52, cities=172, default='california:markets'),
    dict(slug='san-francisco', label='San Francisco', code='SF', kind='market',
         page='liquor-license-san-francisco.html', stock=1,
         cardt='San Francisco County', cardd='1 live listing today',
         default='san-francisco:type-47'),
    dict(slug='los-angeles', label='Los Angeles', code='LA', kind='market',
         page='liquor-license-los-angeles.html', stock=3,
         cardt='Los Angeles County', cardd='3 live listings today',
         default='los-angeles:type-47'),
    dict(slug='san-diego', label='San Diego', code='SD', kind='market',
         page='liquor-license-san-diego.html', stock=1,
         cardt='San Diego County', cardd='1 live listing today',
         default='san-diego:type-47'),
    dict(slug='orange', label='Orange County', code='OC', kind='market',
         page='liquor-license-orange.html', stock=1,
         cardt='Orange County', cardd='1 live listing today',
         default='orange:type-47'),
    dict(slug='ventura', label='Ventura County', code='VC', kind='market',
         page='liquor-license-ventura.html', stock=0,
         cardt='Ventura County', cardd='No live listings today',
         default='ventura:type-47'),
]


def geo_names(code, tier):
    out = [p['label'] for p in _GEO['places']
           if code in p['state'] and p['tier'] == tier
           and (p['namespace'].startswith('/counties/') if tier == 'county' else True)]
    return sorted(set(out))


def row(href, title, sub, mark, opt=None):
    return ('              <a class="mm-casc__row" role="menuitem" href="%s"%s>'
            '<span class="mm-casc__mark">%s</span><span class="mm-casc__txt">'
            '<span class="t">%s</span><span class="s">%s</span></span></a>' % (
                href, (' data-mmopt="%s"' % opt) if opt else '', mark, title, sub))


def detail(key, heading, note, items, cols=2):
    lis = ''.join(('<li><a href="%s">%s</a></li>' % (h, l)) if h else ('<li><span>%s</span></li>' % l)
                  for l, h in items)
    return ('            <div class="mm-casc__detail" data-mmdetail="%s" hidden>\n'
            '              <p class="mm-casc__dhead">%s</p>\n'
            '              <p class="mm-casc__dnote">%s</p>\n'
            '              <ul class="mm-casc__dlist" data-cols="%d" role="list">%s</ul>\n'
            '            </div>' % (key, heading, note, cols, lis))


def card(pl):
    first = pl['slug'] == 'california'
    return ('            <a class="mm-casc__card" role="menuitem" data-mmcard="%s" href="%s"%s>'
            '<span class="mm-casc__cardmark" aria-hidden="true">%s</span>'
            '<span class="mm-casc__cardt">%s</span>'
            '<span class="mm-casc__cardd">%s</span>'
            '<span class="mm-casc__cardgo" aria-hidden="true">&rarr;</span></a>'
            % (pl['slug'], pl['page'], '' if first else ' hidden',
               pl['code'], pl['cardt'], pl['cardd']))


def rail():
    out = []
    for pl in PLACES:
        first = pl['slug'] == 'california'
        sub = ('%d counties &middot; %d cities' % (pl['counties'], pl['cities'])
               if pl['kind'] == 'state' else
               ('%d live listing%s' % (pl['stock'], '' if pl['stock'] == 1 else 's')
                if pl['stock'] else 'No stock today'))
        out.append(
            '            <button class="mm-casc__state" type="button" role="tab" id="mmstate-%s" '
            'data-mmstate="%s" data-mmdefault="%s" aria-controls="mmst-%s" aria-selected="%s" '
            'tabindex="%s"><span class="mm-casc__name">%s</span>'
            '<span class="mm-casc__sub"%s>%s</span>%s</button>'
            % (pl['slug'], pl['slug'], pl['default'], pl['slug'],
               'true' if first else 'false', '0' if first else '-1', pl['label'],
               '' if (pl['kind'] == 'state' or pl.get('stock')) else ' data-thin="1"', sub, CHEV))
    return '\n'.join(out)


def pane(pl):
    first, sl = pl['slug'] == 'california', pl['slug']
    rows = []
    if pl['kind'] == 'state':
        # geography under the state — a licence type is not a place
        rows.append(row(pl['page'], 'Counties we broker in',
                        '%d counties published' % pl['counties'], pl['code'], '%s:counties' % sl))
        rows.append(row(pl['page'], 'Cities we broker in',
                        '%d cities published' % pl['cities'], pl['code'], '%s:cities' % sl))
        rows.append(row('locations.html#state-california', 'All 14 California markets',
                        'Statewide plus thirteen named markets', '&rarr;', '%s:markets' % sl))
        note = ('              <p class="mm-casc__note">Classifications are a market-level '
                'question &mdash; open a market to see which apply there. The definitions live '
                'under <a href="licence-types.html">Licensing</a>.</p>')
    else:
        # classifications under a market — this IS the county/city level
        for n, desc in TYPES:
            rows.append(row('liquor-license-%s-type-%s.html' % (sl, n), 'Type %s' % n, desc, n,
                            '%s:type-%s' % (sl, n)))
        rows.append(row(pl['page'], 'Everything we broker in %s' % pl['label'],
                        pl['cardd'], '&rarr;', '%s:all' % sl))
        note = ('              <p class="mm-casc__note">The client publishes an overview for this '
                'market; these five classification pages are ours.</p>'
                if sl == 'ventura' else '')
    return ('            <div class="mm-casc__pane" id="mmst-%s" data-mmpane="%s" role="tabpanel" '
            'aria-labelledby="mmstate-%s"%s>\n%s\n%s            </div>'
            % (sl, sl, sl, '' if first else ' hidden', '\n'.join(rows), note + '\n' if note else ''))


def details(pl):
    sl, out = pl['slug'], []
    if pl['kind'] == 'state':
        counties = geo_names(pl['code'], 'county')
        have = {v: k for k, v in MARKET_LABEL.items()}
        out.append(detail('%s:counties' % sl, 'California counties',
                          '%d published. Ten carry a market page of their own.' % len(counties),
                          [(c, ('liquor-license-%s.html' % have[c]) if c in have else None)
                           for c in counties], cols=3))
        out.append(detail('%s:cities' % sl, 'California cities',
                          '%d published by the client. No page exists for an individual city here.'
                          % len(geo_names(pl['code'], 'city')),
                          [(x, None) for x in geo_names(pl['code'], 'city')], cols=3))
        out.append(detail('%s:markets' % sl, 'California markets',
                          'Thirteen named markets, each with its own page.',
                          [(MARKET_LABEL[m], 'liquor-license-%s.html' % m) for m in MARKETS]))
    else:
        for n, desc in TYPES:
            out.append(detail('%s:type-%s' % (sl, n), 'Type %s &mdash; %s' % (n, desc),
                              'The same classification in every market that carries a page for it.',
                              [(MARKET_LABEL[m], 'liquor-license-%s-type-%s.html' % (m, n))
                               for m in MARKETS]))
        out.append(detail('%s:all' % sl, '%s' % pl['cardt'],
                          'The market page, and the board filtered to it.',
                          [('Open the %s page' % pl['cardt'], pl['page']),
                           ('See the live board', 'inventory.html')], cols=1))
    return out


NAV = '''      <li class="mm-has-panel" data-disclosure="locations">
        <button class="mm-trigger" type="button" aria-haspopup="true" aria-expanded="false" aria-controls="mm-mega-locations">
          Locations
          %(caret)s
        </button>
        <div class="mm-panel mm-mega mm-mega--locations" id="mm-mega-locations" role="menu" aria-label="Locations">
          <span class="mm-panel__bloom" aria-hidden="true"></span>
          <div class="mm-mega__layout mm-casc" data-mm-cascade>
            <div class="mm-casc__cards">
%(cards)s
              <a class="mm-casc__all" role="menuitem" href="locations.html">All locations &mdash; every market we cover <span aria-hidden="true">&rarr;</span></a>
            </div>
            <div class="mm-casc__rail" role="tablist" aria-label="Where we broker">
%(rail)s
            </div>
            <div class="mm-casc__panes">
%(panes)s
            </div>
            <div class="mm-casc__details">
              <p class="mm-casc__dfall" hidden>Hover an option to see what sits under it.</p>
%(details)s
            </div>
          </div>
        </div>
      </li>
''' % {'caret': CARET, 'cards': '\n'.join(card(x) for x in PLACES), 'rail': rail(),
       'panes': '\n\n'.join(pane(x) for x in PLACES),
       'details': '\n'.join(d for x in PLACES for d in details(x))}

DRAWER = '''    <div class="mm-acc">
      <button class="mm-acc__btn" type="button" aria-expanded="false" aria-controls="mm-acc-locations">
        Locations
        %(caret)s
      </button>
      <div class="mm-acc__panel" id="mm-acc-locations">
        <div class="mm-acc__inner">
%(rows)s
          <a href="locations.html"><span class="mm-acc__ico">&rarr;</span>All markets</a>
        </div>
      </div>
    </div>
''' % {'caret': CARET,
       'rows': '\n'.join('          <a href="%s"><span class="mm-acc__ico">%s</span>%s</a>'
                         % (p['page'], p['code'], p['label']) for p in PLACES)}


def main():
    done = skipped = nonav = 0
    for f in sorted(glob.glob(os.path.join(HERE, '*.html'))):
        src = io.open(f, encoding='utf-8').read()
        if MARKER in src:
            skipped += 1
            continue
        if OLD_NAV not in src:
            nonav += 1
            continue
        src = src.replace(OLD_NAV, NAV, 1)
        if OLD_DRAWER in src:
            src = src.replace(OLD_DRAWER, DRAWER, 1)
        else:
            print('  WARN %s: no drawer link' % os.path.basename(f), file=sys.stderr)
        io.open(f, 'w', encoding='utf-8').write(src)
        done += 1
    print('stamped %d  ·  already had it %d  ·  no site-nav %d' % (done, skipped, nonav))


if __name__ == '__main__':
    main()
