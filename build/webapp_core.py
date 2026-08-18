# -*- coding: utf-8 -*-
"""12개 웹앱이 공유하는 단일 HTML 골격.

- Google Sites 소스 코드 삽입용 단일 파일. 외부 CDN 참조 없음.
- Firebase REST + 3초 폴링. SDK 번들을 인라인하지 않는다.
- 정규식에 역슬래시 이스케이프를 쓰지 않는다. (Apps Script 가 파괴한다)
"""

TEMPLATE = u"""<div id="wise-app">
<style>
#wise-app *,#wise-app *::before,#wise-app *::after{box-sizing:border-box}
#wise-app{--ink:#1f2937;--muted:#6b7280;--line:#e5e7eb;--paper:#fff;--bg:#f9fafb;
--accent:__ACCENT__;--accent-soft:__ACCENT_SOFT__;
font-family:"Pretendard","Malgun Gothic","맑은 고딕",system-ui,sans-serif;
color:var(--ink);background:var(--bg);line-height:1.6;font-size:16px;
padding:16px;max-width:1000px;margin:0 auto}
#wise-app h1,#wise-app h2,#wise-app h3{margin:0;font-weight:700;line-height:1.3}
#wise-app .hd{background:var(--accent);color:#fff;border-radius:14px;padding:18px 20px;margin-bottom:14px}
#wise-app .hd h1{font-size:22px}
#wise-app .hd p{margin:6px 0 0;font-size:14px;opacity:.92}
#wise-app .card{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:18px;margin-bottom:14px}
#wise-app .card h2{font-size:18px;margin-bottom:10px}
#wise-app .row{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
#wise-app label{display:block;font-size:14px;color:var(--muted);margin:10px 0 4px}
#wise-app input,#wise-app textarea,#wise-app select{
width:100%;font:inherit;font-size:18px;padding:12px 14px;border:1px solid var(--line);
border-radius:10px;background:#fff;color:var(--ink)}
#wise-app textarea{min-height:96px;resize:vertical}
#wise-app button{font:inherit;font-size:16px;font-weight:600;min-height:48px;padding:12px 18px;
border-radius:10px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer}
#wise-app button.ghost{background:#fff;color:var(--accent)}
#wise-app button.plain{background:#fff;color:var(--muted);border-color:var(--line)}
#wise-app button:disabled{opacity:.45;cursor:not-allowed}
#wise-app .code{font-size:34px;font-weight:800;letter-spacing:.14em;color:var(--accent)}
#wise-app .muted{color:var(--muted);font-size:14px}
#wise-app .pill{display:inline-block;padding:4px 10px;border-radius:999px;background:var(--accent-soft);
color:var(--accent);font-size:13px;font-weight:700}
#wise-app .hide{display:none}
#wise-app .bucket{border:2px dashed var(--line);border-radius:12px;padding:12px;min-height:120px;background:#fff}
#wise-app .bucket h3{font-size:15px;margin-bottom:8px}
#wise-app .grid{display:grid;gap:12px}
#wise-app .chip{display:block;width:100%;text-align:left;padding:12px 14px;margin-bottom:8px;
border:1px solid var(--line);border-radius:10px;background:#fff;color:var(--ink);font-weight:500;min-height:48px}
#wise-app .chip.on{border-color:var(--accent);background:var(--accent-soft)}
#wise-app .bar{height:14px;border-radius:7px;background:var(--line);overflow:hidden}
#wise-app .bar>i{display:block;height:100%;background:var(--accent)}
#wise-app table{width:100%;border-collapse:collapse;font-size:14px}
#wise-app th,#wise-app td{border:1px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
#wise-app th{background:var(--bg);font-weight:700}
#wise-app .scroll{overflow-x:auto;-webkit-overflow-scrolling:touch}
#wise-app .safe{margin-top:14px;padding:12px 14px;border-radius:10px;background:#fff7ed;
border:1px solid #fed7aa;color:#9a3412;font-size:14px}
#wise-app .ok{color:#15803d;font-weight:600}
#wise-app .warn{color:#b45309;font-weight:600}
#wise-app .foot{text-align:center;color:var(--muted);font-size:12px;padding:14px 0}
@media (max-width:640px){#wise-app{padding:10px;font-size:15px}#wise-app .hd h1{font-size:19px}}
@media (prefers-reduced-motion:reduce){#wise-app *{transition:none!important;animation:none!important}}
</style>

<div class="hd">
  <h1>__APP_NAME__</h1>
  <p>__SUBTITLE__</p>
</div>

<!-- 입장 -->
<section id="gate" class="card">
  <h2>들어가기</h2>
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div>
      <label for="w-room">방 코드 6자리</label>
      <input id="w-room" inputmode="numeric" maxlength="6" placeholder="예: 482913">
    </div>
    <div>
      <label for="w-pw">비밀번호 4자리</label>
      <input id="w-pw" inputmode="numeric" maxlength="4" placeholder="예: 1234">
    </div>
  </div>
  <div class="grid" style="grid-template-columns:1fr 1fr">
    <div>
      <label for="w-nick">닉네임</label>
      <input id="w-nick" maxlength="12" placeholder="이름 말고 별명을 써요">
    </div>
    <div>
      <label for="w-group">모둠</label>
      <input id="w-group" maxlength="10" placeholder="예: 3모둠">
    </div>
  </div>
  <div class="row" style="margin-top:14px">
    <button id="w-enter">입장하기</button>
    <button id="w-solo" class="ghost">혼자 체험해 보기</button>
    <button id="w-teacher" class="plain">선생님 화면</button>
  </div>
  <p id="w-gate-msg" class="muted" style="margin-top:10px"></p>
  <div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>
</section>

<!-- 학생 활동 -->
<section id="stage" class="hide">
  <div class="card">
    <div class="row" style="justify-content:space-between">
      <span class="pill" id="w-who"></span>
      <span class="muted" id="w-sync">저장 준비됨</span>
    </div>
  </div>
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
    <div class="row">
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
        <button id="t-refresh" class="ghost">새로고침</button>
        <button id="t-csv" class="ghost">CSV 내려받기</button>
        <button id="t-lock" class="plain">방 잠그기</button>
      </div>
    </div>
  </div>
  <div id="t-board" class="card hide">
    <h2>제출 현황 <span class="pill" id="t-count">0명</span></h2>
    <div id="t-summary"></div>
    <div class="scroll" style="margin-top:12px"><table id="t-table"></table></div>
  </div>
</section>

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

  var $ = function (id) { return document.getElementById(id); };
  var me = { room: "", pw: "", nick: "", group: "", solo: false };
  var timer = null;

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

  function show(id) {
    var ids = ["gate", "stage", "teacher"];
    for (var i = 0; i < ids.length; i++) {
      $(ids[i]).className = ids[i] === id ? "" : "hide";
    }
  }

  /* ---------- 활동 (차시별) ---------- */

__ACTIVITY__

  /* ---------- 학생 흐름 ---------- */

  function enter(solo) {
    var room = onlyDigits($("w-room").value, 6);
    var pw = onlyDigits($("w-pw").value, 4);
    var nick = $("w-nick").value.trim();
    var group = $("w-group").value.trim();

    if (!nick) { $("w-gate-msg").textContent = "닉네임을 써 주세요."; return; }
    if (!solo && room.length !== 6) { $("w-gate-msg").textContent = "방 코드 6자리를 정확히 써 주세요."; return; }

    me = { room: solo ? "solo" : room, pw: pw, nick: nick, group: group, solo: !!solo };
    $("w-who").textContent = me.nick + (me.group ? " · " + me.group : "") +
      (me.solo ? " · 혼자 체험" : " · " + me.room);
    $("activity").innerHTML = activityHtml();
    activityInit(loadLocal());
    show("stage");
  }

  function loadLocal() {
    try { return JSON.parse(localStorage.getItem(LOCAL_KEY) || "null"); }
    catch (e) { return null; }
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
      nick: me.nick, group: me.group, app: APP,
      room: me.room, at: Date.now(), payload: payload
    };

    $("w-sync").textContent = "저장 중...";
    dbPush(me.room + "/entries", record).then(function () {
      $("w-sync").textContent = "저장됨";
      $("w-msg").innerHTML = '<span class="ok">제출했어요. 고쳐서 다시 제출해도 괜찮아요.</span>';
      sheetBackup(record);
    })["catch"](function () {
      $("w-sync").textContent = "저장 실패";
      $("w-msg").innerHTML = '<span class="warn">인터넷이 불안정해요. 잠시 뒤 다시 제출해 주세요.</span>';
    });
  }

  /* ---------- 교사 흐름 ---------- */

  function teacherMake() {
    var code = makeCode();
    var pw = onlyDigits($("w-pw").value, 4) || "0000";
    dbPut(code + "/meta", { app: APP, pw: pw, at: Date.now(), locked: false })
      .then(function () { teacherOpen(code, pw); })
      ["catch"](function () { alert("방을 만들지 못했어요. 인터넷을 확인해 주세요."); });
  }

  function teacherOpen(code, pw) {
    me.room = code;
    $("t-code").textContent = code;
    $("t-pw").textContent = "비밀번호 " + (pw || "-") + " · 이 화면을 닫아도 방은 사라지지 않아요.";
    $("t-room").className = "";
    $("t-board").className = "card";
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
      $("t-summary").innerHTML = teacherSummary(list);
      $("t-table").innerHTML = teacherTable(list);
      window.__wiseRows = list;
    })["catch"](function () {});
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
  $("w-leave").onclick = function () { if (timer) { clearInterval(timer); } show("gate"); };

  $("t-make").onclick = teacherMake;
  $("t-open").onclick = function () {
    var code = onlyDigits(prompt("방 코드 6자리를 넣어 주세요.") || "", 6);
    if (code.length === 6) { teacherOpen(code, ""); }
  };
  $("t-back").onclick = function () { if (timer) { clearInterval(timer); } show("gate"); };
  $("t-refresh").onclick = teacherRefresh;
  $("t-csv").onclick = download;
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

  /* 자동 검사용 통로. 수업 화면에는 영향이 없다. */
  if (typeof window !== "undefined") {
    window.__wiseTest = {
      app: APP,
      activityHtml: activityHtml,
      activityInit: activityInit,
      activityCollect: activityCollect,
      teacherSummary: teacherSummary,
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
