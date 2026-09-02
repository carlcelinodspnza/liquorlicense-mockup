#!/usr/bin/env python3
"""
_build-band-imagery.py -- [CL] add an image to #authorizes / #fit / #how on the 50
market x type pages.

OWNER ASKED for imagery in these three bands (2026-09-02).

⚠ THE MAPPING IS DRIVEN BY WHAT EACH LICENCE CLASS ACTUALLY PERMITS
    Types 20 and 21 are OFF-SALE: they authorise no on-premises consumption, so those
    pages only ever receive retail imagery. Types 41/47 are on-sale eating places and
    48 is on-sale public premises, so those get dining and bar imagery. Putting a bar
    photograph on a Type 20 page would picture something the licence forbids — the run
    ASSERTS this and exits rather than write it.

    #how is about the brokerage's process rather than the premises, so every page gets
    the same process image regardless of class or market.

NO IMAGE IS USED TWICE ON ONE PAGE
    The hero already carries an image, and on the four markets with no photograph of
    their own it falls back to inventory-shelves (off-sale) or hero-bar-room (on-sale).
    Neither of those appears in this table, so no page repeats a picture. Asserted per
    page before writing.

PLACEMENT: under the copy, not a third column. The bullet column is 630px and the copy
466px; a third column would have squeezed the bullets to ~420px and wrapped most of them
onto a second line, undoing the two-column band just approved.

IDEMPOTENT -- guarded on tp-split__media. Fails closed on a missing image, a duplicate
within a page, an off-sale/on-premises mismatch, or any word loss.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OFF_SALE = {'20', '21'}
ONPREM_TOKENS = ('restaurant', 'bars-nightclub', 'hotel', 'event', 'bar-room', 'whiskey')

# type -> {section: (image, alt)}
# type -> {section: [(image, alt), ...]} — ORDERED CANDIDATES, not one image.
# The [CI] figure rollout already put the FIRST candidate into #fit on the ten Los
# Angeles / San Diego pages, so #authorizes there must fall through to the second.
# Without candidates the same photograph appeared twice on one page — which is exactly
# what the first version of this file shipped before the duplicate audit caught it.
MAP = {
    '20': {
        'authorizes': [('assets/ind-convenience.jpg', 'A convenience store chiller stocked with beer and wine'),
                       ('assets/ind-grocery.jpg',     'A neighbourhood market aisle with a packaged beer and wine set')],
        'fit':        [('assets/ind-grocery.jpg',     'A neighbourhood market aisle with a packaged beer and wine set'),
                       ('assets/ind-convenience.jpg', 'A convenience store chiller stocked with beer and wine')],
    },
    '21': {
        'authorizes': [('assets/ind-liquor-stores.jpg', 'Shelves of spirits, beer and wine in an off-sale store'),
                       ('assets/ind-convenience.jpg',   'A convenience store chiller stocked with beer and wine')],
        'fit':        [('assets/ind-convenience.jpg',   'A convenience store chiller stocked with beer and wine'),
                       ('assets/ind-liquor-stores.jpg', 'Shelves of spirits, beer and wine in an off-sale store')],
    },
    '41': {
        'authorizes': [('assets/ind-restaurants.jpg', 'A restaurant dining room laid for service'),
                       ('assets/ind-hotels.jpg',      'A hotel bar and lounge set for guests')],
        'fit':        [('assets/ind-hotels.jpg',      'A hotel bar and lounge set for guests'),
                       ('assets/ind-restaurants.jpg', 'A restaurant dining room laid for service')],
    },
    '47': {
        'authorizes': [('assets/ind-restaurants.jpg',  'A restaurant dining room laid for service'),
                       ('assets/ind-event-venues.jpg', 'An event space set for a private function')],
        'fit':        [('assets/ind-event-venues.jpg', 'An event space set for a private function'),
                       ('assets/ind-restaurants.jpg',  'A restaurant dining room laid for service')],
    },
    '48': {
        'authorizes': [('assets/ind-bars-nightclubs.jpg', 'A bar counter under low light'),
                       ('assets/ind-hotels.jpg',          'A hotel bar and lounge set for guests')],
        'fit':        [('assets/ind-hotels.jpg',          'A hotel bar and lounge set for guests'),
                       ('assets/ind-bars-nightclubs.jpg', 'A bar counter under low light')],
    },
}
HOW_IMG = [('assets/hero-process.jpg', 'Licence paperwork and a pen on a broker’s desk')]


def words(html):
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).split())


def main():
    done = skipped = 0
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        ltype = re.search(r'-type-(\d+)\.html$', name).group(1)
        if ltype not in MAP:
            continue
        src = io.open(path, encoding='utf-8').read()
        if 'tp-split__media' in src:
            skipped += 1
            continue

        plan = dict(MAP[ltype])
        plan['how'] = HOW_IMG

        # Work out which bands will ACTUALLY receive an image before choosing any.
        # On the ten LA/San Diego pages #fit and #how are [CI] figure bands that already
        # carry one; picking for them first was what made the run fail.
        needs = []
        for sid in list(plan):
            sec = re.search(r'<section([^>]*)id="%s"([^>]*)>' % sid, src)
            if not sec:
                print('FAIL %s: #%s missing entirely' % (name, sid), file=sys.stderr); sys.exit(1)
            if 'ca-fig' in sec.group(1) + sec.group(2):
                continue
            needs.append(sid)
        if not needs:
            skipped += 1
            continue
        plan = {k: v for k, v in plan.items() if k in needs}

        # Every image ALREADY in <main> counts — the hero and, on the ten LA/San Diego
        # pages, the [CI] figures on #fit and #how. Skipping those was the bug that put
        # one photograph on a page twice.
        main = re.search(r'<main[^>]*>(.*?)</main>', src, re.S).group(1)
        used = set(re.findall(r'<img src="(assets/[^"]+)"', main))

        chosen = {}
        for sid, cands in plan.items():
            pick = None
            for img, alt in cands:
                if not os.path.exists(os.path.join(HERE, img)):
                    print('FAIL: %s missing' % img, file=sys.stderr); sys.exit(1)
                if ltype in OFF_SALE and any(t in img for t in ONPREM_TOKENS):
                    print('FAIL %s: OFF-SALE page would get on-premises image %s' % (name, img),
                          file=sys.stderr); sys.exit(1)
                if img in used:
                    continue
                pick = (img, alt); break
            if pick is None:
                print('FAIL %s: every candidate for #%s is already used on this page'
                      % (name, sid), file=sys.stderr); sys.exit(1)
            chosen[sid] = pick
            used.add(pick[0])
        plan = chosen

        out = src
        added = 0
        for sid, (img, alt) in plan.items():
            sec = re.search(r'<section([^>]*)id="%s"([^>]*)>' % sid, out)
            if not sec:
                print('FAIL %s: #%s missing entirely' % (name, sid), file=sys.stderr); sys.exit(1)
            # The ten Los Angeles / San Diego pages already carry the [CI] figure layout on
            # #fit and #how — those bands HAVE an image and are not .tp-split at all. Only
            # their #authorizes is a split band. Skip anything already illustrated rather
            # than forcing a second picture into it.
            if 'ca-fig' in sec.group(1) + sec.group(2):
                continue
            m = re.search(r'(<section[^>]*id="%s"[^>]*>.*?<div class="tp-split__copy">.*?)(\n\s*</div>)'
                          % sid, out, re.S)
            if not m:
                print('FAIL %s: #%s copy column not in its expected shape' % (name, sid),
                      file=sys.stderr); sys.exit(1)
            fig = ('\n      <figure class="tp-split__media">'
                   '<img src="%s" alt="%s" width="1024" height="576" loading="lazy" '
                   'decoding="async"></figure>' % (img, alt))
            out = out[:m.end(1)] + fig + out[m.end(1):]
            added += 1

        if added == 0:
            continue
        if words(out) < words(src):
            print('FAIL %s: lost words' % name, file=sys.stderr); sys.exit(1)
        if out.count('tp-split__media') != added:
            print('FAIL %s: expected %d band images, got %d'
                  % (name, added, out.count('tp-split__media')), file=sys.stderr); sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(out)
        done += 1

    print('imagery added to %d page(s) · already had it %d' % (done, skipped))


if __name__ == '__main__':
    main()
