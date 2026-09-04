#!/usr/bin/env python3
"""
Swap the rebuilt Locations mega menu (CA / FL / AZ) into every page that carries it.

The owner picked the CLASSIFICATIONS nesting after seeing both rendered:

  markets nesting          13 rows, 870px against a 560px panel -- 5 rows clip
  classifications nesting   8 rows, 561px -- 0 rows clip          <- chosen

Both preserve every link. The chosen one also reuses the five existing per-type
detail panels verbatim (each already lists all ten markets), so the 50 market x type
pages stay reachable through 8 rows instead of 13.

SAFE TO SWAP AS ONE STRING: the whole mm-casc block is byte-identical on all 106
pages that carry it (verified, one sha256 across the set), so there is no per-page
variation to preserve. brand-card.html and lock-preview.html have no menu and are
left alone.

FAIL-CLOSED: every page is rebuilt and validated in memory; nothing is written
unless all of them pass. Idempotent -- a second run is a no-op.
"""
import re, io, os, sys, glob, hashlib, html.parser


class _Nest(html.parser.HTMLParser):
    """Real nesting check for the tags the swap touches -- the regex above only
    counts, and cannot see interleaving."""
    TRACK = ('div', 'a', 'ul', 'li', 'button')

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.stray = [], []

    def handle_starttag(self, t, a):
        if t in self.TRACK:
            self.stack.append(t)

    def handle_endtag(self, t):
        if t not in self.TRACK:
            return
        if t in self.stack:
            while self.stack and self.stack[-1] != t:
                self.stray.append(self.stack.pop())
            if self.stack:
                self.stack.pop()
        else:
            self.stray.append(t)

    @property
    def open_at_eof(self):
        return self.stack

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

NEW = io.open('_mm-new-block-classifications.html', encoding='utf-8').read()
assert 'data-mmstate="florida"' in NEW and 'data-mmstate="arizona"' in NEW, 'wrong block file'


def bounds(s):
    i = s.find('mm-casc')
    if i < 0:
        return None
    i = s.rfind('<div', 0, i)
    depth, j = 1, s.find('>', i) + 1
    while depth and j < len(s):
        nx = re.search(r'<(/?)div\b[^>]*>', s[j:])
        if not nx:
            break
        depth += -1 if nx.group(1) else 1
        j += nx.end()
    return i, j


def stray_gt(s):
    t = re.sub(r'<(script|style)\b.*?</\1>', '', s, flags=re.S | re.I)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    t = re.sub(r'<[^<>]*>', '', t)
    return '>' in t


pages = [f for f in sorted(glob.glob('*.html')) if not f.startswith('_')]
staged, skipped, nomenu = {}, [], []

for f in pages:
    s = io.open(f, encoding='utf-8').read()
    b = bounds(s)
    if not b:
        nomenu.append(f)
        continue
    old = s[b[0]:b[1]]
    if 'data-mmstate="florida"' in old:
        skipped.append(f)
        continue

    new_s = s[:b[0]] + NEW + s[b[1]:]

    # ---- guards ------------------------------------------------------------
    # 1. every link the old menu reached is still reachable
    old_links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', old)}
    new_links = {h.split('#')[0] for h in re.findall(r'href="([^"]+)"', NEW)}
    lost = {l for l in old_links - new_links if l}
    assert not lost, '%s: links lost: %s' % (f, sorted(lost))

    # 2. every target exists on disk
    for h in sorted(new_links):
        if h and not h.startswith(('http', 'tel:', 'mailto:', '#')):
            assert os.path.exists(h), '%s: menu points at missing %s' % (f, h)

    # 3. the cascade's own shape
    assert len(re.findall(r'data-mmstate=', new_s)) == 3, '%s: rail must be 3 states' % f
    assert len(re.findall(r'data-mmpane=', new_s)) == 3, '%s: 3 panes' % f
    assert len(re.findall(r'data-mmcard=', new_s)) == 3, '%s: 3 cards' % f
    opts = set(re.findall(r'data-mmopt="([^"]+)"', new_s))
    dets = set(re.findall(r'data-mmdetail="([^"]+)"', new_s))
    assert opts == dets, '%s: rows/panels mismatch %s' % (f, opts ^ dets)

    # 4. all 50 market x type pages still reachable from the menu
    mt = {l for l in new_links if re.match(r'liquor-license-.*-type-\d+\.html$', l)}
    assert len(mt) == 50, '%s: %d market x type links, expected 50' % (f, len(mt))

    # 5. nothing outside the block moved
    assert s[:b[0]] == new_s[:b[0]], '%s: content before the block changed' % f
    assert s[b[1]:] == new_s[len(new_s) - len(s[b[1]:]):], '%s: content after the block changed' % f

    # 6. structural sanity.
    # COUNT ON MARKUP ONLY. A raw regex over the whole file counted about.html as
    # 185 open / 184 close anchors -- but a real parser says the page is perfectly
    # balanced. The extra "open" is the literal text "<a>" inside a CSS comment
    # ("a bare <a> in prose falls back to the UA default"). Strip comments, script
    # and style before counting, and check real nesting with the parser as well.
    markup = re.sub(r'<(script|style)\b.*?</\1>', '', new_s, flags=re.S | re.I)
    markup = re.sub(r'<!--.*?-->', '', markup, flags=re.S)
    for tag in ('div', 'a', 'span', 'ul', 'li', 'p', 'button'):
        o = len(re.findall(r'<%s\b' % tag, markup))
        c = len(re.findall(r'</%s>' % tag, markup))
        assert o == c, '%s: unbalanced <%s> %d/%d' % (f, tag, o, c)
    pr = _Nest(); pr.feed(new_s)
    assert not pr.open_at_eof and not pr.stray, \
        '%s: real nesting broken (open=%s stray=%s)' % (f, pr.open_at_eof, pr.stray)
    assert not stray_gt(new_s), '%s: stray ">"' % f
    # The swap must not CHANGE the h1 count. Asserting "<= 1" was wrong: the new
    # block has no <h1> at all, while design-system.html legitimately carries several
    # as type specimens. What matters is that this edit adds or removes none.
    assert len(re.findall(r'<h1\b', new_s)) == len(re.findall(r'<h1\b', s)), \
        '%s: h1 count changed %d -> %d' % (f, len(re.findall(r'<h1\b', s)),
                                           len(re.findall(r'<h1\b', new_s)))

    staged[f] = new_s

if not staged:
    print('no-op: %d pages already carry the new menu (%d have none)' % (len(skipped), len(nomenu)))
    sys.exit(0)

assert len(staged) + len(skipped) + len(nomenu) == len(pages), 'accounting'

for f, text in staged.items():
    io.open(f, 'w', encoding='utf-8').write(text)

sizes = [(len(io.open(f, encoding='utf-8').read())) for f in staged]
print('swapped the mega menu on %d pages (%d already done, %d have no menu)'
      % (len(staged), len(skipped), len(nomenu)))
print('  rail            : california, florida, arizona')
print('  option rows     : %d   detail panels: %d' % (len(opts), len(dets)))
print('  market x type reachable per page: 50')
print('  pages with no menu: %s' % ', '.join(nomenu))
