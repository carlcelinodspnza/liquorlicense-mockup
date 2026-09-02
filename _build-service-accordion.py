#!/usr/bin/env python3
"""
_build-service-accordion.py -- [CE] rebuild the "Moving a licence between owners" band
(services 01-04) as four <details> rows. Option A, picked by the owner 2026-09-02.

MEASURED BEFORE PICKING, NOT AFTER
    The live band was 1201px at 1440 (first row top to last row bottom). Closed, the
    accordion is 271px -- a 77% cut. Those numbers were put in front of the owner with
    the options, including the two options that turned out TALLER than the current band.

WHY NATIVE <details> AND NOT A JS WIDGET
    Keyboard operable and screen-reader announced for free, works with JS disabled, and
    the copy stays in the DOM so nothing is hidden from indexing.

⚠ THE ANCHORS ARE THE WHOLE RISK HERE
    ~1,285 links across the site point at #buy / #sell / #transfer / #valuation (323 at
    #buy alone). If those ids stayed on a wrapper and the row defaulted closed, every one
    of those links would land the visitor on a heading with nothing under it. So:
      - the id moves ONTO the <details> element, and
      - [CE] in site.js opens the targeted row on load and on hashchange.
    The first row also ships open, so a visitor arriving with no hash sees content.

CONTENT IS LIFTED, NEVER RETYPED
    Prose, bullets, both links and the kicker are parsed out of the existing markup, so
    this inherits the de-Californised copy already in the page.

IDEMPOTENT -- guarded on .svc-acc. Fails closed unless it parses exactly four rows.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'services.html')
MARKER = 'svc-acc'

ROW = re.compile(
    r'<div class="cap-showcase__row wow-reveal" id="([^"]+)">\s*'
    r'(<!--[^>]*-->)?\s*'
    r'<div class="feature-row__body">\s*'
    r'<p class="feature-row__kicker">(Service \d+)</p>\s*<h3>(.*?)</h3>\s*'
    r'<p class="sv-deep"><a href="([^"]+)">(.*?)</a></p>\s*'
    r'<p>(.*?)</p>\s*</div>\s*'
    r'<div class="feature-row__body">\s*'
    r'<p class="feature-row__kicker">What this covers</p>\s*'
    r'<ul class="feature-row__list">(.*?)</ul>\s*'
    r'<div class="cta-row"><a class="btn btn-secondary" href="([^"]+)">(.*?)</a></div>\s*'
    r'</div>\s*</div>', re.S)


def main():
    src = io.open(TARGET, encoding='utf-8').read()
    if MARKER in src:
        print('already built (.svc-acc present) — no-op')
        return

    rows = list(ROW.finditer(src))
    if len(rows) != 4:
        print('FAIL: expected 4 rows, parsed %d — refusing to write' % len(rows), file=sys.stderr)
        sys.exit(1)

    out_rows = []
    for i, m in enumerate(rows):
        sid, comment, kicker, title, dhref, dlabel, prose, ul, chref, clabel = m.groups()
        num = kicker.split()[-1]
        bullets = re.findall(r'<li>(.*?)</li>', ul, re.S)
        if not bullets:
            print('FAIL: %s has no bullets' % sid, file=sys.stderr); sys.exit(1)
        lis = '\n'.join('            <li>%s</li>' % b.strip() for b in bullets)
        out_rows.append(
            '      <details class="svc-acc__row wow-reveal" id="%s"%s>\n'
            '        %s\n'
            '        <summary>\n'
            '          <span class="svc-acc__n">%s</span>\n'
            '          <span class="svc-acc__t">%s</span>\n'
            '          <span class="svc-acc__sign" aria-hidden="true">+</span>\n'
            '        </summary>\n'
            '        <div class="svc-acc__body">\n'
            '          <div>\n'
            '            <p>%s</p>\n'
            '            <p class="sv-deep"><a href="%s">%s</a></p>\n'
            '          </div>\n'
            '          <div>\n'
            '            <p class="feature-row__kicker">What this covers</p>\n'
            '            <ul class="feature-row__list">\n%s\n            </ul>\n'
            '            <div class="cta-row"><a class="btn btn-secondary" href="%s">%s</a></div>\n'
            '          </div>\n'
            '        </div>\n'
            '      </details>\n'
            % (sid, ' open' if i == 0 else '', comment or '', num, title.strip(),
               prose.strip(), dhref, dlabel.strip(), lis, chref, clabel.strip()))

    # replace the contiguous span from the first row to the last
    start, end = rows[0].start(), rows[-1].end()
    block = '<div class="svc-acc">\n' + ''.join(out_rows) + '    </div>'
    out = src[:start] + block + src[end:]

    if 'cap-showcase__row' in out:
        print('FAIL: an old row survived the swap', file=sys.stderr); sys.exit(1)
    if out.count('svc-acc__row') != 4:
        print('FAIL: expected 4 rows written, got %d' % out.count('svc-acc__row'), file=sys.stderr)
        sys.exit(1)

    io.open(TARGET, 'w', encoding='utf-8').write(out)
    print('rebuilt %d accordion rows (ids: %s)'
          % (len(rows), ', '.join(m.group(1) for m in rows)))


if __name__ == '__main__':
    main()
