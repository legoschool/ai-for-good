# -*- coding: utf-8 -*-
"""13개 웹앱이 공유하는 단일 HTML 골격.

- Google Sites 소스 코드 삽입용 단일 파일. 외부 CDN 참조 없음.
- Firebase REST + 3초 폴링. SDK 번들을 인라인하지 않는다.
- 정규식에 역슬래시 이스케이프를 쓰지 않는다. (Apps Script 가 파괴한다)

활동 화면이 쓸 수 있는 골격 기능
  wiseDraft(obj)      입력 중간값을 이 기기에 저장한다
  wiseStep(i, n)      진행 단계를 상단 막대에 표시한다
  wiseNote(text)      상단에 안내 한 줄을 띄운다
  dbGet / dbPush      방 데이터 읽기와 쓰기
  esc / $ / pct / barHtml   도우미
활동 화면이 선택으로 정의할 수 있는 것
  activityAutofill()  자동 검사용 채우기
  presentHtml(list)   발표 모드에 크게 띄울 화면. 없으면 teacherSummary 를 쓴다
  activityDraft()     자동 저장할 중간값
"""

TEMPLATE = u"""<meta charset="utf-8">
<div id="wise-app">
<style>
/* 티처스랩 결. 사이트·슬라이드·인쇄물과 같은 규격이다.
   크림 바탕, 검정 테두리, 번지지 않는 그림자, 굵은 제목. */
#wise-app *,#wise-app *::before,#wise-app *::after{box-sizing:border-box}
#wise-app{--ink:#101010;--ink2:#33312D;--muted:#6F6A61;--line:#111111;--paper:#FFFFFF;
--bg:#F4EEE0;--bg-d:#EBE3D2;--green:#00D45A;--sun:#FFE24B;
--accent:__ACCENT__;--accent-soft:__ACCENT_SOFT__;
--shadow:5px 5px 0 var(--line);
font-family:"Pretendard","Malgun Gothic","맑은 고딕","Apple SD Gothic Neo",system-ui,sans-serif;
color:var(--ink2);background:var(--bg);line-height:1.75;font-size:21px;
padding:18px;max-width:1040px;margin:0 auto;-webkit-text-size-adjust:100%}
#wise-app h1,#wise-app h2,#wise-app h3{margin:0;color:var(--ink);font-weight:900;line-height:1.28;
letter-spacing:-.028em}
#wise-app .hd{background:var(--accent);color:#fff;border:3px solid var(--line);border-radius:18px;
padding:20px 22px;margin-bottom:16px;box-shadow:var(--shadow);position:relative;overflow:hidden}
#wise-app .hd::after{content:"";position:absolute;right:-40px;top:-60px;width:200px;height:200px;
border-radius:50%;background:rgba(255,255,255,.12)}
#wise-app .hd h1{font-size:28px;color:#fff}
#wise-app .hd p{margin:6px 0 0;font-size:19px;opacity:.95;font-weight:700}
#wise-app .card{background:var(--paper);border:3px solid var(--line);border-radius:16px;padding:20px;
margin-bottom:16px;box-shadow:var(--shadow)}
#wise-app .card h2{font-size:27px;margin-bottom:10px}
#wise-app .card h3{font-size:22px}
#wise-app .row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
#wise-app label{display:block;font-size:19px;color:var(--muted);margin:12px 0 4px;font-weight:800}
#wise-app input,#wise-app textarea,#wise-app select{
width:100%;font:inherit;font-size:20px;padding:14px 15px;border:2.5px solid var(--line);
border-radius:12px;background:#fff;color:var(--ink)}
#wise-app input:focus,#wise-app textarea:focus,#wise-app select:focus{
outline:3px solid var(--sun);outline-offset:2px}
#wise-app textarea{min-height:104px;resize:vertical}
#wise-app button{font:inherit;font-size:21px;font-weight:900;min-height:58px;padding:13px 20px;
border-radius:12px;border:2.5px solid var(--line);background:var(--green);color:var(--ink);
cursor:pointer;box-shadow:3px 3px 0 var(--line)}
#wise-app button:hover{background:var(--sun)}
#wise-app button:active{transform:translate(2px,2px);box-shadow:1px 1px 0 var(--line)}
#wise-app button.ghost{background:#fff}
#wise-app button.plain{background:#fff;color:var(--muted);box-shadow:none}
#wise-app button:disabled{opacity:.45;cursor:not-allowed;box-shadow:none}
#wise-app .code{font-size:38px;font-weight:900;letter-spacing:.16em;color:var(--accent)}
#wise-app .muted{color:var(--muted);font-size:19px}
#wise-app .pill{display:inline-block;padding:5px 13px;border-radius:999px;background:var(--sun);
border:2.5px solid var(--line);color:var(--ink);font-size:15px;font-weight:900}
#wise-app .tag{display:inline-block;padding:3px 10px;border-radius:999px;background:#fff;
border:2px solid var(--line);color:var(--ink2);font-size:14px;font-weight:800;margin-right:4px}
#wise-app .hide{display:none !important}
#wise-app .bucket{border:3px dashed var(--line);border-radius:14px;padding:12px;min-height:120px;
background:#fff}
#wise-app .bucket h3{font-size:18px;margin-bottom:8px}
#wise-app .grid{display:grid;gap:12px}
#wise-app .g2{display:grid;gap:14px;grid-template-columns:1fr 1fr}
#wise-app .chip{display:block;width:100%;text-align:left;padding:15px 17px;margin-bottom:10px;font-size:21px;
border:2.5px solid var(--line);border-radius:12px;background:#fff;color:var(--ink);font-weight:700;
min-height:52px;box-shadow:3px 3px 0 var(--line)}
#wise-app .chip:hover{background:var(--bg-d)}
#wise-app .chip.on{background:var(--accent);color:#fff}
#wise-app .bar{height:16px;border-radius:8px;background:#fff;border:2.5px solid var(--line);
overflow:hidden}
#wise-app .bar>i{display:block;height:100%;background:var(--green)}
#wise-app .steps{display:flex;gap:6px;margin:12px 0 0}
#wise-app .steps>span{flex:1;height:10px;border-radius:6px;background:#fff;border:2px solid var(--line)}
#wise-app .steps>span.on{background:var(--green)}
#wise-app table{width:100%;border-collapse:collapse;font-size:17px}
#wise-app th,#wise-app td{border:2px solid var(--line);padding:9px 11px;text-align:left;
vertical-align:top}
#wise-app th{background:var(--bg-d);font-weight:900;color:var(--ink)}
#wise-app .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
#wise-app .safe{margin-top:14px;padding:14px 16px;border-radius:12px;background:#FFF3D6;
border:2.5px solid var(--line);color:var(--ink2);font-size:16px;font-weight:700}
#wise-app .note{padding:13px 15px;border-radius:12px;background:var(--sun);
border:2.5px solid var(--line);color:var(--ink);font-size:17px;font-weight:800;margin-top:12px}
#wise-app .ok{color:#0B7A3B;font-weight:900}
#wise-app .warn{color:#B03A00;font-weight:900}
#wise-app .big{font-size:34px;font-weight:900;line-height:1.2;color:var(--ink)}
#wise-app .foot{text-align:center;color:var(--muted);font-size:14px;padding:16px 0;font-weight:700}
#wise-app .wi{vertical-align:middle;margin-right:8px;flex:none}
#wise-app .ws-scene{display:block;width:100%;height:164px;border:2.5px solid var(--line);
border-radius:14px;background:#fff;margin:10px 0 6px}
#wise-app .iconrow{display:flex;align-items:center;gap:8px}
#wise-app .quest{display:none}
#wise-app .quest.on{display:block;animation:wfade .34s cubic-bezier(.22,.61,.36,1)}
@keyframes wfade{from{opacity:0;transform:translateY(14px) scale(.99)}to{opacity:1;transform:none}}
#wise-app .spin{display:inline-block;width:20px;height:20px;border-radius:50%;
border:3px solid var(--bg-d);border-top-color:var(--ink);animation:wspin .7s linear infinite;
vertical-align:middle;margin-right:8px}
#wise-app .spin.big{width:34px;height:34px;border-width:4px}
@keyframes wspin{to{transform:rotate(360deg)}}
#wise-app .loading{display:flex;align-items:center;gap:10px;font-weight:800;color:var(--ink);
padding:14px 0}
#wise-app .skel{height:16px;border-radius:8px;background:var(--bg-d);margin:8px 0;
animation:wpulse 1.1s ease-in-out infinite}
#wise-app .skel.w60{width:60%}
#wise-app .skel.w80{width:80%}
@keyframes wpulse{0%,100%{opacity:1}50%{opacity:.45}}
#wise-app button.busy{position:relative;color:var(--muted)}
#wise-app .busy-wrap{position:fixed;inset:0;background:rgba(244,238,224,.72);display:flex;
align-items:center;justify-content:center;z-index:65}
#wise-app .busy-wrap .box{background:#fff;border:3px solid var(--line);border-radius:18px;
padding:20px 26px;box-shadow:6px 6px 0 var(--line);display:flex;align-items:center;gap:12px;
font-weight:900;color:var(--ink)}
#wise-app .fade-in{animation:wfade .28s ease-out}
#wise-app .hud{display:flex;gap:12px;align-items:center;flex-wrap:wrap;background:#fff;
border:2.5px solid var(--line);border-radius:14px;padding:11px 15px;margin-bottom:14px;
font-weight:800;font-size:17px;color:var(--ink);box-shadow:3px 3px 0 var(--line)}
#wise-app .hud .grow{flex:1;min-width:120px}
#wise-app .tile{font-size:22px;border:3px solid var(--line);border-radius:16px;padding:16px;background:#fff;
text-align:left;font-weight:800;font-size:20px;min-height:118px;display:flex;flex-direction:column;gap:6px;
box-shadow:var(--shadow);color:var(--ink)}
#wise-app .tile small{font-weight:700;color:var(--muted);font-size:16px}
#wise-app .tile.done{background:var(--sun)}
#wise-app .cele{position:fixed;inset:0;background:rgba(17,17,17,.6);display:flex;align-items:center;
justify-content:center;padding:20px;z-index:60}
#wise-app .cele .box{background:#fff;border:3px solid var(--line);border-radius:22px;padding:26px;
max-width:460px;width:100%;text-align:center;box-shadow:8px 8px 0 var(--line)}
#wise-app .cele h2{font-size:28px;margin-bottom:10px}
#wise-app .toast{position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:var(--ink);
color:#fff;padding:13px 22px;border-radius:999px;font-weight:800;font-size:17px;z-index:70;
border:2.5px solid var(--line)}
#wise-app canvas{max-width:100%;height:auto;border-radius:12px}
#wise-app .intro{margin:-4px 0 16px}
#wise-app .intro svg{display:block;width:100%;height:168px;border:2.5px solid var(--line);
border-radius:14px;background:#fff}
#wise-app .intro p{margin:10px 0 0;font-size:18px;color:var(--muted);font-weight:700}
#wise-app .intro b{color:var(--ink)}
#wise-app .wtop{position:sticky;top:0;z-index:40;display:flex;gap:8px;align-items:center;
flex-wrap:nowrap;overflow-x:auto;background:var(--bg);padding:10px 0;margin:-18px 0 12px}
#wise-app .wtop a,#wise-app .wtop button{font-size:15px;font-weight:800;color:var(--ink);
background:#fff;border:2.5px solid var(--line);border-radius:999px;padding:9px 16px;min-height:44px;
white-space:nowrap;text-decoration:none;cursor:pointer;box-shadow:none}
#wise-app .wtop a:hover,#wise-app .wtop button:hover{background:var(--sun)}
#wise-app #present .card{border-radius:20px}
#wise-app #present table{font-size:23px}
#wise-app #present .big{font-size:46px}
@media (max-width:640px){#wise-app{padding:10px;font-size:19px}#wise-app .hd h1{font-size:32px}
#wise-app .g2{grid-template-columns:1fr}#wise-app .intro svg{height:126px}
#wise-app .ws-scene{height:120px}}
@media (prefers-reduced-motion:reduce){#wise-app *{transition:none!important;animation:none!important}}
</style>

<nav id="w-top" class="wtop">
  <a href="../../index.html" target="_blank" rel="noopener">홈으로 돌아가기</a>
  <a href="../../browse.html" target="_blank" rel="noopener">둘러보기</a>
  <a href="../../lesson/__LESSON_ID__.html" target="_blank" rel="noopener">차시 페이지</a>
  <a href="../../webapp/common/index.html" target="_blank" rel="noopener">사전·사후 설문</a>
  <button type="button" id="w-restart">처음부터</button>
</nav>

<div class="hd">
  <h1>__APP_NAME__</h1>
  <p>__SUBTITLE__</p>
</div>

<!-- 입장 -->
<section id="gate" class="card">
  <div id="w-intro" class="hide"></div>
  <h2>들어가기</h2>
  <p class="muted">선생님이 알려 준 방 번호와 내 닉네임만 쓰면 돼요.</p>
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div>
      <label for="w-room">방 번호 6자리</label>
      <input id="w-room" inputmode="numeric" maxlength="6" placeholder="예: 482913">
    </div>
    <div>
      <label for="w-nick">닉네임</label>
      <input id="w-nick" maxlength="12" placeholder="이름 말고 별명을 써요">
    </div>
  </div>
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div>
      <label for="w-code">내 번호 (자동으로 만들어져요)</label>
      <input id="w-code" inputmode="numeric" maxlength="4" placeholder="자동">
    </div>
    <div>
      <label for="w-group">모둠 (없으면 비워 둬요)</label>
      <input id="w-group" maxlength="10" placeholder="예: 3모둠">
    </div>
  </div>
  <p class="muted" style="margin-top:6px">이 번호는 비밀번호가 아니에요.
    사전 설문과 사후 설문을 이어 보는 데만 씁니다. <b>외우지 않아도 돼요.</b>
    같은 기기로 하면 저절로 이어지고, 기기가 바뀌면 설문이 별명으로 찾아 줍니다.
    잊어버려도 활동은 그대로 할 수 있어요.</p>
  <div class="row" style="margin-top:14px">
    <button id="w-enter">입장하기</button>
    <button id="w-solo" class="ghost">둘러보기</button>
    <button id="w-teacher" class="plain">선생님 화면</button>
  </div>
  <p id="w-gate-msg" class="muted" style="margin-top:10px"></p>
  <div class="note" id="w-prepost">처음 시작하기 전에는 <b>사전 설문</b>, 열두 시간을 마친 뒤에는
    <b>사후 설문</b>을 합니다.
    <a href="../common/index.html" target="_blank" rel="noopener">자기인식 설문 열기</a></div>
  <div class="safe"><b>개인정보를 모으지 않아요.</b> 이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.
    학교, 학년, 반, 전화번호도 묻지 않습니다. 닉네임과 답만 저장합니다.
    모인 자료는 수업 프로그램을 더 좋게 만드는 데만 쓰고, 학년도가 끝나면 지웁니다.</div>
</section>

<!-- 학생 활동 -->
<section id="stage" class="hide">
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <span class="pill" id="w-who"></span>
      <span class="muted" id="w-sync">저장 준비됨</span>
    </div>
    <div class="steps hide" id="w-steps"></div>
    <div class="note hide" id="w-note"></div>
  </div>
  <div id="w-hud" class="hide"></div>
  <div id="activity"></div>
  <div class="card">
    <button id="w-submit">제출하기</button>
    <button id="w-leave" class="plain">나가기</button>
    <p id="w-msg" class="muted" style="margin-top:10px"></p>
  </div>
</section>

<!-- 교사 -->
<section id="teacher" class="hide">
  <div class="card">
    <h2>선생님 화면</h2>
    <p class="muted">방을 만들면 여섯 자리 번호가 나옵니다. 학생에게 번호만 알려 주세요.</p>
    <label for="w-pw">선생님 비밀번호 4자리 (이 화면을 다시 열 때 씁니다)</label>
    <input id="w-pw" inputmode="numeric" maxlength="4" placeholder="예: 1234">
    <label for="w-tag" style="margin-top:10px">학급 이름표 (안 써도 됩니다)</label>
    <input id="w-tag" maxlength="30" placeholder="예: 진해신항초 6학년 1반">
    <p class="muted">기록 시트의 방 목록에 그대로 남습니다. 학급이 여럿일 때 어느 방인지 가려내는 데 씁니다.</p>
    <div class="row" style="margin-top:12px">
      <button id="t-make">새 방 만들기</button>
      <button id="t-open" class="ghost">기존 방 열기</button>
      <button id="t-back" class="plain">돌아가기</button>
    </div>
    <div id="t-room" class="hide" style="margin-top:16px">
      <p class="muted">방 코드</p>
      <div class="row">
        <span class="code" id="t-code">------</span>
        <button id="t-copy" class="ghost">복사</button>
      </div>
      <p class="muted" id="t-pw"></p>
      <div class="row" style="margin-top:12px">
        <button id="t-present">결과 크게 띄우기</button>
        <button id="t-refresh" class="ghost">새로고침</button>
        <button id="t-csv" class="ghost">CSV 내려받기</button>
        <button id="t-lock" class="plain">방 잠그기</button>
      </div>
    </div>
  </div>
  <div id="t-board" class="card hide">
    <h2>제출 현황 <span class="pill" id="t-count">0명</span></h2>
    <p class="muted" id="t-note"></p>
    <div id="t-summary"></div>
    <div class="row" style="margin-top:12px">
      <button id="t-detail" class="plain">낱낱이 보기 켜기</button>
    </div>
    <div class="scroll hide" id="t-wrap" style="margin-top:12px"><table id="t-table"></table></div>
  </div>
</section>

<!-- 발표 -->
<section id="present" class="hide">
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <h2 id="p-title">우리 반 결과</h2>
      <button id="p-close" class="plain">닫기</button>
    </div>
    <div id="p-body" style="margin-top:12px"></div>
  </div>
</section>

<div id="w-cele" class="hide"></div>
<div id="w-busy" class="hide"></div>
<div id="w-toast" class="hide"></div>

<p class="foot">__COPYRIGHT__</p>
</div>

<script>
(function () {
  "use strict";

  var APP = "__SLUG__";
  var DB = "https://remind-c2610-default-rtdb.firebaseio.com";
  var SHEET_ENDPOINT = "__SHEET_ENDPOINT__";
  var QUEUE_KEY = "wise_backup_queue";
  var LOCAL_KEY = "wise_" + APP + "_local";
  var ACCENT = "__ACCENT__";
  var COPYRIGHT_LINE = "__COPYRIGHT__";

  var $ = function (id) { return document.getElementById(id); };
  var me = { room: "", pw: "", nick: "", group: "", code: "", solo: false };
  var CODE_KEY = "wise_student_code";
  var timer = null;
  var draftTimer = null;

  /* ---------- 저장 ---------- */

  function dbUrl(path) { return DB + "/wise/" + APP + "/" + path + ".json"; }

  function dbGet(path) {
    return fetch(dbUrl(path)).then(function (r) { return r.json(); });
  }
  function dbPut(path, data) {
    return fetch(dbUrl(path), {
      method: "PUT", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json(); });
  }
  function dbPush(path, data) {
    return fetch(dbUrl(path), {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    }).then(function (r) { return r.json(); });
  }

  function sheetBackup(record) {
    try {
      var q = JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]");
      q.push(record);
      localStorage.setItem(QUEUE_KEY, JSON.stringify(q));
      if (SHEET_ENDPOINT.indexOf("http") !== 0) { return; }
      fetch(SHEET_ENDPOINT, {
        method: "POST", mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({ rows: q })
      }).then(function () {
        localStorage.setItem(QUEUE_KEY, "[]");
      })["catch"](function () {});
    } catch (e) {}
  }

  /* 방을 만들었다는 것만 시트에 알린다. 학생 응답은 보내지 않는다. */
  function sheetRoom(room, tag) {
    try {
      if (SHEET_ENDPOINT.indexOf("http") !== 0) { return; }
      fetch(SHEET_ENDPOINT, {
        method: "POST", mode: "no-cors",
        headers: { "Content-Type": "text/plain;charset=utf-8" },
        body: JSON.stringify({ rooms: [{ app: APP, room: room, at: Date.now(),
          tag: tag || "" }] })
      })["catch"](function () {});
    } catch (e) {}
  }

  /* ---------- 도구 ---------- */

  function onlyDigits(s, n) {
    var out = "";
    for (var i = 0; i < s.length && out.length < n; i++) {
      if (s.charAt(i) >= "0" && s.charAt(i) <= "9") { out += s.charAt(i); }
    }
    return out;
  }

  function makeCode() {
    var s = "";
    for (var i = 0; i < 6; i++) { s += String(Math.floor(Math.random() * 10)); }
    return s;
  }

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function pct(a, b) { return b ? Math.round(a * 100 / b) : 0; }

  function barHtml(a, b) {
    return '<div class="bar"><i style="width:' + pct(a, b) + '%"></i></div>';
  }

  function show(id) {
    var ids = ["gate", "stage", "teacher", "present"];
    for (var i = 0; i < ids.length; i++) {
      $(ids[i]).className = ids[i] === id ? "" : "hide";
    }
  }

  /* 활동 화면이 부르는 골격 기능 */

  function wiseDraft(obj) {
    try { localStorage.setItem(LOCAL_KEY, JSON.stringify(obj)); } catch (e) {}
    $("w-sync").textContent = "이 기기에 임시 저장됨";
  }

  function wiseStep(i, n) {
    var h = "";
    for (var k = 0; k < n; k++) { h += '<span class="' + (k <= i ? "on" : "") + '"></span>'; }
    $("w-steps").innerHTML = h;
    $("w-steps").className = "steps";
  }

  /* 여정 화면 전환. 활동이 만든 .quest 조각을 갈아 끼운다. */
  /* 여정형 앱에서 다음 화면으로 가는 버튼을 화면마다 자동으로 붙인다.
     허브로 돌아갔다가 다시 고르게 하면 학생이 거기서 멈춘다.
     차시 코드가 이미 '...로 가기' 버튼을 만들어 두었으면 건드리지 않는다. */
  function addNextButtons() {
    var qs = document.querySelectorAll("#activity .quest");
    if (qs.length < 3) { return; }
    var ids = [], titles = [], i;
    for (i = 0; i < qs.length; i++) {
      ids.push(qs[i].getAttribute("data-q"));
      var h = qs[i].querySelector("h2");
      titles.push(h ? h.textContent.trim() : "다음");
    }
    for (i = 0; i < qs.length; i++) {
      var id = ids[i];
      if (id === "story" || id === "hub") { continue; }
      if (i + 1 >= qs.length) { continue; }
      if (hasForward(qs[i])) { continue; }
      var row = document.createElement("div");
      row.className = "row autonext";
      row.style.marginTop = "10px";
      var b = document.createElement("button");
      b.type = "button";
      b.setAttribute("data-next", ids[i + 1]);
      b.textContent = "다음 : " + titles[i + 1];
      b.onclick = function () { wiseGo(this.getAttribute("data-next")); };
      row.appendChild(b);
      var card = qs[i].querySelector(".card");
      (card || qs[i]).appendChild(row);
    }
  }

  /* 이미 앞으로 가는 버튼이 있는가. '교무실로' 같은 되돌아가기와
     '다음 카드' 같은 같은 화면 안 이동은 세지 않는다. */
  function hasForward(sec) {
    var bs = sec.querySelectorAll("button");
    for (var i = 0; i < bs.length; i++) {
      var b = bs[i];
      if (b.parentNode && /autonext/.test(b.parentNode.className || "")) { continue; }
      var t = b.textContent || "";
      var bid = b.id || "";
      if (/(다음 카드|다음 문항|앞 카드|앞 문항|돌아가기|돌아가)/.test(t)) { continue; }
      if (/-go$|^go-/.test(bid)) { return true; }
      if (/(로 가기|으로 가기|보러 가기|하러 가기|넘어가|이어서 하기)/.test(t)) { return true; }
    }
    return false;
  }

  /* 차시 코드가 뒤늦게 만들어 내는 '…로 가기' 버튼과 겹치지 않게,
     화면에 들어올 때마다 자동 버튼을 보일지 말지 다시 정한다. */
  function syncNextButton(sec) {
    if (!sec) { return; }
    var row = sec.querySelector(".autonext");
    if (!row) { return; }
    row.style.display = hasForward(sec) ? "none" : "";
  }

  function wiseGo(id) {
    var qs = document.querySelectorAll("#activity .quest");
    for (var i = 0; i < qs.length; i++) {
      qs[i].className = "quest" + (qs[i].getAttribute("data-q") === id ? " on" : "");
    }
    if (window.scrollTo) { window.scrollTo(0, 0); }
    if (typeof activityEnter === "function") {
      try { activityEnter(id); } catch (e) {}
    }
    for (var k = 0; k < qs.length; k++) {
      if (qs[k].getAttribute("data-q") === id) { syncNextButton(qs[k]); }
    }
  }

  /* 상단 진행 표시. 여러 칸을 한 줄로 보여 준다. */
  function wiseHud(items) {
    var h = "";
    for (var i = 0; i < items.length; i++) {
      var it = items[i];
      h += '<span>' + esc(it.label) + ' ' + it.done + ' / ' + it.total + '</span>';
    }
    var first = items[0] || { done: 0, total: 1 };
    h += '<span class="grow">' + barHtml(first.done, first.total) + '</span>';
    $("w-hud").innerHTML = h;
    $("w-hud").className = "hud";
  }

  /* 기다리는 동안 무엇을 하는 중인지 보여 준다. 화면이 멈춘 것처럼 보이지 않게 한다. */
  function wiseSpinner(text, big) {
    return '<div class="loading"><span class="spin' + (big ? " big" : "") + '"></span>' +
      '<span>' + esc(text || "불러오는 중이에요") + '</span></div>';
  }

  function wiseSkeleton(lines) {
    var n = lines || 3, h = "";
    for (var i = 0; i < n; i++) {
      h += '<div class="skel ' + (i % 3 === 1 ? "w80" : (i % 3 === 2 ? "w60" : "")) + '"></div>';
    }
    return h;
  }

  function wiseBusy(on, text) {
    if (!on) { $("w-busy").className = "hide"; return; }
    $("w-busy").innerHTML = '<div class="busy-wrap"><div class="box">' +
      '<span class="spin big"></span><span>' + esc(text || "잠시만요") + '</span></div></div>';
    $("w-busy").className = "";
  }

  /* 버튼을 누른 뒤 끝날 때까지 눌리지 않게 한다. */
  function wiseButtonBusy(el, on, text) {
    if (!el) { return; }
    if (on) {
      el.setAttribute("data-orig", el.textContent);
      el.innerHTML = '<span class="spin"></span>' + esc(text || "하는 중");
      el.disabled = true;
    } else {
      el.textContent = el.getAttribute("data-orig") || el.textContent;
      el.disabled = false;
    }
  }

  function wiseToast(text) {
    $("w-toast").textContent = text;
    $("w-toast").className = "toast";
    setTimeout(function () { $("w-toast").className = "toast hide"; }, 2200);
  }

  function wiseCelebrate(title, lines, buttonText) {
    var h = '<div class="box"><h2>' + esc(title) + '</h2>';
    for (var i = 0; i < lines.length; i++) {
      h += '<p class="muted" style="margin-top:6px">' + lines[i] + '</p>';
    }
    h += '<div class="row" style="justify-content:center;margin-top:16px">' +
      '<button type="button" id="cele-close">' + esc(buttonText || "닫기") + '</button></div></div>';
    $("w-cele").innerHTML = h;
    $("w-cele").className = "cele";
    var celeClose = function () { $("w-cele").className = "hide"; $("w-cele").innerHTML = ""; };
    $("cele-close").onclick = celeClose;
    $("w-cele").onclick = function (ev) { if (ev.target === $("w-cele")) { celeClose(); } };
  }

  /* 결과 카드를 그림으로 만들어 내려받는다. 교실에서 인쇄해 붙일 수 있다. */
  function wiseCardPng(title, lines, filename) {
    try {
      var c = document.createElement("canvas");
      c.width = 900; c.height = 560;
      var g = c.getContext("2d");
      g.fillStyle = "#ffffff"; g.fillRect(0, 0, 900, 560);
      g.fillStyle = ACCENT; g.fillRect(0, 0, 900, 120);
      g.fillStyle = "#ffffff"; g.font = "bold 40px sans-serif";
      g.fillText(title, 40, 76);
      g.fillStyle = "#111827"; g.font = "26px sans-serif";
      for (var i = 0; i < lines.length && i < 10; i++) {
        g.fillText(String(lines[i]).slice(0, 34), 40, 180 + i * 42);
      }
      g.fillStyle = "#6b7280"; g.font = "18px sans-serif";
      g.fillText(COPYRIGHT_LINE, 40, 530);
      var a = document.createElement("a");
      a.href = c.toDataURL("image/png");
      a.download = (filename || "wise_card") + ".png";
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      wiseToast("카드를 내려받았어요.");
    } catch (e) { wiseToast("이 기기에서는 카드 저장이 안 돼요."); }
  }

  /* 교사 화면용 막대 그림. 캔버스로 그린다. */
  function wiseBars(rows, width) {
    var w = width || 620, h = 42 * rows.length + 24;
    var c = document.createElement("canvas");
    if (!c || typeof c.getContext !== "function") { return barTable(rows); }
    c.width = w; c.height = h;
    var g = c.getContext("2d");
    g.fillStyle = "#ffffff"; g.fillRect(0, 0, w, h);
    var max = 1;
    for (var i = 0; i < rows.length; i++) { if (rows[i].value > max) { max = rows[i].value; } }
    for (var k = 0; k < rows.length; k++) {
      var y = 16 + k * 42;
      g.fillStyle = "#374151"; g.font = "bold 16px sans-serif";
      g.fillText(String(rows[k].label).slice(0, 14), 8, y + 20);
      var x0 = 160, bw = (w - 200) * rows[k].value / max;
      g.fillStyle = "#e5e7eb"; g.fillRect(x0, y, w - 200, 24);
      g.fillStyle = rows[k].color || ACCENT; g.fillRect(x0, y, bw, 24);
      g.fillStyle = "#111827"; g.font = "bold 15px sans-serif";
      g.fillText(String(rows[k].value), x0 + bw + 8, y + 18);
    }
    return '<img alt="분포 그림" style="width:100%" src="' + c.toDataURL("image/png") + '">';
  }

  /* 캔버스를 못 쓰는 자리에서는 표로 대신한다. */
  function barTable(rows) {
    var h = '<div class="scroll"><table><tr><th>항목</th><th>수</th><th>분포</th></tr>';
    var max = 1;
    for (var i = 0; i < rows.length; i++) { if (rows[i].value > max) { max = rows[i].value; } }
    for (var k = 0; k < rows.length; k++) {
      h += "<tr><td>" + esc(rows[k].label) + "</td><td>" + rows[k].value + "</td><td>" +
        barHtml(rows[k].value, max) + "</td></tr>";
    }
    return h + "</table></div>";
  }

  function wiseNote(text) {
    if (!text) { $("w-note").className = "note hide"; return; }
    $("w-note").innerHTML = text;
    $("w-note").className = "note";
  }

  /* ---------- 활동 (차시별) ---------- */

__ACTIVITY__

  /* ---------- 학생 흐름 ---------- */

  function enter(solo) {
    var room = onlyDigits($("w-room").value, 6);
    var nick = $("w-nick").value.trim();
    var group = $("w-group").value.trim();
    var code = onlyDigits($("w-code").value, 4);
    if (code) {
      try { localStorage.setItem(CODE_KEY, code); } catch (e) {}
    }

    if (!nick) {
      if (solo) { nick = "둘러보는 중"; }
      else { $("w-gate-msg").textContent = "닉네임을 써 주세요."; return; }
    }
    if (!solo && room.length !== 6) { $("w-gate-msg").textContent = "방 번호 6자리를 정확히 써 주세요."; return; }

    me = { room: solo ? "solo" : room, pw: "", nick: nick, group: group,
      code: code, solo: !!solo };
    $("w-who").textContent = me.nick + (me.group ? " · " + me.group : "") +
      (me.solo ? " · 혼자 체험" : " · " + me.room);
    $("activity").innerHTML = activityHtml();
    activityInit(loadLocal());
    addNextButtons();
    startDraft();
    show("stage");
  }

  function loadLocal() {
    try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || "null"); }
    catch (e) { return null; }
  }

  function startDraft() {
    if (draftTimer) { clearInterval(draftTimer); }
    if (typeof activityDraft !== "function") { return; }
    draftTimer = setInterval(function () {
      try {
        var d = activityDraft();
        if (d) { wiseDraft(d); }
      } catch (e) {}
    }, 8000);
  }

  function submit() {
    var payload = activityCollect();
    if (payload === null) { return; }

    try { localStorage.setItem(LOCAL_KEY, JSON.stringify(payload)); } catch (e) {}

    if (me.solo) {
      $("w-msg").innerHTML = '<span class="ok">이 기기에만 저장했어요. 혼자 체험 중이에요.</span>';
      return;
    }

    var record = {
      nick: me.nick, group: me.group, code: me.code, app: APP,
      room: me.room, at: Date.now(), payload: payload
    };

    $("w-sync").innerHTML = '<span class="spin"></span>저장 중';
    wiseButtonBusy($("w-submit"), true, "보내는 중");
    dbPush(me.room + "/entries", record).then(function () {
      wiseButtonBusy($("w-submit"), false);
      $("w-sync").textContent = "저장됨";
      $("w-msg").innerHTML = '<span class="ok">제출했어요. 고쳐서 다시 제출해도 괜찮아요.</span>';
      sheetBackup(record);
    })["catch"](function () {
      wiseButtonBusy($("w-submit"), false);
      $("w-sync").textContent = "저장 실패";
      $("w-msg").innerHTML = '<span class="warn">인터넷이 불안정해요. 쓴 내용은 이 기기에 남아 있어요. 잠시 뒤 다시 제출해 주세요.</span>';
    });
  }

  /* ---------- 교사 흐름 ---------- */

  function teacherMake() {
    var code = makeCode();
    var pw = onlyDigits($("w-pw").value, 4) || "0000";
    wiseBusy(true, "방을 만드는 중");
    dbPut(code + "/meta", { app: APP, pw: pw, at: Date.now(), locked: false })
      .then(function () {
        wiseBusy(false);
        sheetRoom(code, $("w-tag") ? $("w-tag").value.trim() : "");
        teacherOpen(code, pw);
      })
      ["catch"](function () {
        wiseBusy(false);
        alert("방을 만들지 못했어요. 인터넷을 확인해 주세요.");
      });
  }

  function teacherOpen(code, pw) {
    me.room = code;
    $("t-code").textContent = code;
    $("t-pw").textContent = "비밀번호 " + (pw || "-") + " · 이 화면을 닫아도 방은 사라지지 않아요.";
    $("t-room").className = "";
    $("t-board").className = "card";
    $("t-summary").innerHTML = wiseSpinner("제출을 불러오는 중이에요", true) + wiseSkeleton(3);
    teacherRefresh();
    if (timer) { clearInterval(timer); }
    timer = setInterval(teacherRefresh, 3000);
  }

  function teacherRefresh() {
    if (!me.room) { return; }
    dbGet(me.room + "/entries").then(function (data) {
      var rows = [];
      for (var k in data) { if (data.hasOwnProperty(k)) { rows.push(data[k]); } }
      rows.sort(function (a, b) { return (a.at || 0) - (b.at || 0); });

      var latest = {};
      for (var i = 0; i < rows.length; i++) { latest[rows[i].nick] = rows[i]; }
      var list = [];
      for (var n in latest) { if (latest.hasOwnProperty(n)) { list.push(latest[n]); } }

      $("t-count").textContent = list.length + "명";
      $("t-note").textContent = noteFor(list, rows.length);
      $("t-summary").innerHTML = teacherSummary(list);
      $("t-table").innerHTML = teacherTable(list);
      window.__wiseRows = list;
      if ($("present").className === "") { paintPresent(list); }
    })["catch"](function () {});
  }

  function noteFor(list, tries) {
    if (!list.length) { return "아직 제출이 없어요. 학생에게 방 코드를 알려 주세요."; }
    var groups = {}, n = 0;
    for (var i = 0; i < list.length; i++) {
      var g = list[i].group || "모둠 없음";
      if (!groups[g]) { groups[g] = 0; n++; }
      groups[g] += 1;
    }
    var last = 0;
    for (var k = 0; k < list.length; k++) { if (list[k].at > last) { last = list[k].at; } }
    return "모둠 " + n + "개 · 제출 시도 " + tries + "회 · 마지막 제출 " +
      new Date(last).toLocaleTimeString("ko-KR");
  }

  function paintPresent(list) {
    var html = "";
    try {
      html = (typeof presentHtml === "function") ? presentHtml(list) : teacherSummary(list);
    } catch (e) { html = teacherSummary(list); }
    $("p-title").textContent = "우리 반 결과 · " + list.length + "명";
    $("p-body").innerHTML = html;
  }

  function teacherTable(list) {
    var h = "<tr><th>닉네임</th><th>모둠</th><th>제출 시각</th><th>내용</th></tr>";
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      h += "<tr><td>" + esc(r.nick) + "</td><td>" + esc(r.group) + "</td><td>" +
        new Date(r.at).toLocaleTimeString("ko-KR") + "</td><td>" +
        esc(JSON.stringify(r.payload).slice(0, 180)) + "</td></tr>";
    }
    return h;
  }

  function toCsv(list) {
    var lines = ["닉네임,모둠,제출시각,내용"];
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      lines.push([r.nick, r.group, new Date(r.at).toLocaleString("ko-KR"),
        JSON.stringify(r.payload)].map(function (v) {
          return '"' + String(v).split('"').join('""') + '"';
        }).join(","));
    }
    return lines.join("\\n");
  }

  function download() {
    var list = window.__wiseRows || [];
    var blob = new Blob(["\\ufeff" + toCsv(list)], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = APP + "_" + me.room + ".csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  /* ---------- 연결 ---------- */

  $("w-enter").onclick = function () { enter(false); };
  $("w-solo").onclick = function () { enter(true); };
  $("w-teacher").onclick = function () { show("teacher"); };
  $("w-submit").onclick = submit;
  $("w-leave").onclick = function () {
    if (timer) { clearInterval(timer); }
    if (draftTimer) { clearInterval(draftTimer); }
    show("gate");
  };

  $("t-make").onclick = teacherMake;
  $("t-open").onclick = function () {
    var code = onlyDigits(prompt("방 코드 6자리를 넣어 주세요.") || "", 6);
    if (code.length === 6) { teacherOpen(code, ""); }
  };
  $("t-back").onclick = function () { if (timer) { clearInterval(timer); } show("gate"); };
  $("t-refresh").onclick = teacherRefresh;
  $("t-csv").onclick = download;
  $("t-detail").onclick = function () {
    var open = $("t-wrap").className.indexOf("hide") < 0;
    $("t-wrap").className = open ? "scroll hide" : "scroll";
    this.textContent = open ? "낱낱이 보기 켜기" : "낱낱이 보기 끄기";
  };
  $("t-present").onclick = function () {
    paintPresent(window.__wiseRows || []);
    show("present");
  };
  $("p-close").onclick = function () { show("teacher"); };
  $("t-lock").onclick = function () {
    dbPut(me.room + "/meta/locked", true).then(function () { alert("방을 잠갔어요."); });
  };
  $("t-copy").onclick = function () {
    var code = $("t-code").textContent;
    var done = function () { $("t-copy").textContent = "복사됨";
      setTimeout(function () { $("t-copy").textContent = "복사"; }, 1500); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(code).then(done)["catch"](function () { fallbackCopy(code, done); });
    } else { fallbackCopy(code, done); }
  };

  /* 상단바는 어느 화면에서나 계속 보인다. 링크는 새 창으로 열어 삽입 화면을 가두지 않는다. */
  /* 번호는 앱이 만든다. 아이들이 스스로 정하고 외우게 하면 열두 주 뒤에 거의 잊는다.
     한 번 만든 번호는 이 기기에 남아 다음 차시와 사후 설문까지 따라온다. */
  function makeStudentCode() {
    var out = "";
    for (var i = 0; i < 4; i++) { out += String(Math.floor(Math.random() * 10)); }
    return out;
  }
  try {
    var savedCode = localStorage.getItem(CODE_KEY);
    if (!savedCode || savedCode.length !== 4) {
      savedCode = makeStudentCode();
      localStorage.setItem(CODE_KEY, savedCode);
    }
    if ($("w-code")) { $("w-code").value = savedCode; }
  } catch (e) {
    if ($("w-code") && !$("w-code").value) { $("w-code").value = makeStudentCode(); }
  }

  /* 미리보기 모드. 주소에 ?shot=화면이름 을 붙이면 둘러보기로 들어가 그 화면을 연다.
     교사 안내 자료의 화면 캡처를 자동으로 뜨기 위한 것이다. fill=1 이면 예시값을 채운다. */
  function shotMode() {
    var q = "";
    try { q = window.location && window.location.search ? window.location.search : ""; } catch (e) { return; }
    if (q.indexOf("shot=") < 0) { return; }
    var val = q.split("shot=")[1].split("&")[0];
    try { val = decodeURIComponent(val); } catch (e) {}
    $("w-nick").value = "미리보기";
    enter(true);
    if (q.indexOf("fill=1") >= 0 && typeof activityAutofill === "function") {
      try { activityAutofill(); } catch (e) {}
    }
    if (val && val !== "stage") {
      try { wiseGo(val); } catch (e) {}
    }
  }

  try { shotMode(); } catch (e) {}

  $("w-restart").onclick = function () {
    if (timer) { clearInterval(timer); }
    if (draftTimer) { clearInterval(draftTimer); }
    show("gate");
  };

  /* 입장 화면에 이 활동을 소개하는 그림을 깐다. 혼자 열어 본 학생을 위한 것이다. */
  if (typeof activityIntro === "function") {
    try {
      $("w-intro").innerHTML = activityIntro();
      $("w-intro").className = "intro";
    } catch (e) {}
  }

  /* 자동 검사용 통로. 수업 화면에는 영향이 없다. */
  if (typeof window !== "undefined") {
    window.__wiseTest = {
      app: APP,
      activityHtml: activityHtml,
      activityInit: activityInit,
      activityCollect: activityCollect,
      teacherSummary: teacherSummary,
      presentHtml: (typeof presentHtml === "function") ? presentHtml : null,
      activityAutofill: (typeof activityAutofill === "function") ? activityAutofill : null,
      setMe: function (v) { me = v; }
    };
  }

  function fallbackCopy(text, done) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); done(); } catch (e) { alert(text); }
    document.body.removeChild(ta);
  }
})();
</script>
"""
