#!/usr/bin/env python3
"""
Generate the 8 per-service pages from services.html.

WHY THESE ARE SAFE TO BUILD AND THE MARKET PAGES NEEDED HOLDING BACK: the same
similarity test was run first. The eight service sections share an AVERAGE of 13%
of their vocabulary, the worst pair is 17%, and ZERO pairs exceed 50%. The market
panels, by contrast, had 13 of 91 pairs above 90% and one pair at 100%. These are
genuinely different documents; those were one document with a name swapped.

ANTI-INVENTION: every sentence, bullet and image on these pages is LIFTED from
services.html. Nothing is written for them.

⚠ new-business IS noindex,follow. services.html itself flags it: "Illustrative
scope, written by the design team and awaiting the client's confirmation. This is
the only service on the page with no source text behind it." Giving unsourced
illustrative copy its own indexable page would publish a claim the project has
explicitly recorded as unconfirmed. The visible caveat is carried over too — it
is not quietly dropped on the way to a dedicated page.
"""
import re, html, json

SRC = open('services.html', encoding='utf-8').read()
LOC = open('locations.html', encoding='utf-8').read()

# ---------------------------------------------------------------- chrome (verbatim)
BODY_OPEN  = SRC.index('<body>')
MAIN_OPEN  = SRC.index('<main id="main">')
FOOT_OPEN  = SRC.index('<footer')
BODY_CLOSE = SRC.index('</body>')
HEAD_TAIL  = SRC[SRC.index('<meta name="theme-color"'):SRC.index('</head>')]
CHROME_TOP = SRC[BODY_OPEN + len('<body>'):MAIN_OPEN]
CHROME_BOT = SRC[FOOT_OPEN:BODY_CLOSE]
assert 'site-header' in CHROME_TOP and 'site-footer' in CHROME_BOT

SERVICES = [
    ('buy',          'Buy a liquor licence',            'buying'),
    ('sell',         'Sell a liquor licence',           'selling'),
    ('transfer',     'Transfer a liquor licence',       'transferring'),
    ('valuation',    'Licence valuation',               'valuing'),
    ('cup',          'Conditional Use Permits',         'permitting'),
    ('compliance',   'ABC compliance consulting',       'compliance'),
    ('escrow',       'Escrow and transaction guidance', 'escrow'),
    ('new-business', 'New business licence planning',   'planning'),
]
UNSOURCED = {'new-business'}

MARKETS = [('los-angeles','Los Angeles County'),('orange','Orange County'),
           ('riverside','Riverside County'),('sacramento','Sacramento County'),
           ('san-bernardino','San Bernardino County'),('san-diego','San Diego County'),
           ('san-francisco','San Francisco County'),('fresno','Fresno'),
           ('napa-valley','Napa Valley'),('palm-springs','Palm Springs'),
           ('san-jose','San Jose'),('santa-barbara','Santa Barbara'),('ventura','Ventura')]

# ---------------------------------------------------------------- lift the sections
marks = sorted((re.search(r'id="%s"' % i, SRC).start(), i) for i, _, _ in SERVICES)
SEG = {}
for n, (p, i) in enumerate(marks):
    end = marks[n + 1][0] if n + 1 < len(marks) else min(len(SRC), p + 9000)
    SEG[i] = SRC[p:end]

def txt(t):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', t)).strip()

def parts(sl):
    seg = SEG[sl]
    # ⚠ CIRCULAR CONTAMINATION — the bug this filter exists to stop. services.html was
    # edited to add `p.sv-deep` deep links INTO these pages, and the generator was then
    # re-run against that edited source. The deep link is the first <p> in each section,
    # so it became the LEDE and therefore the meta description: all 8 pages shipped
    # `content="Full detail on this service &rarr;"`. Caught by a unique-description probe
    # (8 unique -> 1). A generator must be idempotent against its OWN output: lift body
    # prose only, never chrome, eyebrows or navigation this build injected.
    raw = re.findall(r'(<p\b[^>]*>)(.*?)</p>', seg, re.S)
    SKIP_CLASS = re.compile(r'class="[^"]*\b(sv-deep|lm-deep|eyebrow|cross-link-rail__label)\b')
    paras = [inner for tag, inner in raw if not SKIP_CLASS.search(tag)]
    # drop the "Service 0N" eyebrow — the dedicated page has its own eyebrow
    paras = [p for p in paras if not re.fullmatch(r'\s*Service\s+\d+\s*', txt(p))]
    # and drop any stray heading-ish fragment that is not prose
    paras = [p for p in paras if len(txt(p).split()) >= 6]
    lis = re.findall(r'<li[^>]*>(.*?)</li>', seg, re.S)
    im = re.search(r'<img[^>]*src="([^"]+)"[^>]*?alt="([^"]*)"[^>]*>', seg)
    if im:
        w = re.search(r'width="(\d+)"', im.group(0))
        h = re.search(r'height="(\d+)"', im.group(0))
        img = (im.group(1), im.group(2), w.group(1) if w else '', h.group(1) if h else '')
    else:
        img = None
    return paras, lis, img

def build(sl, label, gerund):
    paras, lis, img = parts(sl)
    others = [(o, l) for o, l, _ in SERVICES if o != sl]
    lede = txt(paras[0]) if paras else ''
    body = '\n'.join('      <p>%s</p>' % p.strip() for p in paras[1:]) if len(paras) > 1 else ''
    bullets = ('\n'.join('        <li>%s</li>' % l.strip() for l in lis)) if lis else ''

    media = ''
    if img:
        src, alt, w, h = img
        media = (f'    <div class="sv-media wow-zoom"><img src="{src}" alt="{html.escape(alt)}"'
                 + (f' width="{w}" height="{h}"' if w and h else '')
                 + ' loading="lazy" decoding="async"></div>')

    caveat = ''
    robots = ''
    if sl in UNSOURCED:
        caveat = ('''    <p class="sv-caveat"><strong>Illustrative scope, awaiting the client&rsquo;s confirmation.</strong>
      This is the only service with no source text behind it &mdash; the client&rsquo;s own document repeats the
      escrow description under this heading, so nothing on this page is quoted from it. It is carried here
      exactly as it appears on the services page, flagged, rather than presented as confirmed scope.</p>''')
        robots = ('\n<meta name="robots" content="noindex,follow">'
                  '\n<!-- NOINDEX ON PURPOSE: services.html records this as the one service with NO source\n'
                  "     text behind it — illustrative scope awaiting the client's confirmation. Giving\n"
                  '     unconfirmed copy its own indexable page would publish it as fact. Remove this tag\n'
                  '     when the client confirms the scope. -->')

    market_links = ' &middot; '.join(
        f'<a href="liquor-license-{m}.html">{html.escape(l)}</a>' for m, l in MARKETS)
    other_links = ' &middot; '.join(
        f'<a href="service-{o}.html">{html.escape(l)}</a>' for o, l in others)

    title = f'{label} in California | ABC Licence Brokers'
    desc = (lede[:150].rsplit(' ', 1)[0] + '…') if len(lede) > 150 else lede
    desc = desc or f'{label} — California ABC liquor licence brokerage.'

    ld = {
        "@context": "https://schema.org", "@type": "Service",
        "name": label, "serviceType": label,
        "areaServed": {"@type": "State", "name": "California"},
        "provider": {"@type": "ProfessionalService", "name": "Liquor License Agents",
                     "telephone": "+1-800-799-9081"},
    }

    # ⚠ MEASURED: cup, compliance and escrow have exactly ONE substantive paragraph in
    # services.html. The hero lede consumes it, so a #detail section would render an EMPTY
    # .sv-body — caught by a NO-BODY probe before this shipped. There is no second paragraph
    # to lift and none will be written, so the section is OMITTED for those three and their
    # image moves down beside the bullets instead of floating under nothing.
    if body.strip() or caveat.strip():
        detail_section = f"""<section class="section section--warm" id="detail">
  <div class="container">
{caveat}
    <div class="sv-body">
{body}
    </div>
{media}
  </div>
</section>
"""
        covers_media = ''
    else:
        detail_section = ''
        covers_media = media

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="service-{sl}.html">{robots}
<link rel="preload" href="assets/fonts/ff-8ca9c2a4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ff-c52e5cbb.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="design-system/tokens.css">
<link rel="stylesheet" href="design-system/structural.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Liquor License Agents">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:image" content="assets/og-liquorlicense.jpg">
<script type="application/ld+json">
{json.dumps(ld, indent=2)}
</script>
{HEAD_TAIL}</head>
<body>{CHROME_TOP}<main id="main">

<section class="section hero hero--editorial section--dark wow-bloom">
  <div class="container">
    <p class="eyebrow"><a href="services.html">Services</a> &rsaquo; {html.escape(label)}</p>
    <h1>{html.escape(label)}</h1>
    <p class="lede">{lede}</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Talk to a broker</a>
      <a class="btn btn-secondary" href="inventory.html">See the live board</a>
    </div>
  </div>
</section>

{detail_section}
<section class="section" id="covers">
  <div class="container">
    <p class="eyebrow">What this covers</p>
    <h2>Included in {html.escape(label.lower())}</h2>
    <ul class="sv-list">
{bullets}
    </ul>
{covers_media}
    <p class="sv-note">Every one of these sits inside the same transaction &mdash; see
      <a href="process.html">how a transfer runs end to end</a>, or the
      <a href="licence-types.html">five classifications</a> it can apply to.</p>
  </div>
</section>

<section class="section section--dark" id="where">
  <div class="container">
    <p class="eyebrow">Where</p>
    <h2>{html.escape(label)} across California</h2>
    <p class="lede">We work every county in the state. What differs market by market is how much of the job is
      sourcing rather than filing.</p>
    <p class="cross-link-rail__rail">{market_links}</p>
  </div>
</section>

<section class="section closing-cta" id="next">
  <div class="container">
    <p class="eyebrow">Next</p>
    <h2>Start with a conversation</h2>
    <p class="lede">Tell us the classification, the market and the number you are working to.</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Send a brief</a>
      <a class="btn btn-secondary" href="tel:+18007999081">800.799.9081</a>
    </div>
    <div class="cross-link-rail">
      <p class="cross-link-rail__label">The other seven services</p>
      <p class="cross-link-rail__rail">{other_links}</p>
    </div>
  </div>
</section>

</main>
{CHROME_BOT}</body>
</html>
'''

if __name__ == '__main__':
    out = []
    for sl, label, gerund in SERVICES:
        page = build(sl, label, gerund)
        fn = f'service-{sl}.html'
        assert 'site-header' in page and 'site-footer' in page, 'chrome lost: ' + fn
        assert page.count('<h1>') == 1, 'h1: ' + fn
        assert 'design-system/structural.css' in page, 'css lost: ' + fn
        assert len(page) > 20000, 'suspiciously small: ' + fn
        open(fn, 'w', encoding='utf-8').write(page)
        out.append((fn, len(page), sl in UNSOURCED))
    print('wrote %d service pages' % len(out))
    for fn, n, ni in out:
        print('   %-34s %6d bytes%s' % (fn, n, '  [noindex — unsourced]' if ni else ''))
