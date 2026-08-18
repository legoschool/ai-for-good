# -*- coding: utf-8 -*-
"""13개 웹앱의 공통 골격이 정말 같은지 검사한다.

활동 화면만 다르고 입장·방·저장·교사 화면은 글자 하나까지 같아야 한다.
"""
import hashlib
import io
import os
import re
import sys

import tasks as T

T.setup_console()

ACT_START = "/* ---------- 활동 (차시별) ---------- */"
ACT_END = "/* ---------- 학생 흐름 ---------- */"


def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()


def core_of(html, slug, app_name, subtitle, accent, soft):
    """차시마다 다를 수밖에 없는 것을 지운 나머지가 공통 골격이다."""
    s = html.find(ACT_START)
    e = html.find(ACT_END)
    if s < 0 or e < 0:
        return None
    core = html[:s] + html[e:]
    # 긴 것부터 바꾼다. 앱 이름이 학습 주제의 앞부분과 겹치는 차시가 있다. (7차시)
    pairs = [(subtitle, "<SUBTITLE>"), (app_name, "<APP>"), (slug, "<SLUG>"),
             (accent, "<ACCENT>"), (soft, "<SOFT>")]
    for value, token in sorted(pairs, key=lambda x: -len(x[0] or "")):
        if value:
            core = core.replace(value, token)
    return core


def main():
    data = T.load_lessons()
    soft = {"#2563eb": "#eff6ff", "#d97706": "#fffbeb", "#059669": "#ecfdf5"}

    targets = []
    for l in data["lessons"]:
        m = data["modules"][l["module"] - 1]
        targets.append((l["id"], l["webapp"]["slug"], l["webapp"]["name"],
                        "%d차시 · %s" % (l["no"], l["shortTitle"]),
                        m["color"], soft[m["color"]]))
    targets.append(("common", "survey", "AI적정활용 자기인식 설문",
                    "공통 · 1차시 전과 12차시 뒤에 같은 8문항", "#1d4ed8", "#eff6ff"))

    hashes = {}
    for lid, slug, name, line, accent, softc in targets:
        p = os.path.join(T.ROOT, "out", "webapp", lid, "index.html")
        core = core_of(read(p), slug, name, line, accent, softc)
        if core is None:
            print("실패  %s : 활동 구역 표시를 찾지 못했다" % lid)
            return 1
        hashes.setdefault(hashlib.sha256(core.encode("utf-8")).hexdigest(), []).append(lid)

    print("== 공통 골격 동일성 ==")
    if len(hashes) == 1:
        print("OK  13개 앱의 공통 골격이 완전히 같다 (해시 1종)")
    else:
        print("NG  골격이 %d종으로 갈렸다" % len(hashes))
        for h, ids in hashes.items():
            print("   %s : %s" % (h[:12], ", ".join(ids)))
        return 1

    # 방 코드 규칙 확인
    print("")
    print("== 방 코드 규칙 ==")
    sample = read(os.path.join(T.ROOT, "out", "webapp", "L01", "index.html"))
    checks = [
        ("6자리 생성", "for (var i = 0; i < 6; i++) { s += String(Math.floor(Math.random() * 10)); }"),
        ("숫자만 걸러내기", 'if (s.charAt(i) >= "0" && s.charAt(i) <= "9")'),
        ("방 코드 6자리 제한", 'onlyDigits($("w-room").value, 6)'),
        ("비밀번호 4자리 제한", 'onlyDigits($("w-pw").value, 4)'),
        ("6자리 아니면 입장 거부", 'room.length !== 6'),
        ("입력칸 maxlength 6", 'id="w-room" inputmode="numeric" maxlength="6"'),
        ("입력칸 maxlength 4", 'id="w-pw" inputmode="numeric" maxlength="4"'),
    ]
    ok = True
    for label, needle in checks:
        hit = needle in sample
        print("  %s  %s" % ("OK " if hit else "NG ", label))
        ok = ok and hit

    # 모든 앱에 같은 입장 흐름이 있는가
    print("")
    print("== 앱마다 입장·방·교사 흐름 ==")
    flow = ["w-room", "w-pw", "w-nick", "w-group", "w-enter", "w-solo", "w-teacher",
            "t-make", "t-open", "t-code", "t-copy", "t-csv", "t-lock", "t-refresh",
            "makeCode", "teacherMake", "teacherOpen", "fallbackCopy"]
    for lid, slug, _, _, _, _ in targets:
        html = read(os.path.join(T.ROOT, "out", "webapp", lid, "index.html"))
        missing = [f for f in flow if f not in html]
        mark = "OK " if not missing else "NG "
        print("  %s %-7s slug=%-19s 요소 %d/%d"
              % (mark, lid, slug, len(flow) - len(missing), len(flow)))
        if missing:
            print("       빠짐 : %s" % missing)
            ok = False

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
