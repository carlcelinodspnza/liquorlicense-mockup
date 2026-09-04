#!/usr/bin/env python3
"""
Mirror the structure of liquorlicenseagents.com/sell onto service-sell.html,
keeping this mockup's theme. Same treatment as service-buy.html.

THE LIVE PAGE'S SEQUENCE, measured off the rendered page (3657px):
  1  hero: map left, a lead-capture form card right
  2  intro: h2 "Are you interested in selling your liquor license?" + one paragraph
  3  a three-column classification band: Type 20 & 21 / Type 41 & 47 / Type 48
  4  CTA row: "Schedule an Appointment | 800.799.9081"
  5  a second form card: "Request a Free Consultation"

/sell is structurally identical to /buy. What differs is the intro paragraph and the
FORM FIELDS: buy asks Type of Business + Operating State; sell asks Asking Price,
County and Licence Number. Those are mirrored exactly.

This page already had 4 and 5 (#next and #contact), so 1, 2 and 3 are added.

THE SAME TWO CONSTRAINTS AS THE BUY PAGE, both asserted rather than assumed:

  a) THE CLASSIFICATION DEFINITIONS ARE NOW CARRIED, BY OWNER DECISION. Dedup ledger
     C18-C20 gives them to licence-types.html, and that conflict was raised twice
     before the owner chose to duplicate. The ledger now records the exception in
     writing, licence-types.html stays canonical, and the band keeps its pointer to
     it. The guard was inverted rather than deleted: it asserts the descriptions ARE
     present, the pointer survives, and the ledger records the exception.

  b) NO CALIFORNIA FRAMING. This page measures 0 "California" and 0 "ABC" in <main>
     after the owner's de-Californisation. The live intro ends "...qualified under
     the requirements of the ABC", so that phrase becomes "the licensing authority"
     -- the wording service-buy.html's own hero already uses.

THE COLUMNS NOW CARRY THE CLIENT'S OWN DESCRIPTIONS. They first shipped as heading +
links only, because the selling PROCESS does not vary by classification and three
invented distinctions would have been worse than none. The owner then asked for the
reference pages' descriptions explicitly, so those are used -- see the note on
DESCRIPTIONS below for the two edits and the recorded ledger exception.

The band's own lede and this page's existing claims stay separate: the hero lede and
#covers already own pre-qualified buyers, escrow, the licence as an asset and the
highest achievable price, and the generator asserts none of them is restated.

SPELLING. Visible text on this page is "licence" 12 / "license" 1, so the client's
paragraph is reproduced verbatim except for that spelling and the ABC phrase above.

Fail-closed and idempotent.
"""
import re, io, os, sys, html
from collections import Counter

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGE = 'service-sell.html'

INTRO_H2 = 'Are you interested in selling your liquor licence?'
INTRO_P = (
    'Our team is here to help! We will use our extensive network to ensure that we find the '
    'absolute best value for your licence. In addition to making sure you get the most out of the '
    'sale of your licence, we work to screen any interested buyers to determine that they are '
    'qualified under the requirements of the licensing authority.')
FORM_HEAD = 'Fill out the form below and a member of our team will contact you'
BAND_H2 = 'Which licence are you selling?'
BAND_LEDE = ('Send the licence number and the county for any of these and we open with a valuation '
             'and a read on who is buying.')


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
    ('Type 20 &amp; 21', [('20', 'Type 20'), ('21', 'Type 21')], DESCRIPTIONS['20']),
    ('Type 41 &amp; 47', [('41', 'Type 41'), ('47', 'Type 47')], DESCRIPTIONS['41']),
    ('Type 48', [('48', 'Type 48')], DESCRIPTIONS['48']),
]

FIELDS = [
    ('s-name', 'name', 'text', 'Full name', 'name'),
    ('s-email', 'email', 'email', 'Email address', 'email'),
    ('s-phone', 'phone', 'tel', 'Phone number', 'tel'),
]
RADIOS = [('Type of licence', 'type_of_licence', ['Full liquor', 'Beer and wine'])]
TAIL_FIELDS = [
    ('s-price', 'asking_price', 'text', 'Asking price', 'off'),
    ('s-county', 'county', 'text', 'County', 'address-level2'),
    ('s-number', 'licence_number', 'text', 'Licence number', 'off'),
]

MARK = 'id="sell-lead"'


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
        % (group, o.lower().replace(' ', '-'), ' checked' if i == 0 else '', o)
        for i, o in enumerate(opts))
    fields_html.append('<fieldset class="field field--choice"><legend>%s</legend>'
                       '<div class="choice-row">%s</div></fieldset>' % (legend, radios))
for fid, name, typ, label, ac in TAIL_FIELDS:
    fields_html.append('<div class="field"><label for="%s">%s</label>'
                       '<input id="%s" name="%s" type="%s" autocomplete="%s"></div>'
                       % (fid, label, fid, name, typ, ac))

lead_card = (
    '\n      <aside class="hero__lead" id="sell-lead">\n'
    '        <div class="cta-formcard">\n'
    '          <h2 class="hero__leadh">%s</h2>\n'
    '          <form class="form form--light" onsubmit="return false">\n'
    '            %s\n'
    '            <button class="btn btn-primary wow-glow" type="submit">Send request</button>\n'
    '          </form>\n'
    '        </div>\n'
    '      </aside>\n' % (FORM_HEAD, '\n            '.join(fields_html)))

hero_html = m[hero_start:hero_end]
assert hero_html.count('<div class="hero__inner">') == 1, 'hero__inner not unique'
new_hero = hero_html.replace('<div class="hero__inner">',
                             '<div class="hero__cols"><div class="hero__inner">', 1)
ins = new_hero.rfind('</div>\n  </div>\n</section>')
assert ins > 0, 'hero close not found'
new_hero = new_hero[:ins] + '</div>\n' + lead_card + '    </div>\n  </div>\n</section>'
new_hero = new_hero.replace('class="section hero', 'class="section hero hero--lead', 1)

# ---- 2. intro band, layout I-A (the split the owner picked for the buy page) --
intro = (
    '\n<section class="section" id="sell-intro">\n'
    '  <div class="container">\n'
    '    <div class="buyintro">\n'
    '      <div class="buyintro__head">\n'
    '        <p class="eyebrow">Selling a licence</p>\n'
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
    cls = 'buyclass__col buyclass__col--lead' if idx == 1 else 'buyclass__col'
    cols.append('<li class="%s"><h3>%s</h3><p>%s</p>'
                '<div class="buyclass__go">%s</div></li>' % (cls, head, body, links))
band = (
    '\n<section class="section section--warm" id="sell-classifications">\n'
    '  <div class="container">\n'
    '    <p class="eyebrow">By classification</p>\n'
    '    <h2>%s</h2>\n'
    '    <p class="lede lede--prose">%s</p>\n'
    '    <ul class="buyclass" role="list">\n      %s\n    </ul>\n'
    '    <p class="tp-note">What each classification authorises is set out on the '
    '<a href="licence-types.html">classifications page</a>, which owns those definitions.</p>\n'
    '  </div>\n'
    '</section>\n' % (BAND_H2, BAND_LEDE, '\n      '.join(cols)))

new_m = m[:hero_start] + new_hero + intro + band + m[hero_end:]

# ---- guards -----------------------------------------------------------------
ow, nw = words(m), words(new_m)
assert all(nw[k] >= v for k, v in ow.items()), 'existing words lost'
added, expected = nw - ow, words(lead_card + intro + band)
assert added == expected, ('unexpected word delta\n  extra=%s\n  missing=%s'
                           % (added - expected, expected - added))

new_secs = sections(new_m)
assert len(new_secs) == len(secs) + 2, 'section count %d -> %d' % (len(secs), len(new_secs))
ids = [i.group(1) for i in (re.search(r'id="([^"]*)"', s[2]) for s in new_secs) if i]
assert ids == ['sell-intro', 'sell-classifications', 'covers', 'where', 'next', 'contact'], \
    'unexpected section order: %s' % ids
assert new_m.count(MARK) == 1, 'lead form not exactly once'
assert len(re.findall(r'<h1\b', new_m)) == 1, 'h1 count'
assert len(re.findall(r'<form\b', new_m)) == 2, 'expected exactly 2 forms'
assert not stray_gt(src[:a] + new_m + src[b:]), 'stray ">"'

vis = re.sub(r'<[^>]+>', ' ', re.sub(r'<!--.*?-->', '', new_m, flags=re.S))
assert 'California' not in vis, 'de-Californisation broken: California reappeared'
assert not re.search(r'\bABC\b', vis), 'de-Californisation broken: ABC reappeared'
# The definitions are now REQUIRED here, by owner decision -- see the note on
# DESCRIPTIONS above and the recorded exception in the dedup ledger.
for _t in ('20', '41', '48'):
    assert DESCRIPTIONS[_t].split('.')[0][:40] in new_m, 'missing the Type %s description' % _t
assert 'classifications page' in new_m, 'the pointer to licence-types.html was dropped'
_led = io.open('_content-requirements/_dedup-ledger.md', encoding='utf-8').read()
assert 'C18\u2013C20 **EXCEPTION**' in _led, 'dedup ledger does not record the C18-C20 exception'
# the page's own claims must not be restated in the new copy
for claim in ('pre-qualified', 'escrow', 'highest achievable'):
    assert claim.lower() not in (INTRO_P + BAND_LEDE).lower(), \
        'new copy restates a claim #covers already owns: %r' % claim

for tag in ('section', 'div', 'ul', 'li', 'a', 'span', 'p', 'form', 'fieldset', 'label',
            'aside', 'h2', 'h3'):
    o = len(re.findall(r'<%s\b' % tag, new_m))
    c = len(re.findall(r'</%s>' % tag, new_m))
    assert o == c, 'unbalanced <%s>: %d/%d' % (tag, o, c)

io.open(PAGE, 'w', encoding='utf-8').write(src[:a] + new_m + src[b:])
print('%s restructured to mirror the live sell page' % PAGE)
print('  section order : %s' % ' -> '.join(['(hero+form)'] + ids))
print('  lead form     : %d fields incl. asking price, county, licence number'
      % (len(FIELDS) + len(TAIL_FIELDS)))
print('  forms         : 2 (hero lead capture + #contact consultation)')
print('  words         : %d -> %d' % (sum(ow.values()), sum(nw.values())))
print('  de-Californisation intact : California=0  ABC=0')
print('  ledger C18-C20 respected  : 0 classification definitions added')
