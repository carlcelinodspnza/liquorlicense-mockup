#!/usr/bin/env python3
"""
_build-type-pages.py -- [BZ] generate the 50 market x licence-type pages.

LAYOUT (owner choice): mirror the client's own seven-section template, rebuilt in our
design system. Their order, our chrome, our band rhythm.

CONTENT: extracted verbatim from the client's live pages into
_geography/_source-content/<market>.json by the extraction workflow. Nothing here is
invented -- if a field is missing the page is not written.

INDEXABILITY is decided by MEASURED local content, not by taste. The extraction scored
every page for concrete local references. Markets whose pages name no real place get
noindex,follow with the reason inline -- the same convention already carried by the six
no-stock market pages ("noindex until stock or sourced local content"). The measurement
that justifies it: the highest-overlap pair in the sampled set was san-diego-type-20 vs
los-angeles-type-20 at 48%, and both scored NONE for local content.

CHROME comes from liquor-license-san-diego.html: everything outside <main> is copied
verbatim, so the header, drawer, footer and mega menus stay identical site-wide and any
future header change re-stamps through the existing menu scripts.
"""
import io, json, os, re, html

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_geography', '_source-content')
DONOR = os.path.join(HERE, 'liquor-license-san-diego.html')

TYPES = ['20', '21', '41', '47', '48']
TYPE_NAME = {
    '20': 'Off-Sale Beer &amp; Wine',
    '21': 'Off-Sale General',
    '41': 'On-Sale Beer &amp; Wine, Eating Place',
    '47': 'On-Sale General, Eating Place',
    '48': 'On-Sale General, Public Premises',
}
# markets whose extracted pages scored NONE for concrete local references
NOINDEX = {('los-angeles', t) for t in TYPES} | {('san-diego', t) for t in TYPES} | {('orange', '21')}
NOINDEX_WHY = ('NOINDEX ON PURPOSE: the source content for this market names no concrete local place '
               '(no neighbourhood, district or landmark), so this page carries nothing that '
               'distinguishes it from the same classification in another market. MEASURED: the '
               'highest-overlap pair in the sampled set was san-diego-type-20 vs los-angeles-type-20 '
               'at 48% vocabulary overlap, and both scored NONE for local content. Remove this tag '
               'the moment real sourced local content is written for this market.')

MARKET_TAB = {  # market slug -> the locations.html tab it belongs to
    'los-angeles': 'los-angeles', 'orange': 'orange', 'riverside': 'riverside',
    'sacramento': 'sacramento', 'san-bernardino': 'san-bernardino', 'san-diego': 'san-diego',
    'san-francisco': 'san-francisco', 'fresno': 'fresno', 'santa-barbara': 'santa-barbara',
    'ventura': 'ventura',
}


# Unverifiable claims about this firm's people. Stripped HERE rather than trusting the
# extraction, because the agents applied it inconsistently -- 3 of 11 removed
# "with an experienced advisor", the other 8 did not, and it reached 34 of 50 pages.
CLAIM_PATTERNS = [
    r',?\s*(?:and\s+)?with an experienced advisor',
    r'\s*and engaging experienced representation',
    r'Engaging experienced representation early is the best way to\s*',
    r'\s*with a team familiar with [^.,]+',
    r'\s*with our experienced (?:team|advisors|brokers)',
]


def strip_claims(t):
    if not t:
        return t
    for c in CLAIM_PATTERNS:
        t = re.sub(c, '', t, flags=re.I)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'\s+([.,;])', r'\1', t)
    t = re.sub(r'\b([Ss]tarting early)\s+is the best way', r'\1 helps', t)
    return t.strip()


def esc(s):
    return html.escape(strip_claims(str(s or '')), quote=False)


def clean_title(h1, label, ty):
    """Their titles repeat themselves: 'X Type 47 Full On-Sale... - X Type 47 License'."""
    t = re.sub(r'\s*[-–—]\s*%s Type %s License\s*$' % (re.escape(label), ty), '', h1).strip()
    return t


def para(text):
    """Their body fields sometimes carry '•' bullets inline; split those out."""
    out = []
    for chunk in re.split(r'\s*•\s*', text or ''):
        c = chunk.strip()
        if c:
            out.append(c)
    return out


def bullets(sec):
    b = sec.get('bullets')
    if b:
        return b
    parts = para(sec.get('body', ''))
    return parts[1:] if len(parts) > 1 else []


def lead_of(sec):
    if sec.get('lead'):
        return sec['lead']
    parts = para(sec.get('body', ''))
    return parts[0] if parts else ''


def ul(items):
    if not items:
        return ''
    return ('<ul class="tp-points" role="list">%s</ul>' %
            ''.join('<li>%s</li>' % esc(i) for i in items))


def body_for(market, label, ty, t):
    tab = MARKET_TAB.get(market, market)
    h1 = clean_title(t['h1'], label, ty)
    intro = esc(t['intro'])
    a, rf, hw = t['authorizes'], t['rightFor'], t['howWeHelp']
    faqs = t['faqs']
    cta = t['cta']
    local = t.get('localNames') or []

    s = []
    s.append(
        '<section class="section hero hero--editorial section--dark wow-bloom">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow"><a href="locations.html">Markets</a> &rsaquo; '
        '<a href="liquor-license-%s.html">%s</a> &rsaquo; Type %s</p>\n'
        '    <h1>%s</h1>\n'
        '    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="licence-types.html#type-%s">What a Type %s authorises</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>' % (tab, esc(label), ty, esc(h1), intro, ty, ty))

    s.append(
        '<section class="section section--warm" id="authorizes">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">What it permits</p>\n'
        '    <h2>%s</h2>\n'
        '    <p class="lede">%s</p>\n'
        '    %s\n'
        '    <p class="tp-note">The full ABC authorisation wording for every classification is on the '
        '<a href="licence-types.html#type-%s">classifications page</a>.</p>\n'
        '  </div>\n'
        '</section>' % (esc(a['heading']), esc(a['lead']), ul(a['bullets']), ty))

    s.append(
        '<section class="section" id="fit">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">Is it the right one</p>\n'
        '    <h2>%s</h2>\n'
        '    <p class="lede">%s</p>\n'
        '    %s\n'
        '  </div>\n'
        '</section>' % (esc(rf['heading']), esc(lead_of(rf)), ul(bullets(rf))))

    closing = hw.get('closing', '')
    s.append(
        '<section class="section section--dark" id="how">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">How we work it</p>\n'
        '    <h2>%s</h2>\n'
        '    <p class="lede">%s</p>\n'
        '    %s\n'
        '    %s\n'
        '  </div>\n'
        '</section>' % (esc(hw['heading']), esc(lead_of(hw)), ul(bullets(hw)),
                        ('<p class="tp-note">%s</p>' % esc(closing)) if closing else ''))

    items = ''.join(
        '      <details class="faq-item">\n'
        '        <summary class="faq-item__q">%s</summary>\n'
        '        <div class="faq-item__a">%s</div>\n'
        '      </details>\n' % (esc(f['q']), esc(f['a'])) for f in faqs)
    s.append(
        '<section class="section" id="faqs">\n'
        '  <div class="container">\n'
        '    <p class="eyebrow">Asked most</p>\n'
        '    <h2>%s</h2>\n'
        '    <div class="faq__list">\n%s    </div>\n'
        '    <p class="tp-note">Broader questions &mdash; cost, timelines, city approval &mdash; are '
        'answered on the <a href="faq.html">FAQ page</a>.</p>\n'
        '  </div>\n'
        '</section>' % (esc(t.get('faqHeading') or ('%s Type %s FAQs' % (label, ty))), items))

    s.append(
        '<section class="section closing-cta" id="next">\n'
        '  <div class="container">\n'
        '    <h2>%s</h2>\n'
        '    <p class="lede">%s</p>\n'
        '    <div class="cta-row">\n'
        '      <a class="btn btn-primary wow-glow" href="contact.html">Talk to a broker</a>\n'
        '      <a class="btn btn-secondary" href="liquor-license-%s.html">Everything we broker in %s</a>\n'
        '    </div>\n'
        '  </div>\n'
        '</section>' % (esc(cta['heading']), esc(cta['body']), tab, esc(label)))

    return '\n\n'.join(s), h1, local


def main():
    donor = io.open(DONOR, encoding='utf-8').read()
    pre = donor[:donor.index('<main id="main">') + len('<main id="main">')]
    post = donor[donor.index('</main>'):]

    written = idx = noidx = 0
    for f in sorted(os.listdir(SRC)):
        if not f.endswith('.json'):
            continue
        d = json.load(io.open(os.path.join(SRC, f), encoding='utf-8'))
        if 'types' not in d:
            continue
        market, label = d['market'], d['label']
        if market not in MARKET_TAB:
            print('  skip %s (not one of the ten county markets)' % market)
            continue
        for ty in TYPES:
            t = d['types'].get(ty)
            if not t:
                print('  MISSING %s type %s -- not written' % (market, ty))
                continue
            body, h1, local = body_for(market, label, ty, t)
            head = pre
            title = '%s | ABC Licence Brokers' % clean_title(t['h1'], label, ty)
            if len(title) > 70:
                title = '%s Type %s Licence | ABC Licence Brokers' % (label, ty)
            desc = re.sub(r'\s+', ' ', t['metaDescription'] or t['intro']).strip()
            if len(desc) > 158:
                desc = desc[:155].rsplit(' ', 1)[0] + '…'
            slug = 'liquor-license-%s-type-%s.html' % (market, ty)

            head = re.sub(r'<title>.*?</title>', '<title>%s</title>' % esc(title), head, count=1, flags=re.S)
            head = re.sub(r'<meta name="description" content="[^"]*">',
                          '<meta name="description" content="%s">' % html.escape(desc, quote=True),
                          head, count=1)
            head = re.sub(r'<link rel="canonical" href="[^"]*">',
                          '<link rel="canonical" href="%s">' % slug, head, count=1)
            if (market, ty) in NOINDEX:
                head = head.replace('<link rel="canonical"',
                                    '<meta name="robots" content="noindex,follow">\n<!-- %s -->\n<link rel="canonical"' % NOINDEX_WHY, 1)
                noidx += 1
            else:
                idx += 1
            # per-page Service node
            head = re.sub(
                r'(<script type="application/ld\+json">\s*\{\s*"@context"[^<]*?"@type": "Service".*?</script>)',
                ('<script type="application/ld+json">\n{\n'
                 '  "@context": "https://schema.org",\n  "@type": "Service",\n'
                 '  "name": "California ABC Type %s licence brokerage in %s",\n'
                 '  "serviceType": "California ABC liquor licence brokerage",\n'
                 '  "areaServed": { "@type": "AdministrativeArea", "name": "%s" },\n'
                 '  "provider": { "@type": "ProfessionalService", "name": "Liquor License Agents" }\n'
                 '}\n</script>') % (ty, label, label),
                head, count=1, flags=re.S)

            io.open(os.path.join(HERE, slug), 'w', encoding='utf-8').write(head + '\n\n' + body + '\n\n' + post)
            written += 1
    print('written %d pages  (%d indexable, %d noindex)' % (written, idx, noidx))


if __name__ == '__main__':
    main()
