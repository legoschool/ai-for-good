# -*- coding: utf-8 -*-
"""실제 Firebase 에 요청을 보내 보안 규칙이 살아 있는지 확인한다.

읽기 전용 확인과, 정상 경로 한 곳에 시험 기록을 넣었다가 지우는 것까지 한다.
"""
import json
import sys
import urllib.error
import urllib.request

import tasks as T
T.setup_console()

DB = "https://remind-c2610-default-rtdb.firebaseio.com"
ROOM = "999001"          # 시험용 방 코드
APP = "signal-judges"


def call(method, path, body=None):
    url = "%s%s.json" % (DB, path)
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8")[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")[:200]
    except Exception as e:
        return 0, str(e)


def show(label, method, path, body, expect_ok):
    code, text = call(method, path, body)
    allowed = code in (200,)
    good = allowed == expect_ok
    mark = "OK " if good else "NG "
    want = "허용되어야" if expect_ok else "막혀야"
    print("  %s %-46s %s %s(%s)" % (mark, method + " " + path, want, "함", code))
    if not good:
        print("       응답 : %s" % text.replace("\n", " ")[:120])
    return good, text


print("=" * 66)
print(" 막혀야 하는 것")
print("=" * 66)
ok = True
for path in ["", "/wise", "/wise/%s" % APP]:
    g, _ = show("읽기", "GET", path or "/", None, False)
    ok = ok and g

g, _ = show("쓰기", "PUT", "/침입시도", "hello", False)
ok = ok and g
g, _ = show("읽기", "GET", "/wise/%s/12345" % APP, None, False)   # 5자리
ok = ok and g

print()
print("=" * 66)
print(" 허용되어야 하는 것")
print("=" * 66)
g, body = show("읽기", "GET", "/wise/%s/%s" % (APP, ROOM), None, True)
ok = ok and g

entry = {"nick": "규칙시험", "group": "점검", "app": APP, "room": ROOM,
         "at": 1786000000000, "payload": {"note": "자동 점검"}}
code, text = call("POST", "/wise/%s/%s/entries" % (APP, ROOM), entry)
made = code == 200
print("  %s POST 정상 기록 넣기                             허용되어야 함(%s)" % ("OK " if made else "NG ", code))
key = None
if made:
    try:
        key = json.loads(text)["name"]
    except Exception:
        pass
ok = ok and made

print()
print("=" * 66)
print(" 규칙이 걸러내야 하는 잘못된 기록")
print("=" * 66)
bad_entry = dict(entry)
bad_entry["room"] = "111111"          # 경로와 다른 방 번호
g, _ = show("쓰기", "POST", "/wise/%s/%s/entries" % (APP, ROOM), bad_entry, False)
ok = ok and g

long_nick = dict(entry)
long_nick["nick"] = "가" * 30          # 12자 초과
g, _ = show("쓰기", "POST", "/wise/%s/%s/entries" % (APP, ROOM), long_nick, False)
ok = ok and g

future = dict(entry)
future["at"] = 99999999999999         # 먼 미래
g, _ = show("쓰기", "POST", "/wise/%s/%s/entries" % (APP, ROOM), future, False)
ok = ok and g

if key:
    code, _ = call("DELETE", "/wise/%s/%s/entries/%s" % (APP, ROOM, key))
    blocked = code != 200
    print("  %s DELETE 남의 기록 지우기                          막혀야 함(%s)"
          % ("OK " if blocked else "NG ", code))
    ok = ok and blocked

print()
print("=" * 66)
if ok:
    print(" OK  보안 규칙이 살아서 의도대로 동작한다")
    if key:
        print(" 참고  시험 기록 1건이 /wise/%s/%s 에 남아 있다." % (APP, ROOM))
        print("       규칙상 삭제가 막혀 있어 콘솔에서 지워야 한다. 방 코드 %s 다." % ROOM)
    sys.exit(0)
print(" NG  규칙이 아직 반영되지 않았거나 다르게 적용됐다")
sys.exit(1)
