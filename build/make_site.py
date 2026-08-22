# -*- coding: utf-8 -*-
"""통합 웹사이트를 만든다. 빌드 도구 없이 열리는 순수 정적 HTML.

사용법 : py -3 build/make_site.py
"""
import io
import os
import shutil
import sys

import tasks as T
import make_admin
import make_guide
import make_qr
import make_refs
import make_view
import site_art as ART
from site_css import CSS, DEFS, DOODLES, RIBBON
from site_nav import NAV  # 머리띠 목록은 site_nav 한 곳에서만 고친다

T.setup_console()

SITE = os.path.join(T.ROOT, "out", "site")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))



SKILL_TINT = {
    "중점": ("#E6F7EC", "#0E9F57"),
    "보조": ("#EFEAFD", "#7B4FE8"),
}


def page(title, body, depth=0, current="", data=None):
    up = "../" * depth
    nav = "".join(
        '<a href="%s%s"%s>%s</a>' % (up, href, ' aria-current="page"' if href == current else "", label)
        for href, label in NAV)
    prog = data["program"]
    return u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s 초등 5·6학년 12차시 수업자료">
<link rel="stylesheet" href="%sassets/style.css">
</head>
<body>
%s
<header class="top"><div class="wrap">
  <a class="brand" href="%sindex.html">WISE <em>AI적정활용</em></a>
  <nav class="nav">%s</nav>
</div></header>
%s
<footer><div class="wrap">
  <details class="credit">
    <summary><strong>%s</strong><span class="more">만든 사람과 저작권 보기</span></summary>
    <div class="credit-body">
      <p>%s</p>
      <p>%s</p>
      <p>산출물 저작권은 연구회에 귀속되며 재단이 CC BY-NC-SA로 공개합니다. 수업 자료로 자유롭게 내려받아 고쳐 쓰실 수 있습니다.</p>
    </div>
  </details>
</div></footer>
</body>
</html>
""" % (esc(title), esc(prog["name"]), up, DEFS, up, nav, body,
       esc(prog["name"]), esc(" · ".join(prog["members"])), esc(prog["copyrightLine"]))


# ---------------------------------------------------------------- 조각

def keyvis(lesson, module):
    """영상 자리에 놓는 대표 화면. 자막처럼 학습 문제를 얹는다."""
    focus = lesson["humanSkills"]["focus"][0]["name"]
    know = lesson["humanSkills"]["focus"][0]["knowledge"]
    head, _, tail = know.rpartition(", ")
    if not head:
        head, tail = "", know
    return (u'<div class="keyvis" style="--kv:%s">%s'
            u'<span class="kv-tag">%s</span><span class="kv-mark">WISE %d차시</span>'
            u'<p class="kv-cap">%s<b>%s</b></p></div>'
            % (module["color"], ART.lesson_art(lesson["no"], "kv-art"), esc(focus), lesson["no"],
               esc(head + ", " if head else ""), esc(tail)))


def timeline(lesson):
    """중점 휴먼스킬 둘과 AI적정활용 기준을 시간 축으로 늘어놓는다."""
    out = ['<ol class="timeline">']
    for f in lesson["humanSkills"]["focus"]:
        out.append("<li><h3>%s</h3><p>%s</p><div class=\"tags\">%s</div></li>"
                   % (esc(f["name"]), esc(f["process"]),
                      "".join("<span>#%s</span>" % esc(t)
                              for t in [f["knowledge"][:16].strip(), f["value"][:14].strip()])))
    out.append("<li><h3>AI적정활용 기준</h3><p>%s</p><div class=\"tags\">%s</div></li>"
               % (esc(" / ".join(lesson["aiComponents"])),
                  "".join("<span>#%s</span>" % esc(p.split(". ", 1)[-1])
                          for p in lesson["aiPrinciples"])))
    out.append("</ol>")
    return "".join(out)


def lesson_ticket(lesson, data, depth=1):
    """레퍼런스의 카드 한 장에 해당한다. 차시 페이지와 모듈 페이지가 함께 쓴다."""
    up = "../" * depth
    m = data["modules"][lesson["module"] - 1]
    return u"""<article class="ticket">
  %s
  <div class="card-head">
    <h2>%d차시 %s</h2>
    <p>%s</p>
  </div>
  <div class="split">
    <div>
      %s
      <a class="btn-green" href="%swebapp/%s/index.html">웹앱 열기 · %s</a>
    </div>
    %s
  </div>
  <div class="card-foot">
    <p class="q">화면에서 바로 보기</p>
    <div class="foot-row">
      <span class="t">내려받지 않고 눌러서 봅니다</span>
      <div class="pills">
        <a class="pill" href="%sdeck/%s.html">수업 슬라이드</a>
        <a class="pill" href="%sprint/%s_지도안.html">지도안 보기</a>
        <a class="pill" href="%sprint/%s_활동지.html">활동지 보기</a>
        <a class="pill ghost" href="%swebapp/%s/index.html">웹앱 열기</a>
      </div>
    </div>
    <p class="q" style="margin-top:16px">파일로 내려받기</p>
    <div class="foot-row">
      <span class="t">한글 · 파워포인트로 고쳐 쓰실 수 있습니다</span>
      <div class="pills">
        <a class="pill" href="%sfiles/WISE_%s_지도안.hwpx" download>지도안</a>
        <a class="pill" href="%sfiles/WISE_%s_활동지.hwpx" download>활동지</a>
        <a class="pill" href="%sfiles/WISE_%s_수업.pptx" download>PPT</a>
        <a class="pill ghost" href="%swebapp/%s/PROMPT.md" download>웹앱 프롬프트</a>
      </div>
    </div>
  </div>
</article>""" % (RIBBON, lesson["no"], esc(lesson["shortTitle"]), esc(lesson["problem"]),
                 keyvis(lesson, m), up, lesson["id"], esc(lesson["webapp"]["name"]),
                 timeline(lesson),
                 up, lesson["id"], up, lesson["id"], up, lesson["id"], up, lesson["id"],
                 up, lesson["id"], up, lesson["id"], up, lesson["id"], up, lesson["id"])


def lesson_rows(lessons, data, depth=0):
    up = "../" * depth
    out = ['<div class="rows">']
    for l in lessons:
        m = data["modules"][l["module"] - 1]
        out.append('<a class="row" href="%slesson/%s.html" style="--rc:%s">'
                   '<span class="no">%d차시</span>'
                   '<span class="body"><h3>%s</h3><p>%s</p></span>'
                   '<span class="plus" aria-hidden="true">+</span></a>'
                   % (up, l["id"], m["color"], l["no"],
                      esc(l["shortTitle"]), esc(l["problem"])))
    out.append("</div>")
    return "".join(out)


# ---------------------------------------------------------------- 쪽

def home(data):
    prog = data["program"]
    b = []
    a = b.append

    a('<div class="hero">%s<div class="wrap">' % DOODLES)
    a('<p class="kicker">%s</p>' % esc(prog["team"]))
    a("<h1>AI는 내 생각을 <em>도와주는 걸까요</em>,<br>아니면 <em>대신해 주는 걸까요</em></h1>")
    a('<p class="lede">%s · 초등 5·6학년 12차시</p>' % esc(prog["name"]))
    a('<div class="facts"><span>지도안 12편</span><span>활동지 12종</span>'
      '<span>수업용 PPT 12세트</span><span>수업 웹앱 12개</span></div>')
    a(ART.hero_art())
    a('<p style="text-align:center;margin-top:18px">'
      '<a class="pill" href="browse.html" style="display:inline-block;border:2.5px solid var(--line);'
      'background:var(--green);padding:12px 22px;font-weight:900;color:var(--ink)">'
      '먼저 둘러보기</a></p>')
    a("</div></div>")

    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<h2>열두 시간 동안 어디로 가나요?</h2>'
      '<p>발견에서 판단으로, 판단에서 실천으로 이어집니다.</p></div>')
    a('<div class="stickers">')
    for m in data["modules"]:
        a('<a class="sticker" href="module/M%d.html" style="--sc:%s">'
          '<span class="no">모듈 %02d</span>'
          '<h3>%s<br><em>%s</em></h3><p>%s</p></a>'
          % (m["no"], m["color"], m["no"], esc(m["name"]), esc(m["tagline"]), esc(m["intent"])))
    a("</div></div></section>")

    a('<section class="band tight" style="background:var(--cream-d);'
      'border-top:2px solid var(--line);border-bottom:2px solid var(--line)">'
      '<div class="wrap"><div class="band-head">'
      '<span class="band-note">되고 안 되고 둘로 나뉘지 않습니다</span>'
      '<h2>AI 신호등 네 단계</h2>'
      '<p>6차시에서 학생이 상황 카드 스무 장을 직접 나눕니다.</p></div>')
    a('<div class="signals">')
    for s in data["signals"]:
        a('<div class="signal"><div class="dot" style="--sg:%s"></div>'
          '<p class="say">%s</p><p class="pol">%s · %s</p><p class="mean">%s</p></div>'
          % (s["color"], esc(s["student"]), esc(s["light"]), esc(s["policy"]), esc(s["meaning"])))
    a("</div></div></section>")

    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<h2>사례로 만나는 12차시</h2>'
      '<p>차시를 누르면 지도안, 활동지, PPT, 웹앱이 한자리에 있습니다.</p></div>')
    a(lesson_rows(data["lessons"], data, 0))
    a("</div></section>")

    a('<section class="band tight"><div class="wrap"><div class="band-head">'
      '<h2>함께 쓰는 자료</h2></div><div class="stickers">')
    for href, color, title, desc in [
        ("apps.html", "#111111", "12차시 웹앱",
         "차시마다 하나씩 모두 12개입니다. 방 코드로 함께 들어가고 혼자서도 체험할 수 있습니다."),
        ("survey.html", "#2B59E0", "AI적정활용 자기인식 진단",
         "여덟 문항으로 열두 시간 동안의 변화를 봅니다."),
        ("skills.html", "#7B4FE8", "인간중심 사고 12역량",
         "무엇을 기르는 수업인지 한눈에 봅니다."),
    ]:
        a('<a class="sticker" href="%s" style="--sc:%s"><h3>%s</h3><p>%s</p></a>'
          % (href, color, esc(title), esc(desc)))
    a("</div></div></section>")

    a('<section class="band tight"><div class="wrap"><div class="band-head">'
      '<h2>수업을 마친 아이들의 말</h2>'
      '<p>12차시 성찰문에서 자주 나오기를 바라는 문장들입니다.</p></div><div class="chat">')
    for line in [
        "AI는 사람이 준 데이터로 배운다는 걸 처음 알았어요",
        "그럴듯한 답이 늘 맞는 답은 아니라는 걸 겪어 봤습니다",
        "우리 반 약속을 우리가 만들었다는 게 제일 좋았어요",
        "이 글은 제 글입니다. 왜 이렇게 썼는지 설명할 수 있어요",
    ]:
        a("<div>%s</div>" % esc(line))
    a("</div></div></section>")
    return "".join(b)


def skills_page(data):
    hs = data["humanSkills"]
    b = []
    a = b.append
    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<span class="band-note">중점 일곱 가지와 보조 다섯 가지로 나누어 다룹니다</span>'
      '<h2>AI 시대를 주도적으로 살아가기 위한 힘<br>인간중심 사고 12역량</h2>'
      '<p>네이버 커넥트재단 휴먼스킬 내용 체계를 12차시에 나누어 담았습니다.</p></div>')

    for group, items in [("중점", hs["focus"]), ("보조", hs["support"])]:
        tint, lab = SKILL_TINT[group]
        a('<h3 style="font-size:19px;margin:26px 0 14px">%s 역량 %d가지 <span style="font-weight:600;color:var(--muted);font-size:15px">%s</span></h3>'
          % (group, len(items),
             "평가 기준과 사전·사후 설문에 직접 연결합니다" if group == "중점"
             else "활동 속에서 자연스럽게 다루고 따로 평가하지 않습니다"))
        a('<div class="skills">')
        for s in items:
            a('<div class="skill" style="--sk:%s"><span class="lab" style="--lab:%s">%s</span>'
              '<p class="en">%s</p><h3>%s</h3><p>%s</p></div>'
              % (tint, lab, group, esc(s["en"]), esc(s["name"]), esc(s["concept"])))
        a("</div>")

    a('<div class="panel" style="margin-top:34px"><h2>어느 차시에서 기르나</h2>'
      '<div class="scroll"><table><tr><th>역량</th><th>관련 차시</th><th>평가 목표</th></tr>')
    for p in data["assessmentPlan"]:
        a("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>"
          % (esc(p["skill"]), esc(", ".join("%d차시" % n for n in p["lessons"])), esc(p["goal"])))
    a("</table></div></div>")
    a("</div></section>")
    return "".join(b)


def module_page(m, data):
    b = []
    a = b.append
    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<span class="band-note">모듈 %02d · %s</span>'
      '<h2>%s<br>%s</h2><p style="max-width:720px;margin:14px auto 0">%s</p></div>'
      % (m["no"], esc(m["range"]), esc(m["name"]), esc(m["tagline"]), esc(m["intent"])))
    a('<div class="panel"><h2>이 모듈에서 기르는 힘</h2><p>%s</p></div>'
      % esc(" · ".join(m["skills"])))
    for l in data["lessons"]:
        if l["module"] == m["no"]:
            a(lesson_ticket(l, data, depth=1))
    a("</div></section>")
    return "".join(b)


def stage_html(label, stage):
    b = ['<span class="stage">%s · %d분</span>' % (esc(label), stage["minutes"])]
    for blk in stage["blocks"]:
        b.append("<h3>%s</h3>" % esc(blk["heading"]))
        for t in blk.get("turns", []):
            b.append('<div class="qa"><p class="q">%s</p>' % esc(t["q"]))
            for ans in t.get("a", []):
                b.append('<p class="a">%s</p>' % esc(ans))
            b.append("</div>")
    b.append("<h3>준비물과 유의점</h3><ul>")
    for m in stage["materials"]:
        b.append("<li>%s</li>" % esc(m))
    b.append("</ul>")
    return "".join(b)


def lesson_page(l, data):
    m = data["modules"][l["module"] - 1]
    b = []
    a = b.append
    a('<section class="band"><div class="wrap">')
    a('<div class="band-head" style="text-align:left;margin-bottom:26px">'
      '<span class="band-note">모듈%d %s · %d차시</span><h2>%s</h2>'
      '<p style="font-size:18px;color:var(--ink2)">%s</p></div>'
      % (m["no"], esc(m["name"]), l["no"], esc(l["title"]), esc(l["problem"])))

    a(lesson_ticket(l, data, depth=1))

    a('<div class="panel"><h2>휴먼스킬</h2><div class="scroll"><table>'
      "<tr><th>역량</th><th>지식·이해</th><th>과정·기능</th><th>가치·태도</th></tr>")
    for f in l["humanSkills"]["focus"]:
        a("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (esc(f["name"]), esc(f["knowledge"]), esc(f["process"]), esc(f["value"])))
    a("</table></div>")
    if l["humanSkills"].get("support"):
        a('<p style="margin-top:10px;color:var(--muted);font-size:15px">보조 역량 : %s</p>'
          % esc(", ".join(l["humanSkills"]["support"])))
    a("</div>")

    a('<div class="panel"><h2>수업 흐름</h2>')
    a(stage_html("도입", l["plan"]["intro"]))
    a(stage_html("전개", l["plan"]["develop"]))
    a(stage_html("정리", l["plan"]["close"]))
    a("</div>")

    w = l["webapp"]
    a('<div class="panel"><h2>오늘 쓰는 웹앱</h2><h3>%s</h3><p>%s</p><ul>'
      % (esc(w["name"]), esc(w["purpose"])))
    for sc in w["screens"]:
        a("<li>%s</li>" % esc(sc))
    a("</ul>")
    if w.get("steps"):
        a('<h3>40분을 이렇게 씁니다</h3><div class="scroll"><table>'
          "<tr><th>단계</th><th>시간</th><th>무엇을 하나</th><th>교사 발문</th></tr>")
        for st in w["steps"]:
            a("<tr><td><strong>%d. %s</strong></td><td>%d분</td><td>%s</td>"
              "<td>%s<br><span style=\"color:var(--muted)\">%s</span></td></tr>"
              % (st["no"], esc(st["title"]), st["minutes"], esc(st["what"]),
                 esc(st["ask"]), esc(st["expect"])))
        a("</table></div>")
    a("</div>")

    a('<div class="panel"><h2>기기가 없어도 함께합니다</h2><p>%s</p></div>' % esc(l["alternative"]))

    a('<div class="panel"><h2>관련 영상과 뉴스</h2>')
    a('<p style="color:var(--muted);font-size:15px">%s</p>' % esc(l.get("refHint", "")))
    a('<div class="refs">')
    mine = [r for r in data.get("references", []) if r.get("lesson") == l["id"]]
    common = [r for r in data.get("references", []) if not r.get("lesson")]
    for ref in mine + common:
        a('<div class="ref"><span class="kind">%s</span>%s<br>'
          '<a href="%s" target="_blank" rel="noopener">%s</a><p>%s</p></div>'
          % (esc(ref["kind"]),
             ('<span class="kind" style="background:var(--sun)">%s</span>' % esc(ref["source"]))
             if ref.get("source") else "",
             esc(ref["url"]), esc(ref["title"]), esc(ref["note"])))
    for n in range(max(0, l.get("refSlots", 2) - len(mine))):
        a('<div class="refslot"><strong>이 차시에 쓸 자료 %d</strong><br>'
          '선생님이 고른 영상이나 기사 주소를 여기에 적어 넣습니다. '
          '수업 전에 한 번 열어 보고, 학생 이름과 얼굴이 나오지 않는 것으로 고릅니다.</div>' % (n + 1))
    a('</div>')
    a('<div class="note" style="margin-top:14px">영상과 기사는 자주 바뀝니다. '
      '수업 하루 전에 링크가 살아 있는지 확인하고, 저작권 표시를 함께 보여 줍니다.</div>')
    a('</div>')

    a('<div class="panel"><h2>지도 유의점</h2><ul>')
    for c in l["cautions"]:
        a("<li>%s</li>" % esc(c))
    a("</ul><div class=\"note\">AI적정활용 : %s<br>실행 원칙 : %s</div></div>"
      % (esc(" / ".join(l["aiComponents"])), esc(" / ".join(l["aiPrinciples"]))))

    a('<div class="panel"><h2>교육과정</h2><div class="scroll"><table>'
      "<tr><th>성취기준</th><th>교과·시수</th><th>학생 산출물</th><th>평가 방법</th></tr>"
      "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr></table></div></div>"
      % (esc(" ".join(l["standards"])), esc(l["subject"]),
         esc(", ".join(l["outputs"])), esc(", ".join(l["assessment"]))))

    a('<div class="pager">')
    a('<a href="L%02d.html">앞 차시</a>' % (l["no"] - 1) if l["no"] > 1 else "<span></span>")
    if l["no"] < 12:
        a('<a href="L%02d.html">다음 차시</a>' % (l["no"] + 1))
    a("</div></div></section>")
    return "".join(b)


def browse_page(data):
    """선생님도 학생도 그냥 둘러볼 수 있는 쪽. 그림으로 먼저 보여 준다."""
    b = []
    a = b.append

    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<span class="band-note">수업을 준비하는 선생님도, 궁금한 학생도 이 쪽에서 시작합니다</span>'
      '<h2>열두 시간을 미리 둘러보기</h2>'
      '<p>차시마다 무엇을 하는지 그림으로 보고, 방 코드 없이도 활동을 직접 눌러 볼 수 있습니다.</p></div>')

    a('<div class="two">')
    a('<div class="who"><span class="badge">선생님이라면</span>'
      '<h3>수업 하루 전 5분</h3>'
      '<ol><li>아래에서 그날 차시 카드를 찾습니다.</li>'
      '<li>자세히 보기를 눌러 지도안, 활동지, PPT를 내려받습니다.</li>'
      '<li>체험해 보기로 학생이 볼 화면을 미리 열어 봅니다.</li>'
      '<li>수업에서는 선생님 화면에서 방을 만들어 코드를 나눠 줍니다.</li></ol></div>')
    a('<div class="who"><span class="badge">학생이라면</span>'
      '<h3>방 코드가 없어도 괜찮아요</h3>'
      '<ol><li>궁금한 차시 카드를 눌러요.</li>'
      '<li>체험해 보기를 누르고 닉네임만 쓰면 돼요.</li>'
      '<li>혼자 체험한 내용은 내 기기에만 남아요.</li>'
      '<li>이름, 사진, 친구 이야기는 넣지 않아요.</li></ol></div>')
    a('</div>')

    a('<div class="band-head" style="margin-top:44px"><h2>열두 개의 활동</h2>'
      '<p>그림을 보고 무엇을 하는 시간인지 짐작해 봅시다.</p></div>')
    a('<div class="gallery">')
    for l in data["lessons"]:
        m = data["modules"][l["module"] - 1]
        w = l["webapp"]
        a('<article class="gcard">'
          '<div class="shot"><span class="tagno">%d차시 · %s</span>%s</div>'
          '<div class="body"><h3>%s</h3>'
          '<p class="ask">%s</p><p>%s</p>'
          '<div class="go"><a class="main" href="webapp/%s/index.html">체험해 보기</a>'
          '<a href="deck/%s.html">슬라이드</a>'
          '<a href="lesson/%s.html">자세히 보기</a></div></div></article>'
          % (l["no"], esc(m["name"]), ART.lesson_art(l["no"]),
             esc(w["name"]), esc(l["problem"]), esc(w["purpose"]),
             l["id"], l["id"], l["id"]))
    a('</div></div></section>')

    a('<section class="band tight" style="background:var(--cream-d);'
      'border-top:2px solid var(--line);border-bottom:2px solid var(--line)">'
      '<div class="wrap"><div class="band-head">'
      '<h2>모든 차시에 들어 있는 세 걸음</h2>'
      '<p>먼저 내 생각을 만들고, 그다음에 AI에게 묻고, 마지막에 내 말로 다시 씁니다.</p></div>')
    a(ART.flow_art())
    a('</div></section>')

    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<h2>우리가 쓰는 신호등</h2>'
      '<p>되고 안 되고 둘로 나누지 않습니다. 조건을 붙여 판단합니다.</p></div>')
    a('<div class="sigrow">')
    for s in data["signals"]:
        a('<div class="cell">%s<h3>%s</h3><p>%s</p></div>'
          % (ART.signal_art(s["color"], s["student"]), esc(s["student"]), esc(s["meaning"])))
    a('</div>')
    a('<div class="panel" style="margin-top:26px"><h2>둘러본 뒤에</h2>'
      '<p>수업 전후로 같은 여덟 문항에 답해 보면 무엇이 달라졌는지 숫자로 볼 수 있습니다.</p>'
      '<div class="dl"><a href="webapp/common/index.html">자기인식 설문 열어 보기'
      '<small>사전·사후 공용 · 닉네임만 씁니다</small></a></div></div>')
    a('</div></section>')
    return "".join(b)


def apps_page(data):
    b = []
    a = b.append
    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<span class="band-note">실명·학번·연락처를 묻지 않습니다. 닉네임만 씁니다</span>'
      '<h2>12차시 웹앱</h2>'
      '<p>선생님이 방 코드를 만들어 나눠 주시면 학생은 닉네임으로 들어옵니다. '
      '방 코드 없이 혼자 체험하는 길도 있습니다.</p></div>')

    a('<article class="ticket">%s<div class="card-head"><h2>13개 앱이 같은 방식으로 돌아갑니다</h2>'
      '<p>활동 화면만 차시마다 다릅니다</p></div>'
      '<ol class="timeline">'
      '<li><h3>교사가 방 만들기</h3><p>숫자 여섯 자리 방 코드가 나오고 복사 버튼이 있습니다.</p></li>'
      '<li><h3>학생이 입장</h3><p>방 코드와 비밀번호 네 자리, 닉네임으로 들어옵니다.</p></li>'
      '<li><h3>활동과 제출</h3><p>여기만 차시마다 다릅니다. 고쳐서 다시 제출해도 됩니다.</p></li>'
      '<li><h3>교사 화면</h3><p>제출 현황, 집계, CSV 내려받기, 방 잠그기가 있습니다.</p></li>'
      '</ol></article>' % RIBBON)

    a('<div class="rows" style="margin-top:30px">')
    for l in data["lessons"]:
        m = data["modules"][l["module"] - 1]
        a('<a class="row" href="webapp/%s/index.html" style="--rc:%s">'
          '<span class="no">%d차시</span>'
          '<span class="body"><h3>%s</h3><p>%s</p></span>'
          '<span class="plus" aria-hidden="true">+</span></a>'
          % (l["id"], m["color"], l["no"],
             esc(l["webapp"]["name"]), esc(l["webapp"]["purpose"])))
    a('<a class="row" href="webapp/common/index.html" style="--rc:#111111">'
      '<span class="no">공통</span>'
      '<span class="body"><h3>사전·사후 자기인식 설문</h3>'
      '<p>1차시 전과 12차시 뒤에 같은 여덟 문항으로 묻고 변화량을 자동으로 계산합니다.</p></span>'
      '<span class="plus" aria-hidden="true">+</span></a>')
    a("</div></div></section>")
    return "".join(b)


def survey_page(data):
    s = data["survey"]
    b = []
    a = b.append
    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<span class="band-note">%s 여덟 문항</span><h2>%s</h2>'
      '<p>1차시 전과 12차시 뒤에 같은 문항으로 묻습니다.</p></div>'
      % (esc(s["scale"]), esc(s["title"])))
    a('<div class="panel"><div class="scroll"><table>'
      "<tr><th>번호</th><th>문항</th><th>연계 휴먼스킬</th></tr>")
    for i in s["items"]:
        a("<tr><td>%d</td><td>%s</td><td>%s</td></tr>"
          % (i["no"], esc(i["text"]), esc(i["skill"])))
    a('</table></div><div class="note">%s</div></div>' % esc(s["note"]))
    a('<div class="panel"><h2>자유응답</h2><ul>')
    for o in s["openItems"]:
        a("<li>%s <span style='color:var(--muted)'>(%s)</span></li>" % (esc(o["text"]), esc(o["when"])))
    a("</ul></div>")
    a('<div class="panel"><h2>설문 웹앱</h2><div class="dl">'
      '<a href="webapp/common/index.html">설문 웹앱 열기<small>사전·사후 공용</small></a></div></div>')
    a("</div></section>")
    return "".join(b)


def about_page(data):
    prog = data["program"]
    b = []
    a = b.append
    a('<section class="band"><div class="wrap"><div class="band-head">'
      '<h2>이 수업의 근거와 설계</h2></div>')
    a('<div class="panel"><h2>만든 이유</h2>'
      "<p>아이들은 이미 생성형 AI를 일상처럼 씁니다. 그런데 언제, 어디까지, 어떻게 쓰는 것이 좋은지 "
      "판단하는 기준은 배우지 못한 채 자랍니다. 네 학급에서 같은 질문이 되풀이되었습니다. "
      "<b>이거 AI한테 시켜도 되나요?</b></p>"
      "<p>그래서 이 수업은 질문을 바꾸었습니다. 얼마나 쓰는가가 아니라, "
      "내 생각과 판단을 지키면서 쓰는가입니다. 아이가 열두 시간에 걸쳐 스스로 기준을 세우고 "
      "그 기준대로 살아 보도록 돕습니다.</p></div>")
    a('<div class="panel"><h2>설계</h2>'
      "<p>세 가지 자료를 바탕으로 삼았습니다. 어른들의 문서를 아이들이 할 수 있는 활동으로 옮겼습니다.</p>"
      '<div class="scroll"><table>'
      "<tr><th>바탕이 된 자료</th><th>수업으로 옮긴 방법</th></tr>"
      "<tr><td>네이버 커넥트재단 휴먼스킬 내용 체계</td>"
      "<td>12역량을 지식·이해, 과정·기능, 가치·태도로 나누어 담았습니다. "
      "중점 7개는 평가로 이어지고, 보조 5개는 활동 속에서 자연스럽게 다룹니다.</td></tr>"
      "<tr><td>미래교육원 교육정책연구소 AI적정활용</td>"
      "<td>8가지 핵심 구성요소를 7차시 <b>우리 반 AI 약속 8조항</b>으로 옮겼습니다.</td></tr>"
      "<tr><td>AI적정활용 델파이 조사</td>"
      "<td>인간다움 우선 원칙과 10대 실행 원칙, 4단계 적용기준을 6차시 <b>AI 신호등</b>으로 옮겼습니다.</td></tr>"
      "</table></div></div>")
    a('<div class="panel"><h2>설계 원리</h2><ul>'
      "<li><strong>생각이 먼저입니다</strong> : 모든 차시에 내 생각 먼저 쓰기, AI에게 검토받기, "
      "내 말로 다시 정리하기의 세 걸음이 들어 있습니다.</li>"
      "<li><strong>겪어 본 다음에 판단합니다</strong> : 판단과 약속 활동은 직접 겪어 본 경험 뒤에 옵니다.</li>"
      "<li><strong>금지 목록이 아니라 판단 기준입니다</strong> : 하지 말 것을 나열하지 않고, "
      "어떤 조건이면 써도 되는지를 아이들이 스스로 정합니다.</li>"
      "<li><strong>모두가 참여합니다</strong> : 기기가 한 사람에 한 대가 아니어도 할 수 있는 "
      "대안 활동을 모든 차시에 함께 마련했습니다.</li>"
      "<li><strong>열면 바로 수업이 됩니다</strong> : 발문, 예상 답변, 쓰는 도구, 확인 목록을 "
      "지도안에 모두 적어 두었습니다.</li>"
      "</ul></div>")
    a('<div class="panel"><h2>우리 반 AI 약속 8조항</h2><div class="scroll"><table>'
      "<tr><th>핵심 구성요소</th><th>아이들 말로 옮긴 약속</th><th>주로 다루는 차시</th></tr>")
    for c in data["aiComponents"]:
        a("<tr><td>%s %s</td><td>%s</td><td>%d차시</td></tr>"
          % (esc(c["mark"]), esc(c["name"]), esc(c["pledge"]), c["lesson"]))
    a("</table></div></div>")
    a('<div class="panel"><h2>만든 사람들</h2><p>%s</p><p>%s</p>'
      "<p>적용 학급 : %s</p><p>적용 기간 : %s</p></div>"
      % (esc(prog["team"]), esc(" · ".join(prog["members"])),
         esc(", ".join(prog["classes"])), esc(prog["period"])))
    a("</div></section>")
    return "".join(b)


# ---------------------------------------------------------------- 쓰기

def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def copy_downloads(data):
    files = os.path.join(SITE, "files")
    if not os.path.isdir(files):
        os.makedirs(files)
    n = 0
    for l in data["lessons"]:
        for src in [
            os.path.join(T.ROOT, "out", "지도안", "WISE_%s_지도안.hwpx" % l["id"]),
            os.path.join(T.ROOT, "out", "활동지", "WISE_%s_활동지.hwpx" % l["id"]),
            os.path.join(T.ROOT, "out", "ppt", "WISE_%s_수업.pptx" % l["id"]),
        ]:
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(files, os.path.basename(src)))
                n += 1
    src_root = os.path.join(T.ROOT, "out", "webapp")
    dst_root = os.path.join(SITE, "webapp")
    if os.path.isdir(src_root):
        if os.path.isdir(dst_root):
            shutil.rmtree(dst_root)
        shutil.copytree(src_root, dst_root)
    return n


def main():
    data = T.load_lessons()

    write(os.path.join(SITE, "assets", "style.css"), CSS)
    write(os.path.join(SITE, "index.html"),
          page(data["program"]["name"], home(data), 0, "index.html", data))

    for m in data["modules"]:
        write(os.path.join(SITE, "module", "M%d.html" % m["no"]),
              page("모듈%d %s" % (m["no"], m["name"]), module_page(m, data),
                   1, "module/M%d.html" % m["no"], data))

    for l in data["lessons"]:
        write(os.path.join(SITE, "lesson", "%s.html" % l["id"]),
              page("%d차시 %s" % (l["no"], l["shortTitle"]), lesson_page(l, data),
                   1, "module/M%d.html" % l["module"], data))

    write(os.path.join(SITE, "browse.html"),
          page("둘러보기", browse_page(data), 0, "browse.html", data))
    write(os.path.join(SITE, "skills.html"),
          page("인간중심 사고 12역량", skills_page(data), 0, "skills.html", data))
    write(os.path.join(SITE, "apps.html"), page("12차시 웹앱", apps_page(data), 0, "apps.html", data))
    write(os.path.join(SITE, "survey.html"),
          page("AI적정활용 자기인식 진단", survey_page(data), 0, "survey.html", data))
    write(os.path.join(SITE, "about.html"), page("프로그램 소개", about_page(data), 0, "about.html", data))

    make_qr.build(data, SITE)
    views = make_view.build_all(data, SITE)
    make_admin.build(data, SITE)
    guides = make_guide.build(data, SITE)
    make_refs.build(data, SITE)
    n = copy_downloads(data)
    print("사이트를 만들었다 : %s" % SITE)
    print("  화면에서 바로 보는 자료 %d쪽 (슬라이드 12 · 지도안 12 · 활동지 12) · 관리자 화면 1쪽" % views)
    print("  페이지 %d개 (홈 1 · 둘러보기 1 · 모듈 3 · 차시 12 · 역량 1 · 웹앱 1 · 진단 1 · 소개 1), "
          "내려받기 파일 %d개" % (1 + 1 + 3 + 12 + 4, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
