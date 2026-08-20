# -*- coding: utf-8 -*-
"""차시 지도안 HWPX 를 만든다.

사용법 : py -3 build/make_lesson_hwpx.py 3

원본 assets/base_지도안.hwpx 에서 해당 차시만 잘라 내고,
표 안의 글을 data/lessons.json 으로 다시 채운 뒤,
화면용 지도안과 같은 내용(학습 목표, 시간 배분, 판서 계획, 웹앱 운영,
평가 기준, 어려움과 대처, 산출물)을 문단으로 이어 붙인다.

표는 새로 만들지 않는다. 원본 표의 셀 안에서만 문단을 복제한다.
표 자체를 복제하면 셀 참조가 어긋나 한글이 보안 경고를 띄운다. (CLAUDE.md 3-1절)
"""
import os
import sys

import hwpx
import make_view as V
import tasks as T

T.setup_console()

P = hwpx.P

# 원본이 쓰는 문단 모양. 표 안에서 그대로 재사용한다.
PR_ACT = 62      # ◎ 활동 제목
PR_ASK = 63      # - 교사 발문
PR_ANS = 64      # ‧ 예상 답변
PR_MAT = 65      # ☆ ★ △ 준비물과 유의점
PR_CELL = 22     # 단계, 시간 같은 짧은 칸


def build_mapping(lesson, data):
    """표지와 머리글에 남은 옛 표기를 바로잡는다."""
    m = {}
    app = lesson["webapp"]["name"]
    for n in ("1", "2", "3"):
        m["웹앱%s " % n] = "웹앱 "
    known = {
        1: ["데이터 실험실"], 2: ["AI 검증 실험실"], 3: ["편향 관찰 갤러리"],
        4: ["정보 분류 카드"], 5: ["보조·대행 분류판"], 6: ["AI 신호등 판정단"],
        7: ["우리 반 AI 약속(제안·투표)"], 8: ["약속 선포 게시판"],
        9: ["3단계 글쓰기 기록판"], 10: ["사용 습관 자가 점검"],
        11: ["AI for Good 프로젝트 보드"], 12: ["프로젝트 보드"],
    }
    for name in known.get(lesson["no"], []):
        m["웹앱 " + name] = "웹앱 " + app
    if lesson["no"] == 12:
        m["프로젝트 보드"] = app
    m["—"] = ","
    return {k: v for k, v in m.items() if k != v}


def cover_lines(lesson, data):
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


# ---------------------------------------------------------------- 표 채우기

def stage_lines(stage):
    """한 단계의 활동, 발문, 예상 답변을 셀 문단으로 만든다."""
    out = []
    for i, blk in enumerate(stage["blocks"]):
        if i:
            out.append((PR_ANS, ""))
        out.append((PR_ACT, "◎ %s" % blk["heading"]))
        for turn in blk.get("turns", []):
            out.append((PR_ASK, "- %s" % turn["q"]))
            for ans in turn.get("a", []):
                out.append((PR_ANS, "‧ %s" % ans))
    return out or [(PR_ACT, "◎ 활동")]


def fill_table(root, lesson, data):
    """원본 표의 글을 lessons.json 으로 다시 채운다."""
    tbl = None
    for k in list(root):
        found = k.find(".//" + P + "tbl")
        if found is not None and found.get("rowCnt") == "12":
            tbl = found
            break
    if tbl is None:
        return 0

    focus = lesson["humanSkills"]["focus"]
    first = focus[0]
    second = focus[1] if len(focus) > 1 else focus[0]
    plan = lesson["plan"]
    filled = 0

    pairs = [
        ((0, 0), ["휴먼스킬"]),
        ((1, 0), [first["name"]]),
        ((3, 0), ["지식 이해"]), ((5, 0), [first["knowledge"]]),
        ((3, 1), ["과정 기능"]), ((5, 1), [first["process"]]),
        ((3, 2), ["가치 태도"]), ((5, 2), [first["value"]]),
        ((1, 3), [second["name"]]),
        ((3, 3), ["지식 이해"]), ((5, 3), [second["knowledge"]]),
        ((3, 4), ["과정 기능"]), ((5, 4), [second["process"]]),
        ((3, 5), ["가치 태도"]), ((5, 5), [second["value"]]),
        ((0, 6), ["학습 주제"]), ((5, 6), [lesson["shortTitle"]]),
        ((0, 7), ["학습 문제"]), ((5, 7), [lesson["problem"]]),
        ((0, 8), ["차시"]), ((2, 8), ["단계"]), ((3, 8), ["시간"]),
        ((4, 8), ["교수·학습활동"]), ((6, 8), ["준비 자료와 유의점"]),
        ((0, 9), [str(lesson["no"])]),
        ((2, 9), [(PR_CELL, "도입")]), ((3, 9), [(PR_CELL, "%d‘" % plan["intro"]["minutes"])]),
        ((4, 9), stage_lines(plan["intro"])),
        ((6, 9), [(PR_MAT, x) for x in plan["intro"]["materials"]]),
        ((2, 10), [(PR_CELL, "전개")]), ((3, 10), [(PR_CELL, "%d‘" % plan["develop"]["minutes"])]),
        ((4, 10), stage_lines(plan["develop"])),
        ((6, 10), [(PR_MAT, x) for x in plan["develop"]["materials"]]),
        ((2, 11), [(PR_CELL, "정리")]), ((3, 11), [(PR_CELL, "%d‘" % plan["close"]["minutes"])]),
        ((4, 11), stage_lines(plan["close"])),
        ((6, 11), [(PR_MAT, x) for x in plan["close"]["materials"]]),
    ]
    for (col, row), lines in pairs:
        filled += hwpx.fill_cell(hwpx.cell_of(tbl, col, row), lines)
    return filled


# ---------------------------------------------------------------- 이어 붙이는 문단

def detail_lines(lesson, data):
    """표 뒤에 붙는 상세 안내. 화면용 지도안과 같은 내용이다."""
    w = lesson["webapp"]
    L = []
    head = lambda t: L.append(("head", t))
    body = lambda t: L.append(("body", t))
    blank = lambda: L.append(("blank", ""))

    blank()
    head("1. 학습 목표")
    for o in V.objectives(lesson):
        body("  ㆍ%s" % o)
    body("  △ 교사가 정답을 먼저 말하지 않는다. 판단이 갈리는 자리가 이 수업의 알맹이다.")
    blank()

    head("2. 시간 배분")
    for start, span, label, what in V.minute_plan(lesson):
        body("  %2d분 ~ %2d분   %-6s %d분   %s" % (start, start + span, label, span, what))
    blank()

    head("3. 판서 계획")
    for line in V.board_plan(lesson):
        body("  ㆍ%s" % line)
    blank()

    head("4. 오늘 쓰는 웹앱")
    body("  ㆍ이름 : %s" % w["name"])
    body("  ㆍ하는 일 : %s" % w["purpose"])
    for i, sc in enumerate(w["screens"], 1):
        body("  ㆍ화면 %d. %s" % (i, sc))
    body("  ㆍ교사 화면 : %s" % w.get("teacherView", ""))
    body("  ㆍ운영 : 선생님 화면에서 새 방 만들기를 누르면 여섯 자리 코드가 나온다. "
         "코드를 복사해 학생에게 알려 주고, 수업이 끝나면 방 잠그기를 누른다.")
    body("  ㆍ학생은 방 코드와 닉네임, 나만 아는 숫자 네 자리로 들어온다. 실명은 받지 않는다.")
    body("  ㆍ주소 : https://legoschool.github.io/wise-ai/webapp/%s/" % lesson["id"])
    body("  ㆍ사용 안내(화면 캡처와 QR) : https://legoschool.github.io/wise-ai/guide/%s.html"
         % lesson["id"])
    body("  ㆍ인쇄용 지도안에는 QR 코드와 화면 캡처가 함께 있다. 화면에서 열어 인쇄한다.")
    blocks = lesson["plan"]["develop"]["blocks"]
    screens = w.get("screens", [])
    if screens and blocks:
        body("  ㆍ활동과 화면의 짝")
        for i, blk in enumerate(blocks):
            k = min(i, len(screens) - 1)
            body("    - %s → 웹앱 %s 화면 (학생이 남긴 것이 활동지 %d번 칸이 된다)"
                 % (blk["heading"], screens[k], k + 1))
    body("  ㆍ결과 크게 띄우기를 누르면 학급 화면용 큰 글씨로 결과만 보여 준다.")
    if w.get("steps"):
        for st in w["steps"]:
            body("  ㆍ%d단계 %s (%d분) : %s" % (st["no"], st["title"], st["minutes"], st["what"]))
    blank()

    head("5. 평가 기준")
    for name, hi, mid, low in V.rubric(lesson):
        body("  ㆍ%s" % name)
        body("    잘함 : %s" % hi)
        body("    보통 : %s" % mid)
        body("    도움 필요 : %s" % low)
    body("  △ 정답을 맞혔는지가 아니라 까닭을 댈 수 있는지를 본다.")
    body("  △ 웹앱 교사 화면의 제출 기록, 활동지, 판단이 갈린 자리에서 든 까닭을 함께 본다.")
    blank()

    head("6. 자주 나오는 어려움과 대처")
    for what, how in V.TROUBLE:
        body("  ㆍ%s → %s" % (what, how))
    blank()

    head("7. 지도 유의점")
    for c in lesson["cautions"]:
        body("  △ %s" % c)
    body("  △ 이름, 사진, 친구 이야기를 넣지 않도록 활동 전에 한 번 짚어 준다. "
         "웹앱은 닉네임만 받고 실명과 학번을 묻지 않는다.")
    blank()

    head("8. 학생 활동지 작성 예시")
    body("  ㆍ아래 예시는 활동지에도 같은 문장으로 실려 있다. 학생이 무엇을 쓰는지 먼저 보여 준 뒤 지운다.")
    ws = lesson["worksheet"]
    samples = V.ws_examples(lesson, len(ws["sections"]))
    for i, sec in enumerate(ws["sections"], 1):
        title = sec["title"] if isinstance(sec, dict) else str(sec)
        body("  %d. %s" % (i, title))
        if samples[i - 1]:
            body("     예시) %s" % samples[i - 1])
    blank()

    head("9. 기기가 없어도 함께하는 길")
    body("  ㆍ%s" % lesson["alternative"])
    blank()

    head("10. 산출물과 교육과정")
    body("  ㆍ성취기준 : %s" % " ".join(lesson["standards"]))
    body("  ㆍ교과와 시수 : %s" % lesson["subject"])
    body("  ㆍ학생 산출물 : %s" % ", ".join(lesson["outputs"]))
    body("  ㆍ평가 방법 : %s" % ", ".join(lesson["assessment"]))
    body("  ㆍ수업 도구 : %s" % ", ".join(lesson["tools"]))
    blank()
    body(data["program"]["copyrightLine"])
    return L


def append_details(root, lesson, data):
    kids = list(root)
    head_tpl = None
    body_tpl = None
    blank_tpl = None
    for k in kids:
        if k.find(".//" + P + "tbl") is not None:
            continue
        pr = k.get("paraPrIDRef")
        text = hwpx.paragraph_text(k).strip()
        if pr == "36" and head_tpl is None:
            head_tpl = k
        elif pr == "69" and text and body_tpl is None:
            body_tpl = k
        elif not text and blank_tpl is None:
            blank_tpl = k
    if body_tpl is None:
        body_tpl = kids[-1]
    if head_tpl is None:
        head_tpl = body_tpl
    if blank_tpl is None:
        blank_tpl = body_tpl

    added = 0
    for kind, text in detail_lines(lesson, data):
        tpl = {"head": head_tpl, "body": body_tpl, "blank": blank_tpl}[kind]
        root.append(hwpx.clone_para(tpl, text))
        added += 1
    return added


# ---------------------------------------------------------------- 만들기

def make(lesson_no):
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == lesson_no][0]

    root = hwpx.load_section()
    hwpx.slice_lesson(root, lesson_no)

    mapping = {}
    mapping.update(build_mapping(lesson, data))
    mapping.update(cover_lines(lesson, data))
    changed = hwpx.replace_text(root, mapping)

    filled = fill_table(root, lesson, data)
    added = append_details(root, lesson, data)
    removed = hwpx.strip_linesegarray(root)

    kids = list(root)
    body = "\n".join(hwpx.paragraph_text(k) for k in kids)

    out = os.path.join(T.ROOT, "out", "지도안", "WISE_%s_지도안.hwpx" % lesson["id"])
    hwpx.write_hwpx(out, hwpx.serialize(root), prv_text=body)

    print("만들었다 : %s" % out)
    print("  문단 %d개, 표 칸 %d개, 덧붙인 문단 %d개, 치환 %d곳, linesegarray 제거 %d개"
          % (len(kids), filled, added, changed, removed))
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
