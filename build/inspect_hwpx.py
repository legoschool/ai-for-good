# -*- coding: utf-8 -*-
"""base_지도안.hwpx 의 section0.xml 구조를 살펴본다. 개발용 도구."""
import io
import os
import re
import sys
import zipfile

import tasks as T

T.setup_console()

BASE = os.path.join(T.ROOT, "assets", "base_지도안.hwpx")

HP = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"


def main():
    z = zipfile.ZipFile(BASE)
    print("== zip 항목 ==")
    for i in z.infolist():
        kind = "STORED" if i.compress_type == zipfile.ZIP_STORED else "DEFLATED"
        print("  %-34s %8d  %s" % (i.filename, i.file_size, kind))

    xml = z.read("Contents/section0.xml").decode("utf-8")
    print("")
    print("== section0.xml 길이 : %d ==" % len(xml))
    print("== 선두 400자 ==")
    print(xml[:400])

    import xml.etree.ElementTree as ET
    root = ET.fromstring(xml)
    print("")
    print("== 루트 : %s ==" % root.tag)
    kids = list(root)
    print("== 최상위 자식 %d개 ==" % len(kids))
    from collections import Counter
    print(Counter(k.tag.replace(HP, "hp:") for k in kids))

    print("")
    print("== 최상위 문단별 첫 텍스트 (앞 60자) ==")
    for idx, k in enumerate(kids):
        texts = [t.text or "" for t in k.iter(HP + "t")]
        s = "".join(texts).strip()
        mark = ""
        if re.match(r"^\s*\d{1,2}차시\s", s):
            mark = "   <<<< 차시 시작"
        print("  [%3d] %-8s %s%s" % (idx, k.tag.replace(HP, ""), s[:60], mark))

    print("")
    print("== linesegarray 개수 : %d ==" % xml.count("linesegarray"))
    print("== hp:t 개수 : %d ==" % xml.count("<hp:t"))
    print("== 표(hp:tbl) 개수 : %d ==" % xml.count("<hp:tbl"))


if __name__ == "__main__":
    sys.exit(main())
