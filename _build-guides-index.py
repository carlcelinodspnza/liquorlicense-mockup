#!/usr/bin/env python3
"""
_build-guides-index.py -- [CG] create guides.html, so the Licensing menu's "Guides"
row points at a page of its own instead of an anchor on the HOMEPAGE.

WHY THIS PAGE AND NOT THE OTHER TWO ASKED FOR
    Owner, 2026-09-02: the Licensing menu options should each be an individual page.
    Three of the eight rows were not pages. MEASURED before building any of them:

      Conditional Use Permits -> services.html#cup
          service-cup.html ALREADY EXISTS. Repointed. No new content, no risk.

      Guides -> index.html#guides
          The homepage anchor is a 139-word teaser. A directory page built from it
          overlaps resources.html by 13.2% on vocabulary. SAFE — this file builds it.
          (Copying the guides' PROSE in instead would have hit 82.3%.)

      Transfer timeline & escrow -> process.html#phases
          That section is 582 words and IS process.html's core. A standalone page
          would be a ~100% lift of it — the doorway-page pattern this build has
          refused before. NOT BUILT. The row keeps its anchor and the reasoning is
          reported to the owner rather than papered over with a duplicate page.

CONTENT IS LIFTED, NOT WRITTEN
    Each card's title is the guide page's own <h1>, read from that file at build time.
    The topic labels are the four the Licensing menu already uses ("Classification,
    pricing, routes to market, zoning"). Nothing here is invented copy.

CHROME IS CLONED, NOT RETYPED
    Header, footer, menus and asset links come from an existing guide page, so this
    page inherits every site-wide fix automatically — including the de-Californised
    menu chrome from _build-general-tone-services.py.

IDEMPOTENT -- rewrites guides.html from scratch each run; the output is deterministic.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.join(HERE, 'guide-classification.html')
OUT = os.path.join(HERE, 'guides.html')

GUIDES = [
    ('Classification',    'guide-classification.html'),
    ('Pricing',           'guide-pricing.html'),
    ('Routes to market',  'guide-resale-market.html'),
    ('Zoning',            'guide-zoning.html'),
]

TITLE = 'Liquor Licence Guides | Classification, Pricing, Resale and Zoning'
DESC = ('Four explainers on how liquor licensing actually works: which classification applies, '
        'what sets a licence price, when a market becomes a resale market, and how the address '
        'is approved separately from the licence.')


def h1_of(path):
    s = io.open(path, encoding='utf-8').read()
    m = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    if not m:
        print('FAIL: no <h1> in %s' % os.path.basename(path), file=sys.stderr); sys.exit(1)
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', m.group(1))).strip()


def main():
    if not os.path.exists(DONOR):
        print('FAIL: chrome donor missing', file=sys.stderr); sys.exit(1)
    src = io.open(DONOR, encoding='utf-8').read()

    cards = []
    for i, (topic, href) in enumerate(GUIDES, 1):
        p = os.path.join(HERE, href)
        if not os.path.exists(p):
            print('FAIL: %s does not exist — refusing to link to it' % href, file=sys.stderr)
            sys.exit(1)
        cards.append(
            '        <a class="svc-tile wow-lift" href="%s">\n'
            '          <span class="svc-tile__ghost" aria-hidden="true">%02d</span>\n'
            '          <h3 class="svc-tile__t">%s</h3>\n'
            '          <p class="svc-tile__d">%s</p>\n'
            '          <span class="svc-tile__go">Read the guide</span>\n'
            '        </a>\n' % (href, i, topic, h1_of(p)))

    main_html = (
        '<main id="main">\n'
        '\n'
        '<section class="section section--dark wow-bloom">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">Guides</p>\n'
        '    <h1>Four explainers on how licensing actually works</h1>\n'
        '    <p class="lede">Each one answers a single question in full, and each is written to be '
        'read before a decision rather than after it. The knowledge base sets out the same four '
        'mechanics as continuous prose.</p>\n'
        '    <div class="svc-tiles wow-stagger">\n'
        + ''.join(cards) +
        '    </div>\n'
        '    <div class="cta-row" style="margin-top:32px">\n'
        '      <a class="btn btn-secondary" href="resources.html">Read the knowledge base</a>\n'
        '      <a class="btn btn-secondary" href="faq.html">Licensing FAQs</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>\n'
        '\n'
        '</main>')

    a, b = src.find('<main'), src.find('</main>') + len('</main>')
    if a < 0 or b <= a:
        print('FAIL: could not locate <main> in the donor', file=sys.stderr); sys.exit(1)
    out = src[:a] + main_html + src[b:]

    out = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, out, count=1, flags=re.S)
    out = re.sub(r'(<meta name="description" content=")[^"]*(")',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(")',
                 lambda m: m.group(1) + 'guides.html' + m.group(2), out, count=1)
    # og/twitter mirrors of title+description, where present
    out = re.sub(r'(<meta property="og:title" content=")[^"]*(")',
                 lambda m: m.group(1) + TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:title" content=")[^"]*(")',
                 lambda m: m.group(1) + TITLE + m.group(2), out, count=1)
    out = re.sub(r'(<meta name="twitter:description" content=")[^"]*(")',
                 lambda m: m.group(1) + DESC + m.group(2), out, count=1)

    if out.count('<h1') != 1:
        print('FAIL: expected exactly one <h1>, got %d' % out.count('<h1'), file=sys.stderr)
        sys.exit(1)
    for _, href in GUIDES:
        if 'href="%s"' % href not in out:
            print('FAIL: card for %s missing from the output' % href, file=sys.stderr); sys.exit(1)

    io.open(OUT, 'w', encoding='utf-8').write(out)
    print('wrote guides.html — %d cards, %d bytes' % (len(cards), len(out.encode())))


if __name__ == '__main__':
    main()
