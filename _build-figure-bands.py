#!/usr/bin/env python3
"""
_build-figure-bands.py -- [CI] roll the F layout (measured prose left, apt figure right)
out from california-liquor-license-services.html to the other pages it genuinely fits.

OWNER INSTRUCTION (2026-09-02): apply the changes made on the California services page
to all applicable pages.

WHAT "APPLICABLE" TURNED OUT TO MEAN — surveyed, not assumed
    64 sections across 52 pages carry a <p class="lede"> of 90+ words. That is NOT the
    applicable set. Filtering it down:

    -40  HERO sections. They carry the page <h1> and class hero--editorial, a different
         design language entirely. F was built for BODY bands. Excluded.
    -3   new-jersey / pennsylvania #about-* bands. No state-specific imagery exists and
         nothing in assets/ is honestly "about New Jersey". A figure layout with a
         decorative stock photo would be filler. Excluded and reported.
    = 21 body bands across 11 pages, all with imagery that is actually ABOUT the section.

IMAGERY IS MAPPED FROM THE SITE'S OWN CLASSIFICATION SEMANTICS, NOT PICKED BY VIBE
    The licence classes, per the site's own list:
        Type 20  Off-Sale Beer & Wine        -> a convenience retail image
        Type 21  Off-Sale General            -> a liquor-store image
        Type 41  On-Sale Beer & Wine, Eating -> a restaurant image
        Type 47  On-Sale General, Eating     -> a restaurant image
        Type 48  On-Sale General, Public     -> a bar image
    An OFF-sale page must never get an on-premises bar photograph — that would picture
    something the licence does not permit. This mapping is the reason the rollout is
    safe to automate at all.

    #how ("How we work it") is about the brokerage's process rather than the premises,
    so every one of those gets the process image regardless of market.

REUSES [CI] CSS — no new styles. The .ca-fig rules already shipped for the California
page cover these bands exactly.

IDEMPOTENT -- guarded per section on ca-fig. Fails closed if a band lacks an eyebrow,
an h2 or a lede, or if its mapped image is missing from disk.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

TYPE_IMG = {
    '20': ('assets/ind-convenience.jpg',
           'A convenience store chiller stocked with beer and wine'),
    '21': ('assets/ind-liquor-stores.jpg',
           'Shelves of spirits in an off-sale liquor store'),
    '41': ('assets/ind-restaurants.jpg',
           'A restaurant dining room laid for service'),
    '47': ('assets/ind-restaurants.jpg',
           'A restaurant dining room laid for service'),
    '48': ('assets/ind-bars-nightclubs.jpg',
           'A bar counter under low light'),
}
HOW_IMG = ('assets/hero-process.jpg', 'Paperwork and a pen on a broker’s desk')


def transform(inner):
    """eyebrow + h2 + lede(s) -> the .ca-fig two-column shape. None if it does not fit."""
    eb = re.search(r'<p class="eyebrow">(.*?)</p>', inner, re.S)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', inner, re.S)
    ledes = re.findall(r'<p class="lede">(.*?)</p>', inner, re.S)
    if not (eb and h2 and ledes):
        return None
    return eb.group(1).strip(), h2.group(1).strip(), [l.strip() for l in ledes]


def build(eb, h2, ledes, img, alt):
    copy = '\n'.join('        <p class="lede">%s</p>' % l for l in ledes)
    return ('\n  <div class="container">\n'
            '    <div class="ca-fig__copy">\n'
            '      <p class="eyebrow">%s</p>\n      <h2>%s</h2>\n%s\n'
            '    </div>\n'
            '    <figure class="ca-fig__figure">\n'
            '      <img src="%s" alt="%s" width="512" height="512" loading="lazy" decoding="async">\n'
            '      <figcaption>%s</figcaption>\n'
            '    </figure>\n'
            '  </div>\n' % (eb, h2, copy, img, alt, eb))


def apply_to(path, sid, img, alt, min_words):
    src = io.open(path, encoding='utf-8').read()
    m = re.search(r'<section([^>]*)id="%s"([^>]*)>(.*?)</section>' % sid, src, re.S)
    if not m:
        return 'no-section'
    if 'ca-fig' in m.group(1) or 'ca-fig' in m.group(2):
        return 'already'
    if re.search(r'<h1[\s>]', m.group(3)) or 'hero' in m.group(1):
        return 'hero-skip'
    t = transform(m.group(3))
    if not t:
        return 'shape-mismatch'
    eb, h2, ledes = t
    words = sum(len(re.sub(r'<[^>]+>', '', l).split()) for l in ledes)
    if words < min_words:
        return 'too-short'
    if not os.path.exists(os.path.join(HERE, img)):
        print('FAIL: image %s missing' % img, file=sys.stderr); sys.exit(1)

    open_tag = '<section%sid="%s"%s>' % (m.group(1), sid, m.group(2))
    if 'class="' not in open_tag:
        return 'no-class'
    new = open_tag.replace('class="', 'class="ca-fig ', 1) + build(eb, h2, ledes, img, alt) + '</section>'
    out = src.replace(m.group(0), new, 1)

    # nothing may be lost
    def words_of(h):
        mm = re.search(r'<main[^>]*>(.*?)</main>', h, re.S)
        return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', mm.group(1))).split())
    if words_of(out) < words_of(src):
        print('FAIL: %s #%s lost words' % (os.path.basename(path), sid), file=sys.stderr)
        sys.exit(1)
    if out.count('<h1') != src.count('<h1'):
        print('FAIL: %s h1 count changed' % os.path.basename(path), file=sys.stderr); sys.exit(1)

    io.open(path, 'w', encoding='utf-8').write(out)
    return 'done'


def main():
    tally = {}
    def note(k): tally[k] = tally.get(k, 0) + 1

    # 1. california-liquor-license-services.html #services is NOT converted.
    #    It looked like "the last single-column band" but it is ALREADY the two-column
    #    .svc-split component, carrying an eight-service .svc-grid, a tp-note and a CTA
    #    beside the copy. It never had the empty-half problem, and rebuilding it as a
    #    figure band would have destroyed that grid. The word-count guard caught this
    #    on the first run and refused to write — which is exactly why it is there.

    # 2. the market x type pages that carry #fit / #how body bands
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        t = re.search(r'-type-(\d+)\.html$', path)
        if not t or t.group(1) not in TYPE_IMG:
            continue
        img, alt = TYPE_IMG[t.group(1)]
        note(apply_to(path, 'fit', img, alt, 90))
        note(apply_to(path, 'how', HOW_IMG[0], HOW_IMG[1], 90))

    for k in sorted(tally):
        print('  %-16s %d' % (k, tally[k]))
    print('  CONVERTED: %d band(s)' % tally.get('done', 0))


if __name__ == '__main__':
    main()
