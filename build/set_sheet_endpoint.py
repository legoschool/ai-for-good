# -*- coding: utf-8 -*-
"""Apps Script 웹 앱 배포 주소를 넣고 13개 앱과 사이트를 다시 만든다.

사용법
  py -3 build/set_sheet_endpoint.py https://script.google.com/macros/s/AKfy.../exec
  py -3 build/set_sheet_endpoint.py --show     지금 무엇이 들어 있는지 본다
  py -3 build/set_sheet_endpoint.py --test     주소가 살아 있는지 두드려 본다
  py -3 build/set_sheet_endpoint.py --clear    주소를 지우고 자리표시자로 되돌린다
"""
import io
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

import tasks as T

T.setup_console()

FILE = os.path.join(T.ROOT, "data", "sheet_endpoint.txt")
PATTERN = re.compile(r"^https://script[.]google[.]com/macros/s/[A-Za-z0-9_-]+/exec$")


def current():
    if not os.path.exists(FILE):
        return None
    with io.open(FILE, encoding="utf-8") as f:
        url = f.read().strip()
    return url or None


def ping(url):
    """GET 으로 살아 있는지 본다. doGet 이 안내 문구를 돌려준다."""
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode("utf-8", "replace")[:160]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:160]
    except Exception as e:
        return 0, str(e)[:160]


def post_sample(url):
    """진짜 기록 한 건을 보내 본다. 시트에 시험 행이 하나 생긴다."""
    body = {"rows": [{
        "nick": "연결시험", "group": "점검", "app": "signal-judges",
        "room": "999002", "at": int(__import__("time").time() * 1000),
        "payload": {"note": "엔드포인트 연결 확인"},
    }]}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "text/plain;charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")[:200]
    except Exception as e:
        return 0, str(e)[:200]


def rebuild():
    steps = [
        ([sys.executable, "build/make_webapp.py", "all"], "웹앱 13개"),
        ([sys.executable, "build/make_site.py"], "웹사이트"),
    ]
    for cmd, label in steps:
        p = subprocess.run(cmd, cwd=T.ROOT, capture_output=True)
        if p.returncode != 0:
            print("실패  %s 를 다시 만들지 못했다" % label)
            print((p.stdout + p.stderr).decode("utf-8", "replace")[:600])
            return False
        print("  다시 만들었다 : %s" % label)
    return True


def count_in_apps(url):
    n = 0
    root = os.path.join(T.ROOT, "out", "webapp")
    for d in sorted(os.listdir(root)):
        p = os.path.join(root, d, "index.html")
        if os.path.exists(p):
            with io.open(p, encoding="utf-8") as f:
                if url in f.read():
                    n += 1
    return n


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    arg = sys.argv[1]

    if arg == "--show":
        url = current()
        print("현재 주소 : %s" % (url or "없음 (시트 백업이 꺼져 있다)"))
        if url:
            print("들어간 앱 : %d개" % count_in_apps(url))
        return 0

    if arg == "--clear":
        if os.path.exists(FILE):
            os.remove(FILE)
        print("주소를 지웠다. 다시 만든다.")
        return 0 if rebuild() else 1

    if arg == "--test":
        url = current()
        if not url:
            print("실패  주소가 아직 없다")
            return 1
        code, text = ping(url)
        print("GET  %s  %s" % (code, text))
        return 0 if code == 200 else 1

    url = arg.strip()

    if not PATTERN.match(url):
        print("실패  주소 형태가 다르다.")
        print("      https://script.google.com/macros/s/<배포ID>/exec  꼴이어야 한다.")
        print("      받은 것 : %s" % url[:120])
        if "/dev" in url:
            print("")
            print("      /dev 로 끝나는 것은 개발용 주소다. 학생 브라우저에서는 열리지 않는다.")
            print("      [배포] → [새 배포] 로 만든 /exec 주소를 써야 한다.")
        return 1

    print("1. 주소가 살아 있는지 확인한다")
    code, text = ping(url)
    if code != 200:
        print("   실패  응답 %s : %s" % (code, text))
        print("")
        print("   배포할 때 [액세스 권한이 있는 사용자] 를 [모든 사용자] 로 두었는지 확인해 주세요.")
        return 1
    print("   OK  %s" % text.strip()[:90])

    print("2. 시험 기록을 한 건 보내 본다")
    code, text = post_sample(url)
    if code == 200:
        print("   OK  %s" % text.strip()[:120])
    else:
        print("   주의  응답 %s : %s" % (code, text))
        print("        저장은 됐을 수 있다. 시트를 직접 확인해 주세요.")

    print("3. 주소를 적어 둔다")
    d = os.path.dirname(FILE)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(url + "\n")
    print("   %s" % os.path.relpath(FILE, T.ROOT))

    print("4. 앱과 사이트를 다시 만든다")
    if not rebuild():
        return 1

    n = count_in_apps(url)
    print("")
    print("=" * 56)
    if n == 13:
        print("OK  13개 앱 전부에 주소가 들어갔다.")
        print("    이제 학생이 제출하면 Firebase 와 시트에 함께 쌓인다.")
        print("")
        print("    시트에서 signal-judges 탭의 999002 행을 지워 주세요. 연결 시험 기록이다.")
        print("")
        print("    다음 : py -3 build/verify_all.py")
        return 0
    print("NG  주소가 들어간 앱이 %d개다. 13개여야 한다." % n)
    return 1


if __name__ == "__main__":
    sys.exit(main())
