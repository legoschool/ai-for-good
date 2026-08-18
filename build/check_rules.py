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
    root_flags = [k for k in rules if k.startswith(".")]
    print("루트 .read/.write 선언 : %s" % (root_flags or "없음 (기존 규칙을 덮어쓰지 않는다)"))
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
    bad = [s for s in slugs if not pat.match(s)]
    print("")
    print("앱 slug %d개 규칙 통과 : %s" % (len(slugs), "전부" if not bad else "실패 %s" % bad))

    needed = ["meta", "state", "entries", "votes"]
    missing = [n for n in needed if n not in room]
    print("앱이 쓰는 경로 %s : %s" % (needed, "전부 있음" if not missing else "빠짐 %s" % missing))
    return 1 if (bad or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
