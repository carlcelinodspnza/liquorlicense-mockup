#!/usr/bin/env python3
"""
_build-licensing-menu-pages.py -- [CG] point the Licensing menu's rows at individual
pages instead of anchors, and correct a factual error in that menu.

OWNER INSTRUCTION (2026-09-02): the Licensing menu options should each be a page of
its own. Five of the eight already were. The three that were not, and what was done:

  Conditional Use Permits   services.html#cup   -> service-cup.html
        The page already existed; the menu simply was not using it.

  Guides                    index.html#guides   -> guides.html
        Was linking into the HOMEPAGE. New page built by _build-guides-index.py;
        vocabulary overlap against resources.html measured at 13.2%, well clear of
        the 90% threshold this build treats as the doorway-page line.

  Transfer timeline & escrow  process.html#phases  -> UNCHANGED, ON PURPOSE
        That section is 582 words and is process.html's core. A standalone page would
        be a ~100% lift of it. Building it would manufacture a duplicate to satisfy a
        menu row, which is the pattern this build has refused before. The row keeps
        its anchor; the finding was reported to the owner rather than hidden.

FACTUAL CORRECTION IN THE SAME PASS
    The Guides row claimed "Five explainers". There are FOUR guide pages, and
    resources.html says "Four explainers" four times over. The menu was wrong on every
    page carrying it. Corrected to four.

IDEMPOTENT -- each replacement's new text does not contain its old text. Every pattern
asserts a non-zero match across the tree and the run FAILS if one matches nothing.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

REPLACEMENTS = [
    # desktop mega-menu rows
    ('<a role="menuitem" href="services.html#cup"><span class="t">Conditional Use Permits</span>',
     '<a role="menuitem" href="service-cup.html"><span class="t">Conditional Use Permits</span>',
     'CUP row -> its own page'),
    ('<a role="menuitem" href="index.html#guides"><span class="t">Guides</span>',
     '<a role="menuitem" href="guides.html"><span class="t">Guides</span>',
     'Guides row -> off the homepage'),
    # the count was simply wrong
    ('<span class="d">Five explainers on licence types, transfers and permits</span>',
     '<span class="d">Four explainers on licence types, transfers and permits</span>',
     'FACT: there are four guide pages, not five'),
    # mobile drawer parity
    ('<a href="services.html#cup"><span class="mm-acc__ico">→</span>Conditional Use Permits</a>',
     '<a href="service-cup.html"><span class="mm-acc__ico">→</span>Conditional Use Permits</a>',
     'drawer CUP parity'),
    ('<a href="index.html#guides"><span class="mm-acc__ico">→</span>Guides</a>',
     '<a href="guides.html"><span class="mm-acc__ico">→</span>Guides</a>',
     'drawer Guides parity'),
]


def main():
    files = sorted(glob.glob(os.path.join(HERE, '*.html')))
    hits = {o: 0 for o, _, _ in REPLACEMENTS}
    touched = 0
    for f in files:
        src = io.open(f, encoding='utf-8').read()
        out = src
        for old, new, _ in REPLACEMENTS:
            if old in out:
                hits[old] += out.count(old)
                out = out.replace(old, new)
        if out != src:
            io.open(f, 'w', encoding='utf-8').write(out)
            touched += 1

    warns = 0
    for old, _, why in REPLACEMENTS:
        if hits[old] == 0:
            print('  WARN matched ZERO: %-52s (%s)' % (old[:52], why), file=sys.stderr)
            warns += 1
    print('files %d/%d · replacements %d · zero-match warnings %d'
          % (touched, len(files), sum(hits.values()), warns))
    if warns:
        sys.exit(2)


if __name__ == '__main__':
    main()
