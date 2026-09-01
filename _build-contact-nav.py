#!/usr/bin/env python3
"""
_build-contact-nav.py -- [CA] add a Contact item to the header nav and the mobile drawer.

WHAT WAS ACTUALLY MISSING
    The header already HAS a contact button: `.mm-cta-desktop` -> "Talk to a broker" ->
    contact.html. What it had no route to was a plain Contact NAV ITEM, so contact.html
    was reachable from the header only through the CTA. The client's own nav carries both
    ("Contact Us" as an item, "TALK TO US" as the button), so this closes the same gap
    rather than adding a second button beside the one that already exists.

PLACEMENT
    After Inventory and before the CTA, which is the client's own order.
    The drawer gets the matching flat link after FAQ, where its siblings live.

IDEMPOTENT -- guarded on its own marker; re-running is a no-op.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

NAV_ANCHOR = '      <li class="mm-cta-desktop">'
NAV_NEW = '      <li><a class="mm-navlink" href="contact.html">Contact</a></li>\n\n'
DRAWER_ANCHOR = '    <a class="mm-drawer__link" href="faq.html">FAQ</a>\n'
DRAWER_NEW = '    <a class="mm-drawer__link" href="contact.html">Contact</a>\n'
MARKER = '<a class="mm-navlink" href="contact.html">Contact</a>'


def main():
    done = skipped = nonav = 0
    for f in sorted(glob.glob(os.path.join(HERE, '*.html'))):
        name = os.path.basename(f)
        src = io.open(f, encoding='utf-8').read()
        if '<ul class="site-nav"' not in src:
            nonav += 1
            continue
        if MARKER in src:
            skipped += 1
            continue
        if NAV_ANCHOR not in src:
            print('  FAIL %s: CTA anchor not found' % name, file=sys.stderr)
            sys.exit(1)
        src = src.replace(NAV_ANCHOR, NAV_NEW + NAV_ANCHOR, 1)
        if DRAWER_ANCHOR in src:
            src = src.replace(DRAWER_ANCHOR, DRAWER_ANCHOR + DRAWER_NEW, 1)
        else:
            print('  WARN %s: drawer FAQ link not found, desktop only' % name, file=sys.stderr)
        io.open(f, 'w', encoding='utf-8').write(src)
        done += 1
    print('stamped %d  ·  already had it %d  ·  no site-nav %d' % (done, skipped, nonav))


if __name__ == '__main__':
    main()
