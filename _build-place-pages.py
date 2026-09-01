#!/usr/bin/env python3
"""
_build-place-pages.py -- [BZ] the three place-level pages the county x type set cannot cover.

  palm-springs   city  — a city inside Riverside County, which has its own page set
  san-jose       city  — a city in Santa Clara County
  napa-valley    area  — an AVA; the client publishes nothing under that name at all,
                         so the content comes from their NAPA COUNTY overview page

ALL THREE SHIP noindex,follow, on measurement, not taste:
  san-jose      80.6% word-identical to the client's own San Francisco city page once place
                names are normalised; 18 of 44 sentences character-for-character identical;
                zero concrete local references
  napa-valley   zero concrete local references in 968 words; 14 of 62 sentences >=80%
                identical to the client's Fresno/Kern county pages; the words "Napa Valley"
                never appear on the source at all
  palm-springs  one concrete local name (Coachella Valley) in 854 words; 59% similar to the
                San Jose sibling; the market it describes would read identically for Scottsdale

The three JSON files were written by different agents and their shapes differ, so every
field is read defensively and a page is skipped rather than half-built if its core is absent.
"""
import io, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_geography', '_source-content')
DONOR = os.path.join(HERE, 'liquor-license-san-diego.html')

PAGES = [
    ('palm-springs.json',  'liquor-license-palm-springs.html', 'palm-springs', 'riverside',
     'Riverside County',
     'NOINDEX ON PURPOSE: the source page names ONE concrete local place (Coachella Valley) in 854 '
     'words and measures 59% similar to the client\'s San Jose city page. Palm Springs also sits '
     'inside Riverside County, which has its own five-page set here, so this page would compete '
     'with pages built from a different source. Remove this tag when real Palm Springs fact is '
     'written — named districts, the city\'s own CUP and entertainment-permit path, local pricing.'),
    ('san-jose-city.json', 'liquor-license-san-jose.html', 'san-jose', None, 'Santa Clara County',
     'NOINDEX ON PURPOSE: MEASURED at 80.6% word-identical to the client\'s own San Francisco city '
     'page once place names are normalised, with 18 of 44 sentences character-for-character '
     'identical and ZERO concrete local references in 844 words. Remove this tag when real San Jose '
     'fact is written — Santana Row, SAP Center, San Pedro Square, the city planning process.'),
    ('napa-valley.json',   'liquor-license-napa-valley.html', 'napa-valley', None, 'Napa County',
     'NOINDEX ON PURPOSE: zero concrete local references in 968 words, and 14 of 62 sentences are '
     '>=80% identical to the client\'s Fresno and Kern county pages. The source is their NAPA COUNTY '
     'overview; the client publishes nothing under the name "Napa Valley" at all. Remove this tag '
     'when real Napa Valley fact is written.'),
]


CLAIM_PATTERNS = [
    r',?\s*(?:and\s+)?with an experienced advisor',
    r'\s*with a team familiar with [^.,]+',
    r'\s*with our experienced (?:team|advisors|brokers)',
]


def esc(s):
    t = re.sub(r'\s+', ' ', str(s or '')).strip()
    for c in CLAIM_PATTERNS:
        t = re.sub(c, '', t, flags=re.I)
    t = re.sub(r'\s+([.,;])', r'\1', t)
    return html.escape(re.sub(r'\s{2,}', ' ', t).strip(), quote=False)


def paras(v):
    """intro / cta bodies arrive as a list, a dict with 'paragraphs', or a bare string."""
    if v is None:
        return []
    if isinstance(v, str):
        return [v] if v.strip() else []
    if isinstance(v, list):
        out = []
        for x in v:
            out += paras(x if not isinstance(x, dict) else (x.get('text') or x.get('body') or ''))
        return out
    if isinstance(v, dict):
        for k in ('paragraphs', 'textAfterFlaggedClaimRemoved', 'body', 'text', 'textVerbatimSource'):
            if v.get(k):
                return paras(v[k])
    return []


def faq_of(page):
    f = page.get('faqSection') or page.get('faq') or {}
    items = f.get('items') or []
    out = []
    for it in items:
        q = it.get('q') or it.get('question') or ''
        a = it.get('a') or it.get('answer') or ''
        a = a if isinstance(a, str) else ' '.join(paras(a))
        if q and a:
            out.append((q, a))
    return (f.get('heading') or 'Frequently asked questions'), out


def lists_for(page, heading):
    out = []
    for l in (page.get('lists') or []):
        if (l.get('underHeading') or '').strip().lower() == (heading or '').strip().lower():
            items = l.get('items') or []
            items = [i if isinstance(i, str) else (i.get('text') or json.dumps(i)) for i in items]
            if items:
                out.append((l.get('leadIn') or '', items))
    return out


def ul(items):
    return ('<ul class="tp-points" role="list">%s</ul>'
            % ''.join('<li>%s</li>' % esc(i) for i in items)) if items else ''


def build(d, slug, parent_tab, parent_label):
    page = d['page']
    # OUR market name, not the source's. napa-valley.json is sourced from the client's NAPA
    # COUNTY page and its h1 says "Napa County"; using it verbatim would label our Napa Valley
    # market as a county it is not. Same discipline for the other two.
    h1 = '%s liquor licences for restaurants, bars and retailers' % d['label']
    intro = paras(page.get('intro'))
    secs = page.get('sections') or []
    faq_head, faqs = faq_of(page)
    cta = page.get('cta') or {}

    bands = ['section section--warm', 'section', 'section section--dark']
    body = []
    crumb = ('<a href="locations.html">Markets</a> &rsaquo; %s' % esc(d['label']))
    body.append(
        '<section class="section hero hero--editorial section--dark wow-bloom">\n'
        '  <div class="container">\n    <p class="eyebrow">%s</p>\n    <h1>%s</h1>\n'
        '    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="locations.html#state-california">All California markets</a>\n'
        '    </div>\n  </div>\n</section>' % (crumb, esc(h1), esc(intro[0] if intro else '')))

    prov = d.get('sourceNote') or ''
    if d['market'] == 'napa-valley':
        body.append(
            '<section class="section section--warm" id="provenance">\n  <div class="container">\n'
            '    <p class="tp-note"><strong>About this market.</strong> We call this market Napa Valley. '
            'The licensing detail below is published by the state and the county as <strong>Napa County</strong> '
            '&mdash; the AVA and the county are not the same boundary, and where a rule is a county rule '
            'we have kept it labelled that way.</p>\n  </div>\n</section>')

    if len(intro) > 1:
        body.append('<section class="section section--warm" id="overview">\n  <div class="container">\n'
                    '    <p class="eyebrow">Overview</p>\n%s  </div>\n</section>'
                    % ''.join('    <p class="lede">%s</p>\n' % esc(p) for p in intro[1:]))

    for i, s in enumerate(secs):
        head = s.get('heading') or ''
        ps = paras(s.get('paragraphs') or s.get('body'))
        blocks = ''.join('    <p class="lede">%s</p>\n' % esc(p) for p in ps)
        for lead, items in lists_for(page, head):
            if lead:
                blocks += '    <p class="lede">%s</p>\n' % esc(lead)
            blocks += '    %s\n' % ul(items)
        body.append('<section class="%s" id="s%d">\n  <div class="container">\n    <h2>%s</h2>\n%s  </div>\n</section>'
                    % (bands[i % len(bands)], i + 1, esc(head), blocks))

    if faqs:
        items = ''.join('      <details class="faq-item">\n        <summary class="faq-item__q">%s</summary>\n'
                        '        <div class="faq-item__a">%s</div>\n      </details>\n' % (esc(q), esc(a))
                        for q, a in faqs)
        body.append('<section class="section" id="faqs">\n  <div class="container">\n'
                    '    <p class="eyebrow">Asked most</p>\n    <h2>%s</h2>\n'
                    '    <div class="faq__list">\n%s    </div>\n  </div>\n</section>'
                    % (esc(faq_head), items))

    ctap = paras(cta)
    body.append('<section class="section closing-cta" id="next">\n  <div class="container">\n'
                '    <h2>%s</h2>\n    <p class="lede">%s</p>\n'
                '    <div class="cta-row">\n'
                '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
                '      <a class="btn btn-secondary" href="inventory.html">Open the inventory board</a>\n'
                '    </div>\n  </div>\n</section>'
                % (esc(cta.get('heading') or 'Talk to a broker'),
                   esc(ctap[0] if ctap else 'Tell us the classification and the market you are working to.')))
    return '\n\n'.join(body)


def main():
    donor = io.open(DONOR, encoding='utf-8').read()
    pre = donor[:donor.index('<main id="main">') + len('<main id="main">')]
    post = donor[donor.index('</main>'):]
    n = 0
    for fname, slug, market, parent_tab, parent_label, why in PAGES:
        p = os.path.join(SRC, fname)
        if not os.path.exists(p):
            print('  MISSING source %s -- page not written' % fname)
            continue
        d = json.load(io.open(p, encoding='utf-8'))
        if 'page' not in d:
            print('  %s has no "page" object -- skipped' % fname)
            continue
        body = build(d, slug, parent_tab, parent_label)
        pg = d['page']
        title = '%s Liquor Licence | Buy, Sell, Transfer' % d['label']
        desc = re.sub(r'\s+', ' ', pg.get('metaDescription') or '').strip()[:158]
        head = re.sub(r'<title>.*?</title>', '<title>%s | ABC Licence Brokers</title>' % esc(title), pre, count=1, flags=re.S)
        head = re.sub(r'<meta name="description" content="[^"]*">',
                      '<meta name="description" content="%s">' % html.escape(desc, quote=True), head, count=1)
        head = re.sub(r'<link rel="canonical" href="[^"]*">',
                      '<link rel="canonical" href="%s">' % slug, head, count=1)
        head = head.replace('<link rel="canonical"',
                            '<meta name="robots" content="noindex,follow">\n<!-- %s -->\n<link rel="canonical"' % why, 1)
        head = re.sub(r'(<script type="application/ld\+json">\s*\{\s*"@context"[^<]*?"@type": "Service".*?</script>)',
                      ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n'
                       '  "@type": "Service",\n  "name": "California ABC liquor licence brokerage in %s",\n'
                       '  "serviceType": "California ABC liquor licence brokerage",\n'
                       '  "areaServed": { "@type": "AdministrativeArea", "name": "%s" },\n'
                       '  "provider": { "@type": "ProfessionalService", "name": "Liquor License Agents" }\n}\n</script>')
                      % (d['label'], d['label']), head, count=1, flags=re.S)
        io.open(os.path.join(HERE, slug), 'w', encoding='utf-8').write(head + '\n\n' + body + '\n\n' + post)
        print('  wrote %-38s (noindex)' % slug)
        n += 1
    print('place-level pages written: %d' % n)


if __name__ == '__main__':
    main()
