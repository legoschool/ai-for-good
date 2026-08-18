# -*- coding: utf-8 -*-
"""차시 학생 활동지 HWPX 를 만든다.

사용법 : py -3 build/make_worksheet_hwpx.py 3

지도안 원본의 '단순 문단'만 복제해서 쓴다. 표는 쓰지 않는다.
표를 복제하면 셀 참조가 어긋나 한글이 보안 경고를 띄운다. (CLAUDE.md 3-1절)
"""
import copy
import os
import sys
import xml.etree.ElementTree as ET

import hwpx
import tasks as T

T.setup_console()

P = hwpx.P

TITLE_IDX = 0    # 큰 제목 문단
BODY_IDX = 2     # 본문 문단
BLANK_IDX = 1    # 빈 문단
RULE = "----------------------------------------------------------------------"


def set_text(par, value):
    """문단의 첫 hp:t 에 값을 넣고 나머지 hp:t 는 비운다."""
    nodes = list(par.iter(P + "t"))
    if not nodes:
        return False
    nodes[0].text = value
    for n in nodes[1:]:
        n.text = ""
    return True


def clone(template, value):
    par = copy.deepcopy(template)
    hwpx.strip_linesegarray(par)
    set_text(par, value)
    return par


def worksheet_lines(lesson, data):
    prog = data["program"]
    ws = lesson["worksheet"]
    L = []

    L.append(("title", "%s  학생 활동지" % ws["title"]))
    L.append(("blank", ""))
    L.append(("body", "%d차시  %s" % (lesson["no"], lesson["shortTitle"])))
    L.append(("body", "학습 문제 : %s" % lesson["problem"]))
    L.append(("blank", ""))
    L.append(("body", "학교            학년      반      모둠            닉네임"))
    L.append(("body", RULE))
    L.append(("blank", ""))

    for i, sec in enumerate(ws["sections"], 1):
        L.append(("body", "%d. %s" % (i, sec)))
        for _ in range(4):
            L.append(("body", RULE))
        L.append(("blank", ""))

    L.append(("body", "[ 스스로 점검하기 ]"))
    L.append(("body", "( ) 내 생각을 먼저 쓰고 나서 AI에게 물었다."))
    L.append(("body", "( ) AI의 답을 그대로 쓰지 않고 확인했다."))
    L.append(("body", "( ) 이름, 사진, 친구 이야기 같은 개인정보를 넣지 않았다."))
    L.append(("body", "( ) 오늘 배운 것을 내 말로 설명할 수 있다."))
    L.append(("blank", ""))

    L.append(("body", "[ 오늘 쓰는 웹앱 ]  %s" % lesson["webapp"]["name"]))
    L.append(("body", "방 코드 :                    닉네임 :"))
    L.append(("blank", ""))

    L.append(("body", "[ 기기가 없어도 함께해요 ]"))
    L.append(("body", lesson["alternative"]))
    L.append(("blank", ""))
    L.append(("body", prog["copyrightLine"]))

    return L


def make(no):
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == no][0]

    root = hwpx.load_section()
    kids = list(root)
    tmpl = {
        "title": kids[TITLE_IDX],
        "body": kids[BODY_IDX],
        "blank": kids[BLANK_IDX],
    }

    built = [clone(tmpl[kind], value) for kind, value in worksheet_lines(lesson, data)]

    for k in kids:
        root.remove(k)
    for par in built:
        root.append(par)

    removed = hwpx.strip_linesegarray(root)
    body = "\n".join(hwpx.paragraph_text(p) for p in root)

    out = os.path.join(T.ROOT, "out", "활동지", "WISE_%s_활동지.hwpx" % lesson["id"])
    hwpx.write_hwpx(out, hwpx.serialize(root), prv_text=body)

    print("만들었다 : %s" % out)
    print("  문단 %d개, linesegarray 제거 %d개" % (len(built), removed))
    return out


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/make_worksheet_hwpx.py <차시번호|all>")
        return 1
    if sys.argv[1] == "all":
        for n in range(1, 13):
            make(n)
        return 0
    make(int(sys.argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
