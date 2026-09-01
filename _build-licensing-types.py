#!/usr/bin/env python3
"""
_build-licensing-types.py -- [CC] drop the individual licence TYPES from the Licensing menu.

WHY
    Owner: "Licensing types should not be shown here as licenses differ for every location."
    The menu is site-wide chrome. Listing Type 21 / 47 / 48 there presents California ABC
    classifications as if they were universal, and they are not — Arizona issues Series
    6/7/9/10/11/12, Florida issues 1COP/2COP/3PS/4COP/6COP, and New Jersey, Ohio and
    Pennsylvania each use their own system entirely. Those three rows are replaced by ONE
    that names the state it belongs to, so licence-types.html stays reachable without the
    menu asserting a national classification scheme.

    The preview pane moves with them: it previewed Type 47, so it now previews the
    classifications page. Its watermark becomes the "§" that site.js [AM] already emits for
    non-numbered items — which is exactly the case that glyph exists for.

TWO CONSEQUENCES HANDLED
    1. The ledger drops from 10 rows to 8. `#mm-dd-licensing > ul` was authored for
       `repeat(5, 1fr)` with `li:nth-child(9)` spanning both columns; at 8 items that
       leaves an empty fifth row and the span rule matches nothing.
    2. The drawer accordion carried the same three rows and gets the same treatment.

IDEMPOTENT -- guarded on its own marker.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = '<span class="t">Licence classifications</span>'

DESK_OLD = (
    '            <li><a role="menuitem" href="licence-types.html#type-21"><span class="t">Type 21 — Off-Sale General</span><span class="d">Beer, wine and spirits for off-premises consumption</span></a></li>\n'
    '            <li><a role="menuitem" href="licence-types.html#type-47"><span class="t">Type 47 — On-Sale, Eating Place</span><span class="d">Full liquor at a bona fide eating place</span></a></li>\n'
    '            <li><a role="menuitem" href="licence-types.html#type-48"><span class="t">Type 48 — Public Premises</span><span class="d">Bars and nightclubs; minors prohibited</span></a></li>\n')
DESK_NEW = (
    '            <li><a role="menuitem" href="licence-types.html"><span class="t">Licence classifications</span>'
    '<span class="d">Set by each state &mdash; California ABC issues Types 20, 21, 41, 47 and 48</span></a></li>\n')

PREV_OLD = ('<a class="mm-dd-preview" href="licence-types.html#type-47" tabindex="-1" aria-hidden="true">\n'
            '            <span class="mm-dd-preview__mark" data-kind="num">47</span>\n'
            '            <span class="mm-dd-preview__t">Type 47 — On-Sale, Eating Place</span>\n'
            '            <span class="mm-dd-preview__d">Full liquor at a bona fide eating place</span>')
PREV_NEW = ('<a class="mm-dd-preview" href="licence-types.html" tabindex="-1" aria-hidden="true">\n'
            '            <span class="mm-dd-preview__mark" data-kind="neutral">&sect;</span>\n'
            '            <span class="mm-dd-preview__t">Licence classifications</span>\n'
            '            <span class="mm-dd-preview__d">Set by each state &mdash; not one national scheme</span>')

DRAW_OLD = (
    '          <a href="licence-types.html#type-21"><span class="mm-acc__ico">21</span>Type 21 — Off-Sale General</a>\n'
    '          <a href="licence-types.html#type-47"><span class="mm-acc__ico">47</span>Type 47 — On-Sale, Eating Place</a>\n'
    '          <a href="licence-types.html#type-48"><span class="mm-acc__ico">48</span>Type 48 — Public Premises</a>\n')
DRAW_NEW = '          <a href="licence-types.html"><span class="mm-acc__ico">&sect;</span>Licence classifications</a>\n'


def main():
    done = skipped = nomenu = warn = 0
    for f in sorted(glob.glob(os.path.join(HERE, '*.html'))):
        name = os.path.basename(f)
        src = io.open(f, encoding='utf-8').read()
        if 'id="mm-dd-licensing"' not in src:
            nomenu += 1
            continue
        if MARKER in src:
            skipped += 1
            continue
        if DESK_OLD not in src:
            print('  FAIL %s: the three type rows are not in the expected form' % name, file=sys.stderr)
            sys.exit(1)
        src = src.replace(DESK_OLD, DESK_NEW, 1)
        for old, new, what in ((PREV_OLD, PREV_NEW, 'preview pane'), (DRAW_OLD, DRAW_NEW, 'drawer')):
            if old in src:
                src = src.replace(old, new, 1)
            else:
                print('  WARN %s: %s not in expected form' % (name, what), file=sys.stderr)
                warn += 1
        io.open(f, 'w', encoding='utf-8').write(src)
        done += 1
    print('stamped %d  ·  already had it %d  ·  no licensing menu %d  ·  warnings %d'
          % (done, skipped, nomenu, warn))


if __name__ == '__main__':
    main()
