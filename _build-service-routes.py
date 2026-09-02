#!/usr/bin/env python3
"""
_build-service-routes.py -- [CG] route every service entry point at the service's OWN
PAGE instead of an anchor on services.html.

OWNER INSTRUCTION (2026-09-02), twice, about the same underlying thing:
    "these items 1-4 seems to be a landing page only. I want them to be separate page
     of their own"
    "these items still redirects to .../services.html#buy. can we have each of those
     item to have their own landing page instead?"

    So the complaint was never the on-page detail — it was the ROUTING. Every service
    already has a real page; nothing was linking to them.

VERIFIED BEFORE REPOINTING ANYTHING
    All eight pages exist, are substantive (272-301 words of <main>) and are genuinely
    distinct: worst pairwise vocabulary overlap across buy/sell/transfer/valuation is
    55.9%, far below the 90% line this build treats as the duplicate threshold. So these
    are real destinations, not stubs minted to satisfy a menu.

    All 18 "what this covers" bullets in the services.html accordion were also checked
    against their pages: 18 of 18 already appear there. Nothing on the landing page is
    unique to it, so sending people to the page loses no content.

THREE ENTRY POINTS, ALL REPOINTED
    1. Services mega-menu cards (desktop)     8 rows
    2. Services mobile drawer                 8 rows
    3. .svc-tiles on services.html            8 tiles
    Missing any one of them would leave a route that still dead-ends on an anchor —
    which is exactly the bug being fixed.

WHAT IS DELIBERATELY LEFT ALONE
    The #buy / #sell / ... ids stay on the services.html sections. Roughly 1,300 body
    cross-links across the site still point at them, and those anchors are the reason
    those links land anywhere at all. Removing the ids to "finish the job" would break
    far more than it tidied.

IDEMPOTENT -- each new href does not contain its old one. Every pattern asserts a
non-zero match and the run FAILS if one matches nothing.
"""
import io, os, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    ('buy',          '01'), ('sell',        '02'),
    ('transfer',     '03'), ('valuation',   '04'),
    ('cup',          '05'), ('compliance',  '06'),
    ('escrow',       '07'), ('new-business','08'),
]

REPLACEMENTS = []
for slug, num in SERVICES:
    page = 'service-%s.html' % slug
    # 1. desktop mega-menu card
    REPLACEMENTS.append((
        '<a class="mm-mega__card" role="menuitem" href="services.html#%s">' % slug,
        '<a class="mm-mega__card" role="menuitem" href="%s">' % page,
        'mega-menu card %s' % num))
    # 2. mobile drawer row
    REPLACEMENTS.append((
        '<a href="services.html#%s"><span class="mm-acc__ico">%s</span>' % (slug, num),
        '<a href="%s"><span class="mm-acc__ico">%s</span>' % (page, num),
        'drawer row %s' % num))
    # 3. the on-page tiles (relative in-page anchor)
    REPLACEMENTS.append((
        '<a class="svc-tile wow-lift" href="#%s">' % slug,
        '<a class="svc-tile wow-lift" href="%s">' % page,
        'services.html tile %s' % num))


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
            print('  WARN matched ZERO: %-44s (%s)' % (old[:44], why), file=sys.stderr)
            warns += 1
    print('files %d/%d · replacements %d · zero-match warnings %d'
          % (touched, len(files), sum(hits.values()), warns))
    if warns:
        sys.exit(2)


if __name__ == '__main__':
    main()
