#!/usr/bin/env python3
"""
_build-band-option-a.py -- [CL] option A across all 50 market x type pages: the copy and
the bullets stack in one column, the photograph becomes a full-height second column.

OWNER PICKED A (2026-09-02) and asked for it everywhere applicable, following the
context of similar pages.

WHAT IT FIXES, MEASURED: with the picture under the copy the left column ran far taller
than the bullets beside it — 271px + 308px + 167px = **746px of empty bottom-right**
across three bands totalling 2136px. Making the image its own stretched column means the
imbalance cannot exist; the picture absorbs whatever height is left over.

TWO SHAPES ARE BROUGHT INTO ONE
  1. .tp-split bands (40 pages x 3, plus #authorizes on the other 10) — the <figure>
     moves OUT of .tp-split__copy to become a sibling, so the parent grid can place it.
     It cannot be placed from inside the copy div; that is why this is a markup change
     and not CSS alone.
  2. .ca-fig bands on the ten Los Angeles / San Diego pages (#fit, #how) — these were a
     THIRD variant left over from the earlier rollout. They carry long prose and no
     bullet list, so they convert to the same .tp-split shape with the copy column only.
     Leaving them would have meant three different treatments of the same band on one
     site.

IDEMPOTENT -- a band is skipped once its figure is already a direct child of .container.
Fails closed on word loss, image loss, or a shape it does not recognise.
"""
import io, os, re, glob, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = re.compile(r'\s*<figure class="(?:tp-split__media|ca-fig__figure)">.*?</figure>', re.S)


def words(html):
    m = re.search(r'<main[^>]*>(.*?)</main>', html, re.S)
    return len(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', m.group(1))).split())


def rebuild(section_html, name, sid):
    """Return the section rebuilt in the option-A shape, or None if already done."""
    fig = FIG.search(section_html)
    if not fig:
        return None
    figure = fig.group(0).strip().replace('ca-fig__figure', 'tp-split__media')
    # Option A has no caption slot. Dropping a figcaption is only safe because on these
    # bands it is a VERBATIM COPY of the eyebrow that already sits in the copy column —
    # asserted here rather than assumed, so a caption carrying anything unique stops the
    # run instead of being silently deleted.
    cap = re.search(r'<figcaption>(.*?)</figcaption>', figure, re.S)
    dropped_words = 0
    if cap:
        eyebrow = re.search(r'<p class="eyebrow">(.*?)</p>', section_html, re.S)
        cap_txt = re.sub(r'<[^>]+>', '', cap.group(1)).strip().lower()
        eb_txt = re.sub(r'<[^>]+>', '', eyebrow.group(1)).strip().lower() if eyebrow else ''
        if cap_txt != eb_txt:
            print('FAIL %s #%s: figcaption %r is NOT a duplicate of the eyebrow %r — refusing '
                  'to drop it' % (name, sid, cap_txt, eb_txt), file=sys.stderr)
            sys.exit(1)
        dropped_words = len(cap_txt.split())
        figure = re.sub(r'<figcaption>.*?</figcaption>', '', figure, flags=re.S)
    body = FIG.sub('', section_html, count=1)

    # gather the pieces
    eb = re.search(r'<p class="eyebrow">.*?</p>', body, re.S)
    h2 = re.search(r'<h2[^>]*>.*?</h2>', body, re.S)
    ledes = re.findall(r'<p class="lede">.*?</p>', body, re.S)
    ul = re.search(r'<ul[^>]*>.*?</ul>', body, re.S)
    note = re.search(r'<p class="tp-note">.*?</p>', body, re.S)
    if not h2:
        print('FAIL %s #%s: no h2' % (name, sid), file=sys.stderr); sys.exit(1)

    copy = ''
    if eb: copy += '      %s\n' % eb.group(0)
    copy += '      %s\n' % h2.group(0)
    for l in ledes:
        copy += '      %s\n' % l

    listcol = ''
    if ul:
        listcol += '    <div class="tp-split__list">\n      %s\n' % ul.group(0)
        if note:
            listcol += '      %s\n' % note.group(0)
        listcol += '    </div>\n'
    elif note:
        copy += '      %s\n' % note.group(0)

    return ('\n  <div class="container">\n'
            '    <div class="tp-split__copy">\n%s    </div>\n'
            '%s'
            '    %s\n  </div>\n' % (copy, listcol, figure)), dropped_words


def main():
    done = skipped = 0
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        src = io.open(path, encoding='utf-8').read()
        out = src
        touched = 0
        allowed_loss = 0   # only ever the duplicate figcaptions, proven above

        for sid in ('authorizes', 'fit', 'how'):
            m = re.search(r'<section([^>]*)id="%s"([^>]*)>(.*?)</section>' % sid, out, re.S)
            if not m:
                print('FAIL %s: #%s missing' % (name, sid), file=sys.stderr); sys.exit(1)
            attrs, inner = m.group(1) + m.group(2), m.group(3)
            # already in the option-A shape? the figure is a direct child of .container
            if re.search(r'</div>\s*<figure class="tp-split__media">', inner, re.S):
                continue
            res = rebuild(inner, name, sid)
            if res is None:
                continue
            body, dropped = res
            allowed_loss += dropped
            cls = re.search(r'class="([^"]*)"', attrs).group(1).replace('ca-fig', '').split()
            if 'tp-split' not in cls:
                cls.insert(0, 'tp-split')
            open_tag = '<section%sid="%s"%s>' % (m.group(1), sid, m.group(2))
            new_open = re.sub(r'class="[^"]*"', 'class="%s"' % ' '.join(cls), open_tag, count=1)
            out = out.replace(m.group(0), new_open + body + '</section>', 1)
            touched += 1

        if not touched:
            skipped += 1
            continue
        if words(out) < words(src) - allowed_loss:
            print('FAIL %s: lost words %d -> %d (only %d duplicate caption words allowed)'
                  % (name, words(src), words(out), allowed_loss), file=sys.stderr)
            sys.exit(1)
        if out.count('<img') != src.count('<img'):
            print('FAIL %s: image count changed' % name, file=sys.stderr); sys.exit(1)
        if out.count('ca-fig') != 0:
            print('FAIL %s: a ca-fig band survived' % name, file=sys.stderr); sys.exit(1)
        io.open(path, 'w', encoding='utf-8').write(out)
        done += 1

    print('rebuilt %d page(s) · already option A %d' % (done, skipped))


if __name__ == '__main__':
    main()
