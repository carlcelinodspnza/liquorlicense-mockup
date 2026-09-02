#!/usr/bin/env python3
"""
_build-service-selector.py -- [CF] rebuild services 05-08 as a thumbnail selector.
Option D, picked by the owner 2026-09-02. Replaces the media accordion built earlier
the same day.

WHY IT REPLACED MY OWN BUILD -- ON THE MEASUREMENTS, NOT ON TASTE
    All six candidates were measured at 1440 against the 2486px the band was originally:
        media accordion (what I had shipped)   548px   -78%
        THIS, thumbnail selector               437px   -82%   and keeps all four images
        text-only accordion, images DISCARDED  510px   -79%
    So the option that keeps the most content is also the shortest, and dropping the
    photographs to save space was never a real trade. I had built the accordion on the
    assumption that keeping images costs height; that assumption was wrong once the
    images become the interface.

⚠ THREE THINGS THIS FILE PROTECTS

    1. NO-JS. The panels are emitted WITHOUT `hidden`. With JS off all four render
       stacked -- degraded, but every service readable and every anchor lands. [CF] in
       site.js hides the inactive panels on init. Do not "optimise" by pre-hiding them
       in the markup; that turns a graceful degradation into three unreachable services.

    2. ANCHORS. ~1,283 inbound links point at #cup (432), #escrow (320),
       #new-business (319), #compliance (212). The id therefore goes on the PANEL, and
       [CF] selects the matching panel on load and on hashchange.

    3. THE PLACEHOLDER DISCLOSURE. Service 08 carries the page's only .trust-note --
       its copy is illustrative and awaiting the client's confirmation. Both the note and
       a dashed "Illustrative scope" flag are carried into the tab caption and the panel,
       so the disclosure is visible whether or not that service is the selected one.

CONTENT IS LIFTED, NEVER RETYPED -- parsed from the accordion this replaces.

IDEMPOTENT -- guarded on data-svc-selector. Fails closed unless it parses exactly four
rows, keeps four images and keeps the trust-note.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'services.html')
MARKER = 'data-svc-selector'

ROW = re.compile(
    r'<details class="svc-acc__row wow-reveal" id="([^"]+)"[^>]*>\s*'
    r'(<!--[^>]*-->)?\s*'
    r'<summary>\s*<span class="svc-acc__n">(\d+)</span>\s*'
    r'<span class="svc-acc__t">(.*?)</span>\s*'
    r'<span class="svc-acc__sign"[^>]*>\+</span>\s*</summary>\s*'
    r'<div class="svc-acc__body svc-acc__body--media">\s*'
    r'<div class="svc-acc__media">(<img [^>]*>)</div>\s*'
    r'<div>\s*(<p class="trust-note">.*?</p>\s*)?<p>(.*?)</p>\s*'
    r'<p class="sv-deep"><a href="([^"]+)">(.*?)</a></p>\s*</div>\s*'
    r'<div>\s*(?:<p class="feature-row__kicker">What this covers</p>\s*'
    r'(<ul class="feature-row__list">.*?</ul>)\s*)?'
    r'<div class="cta-row"><a class="btn btn-secondary" href="([^"]+)">(.*?)</a></div>\s*'
    r'</div>\s*</div>\s*</details>', re.S)


def main():
    src = io.open(TARGET, encoding='utf-8').read()
    if MARKER in src:
        print('already built (data-svc-selector present) — no-op')
        return

    start = src.find('<div class="svc-acc svc-acc--media">')
    if start < 0:
        print('FAIL: the media accordion is not in its expected form', file=sys.stderr)
        sys.exit(1)

    rows = list(ROW.finditer(src, start))
    if len(rows) != 4:
        print('FAIL: expected 4 rows, parsed %d — refusing to write' % len(rows), file=sys.stderr)
        sys.exit(1)

    tabs, panels = [], []
    for i, m in enumerate(rows):
        (sid, comment, num, title_html, img, trust, prose,
         dhref, dlabel, ul, chref, clabel) = m.groups()
        # the title span may already carry the placeholder flag — split it back out
        flag = ''
        fm = re.search(r'<span class="svc-acc__flag">(.*?)</span>', title_html or '')
        if fm:
            flag = fm.group(1)
        title = re.sub(r'<span class="svc-acc__flag">.*?</span>', '', title_html or '').strip()

        sel = 'true' if i == 0 else 'false'
        tabs.append(
            '          <button class="svc-sel__thumb" type="button" role="tab" id="tab-%s"\n'
            '                  aria-controls="%s" aria-selected="%s">\n'
            '            %s\n'
            '            <span class="svc-sel__cap">\n'
            '              <span class="svc-sel__kick">Service %s</span>\n'
            '              <span class="svc-sel__name">%s%s</span>\n'
            '            </span>\n'
            '          </button>\n'
            % (sid, sid, sel, img, num, title,
               (' <span class="svc-acc__flag">%s</span>' % flag) if flag else ''))

        right = ''
        if ul:
            right += ('            <p class="feature-row__kicker">What this covers</p>\n'
                      '            %s\n' % ul.strip())
        right += ('            <div class="cta-row"><a class="btn btn-secondary" href="%s">%s</a></div>\n'
                  % (chref, clabel.strip()))

        panels.append(
            '        <div class="svc-sel__panel" id="%s" role="tabpanel" aria-labelledby="tab-%s">\n'
            '          %s\n'
            '          <div>\n'
            '            <p class="feature-row__kicker">Service %s</p>\n'
            '            <h3>%s%s</h3>\n'
            '%s'
            '            <p>%s</p>\n'
            '            <p class="sv-deep"><a href="%s">%s</a></p>\n'
            '          </div>\n'
            '          <div>\n%s          </div>\n'
            '        </div>\n'
            % (sid, sid, comment or '', num, title,
               (' <span class="svc-acc__flag">%s</span>' % flag) if flag else '',
               ('            %s\n' % trust.strip()) if trust else '',
               prose.strip(), dhref, dlabel.strip(), right))

    block = ('<div class="svc-sel wow-reveal" data-svc-selector>\n'
             '        <div class="svc-sel__thumbs" role="tablist" aria-label="Services 05 to 08">\n'
             + ''.join(tabs) +
             '        </div>\n' + ''.join(panels) + '      </div>')

    end = src.find('</div>', rows[-1].end())
    if end < 0:
        print('FAIL: could not find the accordion close', file=sys.stderr); sys.exit(1)
    out = src[:start] + block + src[end + len('</div>'):]

    if 'svc-acc--media' in out:
        print('FAIL: the old accordion survived', file=sys.stderr); sys.exit(1)
    if out.count('<img') != src.count('<img'):
        print('FAIL: image count changed %d -> %d' % (src.count('<img'), out.count('<img')),
              file=sys.stderr); sys.exit(1)
    if 'trust-note' not in out:
        print('FAIL: the placeholder disclosure was lost', file=sys.stderr); sys.exit(1)
    if out.count('svc-sel__panel') != 4 or out.count('svc-sel__thumb"') != 4:
        print('FAIL: expected 4 tabs and 4 panels', file=sys.stderr); sys.exit(1)
    if 'hidden' in block:
        print('FAIL: a panel was pre-hidden in the markup — that breaks the no-JS path',
              file=sys.stderr); sys.exit(1)

    io.open(TARGET, 'w', encoding='utf-8').write(out)
    print('rebuilt selector: %d tabs / %d panels (ids: %s)'
          % (len(tabs), len(panels), ', '.join(m.group(1) for m in rows)))


if __name__ == '__main__':
    main()
