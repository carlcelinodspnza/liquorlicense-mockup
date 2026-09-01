#!/usr/bin/env python3
"""
_build-state-pages.py -- [CA] one real page per state, so every Locations menu option
lands on a page instead of an anchor into locations.html.

  arizona-liquor-license.html       built from the client's published GEOGRAPHY
  florida-liquor-license.html       (counties, cities, classification names) -- they
                                    publish no state page for either; /arizona and
                                    /florida are 28-35 word archive hubs and
                                    /arizona/arizona-liquor-license/ 301s to Phoenix.
  new-jersey-liquor-license.html    from their real state pages, MINUS the California
  ohio-liquor-license.html          sections -- see below.
  pennsylvania-liquor-license.html
  (california already has california-liquor-license-services.html)

WHY NJ / OH / PA DROP 27-41% OF THEIR SOURCE
    Their New Jersey, Ohio and Pennsylvania pages each carry "Type 20 & 21", "Type 41 &
    47" and "Type 48" sections. Those are CALIFORNIA ABC classifications. New Jersey
    issues plenary retail consumption licences, Ohio uses D-1..D-8, Pennsylvania uses
    R/H/E. MEASURED: those sections are 100.0% word-identical across all three states
    (the same 193 words), and they are 27-41% of each page. Reproducing them would put
    factually wrong licence law on three state pages, so they are dropped entirely and
    replaced with a plain statement of who actually regulates that state.

    What remains is still near-duplicate -- NJ vs OH measures 95.8% word-identical -- so
    all three ship noindex,follow with that number in the markup.
"""
import io, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_geography', '_source-content')
DONOR = os.path.join(HERE, 'liquor-license-san-diego.html')
GEO = json.load(io.open(os.path.join(HERE, '_geography', 'geography.json'), encoding='utf-8'))

STATES = [
    dict(slug='arizona', label='Arizona', code='AZ', file='arizona-liquor-license.html',
         reg='the Arizona Department of Liquor Licenses and Control',
         classes='Series 6, 7, 9, 10, 11 and 12', src=None, index=True),
    dict(slug='florida', label='Florida', code='FL', file='florida-liquor-license.html',
         reg='the Florida Division of Alcoholic Beverages and Tobacco',
         classes='1COP, 2COP, 3PS, 4COP and 6COP', src='state-florida-cop.json', index=True),
    dict(slug='new-jersey', label='New Jersey', code='NJ', file='new-jersey-liquor-license.html',
         reg='the New Jersey Division of Alcoholic Beverage Control',
         classes=None, src='state-new-jersey.json', index=False),
    dict(slug='ohio', label='Ohio', code='OH', file='ohio-liquor-license.html',
         reg='the Ohio Division of Liquor Control',
         classes=None, src='state-ohio.json', index=False),
    dict(slug='pennsylvania', label='Pennsylvania', code='PA', file='pennsylvania-liquor-license.html',
         reg='the Pennsylvania Liquor Control Board',
         classes=None, src='state-pennsylvania.json', index=False),
]

NOINDEX_WHY = ('NOINDEX ON PURPOSE: the client\'s source page for this state devotes 27-41%% of its '
               'body to CALIFORNIA licence classifications (Type 20/21/41/47/48), which are 100.0%% '
               'word-identical across their New Jersey, Ohio and Pennsylvania pages. Those sections '
               'are dropped here because they state the wrong state\'s licence law. What remains is '
               'still near-duplicate -- New Jersey and Ohio measure 95.8%% word-identical. Remove '
               'this tag when real %s licensing content is written.')


def esc(s):
    return html.escape(re.sub(r'\s+', ' ', str(s or '')).strip(), quote=False)


def places(code, tier):
    out = [p for p in GEO['places'] if code in p['state'] and p['tier'] == tier]
    if tier == 'county':
        out = [p for p in out if p['namespace'].startswith('/counties/')]
    return sorted({p['label'] for p in out})


def geo_cols(code):
    cs, ct = places(code, 'county'), places(code, 'city')
    def col(title, items):
        return ('<section class="loc-geo__col"><h4>%s <span class="loc-geo__n">%d</span></h4>'
                '<ul class="loc-geo__list" role="list">%s</ul></section>'
                % (title, len(items), ''.join('<li><span class="loc-geo__name">%s</span></li>'
                                              % esc(i) for i in items)))
    return '<div class="loc-geo">%s%s</div>' % (col('Counties', cs), col('Cities', ct))


def build(st):
    label, code = st['label'], st['code']
    nc, nci = len(places(code, 'county')), len(places(code, 'city'))
    body = []
    lede = ('%d counties and %d cities are published for %s, licensed through %s.'
            % (nc, nci, label, st['reg'])) if nc else \
           ('We broker liquor licences in %s, licensed through %s.' % (label, st['reg']))
    body.append(
        '<section class="section hero hero--editorial section--dark wow-bloom">\n  <div class="container">\n'
        '    <p class="eyebrow"><a href="locations.html">Markets</a> &rsaquo; %s</p>\n'
        '    <h1>%s liquor licences</h1>\n    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="locations.html#state-%s">All markets we cover</a>\n'
        '    </div>\n  </div>\n</section>' % (esc(label), esc(label), esc(lede), st['slug']))

    body.append(
        '<section class="section section--warm" id="stock">\n  <div class="container">\n'
        '    <p class="loc-empty"><b>No live listings in %s today.</b> Every licence on our board '
        'right now is Californian. That is a stock position, not a coverage gap &mdash; tell us the '
        'classification and the market you are working to and we go looking off-market against it.</p>\n'
        '  </div>\n</section>' % esc(label))

    if nc:
        body.append(
            '<section class="section" id="markets">\n  <div class="container">\n'
            '    <p class="eyebrow">Where we broker</p>\n    <h2>Counties and cities in %s</h2>\n'
            '    %s\n  </div>\n</section>' % (esc(label), geo_cols(code)))

    # classifications: NAMED only, never defined — we hold no sourced definition for these
    cls = ('<section class="section section--dark" id="classifications">\n  <div class="container">\n'
           '    <p class="eyebrow">Classifications</p>\n    <h2>What %s issues</h2>\n'
           '    <p class="lede">%s issues %s. We name them; what each authorises is set by the state, '
           'not by us &mdash; ask and we will put it in writing for your premises.</p>\n'
           '  </div>\n</section>')
    if st['classes']:
        body.append(cls % (esc(label), st['reg'][0].upper() + st['reg'][1:], st['classes']))
    else:
        body.append(
            '<section class="section section--dark" id="classifications">\n  <div class="container">\n'
            '    <p class="eyebrow">Classifications</p>\n    <h2>What %s issues</h2>\n'
            '    <p class="lede">%s sets the classifications in %s, and they are not California\'s. '
            'We have no sourced list of them, so none is published here rather than repeating a '
            'numbering system that does not apply in this state.</p>\n  </div>\n</section>'
            % (esc(label), st['reg'][0].upper() + st['reg'][1:], esc(label)))

    # whatever genuinely state-specific prose the source had, minus the California sections
    if st['src'] and os.path.exists(os.path.join(SRC, st['src'])):
        d = json.load(io.open(os.path.join(SRC, st['src']), encoding='utf-8'))
        keep = [s for s in d['sections'] if 'Type' not in s['heading']]
        for s in keep:
            body.append(
                '<section class="section" id="about-%s">\n  <div class="container">\n'
                '    <h2>%s</h2>\n%s  </div>\n</section>'
                % (st['slug'], esc(s['heading'].title() if s['heading'].isupper() else s['heading']),
                   ''.join('    <p class="lede">%s</p>\n' % esc(p) for p in s['paragraphs'])))

    body.append(
        '<section class="section closing-cta" id="next">\n  <div class="container">\n'
        '    <h2>Tell us the market and the classification</h2>\n'
        '    <p class="lede">We broker in %s. Send the specifics and we will answer on what is '
        'actually available.</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="inventory.html">Open the inventory board</a>\n'
        '    </div>\n  </div>\n</section>' % esc(label))
    return '\n\n'.join(body)


def main():
    donor = io.open(DONOR, encoding='utf-8').read()
    pre = donor[:donor.index('<main id="main">') + len('<main id="main">')]
    post = donor[donor.index('</main>'):]
    for st in STATES:
        head = re.sub(r'<title>.*?</title>',
                      '<title>%s Liquor Licences | ABC Licence Brokers</title>' % esc(st['label']),
                      pre, count=1, flags=re.S)
        nc, nci = len(places(st['code'], 'county')), len(places(st['code'], 'city'))
        desc = ('Buy, sell and transfer liquor licences in %s. %s' %
                (st['label'], ('%d counties and %d cities we broker in.' % (nc, nci)) if nc
                 else 'Tell us the town and the licence you need.'))
        head = re.sub(r'<meta name="description" content="[^"]*">',
                      '<meta name="description" content="%s">' % html.escape(desc, quote=True), head, count=1)
        head = re.sub(r'<link rel="canonical" href="[^"]*">',
                      '<link rel="canonical" href="%s">' % st['file'], head, count=1)
        if not st['index']:
            head = head.replace('<link rel="canonical"',
                                '<meta name="robots" content="noindex,follow">\n<!-- %s -->\n<link rel="canonical"'
                                % (NOINDEX_WHY % st['label']), 1)
        head = re.sub(r'(<script type="application/ld\+json">\s*\{\s*"@context"[^<]*?"@type": "Service".*?</script>)',
                      ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n'
                       '  "@type": "Service",\n  "name": "Liquor licence brokerage in %s",\n'
                       '  "serviceType": "Liquor licence brokerage",\n'
                       '  "areaServed": { "@type": "State", "name": "%s" },\n'
                       '  "provider": { "@type": "ProfessionalService", "name": "Liquor License Agents" }\n}\n</script>')
                      % (st['label'], st['label']), head, count=1, flags=re.S)
        io.open(os.path.join(HERE, st['file']), 'w', encoding='utf-8').write(head + '\n\n' + build(st) + '\n\n' + post)
        print('  %-34s %-9s %d counties %d cities' % (st['file'], 'noindex' if not st['index'] else 'indexable', nc, nci))
    print('state pages written: %d' % len(STATES))


if __name__ == '__main__':
    main()
