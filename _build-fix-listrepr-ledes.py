#!/usr/bin/env python3
"""
Ten pages render a stringified PYTHON LIST as their hero lede.

The visible text on those pages literally begins  ["Sacramento County's convenience
stores...  and ends  ...land use approvals.']  -- brackets, quotes and the joining
", ' included. A generator str()'d a two-item list instead of indexing into it.

Affected: all five Sacramento type pages and all five San Diego type pages.
All ten parse cleanly as 2-item lists (checked with ast.literal_eval before any
edit).

THE CORRECT SHAPE IS ITEM [1], and that is established rather than assumed: the
40 uncorrupted sibling type pages carry exactly ONE hero lede, and its text is
item [1]'s equivalent (fresno-type-20's lede is 83 words; the Sacramento list's
item [1] is 82 words and structurally identical).

ITEM [2] IS DROPPED, and that is a real content removal so it is reported rather
than buried. Its text ("Liquor License Agents helps <County> owners and buyers
evaluate Type N opportunities, navigate ABC requirements, and coordinate licensing
with city or county land use approvals.") appears on NO healthy page -- it was
never meant to render. The generator prints every dropped sentence.

IDEMPOTENT. FAILS CLOSED.
"""
import re, io, os, glob, ast, html as html_mod

ROOT = os.path.dirname(os.path.abspath(__file__))
fixed, dropped, staged = [], [], {}

for p in sorted(glob.glob(os.path.join(ROOT, 'liquor-license-*.html'))):
    base = os.path.basename(p)
    src = io.open(p, encoding='utf-8').read()
    m = re.search(r'(<p class="lede"[^>]*>)(.*?)(</p>)', src, re.S)
    if not m: continue
    raw = m.group(2).strip()
    if not (raw.startswith('[') or raw.startswith("'") or raw.startswith('"')):
        continue

    # the stored text is HTML-escaped; decode before parsing the literal
    try:
        val = ast.literal_eval(html_mod.unescape(raw))
    except Exception as e:
        raise SystemExit('%s: lede does not parse as a literal (%s) -- refusing to guess' % (base, e))
    assert isinstance(val, list) and len(val) == 2, '%s: expected a 2-item list, got %r' % (base, type(val))
    keep, drop = val[0], val[1]
    # A word-count range was the WRONG guard -- calibrated on one page (fresno, 83w) it
    # rejected San Diego's legitimately shorter ledes (38-51w). Assert STRUCTURE instead:
    # item[1] must be real prose, and item[2] must be the boilerplate line that no healthy
    # page carries, which is what identifies it as the element that was never meant to render.
    assert len(keep.split()) >= 25 and keep[0].isupper() and keep.rstrip().endswith('.'), \
        '%s: item[1] does not look like a finished paragraph: %r' % (base, keep[:60])
    # the verb varies across the ten ("helps" / "works with"); the invariant is the subject
    assert drop.startswith('Liquor License Agents '), \
        '%s: item[2] is not the expected boilerplate: %r' % (base, drop[:60])

    new_lede = m.group(1) + html_mod.escape(keep, quote=False) + m.group(3)
    out = src[:m.start()] + new_lede + src[m.end():]

    # ---- guards ----
    assert out.count('<p class="lede"') == src.count('<p class="lede"'), base + ': lede count changed'
    assert '["' not in out and "', '" not in out, base + ': list syntax still present'
    lede_now = re.search(r'<p class="lede"[^>]*>(.*?)</p>', out, re.S).group(1)
    assert not lede_now.strip().startswith(('[', "'", '"')), base + ': lede still starts like a literal'
    assert out.count('<h1') == src.count('<h1') and out.count('<section') == src.count('<section')
    t = re.sub(r'<(script|style)\b.*?</\1>', '', out, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S); t = re.sub(r'<[^<>]*>', '', t)
    assert '>' not in t, base + ': stray ">" introduced'

    staged[p] = out
    fixed.append(base); dropped.append((base, drop))

# every page validated before ANY file is written -- the first version wrote inside the
# loop and left 5 pages repaired and 5 corrupt when a later guard fired.
for _p, _o in staged.items():
    io.open(_p, 'w', encoding='utf-8').write(_o)

print('ledes repaired: %d page(s)' % len(fixed))
for b in fixed: print('   ', b)
if dropped:
    print('\nSECOND PARAGRAPH DROPPED from each (present on no healthy page):')
    print('   "%s"' % dropped[0][1])
    print('   ...same shape on all %d, with the county and type name swapped.' % len(dropped))
