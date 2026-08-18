# -*- coding: utf-8 -*-
"""검증하고, 올리고, 실제로 열리는지 확인하고, 드라이브까지 맞춘다.

산출물을 고쳤으면 여기까지가 한 작업이다. 만들어만 두면 선생님이 못 본다.

사용법
  py -3 build/publish.py "커밋 메시지"
  py -3 build/publish.py --check     지금 올라간 것이 최신인지만 본다
"""
import io
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

import tasks as T

T.setup_console()

REPO = "legoschool/ai-for-good"
SITE = "https://legoschool.github.io/ai-for-good"
GH = r"C:\Program Files\GitHub CLI\gh.exe"
DRIVE = (r"G:\내 드라이브\02_사업\00_지딜\지딜 엔드 티처스랩"
         r"\2026. 티처스랩\★2026. 티처스랩 자료 개발\8. WISE 산출물")

PAGES = [
    "/out/site/index.html",
    "/out/site/skills.html",
    "/out/site/apps.html",
    "/out/site/survey.html",
    "/out/site/about.html",
    "/out/site/module/M1.html",
    "/out/site/lesson/L01.html",
    "/out/site/lesson/L12.html",
    "/out/site/webapp/L01/index.html",
    "/out/site/webapp/common/index.html",
    "/out/site/assets/style.css",
]


def run(cmd, quiet=False):
    p = subprocess.run(cmd, cwd=T.ROOT, capture_output=True)
    out = (p.stdout + p.stderr).decode("utf-8", "replace")
    if not quiet and out.strip():
        print(out.strip()[:900])
    return p.returncode, out


def gh(args):
    return run([GH] + args, quiet=True)


def fetch(url, timeout=25):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def head_sha():
    _, out = run(["git", "rev-parse", "--short", "HEAD"], quiet=True)
    return out.strip()


def wait_pages(target, tries=14):
    for i in range(1, tries + 1):
        code, out = gh(["api", "repos/%s/pages/builds/latest" % REPO,
                        "--jq", ".commit[0:7] + \" \" + .status"])
        parts = out.strip().split()
        sha = parts[0] if parts else "?"
        status = parts[1] if len(parts) > 1 else "?"
        print("  [%2d] 빌드 %s  %s" % (i, sha, status))
        if sha == target and status == "built":
            return True
        if status == "errored":
            print("  빌드가 실패했다.")
            return False
        time.sleep(20)
    return False


def check_live():
    bad = []
    for p in PAGES:
        code, _ = fetch(SITE + p)
        mark = "OK " if code == 200 else "NG "
        print("  %s %s" % (mark, p))
        if code != 200:
            bad.append(p)
    return bad


def sync_drive():
    if not os.path.isdir(DRIVE):
        print("  드라이브 폴더가 없다. 건너뛴다.")
        return
    import shutil
    n = 0
    for root, dirs, files in os.walk(os.path.join(T.ROOT, "out")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__",)]
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, os.path.join(T.ROOT, "out"))
            dst = os.path.join(DRIVE, "out", rel)
            d = os.path.dirname(dst)
            if not os.path.isdir(d):
                os.makedirs(d)
            try:
                if (not os.path.exists(dst)
                        or os.path.getmtime(src) > os.path.getmtime(dst) + 1):
                    shutil.copy2(src, dst)
                    n += 1
            except Exception:
                pass
    print("  드라이브에 %d개 갱신" % n)


def main():
    args = sys.argv[1:]
    only_check = args and args[0] == "--check"

    if not only_check:
        if not args:
            print("커밋 메시지를 적어 주세요.")
            print('  py -3 build/publish.py "3차시를 40분 수업으로"')
            return 1

        print("1. 전체 검증")
        code, out = run([sys.executable, "build/verify_all.py"], quiet=True)
        tail = [l for l in out.strip().split("\n") if l.strip()][-1:]
        print("  %s" % (tail[0] if tail else ""))
        if code != 0:
            print("")
            print("검증이 실패했다. 고치기 전에는 올리지 않는다.")
            for line in out.strip().split("\n"):
                if line.startswith("NG"):
                    print("  %s" % line)
            return 1

        print("2. 커밋과 올리기")
        run(["git", "add", "-A"], quiet=True)
        code, out = run(["git", "-c", "core.quotepath=false", "commit", "-q", "-m", args[0]], quiet=True)
        if "nothing to commit" in out:
            print("  바뀐 것이 없다.")
        code, _ = run(["git", "push", "-q", "origin", "main"], quiet=True)
        if code != 0:
            print("  올리지 못했다.")
            return 1
        print("  %s" % head_sha())

        print("3. 사이트가 다시 만들어지기를 기다린다")
        if not wait_pages(head_sha()):
            print("  아직이다. 잠시 뒤 --check 로 다시 확인해 주세요.")

    print("4. 실제로 열리는지 확인")
    bad = check_live()

    if not only_check:
        print("5. 드라이브 사본 맞추기")
        sync_drive()

    print("")
    print("=" * 56)
    if bad:
        print("NG  열리지 않는 쪽 %d개" % len(bad))
        return 1
    print("OK  %s" % SITE)
    print("    선생님이 바로 열어 보실 수 있습니다.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
