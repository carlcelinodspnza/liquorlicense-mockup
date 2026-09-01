#!/usr/bin/env python3
"""
build-geography.py -- emit geography.json from the cached liquorlicenseagents.com sitemaps.

WHAT THIS IS
    The client's published service area, extracted from their own sitemaps, layered the way
    THEY layer it, with every place annotated with its true tier.

WHY IT IS SHAPED THIS WAY
    The source site publishes /cities/ and /counties/ as PARALLEL top-level namespaces. A county
    page never lists its cities and there is no city->county link anywhere on the site. So this
    dataset deliberately does NOT invent parentage. It mirrors the source layering

        ROOT -> PLACE -> LICENCE TYPE

    and supplies the missing information as an explicit `tier` label on each place
    (state | county | city | city-county). That label is the sub-categorisation the owner asked
    for, and it is the ONLY thing here that is derived rather than read off a URL.

REPRODUCIBLE
    Reads only _sitemaps/*.xml. No network. Regenerate:  python3 build-geography.py
"""

import json
import os
import re
import glob
import collections

HERE = os.path.dirname(os.path.abspath(__file__))
SITEMAPS = os.path.join(HERE, '_sitemaps')
OUT = os.path.join(HERE, 'geography.json')

# --- licence-slug grammar. This is how a page declares which state it belongs to. -------------
RE_CA = re.compile(r'-type-\d+')                  # California ABC:  Type 20/21/41/47/48/...
RE_AZ = re.compile(r'-series-\d+|-arizona-')      # Arizona DLLC:    Series 6/7/9/10/11/12/14
RE_FL = re.compile(r'-\d(?:cop|ps)(?:-|$)|-florida-')   # Florida:   1COP/2COP/3PS/4COP/6COP
# NOTE: RE_FL is anchored to a DIGIT before "cop" on purpose. A bare /cop/ substring matches
# "mari-COP-a" and mislabels every Maricopa County (AZ) page as Florida.

RE_OVERVIEW = re.compile(r'^(.*?)-liquor-licenses?(?:-|$)')
RE_DUP = re.compile(r'-\d+$')

# The six rows in the client's "How to Get a Liquor License" nav drawer.
# Keyed by state too: /counties/orange-county/ serves BOTH Orange County CA and Orange County
# FL, and it is the California one the nav row points at.
IN_NAV = {('state', 'california', 'CA'), ('city', 'san-francisco', 'CA'),
          ('city', 'los-angeles', 'CA'), ('city', 'san-diego', 'CA'),
          ('county', 'orange-county', 'CA'), ('county', 'ventura-county', 'CA')}

SMALL = {'of', 'and', 'the', 'for', 'in'}
FIXUP = {'st': 'St.', 'mc': 'Mc', 'us': 'US'}


def titlecase(slug):
    parts = [p for p in slug.split('-') if p]
    out = []
    for i, p in enumerate(parts):
        if p in FIXUP:
            out.append(FIXUP[p])
        elif p in SMALL and i > 0:
            out.append(p)
        else:
            out.append(p[:1].upper() + p[1:])
    return ' '.join(out)


def read_sitemaps():
    urls, per_file = [], {}
    for f in sorted(glob.glob(os.path.join(SITEMAPS, '*.xml'))):
        with open(f, encoding='utf-8', errors='replace') as fh:
            found = re.findall(r'<loc>([^<]+)</loc>', fh.read())
        per_file[os.path.basename(f)] = len(found)
        urls += found
    return urls, per_file


def states_of(leaves):
    """Which state(s) a folder's pages declare, from licence grammar alone."""
    s = set()
    for l in leaves:
        if RE_AZ.search(l):
            s.add('AZ')
        if RE_FL.search(l):
            s.add('FL')
        if RE_CA.search(l) and not RE_FL.search(l) and not RE_AZ.search(l):
            s.add('CA')
    return s


def licences_of(leaves):
    out = set()
    for l in leaves:
        for m in re.finditer(r'-type-(\d+)', l):
            out.add('type-' + m.group(1))
        for m in re.finditer(r'-series-(\d+)', l):
            out.add('series-' + m.group(1))
        for m in re.finditer(r'-(\d)(cop|ps)(?:-|$)', l):
            out.add(m.group(1) + m.group(2).upper())
    return sorted(out)


def label_of(slug, leaves):
    """Prefer the name the site itself prints, so 'orange' -> 'City of Orange'."""
    for l in leaves:
        if not l:
            continue
        m = RE_OVERVIEW.match(l)
        if m and not (RE_CA.search(l) or RE_AZ.search(l) or RE_FL.search(l)):
            raw = m.group(1)
            raw = re.sub(r'-(california|arizona|florida)$', '', raw)
            if raw:
                return titlecase(raw)
    return titlecase(slug)


def main():
    urls, per_file = read_sitemaps()
    uniq = sorted(set(urls))

    folders = {'cities': collections.defaultdict(list), 'counties': collections.defaultdict(list)}
    flat = []
    for u in uniq:
        p = re.sub(r'^https?://[^/]+', '', u).strip('/').split('/')
        if p[0] in folders and len(p) >= 2:
            folders[p[0]][p[1]].append('/'.join(p[2:]))
        else:
            flat.append('/'.join(p))

    places = []
    gaps = []
    duplicates = []

    # ---- STATES -------------------------------------------------------------------------
    STATES = [
        ('california', 'California', 'CA', '/california/', 'full',
         [f for f in flat if f.startswith('california')]),
        ('arizona', 'Arizona', 'AZ', '/arizona/', 'full',
         [f for f in flat if f.startswith('arizona')]),
        ('florida', 'Florida', 'FL', '/florida/', 'full',
         [f for f in flat if f.startswith('florida')]),
        ('new-jersey', 'New Jersey', 'NJ', '/new-jersey-liquor-license/', 'orphan',
         [f for f in flat if f.startswith('new-jersey')]),
        ('ohio', 'Ohio', 'OH', '/ohio-liquor-license/', 'orphan',
         [f for f in flat if f.startswith('ohio')]),
        ('pennsylvania', 'Pennsylvania', 'PA', '/pennsylvania-liquor-license/', 'orphan',
         [f for f in flat if f.startswith('pennsylvania')]),
    ]
    for slug, label, code, ns, depth, pages in STATES:
        flags = [] if depth == 'full' else ['orphan-no-counties-or-cities']
        places.append(dict(slug=slug, label=label, tier='state', state=[code], namespace=ns,
                           pages=len(pages), licence_types=licences_of(pages),
                           in_nav=('state', slug, code) in IN_NAV, depth=depth, flags=flags))

    # ---- COUNTIES -----------------------------------------------------------------------
    # Two pseudo-parents act as state buckets -- the ONE nesting the source actually publishes.
    bucket = {}
    for parent, code in (('arizona-county', 'AZ'), ('florida-county', 'FL')):
        for leaf in folders['counties'].get(parent, []):
            if not leaf:
                continue
            name = re.sub(r'-(arizona|florida)-liquor.*$', '', leaf)
            if RE_DUP.search(leaf):
                duplicates.append('/counties/%s/%s' % (parent, leaf))
                continue
            bucket.setdefault((name, code), []).append(leaf)

    county_rec = {}
    for slug, leaves in sorted(folders['counties'].items()):
        if slug in ('arizona-county', 'florida-county'):
            continue
        if RE_DUP.search(slug) or 'county-type' in slug:
            duplicates.append('/counties/%s/' % slug)
            continue
        st = states_of(leaves) or {'CA'}          # overview-only pages carry no grammar; all CA
        flags = []
        if len(st) > 1:
            flags.append('merged-slug-across-states')
        for code in sorted(st):
            key = (re.sub(r'-county$', '', slug), code)
            county_rec[key] = dict(
                slug=slug, label=label_of(slug, leaves), tier='county', state=[code],
                namespace='/counties/', pages=len(leaves), licence_types=licences_of(leaves),
                in_nav=('county', slug, code) in IN_NAV,
                depth='full' if licences_of(leaves) else 'overview-only', flags=list(flags))

    for (name, code), leaves in sorted(bucket.items()):
        key = (re.sub(r'-county$', '', name), code)
        if key in county_rec:
            county_rec[key]['pages'] += len(leaves)
            county_rec[key]['flags'].append('also-in-%s-bucket' % code.lower())
        else:
            county_rec[key] = dict(
                slug=name, label=label_of(name, leaves), tier='county', state=[code],
                namespace='/counties/%s-county/' % code.lower().replace('az', 'arizona').replace('fl', 'florida'),
                pages=len(leaves), licence_types=[], in_nav=False,
                depth='overview-only', flags=['in-state-bucket'])
    places += [county_rec[k] for k in sorted(county_rec)]

    # ---- CITIES -------------------------------------------------------------------------
    for slug, leaves in sorted(folders['cities'].items()):
        if 'county-type' in slug or 'county-series' in slug:
            duplicates.append('/cities/%s/' % slug)
            continue
        st = states_of(leaves) or {'CA'}
        flags = []
        if len(st) > 1:
            flags.append('merged-slug-across-states')

        real = [l for l in leaves if l]
        typed = [l for l in real if RE_CA.search(l) or RE_AZ.search(l) or RE_FL.search(l)]
        county_named = [l for l in typed if re.match(r'^%s-county-' % re.escape(slug), l)]
        tier = 'city'
        if typed and len(county_named) == len(typed) and not any(
                RE_OVERVIEW.match(l) and not re.match(r'^%s-county-' % re.escape(slug), l) for l in real):
            tier = 'county'
            flags.append('tier-mismatch-filed-as-city-all-pages-county')
        elif county_named:
            flags.append('county-named-children-under-city-folder')
        if slug == 'san-francisco':
            tier = 'city-county'
            flags.append('consolidated-city-county')
        if any(re.match(r'^(?!%s)[a-z-]+-county-' % re.escape(slug), l) for l in typed):
            flags.append('inherits-a-county-page')
        if any(RE_DUP.search(l) for l in real):
            flags.append('has-duplicate-page')

        label = label_of(slug, leaves)
        if label.lower().replace(' ', '-').replace('.', '') not in (slug, 'city-of-' + slug):
            if not label.lower().startswith('city of'):
                flags.append('slug-drift')

        for code in sorted(st):
            places.append(dict(
                slug=slug, label=label, tier=tier, state=[code], namespace='/cities/',
                pages=len(leaves), licence_types=licences_of(leaves),
                in_nav=('city', slug, code) in IN_NAV,
                depth='full' if licences_of(leaves) else 'overview-only', flags=list(flags)))

    # ---- KNOWN GAPS (verified 404 during the crawl; recorded, never silently dropped) -----
    for n in ('Alpine', 'Del Norte', 'Mariposa', 'Placer', 'Plumas', 'Trinity'):
        gaps.append(dict(name=n + ' County', state='CA', tier='county', reason='no page published'))
    gaps.append(dict(name='Washington County', state='FL', tier='county', reason='no page published'))

    counts = collections.Counter()
    for p in places:
        counts['%s:%s' % (p['state'][0], p['tier'])] += 1

    data = dict(
        source='https://liquorlicenseagents.com/',
        method='parsed from the site\'s own sitemap.xml tree; no place name is invented',
        layering='ROOT -> PLACE -> LICENCE TYPE (the source publishes /cities/ and /counties/ as '
                 'parallel namespaces; it publishes no city->county link, so none is asserted here)',
        sitemaps=per_file,
        total_urls=len(uniq),
        country=dict(name='United States', code='US'),
        counts=dict(sorted(counts.items())),
        places=places,
        gaps=gaps,
        duplicates=sorted(set(duplicates)),
    )
    with open(OUT, 'w', encoding='utf-8') as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)

    print('urls parsed          : %d' % len(uniq))
    print('places emitted       : %d' % len(places))
    for k, v in sorted(counts.items()):
        print('   %-14s %3d' % (k, v))
    print('gaps recorded        : %d' % len(gaps))
    print('duplicates excluded  : %d' % len(set(duplicates)))
    print('-> %s' % OUT)


if __name__ == '__main__':
    main()
