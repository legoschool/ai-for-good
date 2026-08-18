# -*- coding: utf-8 -*-
"""차시 지도안 HWPX 를 만든다.

사용법 : py -3 build/make_lesson_hwpx.py 3
원본 assets/base_지도안.hwpx 에서 해당 차시만 잘라 내고,
data/lessons.json 과 어긋나는 문구를 갈아끼운다.
"""
import os
import re
import sys

import hwpx
import tasks as T

T.setup_console()


def build_mapping(lesson, data):
    """base 원본과 lessons.json 사이의 차이를 메우는 치환표."""
    m = {}

    # 웹앱 이름을 차시별 실제 앱 이름으로 통일한다.
    # 원본은 모듈 묶음 시절의 '웹앱1·2·3' 표기를 쓰고 있다.
    app = lesson["webapp"]["name"]
    for n in ("1", "2", "3"):
        m["웹앱%s " % n] = "웹앱 "
    m["웹앱 데이터 실험실"] = "웹앱 " + app if lesson["no"] == 1 else "웹앱 데이터 실험실"

    # 차시별 웹앱 이름 고정
    known = {
        1: ["데이터 실험실"],
        2: ["AI 검증 실험실"],
        3: ["편향 관찰 갤러리"],
        4: ["정보 분류 카드"],
        5: ["보조·대행 분류판"],
        6: ["AI 신호등 판정단"],
        7: ["우리 반 AI 약속(제안·투표)"],
        8: ["약속 선포 게시판"],
        9: ["3단계 글쓰기 기록판"],
        10: ["사용 습관 자가 점검"],
        11: ["AI for Good 프로젝트 보드"],
        12: ["프로젝트 보드"],
    }
    for name in known.get(lesson["no"], []):
        m["웹앱 " + name] = "웹앱 " + app

    # 12차시는 원본에 '웹앱3 프로젝트 보드'로 되어 있다
    if lesson["no"] == 12:
        m["프로젝트 보드"] = app

    # em dash 는 쓰지 않는다
    m["—"] = ","

    return {k: v for k, v in m.items() if k != v}


def cover_lines(lesson, data):
    """표지 문단을 이 차시 전용으로 바꾼다."""
    prog = data["program"]
    mod = data["modules"][lesson["module"] - 1]
    return {
        "인간중심 사고를 기르는 AI적정활용 수업 WISE초등 5·6학년 12차시 교수·학습 지도안":
            "%s  %d차시 교수·학습 지도안" % (prog["name"], lesson["no"]),
        "○ 모듈1 WISE 발견(1~4차시) : AI를 직접 만들고 겪으며 판단의 재료를 쌓는다.":
            "○ 모듈%d %s(%s) : %s" % (mod["no"], mod["name"], mod["range"], mod["tagline"]),
        "○ 모듈2 WISE 판단(5~8차시) : 겪은 경험 위에 우리 반의 판단 기준을 세운다.":
            "○ 이 차시 : %d차시 %s" % (lesson["no"], lesson["shortTitle"]),
        "○ 모듈3 WISE 실천(9~12차시) : 세운 기준대로 직접 해 보고 돌아본다.":
            "○ 학습 문제 : %s" % lesson["problem"],
    }


def make(lesson_no):
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == lesson_no][0]

    root = hwpx.load_section()
    hwpx.slice_lesson(root, lesson_no)

    mapping = {}
    mapping.update(build_mapping(lesson, data))
    mapping.update(cover_lines(lesson, data))

    changed = hwpx.replace_text(root, mapping)
    removed = hwpx.strip_linesegarray(root)

    kids = list(root)
    body = "\n".join(hwpx.paragraph_text(k) for k in kids)

    out = os.path.join(T.ROOT, "out", "지도안", "WISE_%s_지도안.hwpx" % lesson["id"])
    hwpx.write_hwpx(out, hwpx.serialize(root), prv_text=body)

    print("만들었다 : %s" % out)
    print("  문단 %d개, 텍스트 치환 %d곳, linesegarray 제거 %d개" % (len(kids), changed, removed))
    return out


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/make_lesson_hwpx.py <차시번호|all>")
        return 1
    arg = sys.argv[1]
    if arg == "all":
        for n in range(1, 13):
            make(n)
        return 0
    make(int(arg))
    return 0


if __name__ == "__main__":
    sys.exit(main())
