#!/usr/bin/env python3
"""
_build-general-tone-services.py -- [CD] strip California-specific vocabulary from the
SERVICES surfaces so they read jurisdiction-neutral across all six states.

WHY
    Owner instruction (2026-09-02): "ensure that contents of these services are not
    focused on services for california ... if you find California-Focused content, turn
    them into general tone."

    The Services mega-menu is site-wide CHROME -- it is stamped on 105 pages, including
    every Arizona, Florida, New Jersey, Ohio and Pennsylvania page. It named California's
    agency (ABC), California's licensee-education programme (LEAD), California's licence
    classes (Type 21/47/48) and "all 58 California counties". A fact that is correct on a
    California page becomes a false universal once it sits in the nav. Arizona licences
    are Series NN under the DLLC; Florida uses 4COP/3PS under the ABT.

WHAT "GENERAL TONE" MEANS HERE -- AND WHAT IT DELIBERATELY DOES NOT DO
    Every rewrite REMOVES a jurisdiction qualifier. None ASSERTS a new one. Dropping
    "California's limited secondary market" to "a limited secondary market" stops claiming
    California; it does not claim Ohio. That distinction is the whole anti-invention rule:
    we may stop naming a state, we may not invent a capability. No new geography, no new
    programme name, no new agency is introduced anywhere in this file.

SCOPE -- verified before writing
    The body strings below occur ONLY in services.html, the eight service-*.html pages and
    index.html. They appear on NO California market page and NO licence-type page, which
    stay California-scoped ON PURPOSE. The chrome strings occur on all 105 pages carrying
    the header, which is correct: chrome is universal by definition.

TWO BYTE FORMS -- the trap this file exists to survive
    "California's major cities" is stored TWICE with DIFFERENT BYTES: a straight apostrophe
    in the visible HTML and a curly U+2019 inside the JSON-LD Service descriptions. A
    matcher written for one silently misses the other, and the machine-readable half is the
    half nobody looks at. Both forms are listed explicitly below.

IDEMPOTENT -- each replacement's "new" text does not contain its "old" text, so re-running
is a no-op. Every replacement asserts a NON-ZERO match across the tree and the run FAILS
if any pattern matches nothing, because a silent zero looks exactly like success.
"""
import io, os, glob, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CURLY = '’'

# (old, new, why)
REPLACEMENTS = [
    # ---- site-wide chrome: the Services mega-menu + mobile drawer ----
    ('<span class="s">Off-market, LOI to ABC issuance</span>',
     '<span class="s">Off-market, LOI to licence issuance</span>',
     'menu 01 - ABC is the California agency'),
    ('<span class="t">ABC compliance</span><span class="s">Audits and LEAD training</span>',
     '<span class="t">Licensing compliance</span><span class="s">Audits and staff training</span>',
     'menu 06 - ABC + LEAD are both California-only'),
    ('<span class="mm-acc__ico">06</span>ABC compliance</a>',
     '<span class="mm-acc__ico">06</span>Licensing compliance</a>',
     'mobile drawer 06 - parity with the desktop menu'),
    ('<span class="mm-mega__note">Serving all <b>58 California counties</b></span>',
     '<span class="mm-mega__note">Serving <b>six states</b>, market by market</span>',
     'menu footer - matches the precedent already set in the Licensing menu'),
    ('<span class="sub">Type 21, 47 and 48 assets that never list publicly, priced and status-checked.</span>',
     '<span class="sub">Off-market licences that never list publicly, priced and status-checked.</span>',
     'menu feature - Type NN is the California class system'),

    # ---- services.html body + the eight generated service pages ----
    ('from search to ABC issuance', 'from search to licence issuance', 'services lede'),
    ("California's limited secondary market", 'a limited secondary market', 'service 01 body'),
    ('final issuance by the ABC', 'final issuance by the licensing authority', 'service 01 body'),
    ('final ABC issuance', 'final licence issuance', 'service 01 bullet'),
    ('Type 47, 48 and 21 licences inside', 'off-market licences inside', 'service 01 body'),
    ('Type 47, 48 and 21 assets vetted before an offer',
     'Off-market assets vetted before an offer', 'service 01 bullet'),
    ("who holds a California licence", 'who holds a licence', 'services 01-04 group lede'),
    ("across California's major cities", 'across the major markets we cover', 'service 05 body (straight quote)'),
    ('across California' + CURLY + 's major cities', 'across the major markets we cover',
     'service 05 JSON-LD description (CURLY quote - the machine-readable copy)'),
    ("Covered across California's major cities", 'Covered across the major markets we cover',
     'service 05 bullet'),
    ('put staff through LEAD-program training', 'put staff through responsible-service training',
     'service 06 body - LEAD is a California ABC programme'),
    ('LEAD-program staff training', 'Responsible-service staff training', 'service 06 bullet'),
    ('costly ABC violation', 'costly licensing violation', 'service 06 bullet'),
    ('ABC compliance consulting', 'Licensing compliance consulting', 'service 06 heading + refs'),

    # ---- HEAD METADATA -- title / meta / og / twitter / JSON-LD ----
    # Missed on the first pass because the audit only read <main>. The <title> is the most
    # visible string on the page and it is not in the body.
    ('Liquor Licence Brokerage Services | Buy, Sell, Transfer &amp; Value &mdash; California',
     'Liquor Licence Brokerage Services | Buy, Sell, Transfer &amp; Value', 'services.html title'),
    (' in California | ABC Licence Brokers', ' | Licence Brokers', 'the eight service page titles'),
    ('Eight California liquor licence services:', 'Eight liquor licence services:', 'services meta'),
    ('Conditional Use Permits, ABC compliance, escrow',
     'Conditional Use Permits, licensing compliance, escrow', 'services meta'),

    # A THIRD byte form of the apostrophe. The visible HTML uses a straight quote, the
    # JSON-LD a curly U+2019, and the meta description the HEX ENTITY below. Three forms
    # of one phrase; a matcher for any one of them silently misses the other two.
    ('California&#x27;s limited secondary market', 'a limited secondary market',
     'meta description - hex-entity apostrophe'),

    # Self-inflicted: the 'Type 47, 48 and 21 licences inside' rule above fires inside the
    # phrase 'We source off-market Type 47, 48 and 21 licences inside', producing
    # 'off-market off-market'. Ordering matters, so this repair runs last.
    ('off-market off-market licences', 'off-market licences', 'repair the doubled word'),

    # The per-service geography band, on index + the industry and service pages only.
    # It appears on NO jurisdiction-scoped page, so generalising it invents nothing.
    ('We work every county in the state.', 'We work market by market.', 'geography band'),

    # ---- FOOTER IDENTITY LINE -- owner decision 2026-09-02 ----
    # This is the FIRM'S OWN self-description, not service copy, so it was put to the
    # owner rather than changed silently. They chose to generalise it. Same rule as
    # everywhere else in this file: the qualifier is removed, nothing new is asserted.
    ('A California liquor licence brokerage helping businesses buy, sell, transfer and '
     'value liquor licences throughout the state.',
     'A liquor licence brokerage helping businesses buy, sell, transfer and value liquor '
     'licences across the markets we serve.', 'site-wide footer descriptor'),
    ('Covered across the major markets we cover', 'Covered across every market we serve',
     'repair redundant phrasing from the first pass'),
    ('We do that work across the major markets we cover',
     'We do that work across the major markets we serve', 'repair redundant phrasing'),
    ('neighbourhood council meetings across the major markets we cover',
     'neighbourhood council meetings across the major markets we serve', 'JSON-LD, same repair'),
]


H2_CA = re.compile(r'(<h2[^>]*>)([^<]*?) across California(</h2>)')


def main():
    files = sorted(glob.glob(os.path.join(HERE, '*.html')))
    hits = {old: 0 for old, _, _ in REPLACEMENTS}
    touched = 0
    for f in files:
        src = io.open(f, encoding='utf-8').read()
        out = src
        out = H2_CA.sub(lambda m: m.group(1) + m.group(2) + ' across our markets'
                          + m.group(3), out)
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
            print('  WARN matched ZERO: %-56s (%s)' % (old[:56], why), file=sys.stderr)
            warns += 1
    print('files rewritten %d / %d  ·  replacements applied %d  ·  zero-match warnings %d'
          % (touched, len(files), sum(hits.values()), warns))
    if warns and touched == 0:
        print('NOTHING CHANGED and %d patterns matched nothing — already applied, or the '
              'markup drifted. Re-read before trusting this.' % warns, file=sys.stderr)
    if warns:
        sys.exit(2)


if __name__ == '__main__':
    main()
