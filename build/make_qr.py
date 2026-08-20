# -*- coding: utf-8 -*-
"""차시별 웹앱 주소를 QR 코드로 만든다.

인쇄한 지도안과 활동지에서 학생이 카메라로 찍어 바로 들어가게 하려는 것이다.
SVG 로 만든다. 인쇄에서 깨지지 않고 파일이 작다.

사용법 : py -3 build/make_qr.py
"""
import io
import os
import sys

import segno

import tasks as T

T.setup_console()

SITE_BASE = "https://legoschool.github.io/wise-ai"


def qr_svg(url, path):
    """검정 한 색 SVG. 인쇄와 화면 양쪽에서 쓴다."""
    code = segno.make(url, error="m")
    code.save(path, kind="svg", scale=4, border=2, dark="#111111", light=None)
    return path


def build(data, site):
    out = os.path.join(site, "assets", "qr")
    if not os.path.isdir(out):
        os.makedirs(out)

    made = []
    for lesson in data["lessons"]:
        lid = lesson["id"]
        url = "%s/webapp/%s/index.html" % (SITE_BASE, lid)
        made.append(qr_svg(url, os.path.join(out, "%s.svg" % lid)))

    made.append(qr_svg("%s/webapp/common/index.html" % SITE_BASE,
                       os.path.join(out, "survey.svg")))
    made.append(qr_svg("%s/index.html" % SITE_BASE, os.path.join(out, "home.svg")))
    made.append(qr_svg("%s/guide/index.html" % SITE_BASE, os.path.join(out, "guide.svg")))
    return made


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    made = build(data, site)
    print("QR 코드를 만들었다 : %d개  (%s)" % (len(made), os.path.relpath(os.path.dirname(made[0]), T.ROOT)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
