#!/usr/bin/env python3
"""
_build-faq-2col.py -- [CK] lay the FAQ band out in two columns on the 50 market x type
pages. Owner picked option A (2026-09-02).

MEASURED FIRST: the live band is 762px tall and the accordion renders only 820px wide
inside a 1200px container — 380px of the row sits empty, beside six collapsed bars with
nothing open.

⚠ WHY THIS STAMPS A CLASS INSTEAD OF STYLING .faq__list
    There are 56 .faq__list instances across 55 files. Only 50 are this band. The other
    six are faq.html (7 items across TWO lists), index.html (4 items) and three market
    pages. Styling the shared class would have re-laid out all 56 to change 50 —
    including the site's own FAQ page. Counted before writing any CSS.

WHY THE MARKUP IS WRAPPED RATHER THAN LEFT ALONE
    Two real column divs of three items each, so opening an answer grows only its own
    column. A CSS `columns: 2` on the existing markup would have reflowed items ACROSS
    the columns on every open and close, which is disorienting on a click.

IDEMPOTENT -- guarded on faq--2col. Fails closed unless a band holds exactly six items
and the page keeps every one of them.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ITEM = re.compile(r'<details class="faq-item">.*?</details>', re.S)


def main():
    done = skipped = 0
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        src = io.open(path, encoding='utf-8').read()
        if 'faq--2col' in src:
            skipped += 1
            continue

        m = re.search(r'<div class="faq__list">(.*?)</div>\s*<p class="tp-note">', src, re.S)
        if not m:
            print('FAIL %s: faq__list not in its expected shape' % name, file=sys.stderr)
            sys.exit(1)
        inner = m.group(1)
        items = ITEM.findall(inner)
        if len(items) != 6:
            print('FAIL %s: expected 6 faq items, found %d' % (name, len(items)), file=sys.stderr)
            sys.exit(1)
        # nothing but the six items may live in there
        residue = ITEM.sub('', inner).strip()
        if residue:
            print('FAIL %s: faq__list holds more than the six items (%r)'
                  % (name, residue[:60]), file=sys.stderr)
            sys.exit(1)

        col = lambda group: ('      <div class="faq__col">\n'
                             + ''.join('        %s\n' % i for i in group)
                             + '      </div>\n')
        new = ('<div class="faq__list faq--2col">\n' + col(items[:3]) + col(items[3:]) + '    </div>\n    ')
        out = src[:m.start()] + new + src[m.start(2) if m.lastindex and False else src.index('<p class="tp-note">', m.start())] \
              if False else src.replace(m.group(0), new + '<p class="tp-note">', 1)

        if out.count('class="faq-item"') != src.count('class="faq-item"'):
            print('FAIL %s: item count changed' % name, file=sys.stderr); sys.exit(1)
        if out.count('faq__col') != 2:
            print('FAIL %s: expected exactly 2 columns' % name, file=sys.stderr); sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(out)
        done += 1

    print('converted %d · already 2-col %d' % (done, skipped))


if __name__ == '__main__':
    main()
