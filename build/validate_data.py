# -*- coding: utf-8 -*-
"""data/lessons.json 무결성 검사. 산출물을 만들기 전에 반드시 통과해야 한다."""
import re
import sys

import tasks as T

T.setup_console()

ERRORS = []
WARNS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNS.append(msg)


FOCUS_SKILLS = {"주체성", "맥락적 사고", "문제해결 사고", "비판적 사고",
                "윤리적 사고", "성찰적 사고", "사회·관계적 사고"}
SUPPORT_SKILLS = {"적응성", "호기심", "창의적 사고", "통합적 사고", "직관적 통찰"}

REQUIRED_LESSON_KEYS = [
    "no", "id", "module", "title", "shortTitle", "problem", "humanSkills",
    "aiComponents", "aiPrinciples", "standards", "subject", "tools", "plan",
    "webapp", "worksheet", "outputs", "assessment", "alternative", "cautions",
]

STAGES = [("intro", 5), ("develop", 30), ("close", 5)]


def check_lesson(l):
    tag = "L%02d" % l.get("no", 0)

    for k in REQUIRED_LESSON_KEYS:
        if k not in l:
            err("%s : 필수 키 없음 -> %s" % (tag, k))
    if not l.get("plan"):
        return

    if l.get("id") != tag:
        err("%s : id 가 %s 여야 한다 (현재 %s)" % (tag, tag, l.get("id")))
    if l.get("module") not in (1, 2, 3):
        err("%s : module 은 1·2·3 중 하나여야 한다" % tag)

    # 학습 문제는 청유형으로 끝난다
    p = l.get("problem", "")
    if not p.endswith("다.") and not p.endswith("까?"):
        warn("%s : 학습 문제 종결이 어색하다 -> %s" % (tag, p[-12:]))
    if "봅시다" not in p and "생각해" not in p:
        warn("%s : 학습 문제가 청유형이 아니다" % tag)

    # 휴먼스킬
    hs = l.get("humanSkills", {})
    focus = hs.get("focus", [])
    if len(focus) != 2:
        err("%s : 중점 휴먼스킬은 2개여야 한다 (현재 %d개)" % (tag, len(focus)))
    for f in focus:
        if f.get("name") not in FOCUS_SKILLS:
            err("%s : 중점 휴먼스킬이 7개 목록에 없다 -> %s" % (tag, f.get("name")))
        for key in ("knowledge", "process", "value"):
            if not f.get(key):
                err("%s : %s 의 %s 가 비어 있다" % (tag, f.get("name"), key))
    for s in hs.get("support", []):
        if s not in SUPPORT_SKILLS and s not in FOCUS_SKILLS:
            err("%s : 보조 휴먼스킬 이름이 목록에 없다 -> %s" % (tag, s))

    # 단계와 시간
    plan = l["plan"]
    for stage, minutes in STAGES:
        if stage not in plan:
            err("%s : plan 에 %s 단계가 없다" % (tag, stage))
            continue
        st = plan[stage]
        if st.get("minutes") != minutes:
            err("%s : %s 단계는 %d분이어야 한다 (현재 %s)" % (tag, stage, minutes, st.get("minutes")))
        if not st.get("blocks"):
            err("%s : %s 단계에 활동 블록이 없다" % (tag, stage))
        if not st.get("materials"):
            err("%s : %s 단계에 준비물·유의점이 없다" % (tag, stage))

    # 발문마다 예상 답변
    for stage, _ in STAGES:
        for b in plan.get(stage, {}).get("blocks", []):
            has_answer = any(t.get("a") for t in b.get("turns", []))
            if not has_answer and b.get("heading") not in ("학습 문제 확인", "다음 차시 예고"):
                err("%s : [%s] 블록에 예상 답변이 하나도 없다" % (tag, b.get("heading")))

    # 전개는 활동 3개 기준
    dev_blocks = plan.get("develop", {}).get("blocks", [])
    if len(dev_blocks) < 2:
        err("%s : 전개 단계 활동이 %d개다. 2개 이상이어야 한다" % (tag, len(dev_blocks)))

    # 유의점 부호
    for stage, _ in STAGES:
        for m in plan.get(stage, {}).get("materials", []):
            if m[0] not in "☆★△":
                err("%s : 준비물 부호가 ☆★△ 가 아니다 -> %s" % (tag, m))

    # 웹앱
    w = l.get("webapp", {})
    if not re.match(r"^[a-z][a-z0-9-]*$", w.get("slug", "")):
        err("%s : 웹앱 slug 형식이 잘못됐다 -> %s" % (tag, w.get("slug")))
    if len(w.get("screens", [])) < 3:
        err("%s : 웹앱 화면이 %d개다. 3개 이상이어야 한다" % (tag, len(w.get("screens", []))))
    if not w.get("teacherView"):
        err("%s : 웹앱에 교사 화면 설명이 없다" % tag)

    # AI 미사용 대안과 유의점
    if not l.get("alternative"):
        err("%s : AI 미사용 대안 활동이 없다" % tag)
    if not l.get("cautions"):
        err("%s : 지도 유의점이 없다" % tag)

    # 금지 표현
    blob = str(l)
    if "—" in blob:
        err("%s : em dash(—) 를 쓰지 않는다" % tag)
    for old in ["허용·조건부·제한", "3단계 신호등", "3수준"]:
        if old in blob:
            err("%s : 옛 3단계 신호등 표현이 남아 있다 -> %s" % (tag, old))


def main():
    data = T.load_lessons()

    lessons = data.get("lessons", [])
    if len(lessons) != 12:
        err("차시가 %d개다. 12개여야 한다" % len(lessons))

    nos = [l.get("no") for l in lessons]
    if nos != list(range(1, 13)):
        err("차시 번호가 1~12 순서가 아니다 -> %s" % nos)

    slugs = [l.get("webapp", {}).get("slug") for l in lessons]
    if len(set(slugs)) != len(slugs):
        err("웹앱 slug 가 중복된다 -> %s" % slugs)

    for l in lessons:
        check_lesson(l)

    # 최상위 구조
    if len(data.get("aiComponents", [])) != 8:
        err("AI적정활용 핵심 구성요소는 8개여야 한다")
    if len(data.get("aiPrinciples", [])) != 11:
        err("실행 원칙은 0번 포함 11개여야 한다")
    if len(data.get("signals", [])) != 4:
        err("신호등은 4단계여야 한다")
    if len(data.get("humanSkills", {}).get("focus", [])) != 7:
        err("중점 휴먼스킬은 7개여야 한다")
    if len(data.get("humanSkills", {}).get("support", [])) != 5:
        err("보조 휴먼스킬은 5개여야 한다")
    if len(data.get("survey", {}).get("items", [])) != 8:
        err("설문 문항은 8개여야 한다")
    if len(data.get("assessmentPlan", [])) != 7:
        err("평가 체계는 중점 7개 역량이어야 한다")

    # 중점 역량이 모두 최소 한 번은 쓰이는가
    used = set()
    for l in lessons:
        for f in l.get("humanSkills", {}).get("focus", []):
            used.add(f.get("name"))
    for s in FOCUS_SKILLS:
        if s not in used:
            err("중점 휴먼스킬 %s 가 어떤 차시에도 쓰이지 않았다" % s)

    for w in WARNS:
        print("주의  %s" % w)
    if ERRORS:
        for e in ERRORS:
            print("실패  %s" % e)
        print("")
        print("NG  오류 %d건" % len(ERRORS))
        return 1

    print("OK  차시 %d개, 필수 키·단계·시간·예상답변·유의점 부호·용어 검사 통과" % len(lessons))
    if WARNS:
        print("    주의 %d건은 통과를 막지 않는다" % len(WARNS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
