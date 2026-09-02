#!/usr/bin/env python3
"""
_build-service-cta-suite.py -- [CG] put the "Getting started" CTA band, the office map
and the consultation form on all eight service pages.

OWNER INSTRUCTION (2026-09-02): include these on every service page. They existed on
index.html ONLY.

WHAT TRAVELS
    It is one section — <section class="section cta-suite" id="contact"> — carrying the
    heading and phone number, the two CTAs, the click-to-load office map, and the
    four-field consultation form. Lifted verbatim from index.html; nothing is retyped,
    so the eight copies cannot drift from the original wording.

⚠ THE SCRIPT HAD TO TRAVEL WITH IT, AND IT COULD NOT SIMPLY BE COPIED
    The map's click-to-load handler was an INLINE <script> on index.html. Copying only
    the markup would have shipped a dead "Load the map" button on eight pages. So the
    handler moved into site.js as [CG] — it is id-guarded and returns immediately where
    the map is absent — and the inline copy was REMOVED from index.html in the same
    change. Leaving both would have bound the listener twice and inserted TWO iframes
    on a single click.

PLACEMENT
    Appended after the existing #next section, which is where the homepage puts it and
    which keeps each page's own "other seven services" cross-links above it. #next is
    NOT replaced: it carries navigation the CTA suite does not.

ID SAFETY
    Checked before writing: none of contact / cta-map-ph / cta-map-load / contact-form /
    c-name / c-email / c-phone / c-msg appears on any service page. Each page is a
    separate document, so the ids repeating ACROSS pages is fine; repeating WITHIN one
    would not be.

IDEMPOTENT -- guarded on the cta-suite class. Fails closed if the donor section cannot
be extracted whole, or if a target already contains any of the ids.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONOR = os.path.join(HERE, 'index.html')
TARGETS = ['service-buy.html', 'service-sell.html', 'service-transfer.html',
           'service-valuation.html', 'service-cup.html', 'service-compliance.html',
           'service-escrow.html', 'service-new-business.html']
MARKER = 'class="section cta-suite"'
IDS = ['contact', 'cta-map-ph', 'cta-map-load', 'contact-form',
       'c-name', 'c-email', 'c-phone', 'c-msg']


def extract_section(src, needle):
    """Pull one <section> out whole by counting depth, not by rfind."""
    i = src.find(needle)
    if i < 0:
        return None
    start = src.rfind('<section', 0, i)
    if start < 0:
        return None
    depth = 0
    for m in re.finditer(r'<section\b|</section>', src[start:]):
        depth += 1 if m.group(0).startswith('<section') else -1
        if depth == 0:
            return src[start:start + m.end()]
    return None


def main():
    src = io.open(DONOR, encoding='utf-8').read()
    block = extract_section(src, MARKER)
    if not block:
        print('FAIL: could not extract the cta-suite section from index.html', file=sys.stderr)
        sys.exit(1)
    for need in ('cta-map-ph', 'contact-form', 'Talk to a senior broker'):
        if need not in block:
            print('FAIL: extracted section is missing %r — refusing to copy' % need, file=sys.stderr)
            sys.exit(1)
    if block.count('<section') != block.count('</section>'):
        print('FAIL: extracted section is unbalanced', file=sys.stderr); sys.exit(1)

    done = skipped = 0
    for name in TARGETS:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            print('FAIL: %s missing' % name, file=sys.stderr); sys.exit(1)
        t = io.open(p, encoding='utf-8').read()
        if MARKER in t:
            skipped += 1
            continue
        clashes = [i for i in IDS if 'id="%s"' % i in t]
        if clashes:
            print('FAIL: %s already uses id(s) %s — would duplicate within one document'
                  % (name, clashes), file=sys.stderr)
            sys.exit(1)

        # append after the #next section; fall back to just before </main>
        nxt = extract_section(t, 'id="next"')
        if nxt and nxt in t:
            out = t.replace(nxt, nxt + '\n\n' + block, 1)
        else:
            k = t.rfind('</main>')
            if k < 0:
                print('FAIL: %s has no </main>' % name, file=sys.stderr); sys.exit(1)
            out = t[:k] + '\n' + block + '\n' + t[k:]

        if out.count(MARKER) != 1:
            print('FAIL: %s would end up with %d cta-suites' % (name, out.count(MARKER)),
                  file=sys.stderr)
            sys.exit(1)
        io.open(p, 'w', encoding='utf-8').write(out)
        done += 1

    print('cta-suite added to %d page(s) · already had it %d' % (done, skipped))


if __name__ == '__main__':
    main()
