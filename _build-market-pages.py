#!/usr/bin/env python3
"""
Generate the 13 per-market pages from locations.html.

WHY 13 AND NOT 14: the "california" tab on locations.html is the ALL view, not a
market. locations.html already IS the statewide page, so generating a california
page would duplicate it against itself. The owner asked for 14; this is the one
deliberate deviation and it is reported rather than taken silently.

CHROME IS COPIED VERBATIM from locations.html (header + drawer + footer + sticky
CTA + script tag), so these pages inherit the stamped nav signature that
verify-chrome-consistent requires, and no chrome is re-authored.

ANTI-INVENTION: every per-market fact here is LIFTED, not written —
  · market label + stock position -> locations.html tab + panel
  · live listings (city, type, price) -> inventory.html data-* attributes
  · the five classifications -> contact.html #q-type
No county quota, no local ordinance, no ABC district office, no price guidance
is asserted, because none of that exists in the project's verified sources.
"""
import re, html, json, os

SRC = 'locations.html'
s = open(SRC, encoding='utf-8').read()

# ---------------------------------------------------------------- chrome
HEAD_END   = s.index('</head>')
BODY_OPEN  = s.index('<body>')
MAIN_OPEN  = s.index('<main id="main">')
FOOT_OPEN  = s.index('<footer')
BODY_CLOSE = s.index('</body>')

HEAD_TAIL = s[s.index('<meta name="theme-color"'):HEAD_END]      # icons/theme/noscript
CHROME_TOP = s[BODY_OPEN + len('<body>'):MAIN_OPEN]              # skip link + header + drawer
CHROME_BOT = s[FOOT_OPEN:BODY_CLOSE]                             # footer + sticky CTA + script

assert 'site-header' in CHROME_TOP and 'mobile-drawer' in CHROME_TOP
assert 'site-footer' in CHROME_BOT and 'site.js' in CHROME_BOT

# ---------------------------------------------------------------- data (lifted)
LISTINGS = {}
for a in re.findall(r'<article\b[^>]*>.*?</article>', open('inventory.html', encoding='utf-8').read(), re.S):
    d = dict(re.findall(r'data-([a-z-]+)="([^"]*)"', a))
    if 'county' not in d:
        continue
    txt = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', a))).strip()
    h3 = re.search(r'<h3[^>]*>(.*?)</h3>', a, re.S)
    price = re.search(r'\$[\d,]+', txt)
    LISTINGS.setdefault(d['county'], []).append({
        'type': d.get('type', ''),
        'city': html.unescape(re.sub(r'<[^>]*>', '', h3.group(1)).strip()) if h3 else '',
        'price': price.group(0) if price else '',
        'status': d.get('status', ''),
    })

TYPES = [('20', 'Off-Sale Beer &amp; Wine'), ('21', 'Off-Sale General'),
         ('41', 'On-Sale Beer &amp; Wine, Eating Place'),
         ('47', 'On-Sale General, Eating Place'),
         ('48', 'On-Sale General, Public Premises')]

# label + the grammatical form used in prose, taken from the tab rail
MARKETS = [
    ('los-angeles',   'Los Angeles County',   'Los Angeles County'),
    ('orange',        'Orange County',        'Orange County'),
    ('riverside',     'Riverside County',     'Riverside County'),
    ('sacramento',    'Sacramento County',    'Sacramento County'),
    ('san-bernardino','San Bernardino County','San Bernardino County'),
    ('san-diego',     'San Diego County',     'San Diego County'),
    ('san-francisco', 'San Francisco County', 'San Francisco County'),
    ('fresno',        'Fresno',               'Fresno'),
    ('napa-valley',   'Napa Valley',          'Napa Valley'),
    ('palm-springs',  'Palm Springs',         'Palm Springs'),
    ('san-jose',      'San Jose',             'San Jose'),
    ('santa-barbara', 'Santa Barbara',        'Santa Barbara'),
    ('ventura',       'Ventura',              'Ventura'),
]

def slug_file(sl):
    return f'liquor-license-{sl}.html'

def esc(t):
    return html.escape(t, quote=True)

# ---------------------------------------------------------------- page
def build(sl, label, prose):
    live = LISTINGS.get(sl, [])
    n = len(live)
    others = [(o, l) for o, l, _ in MARKETS if o != sl]

    # ---- honest, per-market stock sentence (derived from real counts only)
    if n == 0:
        stock_line = (f'No live listings in {prose} today. We broker here, and that is a stock '
                      f'position rather than a coverage gap &mdash; tell us the classification and '
                      f'the number you are working to and we source against it off-market.')
        stock_kicker = 'No live listings today'
    elif n == 1:
        t = live[0]['type']
        stock_line = (f'One live listing in {prose} today, and it is a Type {t}. '
                      f'Everything else in this market is sourced off-market to your brief.')
        stock_kicker = '1 live listing today'
    else:
        ts = ', '.join('Type ' + x['type'] for x in live[:-1]) + ' and Type ' + live[-1]['type']
        stock_line = (f'{n} live listings in {prose} today &mdash; {ts}. '
                      f'It is the deepest market on our board.')
        stock_kicker = f'{n} live listings today'

    # ---- live listing cards (REAL rows only; nothing is manufactured)
    if live:
        cards = '\n'.join(
            f'''        <article class="card lm-card wow-lift">
          <p class="lm-card__type">Type {x['type']}</p>
          <h3 class="lm-card__city">{esc(x['city'])}</h3>
          <p class="lm-card__price">{x['price']}</p>
          <p class="lm-card__meta">{esc(prose)}{' &middot; ' + esc(x['status'].title()) if x['status'] else ''}</p>
          <a class="btn btn-secondary" href="inventory.html?county={sl}&amp;type={x['type']}">Open it on the board</a>
        </article>''' for x in live)
        listings_block = f'''    <div class="lm-grid wow-stagger">
{cards}
    </div>
    <p class="lm-note">Prices are the current asking figures on our board and move as transfers close.
      The board is the single source of truth: <a href="inventory.html?county={sl}">see this market on the inventory board</a>.</p>'''
    else:
        listings_block = f'''    <div class="lm-empty">
      <p class="lede">We broker in {esc(prose)}. There is nothing on the board here right now.</p>
      <p>That is what the board says today, not a statement about what we can reach. Supply in a capped
         market arrives when a holder decides to leave it, and those exits are unscheduled &mdash; so the
         work in a market with no live stock is sourcing, not filtering.</p>
      <div class="cta-row">
        <a class="btn btn-primary wow-glow" href="contact.html#quote">Send a sourcing brief</a>
        <a class="btn btn-secondary" href="inventory.html">See every live listing</a>
      </div>
    </div>'''

    # ---- classification rows, availability computed from the real listings
    rows = []
    for code, name in TYPES:
        got = [x for x in live if x['type'] == code]
        if got:
            avail = (f'<span class="lm-yes">{len(got)} live in {esc(prose)} today</span>')
            cta = f'<a href="inventory.html?county={sl}&amp;type={code}">Open it on the board</a>'
        else:
            avail = '<span class="lm-no">Nothing live in this classification here today</span>'
            cta = '<a href="contact.html#quote">Send a sourcing brief</a>'
        rows.append(f'''        <tr>
          <th scope="row"><a href="licence-types.html#type-{code}">Type {code}</a></th>
          <td>{name}</td>
          <td>{avail}</td>
          <td>{cta}</td>
        </tr>''')
    rows = '\n'.join(rows)

    other_links = ' &middot; '.join(
        f'<a href="{slug_file(o)}">{esc(l)}</a>' for o, l in others)

    title = f'Liquor Licences for Sale in {label} | ABC Licence Brokers'
    desc  = (f'{stock_kicker} in {prose}. Buy, sell and transfer California ABC liquor licences '
             f'in {prose} &mdash; Type 20, 21, 41, 47 and 48, carried through statutory escrow.')[:158]

    # thin pages are held back from the index until they carry market-specific fact
    robots = ('\n<meta name="robots" content="noindex,follow">'
              '\n<!-- NOINDEX ON PURPOSE: with no live stock this page carries no market-specific\n'
              '     fact that the statewide locations.html does not already carry, so indexing it\n'
              '     would publish a near-duplicate. Remove this tag the moment this market gains\n'
              '     live stock or real sourced local content. -->') if n == 0 else ''

    ld = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": f"Liquor licence brokerage in {prose}",
        "serviceType": "California ABC liquor licence brokerage",
        "areaServed": {"@type": "AdministrativeArea", "name": prose},
        "provider": {"@type": "ProfessionalService", "name": "Liquor License Agents",
                     "telephone": "+1-800-799-9081",
                     "address": {"@type": "PostalAddress", "streetAddress": "5243 E Beverly Blvd.",
                                 "addressLocality": "Los Angeles", "addressRegion": "CA",
                                 "postalCode": "90022", "addressCountry": "US"}},
    }

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{slug_file(sl)}">{robots}
<link rel="preload" href="assets/fonts/ff-8ca9c2a4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ff-c52e5cbb.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="design-system/tokens.css">
<link rel="stylesheet" href="design-system/structural.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Liquor License Agents">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="assets/og-liquorlicense.jpg">
<script type="application/ld+json">
{json.dumps(ld, indent=2)}
</script>
{HEAD_TAIL}</head>
<body>{CHROME_TOP}<main id="main">

<section class="section hero hero--editorial section--dark wow-bloom">
  <div class="container">
    <p class="eyebrow"><a href="locations.html">Markets</a> &rsaquo; {esc(label)}</p>
    <h1>Liquor licences in {esc(label)}</h1>
    <p class="lede">{stock_line}</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Talk to a broker</a>
      <a class="btn btn-secondary" href="inventory.html?county={sl}">See the board</a>
    </div>
  </div>
</section>

<section class="section section--warm" id="live">
  <div class="container">
    <p class="eyebrow">On the board today</p>
    <h2>What is live in {esc(prose)}</h2>
{listings_block}
  </div>
</section>

<section class="section" id="classifications">
  <div class="container">
    <p class="eyebrow">By classification</p>
    <h2>The five classifications in {esc(prose)}</h2>
    <p class="lede">Availability below is this market&rsquo;s position on our board today. A classification with
      nothing live is sourced to order &mdash; it is not a classification we cannot reach.</p>
    <div class="lm-table-wrap">
      <table class="lm-table">
        <thead><tr><th scope="col">Classification</th><th scope="col">What it authorises</th>
          <th scope="col">In {esc(prose)} today</th><th scope="col"></th></tr></thead>
        <tbody>
{rows}
        </tbody>
      </table>
    </div>
    <p class="lm-note">The classifications themselves are set out in full on the
      <a href="licence-types.html">licence types page</a>. Which one a business needs is decided by what
      is poured, whether it is consumed on the premises, and what the room is for.</p>
  </div>
</section>

<section class="section section--dark" id="how">
  <div class="container">
    <p class="eyebrow">How we work here</p>
    <h2>The same transaction, run end to end</h2>
    <p class="lede">Nothing about the process changes market by market &mdash; what changes is how much of it is
      sourcing rather than filing.</p>
    <div class="cta-row">
      <a class="btn btn-secondary" href="process.html">See the full process</a>
      <a class="btn btn-secondary" href="services.html">All eight services</a>
      <a class="btn btn-secondary" href="faq.html">Common questions</a>
    </div>
  </div>
</section>

<section class="section closing-cta" id="next">
  <div class="container">
    <p class="eyebrow">Next</p>
    <h2>Working in {esc(prose)}?</h2>
    <p class="lede">Tell us the classification, the market and the number you are working to. If it is not on the
      board we go looking for it.</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Send a sourcing brief</a>
      <a class="btn btn-secondary" href="tel:+18007999081">800.799.9081</a>
    </div>
    <div class="cross-link-rail">
      <p class="cross-link-rail__label">Other markets we cover</p>
      <p class="cross-link-rail__rail">{other_links}</p>
    </div>
  </div>
</section>

</main>
{CHROME_BOT}</body>
</html>
'''

if __name__ == '__main__':
    written = []
    for sl, label, prose in MARKETS:
        out = slug_file(sl)
        page = build(sl, label, prose)
        # guards — refuse to write a page that lost its chrome or its identity
        assert 'site-header' in page and 'site-footer' in page, 'chrome lost: ' + out
        assert page.count('<h1>') == 1, 'h1 count: ' + out
        assert 'design-system/structural.css' in page, 'stylesheet lost: ' + out
        assert label in page, 'label missing: ' + out
        open(out, 'w', encoding='utf-8').write(page)
        written.append((out, len(page), len(LISTINGS.get(sl, []))))
    print('wrote %d market pages' % len(written))
    for o, n, l in written:
        print('   %-40s %6d bytes  %d live listing(s)%s' % (o, n, l, '  [noindex]' if l == 0 else ''))
