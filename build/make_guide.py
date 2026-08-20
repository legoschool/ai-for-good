# -*- coding: utf-8 -*-
"""차시별 웹앱 사용 안내 페이지를 만든다.

교사가 이 한 쪽만 보면 수업을 굴릴 수 있게 한다.

  무엇을 하는 앱인가 · 무엇을 배우는가 · 체험하는 법 세 걸음
  · 화면 캡처 갤러리 · 수업 흐름과 발문 · 관련 영상과 기사 · 내려받기

캡처는 `node build/make_shots.js` 가 먼저 만들어 둔 것을 쓴다.
사용법 : py -3 build/make_guide.py
"""
import io
import json
import os
import sys

import tasks as T
from site_nav import top_bar, foot_bar

T.setup_console()

SHOTS = os.path.join("assets", "shots")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shots_index(site):
    path = os.path.join(site, "assets", "shots", "index.json")
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


PAGE = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · 웹앱 사용 안내</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
%(top)s

<main class="wrap">
<article class="page">

<p class="crumb">%(module)s · %(no)d차시</p>
<h1>%(title)s</h1>
<p class="lead">%(purpose)s</p>

<section class="card">
  <h2>이 앱으로 무엇을 하나</h2>
  <p>%(problem)s</p>
  <div class="pillrow">%(skills)s</div>
</section>

<section class="card">
  <h2>배우는 것</h2>
  <ul>%(learn)s</ul>
</section>

<section class="card">
  <h2>체험하는 법 (세 걸음)</h2>
  <ol class="steps3">
    <li><b>혼자 먼저 해 본다.</b> 앱을 열고 닉네임만 넣은 뒤 <b>둘러보기</b>를 누른다.
      저장되지 않으니 마음껏 눌러 본다.
      <a class="btn" href="../webapp/%(lid)s/index.html" target="_blank" rel="noopener">웹앱 열기</a></li>
    <li><b>수업 직전에 방을 만든다.</b> 앱에서 <b>선생님 화면</b>을 누르고 비밀번호 네 자리를 정한 뒤
      <b>새 방 만들기</b>를 누른다. 여섯 자리 방 번호가 나온다. 칠판에 적는다.</li>
    <li><b>학생이 들어온다.</b> 같은 주소를 열어 방 번호와 닉네임, 나만 아는 숫자 네 자리를 넣는다.
      제출하면 선생님 화면에 바로 모인다.</li>
  </ol>
  <p class="muted">기기가 모자라면 모둠에 한 대로 함께 하고, 없으면 %(alt)s</p>
</section>

<section class="card">
  <h2>화면 미리 보기</h2>
  <p class="muted">실제 앱 화면입니다. 눌러서 크게 볼 수 있습니다.</p>
  <div class="shots">%(shots)s</div>
</section>

<section class="card">
  <h2>수업 흐름과 발문</h2>
  %(flow)s
</section>

<section class="card">
  <h2>함께 보면 좋은 자료</h2>
  %(refs)s
  <div class="embed-slot">
    <p class="muted"><b>영상이나 카드뉴스를 화면 안에 넣으려면</b>
      <code>data/lessons.json</code> 의 <code>references</code> 항목에
      <code>"embed": "https://www.youtube.com/embed/영상아이디"</code> 처럼 적고 다시 만듭니다.
      캔바는 보기 주소 끝에 <code>?embed</code> 를 붙입니다.
      임베드를 넣어도 여는 링크는 그대로 둡니다. 학교망에서 막히는 곳이 있습니다.</p>
  </div>
</section>

<section class="card">
  <h2>내려받기</h2>
  <div class="dl">
    <a href="../files/WISE_%(lid)s_지도안.hwpx">지도안 한글</a>
    <a href="../files/WISE_%(lid)s_활동지.hwpx">활동지 한글</a>
    <a href="../files/WISE_%(lid)s_수업.pptx">수업 PPT</a>
    <a href="../print/%(lid)s_지도안.html">지도안 인쇄용</a>
    <a href="../print/%(lid)s_활동지.html">활동지 인쇄용</a>
    <a href="../deck/%(lid)s.html">수업 슬라이드</a>
  </div>
</section>

<p class="navrow">
  <a href="../guide/index.html">← 사용 안내 목록</a>
  <a href="../lesson/%(lid)s.html">%(no)d차시 자세히 보기 →</a>
</p>

</article>
</main>
%(foot)s
</body>
</html>
"""

INDEX = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>웹앱 사용 안내</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
%(top)s
<main class="wrap">
<article class="page">
<h1>웹앱 사용 안내</h1>
<p class="lead">차시마다 앱을 어떻게 쓰는지, 학생이 무엇을 배우는지,
화면이 어떻게 생겼는지를 한 쪽에 모았습니다.</p>

<section class="card">
  <h2>처음 여는 선생님께</h2>
  <ol class="steps3">
    <li>먼저 <b>둘러보기</b>로 혼자 끝까지 해 봅니다. 저장되지 않습니다.</li>
    <li>수업 직전에 <b>선생님 화면 → 새 방 만들기</b>로 방 번호를 만듭니다.</li>
    <li>학생에게 <b>주소와 방 번호</b>만 알려 줍니다. 이름은 묻지 않습니다.</li>
  </ol>
</section>

<div class="grid3">%(cards)s</div>

</article>
</main>
%(foot)s
</body>
</html>
"""


def skills_of(lesson):
    out = []
    for s in lesson["humanSkills"]["focus"]:
        out.append('<span class="pill">%s</span>' % esc(s["name"]))
    for s in lesson["humanSkills"].get("support", []):
        out.append('<span class="pill ghost">%s</span>' % esc(s))
    return "".join(out)


def learn_of(lesson):
    out = []
    for s in lesson["humanSkills"]["focus"]:
        out.append("<li><b>%s</b> · %s</li>" % (esc(s["name"]), esc(s["process"])))
    for c in lesson.get("aiComponents", []):
        name = c if isinstance(c, str) else ("%s %s" % (c.get("mark", ""), c.get("name", "")))
        out.append("<li>AI적정활용 구성요소 · %s</li>" % esc(name))
    return "".join(out)


def flow_of(lesson):
    rows = []
    for key, label in [("intro", "도입"), ("develop", "전개"), ("close", "정리")]:
        part = lesson["plan"][key]
        for block in part["blocks"]:
            qs = []
            for turn in block["turns"]:
                if turn.get("q"):
                    qs.append("<li>%s</li>" % esc(turn["q"]))
            rows.append(
                '<div class="flowrow"><div class="flowhead">%s · %s분<br><b>%s</b></div>'
                '<ul class="flowq">%s</ul></div>'
                % (label, part["minutes"], esc(block["heading"]), "".join(qs)))
    return "".join(rows)


def refs_of(lesson, data):
    """그 차시 자료를 먼저 보여 주고 공통 자료를 뒤에 붙인다.
    embed 주소가 있으면 화면 안에 끼워 넣고, 여는 링크도 반드시 함께 둔다.
    학교망에서 임베드가 막혀도 링크로 열 수 있어야 하기 때문이다."""
    mine = [r for r in data.get("references", []) if r.get("lesson") == lesson["id"]]
    common = [r for r in data.get("references", []) if not r.get("lesson")]

    items = []
    for r in mine + common:
        title = esc(r.get("title", "자료"))
        url = esc(r.get("url", ""))
        src = esc(r.get("source", ""))
        note = esc(r.get("note", ""))
        kind = esc(r.get("kind", "자료"))
        embed = esc(r.get("embed", ""))
        box = '<li class="refitem"><span class="tagk">%s</span> ' % kind
        if url:
            box += '<a href="%s" target="_blank" rel="noopener"><b>%s</b></a>' % (url, title)
        else:
            box += "<b>%s</b>" % title
        if src:
            box += ' <span class="muted">%s</span>' % src
        box += "<p>%s</p>" % note
        if embed:
            box += ('<div class="embed"><iframe loading="lazy" src="%s" '
                    'allowfullscreen allow="fullscreen" title="%s"></iframe></div>'
                    '<p class="muted">화면에 안 보이면 학교망이 막은 것입니다. 위 제목을 눌러 새 창으로 엽니다.</p>'
                    % (embed, title))
        items.append(box + "</li>")

    hint = esc(lesson.get("refHint", ""))
    if not items:
        return '<p class="muted">아직 채우지 않았습니다. 권장 자료 : %s</p>' % hint
    return '<ul class="reflist">%s</ul>' % "".join(items)


def shots_of(lid, index):
    rows = []
    for s in index.get(lid, []):
        rows.append(
            '<figure><a href="../%s/%s" target="_blank" rel="noopener">'
            '<img loading="lazy" src="../%s/%s" alt="%s 화면"></a>'
            '<figcaption>%s</figcaption></figure>'
            % (SHOTS.replace("\\", "/"), esc(s["file"]), SHOTS.replace("\\", "/"),
               esc(s["file"]), esc(s["name"]), esc(s["name"])))
    if not rows:
        return '<p class="muted">캡처가 아직 없습니다. <code>node build/make_shots.js</code> 를 돌립니다.</p>'
    return "".join(rows)


def build(data, site):
    index = shots_index(site)
    out_dir = os.path.join(site, "guide")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    cards = []
    made = []
    for lesson in data["lessons"]:
        lid = lesson["id"]
        mod = data["modules"][lesson["module"] - 1]
        html = PAGE % {
            "title": esc(lesson["webapp"]["name"]),
            "lid": lid,
            "no": lesson["no"],
            "module": esc(mod["name"]),
            "purpose": esc(lesson["webapp"]["purpose"]),
            "problem": esc(lesson["problem"]),
            "skills": skills_of(lesson),
            "learn": learn_of(lesson),
            "alt": esc(lesson.get("alternative", "인쇄 자료로 대신합니다.")),
            "shots": shots_of(lid, index),
            "flow": flow_of(lesson),
            "refs": refs_of(lesson, data),
            "top": top_bar("../", "guide/index.html"),
            "foot": foot_bar(esc(data["program"]["copyrightLine"])),
        }
        path = os.path.join(out_dir, "%s.html" % lid)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        made.append(path)

        first = index.get(lid, [{}])[0].get("file", "")
        thumb = ('<img loading="lazy" src="../%s/%s" alt="">' % (SHOTS.replace("\\", "/"), esc(first))) if first else ""
        cards.append(
            '<a class="gcard" href="%s.html">%s'
            '<span class="gno">%d차시</span><b>%s</b>'
            '<small>%s</small></a>'
            % (lid, thumb, lesson["no"], esc(lesson["webapp"]["name"]),
               esc(lesson["shortTitle"])))

    idx = INDEX % {"cards": "".join(cards),
                   "top": top_bar("../", "guide/index.html"),
                   "foot": foot_bar(esc(data["program"]["copyrightLine"]))}
    ipath = os.path.join(out_dir, "index.html")
    with io.open(ipath, "w", encoding="utf-8", newline="\n") as f:
        f.write(idx)
    made.append(ipath)
    return made


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    made = build(data, site)
    print("웹앱 사용 안내를 만들었다 : %d쪽" % len(made))
    print("  %s" % os.path.relpath(made[-1], T.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
