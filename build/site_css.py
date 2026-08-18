# -*- coding: utf-8 -*-
"""통합 사이트 공통 스타일.

크림 바탕에 손그림 느낌의 검은 테두리, 왼쪽이 톱니로 파인 티켓 카드,
형광 초록 버튼, 초록 점 타임라인, 파란 해시태그를 쓴다.
단일 톤으로 못 박은 디자인이라 다크 모드를 만들지 않는다.
교실 프로젝터에서 어두운 화면은 보이지 않기 때문이다.
"""

NOISE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
         "width='220' height='220'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
         "type='fractalNoise' baseFrequency='0.85' numOctaves='4'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")")

CSS = u"""/* WISE 통합 사이트 */

:root{
  --cream:#F4EEE0;
  --cream-d:#EBE3D2;
  --paper:#FFFFFF;
  --ink:#101010;
  --ink2:#33312D;
  --muted:#6F6A61;
  --line:#111111;
  --green:#00D45A;
  --green-d:#00B84D;
  --blue:#2B59E0;
  --purple:#7B4FE8;
  --sun:#FFE24B;

  --wrap:1120px;
  --sans:"Pretendard","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",system-ui,-apple-system,sans-serif;
}

*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}

body{
  margin:0;
  background:var(--cream);
  color:var(--ink2);
  font-family:var(--sans);
  font-size:17px;
  line-height:1.72;
  overflow-x:hidden;
  -webkit-font-smoothing:antialiased;
}

h1,h2,h3,h4{margin:0;color:var(--ink);line-height:1.28;font-weight:800;letter-spacing:-.028em;text-wrap:balance}
p{margin:0}
img{max-width:100%;height:auto}

a{color:var(--blue);text-decoration:none}
a:hover{text-decoration:underline}
a:focus-visible{outline:3px solid var(--blue);outline-offset:3px}

.wrap{max-width:var(--wrap);margin:0 auto;padding:0 22px}

/* 머리말 */

.top{background:var(--cream);border-bottom:2px solid var(--line);position:sticky;top:0;z-index:40}
.top .wrap{display:flex;align-items:center;gap:10px 26px;min-height:68px;flex-wrap:wrap}
.brand{font-weight:900;font-size:19px;color:var(--ink);letter-spacing:-.03em;white-space:nowrap}
.brand em{font-style:normal;background:var(--green);padding:0 6px;border:2px solid var(--line)}
.nav{display:flex;gap:4px;flex-wrap:wrap;margin-left:auto}
.nav a{padding:8px 13px;color:var(--ink2);font-size:15px;font-weight:700;border:2px solid transparent}
.nav a:hover{text-decoration:none;border-color:var(--line);background:var(--paper)}
.nav a[aria-current="page"]{background:var(--green);border-color:var(--line);color:var(--ink)}

/* 표지 */

.hero{position:relative;overflow:hidden;color:#fff;background:#2447C8;
  border-bottom:3px solid var(--line);padding:78px 0 86px}
.hero::before{content:"";position:absolute;inset:0;opacity:.45;mix-blend-mode:overlay;
  background-image:__NOISE__}
.hero .wrap{position:relative;z-index:2;text-align:center}
.hero .kicker{font-size:15px;font-weight:700;opacity:.86;margin-bottom:20px}
.hero h1{color:#fff;font-size:clamp(30px,5.4vw,58px);font-weight:900;line-height:1.24}
.hero h1 em{font-style:normal;color:var(--sun)}
.hero .lede{margin-top:20px;font-size:clamp(16px,2vw,20px);opacity:.95}
.hero .facts{margin-top:30px;display:flex;gap:9px;flex-wrap:wrap;justify-content:center}
.hero .facts span{background:rgba(255,255,255,.14);border:2px solid rgba(255,255,255,.45);
  padding:7px 15px;font-size:14px;font-weight:700}
.doodle{position:absolute;z-index:1}
.doodle.a{top:15%;left:6%;width:54px}
.doodle.b{top:62%;left:11%;width:40px}
.doodle.c{top:21%;right:8%;width:48px}
.doodle.d{top:66%;right:6%;width:60px}
@media (max-width:760px){.doodle{display:none}}

/* 구역 */

section.band{padding:66px 0}
section.band.tight{padding:44px 0}
.band-head{text-align:center;margin-bottom:36px}
.band-head h2{font-size:clamp(23px,3.4vw,34px);font-weight:900}
.band-head p{margin-top:10px;color:var(--muted);font-size:16px}
.band-note{display:inline-block;border:2px solid var(--line);background:var(--paper);
  padding:9px 18px;font-size:14px;font-weight:700;color:var(--ink);margin-bottom:22px}

/* 티켓 카드 */

.ticket{position:relative;padding:30px 30px 30px 46px;margin-bottom:26px}
.ticket::before{content:"";position:absolute;inset:0;background:var(--paper);z-index:0;
  -webkit-mask:radial-gradient(circle 11px at left, transparent 11px, #000 11.6px) left top/100% 38px repeat-y;
  mask:radial-gradient(circle 11px at left, transparent 11px, #000 11.6px) left top/100% 38px repeat-y}
.ticket::after{content:"";position:absolute;inset:0;border:2.5px solid var(--line);
  filter:url(#rough);z-index:1;pointer-events:none}
.ticket>*{position:relative;z-index:2}
.ribbon{position:absolute;top:-10px;right:26px;width:26px;z-index:3}

.card-head{margin-bottom:18px}
.card-head h2{font-size:clamp(20px,2.6vw,27px);font-weight:900}
.card-head p{margin-top:7px;color:var(--muted);font-size:15px;font-weight:600}

.split{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,.94fr);gap:34px;align-items:start}

.keyvis{position:relative;border:2.5px solid var(--line);aspect-ratio:16/9;
  display:flex;flex-direction:column;justify-content:flex-end;padding:16px 18px;
  background:var(--kv,#2563EB);color:#fff;overflow:hidden}
.keyvis::before{content:"";position:absolute;inset:0;opacity:.4;mix-blend-mode:overlay;
  background-image:__NOISE__}
.keyvis>*{position:relative;z-index:2}
.kv-tag{position:absolute;top:12px;left:12px;background:var(--purple);color:#fff;
  font-size:12px;font-weight:800;padding:3px 9px;border:2px solid var(--line);z-index:3}
.kv-mark{position:absolute;top:14px;right:14px;font-size:12px;font-weight:900;opacity:.92;z-index:3}
.kv-cap{font-size:clamp(15px,2vw,20px);font-weight:800;line-height:1.42;text-shadow:0 2px 10px rgba(0,0,0,.4)}
.kv-cap b{color:var(--green);font-weight:900}

.btn-green{display:block;margin-top:14px;text-align:center;background:var(--green);color:var(--ink);
  border:2.5px solid var(--line);padding:15px;font-weight:900;font-size:17px}
.btn-green:hover{background:var(--green-d);text-decoration:none}

/* 타임라인 */

.timeline{list-style:none;margin:4px 0 0;padding:0 0 0 26px;border-left:2px solid var(--line);
  display:flex;flex-direction:column;gap:26px}
.timeline li{position:relative}
.timeline li::before{content:"";position:absolute;left:-33px;top:9px;width:13px;height:13px;
  border-radius:50%;background:var(--green);border:2px solid var(--line)}
.timeline h3{font-size:17px;font-weight:900}
.timeline p{margin-top:4px;color:var(--muted);font-size:15px}
.tags{margin-top:5px;display:flex;flex-wrap:wrap;gap:4px 10px}
.tags span{color:var(--blue);font-size:14.5px;font-weight:700}

/* 카드 아래 띠 */

.card-foot{margin-top:26px}
.card-foot .q{font-size:15px;color:var(--ink2);margin-bottom:10px}
.foot-row{border:2px solid var(--line);padding:14px 18px;display:flex;flex-wrap:wrap;
  gap:12px 16px;align-items:center;justify-content:space-between}
.foot-row .t{font-weight:800;font-size:17px;color:var(--ink)}
.pills{display:flex;gap:8px;flex-wrap:wrap}
.pill{background:#1B1B1B;color:#fff;border-radius:999px;padding:9px 20px;
  font-size:14px;font-weight:700;white-space:nowrap}
.pill:hover{background:#000;text-decoration:none}
.pill.ghost{background:var(--paper);color:var(--ink);border:2px solid var(--line)}

/* 번호 스티커 */

.stickers{display:grid;gap:20px;grid-template-columns:repeat(auto-fit,minmax(270px,1fr))}
.sticker{position:relative;border:2.5px solid var(--line);padding:26px 24px 60px;color:#fff;
  background:var(--sc,#2563EB);overflow:hidden;display:block}
.sticker:hover{text-decoration:none}
.sticker::before{content:"";position:absolute;inset:0;opacity:.38;mix-blend-mode:overlay;
  background-image:__NOISE__}
.sticker::after{content:"";position:absolute;right:0;bottom:0;border-width:0 0 30px 30px;
  border-style:solid;border-color:transparent transparent var(--cream) transparent}
.sticker>*{position:relative;z-index:2}
.sticker .no{display:inline-block;background:rgba(0,0,0,.3);border:2px solid rgba(255,255,255,.5);
  padding:2px 12px;font-size:13px;font-weight:800;margin-bottom:14px}
.sticker h3{color:#fff;font-size:21px;font-weight:900;line-height:1.34}
.sticker h3 em{font-style:normal;color:var(--sun)}
.sticker p{margin-top:12px;font-size:15px;line-height:1.62;color:rgba(255,255,255,.94)}

/* 역량 카드 */

.skills{display:grid;gap:18px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.skill{position:relative;border:2px solid var(--line);border-radius:14px;padding:22px;
  background:var(--sk,#EDF2FF)}
.skill .lab{display:inline-block;background:var(--lab,#2B59E0);color:#fff;border:2px solid var(--line);
  border-radius:999px;padding:2px 13px;font-size:12.5px;font-weight:800;margin-bottom:12px}
.skill .en{font-size:14px;color:var(--muted);font-weight:700}
.skill h3{font-size:20px;font-weight:900;margin-top:2px}
.skill p{margin-top:10px;font-size:15px;color:var(--ink2)}

/* 신호등 */

.signals{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(230px,1fr))}
.signal{border:2.5px solid var(--line);background:var(--paper);padding:18px}
.signal .dot{width:26px;height:26px;border-radius:50%;border:2.5px solid var(--line);
  background:var(--sg);margin-bottom:12px}
.signal .say{font-size:19px;font-weight:900;color:var(--ink)}
.signal .pol{margin-top:3px;font-size:13.5px;color:var(--muted);font-weight:700}
.signal .mean{margin-top:10px;font-size:14.5px;color:var(--ink2)}

/* 목록 */

.rows{border-top:2px solid var(--line)}
.row{position:relative;display:flex;align-items:center;gap:18px;padding:22px 6px;
  border-bottom:2px solid var(--line);color:var(--ink2)}
.row:hover{text-decoration:none;background:rgba(255,255,255,.6)}
.row .no{flex:0 0 auto;min-width:58px;text-align:center;border:2px solid var(--line);
  background:var(--rc,#2563EB);color:#fff;font-weight:900;font-size:13px;padding:5px 8px}
.row .body{flex:1 1 auto;min-width:0}
.row h3{font-size:clamp(17px,2.3vw,22px);font-weight:900}
.row p{margin-top:5px;color:var(--muted);font-size:15px}
.row .plus{flex:0 0 auto;font-size:26px;color:var(--ink);line-height:1}

/* 본문 판 */

.panel{border:2.5px solid var(--line);background:var(--paper);padding:26px;margin-bottom:20px}
.panel h2{font-size:20px;font-weight:900;margin-bottom:14px}
.panel h3{font-size:16px;font-weight:800;margin:20px 0 7px}
.panel ul,.panel ol{margin:0;padding-left:20px}
.panel li{margin:6px 0}
.panel .note{border:2px solid var(--line);background:var(--cream);padding:14px 16px;
  font-size:15px;margin-top:14px}

.stage{display:inline-block;background:var(--ink);color:#fff;font-size:13px;font-weight:800;
  padding:4px 13px;margin-bottom:12px}
.qa{margin:0 0 14px;padding-left:15px;border-left:3px solid var(--green)}
.qa .q{font-weight:700;color:var(--ink)}
.qa .a{color:var(--muted);font-size:15px;margin-left:12px}

.dl{display:grid;gap:10px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr))}
.dl a{display:block;border:2px solid var(--line);background:var(--cream);padding:14px 16px;
  font-weight:800;font-size:15px;color:var(--ink)}
.dl a:hover{background:var(--green);text-decoration:none}
.dl a small{display:block;font-weight:600;color:var(--muted);font-size:13px;margin-top:2px}

.scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
table{width:100%;border-collapse:collapse;font-size:15px;min-width:520px}
th,td{border:2px solid var(--line);padding:10px 13px;text-align:left;vertical-align:top}
th{background:var(--cream);font-weight:800;color:var(--ink)}

.pager{display:flex;justify-content:space-between;gap:12px;margin-top:24px;flex-wrap:wrap}
.pager a{border:2.5px solid var(--line);background:var(--paper);padding:13px 20px;
  font-weight:800;color:var(--ink)}
.pager a:hover{background:var(--green);text-decoration:none}

.chat{display:flex;flex-direction:column;gap:12px;max-width:780px;margin:0 auto}
.chat div{border:2px solid var(--line);background:var(--paper);border-radius:999px;
  padding:12px 22px;font-size:15.5px;font-weight:600;color:var(--ink2)}

footer{border-top:3px solid var(--line);background:var(--cream-d);padding:34px 0 46px;
  color:var(--ink2);font-size:14.5px}
footer p{margin:4px 0}
footer strong{color:var(--ink)}

@media (max-width:820px){
  .split{grid-template-columns:minmax(0,1fr);gap:26px}
  .ticket{padding:22px 20px 22px 36px}
  section.band{padding:44px 0}
  .top .wrap{min-height:auto;padding-top:10px;padding-bottom:10px}
  .nav{margin-left:0;width:100%}
  .row{gap:12px;padding:18px 4px}
  .row .no{min-width:48px;font-size:12px}
}

@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
""".replace("__NOISE__", NOISE)


# 손그림 느낌을 내는 필터와 장식. 모든 쪽 맨 위에 한 번 넣는다.
DEFS = u"""<svg width="0" height="0" aria-hidden="true" focusable="false"
  style="position:absolute;pointer-events:none">
  <filter id="rough">
    <feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="3" seed="9" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="4.5"
      xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>"""

RIBBON = (u'<svg class="ribbon" viewBox="0 0 26 34" aria-hidden="true">'
          u'<path d="M2 2h22v30l-11-8-11 8z" fill="#00D45A" stroke="#111" stroke-width="2.5"'
          u' stroke-linejoin="round"/></svg>')

DOODLES = u"""
<svg class="doodle a" viewBox="0 0 60 60" aria-hidden="true">
  <circle cx="30" cy="30" r="22" fill="#00D45A" stroke="#111" stroke-width="3"/>
  <circle cx="23" cy="27" r="4" fill="#fff"/><circle cx="37" cy="27" r="4" fill="#fff"/>
  <circle cx="23" cy="28" r="2" fill="#111"/><circle cx="37" cy="28" r="2" fill="#111"/>
</svg>
<svg class="doodle b" viewBox="0 0 60 60" aria-hidden="true">
  <path d="M8 40c8-26 20-26 26-14s16 10 18-8" fill="none" stroke="#FFE24B"
    stroke-width="6" stroke-linecap="round"/>
</svg>
<svg class="doodle c" viewBox="0 0 60 60" aria-hidden="true">
  <path d="M30 4l7 17 18 2-13 12 4 18-16-9-16 9 4-18L5 23l18-2z" fill="#fff"
    stroke="#111" stroke-width="3" stroke-linejoin="round"/>
</svg>
<svg class="doodle d" viewBox="0 0 60 60" aria-hidden="true">
  <path d="M6 44c0-18 12-30 24-30s24 12 24 30z" fill="#7B4FE8" stroke="#111" stroke-width="3"/>
  <circle cx="22" cy="32" r="4" fill="#fff"/><circle cx="38" cy="32" r="4" fill="#fff"/>
  <circle cx="22" cy="33" r="2" fill="#111"/><circle cx="38" cy="33" r="2" fill="#111"/>
</svg>
"""
