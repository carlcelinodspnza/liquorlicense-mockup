#!/usr/bin/env python3
"""
_build-type-hero-photo.py -- [CJ] rebuild the 50 market x type heroes as FULL-BLEED
photo heroes, using the design system's existing .hero--photo pattern.

WHY THIS REPLACES THE SPLIT HERO I BUILT FIRST
    The owner picked the full-bleed hero. I had shipped the split (copy left, image
    right) and they corrected it. Rather than invent a second full-bleed treatment,
    this reuses the pattern ALREADY on ten pages (about, faq, contact, index,
    inventory, …):

        <section class="... hero hero--photo hero--editorial section--dark ...">
          <div class="hero__media"><img … fetchpriority="high"></div>
          <div class="hero__scrim"></div>
          <div class="container"><div class="hero__inner"> … copy … </div></div>
        </section>

    That matters for three reasons that a bespoke version would have lost:
      - `.hero__scrim` is a DUAL GRADUATED VEIL built specifically so on-image text
        stays legible at every edge, including over a bright photo. It is a solved
        problem in this codebase; re-solving it would have been the risky path.
      - a `:has()` rule re-lights the eyebrow and headline accent to cream on photo
        heroes, because brand amber over a photograph is a contrast trap.
      - every existing photo hero carries `fetchpriority="high"` on the image, which
        is the LCP element. Copying the pattern inherits that.

    The bespoke `.tp-hero` CSS is REMOVED in the same change rather than left as dead
    rules that would quietly compete.

IMAGERY IS UNCHANGED from the previous pass and stays licence-safe: Types 20 and 21 are
OFF-SALE and never receive an on-premises image. Asserted below, not assumed.

IDEMPOTENT -- guarded on hero--photo. Fails closed on a shape mismatch or word loss.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIMS = {}                                  # filled from the existing markup
OFF_SALE = {'20', '21'}
ONPREM = ('bar-room', 'whiskey', 'restaurant', 'bars-nightclub', 'hotel', 'event')

IMG_SIZE = {
    'assets/lic-losangeles.jpg': (1024, 683), 'assets/lic-orange.jpg': (1024, 683),
    'assets/lic-riverside.jpg': (1024, 683), 'assets/lic-sacramento.jpg': (1024, 683),
    'assets/lic-sanbernardino.jpg': (1024, 683), 'assets/lic-sanfrancisco.jpg': (1024, 683),
    'assets/inventory-shelves.jpg': (1400, 933), 'assets/hero-bar-room.jpg': (2496, 1664),
}


def words(html):
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).split())


def main():
    done = skipped = 0
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        ltype = re.search(r'-type-(\d+)\.html$', name).group(1)
        src = io.open(path, encoding='utf-8').read()
        if 'hero--photo' in src:
            skipped += 1
            continue

        m = re.search(r'<section([^>]*tp-hero[^>]*)>(.*?)</section>', src, re.S)
        if not m:
            print('  SKIP %s: no .tp-hero to convert' % name); continue
        attrs, inner = m.group(1), m.group(2)

        img = re.search(r'<img src="(assets/[^"]+)" alt="([^"]*)"', inner)
        if not img:
            print('FAIL %s: hero image not found' % name, file=sys.stderr); sys.exit(1)
        src_img, alt = img.group(1), img.group(2)
        if ltype in OFF_SALE and any(k in src_img for k in ONPREM):
            print('FAIL %s: OFF-SALE page would carry an on-premises hero image %s'
                  % (name, src_img), file=sys.stderr)
            sys.exit(1)
        w, h = IMG_SIZE.get(src_img, (1400, 933))

        eb = re.search(r'<p class="eyebrow">.*?</p>', inner, re.S)
        h1 = re.search(r'<h1[^>]*>.*?</h1>', inner, re.S)
        lede = re.search(r'<p class="lede">.*?</p>', inner, re.S)
        cta = re.search(r'<div class="cta-row">.*?</div>', inner, re.S)
        if not (h1 and lede):
            print('FAIL %s: hero copy shape unexpected' % name, file=sys.stderr); sys.exit(1)

        copy = ''
        if eb:  copy += '        %s\n' % eb.group(0)
        copy += '        %s\n        %s\n' % (h1.group(0), lede.group(0))
        if cta: copy += '        %s\n' % cta.group(0)

        # rebuild the class list on the established pattern
        cls = re.search(r'class="([^"]*)"', attrs).group(1)
        cls = cls.replace('tp-hero', '').split()
        for need in ('section', 'hero', 'hero--photo', 'hero--editorial', 'section--dark'):
            if need not in cls:
                cls.append(need)
        new_attrs = re.sub(r'class="[^"]*"', 'class="%s"' % ' '.join(cls), attrs, count=1)

        body = ('\n  <div class="hero__media"><img src="%s" alt="%s" width="%d" height="%d" '
                'fetchpriority="high" decoding="async"></div>\n'
                '  <div class="hero__scrim"></div>\n'
                '  <div class="container">\n    <div class="hero__inner">\n%s'
                '    </div>\n  </div>\n' % (src_img, alt, w, h, copy))
        out = src.replace(m.group(0), '<section%s>%s</section>' % (new_attrs, body), 1)

        if words(out) < words(src):
            print('FAIL %s: lost words %d -> %d' % (name, words(src), words(out)), file=sys.stderr)
            sys.exit(1)
        if out.count('<h1') != src.count('<h1'):
            print('FAIL %s: h1 count changed' % name, file=sys.stderr); sys.exit(1)
        if 'hero__scrim' not in out or 'hero__media' not in out:
            print('FAIL %s: scrim or media missing after rebuild' % name, file=sys.stderr); sys.exit(1)

        io.open(path, 'w', encoding='utf-8').write(out)
        done += 1

    print('converted %d · already photo-hero %d' % (done, skipped))


if __name__ == '__main__':
    main()
