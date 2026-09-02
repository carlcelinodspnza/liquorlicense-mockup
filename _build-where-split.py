#!/usr/bin/env python3
"""
_build-where-split.py -- [CH] turn the "Where … across our markets" band into two
columns: the copy on the left, the markets as a real list on the right.

OWNER INSTRUCTION (2026-09-02): convert this section to a two-column layout.
Before: a heading and a 62ch lede filling the left ~55% with the right half empty,
and thirteen market links flowing beneath as one run-on line separated by middots.

TWO COUNTS TAKEN BEFORE ANY STYLING — both changed the design
    1. `.cross-link-rail__rail` appears 83 times site-wide; only 25 sit inside a
       #where band. Restyling that class would have moved 58 rails elsewhere on the
       site to change 25. So the markets get their OWN class instead.
    2. `#where` is not uniform. 25 pages carry a market rail;
       california-liquor-license-services.html carries a CTA row and NO rail. Scoping
       the layout to #where would have left that page with an empty second column.
       So this stamps `.where--split` ONLY on bands it actually converts, and the CSS
       keys off that — the page without a rail is untouched by construction.

MARKUP CHANGE
    <p class="cross-link-rail__rail">a &middot; a &middot; …</p>
      becomes
    <ul class="mkt-list"><li><a>…</a></li>…</ul>

    Which is what thirteen links always were. The hrefs and link text are lifted
    verbatim — this parses the existing rail and never retypes a market name.

SCOPE
    26 pages carry a #where band: 8 service, 8 industry, 5 licence-type, 4 guide, and
    the California services page. 25 get converted; the CTA-row one is skipped and
    reported, not silently touched.

IDEMPOTENT -- guarded on .mkt-list. Fails closed if a rail cannot be parsed into at
least two links, or if the link count would change.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MARKER = 'mkt-list'
RAIL = re.compile(r'(\s*)<p class="cross-link-rail__rail">(.*?)</p>', re.S)
LINK = re.compile(r'<a href="([^"]+)">(.*?)</a>', re.S)


def main():
    converted = skipped_done = no_rail = 0
    for f in sorted(glob.glob(os.path.join(HERE, '*.html'))):
        name = os.path.basename(f)
        src = io.open(f, encoding='utf-8').read()

        sec = re.search(r'<section([^>]*)id="where"([^>]*)>(.*?)</section>', src, re.S)
        if not sec:
            continue
        if MARKER in sec.group(0):
            skipped_done += 1
            continue

        body = sec.group(3)
        rail = RAIL.search(body)
        if not rail:
            print('  SKIP %s: #where has no market rail (it carries a CTA row)' % name)
            no_rail += 1
            continue

        links = LINK.findall(rail.group(2))
        if len(links) < 2:
            print('FAIL %s: parsed %d links from the rail — refusing to write'
                  % (name, len(links)), file=sys.stderr)
            sys.exit(1)

        items = '\n'.join('      <li><a href="%s">%s</a></li>' % (h, t.strip())
                          for h, t in links)
        new_list = '%s<ul class="mkt-list">\n%s\n    </ul>' % (rail.group(1), items)
        new_body = body.replace(rail.group(0), new_list, 1)

        # stamp the class on the section itself so the CSS only touches converted bands
        open_tag = '<section%sid="where"%s>' % (sec.group(1), sec.group(2))
        if 'class="' not in open_tag:
            print('FAIL %s: #where section has no class attribute to extend' % name,
                  file=sys.stderr)
            sys.exit(1)
        new_open = open_tag.replace('class="', 'class="where--split ', 1)
        new_sec = new_open + new_body + '</section>'
        out = src.replace(sec.group(0), new_sec, 1)

        # the link count must be identical before and after
        if len(LINK.findall(new_list)) != len(links):
            print('FAIL %s: link count changed' % name, file=sys.stderr); sys.exit(1)
        if out.count('where--split') != 1:
            print('FAIL %s: expected exactly one .where--split' % name, file=sys.stderr)
            sys.exit(1)

        io.open(f, 'w', encoding='utf-8').write(out)
        converted += 1

    print('converted %d · already done %d · skipped (no rail) %d'
          % (converted, skipped_done, no_rail))


if __name__ == '__main__':
    main()
