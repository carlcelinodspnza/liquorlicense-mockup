#!/usr/bin/env python3
"""
Generate the 5 per-classification pages from licence-types.html.

SIMILARITY: run first, as on the other two sets. Average pairwise vocabulary
overlap 15%, ZERO pairs over 50% (worst is 45%, type-20/type-41). So duplication
is NOT the constraint here — thinness is.

⚠ TYPE 20 AND TYPE 41 ARE noindex,follow, AND THAT IS NOT AN OVERSIGHT.
licence-types.html states it outright in a comment at their anchors: "our
verified sources carry the official designation and scope for these two, not the
full authorisation sentence recorded for 21, 47 and 48. The matrix row is
therefore the fullest thing the site can honestly say about them." Measured: 15
and 22 words, against 126-148 for the other three. Their pages therefore carry
the matrix facts, say plainly why there is no more, and stay out of the index.
Writing an authorisation sentence for them would be inventing regulatory text
about a licence class — the single worst place on this site to guess.

ANTI-INVENTION: every classification sentence and bullet is LIFTED from
licence-types.html. The only authored text is navigational scaffolding and the
sourcing note, which describes the project's own evidence state rather than
asserting anything about the licences.
"""
import re, html, json

SRC = open('licence-types.html', encoding='utf-8').read()

HEAD_TAIL  = SRC[SRC.index('<meta name="theme-color"'):SRC.index('</head>')]
CHROME_TOP = SRC[SRC.index('<body>') + len('<body>'):SRC.index('<main id="main">')]
CHROME_BOT = SRC[SRC.index('<footer'):SRC.index('</body>')]
assert 'site-header' in CHROME_TOP and 'site-footer' in CHROME_BOT

# code -> (page label, the official designation as the site words it)
TYPES = [
    ('20', 'Type 20', 'Off-Sale Beer &amp; Wine'),
    ('21', 'Type 21', 'Off-Sale General'),
    ('41', 'Type 41', 'On-Sale Beer &amp; Wine, Eating Place'),
    ('47', 'Type 47', 'On-Sale General, Eating Place'),
    ('48', 'Type 48', 'On-Sale General, Public Premises'),
]
THIN = {'20', '41'}          # designation + scope only in verified sources

MARKETS = [('los-angeles','Los Angeles County'),('orange','Orange County'),
           ('riverside','Riverside County'),('sacramento','Sacramento County'),
           ('san-bernardino','San Bernardino County'),('san-diego','San Diego County'),
           ('san-francisco','San Francisco County'),('fresno','Fresno'),
           ('napa-valley','Napa Valley'),('palm-springs','Palm Springs'),
           ('san-jose','San Jose'),('santa-barbara','Santa Barbara'),('ventura','Ventura')]

def clean(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', t))).strip()

def element(idv):
    """Return the whole element carrying id=<idv>, balanced on its own tag."""
    m = re.search(r'<(\w+)([^>]*\bid="%s")' % re.escape(idv), SRC)
    if not m:
        return ''
    tag, start = m.group(1), m.start()
    depth = 0
    for mm in re.finditer(r'<(/?)%s\b' % tag, SRC[start:]):
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return SRC[start:start + mm.end() + len(tag)]
    return SRC[start:start + 6000]

def lift(code):
    seg = element('type-' + code)
    # skip any deep link this generator previously injected (idempotence — the
    # circular-contamination bug the service build hit)
    raw = re.findall(r'(<p\b[^>]*>)(.*?)</p>', seg, re.S)
    SKIP = re.compile(r'class="[^"]*\b(tp-deep|sv-deep|lm-deep|eyebrow)\b')
    paras = [inner for tag, inner in raw if not SKIP.search(tag) and len(clean(inner).split()) >= 6]
    lis = [l for l in re.findall(r'<li[^>]*>(.*?)</li>', seg, re.S) if clean(l)]
    h3 = re.search(r'<h3[^>]*>(.*?)</h3>', seg, re.S)
    cells = [clean(c) for c in re.findall(r'<td[^>]*>(.*?)</td>', seg, re.S)]
    return paras, lis, (clean(h3.group(1)) if h3 else ''), cells

def build(code, label, designation):
    paras, lis, h3name, cells = lift(code)
    thin = code in THIN
    others = [(c, l, d) for c, l, d in TYPES if c != code]

    lede = clean(paras[0]) if paras else ''
    if thin:
        # the matrix row IS the source of truth for these two
        scope = ' &middot; '.join(html.escape(c) for c in cells if c)
        lede = (f'The official designation is {designation}. '
                + (f'Scope on record: {scope}.' if scope else ''))

    body = '\n'.join('      <p>%s</p>' % p.strip() for p in paras[1:]) if len(paras) > 1 else ''
    bullets = '\n'.join('        <li>%s</li>' % l.strip() for l in lis) if lis else ''

    sourcing = ''
    robots = ''
    if thin:
        sourcing = f'''    <p class="tp-caveat"><strong>What this site can say about {label} is limited on purpose.</strong>
      Our verified sources carry the official designation and scope for {label}, not the full
      authorisation sentence recorded for Types 21, 47 and 48. Rather than write one, this page states
      what is on record and stops there. For the operative wording, the Department of Alcoholic Beverage
      Control is the authority; for what it means for a specific site,
      <a href="contact.html#quote">talk to a broker</a>.</p>'''
        robots = ('\n<meta name="robots" content="noindex,follow">'
                  '\n<!-- NOINDEX ON PURPOSE: licence-types.html records that verified sources carry only\n'
                  '     the designation and scope for this classification, not the full authorisation\n'
                  '     sentence held for 21/47/48 — measured at 15-22 words against 126-148. The page\n'
                  '     exists so the classification has a destination, but it is not indexed while it\n'
                  '     is that thin. Remove this tag if a sourced authorisation sentence is added. -->')

    covers = ''
    if bullets:
        covers = f'''
<section class="section" id="covers">
  <div class="container">
    <p class="eyebrow">In practice</p>
    <h2>What a {label} actually covers</h2>
    <ul class="tp-list">
{bullets}
    </ul>
  </div>
</section>
'''

    market_links = ' &middot; '.join(
        f'<a href="liquor-license-{m}.html">{html.escape(l)}</a>' for m, l in MARKETS)
    other_links = ' &middot; '.join(
        f'<a href="licence-type-{c}.html">{l} &mdash; {d}</a>' for c, l, d in others)

    # ⚠ MEASURED: on the two thin classifications `body` is empty (their source is a
    # table row, not prose), and the earlier fallback re-printed the hero lede here — the
    # SAME sentence twice on one page, confirmed by comparing the two strings. The section
    # is not empty without it: the sourcing caveat and the note both live there. So the
    # body div is rendered only when there is genuinely a second paragraph to put in it.
    body_block = ('    <div class="tp-body">\n' + body + '\n    </div>') if body.strip() else ''

    plain = html.unescape(designation)
    title = f'{label} Liquor Licence &mdash; {designation} | California ABC'
    desc = (lede[:150].rsplit(' ', 1)[0] + '…') if len(lede) > 150 else lede
    desc = desc or f'{label} — {plain}. California ABC classification.'

    ld = {"@context": "https://schema.org", "@type": "Product",
          "name": f"{label} — {plain}",
          "category": "California ABC liquor licence",
          "brand": {"@type": "Brand", "name": "California Department of Alcoholic Beverage Control"},
          "offers": {"@type": "AggregateOffer", "availability": "https://schema.org/LimitedAvailability",
                     "priceCurrency": "USD",
                     "seller": {"@type": "ProfessionalService", "name": "Liquor License Agents"}}}

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="licence-type-{code}.html">{robots}
<link rel="preload" href="assets/fonts/ff-8ca9c2a4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ff-c52e5cbb.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="design-system/tokens.css">
<link rel="stylesheet" href="design-system/structural.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Liquor License Agents">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:image" content="assets/og-liquorlicense.jpg">
<script type="application/ld+json">
{json.dumps(ld, indent=2)}
</script>
{HEAD_TAIL}</head>
<body>{CHROME_TOP}<main id="main">

<section class="section hero hero--editorial section--dark wow-bloom">
  <div class="container">
    <p class="eyebrow"><a href="licence-types.html">Classifications</a> &rsaquo; {label}</p>
    <h1>{label} &mdash; {designation}</h1>
    <p class="lede">{lede}</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="inventory.html?type={code}">See {label} on the board</a>
      <a class="btn btn-secondary" href="contact.html#quote">Ask a broker</a>
    </div>
  </div>
</section>

<section class="section section--warm" id="detail">
  <div class="container">
{sourcing}
{body_block}
    <p class="tp-note">All five classifications are set side by side on the
      <a href="licence-types.html">licence types page</a>. Which one a business needs is decided by what is
      poured, whether it is consumed where it is bought, and what the room is for &mdash; not by size.</p>
  </div>
</section>
{covers}
<section class="section section--dark" id="where">
  <div class="container">
    <p class="eyebrow">Where</p>
    <h2>{label} across California</h2>
    <p class="lede">Availability is a local question. What a classification is worth, and whether one is even
      obtainable, turns on the county rather than the state.</p>
    <p class="cross-link-rail__rail">{market_links}</p>
  </div>
</section>

<section class="section closing-cta" id="next">
  <div class="container">
    <p class="eyebrow">Next</p>
    <h2>Working towards a {label}?</h2>
    <p class="lede">Tell us the market and the number you are working to. If it is not on the board we source
      against it.</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Send a sourcing brief</a>
      <a class="btn btn-secondary" href="tel:+18007999081">800.799.9081</a>
    </div>
    <div class="cross-link-rail">
      <p class="cross-link-rail__label">The other four classifications</p>
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
    for code, label, designation in TYPES:
        page = build(code, label, designation)
        fn = f'licence-type-{code}.html'
        assert 'site-header' in page and 'site-footer' in page, 'chrome lost: ' + fn
        assert page.count('<h1>') == 1, 'h1: ' + fn
        assert 'design-system/structural.css' in page, 'css lost: ' + fn
        assert 'Full detail on this' not in page, 'deep-link leaked: ' + fn
        assert len(page) > 20000, 'too small: ' + fn
        open(fn, 'w', encoding='utf-8').write(page)
        out.append((fn, len(page), code in THIN))
    print('wrote %d classification pages' % len(out))
    for fn, n, thin in out:
        print('   %-30s %6d bytes%s' % (fn, n, '  [noindex — designation+scope only]' if thin else ''))
