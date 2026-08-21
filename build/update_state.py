# -*- coding: utf-8 -*-
"""작업 상태를 바꾸고 STATE.md 를 다시 만든다."""
import datetime
import io
import os
import sys

import tasks as T

T.setup_console()

DECISIONS_KEY = "__decisions__"
META_KEY = "__meta__"


def today():
    return datetime.date.today().isoformat()


def render_state_md(tasks, state):
    c = T.counts(tasks, state)
    total = len(tasks)
    pct = c["완료"] * 100.0 / total if total else 0

    running = [t["id"] for t in tasks if T.get(state, t["id"])["status"] == "진행"]
    blocked = [t for t in tasks if T.get(state, t["id"])["status"] == "막힘"]

    L = []
    a = L.append
    a("# STATE.md — 진행 상태 보드")
    a("")
    a("> 루프가 작업을 마칠 때마다 이 파일이 자동으로 갱신된다. 손으로 고치지 않는다.")
    a("> 상태 값: `대기` · `진행` · `완료` · `막힘`")
    a("")
    a("## 지금 상황")
    a("")
    a("- 마지막 갱신 : %s" % state.get(META_KEY, {}).get("updated", "(미갱신)"))
    a("- 진행률 : 완료 %d / 전체 %d (%.1f%%)" % (c["완료"], total, pct))
    a("- 진행 중인 작업 : %s" % (", ".join(running) if running else "없음"))
    a("- 막힌 작업 : %s" % (", ".join(t["id"] for t in blocked) if blocked else "없음"))
    a("")
    a("## 작업 보드")
    a("")
    a("전체 %d개 작업. 12차시 × 7종 + 데이터 1 + 공통 5 + 사이트 2." % total)
    a("")
    a("| 단위 | 산출물 | 상태 | 완료일 | 경로 | 비고 |")
    a("|---|---|---|---|---|---|")
    for t in tasks:
        s = T.get(state, t["id"])
        a("| %s | %s | %s | %s | %s | %s |" % (
            t["unit"], t["name"], s["status"], s.get("done", "-"),
            t["path"], s.get("note", "")))
    a("")
    a("## 막힘 기록")
    a("")
    if blocked:
        for t in blocked:
            s = T.get(state, t["id"])
            a("### %s 막힘 (%s)" % (t["id"], s.get("done", "-")))
            a("- 사유 : %s" % s.get("note", ""))
            a("- 검증 명령 : `%s`" % t["verify"])
            a("")
    else:
        a("없음")
        a("")
    a("## 결정 기록")
    a("")
    a("| 날짜 | 질문 | 결정 | 반영 위치 |")
    a("|---|---|---|---|")
    for d in state.get(DECISIONS_KEY, []):
        a("| %s | %s | %s | %s |" % (d["date"], d["q"], d["a"], d["where"]))
    a("")
    a("---")
    a("")
    a("2026년 G-DEAL A.N.D · CC BY-NC-SA")
    a("")

    with io.open(T.STATE_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))


def usage():
    print("사용법")
    print('  py -3 build/update_state.py "<작업ID>" <대기|진행|완료|막힘> ["비고"]')
    print('  py -3 build/update_state.py --decision "질문" "결정" "반영 위치"')
    print('  py -3 build/update_state.py --render')
    return 1


def main():
    tasks = T.build_tasks()
    state = T.load_state()
    args = sys.argv[1:]

    if not args:
        return usage()

    if args[0] == "--render":
        render_state_md(tasks, state)
        print("STATE.md 를 다시 만들었다.")
        return 0

    if args[0] == "--decision":
        if len(args) < 4:
            return usage()
        state.setdefault(DECISIONS_KEY, []).append(
            {"date": today(), "q": args[1], "a": args[2], "where": args[3]})
        state.setdefault(META_KEY, {})["updated"] = today()
        T.save_state(state)
        render_state_md(tasks, state)
        print("결정을 기록했다 : %s -> %s (%s)" % (args[1], args[2], args[3]))
        return 0

    if len(args) < 2:
        return usage()

    tid, status = args[0], args[1]
    note = args[2] if len(args) > 2 else ""

    ids = [t["id"] for t in tasks]
    if tid not in ids:
        print("그런 작업 ID가 없다 : %s" % tid)
        near = [i for i in ids if tid.split("/")[0] in i]
        if near:
            print("혹시 이것인가 :")
            for i in near[:8]:
                print("  %s" % i)
        return 1

    if status not in T.STATUSES:
        print("상태 값은 %s 중 하나여야 한다." % " · ".join(T.STATUSES))
        return 1

    task = [t for t in tasks if t["id"] == tid][0]
    if status == "진행" and not T.ready(task, state):
        missing = [d for d in task["deps"] if T.get(state, d)["status"] != "완료"]
        print("선행 작업이 끝나지 않았다. 이 작업은 아직 착수할 수 없다.")
        for m in missing:
            print("  대기 중 선행 : %s" % m)
        return 1

    entry = T.get(state, tid)
    entry["status"] = status
    entry["note"] = note or entry.get("note", "")
    if status in ("완료", "막힘"):
        entry["done"] = today()
    elif status == "진행":
        entry["done"] = "-"
    state[tid] = entry
    state.setdefault(META_KEY, {})["updated"] = today()

    T.save_state(state)
    render_state_md(tasks, state)

    c = T.counts(tasks, state)
    print("%s -> %s" % (tid, status))
    print("완료 %d / 전체 %d" % (c["완료"], len(tasks)))
    if status == "완료":
        print("")
        print("다음 작업을 보려면 : py -3 build/next_task.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
