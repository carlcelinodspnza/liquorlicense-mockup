#!/usr/bin/env python3
"""
_build-service-tiles.py -- [CD] rebuild the "service list" band on services.html as
eight dense tiles, four across (Option D, picked by the owner 2026-09-02).

WHAT CHANGES
    .cap-breakdown__grid  ->  .svc-tiles      (3 columns -> 4)
    <article class="card capability-card">  ->  <a class="svc-tile">
    The number moves out of its own stacked block and becomes a ghost numeral
    behind the title, so it still anchors the tile without taking vertical space.

WHY A NEW NAMESPACE INSTEAD OF RESTYLING .capability-card
    .capability-card is used 42 times site-wide and only EIGHT of them are this
    band; the other 26 are specimens on brand-card.html and design-system.html.
    Restyling the shared class would have moved all 42 to change 8. Counted before
    writing a line of CSS, not after.

WHY THE WHOLE TILE IS THE LINK
    The old card had a small "How buying works" anchor as the only hit target. An
    <a> may legally contain flow content, so the h3 and p stay real elements -- the
    document outline is unchanged and the tap target is now the whole tile. There
    is no nested interactive element, so this introduces no a11y violation.

CONTENT IS LIFTED, NEVER RETYPED
    Every string is parsed out of the existing markup, so this inherits whatever
    services.html currently says -- including the de-Californised copy from
    _build-general-tone-services.py. Nothing here is a transcription.

IDEMPOTENT -- guarded on .svc-tiles; a second run is a no-op. Fails closed if it
does not find exactly eight cards.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = os.path.join(HERE, 'services.html')
MARKER = 'svc-tiles'

CARD = re.compile(
    r'<article class="card capability-card wow-lift">\s*'
    r'<span class="capability-card__icon" aria-hidden="true">(\d+)</span>\s*'
    r'<h3>(.*?)</h3>\s*'
    r'<p>(.*?)</p>\s*'
    r'<a class="cross-link" href="(.*?)">(.*?)</a>\s*'
    r'</article>', re.S)


def main():
    src = io.open(TARGET, encoding='utf-8').read()

    if MARKER in src:
        print('already built (.svc-tiles present) — no-op')
        return

    i = src.find('id="services"')
    if i < 0:
        print('FAIL: #services not found', file=sys.stderr); sys.exit(1)
    j = src.find('<div class="cap-breakdown__grid wow-stagger">', i)
    if j < 0:
        print('FAIL: the grid wrapper is not in its expected form', file=sys.stderr); sys.exit(1)
    k = src.find('</section>', j)
    block = src[j:k]

    cards = CARD.findall(block)
    if len(cards) != 8:
        print('FAIL: expected 8 cards, parsed %d — refusing to write' % len(cards), file=sys.stderr)
        sys.exit(1)

    tiles = []
    for num, title, desc, href, link in cards:
        tiles.append(
            '        <a class="svc-tile wow-lift" href="%s">\n'
            '          <span class="svc-tile__ghost" aria-hidden="true">%s</span>\n'
            '          <h3 class="svc-tile__t">%s</h3>\n'
            '          <p class="svc-tile__d">%s</p>\n'
            '          <span class="svc-tile__go">%s</span>\n'
            '        </a>\n' % (href, num, title.strip(), desc.strip(), link.strip()))

    new_block = ('<div class="svc-tiles wow-stagger">\n' + ''.join(tiles) + '      ')

    # Find the grid div's MATCHING close by depth, not by rfind.
    # rfind('</div>') grabs the LAST </div> in the slice, which is the .container's,
    # not the grid's -- that silently ate one closing tag and left the section with an
    # unbalanced <div>. The browser auto-corrects it, so the page still LOOKED right;
    # only a tag-balance check caught it.
    depth = 0
    end = -1
    for m in re.finditer(r'<div\b|</div>', block):
        depth += 1 if m.group(0).startswith('<div') else -1
        if depth == 0:
            end = m.end()
            break
    if end < 0:
        print('FAIL: the grid div is never closed', file=sys.stderr); sys.exit(1)
    out = src[:j] + new_block + '</div>' + src[j + end:]

    if 'capability-card' in out[j:j + len(new_block) + 200]:
        print('FAIL: old cards survived the swap', file=sys.stderr); sys.exit(1)

    io.open(TARGET, 'w', encoding='utf-8').write(out)
    print('rebuilt %d tiles in services.html' % len(cards))


if __name__ == '__main__':
    main()
