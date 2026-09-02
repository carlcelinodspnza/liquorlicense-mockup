#!/usr/bin/env python3
"""
_build-type-page-layout.py -- [CJ] Hero A + Sections B across all 50 market x type pages.

OWNER PICKED 2026-09-02: "Hero A + Sections B", applied to the whole family.

MEASURED ON THE LIVE PAGE FIRST (liquor-license-san-francisco-type-20.html):
    six stacked single-column sections, ZERO images in <main>
    hero 741px, lede 715px of a 1200px container — 40% of the width empty
    the three middle bands share the IDENTICAL shape, which is what read as flat

HERO IMAGERY — 6 markets have a photograph, 4 do not
    los-angeles, orange, riverside, sacramento, san-bernardino, san-francisco
        -> their own lic-<market>.jpg                       (30 pages)
    fresno, san-diego, santa-barbara, ventura
        -> no market photograph exists, so the hero falls back to an image chosen
           by LICENCE CLASS, which is the page's other subject                (20 pages)

⚠ THE FALLBACK IS CONSTRAINED BY WHAT THE LICENCE PERMITS
    Types 20 and 21 are OFF-SALE. They authorise no on-premises consumption, so
    their fallback is a retail shelf image — never a bar or dining room, which
    would picture something the licence does not allow. Types 41/47/48 are
    on-sale and get a bar-room image. This is asserted in the run, not trusted.

SECTIONS B IS APPLIED WHERE THERE ARE BULLETS TO MOVE
    #authorizes on all 50, and #fit/#how on the 40 pages whose bands are a short
    lede plus a list. The ten Los Angeles and San Diego pages have 116-159 words
    of PROSE and no list in #fit/#how — those already carry the [CI] figure
    layout, which is the right treatment for prose. Content decides, not a sweep.

IDEMPOTENT -- guarded per section. Fails closed if a band's shape does not match,
if a mapped image is missing, or if any page loses words.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

MARKET_IMG = {
    'los-angeles':    ('assets/lic-losangeles.jpg',    'Los Angeles County retail frontage'),
    'orange':         ('assets/lic-orange.jpg',        'Orange County retail frontage'),
    'riverside':      ('assets/lic-riverside.jpg',     'Riverside County retail frontage'),
    'sacramento':     ('assets/lic-sacramento.jpg',    'Sacramento County retail frontage'),
    'san-bernardino': ('assets/lic-sanbernardino.jpg', 'San Bernardino County retail frontage'),
    'san-francisco':  ('assets/lic-sanfrancisco.jpg',  'A San Francisco street with retail frontage'),
}
OFF_SALE = {'20', '21'}
FALLBACK_OFF = ('assets/inventory-shelves.jpg', 'Shelves of sealed bottles in a retail store')
FALLBACK_ON  = ('assets/hero-bar-room.jpg',     'A bar room set for service')


def hero_image(market, ltype):
    if market in MARKET_IMG:
        return MARKET_IMG[market]
    return FALLBACK_OFF if ltype in OFF_SALE else FALLBACK_ON


def split_hero(inner, img, alt):
    h1 = re.search(r'<h1[^>]*>.*?</h1>', inner, re.S)
    lede = re.search(r'<p class="lede">.*?</p>', inner, re.S)
    if not (h1 and lede):
        return None
    eb = re.search(r'<p class="eyebrow">.*?</p>', inner, re.S)
    cta = re.search(r'<div class="cta-row">.*?</div>', inner, re.S)
    copy = ''
    if eb:  copy += '      %s\n' % eb.group(0)
    copy += '      %s\n      %s\n' % (h1.group(0), lede.group(0))
    if cta: copy += '      %s\n' % cta.group(0)
    return ('\n  <div class="container">\n'
            '    <div class="tp-hero__copy">\n%s    </div>\n'
            '    <figure class="tp-hero__media">\n'
            '      <img src="%s" alt="%s" width="1000" height="750" loading="eager" '
            'decoding="async">\n    </figure>\n  </div>\n' % (copy, img, alt))


def split_band(inner):
    eb = re.search(r'<p class="eyebrow">.*?</p>', inner, re.S)
    h2 = re.search(r'<h2[^>]*>.*?</h2>', inner, re.S)
    lede = re.search(r'<p class="lede">.*?</p>', inner, re.S)
    ul = re.search(r'<ul[^>]*>.*?</ul>', inner, re.S)
    # A trailing .tp-note sits AFTER the list on many of these bands and carries real
    # content — a cross-reference on #authorizes, a scheduling note on #how. The first
    # version of this transform dropped it and the word-count guard caught it on
    # liquor-license-fresno-type-20.html (-46 words). It travels with the list.
    note = re.search(r'<p class="tp-note">.*?</p>', inner, re.S)
    if not (h2 and ul):
        return None
    copy = ''
    if eb:   copy += '      %s\n' % eb.group(0)
    copy += '      %s\n' % h2.group(0)
    if lede: copy += '      %s\n' % lede.group(0)
    listcol = '      %s\n' % ul.group(0)
    if note: listcol += '      %s\n' % note.group(0)
    return ('\n  <div class="container">\n'
            '    <div class="tp-split__copy">\n%s    </div>\n'
            '    <div class="tp-split__list">\n%s    </div>\n  </div>\n'
            % (copy, listcol))


def words(html):
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).split())


def main():
    tally = {}
    def note(k): tally[k] = tally.get(k, 0) + 1

    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        mt = re.match(r'liquor-license-(.+)-type-(\d+)\.html$', name)
        if not mt:
            continue
        market, ltype = mt.group(1), mt.group(2)
        src = io.open(path, encoding='utf-8').read()
        before = words(src)
        out = src

        # ---- Hero A -------------------------------------------------------
        hero = re.search(r'<section([^>]*hero[^>]*)>(.*?)</section>', out, re.S)
        if hero and 'tp-hero' not in hero.group(1):
            img, alt = hero_image(market, ltype)
            if not os.path.exists(os.path.join(HERE, img)):
                print('FAIL: %s missing' % img, file=sys.stderr); sys.exit(1)
            if ltype in OFF_SALE and ('bar' in img or 'restaurant' in img):
                print('FAIL: %s is OFF-SALE and would get an on-premises image %s'
                      % (name, img), file=sys.stderr)
                sys.exit(1)
            body = split_hero(hero.group(2), img, alt)
            if body:
                new_open = '<section%s>' % hero.group(1)
                new_open = new_open.replace('class="', 'class="tp-hero ', 1)
                out = out.replace(hero.group(0), new_open + body + '</section>', 1)
                note('hero')
            else:
                note('hero-shape-skip')
        elif hero:
            note('hero-already')

        # ---- Sections B ---------------------------------------------------
        for sid in ('authorizes', 'fit', 'how'):
            m = re.search(r'<section([^>]*)id="%s"([^>]*)>(.*?)</section>' % sid, out, re.S)
            if not m:
                note('%s-absent' % sid); continue
            attrs = m.group(1) + m.group(2)
            if 'tp-split' in attrs:
                note('band-already'); continue
            if 'ca-fig' in attrs:
                note('band-is-figure-left-alone'); continue
            body = split_band(m.group(3))
            if not body:
                note('band-no-list'); continue
            open_tag = '<section%sid="%s"%s>' % (m.group(1), sid, m.group(2))
            if 'class="' not in open_tag:
                note('band-no-class'); continue
            out = out.replace(m.group(0),
                              open_tag.replace('class="', 'class="tp-split ', 1) + body + '</section>', 1)
            note('band')

        if out == src:
            continue
        if words(out) < before:
            print('FAIL: %s lost words %d -> %d' % (name, before, words(out)), file=sys.stderr)
            sys.exit(1)
        if out.count('<h1') != src.count('<h1'):
            print('FAIL: %s h1 count changed' % name, file=sys.stderr); sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(out)

    for k in sorted(tally):
        print('  %-28s %d' % (k, tally[k]))


if __name__ == '__main__':
    main()
