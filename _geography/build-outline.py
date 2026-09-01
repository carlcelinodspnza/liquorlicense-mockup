#!/usr/bin/env python3
"""build-outline.py -- render geography.json as the reviewable Service Area Register page."""
import json, os, html, collections

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, 'geography.json'), encoding='utf-8'))
OUT = os.path.join(HERE, 'service-area-register.html')

P = D['places']
STATE_ORDER = ['CA', 'AZ', 'FL', 'NJ', 'OH', 'PA']
STATE_NAME = {p['state'][0]: p['label'] for p in P if p['tier'] == 'state'}
DEPTH = {p['state'][0]: p['depth'] for p in P if p['tier'] == 'state'}

counties = collections.defaultdict(list)
cities = collections.defaultdict(list)
for p in P:
    if p['tier'] == 'state':
        continue
    (counties if p['namespace'].startswith('/counties/') else cities)[p['state'][0]].append(p)

n_counties = sum(len(v) for v in counties.values())
# Distinct city-namespace slugs at city tier. Glendale is ONE slug serving two different
# cities (CA + AZ); it is counted once here and carried as a filing defect below.
n_cities = len({p['slug'] for v in cities.values() for p in v if p['tier'] != 'county'})
n_misfiled = sum(1 for v in cities.values() for p in v if p['tier'] == 'county')
n_nav = sum(1 for p in P if p['in_nav'])
n_orphan = len(P) - n_nav - 0

DEFECT = {'tier-mismatch-filed-as-city-all-pages-county', 'merged-slug-across-states',
          'slug-drift', 'has-duplicate-page'}
FLAG_TEXT = {
    'tier-mismatch-filed-as-city-all-pages-county': 'filed under /cities/ — every page is a county page',
    'merged-slug-across-states': 'one slug serving two states',
    'slug-drift': 'folder slug ≠ the name the page prints',
    'has-duplicate-page': 'duplicate page in the same folder',
    'consolidated-city-county': 'consolidated city-county — legitimately both tiers',
    'county-named-children-under-city-folder': 'city folder, county-named licence pages',
    'inherits-a-county-page': 'inherits a county page',
    'in-state-bucket': 'lives in the state bucket, no own folder',
    'also-in-az-bucket': 'also listed in the Arizona bucket',
    'also-in-fl-bucket': 'also listed in the Florida bucket',
    'orphan-no-counties-or-cities': 'one page only — no counties, no cities, unlinked from nav',
}
TIER_LABEL = {'state': 'STATE', 'county': 'COUNTY', 'city': 'CITY', 'city-county': 'CITY-COUNTY'}


def esc(s):
    return html.escape(str(s), quote=True)


def row(p):
    cls = 'row' + (' is-flagged' if any(f in DEFECT for f in p['flags']) else '')
    types = ''.join('<i class="lt">%s</i>' % esc(t) for t in p['licence_types'][:14])
    flags = ''.join(
        '<span class="flag %s" title="%s">%s</span>' % (
            'flag--defect' if f in DEFECT else 'flag--note',
            esc(FLAG_TEXT.get(f, f)), esc(FLAG_TEXT.get(f, f)))
        for f in p['flags'])
    nav = '<span class="navpin" title="One of the six rows in the client\'s nav drawer">in nav</span>' if p['in_nav'] else ''
    return ('<li class="%s" data-search="%s" data-tier="%s">'
            '<div class="row__head"><span class="tier tier--%s">%s</span>'
            '<span class="row__name">%s</span>%s'
            '<span class="row__pages" title="pages published in this folder">%d</span></div>'
            '<div class="row__slug">%s%s</div>'
            '%s%s</li>') % (
        cls, esc((p['label'] + ' ' + p['slug']).lower()), p['tier'],
        p['tier'], TIER_LABEL[p['tier']], esc(p['label']), nav, p['pages'],
        esc(p['namespace']), esc(p['slug']),
        ('<div class="lts">%s</div>' % types) if types else '',
        ('<div class="flags">%s</div>' % flags) if flags else '')


def column(title, note, items):
    body = ''.join(row(p) for p in sorted(items, key=lambda x: x['label']))
    return ('<section class="col"><header class="col__head"><h4>%s</h4>'
            '<span class="col__count">%d</span></header>'
            '<p class="col__note">%s</p><ul class="rows">%s</ul></section>') % (
        esc(title), len(items), esc(note), body)


sections = []
for code in STATE_ORDER:
    cn, ci = counties.get(code, []), cities.get(code, [])
    orphan = DEPTH.get(code) == 'orphan'
    if orphan:
        inner = ('<p class="orphan">One page only. This state names <strong>no counties and no '
                 'cities</strong>, and nothing on the site links to it — not the nav, not the '
                 'homepage, not the state hub.</p>')
    else:
        inner = ('<div class="parallel">%s%s</div>'
                 '<p class="parallel__note"><strong>These two columns are parallel, not nested.</strong> '
                 'The source publishes <code>/counties/</code> and <code>/cities/</code> as separate '
                 'top-level taxonomies and never links a city to its county. The tier badge is what '
                 'supplies the level their URLs leave out.</p>') % (
            column('/counties/', 'Each county page drills straight to licence types — never to its cities.', cn),
            column('/cities/', 'Every city sits at the same level, whatever its actual size or status.', ci))
    sections.append(
        '<section class="state%s" id="st-%s"><header class="state__head">'
        '<h3>%s <span class="state__code">%s</span></h3>'
        '<div class="state__counts">%s</div></header>%s</section>' % (
            ' state--orphan' if orphan else '', code, esc(STATE_NAME[code]), code,
            # Counts are stated PER NAMESPACE so they match the two columns exactly. Saying
            # "173 cities" would be wrong for CA: one of those folders (Fresno) is badged
            # COUNTY, which is the whole point the page is making.
            ('<span class="orphan-pill">orphan</span>' if orphan else
             '<span class="ns">/counties/ <b>%d</b></span>'
             '<span class="ns">/cities/ <b>%d</b></span>' % (len(cn), len(ci))),
            inner))

anom = [p for p in P if any(f in DEFECT for f in p['flags'])]
anom_rows = ''.join(
    '<tr><td><strong>%s</strong><br><code>%s%s</code></td><td><span class="tier tier--%s">%s</span></td>'
    '<td>%s</td><td>%s</td></tr>' % (
        esc(p['label']), esc(p['namespace']), esc(p['slug']), p['tier'], TIER_LABEL[p['tier']],
        esc(', '.join(p['state'])),
        '<br>'.join(esc(FLAG_TEXT.get(f, f)) for f in p['flags'] if f in DEFECT))
    for p in sorted(anom, key=lambda x: (x['state'][0], x['label'])))

gap_rows = ''.join(
    '<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>' % (
        esc(g['name']), esc(g['state']), esc(g['reason']))
    for g in D['gaps'])

TPL = open(os.path.join(HERE, '_outline-template.html'), encoding='utf-8').read()
page = (TPL
        .replace('{{STATES}}', ''.join(sections))
        .replace('{{ANOMALIES}}', anom_rows)
        .replace('{{GAPS}}', gap_rows)
        .replace('{{N_URLS}}', '{:,}'.format(D['total_urls']))
        .replace('{{N_COUNTIES}}', str(n_counties))
        .replace('{{N_CITIES}}', str(n_cities))
        .replace('{{N_MISFILED}}', str(n_misfiled))
        .replace('{{N_NAV}}', str(n_nav))
        .replace('{{N_PLACES}}', str(len(P)))
        .replace('{{N_ANOM}}', str(len(anom))))
open(OUT, 'w', encoding='utf-8').write(page)
print('places   : %d  (%d counties, %d cities, %d misfiled)' % (len(P), n_counties, n_cities, n_misfiled))
print('anomalies: %d   gaps: %d   nav: %d' % (len(anom), len(D['gaps']), n_nav))
print('-> %s  (%d bytes)' % (OUT, os.path.getsize(OUT)))
