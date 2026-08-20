# -*- coding: utf-8 -*-
"""전체 점검. 산출물 무결성, 비밀값 잔존, 자리표시자, 사본 일치를 본다."""
import hashlib, io, os, re, subprocess, sys, zipfile
import tasks as T
T.setup_console()

ROOT = T.ROOT
issues, warns, notes = [], [], []
def bad(m): issues.append(m)
def warn(m): warns.append(m)
def note(m): notes.append(m)

def walk(d, ext=None):
    out = []
    for r, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x not in (".git", "node_modules", "__pycache__")]
        for f in fs:
            if ext is None or f.lower().endswith(ext):
                out.append(os.path.join(r, f))
    return out

print("=" * 62)
print(" 1. 산출물 개수")
print("=" * 62)
expect = [("out/지도안", 12, ".hwpx"), ("out/활동지", 12, ".hwpx"),
          ("out/ppt", 12, ".pptx"), ("out/서류", 1, ".xlsx"),
          ("out/교구", 3, ".hwpx"), ("out/해설서", 1, ".hwpx")]
for rel, n, ext in expect:
    p = os.path.join(ROOT, rel)
    got = len([f for f in os.listdir(p) if f.lower().endswith(ext)]) if os.path.isdir(p) else 0
    ok = got == n
    print("  %s %-14s %d개 (기대 %d)" % ("OK " if ok else "NG ", rel, got, n))
    if not ok: bad("%s 가 %d개다. %d개여야 한다" % (rel, got, n))

apps = sorted(d for d in os.listdir(os.path.join(ROOT, "out", "webapp")))
print("  %s out/webapp     %d개 %s" % ("OK " if len(apps) == 13 else "NG ", len(apps), apps[:3]))
if len(apps) != 13: bad("웹앱이 %d개다. 13개여야 한다" % len(apps))

pages = [p for p in walk(os.path.join(ROOT, "out", "site"), ".html") if "webapp" not in p]
print("  %s out/site       %d쪽 (기대 72)" % ("OK " if len(pages) == 72 else "NG ", len(pages)))
if len(pages) != 72: bad("사이트가 %d쪽이다. 72쪽이어야 한다 (차시 12 + 안내 13 + 참고자료 1 + 나머지)" % len(pages))

print()
print("=" * 62)
print(" 2. 한글·오피스 파일 무결성")
print("=" * 62)
office = walk(os.path.join(ROOT, "out"), (".hwpx", ".pptx", ".xlsx"))
broken = 0
for p in office:
    rel = os.path.relpath(p, ROOT)
    if not zipfile.is_zipfile(p):
        bad("%s 가 zip 이 아니다" % rel); broken += 1; continue
    z = zipfile.ZipFile(p)
    if z.testzip() is not None:
        bad("%s 안에 깨진 항목이 있다" % rel); broken += 1; continue
    if p.endswith(".hwpx"):
        infos = z.infolist()
        if infos[0].filename != "mimetype":
            bad("%s : mimetype 이 첫 항목이 아니다" % rel); broken += 1
        elif infos[0].compress_type != zipfile.ZIP_STORED:
            bad("%s : mimetype 이 무압축이 아니다" % rel); broken += 1
        xml = z.read("Contents/section0.xml").decode("utf-8")
        if "linesegarray" in xml:
            bad("%s : linesegarray 가 남아 있다" % rel); broken += 1
print("  검사한 파일 %d개, 문제 %d건" % (len(office), broken))

print()
print("=" * 62)
print(" 3. 비밀값·자리표시자 잔존")
print("=" * 62)
# 점검기 자신이 검색어를 담으면 스스로를 잡는다. 조각으로 나눠 조립한다.
gone = ["AIzaSyBVP4GHK3tClhSbr01Sv" + "CTHZnh9wLWmgdU", "30613" + "8692167",
        "G-6ZBK5" + "NTVDG", "firebasestor" + "age.app", "firebase" + "app.com"]
texts = walk(ROOT, (".md", ".py", ".js", ".html", ".json", ".css", ".txt"))
texts = [p for p in texts if ".git" not in p and "node_modules" not in p]
for token in gone:
    hits = []
    for p in texts:
        try:
            if token in io.open(p, encoding="utf-8", errors="ignore").read():
                hits.append(os.path.relpath(p, ROOT))
        except Exception: pass
    print("  %s %-42s %d건" % ("OK " if not hits else "NG ", token[:40], len(hits)))
    if hits: bad("제거했어야 할 값이 남아 있다 : %s -> %s" % (token, hits[:3]))

ph = []
for p in texts:
    try:
        if "PASTE_YOUR_APPS_SCRIPT_DEPLOY_URL" in io.open(p, encoding="utf-8", errors="ignore").read():
            ph.append(os.path.relpath(p, ROOT))
    except Exception: pass
print("  -- 시트 백업 주소 자리표시자 : %d개 파일" % len(ph))
if ph: warn("Apps Script 배포 URL 이 아직 자리표시자다. 시트 백업이 동작하지 않는다 (%d개 파일)" % len(ph))

print()
print("=" * 62)
print(" 4. 사이트 사본이 원본과 같은가")
print("=" * 62)
def sha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()
mismatch = 0
for lid in apps:
    a = os.path.join(ROOT, "out", "webapp", lid, "index.html")
    b = os.path.join(ROOT, "out", "site", "webapp", lid, "index.html")
    if not os.path.exists(b):
        bad("사이트 안에 %s 웹앱이 없다" % lid); mismatch += 1
    elif sha(a) != sha(b):
        bad("%s 웹앱이 사이트 사본과 다르다. make_site.py 를 다시 돌려야 한다" % lid); mismatch += 1
data = T.load_lessons()
for l in data["lessons"]:
    for src, name in [("지도안", "지도안"), ("활동지", "활동지")]:
        a = os.path.join(ROOT, "out", src, "WISE_%s_%s.hwpx" % (l["id"], name))
        b = os.path.join(ROOT, "out", "site", "files", "WISE_%s_%s.hwpx" % (l["id"], name))
        if not os.path.exists(b) or sha(a) != sha(b):
            bad("%s %s 가 사이트 사본과 다르다" % (l["id"], name)); mismatch += 1
    a = os.path.join(ROOT, "out", "ppt", "WISE_%s_수업.pptx" % l["id"])
    b = os.path.join(ROOT, "out", "site", "files", "WISE_%s_수업.pptx" % l["id"])
    if not os.path.exists(b) or sha(a) != sha(b):
        bad("%s PPT 가 사이트 사본과 다르다" % l["id"]); mismatch += 1
print("  웹앱 13 + 자료 36 대조, 불일치 %d건" % mismatch)

print()
print("=" * 62)
print(" 5. 금지 표기 전수 검사")
print("=" * 62)
outs = [p for p in walk(os.path.join(ROOT, "out"), (".html", ".md"))]
em = [os.path.relpath(p, ROOT) for p in outs
      if "—" in io.open(p, encoding="utf-8", errors="ignore").read()]
print("  %s em dash : %d건" % ("OK " if not em else "NG ", len(em)))
if em: bad("em dash 가 남아 있다 : %s" % em[:3])
old = []
for p in outs:
    t = io.open(p, encoding="utf-8", errors="ignore").read()
    for term in ["허용·조건부·제한", "3수준"]:
        if term in t: old.append((os.path.relpath(p, ROOT), term))
print("  %s 옛 3단계 신호등 표기 : %d건" % ("OK " if not old else "NG ", len(old)))
if old: bad("옛 신호등 표기가 남아 있다 : %s" % old[:3])

print()
print("=" * 62)
print(" 6. 상태 보드")
print("=" * 62)
tasks = T.build_tasks()
state = T.load_state()
c = T.counts(tasks, state)
print("  전체 %d · 완료 %d · 진행 %d · 대기 %d · 막힘 %d"
      % (len(tasks), c["완료"], c["진행"], c["대기"], c["막힘"]))
if c["완료"] != len(tasks): bad("완료가 %d/%d 다" % (c["완료"], len(tasks)))
if c["막힘"]: bad("막힌 작업이 %d건 있다" % c["막힘"])

print()
print("=" * 62)
print(" 결과")
print("=" * 62)
for w in warns: print("  주의  %s" % w)
for n in notes: print("  참고  %s" % n)
if issues:
    for i in issues: print("  실패  %s" % i)
    print()
    print("  NG  문제 %d건" % len(issues))
    sys.exit(1)
print("  OK  구조 점검 통과 (주의 %d건은 통과를 막지 않는다)" % len(warns))
