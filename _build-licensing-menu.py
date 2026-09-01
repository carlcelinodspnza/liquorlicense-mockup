#!/usr/bin/env python3
"""
_build-licensing-menu.py -- [BZ] add the "How to get a liquor licence" entry to the
Licensing menu, and de-duplicate the process.html target while doing it.

WHY THIS ROW EXISTS
    The client's own nav parents its whole locations dropdown under a page called
    "How to Get a Liquor License" (/california/liquor-license/). Our header had no
    equivalent entry point at all.

WHY IT POINTS AT process.html AND NOT A NEW PAGE
    Their page was fetched and read: <main> is 695 words, has NO <h1>, an EMPTY meta
    description, ZERO internal links, and generic national copy in which the word
    "California" never appears. It answers three things -- what a licence costs, how long
    it takes, what documents are needed.

    We already answer all three, better and California-specific, and the dedup ledger
    already assigns them: the cost number is C28 (faq.html), the 60-120 day timeline is
    C16 (process.html), local approval and zoning is C14. process.html is the page that
    lays out the actual route in order and pointers out of every phase. Cloning their
    article would have meant restating three owned claims and importing figures we cannot
    source for California.

DE-DUPLICATION
    The Licensing list already had a row pointing at process.html ("Transfer timeline &
    escrow"). Two rows on one href is sloppy in a menu, so that row now targets the
    #phases section while the new row takes the page itself as the entry point.

IDEMPOTENT -- guarded on its own before/after text; re-running is a no-op.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

NEW_ROW = ('            <li><a role="menuitem" href="process.html">'
           '<span class="t">How to get a liquor licence</span>'
           '<span class="d">The route from consultation to ABC approval</span></a></li>\n')

# the row the new one is inserted ABOVE (currently first in the list)
ANCHOR = ('            <li><a role="menuitem" href="licence-types.html#type-21">'
          '<span class="t">Type 21 — Off-Sale General</span>'
          '<span class="d">Beer, wine and spirits for off-premises consumption</span></a></li>\n')

OLD_TRANSFER = ('<li><a role="menuitem" href="process.html">'
                '<span class="t">Transfer timeline &amp; escrow</span>'
                '<span class="d">Six phases, 60 to 120 days</span></a></li>')
NEW_TRANSFER = ('<li><a role="menuitem" href="process.html#phases">'
                '<span class="t">Transfer timeline &amp; escrow</span>'
                '<span class="d">Six phases, 60 to 120 days</span></a></li>')

MARKER = 'How to get a liquor licence'

# The Licensing row that points at locations.html still described it as California-only
# ("Statewide coverage / Local experts in all 58 counties"). locations.html is now six
# states, so that label contradicted its own destination. Retitled, not deleted -- the
# 58-county claim itself (C33) still lives on the page, where it is owned.
OLD_COVERAGE = ('<li><a role="menuitem" href="locations.html">'
                '<span class="t">Statewide coverage</span>'
                '<span class="d">Local experts in all 58 counties</span></a></li>')
NEW_COVERAGE = ('<li><a role="menuitem" href="locations.html">'
                '<span class="t">Where we broker</span>'
                '<span class="d">Six states, market by market</span></a></li>')
DRAWER_OLD_COVERAGE = None

# Mobile drawer parity: the Licensing accordion carries the same entry point, and its
# process.html row gets the same #phases anchor so the two are not the identical href.
DRAWER_ANCHOR = ('          <a href="licence-types.html#type-21">'
                 '<span class="mm-acc__ico">21</span>Type 21 \u2014 Off-Sale General</a>\n')
DRAWER_NEW = ('          <a href="process.html">'
              '<span class="mm-acc__ico">\u2192</span>How to get a liquor licence</a>\n')
DRAWER_OLD_TRANSFER = ('<a href="process.html">'
                       '<span class="mm-acc__ico">\u2192</span>Transfer timeline &amp; escrow</a>')
DRAWER_NEW_TRANSFER = ('<a href="process.html#phases">'
                       '<span class="mm-acc__ico">\u2192</span>Transfer timeline &amp; escrow</a>')


def main():
    done = skipped = missing = 0
    for f in sorted(glob.glob(os.path.join(HERE, '*.html'))):
        name = os.path.basename(f)
        src = io.open(f, encoding='utf-8').read()
        if 'id="mm-dd-licensing"' not in src:
            missing += 1
            continue
        if MARKER in src:
            skipped += 1
            continue
        if ANCHOR not in src:
            print('  FAIL %s: anchor row not found verbatim' % name, file=sys.stderr)
            sys.exit(1)
        src = src.replace(ANCHOR, NEW_ROW + ANCHOR, 1)
        if OLD_TRANSFER in src:
            src = src.replace(OLD_TRANSFER, NEW_TRANSFER, 1)
        else:
            print('  WARN %s: transfer row not in expected form' % name, file=sys.stderr)
        # drawer: same entry, same de-duplication. Order matters -- insert the new row
        # BEFORE retargeting the transfer row, or the new row's bare href would be the
        # one rewritten.
        if OLD_COVERAGE in src:
            src = src.replace(OLD_COVERAGE, NEW_COVERAGE, 1)
        if DRAWER_ANCHOR in src:
            src = src.replace(DRAWER_ANCHOR, DRAWER_NEW + DRAWER_ANCHOR, 1)
            if DRAWER_OLD_TRANSFER in src:
                src = src.replace(DRAWER_OLD_TRANSFER, DRAWER_NEW_TRANSFER, 1)
        else:
            print('  WARN %s: drawer licensing anchor not found' % name, file=sys.stderr)
        io.open(f, 'w', encoding='utf-8').write(src)
        done += 1
    print('stamped %d  ·  already had it %d  ·  no licensing menu %d' % (done, skipped, missing))


if __name__ == '__main__':
    main()
