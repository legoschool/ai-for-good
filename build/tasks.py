# -*- coding: utf-8 -*-
"""92개 작업 정의. next_task.py 와 update_state.py 가 함께 쓴다."""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LESSONS = os.path.join(ROOT, "data", "lessons.json")
STATE_JSON = os.path.join(ROOT, "data", "state.json")
STATE_MD = os.path.join(ROOT, "STATE.md")

STATUSES = ["대기", "진행", "완료", "막힘"]


def setup_console():
    """윈도우 콘솔에서 한글이 깨지지 않게 한다."""
    for stream in ("stdout", "stderr"):
        s = getattr(sys, stream)
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8")
            except Exception:
                pass


def load_lessons():
    with io.open(LESSONS, encoding="utf-8") as f:
        return json.load(f)


# 차시 안에서 이 순서를 어길 수 없다.
LESSON_KINDS = [
    ("지도안", "out/지도안/WISE_{lid}_지도안.hwpx", "prompts/P1_지도안.md",
     "CL1_지도안.md", "CLAUDE.md 3-1절, spec/04_산출물_규격.md A절",
     'py -3 build/validate_hwpx.py "out/지도안/WISE_{lid}_지도안.hwpx"'),
    ("활동지", "out/활동지/WISE_{lid}_활동지.hwpx", "prompts/P2b_활동지.md",
     "CL2_활동지.md", "CLAUDE.md 3-1절, spec/04_산출물_규격.md B절",
     'py -3 build/validate_hwpx.py "out/활동지/WISE_{lid}_활동지.hwpx"'),
    ("PPT", "out/ppt/WISE_{lid}_수업.pptx", "prompts/P2_PPT.md",
     "CL2b_PPT.md", "CLAUDE.md 3-4절, spec/04_산출물_규격.md C절",
     'py -3 build/validate_pptx.py "out/ppt/WISE_{lid}_수업.pptx"'),
    ("웹앱 구성안", "out/webapp/{lid}/SPEC.md", "prompts/P3a_웹앱_구성안과_프롬프트.md",
     "CL3a_웹앱_구성안.md", "spec/07_웹앱_공통사양.md 전체",
     'py -3 build/validate_webapp_spec.py "out/webapp/{lid}"'),
    ("웹앱 프롬프트", "out/webapp/{lid}/PROMPT.md", "prompts/P3a_웹앱_구성안과_프롬프트.md",
     "CL3a_웹앱_구성안.md", "spec/07_웹앱_공통사양.md 전체",
     'py -3 build/validate_webapp_spec.py "out/webapp/{lid}"'),
    ("웹앱 구현", "out/webapp/{lid}/index.html", "prompts/P3_웹앱.md",
     "CL3_웹앱.md", "spec/07_웹앱_공통사양.md, spec/05_디자인_시스템.md",
     'node build/smoke_webapp.js "out/webapp/{lid}"'),
    ("사이트 차시 페이지", "out/site/lesson/{lid}.html", "prompts/P5_웹사이트_구현.md",
     "CL5_사이트.md", "spec/05_디자인_시스템.md, spec/08_사이트_구조.md",
     'node build/check_site.js out/site'),
]

COMMON_TASKS = [
    ("데이터", "lessons.json 확정", "data/lessons.json", "-", "-", "-",
     "py -3 build/validate_data.py", []),
    ("공통", "사전·사후 설문 웹앱", "out/webapp/common/index.html",
     "prompts/P3_웹앱.md", "CL3_웹앱.md", "spec/07_웹앱_공통사양.md",
     'node build/smoke_webapp.js out/webapp/common', []),
    ("공통", "12차시 웹앱 모음 허브", "out/site/apps.html",
     "prompts/P5_웹사이트_구현.md", "CL5_사이트.md", "spec/08_사이트_구조.md",
     "node build/check_site.js out/site",
     ["L%02d/웹앱 구현" % n for n in range(1, 13)]),
    ("공통", "학교자율시간 진도표", "out/서류/WISE_학교자율시간_진도표.xlsx",
     "prompts/P7_서류.md", "CL6_서류.md", "spec/04_산출물_규격.md D절",
     "py -3 build/validate_xlsx.py", []),
    ("공통", "카드 교구 3종", "out/교구/", "prompts/P7_서류.md", "CL6_서류.md",
     "spec/04_산출물_규격.md E절", "사람 확인", ["L04/지도안", "L05/지도안", "L06/지도안"]),
    ("공통", "교사용 해설서", "out/해설서/WISE_교사용_해설서.hwpx",
     "prompts/P7_서류.md", "CL6_서류.md", "spec/04_산출물_규격.md F절",
     'py -3 build/validate_hwpx.py "out/해설서/WISE_교사용_해설서.hwpx"',
     ["L%02d/지도안" % n for n in range(1, 13)]),
    ("SITE", "웹사이트 디자인 시안", "out/site/design/", "prompts/P4_웹사이트_디자인.md",
     "CL5_사이트.md", "spec/05_디자인_시스템.md, spec/08_사이트_구조.md",
     "사람 확인", []),
    ("SITE", "웹사이트 구현", "out/site/index.html", "prompts/P5_웹사이트_구현.md",
     "CL5_사이트.md", "spec/05_디자인_시스템.md, spec/08_사이트_구조.md",
     "node build/check_site.js out/site", ["SITE/웹사이트 디자인 시안"]),
]


def build_tasks():
    """작업 92건을 순서대로 만든다."""
    data = load_lessons()
    tasks = []

    # 데이터 확정 1건
    unit, name, path, prompt, cl, spec, verify, deps = COMMON_TASKS[0]
    tasks.append({
        "id": "%s/%s" % (unit, name), "unit": unit, "name": name, "path": path,
        "prompt": prompt, "checklist": cl, "spec": spec, "verify": verify,
        "deps": deps, "lesson": None,
    })

    # 차시별 84건
    for lesson in data["lessons"]:
        lid = lesson["id"]
        prev = None
        for kind, path, prompt, cl, spec, verify in LESSON_KINDS:
            tid = "%s/%s" % (lid, kind)
            deps = ["데이터/lessons.json 확정"]
            if prev:
                deps.append(prev)
            tasks.append({
                "id": tid, "unit": lid, "name": kind,
                "path": path.format(lid=lid),
                "prompt": prompt, "checklist": cl, "spec": spec,
                "verify": verify.format(lid=lid),
                "deps": deps, "lesson": lesson["no"],
            })
            prev = tid

    # 공통·사이트 7건
    for unit, name, path, prompt, cl, spec, verify, deps in COMMON_TASKS[1:]:
        tasks.append({
            "id": "%s/%s" % (unit, name), "unit": unit, "name": name, "path": path,
            "prompt": prompt, "checklist": cl, "spec": spec, "verify": verify,
            "deps": ["데이터/lessons.json 확정"] + list(deps), "lesson": None,
        })

    return tasks


def load_state():
    if not os.path.exists(STATE_JSON):
        return {}
    with io.open(STATE_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with io.open(STATE_JSON, "w", encoding="utf-8") as f:
        f.write(json.dumps(state, ensure_ascii=False, indent=2))


def get(state, tid):
    return state.get(tid, {"status": "대기", "done": "-", "note": ""})


def counts(tasks, state):
    c = {s: 0 for s in STATUSES}
    for t in tasks:
        c[get(state, t["id"])["status"]] += 1
    return c


def ready(task, state):
    """선행 작업이 모두 완료면 착수 가능."""
    for d in task["deps"]:
        if get(state, d)["status"] != "완료":
            return False
    return True
