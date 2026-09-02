#!/usr/bin/env python3
"""
_build-service-accordion-media.py -- [CE] collapse services 05-08 into the same
accordion as 01-04, KEEPING each row's photograph.

WHY
    Owner, 2026-09-02: "make this section look more compact." MEASURED first: the
    05-08 band spans 2486px at 1440, the tallest on the page, because each row paints
    its image at 544x512 (one at 544x756). It is more than twice the 1201px that the
    01-04 band was before it became an accordion.

WHY THE IMAGES SURVIVE
    Four real photographs sit in these rows. Collapsing to a plain accordion would have
    thrown them away, which is a content decision, not a layout one. Instead the image
    moves INSIDE the open body at ~200px, so the band collapses and nothing is lost.
    If the owner would rather drop them for a tighter open state, that is a one-line
    change here -- but it is theirs to make, not mine.

⚠ TWO THINGS THIS FILE EXISTS TO PROTECT

    1. ANCHORS. ~1,283 inbound links point at #cup (432), #compliance (212),
       #escrow (320) and #new-business (319). The id therefore goes ON the <details>,
       and [CE] in site.js was changed from querySelector to querySelectorAll first --
       a singular lookup would have found only the 01-04 container and silently
       stranded every one of these.

    2. THE PLACEHOLDER DISCLOSURE. Service 08 carries a .trust-note saying its copy is
       illustrative and awaiting the client's confirmation, and it is the only service
       with no source text behind it. Collapsing the row would hide that disclosure
       along with the draft copy, so the summary gets a visible dashed "Illustrative
       scope" flag that shows even when the row is CLOSED.

SHAPE DIFFERENCES HANDLED, NOT ASSUMED AWAY
    05/06/07 have a bullet list; 08 has none and has the trust-note instead. The parser
    treats both as optional and the row is built from whatever is actually present.

IDEMPOTENT -- guarded on svc-acc--media. Fails closed unless it parses exactly four rows.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'services.html')
MARKER = 'svc-acc--media'

ROW = re.compile(
    r'<div class="feature-row wow-reveal" id="([^"]+)">\s*'
    r'<div class="feature-row__media wow-zoom">(<img [^>]*>)</div>\s*'
    r'(<!--[^>]*-->)?\s*'
    r'<div class="feature-row__body">\s*'
    r'<p class="feature-row__kicker">(Service \d+)</p>\s*<h3>(.*?)</h3>\s*'
    r'<p class="sv-deep"><a href="([^"]+)">(.*?)</a></p>\s*'
    r'(<p class="trust-note">.*?</p>\s*)?'
    r'<p>(.*?)</p>\s*'
    r'(<ul class="feature-row__list">.*?</ul>\s*)?'
    r'<div class="cta-row"><a class="btn btn-secondary" href="([^"]+)">(.*?)</a></div>\s*'
    r'</div>\s*</div>', re.S)


def main():
    src = io.open(TARGET, encoding='utf-8').read()
    if MARKER in src:
        print('already built (svc-acc--media present) — no-op')
        return

    rows = list(ROW.finditer(src))
    if len(rows) != 4:
        print('FAIL: expected 4 rows, parsed %d — refusing to write' % len(rows), file=sys.stderr)
        sys.exit(1)

    out_rows = []
    for i, m in enumerate(rows):
        (sid, img, comment, kicker, title, dhref, dlabel,
         trust, prose, ul, chref, clabel) = m.groups()
        num = kicker.split()[-1]
        # the image loses its decorative wrapper but keeps every attribute it had
        img_tag = img.replace('width="1000" height="756"', 'width="1000" height="756"')
        flag = ('<span class="svc-acc__flag">Illustrative scope</span>' if trust else '')
        right = ''
        if ul:
            right += '            <p class="feature-row__kicker">What this covers</p>\n            %s\n' % ul.strip()
        right += ('            <div class="cta-row"><a class="btn btn-secondary" href="%s">%s</a></div>\n'
                  % (chref, clabel.strip()))
        out_rows.append(
            '      <details class="svc-acc__row wow-reveal" id="%s"%s>\n'
            '        %s\n'
            '        <summary>\n'
            '          <span class="svc-acc__n">%s</span>\n'
            '          <span class="svc-acc__t">%s%s</span>\n'
            '          <span class="svc-acc__sign" aria-hidden="true">+</span>\n'
            '        </summary>\n'
            '        <div class="svc-acc__body svc-acc__body--media">\n'
            '          <div class="svc-acc__media">%s</div>\n'
            '          <div>\n'
            '%s'
            '            <p>%s</p>\n'
            '            <p class="sv-deep"><a href="%s">%s</a></p>\n'
            '          </div>\n'
            '          <div>\n%s          </div>\n'
            '        </div>\n'
            '      </details>\n'
            % (sid, ' open' if i == 0 else '', comment or '', num, title.strip(), flag,
               img_tag, ('            %s\n' % trust.strip()) if trust else '',
               prose.strip(), dhref, dlabel.strip(), right))

    start, end = rows[0].start(), rows[-1].end()
    block = '<div class="svc-acc svc-acc--media">\n' + ''.join(out_rows) + '    </div>'
    out = src[:start] + block + src[end:]

    if 'feature-row wow-reveal' in out:
        print('FAIL: an old row survived the swap', file=sys.stderr); sys.exit(1)
    if out.count('svc-acc--media') != 1:
        print('FAIL: marker count wrong', file=sys.stderr); sys.exit(1)
    if 'trust-note' not in out:
        print('FAIL: the placeholder disclosure was lost', file=sys.stderr); sys.exit(1)
    if out.count('<img') != src.count('<img'):
        print('FAIL: image count changed %d -> %d' % (src.count('<img'), out.count('<img')),
              file=sys.stderr); sys.exit(1)

    io.open(TARGET, 'w', encoding='utf-8').write(out)
    print('rebuilt %d media accordion rows (ids: %s)'
          % (len(rows), ', '.join(m.group(1) for m in rows)))


if __name__ == '__main__':
    main()
