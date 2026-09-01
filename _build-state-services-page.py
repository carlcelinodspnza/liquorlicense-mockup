#!/usr/bin/env python3
"""
_build-state-services-page.py -- [BZ] the California state services page.

LAYOUT (owner choice): OUR section stack, THEIR content. Their page is heading-and-paragraph
throughout with no table, list, FAQ or in-body link, so it reads flat beside our other pages;
this carries their four service themes into components we already have.

THREE SOURCE DEFECTS NOT REPRODUCED
  1. The source has NO <h1> at all and runs H2 -> H4 with H3 skipped. Ours has a real h1.
  2. Its Brokerage block ends "...assistance in the following areas of liquor licensing:" and
     then delivers nothing -- 46 of its 52 <p> tags are empty. We supply that list from our
     own service pages, which exist, rather than reproducing a colon with no list.
  3. Four unverifiable firm claims are excluded, listed in the JSON's firmClaimsFlagged.

CLAIM OWNERSHIP: the five classifications are NAMED and LINKED, never defined. C18-C20 belong
to licence-types.html. C33 (statewide / 58 counties) belongs to locations.html, so the coverage
band here is a one-line summary that routes through, the same demotion index.html#coverage uses.
"""
import io, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_geography', '_source-content', 'california-services.json')
DONOR = os.path.join(HERE, 'liquor-license-san-diego.html')
SLUG = 'california-liquor-license-services.html'

# the eight services that DO exist here — this is the list their page promises and never gives
SERVICES = [
    ('01', 'Buy a licence', 'Off-market, LOI to ABC issuance', 'service-buy.html'),
    ('02', 'Sell a licence', 'Pre-qualified buyers, secure escrow', 'service-sell.html'),
    ('03', 'Transfer a licence', 'Person and premises transfers', 'service-transfer.html'),
    ('04', 'Licence valuation', 'Appraisals from closed transactions', 'service-valuation.html'),
    ('05', 'Conditional Use Permits', 'Zoning, police permits, hearings', 'service-cup.html'),
    ('06', 'ABC compliance', 'Audits and LEAD training', 'service-compliance.html'),
    ('07', 'Escrow guidance', 'Statutory notices, disbursements', 'service-escrow.html'),
    ('08', 'New business planning', 'Strategy before you sign a site', 'service-new-business.html'),
]
TYPES = [('20', 'Off-Sale Beer &amp; Wine'), ('21', 'Off-Sale General'),
         ('41', 'On-Sale Beer &amp; Wine, Eating Place'), ('47', 'On-Sale General, Eating Place'),
         ('48', 'On-Sale General, Public Premises')]


def esc(s):
    return html.escape(re.sub(r'\s+', ' ', str(s or '')).strip(), quote=False)


def main():
    d = json.load(io.open(SRC, encoding='utf-8'))
    secs = {s['heading'].lower(): s for s in d['sections']}

    def para(name, n=0):
        s = secs.get(name.lower())
        if not s or len(s['paragraphs']) <= n:
            return ''
        return s['paragraphs'][n]

    intro = para('california liquor license services')
    body = []

    body.append(
        '<section class="section hero hero--editorial section--dark wow-bloom">\n  <div class="container">\n'
        '    <p class="eyebrow"><a href="locations.html">Markets</a> &rsaquo; California</p>\n'
        '    <h1>California liquor licence services</h1>\n'
        '    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="inventory.html">Open the inventory board</a>\n'
        '    </div>\n  </div>\n</section>' % esc(intro))

    # SERVICES — [CB] split: copy left, the eight services in the space the old
    # full-width .doc-list left empty. 1410px -> 582px, measured at 1440.
    # card structure mirrors the Licensing dropdown's preview pane: a clipped numeral
    # watermark behind, copy anchored to the bottom, a gradient arrow as the affordance.
    items = ''.join(
        '        <a class="svc-card" href="%s">'
        '<span class="svc-card__mark" aria-hidden="true">%s</span>'
        '<span class="svc-card__t">%s</span>'
        '<span class="svc-card__d">%s</span>'
        '<span class="svc-card__go" aria-hidden="true">&rarr;</span></a>\n' % (h, n, t, k)
        for n, t, k, h in SERVICES)
    body.append(
        '<section class="section section--warm" id="services">\n  <div class="container">\n'
        '    <div class="svc-split">\n'
        '      <div class="svc-split__copy">\n'
        '        <p class="eyebrow">What we handle</p>\n        <h2>Brokerage</h2>\n'
        '        <p class="lede">%s</p>\n'
        '        <p class="tp-note">The client\'s own page promises &ldquo;assistance in the following '
        'areas of liquor licensing&rdquo; and then lists nothing. These are the eight it should name.</p>\n'
        '        <a class="btn btn-secondary" href="services.html">All services</a>\n'
        '      </div>\n'
        '      <div class="svc-grid">\n%s      </div>\n'
        '    </div>\n  </div>\n</section>'
        % (esc(para('brokerage')), items))

    body.append(
        '<section class="section" id="qualification">\n  <div class="container">\n'
        '    <p class="eyebrow">Before it changes hands</p>\n    <h2>Qualification</h2>\n'
        '    <p class="lede">%s</p>\n  </div>\n</section>' % esc(para('qualification')))

    body.append(
        '<section class="section section--dark" id="consulting">\n  <div class="container">\n'
        '    <p class="eyebrow">After the licence issues</p>\n    <h2>Consulting</h2>\n'
        '    <p class="lede">%s</p>\n    <p class="lede">%s</p>\n  </div>\n</section>'
        % (esc(para('consulting')), esc(para('consulting', 1))))

    body.append(
        '<section class="section" id="corporate">\n  <div class="container">\n'
        '    <p class="eyebrow">Entity work</p>\n    <h2>Corporate applications</h2>\n'
        '    <p class="lede">%s</p>\n  </div>\n</section>' % esc(para('corporate applications')))

    # classifications NAMED and LINKED only — C18-C20 belong to licence-types.html
    rows = ''.join('<li><a href="licence-type-%s.html"><strong>Type %s</strong> &mdash; %s</a></li>'
                   % (n, n, t) for n, t in TYPES)
    body.append(
        '<section class="section section--warm" id="classifications">\n  <div class="container">\n'
        '    <p class="eyebrow">By classification</p>\n    <h2>The five we are asked for most</h2>\n'
        '    <ul class="tp-points" role="list">%s</ul>\n'
        '    <p class="tp-note">What each classification authorises is set out on the '
        '<a href="licence-types.html">classifications page</a>, which owns those definitions.</p>\n'
        '  </div>\n</section>' % rows)

    body.append(
        '<section class="section section--dark" id="where">\n  <div class="container">\n'
        '    <p class="eyebrow">Coverage</p>\n    <h2>Where we broker in California</h2>\n'
        '    <p class="lede">Thirteen named markets and a statewide desk. The market list, market by '
        'market, is on the coverage page.</p>\n'
        '    <div class="cta-row"><a class="btn btn-secondary" href="locations.html#state-california">'
        'See every market we cover</a></div>\n  </div>\n</section>')

    body.append(
        '<section class="section closing-cta" id="next">\n  <div class="container">\n'
        '    <h2>%s</h2>\n    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="process.html">How a transfer runs</a>\n'
        '    </div>\n  </div>\n</section>'
        % (esc(secs.get('don’t wait! contact us today!', {}).get('heading', 'Talk to a broker')),
           esc(para('don’t wait! contact us today!'))))

    donor = io.open(DONOR, encoding='utf-8').read()
    pre = donor[:donor.index('<main id="main">') + len('<main id="main">')]
    post = donor[donor.index('</main>'):]
    head = re.sub(r'<title>.*?</title>',
                  '<title>California Liquor Licence Services | Brokerage &amp; Consulting</title>',
                  pre, count=1, flags=re.S)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Brokerage, qualification, consulting and corporate '
                  'applications for California ABC liquor licences, across thirteen named markets and a '
                  'statewide desk.">', head, count=1)
    head = re.sub(r'<link rel="canonical" href="[^"]*">',
                  '<link rel="canonical" href="%s">' % SLUG, head, count=1)
    head = re.sub(r'(<script type="application/ld\+json">\s*\{\s*"@context"[^<]*?"@type": "Service".*?</script>)',
                  ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n'
                   '  "@type": "Service",\n  "name": "California liquor licence brokerage services",\n'
                   '  "serviceType": "California ABC liquor licence brokerage",\n'
                   '  "areaServed": { "@type": "State", "name": "California" },\n'
                   '  "provider": { "@type": "ProfessionalService", "name": "Liquor License Agents" }\n}\n</script>'),
                  head, count=1, flags=re.S)
    io.open(os.path.join(HERE, SLUG), 'w', encoding='utf-8').write(head + '\n\n' + '\n\n'.join(body) + '\n\n' + post)
    words = sum(len(p.split()) for s in d['sections'] for p in s['paragraphs'])
    print('wrote %s  (%d source words carried, %d firm claims excluded)'
          % (SLUG, words, len(d['firmClaimsFlagged'])))


if __name__ == '__main__':
    main()
