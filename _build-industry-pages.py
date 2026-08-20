#!/usr/bin/env python3
"""
Generate the 8 per-industry pages from index.html #industries.

THE TEST, run first as on the other three sets:
  · duplication  — average pairwise overlap 9%, ZERO pairs over 50%. Not a risk.
  · THINNESS     — mean 20 words per industry (min 16, max 25). This is by far
                   the thinnest set: markets had ~150-200, services 99-153,
                   classifications 15-148. Twenty words is a caption, not a page.

So these ship as the owner asked: a REAL kernel plus an explicit PLACEHOLDER the
owner replaces, and noindex until that happens.

WHAT IS REAL ON THESE PAGES (lifted, never written):
  · the industry name, its one-line description and its photograph — index.html
  · the classifications named IN that description — extracted by regex from the
    copy itself, never inferred. "Restaurants" names Type 41 and Type 47, so the
    page says so. "Hotels" names none, so the page claims none. Inferring a type
    from a business category would be exactly the guess this build refuses.

WHAT IS PLACEHOLDER (visibly flagged, and the reason for noindex):
  · one block per page, marked in the markup, in the rendered page and in the
    robots tag. It states what belongs there rather than pretending to be copy,
    so it cannot be mistaken for finished content the way three fabricated
    testimonials once were on this site.
"""
import re, html, json

SRC = open('index.html', encoding='utf-8').read()

HEAD_TAIL  = SRC[SRC.index('<meta name="theme-color"'):SRC.index('</head>')]
CHROME_TOP = SRC[SRC.index('<body>') + len('<body>'):SRC.index('<main id="main">')]
CHROME_BOT = SRC[SRC.index('<footer'):SRC.index('</body>')]
assert 'site-header' in CHROME_TOP and 'site-footer' in CHROME_BOT

SEG = SRC[SRC.index('id="industries"'):SRC.index('id="licensing"')]

SLUGS = {
    'Restaurants': 'restaurants',
    'Bars & nightclubs': 'bars-nightclubs',
    'Hotels': 'hotels',
    'Liquor stores': 'liquor-stores',
    'Grocery stores': 'grocery-stores',
    'Convenience stores': 'convenience-stores',
    'Franchise operators': 'franchise-operators',
    'Event venues': 'event-venues',
}
DESIGNATION = {'20': 'Off-Sale Beer &amp; Wine', '21': 'Off-Sale General',
               '41': 'On-Sale Beer &amp; Wine, Eating Place',
               '47': 'On-Sale General, Eating Place',
               '48': 'On-Sale General, Public Premises'}

MARKETS = [('los-angeles','Los Angeles County'),('orange','Orange County'),
           ('riverside','Riverside County'),('sacramento','Sacramento County'),
           ('san-bernardino','San Bernardino County'),('san-diego','San Diego County'),
           ('san-francisco','San Francisco County'),('fresno','Fresno'),
           ('napa-valley','Napa Valley'),('palm-springs','Palm Springs'),
           ('san-jose','San Jose'),('santa-barbara','Santa Barbara'),('ventura','Ventura')]

def clean(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', t))).strip()

def lift():
    out = []
    for href, body in re.findall(r'<a class="category-card[^"]*"[^>]*href="([^"]*)"[^>]*>(.*?)</a>', SEG, re.S):
        lab = re.search(r'category-card__label">(.*?)</span>', body, re.S)
        dsc = re.search(r'ind-tile__desc">(.*?)</span>', body, re.S)
        img = re.search(r'src="([^"]+)"', body)
        w   = re.search(r'width="(\d+)"', body)
        h   = re.search(r'height="(\d+)"', body)
        alt = re.search(r'alt="([^"]*)"', body)
        if not lab:
            continue
        name = clean(lab.group(1))
        desc_html = dsc.group(1).strip() if dsc else ''
        # classifications NAMED IN THE COPY — extracted, never inferred
        types = sorted(set(re.findall(r'Type\s+(20|21|41|47|48)', clean(desc_html))))
        out.append({'name': name, 'slug': SLUGS.get(name, name.lower().replace(' ', '-').replace('&', 'and')),
                    'desc_html': desc_html, 'desc': clean(desc_html),
                    'img': img.group(1) if img else '', 'w': w.group(1) if w else '',
                    'h': h.group(1) if h else '', 'alt': alt.group(1) if alt else name,
                    'types': types})
    return out

def build(it, everything):
    name, slug, desc, types = it['name'], it['slug'], it['desc_html'], it['types']
    plain = clean(name)
    others = [x for x in everything if x['slug'] != slug]

    if types:
        rows = '\n'.join(
            f'''        <li><a href="licence-type-{t}.html"><strong>Type {t}</strong> &mdash; {DESIGNATION[t]}</a></li>'''
            for t in types)
        types_block = f'''    <p class="lede">The description above names {'these classifications' if len(types)>1 else 'this classification'} directly:</p>
    <ul class="ind-types">
{rows}
    </ul>
    <p class="ind-note">Only the classifications this site already names for {html.escape(plain.lower())} are listed.
      Which one a specific business needs turns on what is poured, whether it is drunk where it is bought, and
      what the room is for &mdash; see all five on the <a href="licence-types.html">licence types page</a>.</p>'''
    else:
        types_block = f'''    <p class="lede">This site does not yet name a specific classification for {html.escape(plain.lower())}.</p>
    <p class="ind-note">Rather than infer one from the business category, the five classifications are set out
      in full on the <a href="licence-types.html">licence types page</a>, and a broker will tell you which
      applies to a specific site. Naming a type here without a source behind it is the one thing this page
      will not do.</p>'''

    media = ''
    if it['img']:
        dims = f' width="{it["w"]}" height="{it["h"]}"' if it['w'] and it['h'] else ''
        media = (f'    <div class="ind-media wow-zoom"><img src="{it["img"]}" '
                 f'alt="{html.escape(it["alt"])}"{dims} loading="lazy" decoding="async"></div>')

    market_links = ' &middot; '.join(
        f'<a href="liquor-license-{m}.html">{html.escape(l)}</a>' for m, l in MARKETS)
    other_links = ' &middot; '.join(
        f'<a href="industry-{o["slug"]}.html">{html.escape(o["name"])}</a>' for o in others)

    title = f'Liquor Licences for {plain} in California | ABC Brokers'
    d = clean(desc)
    meta_desc = (d[:150].rsplit(' ', 1)[0] + '…') if len(d) > 150 else d

    ld = {"@context": "https://schema.org", "@type": "Service",
          "name": f"Liquor licence brokerage for {plain.lower()}",
          "serviceType": "California ABC liquor licence brokerage",
          "areaServed": {"@type": "State", "name": "California"},
          "audience": {"@type": "BusinessAudience", "audienceType": plain},
          "provider": {"@type": "ProfessionalService", "name": "Liquor License Agents",
                       "telephone": "+1-800-799-9081"}}

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc, quote=True)}">
<link rel="canonical" href="industry-{slug}.html">
<meta name="robots" content="noindex,follow">
<!-- NOINDEX ON PURPOSE — AND THIS ONE IS MEANT TO BE REMOVED BY HAND.
     This page carries a deliberate PLACEHOLDER block (section#draft below). The
     real content for it does not exist yet: index.html gives this industry a
     20-word caption, which is a tile, not a page. Measured across the eight
     industries: min 16, max 25, mean 20 words.
     TO PUBLISH THIS PAGE: replace section#draft with real copy, then delete this
     robots tag and this comment. Do not delete the robots tag first. -->
<link rel="preload" href="assets/fonts/ff-8ca9c2a4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ff-c52e5cbb.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="design-system/tokens.css">
<link rel="stylesheet" href="design-system/structural.css">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Liquor License Agents">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc, quote=True)}">
<meta property="og:image" content="assets/og-liquorlicense.jpg">
<script type="application/ld+json">
{json.dumps(ld, indent=2)}
</script>
{HEAD_TAIL}</head>
<body>{CHROME_TOP}<main id="main">

<section class="section hero hero--editorial section--dark wow-bloom">
  <div class="container">
    <p class="eyebrow"><a href="index.html#industries">Who we license</a> &rsaquo; {html.escape(plain)}</p>
    <h1>Liquor licences for {html.escape(plain.lower())}</h1>
    <p class="lede">{desc}</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Talk to a broker</a>
      <a class="btn btn-secondary" href="inventory.html">See the live board</a>
    </div>
  </div>
</section>

<section class="section section--warm" id="classifications">
  <div class="container">
    <p class="eyebrow">Classification</p>
    <h2>What {html.escape(plain.lower())} are licensed under</h2>
{types_block}
{media}
  </div>
</section>

<!-- ═══════════════════════════════════════════════════════════════════════════
     PLACEHOLDER — THE OWNER REPLACES THIS BLOCK.
     Everything above and below this section is REAL: lifted from index.html or
     generated from links that resolve. This section is the only invented thing
     on the page, and it deliberately describes what belongs here instead of
     pretending to be copy. That is the lesson from the three fabricated
     testimonials that sat on the public homepage for weeks reading as real.
     When this is replaced, also remove the robots noindex tag in the head.
     ═══════════════════════════════════════════════════════════════════════ -->
<section class="section ind-draft" id="draft">
  <div class="container">
    <p class="ind-draft__flag">Placeholder &mdash; not client copy. Replace before publishing.</p>
    <h2>What goes here</h2>
    <p class="lede">This page needs one thing the site does not have yet: what licensing actually looks like for
      {html.escape(plain.lower())}, in this brokerage&rsquo;s own words.</p>
    <ul class="ind-draft__slots">
      <li><strong>The decision that gets made wrong.</strong> The classification mistake operators in this
        category most often make, and what it costs to unwind.</li>
      <li><strong>What the licence is attached to.</strong> Whether it follows the site, the operator or the
        brand &mdash; and what that means when the business is sold.</li>
      <li><strong>The local approval that bites.</strong> Which permit or hearing this category usually runs
        into beyond the ABC file itself.</li>
      <li><strong>One real transaction.</strong> A deal in this category: county, classification, what made it
        straightforward or slow. No names needed.</li>
    </ul>
    <p class="ind-note">Written by the design team as a brief, not as copy. Nothing in this block is quoted from
      the client and nothing in it should be published as-is.</p>
  </div>
</section>

<section class="section section--dark" id="where">
  <div class="container">
    <p class="eyebrow">Where</p>
    <h2>{html.escape(plain)} across California</h2>
    <p class="lede">We work every county in the state. What differs market by market is how much of the job is
      sourcing rather than filing.</p>
    <p class="cross-link-rail__rail">{market_links}</p>
  </div>
</section>

<section class="section closing-cta" id="next">
  <div class="container">
    <p class="eyebrow">Next</p>
    <h2>Opening or buying in {html.escape(plain.lower())}?</h2>
    <p class="lede">Tell us the market, the classification and the number you are working to.</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Send a sourcing brief</a>
      <a class="btn btn-secondary" href="tel:+18007999081">800.799.9081</a>
    </div>
    <div class="cross-link-rail">
      <p class="cross-link-rail__label">The other seven business types</p>
      <p class="cross-link-rail__rail">{other_links}</p>
    </div>
  </div>
</section>

</main>
{CHROME_BOT}</body>
</html>
'''

if __name__ == '__main__':
    items = lift()
    assert len(items) == 8, 'expected 8 industries, lifted %d' % len(items)
    out = []
    for it in items:
        page = build(it, items)
        fn = f'industry-{it["slug"]}.html'
        assert 'site-header' in page and 'site-footer' in page, 'chrome lost: ' + fn
        assert page.count('<h1>') == 1, 'h1: ' + fn
        assert 'noindex' in page, 'placeholder page must be noindex: ' + fn
        assert 'ind-draft__flag' in page, 'placeholder flag missing: ' + fn
        assert len(page) > 20000, 'too small: ' + fn
        open(fn, 'w', encoding='utf-8').write(page)
        out.append((fn, len(page), it['types']))
    print('wrote %d industry pages (ALL noindex — each carries a placeholder block)' % len(out))
    for fn, n, t in out:
        print('   %-38s %6d bytes  types named in source: %s' % (fn, n, ', '.join(t) if t else 'none'))
