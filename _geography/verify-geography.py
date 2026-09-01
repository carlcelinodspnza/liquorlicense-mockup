#!/usr/bin/env python3
"""verify-geography.py -- fail-closed gates on geography.json. No network (see spot-check script)."""
import json, re, glob, os, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, 'geography.json'), encoding='utf-8'))
raw = ' '.join(open(f, encoding='utf-8', errors='replace').read()
               for f in glob.glob(os.path.join(HERE, '_sitemaps', '*.xml')))
fails = []

def gate(name, ok, detail=''):
    print('%-4s %-52s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append(name)

# G1 -- no invented places: every slug must appear verbatim in a cached sitemap
missing = [p['slug'] for p in d['places']
           if p['tier'] != 'state' and p['slug'] not in raw]
gate('G1 every place slug appears in a sitemap', not missing, str(missing[:5]))

# G2 -- url total matches what we parsed
n = len(set(re.findall(r'<loc>([^<]+)</loc>', raw)))
gate('G2 total_urls matches sitemap parse', d['total_urls'] == n,
     '%d == %d' % (d['total_urls'], n))

# G3 -- negative control: unpublished counties must be ABSENT from places, PRESENT in gaps
absent = {'alpine', 'del-norte', 'mariposa', 'placer', 'plumas', 'trinity'}
leaked = [p['slug'] for p in d['places']
          if re.sub(r'-county$', '', p['slug']) in absent and 'CA' in p['state']]
gate('G3a unpublished CA counties absent from places', not leaked, str(leaked))
gapnames = {g['name'] for g in d['gaps']}
want = {n.title().replace('Del Norte', 'Del Norte') + ' County' for n in
        ['Alpine', 'Del Norte', 'Mariposa', 'Placer', 'Plumas', 'Trinity']}
gate('G3b those counties recorded as gaps', want <= gapnames, str(sorted(want - gapnames)))
gate('G3c Washington County FL recorded as a gap', 'Washington County' in gapnames)

# G4 -- published county totals
cty = collections.defaultdict(set)
for p in d['places']:
    if p['tier'] == 'county' and p['namespace'].startswith('/counties/'):
        cty[p['state'][0]].add(p['slug'])
gate('G4a CA counties published == 52', len(cty['CA']) == 52, str(len(cty['CA'])))
gate('G4b AZ counties published == 15', len(cty['AZ']) == 15, str(len(cty['AZ'])))
gate('G4c FL counties published == 66', len(cty['FL']) == 66, str(len(cty['FL'])))

# G5 -- city namespace totals
cs = {p['slug'] for p in d['places'] if p['namespace'] == '/cities/'}
citytier = {p['slug'] for p in d['places'] if p['namespace'] == '/cities/' and p['tier'] != 'county'}
gate('G5a distinct city-namespace folders == 192', len(cs) == 192, str(len(cs)))
gate('G5b genuine city-tier places == 191', len(citytier) == 191, str(len(citytier)))

# G6 -- every place carries a tier label from the closed set
TIERS = {'state', 'county', 'city', 'city-county'}
bad = [p['slug'] for p in d['places'] if p['tier'] not in TIERS]
gate('G6 every place has a valid tier label', not bad, str(bad[:5]))

# G7 -- the named anomalies are actually flagged
def flags(slug, state=None):
    for p in d['places']:
        if p['slug'] == slug and (state is None or state in p['state']):
            return p['flags']
    return None
gate('G7a fresno flagged tier-mismatch',
     any('tier-mismatch' in f for f in (flags('fresno') or [])), str(flags('fresno')))
gate('G7b glendale flagged merged-slug',
     any('merged-slug' in f for f in (flags('glendale', 'CA') or [])), str(flags('glendale', 'CA')))
gate('G7c orange-county flagged merged-slug',
     any('merged-slug' in f for f in (flags('orange-county', 'CA') or [])),
     str(flags('orange-county', 'CA')))
gate('G7d san-francisco tier == city-county',
     next(p['tier'] for p in d['places'] if p['slug'] == 'san-francisco') == 'city-county')

# G8 -- states
st = {p['slug'] for p in d['places'] if p['tier'] == 'state'}
gate('G8 six states published', len(st) == 6, str(sorted(st)))

print('\n%d gate(s) failed' % len(fails))
sys.exit(1 if fails else 0)
