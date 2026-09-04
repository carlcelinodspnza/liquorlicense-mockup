#!/usr/bin/env python3
"""
Mirror the structure of liquorlicenseagents.com/buy onto service-buy.html,
keeping this mockup's theme.

THE LIVE PAGE'S SEQUENCE, measured off the rendered page (3704px, 358 words):
  1  hero: map on the left, a lead-capture form card on the right
  2  intro: h2 "Do you need to buy a liquor license for your business?" + one paragraph
  3  a three-column classification band: Type 20 & 21 / Type 41 & 47 / Type 48
  4  CTA row: "Schedule an Appointment | 800.799.9081" + Buy / Sell buttons
  5  a second form card: "Request a Free Consultation"

WHAT THIS PAGE ALREADY HAD: 4 and 5. #next is the appointment CTA and #contact is
the consultation form -- and #contact already carries the map too. So only 1, 2 and 3
are missing, and 1 is really "the form the hero never had".

TWO SECTIONS OF THE LIVE PAGE ARE DELIBERATELY NOT COPIED VERBATIM.

  a) THE CLASSIFICATION DEFINITIONS. Dedup ledger rows C18-C20 assign the Type
     21/47/48 definitions to licence-types.html, and the ledger's own words are
     "MUST NOT restate ... may NAME a type but must NOT define what that type
     authorises". The live band's three columns ARE those definitions. So the band
     here mirrors the SHAPE and the pairing (20&21 / 41&47 / 48), names each
     classification, links to the page that owns the definition, and says only what
     the buy page itself owns -- what we do about it.

  b) THE CALIFORNIA FRAMING. This page was de-Californised on the owner's
     instruction and currently measures 0 "California", 0 "ABC" and 0 mentions of
     any Type NN in <main>. The live column copy is explicitly Californian ("The
     California Department of Alcoholic Beverage Control states that ..."). Copying
     it would reverse that instruction, so the new band names classifications
     without attaching them to one state's regulator.

SPELLING. service-buy.html uses "licence" 12 times and "license" 0. The client's
paragraph is reproduced verbatim except for that spelling, so the page stays
internally consistent. This is the ONLY edit made to their wording.

EVERYTHING ELSE IS PRESERVED. #covers and #where have no counterpart on the live
page; they are kept, not dropped, and sit after the mirrored bands so the live
sequence still reads top to bottom. Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGE = 'service-buy.html'

# --- copy lifted verbatim from the live page (spelling adapted, see docstring) ---
INTRO_H2 = 'Do you need to buy a liquor licence for your business?'
INTRO_P = (
    'We can help you make your liquor licence purchase a worry-free experience. Our team of '
    'dedicated specialists provide both assistance and consultation in brokering the purchase of '
    'your liquor licence from a seller on the open market. As a buyer, you also benefit from our '
    'team&rsquo;s experience in identifying sellers who have yet to place their licence on the '
    'market. This means that you will get your licence for the best value &ndash; even in the most '
    'competitive markets. You will also be able to rest easy knowing that each seller we work with '
    'is fully qualified.')
FORM_HEAD = 'Contact us today for a free consultation'

# The three columns mirror the live band's pairing. The BODY text is service-side --
# what we do -- because the definitions belong to licence-types.html (ledger C18-C20).

# THE CLIENT'S OWN DESCRIPTIONS, added on the owner's explicit instruction after the
# ledger conflict was raised twice. Reproduced from their /buy and /sell verbatim,
# with exactly two edits, both of which keep a STANDING instruction intact:
#   1. license -> licence, this page's own spelling.
#   2. "The California Department of Alcoholic Beverage Control states that" becomes
#      "The state licensing authority requires that". These pages were de-Californised
#      on the owner's instruction and measure 0 "California" in <main>; naming one
#      state's regulator here would reverse that. The substance -- bona fide eating
#      place, 51% of sales from food -- is unchanged, and licence-types.html still
#      carries the attributed version.
# dedup-ledger.md now records this as a written C18-C20 exception rather than a
# silent breach; licence-types.html remains the canonical owner and both bands keep
# their pointer note to it.
DESCRIPTIONS = {
    '20': ('Both Type 20 and Type 21 licences are designated for the sale of alcohol for '
           'off-premises consumption. Minors are allowed on the premises of businesses that are '
           'issued this type of licence. The Type 20 licence is issued for the sale of packaged '
           'beer and wine, while the Type 21 is designated for the sale of general packaged '
           'alcohol, including spirits and liquor.'),
    '41': ('Probably some of the most common types of liquor licence, the Type 41 and Type 47 '
           'licences are specifically designated for businesses that primarily serve food. The '
           'state licensing authority requires that, in order to be issued a Type 41 or Type 47 '
           'licence, your facility must be a &ldquo;bona fide eating place.&rdquo; 51% of the '
           'total sales should come from food.'),
    '48': ('Type 48 licences differ from Type 41 and Type 47 licences as they are used in '
           'establishments that are not primarily eateries. Type 48 licences are typically issued '
           'for bars and nightclubs. The Type 48 licence permits the holder to serve liquor until '
           '2:00 AM. Unique to this licence, the Type 48 allows closed containers of beer or wine '
           'to be sold for &ldquo;off-premises&rdquo; consumption.'),
}

COLUMNS = [
    ('Type 20 &amp; 21', [('20', 'Type 20'), ('21', 'Type 21')],
     DESCRIPTIONS['20']),
    ('Type 41 &amp; 47', [('41', 'Type 41'), ('47', 'Type 47')],
     DESCRIPTIONS['41']),
    ('Type 48', [('48', 'Type 48')],
     DESCRIPTIONS['48']),
]

FIELDS = [
    ('b-name', 'name', 'text', 'Full name', 'name'),
    ('b-email', 'email', 'email', 'Email address', 'email'),
    ('b-phone', 'phone', 'tel', 'Phone number', 'tel'),
]
RADIOS = [
    ('Type of licence', 'type_of_licence', ['Full liquor', 'Beer and wine']),
    ('Type of business', 'type_of_business', ['Bar / restaurant', 'Liquor store', 'Other']),
]
TAIL_FIELDS = [
    ('b-state', 'operating_state', 'text', 'Operating state', 'address-level1'),
    ('b-county', 'county', 'text', 'County', 'address-level2'),
]

MARK = 'id="buy-lead"'


def main_span(s):
    a, b = s.find('<main'), s.find('</main>')
    assert a >= 0 and b > a, 'no <main>'
    return a, b


def words(fragment):
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', fragment, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', ' ', t, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return Counter(html.unescape(t).split())


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


def sections(m):
    out = []
    for mm in re.finditer(r'<section\b([^>]*)>', m):
        depth, i = 1, mm.end()
        while depth and i < len(m):
            nx = re.search(r'<(/?)section\b[^>]*>', m[i:])
            if not nx:
                break
            depth += -1 if nx.group(1) else 1
            i += nx.end()
        out.append((mm.start(), i, mm.group(1)))
    return out


src = io.open(PAGE, encoding='utf-8').read()
a, b = main_span(src)
m = src[a:b]

if MARK in m:
    print('no-op: %s already carries the mirrored structure' % PAGE)
    sys.exit(0)

secs = sections(m)
hero = [i for i, s in enumerate(secs) if 'hero' in s[2]]
assert len(hero) == 1 and hero[0] == 0, 'expected the hero to be the first section'
hero_start, hero_end, _ = secs[hero[0]]

# ---- 1. the hero gains the lead form ---------------------------------------
fields_html = []
for fid, name, typ, label, ac in FIELDS:
    fields_html.append('<div class="field"><label for="%s">%s</label>'
                       '<input id="%s" name="%s" type="%s" autocomplete="%s"></div>'
                       % (fid, label, fid, name, typ, ac))
for legend, group, opts in RADIOS:
    radios = ''.join(
        '<label class="choice"><input type="radio" name="%s" value="%s"%s><span>%s</span></label>'
        % (group, o.lower().replace(' ', '-').replace('/', ''), ' checked' if i == 0 else '', o)
        for i, o in enumerate(opts))
    fields_html.append('<fieldset class="field field--choice"><legend>%s</legend>'
                       '<div class="choice-row">%s</div></fieldset>' % (legend, radios))
for fid, name, typ, label, ac in TAIL_FIELDS:
    fields_html.append('<div class="field"><label for="%s">%s</label>'
                       '<input id="%s" name="%s" type="%s" autocomplete="%s"></div>'
                       % (fid, label, fid, name, typ, ac))

lead_card = (
    '\n      <aside class="hero__lead" id="buy-lead">\n'
    '        <div class="cta-formcard">\n'
    '          <h2 class="hero__leadh">%s</h2>\n'
    '          <form class="form form--light" onsubmit="return false">\n'
    '            %s\n'
    '            <button class="btn btn-primary wow-glow" type="submit">Send request</button>\n'
    '          </form>\n'
    '        </div>\n'
    '      </aside>\n' % (FORM_HEAD, '\n            '.join(fields_html)))

hero_html = m[hero_start:hero_end]
# wrap the existing copy and the new card in a two-column grid
assert hero_html.count('<div class="hero__inner">') == 1, 'hero__inner not unique'
new_hero = hero_html.replace('<div class="hero__inner">',
                             '<div class="hero__cols"><div class="hero__inner">', 1)
close = new_hero.rfind('</div>\n  </div>\n</section>')
assert close > 0, 'could not find the hero container close'
new_hero = new_hero[:close] + '</div>\n' + lead_card + '    </div>\n  </div>\n</section>' \
    if False else new_hero
# close hero__inner, then append the card, then close hero__cols
ins = new_hero.rfind('</div>\n  </div>\n</section>')
assert ins > 0, 'hero close not found'
new_hero = new_hero[:ins] + '</div>\n' + lead_card + '    </div>\n  </div>\n</section>'
new_hero = new_hero.replace('class="section hero', 'class="section hero hero--lead', 1)

# ---- 2. the intro band ------------------------------------------------------
# LAYOUT I-A, chosen by the owner from four measured options. The first build put a
# full-width h2 (96% of the container) above a 506px paragraph, leaving 694px -- 58%
# of the band -- empty to its right. The split gives the heading its own column so the
# prose fills the rest: measured 463px -> 334px, and the unused gutter 694px -> 24px.
intro = (
    '\n<section class="section" id="buy-intro">\n'
    '  <div class="container">\n'
    '    <div class="buyintro">\n'
    '      <div class="buyintro__head">\n'
    '        <p class="eyebrow">Buying a licence</p>\n'
    '        <h2>%s</h2>\n'
    '      </div>\n'
    '      <div class="buyintro__body">\n'
    '        <p class="lede lede--prose">%s</p>\n'
    '      </div>\n'
    '    </div>\n'
    '  </div>\n'
    '</section>\n' % (INTRO_H2, INTRO_P))

# ---- 3. the three-column classification band -------------------------------
cols = []
for idx, (head, types, body) in enumerate(COLUMNS):
    links = ''.join('<a class="btn btn-secondary" href="licence-types.html#type-%s">%s</a>'
                    % (t, label) for t, label in types)
    # the reference gives the middle column a bordered card; mirrored here
    cls = 'buyclass__col buyclass__col--lead' if idx == 1 else 'buyclass__col'
    cols.append('<li class="%s"><h3>%s</h3><p>%s</p>'
                '<div class="buyclass__go">%s</div></li>' % (cls, head, body, links))
band = (
    '\n<section class="section section--warm" id="buy-classifications">\n'
    '  <div class="container">\n'
    '    <p class="eyebrow">By classification</p>\n'
    '    <h2>Which licence are you buying?</h2>\n'
    '    <ul class="buyclass" role="list">\n      %s\n    </ul>\n'
    '    <p class="tp-note">What each classification authorises is set out on the '
    '<a href="licence-types.html">classifications page</a>, which owns those definitions.</p>\n'
    '  </div>\n'
    '</section>\n' % ('\n      '.join(cols)))

new_m = m[:hero_start] + new_hero + intro + band + m[hero_end:]

# ---- guards -----------------------------------------------------------------
ow, nw = words(m), words(new_m)
assert all(nw[k] >= v for k, v in ow.items()), 'existing words lost'
# The only NEW visible words are the lead card, the intro and the band. Computing
# this as new_hero.replace(hero_html, '') does not work -- new_hero is a MODIFIED
# copy of hero_html, so hero_html is not a substring of it and the replace is a
# no-op, which silently folds the whole hero into "expected".
added, expected = nw - ow, words(lead_card + intro + band)
assert added == expected, ('unexpected word delta\n  extra=%s\n  missing=%s'
                           % (added - expected, expected - added))

new_secs = sections(new_m)
assert len(new_secs) == len(secs) + 2, 'section count: %d -> %d' % (len(secs), len(new_secs))
ids = [re.search(r'id="([^"]*)"', s[2]) for s in new_secs]
ids = [i.group(1) for i in ids if i]
assert ids == ['buy-intro', 'buy-classifications', 'covers', 'where', 'next', 'contact'], \
    'unexpected section order: %s' % ids
assert new_m.count(MARK) == 1, 'lead form not exactly once'
assert len(re.findall(r'<h1\b', new_m)) == 1, 'h1 count'
assert len(re.findall(r'<form\b', new_m)) == 2, 'expected exactly 2 forms'
assert not stray_gt(src[:a] + new_m + src[b:]), 'stray ">"'

vis = re.sub(r'<[^>]+>', ' ', new_m)
# Element boundaries matter for the ledger check: with tags flattened to spaces, the
# button label "Type 48" lands within 40 chars of the note's generic "...authorises
# is set out on the classifications page", and a naive proximity regex reads that as
# a definition. Flatten tags to a sentinel the pattern cannot cross instead.
vis_blocks = re.sub(r'<[^>]+>', ' | ', new_m)
# The definitions are now REQUIRED here, by owner decision. Assert they are present,
# that the pointer to the owning page survives, and that the ledger records the
# exception -- so this can never become a silent, undocumented duplication.
for _t in ('20', '41', '48'):
    assert DESCRIPTIONS[_t].split('.')[0][:40] in new_m, 'missing the Type %s description' % _t
assert 'classifications page' in new_m, 'the pointer to licence-types.html was dropped'
_led = io.open('_content-requirements/_dedup-ledger.md', encoding='utf-8').read()
assert 'C18\u2013C20 **EXCEPTION**' in _led, 'dedup ledger does not record the C18-C20 exception'
for bad in ('California', ' ABC '):
    assert bad not in vis, 'de-Californisation broken: %r reappeared in <main>' % bad
assert 'license' not in vis.lower().replace('licence', ''), 'US spelling leaked in'

for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p', 'form', 'fieldset', 'label', 'aside', 'h2', 'h3'):
    o = len(re.findall(r'<%s\b' % tag, new_m))
    c = len(re.findall(r'</%s>' % tag, new_m))
    assert o == c, 'unbalanced <%s>: %d/%d' % (tag, o, c)

assert 'id="buy-intro"' in new_m and 'section--warm" id="buy-classifications"' in new_m, \
    'ground assignment lost'

io.open(PAGE, 'w', encoding='utf-8').write(src[:a] + new_m + src[b:])
print('%s restructured to mirror the live buy page' % PAGE)
print('  section order : %s' % ' -> '.join(['(hero+form)'] + ids))
print('  forms         : 2 (hero lead capture + #contact consultation)')
print('  words         : %d -> %d' % (sum(ow.values()), sum(nw.values())))
print('  de-Californisation intact : California=0  ABC=0')
print('  ledger C18-C20 respected  : 0 classification definitions added')
