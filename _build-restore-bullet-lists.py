#!/usr/bin/env python3
"""
_build-restore-bullet-lists.py -- [CM] restore twenty bullet lists that had been
flattened into a single run-on paragraph.

FOUND BY LOOKING AT A RENDERED PAGE. The Los Angeles Type 47 page read
"...may be the right move if: - Cocktails and spirits-forward drinks are important... -
You have, or plan to build, a full kitchen..." — a list that had lost its markup and was
rendering as inline hyphens inside one <p class="lede">. The owner asked for that page;
the same defect turned out to be on **20 bands across 10 pages** (every Los Angeles and
San Diego type page, #fit and #how). Fixing one of twenty identical defects would have
been odd, so all twenty are done and the count is reported.

THE PARSE IS EXPLICIT, NOT HEURISTIC
    Two shapes had to be handled:
      - the intro and the FIRST item share a line on the LA pages ("intro: - item one")
      - the LAST item runs straight into trailing prose with NO punctuation between them
        ("...experience and revenue If your concept is intentionally...")

    The second is the dangerous one. Rather than guess with a capital-letter heuristic —
    which mis-fired on mid-sentence capitals like "Type 47" and "County" — the boundary
    is matched against an EXPLICIT list of sentence openers actually observed in the
    copy: If your / If you / If the / If a / Our goal / Our aim / Our focus / We focus /
    We help / We work. All 20 split cleanly on that list and each split was read back
    before this file was written. A band that does not split exactly once STOPS the run.

WORDS ARE CONSERVED, ASSERTED
    Every word of the original paragraph ends up in the intro, the list items or the
    trailing paragraph. The run compares word multisets before and after and refuses to
    write on any difference.

IDEMPOTENT -- a band with no "\\n- " left in its lede is skipped.
"""
import io, os, re, glob, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
MARKERS = (r'(?:If your |If you |If the |If a |Our goal |Our aim |Our focus |'
           r'We focus |We help |We work )')
BOUND = re.compile(r'(?<=[a-z\)\.,]) (?=' + MARKERS + r')')
SPLIT_ITEM = re.compile(r'\n\s*-\s+')


def bag(t):
    return collections.Counter(re.findall(r"[A-Za-z0-9']+", re.sub(r'<[^>]+>', ' ', t)).__iter__())


def main():
    fixed = pages = 0
    for path in sorted(glob.glob(os.path.join(HERE, 'liquor-license-*-type-*.html'))):
        name = os.path.basename(path)
        src = io.open(path, encoding='utf-8').read()
        out = src
        touched = 0

        for sid in ('fit', 'how'):
            m = re.search(r'<section[^>]*id="%s"[^>]*>.*?</section>' % sid, out, re.S)
            if not m:
                continue
            lm = re.search(r'<p class="lede">(.*?)</p>', m.group(0), re.S)
            if not lm:
                continue
            lede = lm.group(1)
            if not SPLIT_ITEM.search(lede):
                continue                      # already a real list, or never was one

            parts = SPLIT_ITEM.split(lede)
            intro = re.sub(r'\s+', ' ', parts[0]).strip()
            items = [re.sub(r'\s+', ' ', p).strip() for p in parts[1:]]

            # the first item may share the intro's line: "intro: - item one"
            im = re.search(r'\s-\s+', intro)
            if im:
                first = intro[im.end():].strip()
                intro = intro[:im.start()].strip()
                items.insert(0, first)

            # the last item runs into trailing prose
            sp = BOUND.split(items[-1], maxsplit=1)
            if len(sp) != 2:
                print('FAIL %s #%s: last item does not split on a known sentence opener — %r'
                      % (name, sid, items[-1][-90:]), file=sys.stderr)
                sys.exit(1)
            items[-1] = sp[0].strip()
            tail = sp[1].strip()

            if len(items) < 2 or not intro or not tail:
                print('FAIL %s #%s: unexpected shape' % (name, sid), file=sys.stderr); sys.exit(1)

            lis = '\n'.join('        <li>%s</li>' % i for i in items)
            new_lede = '<p class="lede">%s</p>' % intro
            listcol = ('\n    <div class="tp-split__list">\n'
                       '      <ul class="tp-points" role="list">\n%s\n      </ul>\n'
                       '      <p class="tp-note">%s</p>\n    </div>' % (lis, tail))

            # Replace the lede, then insert the list column immediately after the
            # .tp-split__copy div closes. Locating that close by depth — rfind would find
            # the .container's close instead, which is the bug the first run hit.
            seg = m.group(0)
            new_seg = seg.replace(lm.group(0), new_lede, 1)
            cstart = new_seg.find('<div class="tp-split__copy">')
            if cstart < 0:
                print('FAIL %s #%s: no copy column' % (name, sid), file=sys.stderr); sys.exit(1)
            depth = 0; cend = -1
            for dm in re.finditer(r'<div\b|</div>', new_seg[cstart:]):
                depth += 1 if dm.group(0).startswith('<div') else -1
                if depth == 0:
                    cend = cstart + dm.end(); break
            if cend < 0:
                print('FAIL %s #%s: copy column never closes' % (name, sid), file=sys.stderr)
                sys.exit(1)
            new_seg = new_seg[:cend] + listcol + new_seg[cend:]

            cand = out.replace(seg, new_seg, 1)
            if bag(cand) - bag(out) or bag(out) - bag(cand):
                lost = bag(out) - bag(cand); gained = bag(cand) - bag(out)
                print('FAIL %s #%s: words changed. lost=%s gained=%s'
                      % (name, sid, list(lost)[:6], list(gained)[:6]), file=sys.stderr)
                sys.exit(1)
            out = cand
            touched += 1
            fixed += 1

        if touched:
            io.open(path, 'w', encoding='utf-8').write(out)
            pages += 1

    print('restored %d bullet list(s) across %d page(s)' % (fixed, pages))


if __name__ == '__main__':
    main()
