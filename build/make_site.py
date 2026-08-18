# -*- coding: utf-8 -*-
"""통합 웹사이트를 만든다. 빌드 도구 없이 열리는 순수 정적 HTML.

사용법 : py -3 build/make_site.py
"""
import io
import os
import shutil
import sys

import tasks as T

T.setup_console()

SITE = os.path.join(T.ROOT, "out", "site")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


CSS = u"""/* WISE 통합 사이트 공통 스타일 */
*,*::before,*::after{box-sizing:border-box}
:root{
  --ink:#111827; --body:#374151; --muted:#6b7280; --line:#e5e7eb;
  --paper:#ffffff; --bg:#f9fafb; --brand:#1d4ed8;
  --m1:#2563eb; --m2:#d97706; --m3:#059669;
  --wrap:1080px; --radius:16px;
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--body);
  font-family:"Pretendard","Malgun Gothic","맑은 고딕",system-ui,-apple-system,sans-serif;
  font-size:17px;line-height:1.7;overflow-x:hidden}
h1,h2,h3,h4{margin:0;color:var(--ink);line-height:1.35;font-weight:700}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
img{max-width:100%;height:auto}
.wrap{max-width:var(--wrap);margin:0 auto;padding:0 20px}

/* 머리말 */
.top{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.94);
  backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .wrap{display:flex;align-items:center;gap:18px;min-height:64px;flex-wrap:wrap}
.brand{font-weight:800;color:var(--ink);font-size:18px;white-space:nowrap}
.brand span{color:var(--brand)}
.nav{display:flex;gap:6px;flex-wrap:wrap;margin-left:auto}
.nav a{padding:8px 12px;border-radius:9px;color:var(--body);font-size:15px;font-weight:600}
.nav a:hover{background:var(--bg);text-decoration:none}
.nav a[aria-current="page"]{background:var(--brand);color:#fff}

/* 표지 */
.hero{background:linear-gradient(135deg,#1e3a8a,#1d4ed8 55%,#0ea5e9);color:#fff;
  padding:64px 0 72px}
.hero .kicker{font-size:15px;font-weight:700;opacity:.85;letter-spacing:.02em}
.hero h1{color:#fff;font-size:40px;margin:14px 0 16px;letter-spacing:-.02em}
.hero p{margin:0;font-size:19px;max-width:640px;opacity:.94}
.hero .meta{margin-top:26px;display:flex;gap:10px;flex-wrap:wrap}
.hero .meta span{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.28);
  border-radius:999px;padding:7px 15px;font-size:14px;font-weight:600}

/* 구역 */
section{padding:52px 0}
.sec-h{margin-bottom:24px}
.sec-h h2{font-size:26px}
.sec-h p{margin:8px 0 0;color:var(--muted)}

/* 카드 */
.cards{display:grid;gap:18px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}
.card{display:block;background:var(--paper);border:1px solid var(--line);
  border-radius:var(--radius);padding:24px;color:var(--body);
  transition:box-shadow .18s ease,transform .18s ease}
a.card:hover{text-decoration:none;box-shadow:0 10px 26px rgba(17,24,39,.09);transform:translateY(-2px)}
.card h3{font-size:19px;margin-bottom:8px}
.card p{margin:0;font-size:15px;color:var(--muted)}
.tag{display:inline-block;font-size:13px;font-weight:800;padding:4px 11px;
  border-radius:999px;margin-bottom:12px}
.m1{background:#eff6ff;color:var(--m1)} .m2{background:#fffbeb;color:var(--m2)}
.m3{background:#ecfdf5;color:var(--m3)}
.bar{height:5px;border-radius:5px;margin-bottom:16px}
.bar.m1{background:var(--m1)} .bar.m2{background:var(--m2)} .bar.m3{background:var(--m3)}

/* 차시 목록 */
.lessons{display:grid;gap:12px}
.lesson-row{display:flex;gap:16px;align-items:flex-start;background:var(--paper);
  border:1px solid var(--line);border-radius:12px;padding:18px 20px;color:var(--body)}
a.lesson-row:hover{text-decoration:none;border-color:var(--brand)}
.lesson-no{flex:0 0 auto;width:46px;height:46px;border-radius:11px;display:flex;
  align-items:center;justify-content:center;font-weight:800;font-size:15px;color:#fff}
.lesson-row h3{font-size:17px;margin-bottom:4px}
.lesson-row p{margin:0;font-size:14px;color:var(--muted)}

/* 본문 */
.panel{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);
  padding:26px;margin-bottom:18px}
.panel h2{font-size:20px;margin-bottom:14px}
.panel h3{font-size:16px;margin:18px 0 6px}
.panel ul,.panel ol{margin:0;padding-left:20px}
.panel li{margin:5px 0}
.qa{margin:0 0 14px;padding-left:14px;border-left:3px solid var(--line)}
.qa .q{font-weight:600;color:var(--ink)}
.qa .a{color:var(--muted);font-size:15px;margin-left:12px}
.stage{display:inline-block;font-size:13px;font-weight:800;color:var(--brand);
  background:#eff6ff;border-radius:999px;padding:3px 10px;margin-bottom:10px}

.dl{display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(210px,1fr))}
.dl a{display:block;border:1px solid var(--line);border-radius:11px;padding:14px 16px;
  background:var(--bg);font-weight:600;font-size:15px;color:var(--ink)}
.dl a:hover{border-color:var(--brand);text-decoration:none}
.dl a small{display:block;font-weight:500;color:var(--muted);font-size:13px;margin-top:2px}

.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:15px;min-width:520px}
th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
th{background:var(--bg);font-weight:700;color:var(--ink)}

.note{background:#fff7ed;border:1px solid #fed7aa;color:#9a3412;
  border-radius:11px;padding:14px 16px;font-size:15px}

.signal{display:grid;gap:10px}
.signal div{border-radius:11px;padding:14px 16px;color:#fff;font-weight:600}

.pager{display:flex;justify-content:space-between;gap:12px;margin-top:20px;flex-wrap:wrap}
.pager a{background:var(--paper);border:1px solid var(--line);border-radius:11px;
  padding:12px 16px;font-weight:600}

footer{border-top:1px solid var(--line);background:var(--paper);padding:30px 0;
  color:var(--muted);font-size:14px}
footer p{margin:4px 0}

@media (max-width:640px){
  body{font-size:16px}
  .hero{padding:44px 0 50px} .hero h1{font-size:29px} .hero p{font-size:17px}
  section{padding:36px 0} .panel{padding:20px}
  .top .wrap{min-height:auto;padding-top:10px;padding-bottom:10px}
  .nav{margin-left:0;width:100%}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

NAV = [
    ("index.html", "홈"),
    ("module/M1.html", "모듈1 발견"),
    ("module/M2.html", "모듈2 판단"),
    ("module/M3.html", "모듈3 실천"),
    ("apps.html", "12차시 웹앱"),
    ("survey.html", "자기인식 진단"),
    ("about.html", "소개"),
]


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
<header class="top"><div class="wrap">
  <a class="brand" href="%sindex.html">WISE <span>AI적정활용</span></a>
  <nav class="nav">%s</nav>
</div></header>
%s
<footer><div class="wrap">
  <p><strong>%s</strong></p>
  <p>%s</p>
  <p>%s</p>
  <p>산출물 저작권은 연구회에 귀속되며 재단이 CC BY-NC-SA로 공개합니다. 수업 자료로 자유롭게 내려받아 고쳐 쓰실 수 있습니다.</p>
</div></footer>
</body>
</html>
""" % (esc(title), esc(prog["name"]), up, up, nav, body,
       esc(prog["name"]), esc(" · ".join(prog["members"])), esc(prog["copyrightLine"]))


def home(data):
    prog = data["program"]
    b = []
    a = b.append
    a('<div class="hero"><div class="wrap">')
    a('<p class="kicker">%s</p>' % esc(prog["team"]))
    a("<h1>%s</h1>" % esc(prog["name"]))
    a("<p>%s</p>" % esc(prog["subtitle"]))
    a('<div class="meta"><span>초등 5·6학년</span><span>총 12차시</span>'
      '<span>지도안 · 활동지 · PPT · 웹앱</span><span>%s</span></div>' % esc(prog["corePrinciple"]))
    a("</div></div>")

    a('<section><div class="wrap"><div class="sec-h"><h2>세 개의 모듈</h2>'
      '<p>발견에서 판단으로, 판단에서 실천으로 이어집니다.</p></div><div class="cards">')
    for m in data["modules"]:
        a('<a class="card" href="module/M%d.html"><div class="bar m%d"></div>'
          '<span class="tag m%d">모듈%d · %s</span><h3>%s</h3><p>%s</p></a>'
          % (m["no"], m["no"], m["no"], m["no"], esc(m["range"]),
             esc(m["name"] + " : " + m["tagline"]), esc(m["intent"])))
    a("</div></div></section>")

    a('<section><div class="wrap"><div class="sec-h"><h2>함께 쓰는 자료</h2></div><div class="cards">')
    for href, title, desc in [
        ("apps.html", "12차시 웹앱", "차시마다 하나씩, 모두 12개입니다. 방 코드로 함께 들어가고 혼자서도 체험할 수 있습니다."),
        ("survey.html", "AI적정활용 자기인식 진단", "8문항 사전·사후 설문으로 열두 시간 동안의 변화를 봅니다."),
        ("about.html", "프로그램 소개", "무엇을 근거로 어떻게 설계했는지 정리했습니다."),
    ]:
        a('<a class="card" href="%s"><h3>%s</h3><p>%s</p></a>' % (href, esc(title), esc(desc)))
    a("</div></div></section>")

    a('<section><div class="wrap"><div class="sec-h"><h2>AI 신호등</h2>'
      '<p>6차시에서 학생이 직접 상황을 네 가지 신호로 나눕니다.</p></div><div class="signal">')
    for s in data["signals"]:
        a('<div style="background:%s">%s · %s <span style="opacity:.85;font-weight:500">'
          '(%s)</span></div>' % (s["color"], esc(s["light"]), esc(s["student"]), esc(s["policy"])))
    a("</div></div></section>")

    a('<section><div class="wrap"><div class="sec-h"><h2>12차시 한눈에 보기</h2></div><div class="lessons">')
    for l in data["lessons"]:
        m = data["modules"][l["module"] - 1]
        a('<a class="lesson-row" href="lesson/%s.html">'
          '<span class="lesson-no" style="background:%s">%d차시</span>'
          '<span><h3>%s</h3><p>%s</p></span></a>'
          % (l["id"], m["color"], l["no"], esc(l["shortTitle"]), esc(l["problem"])))
    a("</div></div></section>")
    return "".join(b)


def module_page(m, data):
    b = []
    a = b.append
    a('<section><div class="wrap">')
    a('<div class="bar m%d"></div><span class="tag m%d">모듈%d · %s</span>'
      % (m["no"], m["no"], m["no"], esc(m["range"])))
    a("<h1>%s</h1>" % esc(m["name"] + " : " + m["tagline"]))
    a('<p style="max-width:720px;margin-top:12px">%s</p>' % esc(m["intent"]))
    a('<div class="panel" style="margin-top:24px"><h2>중심 휴먼스킬</h2><ul>')
    for s in m["skills"]:
        a("<li>%s</li>" % esc(s))
    a("</ul></div>")
    a('<div class="lessons">')
    for l in data["lessons"]:
        if l["module"] != m["no"]:
            continue
        a('<a class="lesson-row" href="../lesson/%s.html">'
          '<span class="lesson-no" style="background:%s">%d차시</span>'
          '<span><h3>%s</h3><p>%s</p></span></a>'
          % (l["id"], m["color"], l["no"], esc(l["shortTitle"]), esc(l["problem"])))
    a("</div></div></section>")
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
    a('<section><div class="wrap">')
    a('<div class="bar m%d"></div><span class="tag m%d">%d차시 · 모듈%d %s</span>'
      % (m["no"], m["no"], l["no"], m["no"], esc(m["name"])))
    a("<h1>%s</h1>" % esc(l["title"]))
    a('<p style="font-size:19px;margin-top:12px">%s</p>' % esc(l["problem"]))

    a('<div class="panel" style="margin-top:24px"><h2>자료 내려받기</h2><div class="dl">')
    a('<a href="../files/WISE_%s_지도안.hwpx" download>교수·학습 지도안<small>HWPX</small></a>' % l["id"])
    a('<a href="../files/WISE_%s_활동지.hwpx" download>학생 활동지<small>HWPX</small></a>' % l["id"])
    a('<a href="../files/WISE_%s_수업.pptx" download>수업용 PPT<small>PPTX · 11장</small></a>' % l["id"])
    a('<a href="../webapp/%s/index.html">웹앱 열기<small>%s</small></a>' % (l["id"], esc(l["webapp"]["name"])))
    a('<a href="../webapp/%s/PROMPT.md" download>웹앱 제작 프롬프트<small>고쳐 쓰기용</small></a>' % l["id"])
    a("</div></div>")

    a('<div class="panel"><h2>휴먼스킬</h2><div class="scroll"><table>'
      "<tr><th>역량</th><th>지식·이해</th><th>과정·기능</th><th>가치·태도</th></tr>")
    for f in l["humanSkills"]["focus"]:
        a("<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (esc(f["name"]), esc(f["knowledge"]), esc(f["process"]), esc(f["value"])))
    a("</table></div>")
    if l["humanSkills"].get("support"):
        a("<p style='margin-top:10px;color:var(--muted);font-size:15px'>보조 역량 : %s</p>"
          % esc(", ".join(l["humanSkills"]["support"])))
    a("</div>")

    a('<div class="panel"><h2>수업 흐름</h2>')
    a(stage_html("도입", l["plan"]["intro"]))
    a(stage_html("전개", l["plan"]["develop"]))
    a(stage_html("정리", l["plan"]["close"]))
    a("</div>")

    a('<div class="panel"><h2>오늘 쓰는 웹앱</h2><h3>%s</h3><p>%s</p><ul>'
      % (esc(l["webapp"]["name"]), esc(l["webapp"]["purpose"])))
    for s in l["webapp"]["screens"]:
        a("<li>%s</li>" % esc(s))
    a("</ul></div>")

    a('<div class="panel"><h2>기기가 없어도 함께합니다</h2><p>%s</p></div>' % esc(l["alternative"]))

    a('<div class="panel"><h2>지도 유의점</h2><ul>')
    for c in l["cautions"]:
        a("<li>%s</li>" % esc(c))
    a("</ul>")
    a('<div class="note" style="margin-top:14px">AI적정활용 : %s<br>실행 원칙 : %s</div>'
      % (esc(" / ".join(l["aiComponents"])), esc(" / ".join(l["aiPrinciples"]))))
    a("</div>")

    a('<div class="panel"><h2>교육과정</h2><div class="scroll"><table>'
      "<tr><th>성취기준</th><th>교과·시수</th><th>학생 산출물</th><th>평가 방법</th></tr>"
      "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr></table></div></div>"
      % (esc(" ".join(l["standards"])), esc(l["subject"]),
         esc(", ".join(l["outputs"])), esc(", ".join(l["assessment"]))))

    a('<div class="pager">')
    if l["no"] > 1:
        a('<a href="L%02d.html">← %d차시</a>' % (l["no"] - 1, l["no"] - 1))
    else:
        a("<span></span>")
    if l["no"] < 12:
        a('<a href="L%02d.html">%d차시 →</a>' % (l["no"] + 1, l["no"] + 1))
    a("</div></div></section>")
    return "".join(b)


def apps_page(data):
    b = []
    a = b.append
    a('<section><div class="wrap"><div class="sec-h"><h1>12차시 웹앱</h1>'
      "<p>차시마다 하나씩, 모두 12개입니다. 선생님이 방 코드를 만들어 나눠 주시면 "
      "학생은 닉네임으로 들어옵니다. 방 코드 없이 혼자 체험하는 길도 있습니다.</p></div>")
    a('<div class="note" style="margin-bottom:22px">실명, 학번, 연락처를 묻지 않습니다. '
      "닉네임만 씁니다. 기록은 학년도가 끝나면 지웁니다.</div>")
    a('<div class="cards">')
    for l in data["lessons"]:
        m = data["modules"][l["module"] - 1]
        a('<a class="card" href="../webapp/%s/index.html"><div class="bar m%d"></div>'
          '<span class="tag m%d">%d차시</span><h3>%s</h3><p>%s</p></a>'
          % (l["id"], m["no"], m["no"], l["no"],
             esc(l["webapp"]["name"]), esc(l["webapp"]["purpose"])))
    a('<a class="card" href="../webapp/common/index.html"><div class="bar m1"></div>'
      '<span class="tag m1">공통</span><h3>사전·사후 자기인식 설문</h3>'
      "<p>1차시 전과 12차시 뒤에 같은 8문항으로 묻고 변화를 봅니다.</p></a>")
    a("</div></div></section>")
    return "".join(b)


def survey_page(data):
    s = data["survey"]
    b = []
    a = b.append
    a('<section><div class="wrap"><div class="sec-h"><h1>%s</h1>'
      "<p>%s 8문항입니다. 1차시 전과 12차시 뒤에 같은 문항으로 묻습니다.</p></div>" % (esc(s["title"]), esc(s["scale"])))
    a('<div class="panel"><div class="scroll"><table>'
      "<tr><th>번호</th><th>문항</th><th>연계 휴먼스킬</th><th>채점</th></tr>")
    for i in s["items"]:
        a("<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (i["no"], esc(i["text"]), esc(i["skill"]), esc(i["scoring"])))
    a("</table></div>")
    a('<div class="note" style="margin-top:16px">%s</div></div>' % esc(s["note"]))
    a('<div class="panel"><h2>자유응답</h2><ul>')
    for o in s["openItems"]:
        a("<li>%s <span style='color:var(--muted)'>(%s)</span></li>" % (esc(o["text"]), esc(o["when"])))
    a("</ul></div>")
    a('<div class="panel"><h2>설문 웹앱</h2>'
      '<div class="dl"><a href="../webapp/common/index.html">설문 웹앱 열기<small>사전·사후 공용</small></a></div></div>')
    a("</div></section>")
    return "".join(b)


def about_page(data):
    prog = data["program"]
    b = []
    a = b.append
    a('<section><div class="wrap"><div class="sec-h"><h1>프로그램 소개</h1></div>')
    a('<div class="panel"><h2>왜 만들었는가</h2>'
      "<p>학생은 생성형 AI를 이미 일상적으로 씁니다. 그런데 언제, 어디까지, 어떻게 쓰는 것이 "
      "적절한지 판단할 기준은 배우지 못한 채 자랍니다. 같은 질문이 네 개 학급에서 반복되었습니다.</p>"
      "<p>이 프로그램은 AI적정활용을 얼마나 쓰는가의 문제가 아니라 "
      "학습자의 사고와 판단을 지키며 적정하게 쓰는가의 문제로 다시 정의합니다. "
      "학생이 열두 시간에 걸쳐 스스로 판단 기준을 세우고 실천하도록 돕습니다.</p></div>")
    a('<div class="panel"><h2>설계의 뼈대</h2><div class="scroll"><table>'
      "<tr><th>토대</th><th>가져온 것</th></tr>"
      "<tr><td>네이버 커넥트재단 휴먼스킬 내용 체계</td>"
      "<td>12역량의 지식·이해 / 과정·기능 / 가치·태도. 중점 7개는 평가에 연결하고 보조 5개는 활동에 분산합니다.</td></tr>"
      "<tr><td>미래교육원 교육정책연구소 AI적정활용</td>"
      "<td>8가지 핵심 구성요소를 7차시 우리 반 AI 약속 8조항으로 옮깁니다.</td></tr>"
      "<tr><td>AI적정활용 델파이 조사</td>"
      "<td>인간다움 우선 원칙과 10대 실행 원칙, 4단계 적용기준을 6차시 4색 신호등으로 옮깁니다.</td></tr>"
      "</table></div></div>")
    a('<div class="panel"><h2>설계 원리</h2><ul>'
      "<li><strong>생각 먼저</strong> : 모든 차시에 내 생각 먼저, AI 검토, 내 말로 재구성의 3단계를 넣습니다.</li>"
      "<li><strong>겪고 나서 판단</strong> : 판단과 약속 활동은 반드시 직접 겪은 경험 뒤에 옵니다.</li>"
      "<li><strong>금지 목록이 아니라 판단 기준</strong> : 하지 말 것의 나열이 아니라 어떤 조건이면 되는가를 담습니다.</li>"
      "<li><strong>모두가 참여하는 설계</strong> : 1인 1기기가 없어도 참여할 수 있는 대안을 전 차시에 마련합니다.</li>"
      "<li><strong>클릭만으로 전개</strong> : 발문, 예상 답변, 도구, 체크리스트를 지도안에 모두 적었습니다.</li>"
      "</ul></div>")
    a('<div class="panel"><h2>우리 반 AI 약속 8조항</h2><div class="scroll"><table>'
      "<tr><th>핵심 구성요소</th><th>학생 언어로 옮긴 약속</th><th>주 연계 차시</th></tr>")
    for c in data["aiComponents"]:
        a("<tr><td>%s %s</td><td>%s</td><td>%d차시</td></tr>"
          % (esc(c["mark"]), esc(c["name"]), esc(c["pledge"]), c["lesson"]))
    a("</table></div></div>")
    a('<div class="panel"><h2>평가 체계</h2><div class="scroll"><table>'
      "<tr><th>역량</th><th>관련 차시</th><th>평가 목표</th><th>평가 방법</th></tr>")
    for p in data["assessmentPlan"]:
        a("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (esc(p["skill"]), esc(", ".join("%d차시" % n for n in p["lessons"])),
             esc(p["goal"]), esc(", ".join(p["method"]))))
    a("</table></div></div>")
    a('<div class="panel"><h2>만든 사람들</h2><p>%s</p><p>%s</p>'
      "<p>적용 학급 : %s</p><p>적용 기간 : %s</p></div>"
      % (esc(prog["team"]), esc(" · ".join(prog["members"])),
         esc(", ".join(prog["classes"])), esc(prog["period"])))
    a("</div></section>")
    return "".join(b)


def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def copy_downloads(data):
    """차시 페이지에서 바로 내려받을 수 있게 산출물을 사이트 안으로 복사한다."""
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
    # 웹앱을 사이트 안으로 복사한다
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

    write(os.path.join(SITE, "apps.html"), page("12차시 웹앱", apps_page(data), 0, "apps.html", data))
    write(os.path.join(SITE, "survey.html"),
          page("AI적정활용 자기인식 진단", survey_page(data), 0, "survey.html", data))
    write(os.path.join(SITE, "about.html"), page("프로그램 소개", about_page(data), 0, "about.html", data))

    n = copy_downloads(data)
    print("사이트를 만들었다 : %s" % SITE)
    print("  페이지 %d개 (홈 1 · 모듈 3 · 차시 12 · 웹앱 1 · 진단 1 · 소개 1), 내려받기 파일 %d개"
          % (1 + 3 + 12 + 3, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
