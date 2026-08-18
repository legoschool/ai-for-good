# -*- coding: utf-8 -*-
"""다음 작업 하나를 골라 주고, 읽어야 할 파일까지 알려 준다."""
import sys

import tasks as T

T.setup_console()


def header(tasks, state):
    c = T.counts(tasks, state)
    total = len(tasks)
    pct = c["완료"] * 100.0 / total if total else 0
    return "전체 %d건 | 완료 %d 진행 %d 대기 %d 막힘 %d (%.1f%%)" % (
        total, c["완료"], c["진행"], c["대기"], c["막힘"], pct)


def show_status(tasks, state):
    print(header(tasks, state))
    blocked = [t for t in tasks if T.get(state, t["id"])["status"] == "막힘"]
    running = [t for t in tasks if T.get(state, t["id"])["status"] == "진행"]
    if running:
        print("")
        print("진행 중 :")
        for t in running:
            print("  - %s  ->  %s" % (t["id"], t["path"]))
    if blocked:
        print("")
        print("막힌 작업 :")
        for t in blocked:
            print("  - %s : %s" % (t["id"], T.get(state, t["id"])["note"]))


def show_all(tasks, state):
    print(header(tasks, state))
    print("")
    print("  ○ 지금 착수 가능   × 선행 대기   ● 완료   ! 막힘   > 진행 중")
    print("")
    unit = None
    for t in tasks:
        st = T.get(state, t["id"])["status"]
        if st == "완료":
            mark = "●"
        elif st == "막힘":
            mark = "!"
        elif st == "진행":
            mark = ">"
        elif T.ready(t, state):
            mark = "○"
        else:
            mark = "×"
        if t["unit"] != unit:
            unit = t["unit"]
            print("")
        print("  %s  %-34s %s" % (mark, t["id"], t["path"]))


def show_next(tasks, state):
    print(header(tasks, state))

    blocked = [t for t in tasks if T.get(state, t["id"])["status"] == "막힘"]
    if blocked:
        print("")
        print("막힌 작업이 있어 새 작업을 내주지 않는다. 사람이 결정해야 루프가 다시 돈다.")
        for t in blocked:
            print("  - %s : %s" % (t["id"], T.get(state, t["id"])["note"]))
        print("")
        print("결정을 받았으면 아래를 실행한다.")
        print('  py -3 build/update_state.py --decision "질문" "결정" "반영 위치"')
        print('  py -3 build/update_state.py "%s" 대기' % blocked[0]["id"])
        return 2

    running = [t for t in tasks if T.get(state, t["id"])["status"] == "진행"]
    if running:
        t = running[0]
        print("")
        print("이미 진행 중인 작업이 있다. 이것부터 끝낸다.")
        emit(t)
        return 0

    for t in tasks:
        if T.get(state, t["id"])["status"] == "대기" and T.ready(t, state):
            emit(t)
            return 0

    print("")
    print("남은 작업이 없다. 마지막으로 prompts/P6_검수.md 를 돌려 전체를 점검한다.")
    return 0


def emit(t):
    print("")
    print("다음 작업 : %s" % t["id"])
    print("산출 경로 : %s" % t["path"])
    print("")
    print("1. 프롬프트  : %s" % t["prompt"])
    print("2. 읽을 규격 : %s" % t["spec"])
    if t["lesson"]:
        print("3. 데이터    : data/lessons.json 에서 lessons[] 중 no==%d 객체 하나만" % t["lesson"])
    else:
        print("3. 데이터    : data/lessons.json 에서 필요한 최상위 키만")
    print("4. 체크리스트 : loops/checklists/%s" % t["checklist"])
    print("5. 자동 검증 : %s" % t["verify"])
    print("")
    print("시작하려면 : py -3 build/update_state.py \"%s\" 진행" % t["id"])


def main():
    tasks = T.build_tasks()
    state = T.load_state()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "--status":
        show_status(tasks, state)
        return 0
    if arg == "--all":
        show_all(tasks, state)
        return 0
    return show_next(tasks, state)


if __name__ == "__main__":
    sys.exit(main())
