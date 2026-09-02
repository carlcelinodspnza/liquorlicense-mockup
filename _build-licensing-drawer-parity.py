#!/usr/bin/env python3
"""
_build-licensing-drawer-parity.py -- [CG] give the mobile Licensing drawer the same
eight options the desktop mega-menu has.

HOW THIS WAS FOUND
    Not by looking. While repointing the Licensing rows at individual pages, two of the
    drawer patterns matched ZERO and the generator failed closed. That is what surfaced
    the real defect: the desktop Licensing menu has EIGHT rows, the mobile drawer had
    THREE. Five destinations were unreachable on a phone:

        service-cup.html    Conditional Use Permits
        locations.html      Where we broker
        resources.html      Knowledge base
        guides.html         Guides
        faq.html            Licensing FAQs

    A silent zero-match would have shipped that gap unnoticed. The whole reason the
    generators assert non-zero and exit 2 is this class of miss.

WHY IT MATTERS HERE SPECIFICALLY
    The owner's instruction was that each Licensing option be a page of its own. An
    option that no phone user can reach is not "a page of its own" in any useful sense.

IDEMPOTENT -- guarded on the first inserted href; a second run is a no-op.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# inserted after this existing drawer row (the last one currently present)
ANCHOR = ('          <a href="process.html#phases"><span class="mm-acc__ico">→</span>'
          'Transfer timeline &amp; escrow</a>\n')

NEW_ROWS = (
    '          <a href="service-cup.html"><span class="mm-acc__ico">→</span>'
    'Conditional Use Permits</a>\n'
    '          <a href="locations.html"><span class="mm-acc__ico">→</span>'
    'Where we broker</a>\n'
    '          <a href="resources.html"><span class="mm-acc__ico">→</span>'
    'Knowledge base</a>\n'
    '          <a href="guides.html"><span class="mm-acc__ico">→</span>'
    'Guides</a>\n'
    '          <a href="faq.html"><span class="mm-acc__ico">→</span>'
    'Licensing FAQs</a>\n'
)

MARKER = '<a href="guides.html"><span class="mm-acc__ico">'


def main():
    files = sorted(glob.glob(os.path.join(HERE, '*.html')))
    done = skipped = missing = 0
    for f in files:
        src = io.open(f, encoding='utf-8').read()
        if 'id="mm-acc-licensing"' not in src:
            missing += 1
            continue
        if MARKER in src:
            skipped += 1
            continue
        if ANCHOR not in src:
            print('  WARN %s: drawer anchor row not in expected form — skipped'
                  % os.path.basename(f), file=sys.stderr)
            continue
        io.open(f, 'w', encoding='utf-8').write(src.replace(ANCHOR, ANCHOR + NEW_ROWS, 1))
        done += 1
    print('drawer rows added on %d · already had them %d · no licensing drawer %d'
          % (done, skipped, missing))
    if done == 0 and skipped == 0:
        print('NOTHING CHANGED — re-read before trusting this.', file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
