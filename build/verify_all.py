# -*- coding: utf-8 -*-
"""전체 산출물을 한 번에 검증한다.

사용법 : py -3 build/verify_all.py
"""
import os
import subprocess
import sys

import tasks as T

T.setup_console()

PY = [sys.executable]
NODE = ["node"]


def run(cmd, label):
    try:
        p = subprocess.run(cmd, cwd=T.ROOT, capture_output=True, timeout=180)
    except Exception as e:
        return (label, 1, str(e))
    out = (p.stdout + p.stderr).decode("utf-8", "replace").strip()
    return (label, p.returncode, out)


def main():
    jobs = []
    jobs.append((PY + ["build/validate_data.py"], "lessons.json"))
    jobs.append((PY + ["build/validate_xlsx.py"], "진도표 XLSX"))

    for n in range(1, 13):
        lid = "L%02d" % n
        jobs.append((PY + ["build/validate_hwpx.py", "out/지도안/WISE_%s_지도안.hwpx" % lid],
                     "%s 지도안" % lid))
        jobs.append((PY + ["build/validate_hwpx.py", "out/활동지/WISE_%s_활동지.hwpx" % lid],
                     "%s 활동지" % lid))
        jobs.append((PY + ["build/validate_pptx.py", "out/ppt/WISE_%s_수업.pptx" % lid],
                     "%s PPT" % lid))
        jobs.append((PY + ["build/validate_webapp_spec.py", "out/webapp/%s" % lid],
                     "%s 웹앱 문서" % lid))
        jobs.append((NODE + ["build/smoke_webapp.js", "out/webapp/%s" % lid],
                     "%s 웹앱 구조" % lid))
        jobs.append((NODE + ["build/run_webapp.js", "out/webapp/%s" % lid],
                     "%s 웹앱 실행" % lid))

    jobs.append((NODE + ["build/run_webapp.js", "out/webapp/common"], "공통 설문 웹앱"))
    jobs.append((PY + ["build/check_core_same.py"], "웹앱 공통 골격 동일성"))
    jobs.append((PY + ["build/check_rules.py"], "Firebase 보안 규칙"))
    jobs.append((PY + ["build/validate_hwpx.py", "out/해설서/WISE_교사용_해설서.hwpx"], "교사용 해설서"))
    for name in ["WISE_정보_분류_카드", "WISE_AI_활용_장면_카드", "WISE_상황_카드"]:
        jobs.append((PY + ["build/validate_hwpx.py", "out/교구/%s.hwpx" % name], name))
    jobs.append((NODE + ["build/check_site.js", "out/site"], "통합 웹사이트"))
    jobs.append((PY + ["build/audit.py"], "전체 점검"))

    failed = []
    for cmd, label in jobs:
        label, code, out = run(cmd, label)
        if code == 0:
            print("OK    %s" % label)
        else:
            failed.append((label, out))
            print("NG    %s" % label)

    print("")
    print("=" * 56)
    if failed:
        for label, out in failed:
            print("")
            print("[%s]" % label)
            print(out[:900])
        print("")
        print("NG  %d / %d 실패" % (len(failed), len(jobs)))
        return 1

    print("OK  %d개 검사 전부 통과" % len(jobs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
