# -*- coding: utf-8 -*-
"""웹앱 SPEC.md · PROMPT.md 검증."""
import io
import os
import sys

import tasks as T

T.setup_console()

ERRORS = []


def err(m):
    ERRORS.append(m)


def read(p):
    if not os.path.exists(p):
        return None
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/validate_webapp_spec.py <out/webapp/L06>")
        return 1

    target = sys.argv[1]
    d = target if os.path.isabs(target) else os.path.join(T.ROOT, target)
    lid = os.path.basename(d.rstrip("\\/"))

    data = T.load_lessons()
    match = [l for l in data["lessons"] if l["id"] == lid]
    if not match:
        print("실패  차시 폴더 이름이 이상하다 : %s" % lid)
        return 1
    lesson = match[0]
    w = lesson["webapp"]

    spec = read(os.path.join(d, "SPEC.md"))
    prompt = read(os.path.join(d, "PROMPT.md"))

    if spec is None:
        err("SPEC.md 가 없다")
    if prompt is None:
        err("PROMPT.md 가 없다")

    if spec:
        for need, label in [
            (w["name"], "앱 이름"),
            (w["slug"], "slug"),
            (lesson["problem"], "학습 문제"),
            (w["purpose"], "앱 목적"),
            ("혼자 체험", "혼자 체험 경로"),
            ("방 코드", "방 코드 입장"),
            ("Firebase", "저장 방식"),
            ("Google Sheets", "백업 방식"),
            (lesson["alternative"], "기기가 없을 때 대안"),
            ("CC BY-NC-SA", "저작권 표기"),
        ]:
            if need not in spec:
                err("SPEC.md 에 %s 가 없다" % label)
        for s in w["screens"]:
            if s not in spec:
                err("SPEC.md 에 화면이 빠졌다 : %s" % s)
        for c in lesson["cautions"]:
            if c not in spec:
                err("SPEC.md 에 지도 유의점이 빠졌다 : %s" % c[:24])

    if prompt:
        if "```" not in prompt:
            err("PROMPT.md 에 복사해 붙일 코드 블록이 없다")
        for need, label in [
            (w["name"], "앱 이름"),
            (w["slug"], "slug"),
            ("외부 라이브러리", "CDN 금지 지시"),
            ("복사 버튼", "방 코드 복사 버튼 지시"),
            ("혼자 체험", "혼자 체험 경로 지시"),
            ("닉네임 중복을 막지 마라", "닉네임 중복 허용 지시"),
            ("방이 사라지면 안 된다", "방 유지 지시"),
            ("역슬래시 이스케이프", "Apps Script 함정 지시"),
            ("no-cors", "Sheets 백업 지시"),
            ("44px", "터치 대상 크기 지시"),
            ("em dash", "표기 규칙"),
        ]:
            if need not in prompt:
                err("PROMPT.md 에 %s 가 없다" % label)
        if lesson["no"] == 10 and "믿을 수 있는 어른" not in prompt:
            err("PROMPT.md 에 10차시 안전 문구 지시가 없다")

    for text, name in [(spec, "SPEC.md"), (prompt, "PROMPT.md")]:
        if text and "—" in text:
            err("%s 에 em dash(—) 가 있다" % name)

    if ERRORS:
        for e in ERRORS:
            print("실패  %s" % e)
        print("")
        print("NG  오류 %d건" % len(ERRORS))
        return 1

    print("OK  %s  SPEC.md · PROMPT.md" % lid)
    print("    앱 %s, 화면 %d개, 유의점 %d건, 프롬프트 지시 11종 확인"
          % (w["name"], len(w["screens"]), len(lesson["cautions"])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
