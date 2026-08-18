# -*- coding: utf-8 -*-
"""사이트 페이지 하나를 CSS 인라인한 단일 파일로 뽑는다. 미리보기 전용.

사용법 : py -3 build/preview_page.py index.html <내보낼경로>
"""
import io
import os
import sys

import tasks as T

T.setup_console()

SITE = os.path.join(T.ROOT, "out", "site")


def main():
    rel = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(T.ROOT, "out", "preview.html")

    src = os.path.join(SITE, rel)
    with io.open(src, encoding="utf-8") as f:
        html = f.read()
    with io.open(os.path.join(SITE, "assets", "style.css"), encoding="utf-8") as f:
        css = f.read()

    depth = rel.count("/")
    link = '<link rel="stylesheet" href="%sassets/style.css">' % ("../" * depth)
    html = html.replace(link, "<style>\n%s\n</style>" % css)

    d = os.path.dirname(out)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    print("%s  (%d바이트)" % (out, len(html)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
