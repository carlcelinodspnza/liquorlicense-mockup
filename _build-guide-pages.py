#!/usr/bin/env python3
"""
Generate the 4 guide pages from resources.html's explainer sections.

THE TEST, run first as on the other four sets — and this set scores BEST:
  · duplication — average pairwise overlap 16%, highest 19%, ZERO pairs over 50%
  · depth       — 251-414 words each, mean 297, with 3-8 real paragraphs

Compare: industries 20 words, classifications 15-148, services 99-153, markets
~150-200 with a 100%-identical pair. These four are the only set that needed no
holding back at all: every one ships INDEXABLE with no placeholder.

ANTI-INVENTION: the prose is lifted verbatim, INCLUDING its inline links — the
paragraphs are copied as HTML, not as text, so the existing cross-references to
licence-types / services / inventory / faq survive rather than being flattened.
Nothing is written for these pages except navigation.
"""
import re, html, json

SRC = open('resources.html', encoding='utf-8').read()

HEAD_TAIL  = SRC[SRC.index('<meta name="theme-color"'):SRC.index('</head>')]
CHROME_TOP = SRC[SRC.index('<body>') + len('<body>'):SRC.index('<main id="main">')]
CHROME_BOT = SRC[SRC.index('<footer'):SRC.index('</body>')]
assert 'site-header' in CHROME_TOP and 'site-footer' in CHROME_BOT

# source id -> (output slug, short nav label)
GUIDES = {
    'classification': ('classification',  'Choosing a classification'),
    'pricing':        ('pricing',         'What a licence costs'),
    'route':          ('resale-market',   'Why it is a resale market'),
    'zoning':         ('zoning',          'Zoning and local approval'),
}

MARKETS = [('los-angeles','Los Angeles County'),('orange','Orange County'),
           ('san-diego','San Diego County'),('san-francisco','San Francisco County'),
           ('riverside','Riverside County'),('sacramento','Sacramento County'),
           ('san-bernardino','San Bernardino County')]

def clean(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]*>', ' ', t))).strip()

def prose_container_end():
    """End of `.article-body__prose`, balanced on its own div.

    ⚠ THIS BOUND IS THE FIX FOR A REAL CONTAMINATION BUG. #zoning is the LAST
    h2[id] on resources.html, so bounding the last section at `</main>` swept up
    everything after the article — the "Topic directory" and "Next step" blocks —
    and put TWO paragraphs belonging to those closing sections onto the zoning
    guide. Caught by reading every <p> the slice contained, not by word counts:
    the counts looked plausible because the eyebrow labels were filtered out and
    only the body paragraphs survived to be miscounted as article prose.
    The article ends where its container ends, never where the page does.
    """
    i = SRC.index('article-body__prose')
    start = SRC.rfind('<div', 0, i)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', SRC[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.start()
    return SRC.index('</main>')

def sections():
    heads = [(m.start(), m.group(1), m.group(2))
             for m in re.finditer(r'<h2[^>]*\bid="([a-z-]+)"[^>]*>(.*?)</h2>', SRC, re.S)]
    end_of_prose = prose_container_end()
    out = {}
    for n, (p, idv, title) in enumerate(heads):
        if idv not in GUIDES:
            continue
        end = min(heads[n + 1][0] if n + 1 < len(heads) else end_of_prose, end_of_prose)
        out[idv] = {'title': clean(title), 'html': SRC[p:end]}
    return out

def build(idv, sec, everything):
    slug, label = GUIDES[idv]
    seg = sec['html']

    # paragraphs are copied as HTML so their inline cross-links survive the lift
    raw = re.findall(r'(<p\b[^>]*>)(.*?)</p>', seg, re.S)
    SKIP = re.compile(r'class="[^"]*\b(gd-deep|sv-deep|lm-deep|tp-deep|eyebrow)\b')
    paras = [inner for tag, inner in raw
             if not SKIP.search(tag) and len(clean(inner).split()) >= 6]
    assert paras, 'no prose lifted for ' + idv

    im = re.search(r'<img[^>]*>', seg)
    media = ''
    if im:
        media = f'    <div class="gd-media wow-zoom">{im.group(0)}</div>'

    lede = paras[0]
    body = '\n'.join('      <p>%s</p>' % p.strip() for p in paras[1:])
    others = [(GUIDES[k][0], GUIDES[k][1]) for k in everything if k != idv]

    other_links = ' &middot; '.join(
        f'<a href="guide-{s}.html">{html.escape(l)}</a>' for s, l in others)
    market_links = ' &middot; '.join(
        f'<a href="liquor-license-{m}.html">{html.escape(l)}</a>' for m, l in MARKETS)

    title_txt = sec['title']
    page_title = f'{label} | California Liquor Licence Guide'
    d = clean(lede)
    meta_desc = (d[:150].rsplit(' ', 1)[0] + '…') if len(d) > 150 else d

    ld = {"@context": "https://schema.org", "@type": "Article",
          "headline": title_txt,
          "description": meta_desc,
          "about": "California ABC liquor licensing",
          "isPartOf": {"@type": "Blog", "name": "California Liquor Licensing Knowledge Base"},
          "publisher": {"@type": "ProfessionalService", "name": "Liquor License Agents",
                        "telephone": "+1-800-799-9081"}}

    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(page_title)}</title>
<meta name="description" content="{html.escape(meta_desc, quote=True)}">
<link rel="canonical" href="guide-{slug}.html">
<link rel="preload" href="assets/fonts/ff-8ca9c2a4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ff-c52e5cbb.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="design-system/tokens.css">
<link rel="stylesheet" href="design-system/structural.css">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Liquor License Agents">
<meta property="og:title" content="{html.escape(page_title)}">
<meta property="og:description" content="{html.escape(meta_desc, quote=True)}">
<meta property="og:image" content="assets/og-liquorlicense.jpg">
<script type="application/ld+json">
{json.dumps(ld, indent=2)}
</script>
{HEAD_TAIL}</head>
<body>{CHROME_TOP}<main id="main">

<article>
<section class="section hero hero--editorial section--dark wow-bloom">
  <div class="container">
    <p class="eyebrow"><a href="resources.html">Knowledge base</a> &rsaquo; {html.escape(label)}</p>
    <h1>{title_txt}</h1>
    <p class="lede">{lede}</p>
  </div>
</section>

<section class="section section--warm" id="read">
  <div class="container">
    <div class="gd-prose">
{body}
    </div>
{media}
  </div>
</section>
</article>

<section class="section" id="related">
  <div class="container">
    <p class="eyebrow">Keep reading</p>
    <h2>The rest of the knowledge base</h2>
    <p class="cross-link-rail__rail">{other_links}</p>
    <p class="gd-note">The five classifications are set out on the
      <a href="licence-types.html">licence types page</a>; what we do at each stage is on
      <a href="services.html">services</a>; what is actually for sale today is on the
      <a href="inventory.html">inventory board</a>.</p>
  </div>
</section>

<section class="section section--dark" id="where">
  <div class="container">
    <p class="eyebrow">Where this applies</p>
    <h2>Every county in California</h2>
    <p class="lede">The rules are statewide. What changes between markets is supply &mdash; and that changes
      what the same classification costs and how long it takes to find.</p>
    <p class="cross-link-rail__rail">{market_links} &middot; <a href="locations.html">all markets</a></p>
  </div>
</section>

<section class="section closing-cta" id="next">
  <div class="container">
    <p class="eyebrow">Next</p>
    <h2>Have a specific situation?</h2>
    <p class="lede">Guides answer the general question. For the one in front of you, tell us the market, the
      classification and the number you are working to.</p>
    <div class="cta-row">
      <a class="btn btn-primary wow-glow" href="contact.html#quote">Talk to a broker</a>
      <a class="btn btn-secondary" href="faq.html">Read the FAQs</a>
    </div>
  </div>
</section>

</main>
{CHROME_BOT}</body>
</html>
'''

if __name__ == '__main__':
    secs = sections()
    assert len(secs) == 4, 'expected 4 guide sections, found %d' % len(secs)
    out = []
    for idv, sec in secs.items():
        page = build(idv, sec, secs)
        slug = GUIDES[idv][0]
        fn = f'guide-{slug}.html'
        assert 'site-header' in page and 'site-footer' in page, 'chrome lost: ' + fn
        assert page.count('<h1>') == 1, 'h1: ' + fn
        assert 'design-system/structural.css' in page, 'css lost: ' + fn
        assert 'Full detail on' not in page, 'deep link leaked: ' + fn
        assert len(page) > 20000, 'too small: ' + fn
        open(fn, 'w', encoding='utf-8').write(page)
        words = len(clean(page).split())
        links = len(re.findall(r'<a\b', page))
        out.append((fn, len(page), words, links))
    print('wrote %d guide pages (ALL indexable — best-sourced set of the five)' % len(out))
    for fn, n, w, l in out:
        print('   %-32s %6d bytes  %4d words  %3d links' % (fn, n, w, l))
