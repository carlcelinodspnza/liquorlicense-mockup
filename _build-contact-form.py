#!/usr/bin/env python3
"""
Rebuild contact.html's enquiry form to match the client's own /contact-us exactly.

THE OWNER CHOSE THIS WITH THE COST STATED. The form had SEVEN fields because
locations.html's five-step qualifier hands EIGHT answers into it, and site.js's own
comment records that the seven-field rebuild is what made that carry complete:
"all eight answers now land and nothing the visitor typed is lost between the two
pages" (2026-07-29). The reference form has FOUR. Asked to choose, the owner picked
the exact four and accepted the loss.

WHAT IS LOST, precisely, so it is on the record:
  name     -> Full name          kept
  reach    -> Email or Phone     kept, split on whether it contains "@"
  note     -> Message            kept
  business -> (no field)         DROPPED
  industry -> (no field)         DROPPED
  type     -> (no field)         DROPPED
  need     -> (no field)         DROPPED
The fills are null-guarded, so nothing throws -- those answers just stop arriving,
silently. That is the regression the 2026-07-29 change fixed, deliberately re-taken.

THREE PARAGRAPHS WOULD OTHERWISE BECOME FALSE and are rewritten here, not left:
  · "...an availability read on the county you name" -- there is no county field.
  · "Your name, your business and county, what you need and how to reach you land
    here already filled in" -- only name and reach land now.
  · "Leave it on Not sure yet" -- there is no classification control to leave.

RECAPTCHA IS REAL, BY OWNER DECISION, AND IT COSTS THE ZERO-OFF-ORIGIN PROPERTY.
This build previously made NO off-origin requests -- the map is click-to-load and
its own comment calls that embed "the page's ONLY external dependency". Loading
reCAPTCHA means google.com scripts and frames on every view of this page.

THE SITE KEY IS GOOGLE'S PUBLISHED TEST KEY. The client's own key is domain-locked
to liquorlicenseagents.com, would fail here, and using it would mean borrowing their
credential. The test key always passes and gates nothing. It MUST be replaced before
launch -- this script registers that as a blocker in the content registry.

FAIL-CLOSED. An earlier version wrote contact.html and only then tried the site.js
edit, which failed on an indentation mismatch and left the page rebuilt against JS
that still filled seven fields. All three files are staged and written together.
Idempotent.
"""
import re, io, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
PAGE = 'contact.html'
JS = 'design-system/site.js'
REG = '_content-requirements/index.md'

TEST_KEY = '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI'

NEW_FORM = '''<form class="form form--ref" onsubmit="return false">
          <div class="field"><label class="vh" for="q-name">Full name</label>
            <input id="q-name" name="name" type="text" autocomplete="name" placeholder="Full Name*" required></div>
          <div class="field"><label class="vh" for="q-email">Email address</label>
            <input id="q-email" name="email" type="email" autocomplete="email" placeholder="Email Address*" required></div>
          <div class="field"><label class="vh" for="q-phone">Phone number</label>
            <input id="q-phone" name="phone" type="tel" autocomplete="tel" placeholder="+1 (555) 555-5555"></div>
          <div class="field"><label class="vh" for="q-note">Message</label>
            <textarea id="q-note" name="message" placeholder="Message"></textarea></div>
          <div class="field g-recaptcha" data-sitekey="%s"></div>
          <button class="btn btn-primary wow-glow" type="submit">Send request</button>
        </form>''' % TEST_KEY

REWRITES = [
    ("A broker can only be useful once they know what is being bought or sold, where it has to "
     "sit, and how soon. Every field is optional &mdash; answer what you have and leave the rest "
     "&mdash; and the reply comes back with an availability read on the county you name and a "
     "straight account of what happens next.",
     "A broker can only be useful once they know what is being bought or sold, where it has to "
     "sit, and how soon. Put as much of that in the message as you have &mdash; the reply comes "
     "back with an availability read on the market you name and a straight account of what "
     "happens next."),
    ("Arrived from the five-step <a href=\"locations.html#qualifier\">market qualifier</a>? Your "
     "name, your business and county, what you need and how to reach you land here already "
     "filled in. Check them, add whatever else matters, and send.",
     "Arrived from the five-step <a href=\"locations.html#qualifier\">market qualifier</a>? Your "
     "name and how to reach you land here already filled in. Add the market, the classification "
     "and anything else that matters in the message, and send."),
    ("Not sure which classification you are after? Leave it on <b>Not sure yet</b> &mdash; what "
     "each one authorises is set out on the <a href=\"licence-types.html\">classifications "
     "page</a>, and a broker will confirm it against your site either way.",
     "Not sure which classification you are after? Say so in the message &mdash; what each one "
     "authorises is set out on the <a href=\"licence-types.html\">classifications page</a>, and a "
     "broker will confirm it against your site either way."),
]

OLD_COMMENT = """  // UPDATED 2026-07-29 — the carry is now COMPLETE. This comment previously read
  // "contact.html has four fields and the qualifier collects eight answers;
  // industry / type / note have no field to land in and stay in the URL". That was
  // true when contact.html had four fields. Its rebuild added #q-industry, #q-type
  // and #q-note, so all eight answers now land and nothing the visitor typed is
  // lost between the two pages."""

NEW_COMMENT = """  // UPDATED 2026-09-04 — the carry is INCOMPLETE again, deliberately. contact.html
  // was rebuilt to the client's own four-field form on the owner's instruction,
  // with this cost stated and accepted. Only name, reach and note have somewhere to
  // land now; business, industry, type and need are still collected by the
  // qualifier and have no field here, so they stay in the URL and are never shown.
  // Restoring them means restoring the fields — see _build-contact-form.py."""

OLD_FILLS = """      fill('q-name', cq.get('name') || '');
      fill('q-business', biz && mktLabel ? biz + ' — ' + mktLabel : (biz || mktLabel));
      fill('q-reach', cq.get('reach') || '');"""

NEW_FILLS = """      fill('q-name', cq.get('name') || '');
      // reach is ONE field on the qualifier and TWO here, so it is split on the only
      // reliable signal available: an "@" means an address, anything else a number.
      // Guessing wrong would drop an email into a tel input.
      var reach = cq.get('reach') || '';
      if (reach) fill(reach.indexOf('@') > -1 ? 'q-email' : 'q-phone', reach);"""

DEAD = ["      fillSel('q-need', cq.get('need') || '');\n",
        "      fillSel('q-industry', cq.get('industry') || '');\n",
        "      fillSel('q-type', cq.get('type') || '');\n"]


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


src = io.open(PAGE, encoding='utf-8').read()
if 'g-recaptcha' in src:
    print('no-op: contact.html already carries the reference form')
    sys.exit(0)
orig = src

# ---- 1. the form ------------------------------------------------------------
fm = re.search(r'<form class="form"[^>]*>.*?</form>', src, re.S)
assert fm, 'enquiry form not found'
old_names = re.findall(r'name="([^"]+)"', fm.group(0))
assert set(old_names) == {'name', 'business', 'industry', 'type', 'need', 'reach', 'note'}, \
    'not the expected seven-field form: %s' % old_names
src = src[:fm.start()] + NEW_FORM + src[fm.end():]

# ---- 2. the copy the removed fields made false ------------------------------
for before, after in REWRITES:
    assert src.count(before) == 1, 'no unique match for: %r' % before[:60]
    src = src.replace(before, after)

# ---- 3. reCAPTCHA -----------------------------------------------------------
assert 'recaptcha/api.js' not in src, 'recaptcha already loaded'
src = src.replace('</body>',
                  '<script src="https://www.google.com/recaptcha/api.js" async defer></script>\n</body>', 1)

# ---- 4. site.js -------------------------------------------------------------
js = io.open(JS, encoding='utf-8').read()
js_before = js
assert OLD_COMMENT in js, 'the 2026-07-29 comment is not where expected'
js = js.replace(OLD_COMMENT, NEW_COMMENT)
assert OLD_FILLS in js, 'fill block not where expected'
js = js.replace(OLD_FILLS, NEW_FILLS)
for d in DEAD:
    assert d in js, 'missing dead fill %r' % d
    js = js.replace(d, '')
assert js != js_before, 'site.js unchanged'
for gone in ('q-business', 'q-industry', 'q-type', 'q-need', 'q-reach'):
    assert "'%s'" % gone not in js, 'site.js still references %s' % gone
assert js.count('(') == js.count(')'), 'site.js parens unbalanced'
assert js.count('{') == js.count('}'), 'site.js braces unbalanced'
assert js.count('function') == js_before.count('function'), 'site.js function count changed'

# ---- 5. registry ------------------------------------------------------------
reg = io.open(REG, encoding='utf-8').read()
if 'R-CAPTCHA-01' not in reg:
    reg = reg.rstrip('\n') + '\n' + (
        'R-CAPTCHA-01 | integration | "reCAPTCHA site key" — contact.html loads Google reCAPTCHA '
        'with Google\'s PUBLIC TEST KEY %s, which always passes and gates nothing. '
        '⚠ BLOCKER — replace with the client\'s own key before launch; theirs is domain-locked '
        'to liquorlicenseagents.com and cannot be reused here. Loading it also ends this build\'s '
        'zero-off-origin property. ; src: owner decision 2026-09-04\n' % TEST_KEY)

# ---- html guards ------------------------------------------------------------
new_names = re.findall(r'name="([^"]+)"',
                       re.search(r'<form class="form[^"]*"[^>]*>.*?</form>', src, re.S).group(0))
assert new_names == ['name', 'email', 'phone', 'message'], 'unexpected fields: %s' % new_names
for fid in ('q-name', 'q-email', 'q-phone', 'q-note'):
    assert 'id="%s"' % fid in src, 'missing %s' % fid
for gone in ('q-business', 'q-industry', 'q-type', 'q-need', 'q-reach'):
    assert 'id="%s"' % gone not in src, '%s should be gone' % gone
assert src.count('g-recaptcha') == 1 and TEST_KEY in src, 'recaptcha block wrong'
assert len(re.findall(r'<h1\b', src)) == len(re.findall(r'<h1\b', orig)), 'h1 changed'
assert not stray_gt(src), 'stray ">"'
for tag in ('div', 'p', 'a', 'label', 'section', 'form', 'textarea'):
    o = len(re.findall(r'<%s\b' % tag, src)); c = len(re.findall(r'</%s>' % tag, src))
    assert o == c, 'unbalanced <%s> %d/%d' % (tag, o, c)
vis = re.sub(r'<[^>]+>', ' ', re.sub(r'<!--.*?-->', '', src, flags=re.S))
for phrase in ('Not sure yet', 'business and county', 'Every field is optional'):
    assert phrase not in vis, 'copy still describes a removed control: %r' % phrase

# ---- write all three together ----------------------------------------------
io.open(PAGE, 'w', encoding='utf-8').write(src)
io.open(JS, 'w', encoding='utf-8').write(js)
io.open(REG, 'w', encoding='utf-8').write(reg)

print("contact.html rebuilt to the client's four-field form")
print('  fields    : %s' % ', '.join(new_names))
print('  kept      : name, reach (split on "@"), note -> message')
print('  DROPPED   : business, industry, type, need  (qualifier answers with nowhere to land)')
print('  paragraphs rewritten: %d' % len(REWRITES))
print('  reCAPTCHA : REAL, Google test key %s' % TEST_KEY)
print('  registered R-CAPTCHA-01 as a launch BLOCKER')
print('  zero-off-origin property: ENDED for this page')
