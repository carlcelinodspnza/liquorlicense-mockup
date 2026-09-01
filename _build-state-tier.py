#!/usr/bin/env python3
"""
_build-state-tier.py -- [BX] convert locations.html from a California-only page to a
six-state page, then hand off to _build-state-panels.py to fill the generated panels.

WHAT IT CHANGES
    title / description / h1 / lede / section heading, the "how to read this" conventions,
    the qualifier's market select, the JSON-LD (areaServed + a States ItemList), and it
    wraps the existing fourteen-tab matrix in a California state panel so an outer state
    rail can sit above it. The matrix markup itself is never touched.

IDEMPOTENT
    Every edit is guarded on its own before/after text. Re-running is a no-op and prints
    what it skipped, so this can be re-applied after a revert without duplicating anything.
"""
import io, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 'locations.html')

EDITS = [
    ('title',
     '<title>Where We Broker Liquor Licences in California | Markets &amp; Coverage</title>',
     '<title>Where We Broker Liquor Licences | Coverage by State</title>'),

    ('meta description',
     '<meta name="description" content="Statewide plus thirteen California markets, each showing which of the five ABC classifications hold live stock there today, and a five-step qualifier.">',
     '<meta name="description" content="Six states \u2014 Arizona, California, Florida, New Jersey, Ohio and Pennsylvania. The counties and cities we broker in, the classifications each one issues, and what is on the board today.">'),

    ('h1 + lede',
     '      <h1>Where we broker liquor licences in California</h1>\n'
     '      <p class="lede">Thirteen named markets and one statewide desk. Open a market to see which of the five ABC classifications we are holding stock in there today, and which ones we go and find.</p>',
     '      <h1>Where we broker liquor licences</h1>\n'
     '      <p class="lede">Arizona, California, Florida, New Jersey, Ohio and Pennsylvania &mdash; six states, '
     'each with its own regulator and its own classifications. Open one to see the counties and cities '
     'we broker in there, and what is on the board today.</p>'),

    ('section heading',
     '    <h2>Fourteen tabs: one statewide, thirteen markets</h2>\n'
     '    <p class="lede">Every tab asks the same question locally. Which of the five classifications can you actually get here, and can you get one this month?</p>',
     '    <h2>Six states, market by market</h2>\n'
     '    <p class="lede">Pick a state, then a market. Each one asks the same question locally &mdash; which '
     'classifications can you actually get here, and can you get one this month?</p>'),

    ('conventions count',
     '<span class="loc-flag__lbl">How to read this</span> Two conventions run through every tab.',
     '<span class="loc-flag__lbl">How to read this</span> Three conventions run through every tab.'),

    ('third convention',
     'because it holds a real listing and leaving it out would have been the dishonest tidy-up.</p>',
     'because it holds a real listing and leaving it out would have been the dishonest tidy-up. '
     'And the board\'s stock today all sits in one state, so every other state shows the markets '
     'published there and says plainly that it holds no live listings.</p>'),

    ('qualifier state options',
     '              <option value="other">Another California county</option>\n            </select>',
     '              <option value="other">Another California county</option>\n'
     '              <option value="st-arizona">Arizona</option>\n'
     '              <option value="st-florida">Florida</option>\n'
     '              <option value="st-new-jersey">New Jersey</option>\n'
     '              <option value="st-ohio">Ohio</option>\n'
     '              <option value="st-pennsylvania">Pennsylvania</option>\n'
     '            </select>'),

    ('schema areaServed',
     '      "areaServed": {\n        "@type": "State",\n        "name": "California"\n      },',
     '      "areaServed": [\n'
     '        { "@type": "State", "name": "California" },\n'
     '        { "@type": "State", "name": "Arizona" },\n'
     '        { "@type": "State", "name": "Florida" },\n'
     '        { "@type": "State", "name": "New Jersey" },\n'
     '        { "@type": "State", "name": "Ohio" },\n'
     '        { "@type": "State", "name": "Pennsylvania" }\n'
     '      ],'),

    ('schema States ItemList',
     '    {\n      "@type": "ItemList",\n      "name": "California markets served",',
     '    {\n      "@type": "ItemList",\n      "name": "States served",\n      "numberOfItems": 6,\n'
     '      "itemListElement": [\n'
     '        { "@type": "ListItem", "position": 1, "name": "California", "item": "locations.html#state-california" },\n'
     '        { "@type": "ListItem", "position": 2, "name": "Arizona", "item": "locations.html#state-arizona" },\n'
     '        { "@type": "ListItem", "position": 3, "name": "Florida", "item": "locations.html#state-florida" },\n'
     '        { "@type": "ListItem", "position": 4, "name": "New Jersey", "item": "locations.html#state-new-jersey" },\n'
     '        { "@type": "ListItem", "position": 5, "name": "Ohio", "item": "locations.html#state-ohio" },\n'
     '        { "@type": "ListItem", "position": 6, "name": "Pennsylvania", "item": "locations.html#state-pennsylvania" }\n'
     '      ]\n    },\n'
     '    {\n      "@type": "ItemList",\n      "name": "California markets served",'),

    ('schema note',
     '<!-- Markets are emitted as plain named ListItems, NOT as Place nodes with geo. No source gives',
     '<!-- [BX] areaServed now carries all SIX states the client publishes, and a second ItemList\n'
     '     names them. The 13 market pages and the other 49 pages still declare California only, which\n'
     '     is correct for their own content but leaves the ORG-level areaServed inconsistent across the\n'
     '     site. Flagged, not silently propagated: a 51-page schema change was not in scope here.\n'
     '     Markets are emitted as plain named ListItems, NOT as Place nodes with geo. No source gives'),
]

OPEN_TABS = '    <div class="loc-tabs wow-reveal" data-loc-tabs>\n'
WRAP_PRE = (
    '    <!-- [BX] STATE TIER. Adds one level ABOVE the fourteen market tabs, because the client\n'
    '         publishes six states, not one. California keeps the hand-authored matrix below\n'
    '         verbatim; the other five panels are GENERATED from the client\'s own sitemaps by\n'
    '         _build-state-panels.py and must not be hand-edited between the sentinels.\n'
    '         NO new pages are created for any of it -- owner decision, and the measured\n'
    '         duplication finding that produced the six noindex market pages applies with more\n'
    '         force to 81 further counties. -->\n'
    '    <div class="loc-states" data-loc-states>\n'
    '      <!-- LLA:STATE-RAIL:BEGIN -->\n'
    '      <!-- LLA:STATE-RAIL:END -->\n\n'
    '      <div class="loc-panel loc-panel--state" id="state-california" data-loc-statepanel="california" role="tabpanel" aria-labelledby="locstate-california">\n')
OLD_CLOSE = '      </div>\n\n    </div>\n  </div>\n</section>\n\n<!-- BAND 3 · THE QUALIFIER.'
NEW_CLOSE = ('      </div>\n\n    </div>\n'
             '      </div>\n\n'
             '      <!-- LLA:STATE-PANELS:BEGIN -->\n'
             '      <!-- LLA:STATE-PANELS:END -->\n'
             '    </div>\n'
             '  </div>\n</section>\n\n<!-- BAND 3 · THE QUALIFIER.')


def main():
    s = io.open(P, encoding='utf-8').read()
    applied = skipped = 0
    for name, old, new in EDITS:
        if new in s:
            skipped += 1
            continue
        if old not in s:
            raise SystemExit('FAIL "%s": neither the before nor the after text is present' % name)
        s = s.replace(old, new, 1)
        applied += 1

    if 'data-loc-states' not in s:
        assert s.count(OPEN_TABS) == 1, 'expected exactly one .loc-tabs open tag'
        s = s.replace(OPEN_TABS, WRAP_PRE + OPEN_TABS, 1)
        assert OLD_CLOSE in s, 'tab-block close pattern not found'
        s = s.replace(OLD_CLOSE, NEW_CLOSE, 1)
        applied += 1
    else:
        skipped += 1

    io.open(P, 'w', encoding='utf-8').write(s)
    print('locations.html: %d edit(s) applied, %d already present' % (applied, skipped))
    subprocess.check_call([sys.executable, os.path.join(HERE, '_build-state-panels.py')])


if __name__ == '__main__':
    main()
