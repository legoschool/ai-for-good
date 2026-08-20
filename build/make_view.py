# -*- coding: utf-8 -*-
"""화면에서 바로 보는 수업 자료를 만든다.

  out/site/deck/L06.html       넘겨 보는 수업 슬라이드 (PPT 대신 브라우저에서 연다)
  out/site/print/L06_지도안.html  인쇄용 지도안. 발문과 예상 답변까지 전부 담는다
  out/site/print/L06_활동지.html  인쇄용 학생 활동지. 쓰는 칸이 넉넉하다

티처스랩 자료 화면의 결을 따랐다. 크림 바탕, 굵은 검정 테두리, 초록 강조,
둥근 카드, 큰 제목. 그림은 site_art.py 의 인라인 SVG 를 쓴다.
외부 글꼴과 이미지 파일을 참조하지 않는다.
"""
import io
import json
import os
import sys

import site_art as ART
import tasks as T

T.setup_console()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------- 공통 껍데기

BASE_CSS = u"""
:root{--cream:#F4EEE0;--cream-d:#EBE3D2;--paper:#fff;--ink:#101010;--ink2:#33312D;
--muted:#6F6A61;--line:#111;--green:#00D45A;--blue:#2B59E0;--purple:#7B4FE8;--sun:#FFE24B;
--sans:"Pretendard","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",system-ui,sans-serif}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink2);font-family:var(--sans);line-height:1.7}
h1,h2,h3,h4{margin:0;color:var(--ink);line-height:1.25;letter-spacing:-.03em;font-weight:800}
p{margin:0}
a{color:var(--blue)}
.tag{display:inline-block;border:2.5px solid var(--line);border-radius:999px;padding:4px 14px;
font-size:13px;font-weight:800;background:var(--sun)}
.tag.g{background:var(--green)}
.tag.b{background:var(--blue);color:#fff}
.tag.p{background:var(--purple);color:#fff}
.tag.w{background:#fff}
"""

SHOT_DIR = os.path.join("assets", "shots")


def shots_of(lid):
    """build/make_shots.js 가 찍어 둔 화면 목록. 없으면 빈 목록을 준다."""
    path = os.path.join(T.ROOT, "out", "site", "assets", "shots", "index.json")
    if not os.path.exists(path):
        return []
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f).get(lid, [])
    except Exception:
        return []


def teach_shots(lid, limit=6):
    """입장 화면은 따로 쓰고, 활동 화면만 골라 온다."""
    out = [x for x in shots_of(lid) if x.get("name") not in ("입장", "이야기")]
    return out[:limit]


def gate_shot(lid):
    for x in shots_of(lid):
        if x.get("name") == "입장":
            return x
    return None


def qr_img(lid, size=110, rel=".."):
    """웹앱 주소 QR. build/make_qr.py 가 만든 SVG 를 건다."""
    return (u'<img class="qr" src="%s/assets/qr/%s.svg" width="%d" height="%d" '
            u'alt="%s 웹앱 QR 코드">' % (rel, lid, size, size, lid))


DECK_CSS = BASE_CSS + u"""
body{overflow:hidden}
.topbar{position:fixed;left:0;right:0;top:0;height:52px;z-index:20;display:flex;align-items:center;
gap:10px;padding:0 16px;background:var(--cream);border-bottom:3px solid var(--line);flex-wrap:nowrap;
overflow-x:auto}
.topbar a,.topbar span{font-size:14px;font-weight:800;color:var(--ink);white-space:nowrap;
border:2.5px solid var(--line);border-radius:999px;padding:6px 14px;background:#fff;text-decoration:none}
.topbar a:hover{background:var(--sun)}
.topbar .now{background:var(--green);border-color:var(--line)}
.deck{position:relative;height:100vh}
.slide{position:absolute;inset:0;display:none;flex-direction:column;justify-content:center;
padding:calc(52px + 4vh) 7vw 12vh;background:var(--cream)}
.slide.on{display:flex}
.slide .kicker{font-size:clamp(13px,1.5vw,17px);font-weight:800;color:var(--muted);
letter-spacing:.02em;margin-bottom:14px}
.slide h1{font-size:clamp(30px,5.4vw,68px)}
.slide h2{font-size:clamp(24px,3.6vw,46px)}
.slide h3{font-size:clamp(18px,2.1vw,28px)}
.slide p.big{font-size:clamp(18px,2.3vw,32px);font-weight:700;color:var(--ink)}
.slide p.mid{font-size:clamp(15px,1.5vw,21px);margin-top:12px}
.cover{background:var(--cream-d)}
.cover .no{font-size:clamp(46px,9vw,120px);font-weight:900;color:var(--green);
-webkit-text-stroke:3px var(--line);line-height:1}
.art-wrap{margin-top:26px;border:3px solid var(--line);border-radius:20px;overflow:hidden;
background:#fff;max-height:38vh}
.art-wrap svg{display:block;width:100%;height:100%}
.cards{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));margin-top:26px}
.card{border:3px solid var(--line);border-radius:18px;background:var(--paper);padding:20px 22px;
box-shadow:7px 7px 0 var(--line)}
.card h3{font-size:clamp(17px,1.8vw,23px);margin-bottom:8px}
.card p{font-size:clamp(14px,1.35vw,18px);color:var(--ink2)}
.card.sun{background:var(--sun)}
.card.green{background:var(--green)}
.card.white{background:#fff}
.bubble{border:3px solid var(--line);border-radius:26px;background:#fff;padding:22px 26px;
position:relative;margin-top:24px}
.bubble::after{content:"";position:absolute;left:44px;bottom:-18px;width:26px;height:18px;
background:#fff;border-left:3px solid var(--line);border-bottom:3px solid var(--line);
transform:skewX(-24deg)}
.answers{margin-top:30px;display:flex;flex-direction:column;gap:10px}
.answers .a{border:2.5px dashed var(--line);border-radius:16px;background:#fff;padding:12px 18px;
font-size:clamp(14px,1.4vw,19px)}
.answers.hide{display:none}
.rowlist{margin-top:22px;display:flex;flex-direction:column;gap:12px}
.rowlist .r{display:flex;gap:14px;align-items:flex-start;border:2.5px solid var(--line);
border-radius:16px;background:#fff;padding:14px 18px}
.rowlist .r b{background:var(--green);border:2.5px solid var(--line);border-radius:999px;
min-width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px}
.hud{position:fixed;left:0;right:0;bottom:0;height:58px;display:flex;align-items:center;gap:10px;
padding:0 18px;background:var(--paper);border-top:3px solid var(--line);z-index:9}
.hud button{font:inherit;font-size:14px;font-weight:800;border:2.5px solid var(--line);
border-radius:10px;background:#fff;padding:8px 14px;cursor:pointer;min-height:38px}
.hud button:hover{background:var(--sun)}
.hud .count{margin-left:auto;font-weight:800;font-size:14px}
.bar{position:fixed;left:0;top:0;height:6px;background:var(--green);z-index:10;transition:width .2s}
.tap{position:fixed;top:52px;bottom:58px;width:16vw;z-index:8;cursor:pointer;background:transparent}
.tap.l{left:0}
.tap.r{right:0}
@media print{
 body{overflow:visible}
 .deck{height:auto}
 .slide{position:static;display:flex!important;height:190mm;page-break-after:always;border:2px solid var(--line);
 margin-bottom:6mm;padding:14mm}
 .hud,.tap,.bar,.topbar{display:none!important}
 .answers.hide{display:flex}
}
"""

DECK_CSS += u"""
.shot-slide{display:grid;grid-template-columns:1.05fr .95fr;gap:26px;align-items:center;height:100%}
.shot-slide img.cap{width:100%;max-height:74vh;object-fit:contain;border:3px solid #111;
border-radius:14px;background:#fff;box-shadow:8px 8px 0 #111}
.shot-slide .why h2{font-size:38px;margin:0 0 10px}
.shot-slide .why p{font-size:24px;line-height:1.7;margin:8px 0}
.shot-slide .why .do{background:#FFE24B;border:3px solid #111;border-radius:14px;padding:14px 16px;
font-weight:800;font-size:23px;margin-top:14px}
.qrbox{display:flex;gap:18px;align-items:center;margin-top:16px}
.qrbox img{background:#fff;border:3px solid #111;border-radius:12px;padding:6px}
.qrbox b{font-size:26px}
"""

PRINT_CSS = BASE_CSS + u"""
body{background:var(--cream-d);padding:18px}
.sheet{width:210mm;min-height:297mm;margin:0 auto 18px;background:#fff;border:3px solid var(--line);
border-radius:8px;padding:16mm 14mm;font-size:13.5px}
.sheet h1{font-size:26px}
.sheet h2{font-size:18px;margin:22px 0 10px;padding-bottom:6px;border-bottom:3px solid var(--line)}
.sheet h3{font-size:15px;margin:14px 0 6px}
.head{display:flex;gap:16px;align-items:center;border:3px solid var(--line);border-radius:16px;
padding:14px 18px;background:var(--cream)}
.head .no{font-size:34px;font-weight:900;color:var(--green);-webkit-text-stroke:2px var(--line);
line-height:1;min-width:96px}
.head .art{width:150px;border:2.5px solid var(--line);border-radius:12px;overflow:hidden;background:#fff}
.head .art svg{display:block;width:100%;height:84px}
table{width:100%;border-collapse:collapse;margin-top:8px;font-size:12.5px}
th,td{border:1.5px solid var(--line);padding:7px 9px;vertical-align:top;text-align:left}
th{background:var(--cream);font-weight:800;color:var(--ink)}
td.stage{background:var(--sun);font-weight:800;text-align:center;width:52px}
.qa{margin:0 0 6px}
.qa .q{font-weight:800;color:var(--ink)}
.qa .a{color:var(--muted)}
.note{border:2.5px solid var(--line);border-radius:12px;background:var(--sun);padding:12px 14px;
margin-top:12px;font-size:12.5px}
.note.g{background:#E6F7EC}
.note.b{background:#EEF2FF}
ul{margin:6px 0;padding-left:18px}
li{margin:3px 0}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.foot{margin-top:22px;border-top:2px solid var(--line);padding-top:8px;color:var(--muted);font-size:11.5px}

/* 활동지 */
.ws .band{border:3px solid var(--line);border-radius:16px;padding:14px 16px;margin-top:14px;background:#fff}
.ws .band.sun{background:#FFFBEA}
.ws .band.green{background:#F0FCF5}
.ws .band h3{display:flex;gap:8px;align-items:center;font-size:16px}
.ws .band h3 span.n{background:var(--green);border:2.5px solid var(--line);border-radius:999px;
width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;font-size:14px}
.lines{margin-top:10px}
.lines div{border-bottom:1.5px dashed var(--line);height:26px}
.boxes{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(min(140px,100%),1fr));margin-top:10px}
.boxes .b{border:2.5px solid var(--line);border-radius:12px;min-height:74px;padding:8px 10px;
font-size:12px;color:var(--muted)}
.checks{margin-top:10px;display:flex;flex-direction:column;gap:6px}
.checks label{display:flex;gap:8px;align-items:flex-start;font-size:13px}
.checks i{display:inline-block;width:16px;height:16px;border:2.5px solid var(--line);border-radius:4px;
flex:none;margin-top:3px}
.sample{margin-top:8px;border:2px dashed var(--line);border-radius:10px;background:var(--cream);
padding:8px 10px;font-size:12.5px;color:var(--ink2)}
.sample span{display:inline-block;background:var(--sun);border:2px solid var(--line);border-radius:999px;
padding:1px 8px;font-size:11px;font-weight:800;margin-right:8px}
.namebar{display:flex;gap:10px;margin-top:12px}
.namebar div{flex:1;border:2.5px solid var(--line);border-radius:10px;padding:8px 10px;font-size:12px;
color:var(--muted)}
/* 휴대폰에서 종이 너비(210mm)가 화면을 넘겨 가로로 밀리는 것을 막는다.
   인쇄할 때는 아래 @media print 가 다시 종이 크기로 되돌린다. */
@media screen and (max-width:860px){
 body{padding:10px}
 .sheet{width:auto;max-width:100%;min-height:0;padding:18px 14px}
 .toolbar{max-width:100%}
}
@media print{
 body{background:#fff;padding:0}
 .sheet{border:none;border-radius:0;margin:0;width:auto;min-height:auto;padding:10mm 8mm}
 .sheet + .sheet{page-break-before:always}
 .toolbar{display:none}
}
.toolbar{position:sticky;top:0;z-index:20;max-width:210mm;margin:0 auto 12px;display:flex;
gap:8px;flex-wrap:wrap;background:var(--cream-d);padding:10px 0}
.toolbar a,.toolbar button{font:inherit;font-size:14px;font-weight:800;border:2.5px solid var(--line);
border-radius:10px;background:#fff;padding:9px 14px;cursor:pointer;text-decoration:none;color:var(--ink)}
.toolbar a:hover,.toolbar button:hover{background:var(--sun)}
"""


PRINT_CSS += u"""
.appuse{background:#EAF4FF;border:2px solid var(--line);border-radius:10px;padding:8px 10px;
margin:0 0 8px;font-size:12.5px;font-weight:700;color:var(--ink)}
.appuse-s{margin:4px 0 0;font-size:11.5px;font-weight:800;color:var(--blue)}
/* 활동지는 학생이 본다. 초등 5·6학년이 읽을 크기로 키운다. */
.sheet.ws{font-size:16.5px;line-height:1.85}
.ws h1{font-size:32px}
.ws .band{padding:18px 20px;margin-top:18px}
.ws .band h3{font-size:21px;gap:10px}
.ws .band h3 span.n{width:34px;height:34px;font-size:19px}
.ws .band p{font-size:16.5px;line-height:1.8}
.ws .lead{font-size:18px;font-weight:800;color:var(--ink);margin:2px 0 10px}
.ws .sample{font-size:16px;background:#FFFBEA;border:2.5px solid var(--line);border-radius:12px;
padding:10px 12px;margin:10px 0}
.ws .sample span{display:inline-block;background:var(--sun);border:2px solid var(--line);
border-radius:999px;padding:2px 10px;font-size:14px;font-weight:900;margin-right:8px}
.ws .checks label{font-size:17px;gap:10px;align-items:center}
.ws .checks i{width:22px;height:22px;border-radius:6px}
.ws .namebar div{font-size:15px;padding:12px 12px}
.ws .rule{margin:34px 0;border-bottom-width:2.5px}
.ws .rule:first-of-type{margin-top:20px}
.ws .boxes .b{font-size:15px;min-height:78px}
.ws table{font-size:15px}
.ws .appbox{padding:16px 18px}
.ws .appbox p{font-size:14.5px}
@media print{.sheet.ws{font-size:16px}.ws .band h3{font-size:20px}}

.appbox{border:2px solid #111;border-radius:12px;padding:14px 16px;margin:12px 0;background:#FCFBF7}
.appbox .row{display:flex;gap:16px;align-items:center;flex-wrap:wrap}
.appbox img.qr{border:2px solid #111;border-radius:10px;background:#fff;padding:4px}
.appshots{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:10px}
.appshots figure{margin:0}
.appshots img{width:100%;height:150px;object-fit:cover;object-position:top center;
border:2px solid #111;border-radius:10px;background:#fff}
.appshots figcaption{font-size:12px;font-weight:700;margin-top:4px;text-align:center}
@media print{.appshots img{height:120px}}
"""


def shell(title, css, body, script=""):
    return u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<style>%s</style>
</head>
<body>
%s
<script>%s</script>
</body>
</html>
""" % (esc(title), css, body, script)


FOOT = u"2026년 티처스랩 5기 교사연구회 A.N.D · CC BY-NC-SA"


# ---------------------------------------------------------------- 슬라이드

DECK_JS = u"""
(function(){
  var slides = document.querySelectorAll(".slide");
  var i = 0, notes = false;
  function paint(){
    for (var k = 0; k < slides.length; k++) {
      slides[k].className = "slide" + (slides[k].getAttribute("data-kind") === "cover" ? " cover" : "") +
        (k === i ? " on" : "");
    }
    document.getElementById("count").textContent = (i + 1) + " / " + slides.length;
    document.getElementById("bar").style.width = ((i + 1) * 100 / slides.length) + "%";
    var ans = document.querySelectorAll(".answers");
    for (var a = 0; a < ans.length; a++) {
      ans[a].className = "answers" + (notes ? "" : " hide");
    }
    if (location.hash !== "#" + (i + 1)) { history.replaceState(null, "", "#" + (i + 1)); }
  }
  function go(n){ i = Math.max(0, Math.min(slides.length - 1, n)); paint(); }
  document.getElementById("prev").onclick = function(){ go(i - 1); };
  document.getElementById("next").onclick = function(){ go(i + 1); };
  document.getElementById("tapl").onclick = function(){ go(i - 1); };
  document.getElementById("tapr").onclick = function(){ go(i + 1); };
  document.getElementById("notes").onclick = function(){
    notes = !notes;
    this.textContent = notes ? "예상 답변 숨기기" : "예상 답변 보기";
    paint();
  };
  document.getElementById("full").onclick = function(){
    if (document.fullscreenElement) { document.exitFullscreen(); }
    else if (document.documentElement.requestFullscreen) { document.documentElement.requestFullscreen(); }
  };
  document.getElementById("print").onclick = function(){ window.print(); };
  document.onkeydown = function(e){
    var k = e.key;
    if (k === "ArrowRight" || k === " " || k === "PageDown") { go(i + 1); e.preventDefault(); }
    else if (k === "ArrowLeft" || k === "PageUp") { go(i - 1); e.preventDefault(); }
    else if (k === "Home") { go(0); }
    else if (k === "End") { go(slides.length - 1); }
    else if (k === "n" || k === "N") { document.getElementById("notes").click(); }
    else if (k === "f" || k === "F") { document.getElementById("full").click(); }
  };
  var x0 = null;
  document.addEventListener("touchstart", function(e){ x0 = e.touches[0].clientX; });
  document.addEventListener("touchend", function(e){
    if (x0 === null) { return; }
    var dx = e.changedTouches[0].clientX - x0;
    if (dx < -50) { go(i + 1); } else if (dx > 50) { go(i - 1); }
    x0 = null;
  });
  var start = Number((location.hash || "#1").slice(1));
  go(isNaN(start) ? 0 : start - 1);
})();
"""


def slide(kind, inner):
    return u'<section class="slide%s" data-kind="%s">%s</section>' % (
        " cover" if kind == "cover" else "", kind, inner)


def qa_slide(kicker, heading, turns):
    b = [u'<p class="kicker">%s</p><h2>%s</h2>' % (esc(kicker), esc(heading))]
    for t in turns:
        b.append(u'<div class="bubble"><p class="big">%s</p></div>' % esc(t["q"]))
        if t.get("a"):
            b.append(u'<div class="answers hide">')
            for ans in t["a"]:
                b.append(u'<div class="a">예상 답변 · %s</div>' % esc(ans))
            b.append(u"</div>")
    return slide("ask", "".join(b))


def app_slides(lesson):
    """웹앱을 어떻게 쓰는지 화면 캡처로 보여 준다. 지도안 흐름 끝에 붙는다.
    한 차시에 열 장 안쪽으로 만든다. 교사가 화면을 띄워 놓고 그대로 따라 하면 된다."""
    lid = lesson["id"]
    w = lesson["webapp"]
    out = []
    gate = gate_shot(lid)
    shots = teach_shots(lid, 6)
    if not gate and not shots:
        return out

    out.append(slide("q",
                     u'<p class="kicker">웹앱으로 합니다</p><h1>%s</h1>'
                     u'<p class="mid">%s</p>'
                     u'<div class="qrbox">%s<div><b>수업 전에 방을 만듭니다.</b>'
                     u'<p style="font-size:22px;margin-top:6px">선생님 화면 → 새 방 만들기 → '
                     u'여섯 자리 방 번호를 칠판에 적습니다.</p>'
                     u'<p style="font-size:20px;color:#6F6A61">학생은 QR 을 찍거나 주소를 열고 '
                     u'방 번호와 닉네임을 넣습니다.</p></div></div>'
                     % (esc(w["name"]), esc(w["purpose"]), qr_img(lid, 150))))

    if gate:
        out.append(slide("shot",
                         u'<div class="shot-slide"><img class="cap" src="../assets/shots/%s" alt="입장 화면">'
                         u'<div class="why"><h2>학생 입장 화면</h2>'
                         u'<p>방 번호 여섯 자리와 닉네임만 넣습니다. 이름을 묻지 않습니다.</p>'
                         u'<p>나만 아는 숫자 네 자리는 사전 설문과 사후 설문을 잇는 데만 씁니다.</p>'
                         u'<div class="do">기기가 없으면 둘러보기로 교사가 시연합니다.</div></div></div>'
                         % esc(gate["file"])))

    for i, sh in enumerate(shots):
        step = w["screens"][i] if i < len(w["screens"]) else sh["name"]
        out.append(slide("shot",
                         u'<div class="shot-slide"><img class="cap" src="../assets/shots/%s" alt="%s 화면">'
                         u'<div class="why"><p class="kicker">웹앱 %d단계</p><h2>%s</h2>'
                         u'<p>%s</p>'
                         u'<div class="do">학생이 여기서 남긴 것이 활동지 %d번 칸과 이어집니다.</div>'
                         u'</div></div>'
                         % (esc(sh["file"]), esc(sh["name"]), i + 1, esc(sh["name"]),
                            esc(step), min(i + 1, 4))))

    out.append(slide("q",
                     u'<p class="kicker">교사 화면</p><h1>제출이 실시간으로 모입니다</h1>'
                     u'<p class="mid">%s</p>'
                     u'<p style="font-size:22px">결과 크게 띄우기를 누르면 학급 화면으로 함께 봅니다. '
                     u'CSV 로 내려받고, 수업이 끝나면 방을 잠급니다.</p>'
                     % esc(w.get("teacherView", "학급 집계를 봅니다."))))
    return out


def deck(lesson, data):
    m = data["modules"][lesson["module"] - 1]
    w = lesson["webapp"]
    s = []

    s.append(slide("cover",
                   u'<p class="kicker">%s · 모듈%d %s</p>'
                   u'<p class="no">%02d</p><h1>%s</h1>'
                   u'<p class="mid">%s</p>'
                   u'<div class="art-wrap">%s</div>'
                   % (esc(data["program"]["name"]), m["no"], esc(m["name"]),
                      lesson["no"], esc(lesson["title"]), esc(lesson["problem"]),
                      ART.lesson_art(lesson["no"]))))

    s.append(slide("q",
                   u'<p class="kicker">오늘의 학습 문제</p><h1>%s</h1>'
                   u'<p class="mid">AI는 내 생각을 도와주는가, 아니면 대신해 주는가</p>'
                   % esc(lesson["problem"])))

    focus = lesson["humanSkills"]["focus"]
    cards = "".join(
        u'<div class="card%s"><h3>%s</h3><p>%s</p></div>'
        % ([" sun", " white", " green"][k % 3], esc(f["name"]), esc(f["process"]))
        for k, f in enumerate(focus))
    cards += (u'<div class="card white"><h3>AI적정활용</h3><p>%s</p></div>'
              % esc(" / ".join(lesson["aiComponents"])))
    s.append(slide("cards", u'<p class="kicker">오늘 기르는 힘</p>'
                            u'<h2>이 시간에 자라는 생각</h2><div class="cards">%s</div>' % cards))

    for label, key in [("도입", "intro"), ("전개", "develop"), ("정리", "close")]:
        stage = lesson["plan"][key]
        s.append(slide("stage",
                       u'<p class="kicker">%s · %d분</p><h1>%s</h1>'
                       u'<div class="rowlist">%s</div>'
                       % (label, stage["minutes"],
                          esc(stage["blocks"][0]["heading"] if stage["blocks"] else label),
                          "".join(u'<div class="r"><b>%d</b><span>%s</span></div>'
                                  % (n + 1, esc(blk["heading"]))
                                  for n, blk in enumerate(stage["blocks"])))))
        for blk in stage["blocks"]:
            if blk.get("turns"):
                s.append(qa_slide("%s · %s" % (label, blk["heading"]), blk["heading"], blk["turns"]))

        s.append(slide("mat",
                       u'<p class="kicker">%s 준비물과 유의점</p><h2>이것만 챙기면 됩니다</h2>'
                       u'<div class="cards">%s</div>'
                       % (label, "".join(u'<div class="card white"><p>%s</p></div>' % esc(x)
                                         for x in stage["materials"]))))

    s.append(slide("app",
                   u'<p class="kicker">오늘 쓰는 웹앱</p><h1>%s</h1><p class="mid">%s</p>'
                   u'<div class="cards">'
                   u'<div class="card sun"><h3>1. 방 만들기</h3><p>선생님 화면에서 여섯 자리 코드를 만들어요.</p></div>'
                   u'<div class="card white"><h3>2. 들어오기</h3><p>코드와 비밀번호, 닉네임만 쓰면 돼요.</p></div>'
                   u'<div class="card green"><h3>3. 활동과 제출</h3><p>고쳐서 다시 제출해도 괜찮아요.</p></div>'
                   u'<div class="card white"><h3>4. 함께 보기</h3><p>결과 크게 띄우기로 우리 반 결과를 봐요.</p></div>'
                   u'</div>' % (esc(w["name"]), esc(w["purpose"]))))

    if w.get("steps"):
        rows = "".join(u'<div class="r"><b>%d</b><span><strong>%s</strong> · %d분<br>%s</span></div>'
                       % (st["no"], esc(st["title"]), st["minutes"], esc(st["what"]))
                       for st in w["steps"])
        s.append(slide("steps", u'<p class="kicker">웹앱으로 40분 쓰기</p>'
                                u'<h2>이 순서로 진행합니다</h2><div class="rowlist">%s</div>' % rows))

    ws = lesson["worksheet"]
    s.append(slide("ws",
                   u'<p class="kicker">활동지</p><h1>%s</h1><div class="rowlist">%s</div>'
                   % (esc(ws["title"]),
                      "".join(u'<div class="r"><b>%d</b><span>%s</span></div>'
                              % (n + 1, esc(sec["title"] if isinstance(sec, dict) else sec))
                              for n, sec in enumerate(ws["sections"])))))

    s.append(slide("alt",
                   u'<p class="kicker">기기가 부족해도 함께합니다</p><h2>이렇게 대신합니다</h2>'
                   u'<div class="bubble"><p class="big">%s</p></div>' % esc(lesson["alternative"])))

    s.append(slide("care",
                   u'<p class="kicker">지도 유의점</p><h2>선생님이 지켜 주실 것</h2>'
                   u'<div class="cards">%s</div>'
                   % "".join(u'<div class="card white"><p>%s</p></div>' % esc(c)
                             for c in lesson["cautions"])))

    nxt = None
    for other in data["lessons"]:
        if other["no"] == lesson["no"] + 1:
            nxt = other
    s.append(slide("end",
                   u'<p class="kicker">오늘 여기까지</p><h1>%s</h1><p class="mid">%s</p>'
                   u'<p class="mid" style="margin-top:26px">%s</p>'
                   % ("다음 시간에는" if nxt else "열두 시간을 마쳤습니다",
                      esc(nxt["title"]) if nxt else esc(data["program"]["name"]),
                      esc(FOOT))))

    hud = (u'<div class="bar" id="bar"></div>'
           u'<div class="tap l" id="tapl"></div><div class="tap r" id="tapr"></div>'
           u'<div class="hud">'
           u'<button id="prev">이전</button><button id="next">다음</button>'
           u'<button id="notes">예상 답변 보기</button>'
           u'<button id="full">전체 화면</button>'
           u'<button id="print">인쇄</button>'
           u'<span class="count" id="count"></span></div>')

    prev_l = None
    next_l = None
    for other in data["lessons"]:
        if other["no"] == lesson["no"] - 1:
            prev_l = other
        if other["no"] == lesson["no"] + 1:
            next_l = other
    app = app_slides(lesson)
    if app:
        at = len(s)
        for k, one in enumerate(s):
            if "전개 · 30분" in one or "전개 ·" in one:
                at = k
                break
        s[at:at] = app

    bar = (u'<nav class="topbar">'
           u'<a href="../index.html">WISE 홈</a>'
           u'<a href="../browse.html">둘러보기</a>'
           u'<a href="../lesson/%s.html">%d차시 페이지</a>'
           u'<a href="../webapp/%s/index.html">웹앱 열기</a>'
           u'<a href="../print/%s_지도안.html">지도안</a>'
           u'<a href="../print/%s_활동지.html">활동지</a>'
           u'%s%s'
           u'<span class="now">%d차시 슬라이드</span></nav>'
           % (lesson["id"], lesson["no"], lesson["id"], lesson["id"], lesson["id"],
              (u'<a href="%s.html">앞 차시</a>' % prev_l["id"]) if prev_l else "",
              (u'<a href="%s.html">다음 차시</a>' % next_l["id"]) if next_l else "",
              lesson["no"]))
    body = bar + u'<div class="deck">%s</div>%s' % ("".join(s), hud)
    return shell(u"%d차시 수업 슬라이드 · %s" % (lesson["no"], lesson["shortTitle"]),
                 DECK_CSS, body, DECK_JS)


# ---------------------------------------------------------------- 인쇄용 지도안

def toolbar(links):
    return (u'<div class="toolbar">%s<button onclick="window.print()">인쇄하기</button></div>'
            % "".join(u'<a href="%s">%s</a>' % (href, esc(label)) for href, label in links))


def app_screens(lesson):
    """전개 활동 순서대로 웹앱 화면을 짝지어 준다.
    활동이 더 많으면 마지막 화면을 이어 쓰고, 화면이 더 많으면 남는 것은 웹앱 운영 칸에서 본다."""
    names = lesson["webapp"].get("screens", [])
    blocks = lesson["plan"]["develop"]["blocks"]
    out = []
    for i in range(len(blocks)):
        if not names:
            out.append(None)
            continue
        k = min(i, len(names) - 1)
        out.append((names[k],
                    u"학생이 여기에 남긴 것이 활동지 %d번 칸이 된다." % (k + 1)))
    return out


def stage_rows(label, stage, lesson=None, screens=None):
    rows = []
    for bi, blk in enumerate(stage["blocks"]):
        qa = []
        for t in blk.get("turns", []):
            qa.append(u'<div class="qa"><p class="q">발문 · %s</p>%s</div>'
                      % (esc(t["q"]),
                         "".join(u'<p class="a">예상 답변 · %s</p>' % esc(a) for a in t.get("a", []))))
        app = ""
        if screens and bi < len(screens) and screens[bi]:
            app = (u'<p class="appuse"><b>★ 웹앱</b> %s 화면 · %s</p>'
                   % (esc(screens[bi][0]), esc(screens[bi][1])))
        rows.append(u'<tr><td class="stage">%s</td><td><strong>%s</strong>%s</td><td>%s</td></tr>'
                    % (esc(label), esc(blk["heading"]), "",
                       (app + "".join(qa)) or "&nbsp;"))
        label = ""
    rows.append(u'<tr><td class="stage">%s</td><td>준비물과 유의점</td><td><ul>%s</ul></td></tr>'
                % ("", "".join(u"<li>%s</li>" % esc(x) for x in stage["materials"])))
    return "".join(rows)


def objectives(lesson):
    """학습 목표 세 줄. 중점 역량의 지식·기능·태도에서 뽑는다."""
    f = lesson["humanSkills"]["focus"][0]
    g = lesson["humanSkills"]["focus"][-1]
    return [
        u"%s (지식·이해)" % f["knowledge"].rstrip("."),
        u"%s (과정·기능)" % f["process"].rstrip("."),
        u"%s (가치·태도)" % g["value"].rstrip("."),
    ]


def minute_plan(lesson):
    """분 단위 진행표. 전개 시간을 활동 수로 나눈다."""
    rows = []
    t = 0
    intro = lesson["plan"]["intro"]
    rows.append((t, intro["minutes"], u"도입", intro["blocks"][0]["heading"] if intro["blocks"] else u"동기 유발"))
    t += intro["minutes"]
    dev = lesson["plan"]["develop"]
    blocks = dev["blocks"] or [{"heading": u"활동"}]
    each = max(5, int(round(float(dev["minutes"]) / len(blocks) / 5.0)) * 5)
    left = dev["minutes"]
    for i, blk in enumerate(blocks):
        span = each if i < len(blocks) - 1 else max(5, left)
        span = min(span, left)
        rows.append((t, span, u"전개 %d" % (i + 1), blk["heading"]))
        t += span
        left -= span
    close = lesson["plan"]["close"]
    rows.append((t, close["minutes"], u"정리",
                 close["blocks"][0]["heading"] if close["blocks"] else u"되돌아보기"))
    return rows


def rubric(lesson):
    """중점 역량별 평가 기준. 잘함 · 보통 · 도움 필요 세 칸이다."""
    out = []
    for f in lesson["humanSkills"]["focus"]:
        base = f["process"].rstrip(".")
        out.append((f["name"],
                    u"%s. 스스로 해내고 그렇게 판단한 까닭을 설명한다" % base,
                    u"%s. 친구나 교사의 도움을 조금 받아 해낸다" % base,
                    u"%s. 예시를 함께 보며 한 단계씩 따라 한다" % base))
    return out


TROUBLE = [
    (u"기기가 모자란다", u"모둠에 한 대만 두고 기록 담당을 정한다. 판단은 모둠이 함께 하고 입력만 한 사람이 한다."),
    (u"인터넷이 끊긴다", u"쓰던 내용은 그 기기에 남는다. 활동지에 먼저 쓰게 하고 연결이 돌아오면 제출한다."),
    (u"방 코드를 잃어버렸다", u"선생님 화면에서 기존 방 열기를 누르고 코드를 넣으면 다시 열린다."),
    (u"닉네임이 겹친다", u"막지 않는다. 뒤에 낸 제출이 반영되므로 닉네임 뒤에 숫자를 붙이게 한다."),
    (u"의견이 한쪽으로 쏠린다", u"소수 의견을 먼저 듣는다. 결과 크게 띄우기로 분포를 보여 주고 까닭을 묻는다."),
    (u"시간이 모자란다", u"활동 하나를 줄이고 정리 발문은 반드시 남긴다. 남은 활동은 활동지로 마무리한다."),
]


def board_plan(lesson):
    """칠판에 그대로 옮겨 적을 판서 계획."""
    dev = lesson["plan"]["develop"]["blocks"]
    close = lesson["plan"]["close"]["blocks"]
    lines_out = [u"학습 문제 : %s" % lesson["problem"]]
    for i, blk in enumerate(dev):
        head = blk["heading"]
        if head.startswith(u"[활동"):
            head = head.split(u"]", 1)[-1].strip()
        lines_out.append(u"활동 %d. %s" % (i + 1, head))
    if close and close[0].get("turns"):
        lines_out.append(u"정리 : %s" % close[0]["turns"][0]["q"])
    lines_out.append(u"오늘 쓰는 웹앱 : %s" % lesson["webapp"]["name"])
    return lines_out


def app_box(lesson, rel="..", limit=3):
    """지도안과 활동지 위쪽에 붙는 웹앱 안내 상자. QR, 주소, 화면 캡처."""
    lid = lesson["id"]
    w = lesson["webapp"]
    shots = teach_shots(lid, limit)
    figs = "".join(
        u'<figure><img src="%s/assets/shots/%s" alt="%s 화면"><figcaption>%s</figcaption></figure>'
        % (rel, esc(x["file"]), esc(x["name"]), esc(x["name"])) for x in shots)
    return (u'<div class="appbox"><div class="row">%s'
            u'<div style="flex:1;min-width:min(220px,100%%)"><strong>★ 웹앱 %s</strong>'
            u'<p style="margin:4px 0">%s</p>'
            u'<p style="margin:4px 0;font-size:13px">주소 : legoschool.github.io/wise-ai/webapp/%s/'
            u' · <a href="%s/webapp/%s/index.html">바로 열기</a>'
            u' · <a href="%s/guide/%s.html">사용 안내</a></p>'
            u'<p style="margin:4px 0;font-size:13px">수업 전에 <b>선생님 화면 → 새 방 만들기</b>로 '
            u'방 번호를 만들고 칠판에 적습니다. 학생은 QR 을 찍어 들어옵니다.</p></div></div>'
            u'<div class="appshots">%s</div></div>'
            % (qr_img(lid, 104, rel), esc(w["name"]), esc(w["purpose"]), lid,
               rel, lid, rel, lid, figs))


def plan_html(lesson, data):
    m = data["modules"][lesson["module"] - 1]
    w = lesson["webapp"]
    b = []
    a = b.append
    a(toolbar([("../index.html", "WISE 홈"),
               ("../lesson/%s.html" % lesson["id"], "%d차시 페이지" % lesson["no"]),
               ("../deck/%s.html" % lesson["id"], "수업 슬라이드"),
               ("%s_활동지.html" % lesson["id"], "활동지"),
               ("../webapp/%s/index.html" % lesson["id"], "웹앱")]))
    a(u'<div class="sheet">')
    a(u'<div class="head"><div class="no">%02d</div>'
      u'<div style="flex:1"><h1>%s</h1>'
      u'<p style="margin-top:6px">%s</p>'
      u'<div class="meta"><span class="tag g">모듈%d %s</span><span class="tag">%s</span>'
      u'<span class="tag w">%s</span></div></div>'
      u'<div class="art">%s</div></div>'
      % (lesson["no"], esc(lesson["title"]), esc(lesson["problem"]),
         m["no"], esc(m["name"]), esc(lesson["subject"]),
         esc(", ".join(lesson["tools"])[:40]), ART.lesson_art(lesson["no"])))

    a(app_box(lesson))

    a(u"<h2>1. 학습 목표</h2><ul>%s</ul>"
      % "".join(u"<li>%s</li>" % esc(o) for o in objectives(lesson)))
    a(u'<div class="note g"><strong>이 시간의 핵심</strong> 학생이 스스로 판단하고 그 까닭을 말하게 합니다. '
      u'교사가 정답을 먼저 말하지 않습니다. 판단이 갈리는 자리가 이 수업의 알맹이입니다.</div>')

    a(u"<h2>2. 시간 배분</h2><table>"
      u"<tr><th style='width:90px'>시각</th><th style='width:70px'>단계</th>"
      u"<th style='width:56px'>시간</th><th>무엇을 하나</th></tr>")
    for start, span, label, what in minute_plan(lesson):
        a(u"<tr><td>%d분 ~ %d분</td><td class='stage'>%s</td><td>%d분</td><td>%s</td></tr>"
          % (start, start + span, esc(label), span, esc(what)))
    a(u"</table>")

    a(u"<h2>3. 이 시간에 기르는 힘</h2><table>"
      u"<tr><th style='width:120px'>중점 역량</th><th>지식·이해</th><th>과정·기능</th><th>가치·태도</th></tr>")
    for f in lesson["humanSkills"]["focus"]:
        a(u"<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (esc(f["name"]), esc(f["knowledge"]), esc(f["process"]), esc(f["value"])))
    a(u"</table>")
    if lesson["humanSkills"].get("support"):
        a(u'<p style="margin-top:6px;color:var(--muted);font-size:12px">보조 역량 : %s</p>'
          % esc(", ".join(lesson["humanSkills"]["support"])))
    a(u'<div class="note b"><strong>AI적정활용 기준</strong> %s<br><strong>실행 원칙</strong> %s</div>'
      % (esc(" / ".join(lesson["aiComponents"])), esc(" / ".join(lesson["aiPrinciples"]))))

    a(u"<h2>4. 교수·학습 과정</h2><table>"
      u"<tr><th style='width:52px'>단계</th><th style='width:150px'>학습 내용</th>"
      u"<th>교사 발문과 예상 답변</th></tr>")
    a(stage_rows("도입 %d분" % lesson["plan"]["intro"]["minutes"], lesson["plan"]["intro"]))
    a(stage_rows("전개 %d분" % lesson["plan"]["develop"]["minutes"], lesson["plan"]["develop"],
                 lesson, app_screens(lesson)))
    a(stage_rows("정리 %d분" % lesson["plan"]["close"]["minutes"], lesson["plan"]["close"]))
    a(u"</table>")

    a(u"<h2>5. 판서 계획</h2>")
    a(u'<div class="note b">%s</div>'
      % "<br>".join(esc(x) for x in board_plan(lesson)))

    a(u"<h2>6. 웹앱 운영</h2>")
    a(u'<p><strong>%s</strong> · %s</p>' % (esc(w["name"]), esc(w["purpose"])))
    a(u"<ul>%s</ul>" % "".join(u"<li>%s</li>" % esc(x) for x in w["screens"]))
    if w.get("steps"):
        a(u"<table><tr><th style='width:40px'>순서</th><th style='width:120px'>단계</th>"
          u"<th style='width:44px'>시간</th><th>무엇을 하나</th><th>교사 발문</th></tr>")
        for st in w["steps"]:
            a(u"<tr><td>%d</td><td><strong>%s</strong></td><td>%d분</td><td>%s</td>"
              u"<td>%s<br><span style='color:var(--muted)'>%s</span></td></tr>"
              % (st["no"], esc(st["title"]), st["minutes"], esc(st["what"]),
                 esc(st["ask"]), esc(st["expect"])))
        a(u"</table>")
    a(u'<div class="note g"><strong>교사 화면</strong> %s<br>'
      u'<strong>방 만들기</strong> 선생님 화면 → 새 방 만들기 → 여섯 자리 코드를 복사해 학생에게 알려 줍니다. '
      u'수업이 끝나면 방 잠그기를 누릅니다.</div>' % esc(w.get("teacherView", "")))

    a(u"<h2>7. 기기가 없어도 함께하는 길</h2>")
    a(u'<div class="note">%s</div>' % esc(lesson["alternative"]))

    a(u"<h2>8. 지도 유의점</h2><ul>%s</ul>"
      % "".join(u"<li>%s</li>" % esc(c) for c in lesson["cautions"]))
    a(u'<div class="note"><strong>개인정보 지도</strong> 이름, 사진, 친구 이야기를 넣지 않도록 '
      u'활동 전에 한 번 짚어 줍니다. 웹앱은 닉네임만 받고 실명과 학번을 묻지 않습니다.</div>')

    a(u"<h2>9. 학생 활동지 작성 예시</h2>")
    a(u'<p style="font-size:12.5px;color:var(--muted)">활동지에도 같은 예시가 실려 있습니다. '
      u'무엇을 쓰는지 먼저 보여 준 뒤 학생이 자기 말로 바꾸게 합니다.</p><table>'
      u"<tr><th style='width:170px'>활동지 칸</th><th>학생 작성 예시</th></tr>")
    ws_secs = lesson["worksheet"]["sections"]
    samples = ws_examples(lesson, len(ws_secs))
    for i, sec in enumerate(ws_secs):
        title = sec["title"] if isinstance(sec, dict) else str(sec)
        a(u"<tr><td><strong>%d. %s</strong></td><td>%s</td></tr>"
          % (i + 1, esc(title), esc(samples[i] or u"자기 경험으로 쓰게 합니다")))
    a(u"</table>")

    a(u"<h2>10. 자주 나오는 어려움과 대처</h2><table>"
      u"<tr><th style='width:150px'>이런 일이 생기면</th><th>이렇게 합니다</th></tr>")
    for what, how in TROUBLE:
        a(u"<tr><td><strong>%s</strong></td><td>%s</td></tr>" % (esc(what), esc(how)))
    a(u"</table>")

    a(u"<h2>11. 평가 기준</h2><table>"
      u"<tr><th style='width:110px'>역량</th><th>잘함</th><th>보통</th><th>도움 필요</th></tr>")
    for name, hi, mid, low in rubric(lesson):
        a(u"<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s</td></tr>"
          % (esc(name), esc(hi), esc(mid), esc(low)))
    a(u"</table>")
    a(u'<div class="note g"><strong>무엇을 보고 판단하나</strong> 웹앱 교사 화면의 제출 기록과 활동지, '
      u'그리고 판단이 갈린 자리에서 학생이 든 까닭을 함께 봅니다. 정답을 맞혔는지가 아니라 '
      u'까닭을 댈 수 있는지를 봅니다.</div>')

    a(u"<h2>12. 산출물과 교육과정</h2><table>"
      u"<tr><th style='width:130px'>성취기준</th><td>%s</td></tr>"
      u"<tr><th>학생 산출물</th><td>%s</td></tr>"
      u"<tr><th>평가 방법</th><td>%s</td></tr>"
      u"<tr><th>수업 도구</th><td>%s</td></tr></table>"
      % (esc(" ".join(lesson["standards"])), esc(", ".join(lesson["outputs"])),
         esc(", ".join(lesson["assessment"])), esc(", ".join(lesson["tools"]))))

    a(u'<p class="foot">%s · %s</p>' % (esc(data["program"]["name"]), esc(FOOT)))
    a(u"</div>")
    return shell(u"%d차시 지도안 · %s" % (lesson["no"], lesson["shortTitle"]),
                 PRINT_CSS, "".join(b))


# ---------------------------------------------------------------- 인쇄용 활동지

def lines(n):
    return u'<div class="lines">%s</div>' % ("<div></div>" * n)


def ws_examples(lesson, n):
    """활동지 칸마다 붙일 예시문. 그 차시의 예상 답변을 학생 말로 그대로 쓴다."""
    answers = []
    for key in ("develop", "intro", "close"):
        for blk in lesson["plan"][key]["blocks"]:
            for t in blk.get("turns", []):
                for a in t.get("a", []):
                    if a not in answers:
                        answers.append(a)
    out = []
    for i in range(n):
        out.append(answers[i] if i < len(answers) else "")
    return out


def ws_hints(lesson, n):
    """활동지 칸마다 붙일 안내문. 그 차시의 실제 발문에서 가져온다."""
    asks = []
    for key in ("develop", "intro", "close"):
        for blk in lesson["plan"][key]["blocks"]:
            for t in blk.get("turns", []):
                asks.append(t["q"])
    out = []
    for i in range(n):
        out.append(asks[i] if i < len(asks) else u"내 생각을 먼저 쓰고, 그다음에 확인한 것을 씁니다.")
    return out


def worksheet_html(lesson, data):
    ws = lesson["worksheet"]
    w = lesson["webapp"]
    b = []
    a = b.append
    a(toolbar([("../index.html", "WISE 홈"),
               ("../lesson/%s.html" % lesson["id"], "%d차시 페이지" % lesson["no"]),
               ("%s_지도안.html" % lesson["id"], "지도안"),
               ("../deck/%s.html" % lesson["id"], "수업 슬라이드"),
               ("../webapp/%s/index.html" % lesson["id"], "웹앱")]))
    a(u'<div class="sheet ws">')
    a(u'<div class="head"><div class="no">%02d</div>'
      u'<div style="flex:1"><h1>%s</h1><p style="margin-top:6px">%s</p></div>'
      u'<div class="art">%s</div></div>'
      % (lesson["no"], esc(ws["title"]), esc(lesson["problem"]), ART.lesson_art(lesson["no"])))
    a(u'<div class="namebar"><div>학교</div><div>학년 반</div><div>번호</div><div>닉네임</div></div>')
    a(u'<div class="note"><strong>오늘의 약속</strong> 이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요. '
      u'웹앱에는 닉네임만 씁니다. 웹앱 이름은 <strong>%s</strong> 입니다.</div>' % esc(w["name"]))
    a(app_box(lesson, "..", 2))

    a(u'<div class="band sun"><h3>오늘 할 일</h3>'
      u'<p class="lead">%s</p><div class="checks">%s</div></div>'
      % (esc(lesson["problem"]),
         "".join(u'<label><i></i>%s</label>' % esc(blk["heading"])
                 for blk in lesson["plan"]["develop"]["blocks"])))

    hints = ws_hints(lesson, len(ws["sections"]))
    samples = ws_examples(lesson, len(ws["sections"]))
    tone = ["", "green", "", "sun"]
    box_words = [u"카드", u"분류", u"목록", u"후보", u"가지", u"세 개", u"모은", u"역할", u"약속"]
    for i, sec in enumerate(ws["sections"]):
        title = sec["title"] if isinstance(sec, dict) else str(sec)
        hint = (sec.get("hint", "") if isinstance(sec, dict) else "") or hints[i]
        kind = sec.get("kind", "") if isinstance(sec, dict) else ""
        numbered = title[:1].isdigit()
        a(u'<div class="band %s"><h3>%s%s</h3>'
          % (tone[i % 4], "" if numbered else u'<span class="n">%d</span>' % (i + 1), esc(title)))
        if hint:
            a(u'<p class="lead">%s</p>' % esc(hint))
        if samples[i]:
            a(u'<p class="sample"><span>예시</span>%s</p>' % esc(samples[i]))
        wants_boxes = kind == "boxes" or any(w in title for w in box_words)
        if wants_boxes:
            a(u'<div class="boxes"><div class="b">여기에 써요</div><div class="b">여기에 써요</div>'
              u'<div class="b">여기에 써요</div><div class="b">여기에 써요</div></div>')
            a(lines(2))
        else:
            a(lines(6))
        a(u"</div>")

    a(u'<div class="band"><h3><span class="n">%d</span>오늘의 되돌아보기</h3>'
      u'<div class="checks">'
      u'<label><i></i>내 생각을 먼저 쓰고 나서 AI에게 물었다</label>'
      u'<label><i></i>AI가 알려 준 것을 확인했다</label>'
      u'<label><i></i>개인정보를 넣지 않았다</label>'
      u'<label><i></i>AI가 한 일과 내가 한 일을 밝힐 수 있다</label>'
      u'</div>%s</div>' % (len(ws["sections"]) + 1, lines(2)))

    a(u'<p class="foot">%s · %s</p>' % (esc(data["program"]["name"]), esc(FOOT)))
    a(u"</div>")
    return shell(u"%d차시 활동지 · %s" % (lesson["no"], ws["title"]),
                 PRINT_CSS, "".join(b))


# ---------------------------------------------------------------- 쓰기

def write(path, text):
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def build_all(data, site):
    n = 0
    for l in data["lessons"]:
        write(os.path.join(site, "deck", "%s.html" % l["id"]), deck(l, data))
        write(os.path.join(site, "print", "%s_지도안.html" % l["id"]), plan_html(l, data))
        write(os.path.join(site, "print", "%s_활동지.html" % l["id"]), worksheet_html(l, data))
        n += 3
    return n


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    n = build_all(data, site)
    print("화면용 자료 %d쪽을 만들었다 : %s" % (n, site))
    return 0


if __name__ == "__main__":
    sys.exit(main())
