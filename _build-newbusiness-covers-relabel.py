#!/usr/bin/env python3
"""
service-new-business.html's #covers band made a claim its content does not support.

WHAT WAS WRONG. The heading read "Included in new business licence planning" over a
list of 13 links -- 7 services and 6 markets. Three separate problems:
  * it asserts those 13 things are the SCOPE of the service, which they are not;
  * it is circular: "New business licence planning" is listed inside its own scope;
  * the closing note began "Every one of these sits inside the same transaction",
    which is false of a market link.

WHY THE FIX IS RE-LABELLING, NOT A REAL SCOPE LIST. This page states twice -- in its
hero and in its #detail caveat -- that it is "the only service with no source text
behind it: the client's own document repeats the escrow description under this
heading". services.html carries no <ul> scope list for it either, unlike its seven
siblings. So a scope list cannot be written without inventing client claims, and
inventing them is exactly what the page's own flag exists to prevent.

WHY NOT DELETE THE BAND. Checked before assuming: the 13 hrefs are UNIQUE on this
page. #next links to service-buy.html and #where to liquor-license-los-angeles.html,
while this band links to services.html#buy and locations.html#los-angeles -- same
subjects, different destinations. Removing it would drop 13 reachable links.

SO: keep every link, and make the heading and note describe what the list actually is.
No claim is added; a false one is removed.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.join(ROOT, 'service-new-business.html')

OLD_EYEBROW = '<p class="eyebrow">What this covers</p>'
NEW_EYEBROW = '<p class="eyebrow">Where this hands off</p>'
OLD_H2 = '<h2>Included in new business licence planning</h2>'
NEW_H2 = '<h2>Services and markets on this site</h2>'
OLD_NOTE = ('<p class="sv-note">Every one of these sits inside the same transaction &mdash; see\n'
            '      <a href="process.html">how a transfer runs end to end</a>, or the\n'
            '      <a href="licence-types.html">five classifications</a> it can apply to.</p>')
NEW_NOTE = ('<p class="sv-note">Follow any of these for the detail &mdash; or see\n'
            '      <a href="process.html">how a transfer runs end to end</a>, and the\n'
            '      <a href="licence-types.html">five classifications</a> it can apply to.</p>')

src = io.open(PAGE, encoding='utf-8').read()

def covers_span(s):
    m = re.search(r'<section[^>]*id="covers"[^>]*>', s)
    assert m, 'no #covers band'
    st = m.start(); d = 0
    for t in re.finditer(r'<(/?)section\b[^>]*>', s[st:]):
        d += 1 if not t.group(1) else -1
        if d == 0: return st, st + t.end()
    raise SystemExit('unbalanced #covers')

cs, ce = covers_span(src)
band = src[cs:ce]

if NEW_H2 in band:
    print('already re-labelled -- no-op')
    raise SystemExit(0)

hrefs_before = re.findall(r'<li><a href="([^"]+)"', band)
assert len(hrefs_before) == 13, 'expected 13 links, found %d' % len(hrefs_before)

new = band
for old, rep, what in ((OLD_EYEBROW, NEW_EYEBROW, 'eyebrow'),
                       (OLD_H2, NEW_H2, 'h2'),
                       (OLD_NOTE, NEW_NOTE, 'note')):
    assert new.count(old) == 1, '%s not found exactly once -- refusing to guess' % what
    new = new.replace(old, rep)

out = src[:cs] + new + src[ce:]

# ---- guards ----
ns, ne = covers_span(out)
nb = out[ns:ne]
assert re.findall(r'<li><a href="([^"]+)"', nb) == hrefs_before, 'a link was lost or reordered'
assert out.count('<h1') == src.count('<h1') == 1, 'h1 count changed'
assert out.count('<section') == src.count('<section'), 'section count changed'
assert out.count('</section>') == src.count('</section>'), 'section close count changed'
assert out[:cs] == src[:cs] and out[ne:] == src[ce:], 'edit leaked outside #covers'
assert 'Included in new business' not in out, 'the false scope heading survives'
assert 'sits inside the same transaction' not in out, 'the false note survives'
# no stray '>' outside a tag (the [CP]-era guard, kept)
t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
assert '>' not in t, 'stray ">" introduced'

io.open(PAGE, 'w', encoding='utf-8').write(out)
print('re-labelled #covers on service-new-business.html')
print('  eyebrow : What this covers            -> Where this hands off')
print('  heading : Included in new business... -> Services and markets on this site')
print('  note    : false "same transaction" claim removed')
print('  links   : %d preserved, unchanged and in order' % len(hrefs_before))
