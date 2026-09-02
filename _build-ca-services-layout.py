#!/usr/bin/env python3
"""
_build-ca-services-layout.py -- [CI] restructure the prose bands on
california-liquor-license-services.html.

OWNER PICKED, 2026-09-02, from the measured options round:
    F  for the two LONG bands   -> Qualification (166 words), Consulting (199)
    E  for the three SHORT ones -> Corporate (77), Classifications (15+5 links),
                                   Coverage (18) — merged into ONE row of cards

WHAT WAS ACTUALLY WRONG
    Measured live before any of this: the five bands ran to 2998px and the text
    column occupied 633px of a 1200px container — 47% of the width sat empty. The
    long paragraphs sit inside <p class="lede">, a class meant for a SHORT intro,
    which is WHY they rendered at that measure. Missing pictures were the symptom;
    the misused class was the cause. F fixes the cause by giving the copy a real
    62ch measure and putting a figure in the space that was empty.

NOTHING IS RETYPED, NOTHING IS INVENTED
    Every paragraph, list item, note and CTA is parsed out of the existing markup and
    re-emitted. The five classification links and their trailing note survive intact,
    and so does the coverage band's "See every market we cover" button — the options
    mock-up had dropped that button, and it is restored here deliberately.

ANCHORS CHECKED FIRST
    #corporate, #classifications and #where have ZERO inbound links anywhere on the
    site, so merging those three sections into one breaks nothing. Their ids are kept
    on the individual cards anyway, as cheap insurance. (#services has 1 inbound link
    and is NOT touched — see below.)

DELIBERATELY OUT OF SCOPE
    The "Brokerage" band (#services, 127 words) was in NEITHER group the owner chose
    between, so it is left exactly as it is rather than being swept in. It is flagged
    to the owner instead.

IDEMPOTENT -- guarded on .ca-fig / .ca-cards. Fails closed if a band cannot be parsed.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'california-liquor-license-services.html')

FIGS = {
    'qualification': ('assets/escrow-signing.jpg',
                      'A hand signing a transfer document with a fountain pen'),
    'consulting':    ('assets/compliance-gavel.jpg',
                      'A gavel, law books and a legal document on a desk'),
}
CARD_IMG = {
    'corporate':       ('assets/hero-about.jpg', 'The brokerage team at work'),
    'classifications': ('assets/hero-licence-types.jpg', 'Bottles arranged behind a bar by classification'),
    'where':           ('assets/coverage-california-map.jpg', 'A map of the California markets served'),
}


def grab(src, sid):
    m = re.search(r'<section([^>]*)id="%s"([^>]*)>(.*?)</section>' % sid, src, re.S)
    if not m:
        print('FAIL: #%s not found' % sid, file=sys.stderr); sys.exit(1)
    return m


def parts(inner):
    eb = re.search(r'<p class="eyebrow">(.*?)</p>', inner, re.S)
    h2 = re.search(r'<h2[^>]*>(.*?)</h2>', inner, re.S)
    body = re.findall(r'<p class="lede">(.*?)</p>', inner, re.S)
    ul = re.search(r'<ul class="tp-points"[^>]*>.*?</ul>', inner, re.S)
    note = re.search(r'<p class="tp-note">.*?</p>', inner, re.S)
    cta = re.search(r'<div class="cta-row">.*?</div>', inner, re.S)
    return (eb.group(1).strip() if eb else '',
            h2.group(1).strip() if h2 else '',
            [b.strip() for b in body],
            ul.group(0) if ul else '',
            note.group(0) if note else '',
            cta.group(0) if cta else '')


def main():
    src = io.open(TARGET, encoding='utf-8').read()
    if 'ca-fig' in src or 'ca-cards' in src:
        print('already built — no-op')
        return

    out = src

    # ---- F on the two long bands ----------------------------------------
    for sid, (img, alt) in FIGS.items():
        m = grab(out, sid)
        a1, a2, inner = m.group(1), m.group(2), m.group(3)
        eb, h2, body, _, _, _ = parts(inner)
        if not body:
            print('FAIL: #%s has no prose to lay out' % sid, file=sys.stderr); sys.exit(1)
        copy = '\n'.join('        <p class="lede">%s</p>' % b for b in body)
        new_inner = (
            '\n  <div class="container">\n'
            '    <div class="ca-fig__copy">\n'
            '      <p class="eyebrow">%s</p>\n      <h2>%s</h2>\n%s\n'
            '    </div>\n'
            '    <figure class="ca-fig__figure">\n'
            '      <img src="%s" alt="%s" width="512" height="512" loading="lazy" decoding="async">\n'
            '      <figcaption>%s</figcaption>\n'
            '    </figure>\n'
            '  </div>\n' % (eb, h2, copy, img, alt, eb))
        open_tag = '<section%sid="%s"%s>' % (a1, sid, a2)
        if 'class="' not in open_tag:
            print('FAIL: #%s has no class attribute' % sid, file=sys.stderr); sys.exit(1)
        new_open = open_tag.replace('class="', 'class="ca-fig ', 1)
        out = out.replace(m.group(0), new_open + new_inner + '</section>', 1)

    # ---- E: merge the three short bands into one card row ----------------
    cards = []
    first_open = None
    for sid in ('corporate', 'classifications', 'where'):
        m = grab(out, sid)
        if first_open is None:
            first_open = m
        eb, h2, body, ul, note, cta = parts(m.group(3))
        img, alt = CARD_IMG[sid]
        inner = ''
        for b in body:
            inner += '          <p>%s</p>\n' % b
        if ul:
            inner += '          %s\n' % ul
        if note:
            inner += '          %s\n' % note
        foot = ('          <div class="ca-card__foot">%s</div>\n' % cta) if cta else ''
        cards.append(
            '        <article class="ca-card" id="%s">\n'
            '          <div class="ca-card__img"><img src="%s" alt="%s" width="512" height="512" '
            'loading="lazy" decoding="async"></div>\n'
            '          <div class="ca-card__in">\n'
            '            <p class="eyebrow">%s</p>\n            <h3>%s</h3>\n%s%s'
            '          </div>\n        </article>\n' % (sid, img, alt, eb, h2, inner, foot))

    row = ('<section class="section ca-cards">\n  <div class="container">\n'
           '    <div class="ca-cards__grid">\n' + ''.join(cards) +
           '    </div>\n  </div>\n</section>')

    # replace the first of the three, delete the other two
    secs = [grab(out, s).group(0) for s in ('corporate', 'classifications', 'where')]
    out = out.replace(secs[0], row, 1)
    for s in secs[1:]:
        out = out.replace(s, '', 1)

    # ---- fail-closed checks --------------------------------------------
    for need, why in [
            ('ca-fig', 'F layout missing'),
            ('ca-cards__grid', 'card row missing'),
            ('See every market we cover', 'the coverage CTA was dropped'),
            ('tp-points', 'the classification links were dropped'),
            ('tp-note', 'the classification note was dropped')]:
        if need not in out:
            print('FAIL: %s' % why, file=sys.stderr); sys.exit(1)
    if out.count('class="ca-card"') != 3:
        print('FAIL: expected 3 cards, got %d' % out.count('class="ca-card"'), file=sys.stderr)
        sys.exit(1)
    if out.count('licence-type-') < src.count('licence-type-'):
        print('FAIL: classification links lost', file=sys.stderr); sys.exit(1)
    if out.count('<h1') != 1:
        print('FAIL: h1 count changed', file=sys.stderr); sys.exit(1)

    io.open(TARGET, 'w', encoding='utf-8').write(out)
    print('rebuilt: 2 figure bands (F) + 3 bands merged into 1 card row (E)')


if __name__ == '__main__':
    main()
