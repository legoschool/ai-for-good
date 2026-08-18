# -*- coding: utf-8 -*-
"""Firebase 보안 규칙 파일을 점검한다."""
import io
import json
import os
import sys

import tasks as T

T.setup_console()

PATH = os.path.join(T.ROOT, "spec", "firebase_rules.json")


def main():
    with io.open(PATH, encoding="utf-8") as f:
        d = json.load(f)
    print("JSON 문법 OK")

    rules = d["rules"]
    bad = []

    # 루트는 잠겨 있어야 한다. WISE 전용 프로젝트이므로 /wise 밖은 열 이유가 없다.
    if rules.get(".read") is not False:
        bad.append("루트 .read 가 false 가 아니다")
    if rules.get(".write") is not False:
        bad.append("루트 .write 가 false 가 아니다")
    print("루트 잠김 : %s" % ("예" if not bad else "아니오 -> %s" % bad))
    print("최상위 키 : %s" % list(rules.keys()))

    room = rules["wise"]["$app"]["$room"]
    writable = [k for k, v in room.items() if isinstance(v, dict) and ".write" in v]
    nested = [k for k, v in room.items()
              if isinstance(v, dict) and any(isinstance(x, dict) and ".write" in x
                                             for x in v.values())]
    print("방 하위 노드 : %s" % [k for k in room if not k.startswith(".")])
    print("직접 쓰기 가능 : %s" % writable)
    print("자식 단위 쓰기 가능 : %s" % nested)
    print("방 단위 읽기 규칙 : %s" % (".read" in room))

    # 실제 앱이 쓰는 경로가 규칙에 다 있는가
    data = T.load_lessons()
    slugs = [l["webapp"]["slug"] for l in data["lessons"]] + ["survey"]
    import re
    pat = re.compile(r"^[a-z][a-z0-9-]{1,23}$")
    badslug = [s for s in slugs if not pat.match(s)]
    print("")
    print("앱 slug %d개 규칙 통과 : %s" % (len(slugs), "전부" if not badslug else "실패 %s" % badslug))

    needed = ["meta", "state", "entries", "votes"]
    missing = [n for n in needed if n not in room]
    print("앱이 쓰는 경로 %s : %s" % (needed, "전부 있음" if not missing else "빠짐 %s" % missing))

    if bad:
        print("")
        for b in bad:
            print("실패  %s" % b)
    return 1 if (bad or badslug or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
