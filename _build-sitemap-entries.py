#!/usr/bin/env python3
"""
_build-sitemap-entries.py -- [CA] record the new pages in sitemap.yaml.

sitemap.yaml is this build's page manifest: every page kind has a block, and every entry
carries `indexable`, which is how the noindex decisions stay auditable. The 56 pages added
this session (50 market x type, 6 state, plus the 3 place-level pages whose kind changed)
were not in it, so the manifest no longer described the site.

Indexability is READ FROM THE PAGES THEMSELVES, not re-derived — the file must agree with
what actually shipped, and deriving it twice is how the two drift apart.

IDEMPOTENT -- rewrites only between its own sentinels.
"""
import io, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SM = os.path.join(HERE, 'sitemap.yaml')

TYPE_NAME = {'20': 'Off-Sale Beer & Wine', '21': 'Off-Sale General',
             '41': 'On-Sale Beer & Wine, Eating Place', '47': 'On-Sale General, Eating Place',
             '48': 'On-Sale General, Public Premises'}
MARKET_LABEL = {
    'los-angeles': 'Los Angeles County', 'orange': 'Orange County', 'riverside': 'Riverside County',
    'sacramento': 'Sacramento County', 'san-bernardino': 'San Bernardino County',
    'san-diego': 'San Diego County', 'san-francisco': 'San Francisco County',
    'fresno': 'Fresno County', 'santa-barbara': 'Santa Barbara County', 'ventura': 'Ventura County',
}
STATE_PAGES = [
    ('california-liquor-license-services', 'California', 'state services'),
    ('arizona-liquor-license', 'Arizona', 'state'),
    ('florida-liquor-license', 'Florida', 'state'),
    ('new-jersey-liquor-license', 'New Jersey', 'state'),
    ('ohio-liquor-license', 'Ohio', 'state'),
    ('pennsylvania-liquor-license', 'Pennsylvania', 'state'),
]
PLACE_PAGES = [('liquor-license-palm-springs', 'Palm Springs', 'city'),
               ('liquor-license-san-jose', 'San Jose', 'city'),
               ('liquor-license-napa-valley', 'Napa Valley', 'area')]


def indexable(slug):
    """Read it off the shipped page. Never re-derive."""
    p = os.path.join(HERE, slug + '.html')
    if not os.path.exists(p):
        return None
    return 'name="robots" content="noindex' not in io.open(p, encoding='utf-8').read()


def block():
    L = []
    L.append('# ---- ADDED THIS SESSION. Regenerate with _build-sitemap-entries.py ----------')
    L.append('# indexable is read from each shipped page, not re-derived, so this file cannot')
    L.append('# drift from what actually has a robots tag.')
    L.append('')
    L.append('state_pages:')
    for slug, label, kind in STATE_PAGES:
        ix = indexable(slug)
        note = '' if ix else \
            "   # noindex: source states California licence law on a non-California state" \
            if kind == 'state' else ''
        L.append('  - { slug: %s, kind: %s, state: "%s", indexable: %s }%s'
                 % (slug, kind.replace(' ', '_'), label, str(ix).lower(), note))
    L.append('')
    L.append('market_type_pages:')
    L.append('  # 50 pages: 10 county markets x ABC Types 20/21/41/47/48. Content extracted')
    L.append('  # verbatim from the client\'s own per-type pages. 11 ship noindex because their')
    L.append('  # source names no concrete local place -- see the inline reason on each page.')
    for slug in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        b = os.path.basename(slug)[:-5]
        m = re.match(r'liquor-license-(.+)-type-(\d+)$', b)
        mk, ty = m.group(1), m.group(2)
        L.append('  - { slug: %s, kind: market_type, market: "%s", type: %s, name: "%s", indexable: %s }'
                 % (b, MARKET_LABEL.get(mk, mk), ty, TYPE_NAME[ty], str(indexable(b)).lower()))
    L.append('')
    L.append('place_pages:')
    L.append('  # these three REPLACED their former market_pages entries: the client publishes no')
    L.append('  # licence-type pages for them, so they carry a place-level page instead.')
    for slug, label, kind in PLACE_PAGES:
        L.append('  - { slug: %s, kind: %s, place: "%s", indexable: %s }'
                 % (slug, kind, label, str(indexable(slug)).lower()))
    return '\n'.join(L)


def main():
    s = io.open(SM, encoding='utf-8').read()
    B, E = '# <<< SESSION-PAGES:BEGIN >>>', '# <<< SESSION-PAGES:END >>>'
    payload = '%s\n%s\n%s' % (B, block(), E)
    if B in s:
        s = re.sub(re.escape(B) + r'.*?' + re.escape(E), payload, s, flags=re.S)
    else:
        s = s.rstrip('\n') + '\n\n' + payload + '\n'
    io.open(SM, 'w', encoding='utf-8').write(s)
    n_t = len(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html')))
    print('sitemap.yaml: %d state + %d market_type + %d place entries recorded'
          % (len(STATE_PAGES), n_t, len(PLACE_PAGES)))


if __name__ == '__main__':
    main()
