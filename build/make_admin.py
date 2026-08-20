# -*- coding: utf-8 -*-
"""관리자 페이지를 만든다. out/site/admin.html

여러 학급, 여러 차시의 결과를 한자리에서 본다.
학생 개인을 특정하지 않는다. 학급 단위 집계와 사전·사후 변화만 보여 준다.

로그인은 가벼운 잠금이다. 브라우저 안에서만 확인하므로 비밀을 지키는 장치가 아니다.
진짜 접근 제한은 Firebase 보안 규칙이 한다. 방 번호를 모르면 자료를 읽을 수 없다.
암호는 data/admin_code.txt 한 줄로 둔다. 없으면 wise2026 을 쓴다.
"""
import io
import os
import sys

import tasks as T

T.setup_console()

CODE_FILE = os.path.join(T.ROOT, "data", "admin_code.txt")
DEFAULT_CODE = "wise2026"


def admin_code():
    if os.path.exists(CODE_FILE):
        with io.open(CODE_FILE, encoding="utf-8") as f:
            code = f.read().strip()
        if code:
            return code
    return DEFAULT_CODE


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


PAGE = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>관리자 화면 · %(program)s</title>
<style>
:root{--cream:#F4EEE0;--cream-d:#EBE3D2;--paper:#fff;--ink:#101010;--ink2:#33312D;
--muted:#6F6A61;--line:#111;--green:#00D45A;--blue:#2B59E0;--sun:#FFE24B;
--sans:"Pretendard","Malgun Gothic","Apple SD Gothic Neo","Noto Sans KR",system-ui,sans-serif}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink2);font-family:var(--sans);line-height:1.7}
h1,h2,h3{margin:0;color:var(--ink);line-height:1.3;letter-spacing:-.02em}
.top{position:sticky;top:0;z-index:30;background:var(--cream);border-bottom:3px solid var(--line);
display:flex;gap:8px;align-items:center;padding:10px 16px;flex-wrap:wrap}
.top a,.top button{font-size:14px;font-weight:800;color:var(--ink);background:#fff;
border:2.5px solid var(--line);border-radius:999px;padding:8px 14px;text-decoration:none;cursor:pointer}
.top a:hover,.top button:hover{background:var(--sun)}
.wrap{max-width:1040px;margin:0 auto;padding:22px}
.card{background:var(--paper);border:3px solid var(--line);border-radius:16px;padding:20px;
margin-bottom:16px;box-shadow:6px 6px 0 var(--line)}
label{display:block;font-size:14px;font-weight:700;color:var(--muted);margin:12px 0 4px}
input,select{width:100%%;font:inherit;font-size:17px;padding:12px 14px;border:2.5px solid var(--line);
border-radius:12px;background:#fff}
button.go{font:inherit;font-size:16px;font-weight:800;border:2.5px solid var(--line);border-radius:12px;
background:var(--green);padding:12px 20px;cursor:pointer;min-height:48px}
button.ghost{background:#fff}
table{width:100%%;border-collapse:collapse;font-size:14px;margin-top:10px}
th,td{border:1.5px solid var(--line);padding:8px 10px;text-align:left;vertical-align:top}
th{background:var(--cream)}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.pill{display:inline-block;background:var(--sun);border:2px solid var(--line);border-radius:999px;
padding:3px 12px;font-size:13px;font-weight:800}
.muted{color:var(--muted);font-size:14px}
.hide{display:none}
.note{border:2.5px solid var(--line);border-radius:12px;background:var(--cream-d);padding:14px 16px;
font-size:14px;margin-top:12px}
.bar{height:16px;border-radius:8px;background:var(--cream-d);overflow:hidden;border:1.5px solid var(--line)}
.bar>i{display:block;height:100%%;background:var(--green)}
.foot{color:var(--muted);font-size:12px;text-align:center;padding:20px}
</style>
</head>
<body>
<nav class="top">
  <a href="index.html">홈으로 돌아가기</a>
  <a href="browse.html">둘러보기</a>
  <a href="apps.html">12차시 웹앱</a>
  <a href="survey.html">자기인식 진단</a>
  <span class="pill">관리자 화면</span>
</nav>

<div class="wrap">

<section class="card" id="login">
  <h1>관리자 화면</h1>
  <p class="muted" style="margin-top:8px">학급별 결과를 한자리에서 봅니다. 학생 개인은 보이지 않습니다.</p>
  <label for="code">관리자 암호</label>
  <input id="code" type="password" placeholder="연구회에서 받은 암호">
  <div class="row" style="margin-top:12px"><button class="go" id="login-btn">들어가기</button></div>
  <p class="muted" id="login-msg" style="margin-top:10px"></p>
  <div class="note"><b>개인정보를 모으지 않습니다.</b> 학생은 닉네임만 씁니다.
    이름, 학교, 학년, 반, 전화번호를 묻지 않습니다.
    모인 자료는 수업 프로그램을 개선하는 데만 쓰고 학년도가 끝나면 지웁니다.</div>
</section>

<section id="panel" class="hide">
  <section class="card">
    <h2>0. 전체 학급 불러오기</h2>
    <p class="muted">교사가 방을 만들면 구글 시트 <b>방목록</b> 탭에 쌓입니다.
      여기서 전체 학급을 한 번에 불러옵니다.</p>
    <div class="row">
      <button class="go" id="pull">시트에서 전체 학급 불러오기</button>
      <button class="go ghost" id="pull-all">불러온 학급 자료 모두 읽기</button>
    </div>
    <p class="muted" id="pull-msg" style="margin-top:10px"></p>
    <div id="sheetrooms" style="margin-top:12px"></div>
  </section>

  <section class="card">
    <h2>1. 볼 방 등록하기</h2>
    <p class="muted">교사가 만든 방 번호를 넣으면 이 브라우저에만 저장됩니다.
      방 번호를 모르면 아무 자료도 읽히지 않습니다.</p>
    <div class="row">
      <div style="flex:1;min-width:160px"><label for="app">차시</label>
        <select id="app">%(options)s</select></div>
      <div style="flex:1;min-width:160px"><label for="room">방 번호 6자리</label>
        <input id="room" inputmode="numeric" maxlength="6" placeholder="예: 482913"></div>
      <div style="flex:1;min-width:120px"><label for="tag">학급 이름표</label>
        <input id="tag" maxlength="12" placeholder="예: 5학년 1반"></div>
    </div>
    <div class="row" style="margin-top:12px">
      <button class="go" id="add">등록</button>
      <button class="go ghost" id="load">전부 불러오기</button>
      <button class="go ghost" id="csv">CSV 내려받기</button>
      <button class="go ghost" id="clear">등록 지우기</button>
    </div>
    <div id="rooms" style="margin-top:12px"></div>
  </section>

  <section class="card">
    <h2>1-2. 사전·사후 한눈에 보기 (시트 집계)</h2>
    <p class="muted">시트에 쌓인 전체 응답으로 계산합니다. 학생 코드가 같은 응답끼리 이어
      개인 변화량도 함께 냅니다. 개인 응답은 보여 주지 않습니다.</p>
    <div id="dash"><p class="muted">위에서 불러오기를 누르세요.</p></div>
  </section>

  <section class="card">
    <h2>2. 사전·사후 설문</h2>
    <p class="muted">문항별 평균과 변화량입니다. 개인 응답은 보여 주지 않습니다.</p>
    <div id="survey"><p class="muted">방을 등록하고 불러오기를 누르세요.</p></div>
  </section>

  <section class="card">
    <h2>2-2. 휴먼스킬 영역별 변화</h2>
    <p class="muted">문항을 다섯 영역으로 묶어 사전과 사후를 견줍니다.</p>
    <div id="skills"><p class="muted">설문 방을 등록하고 불러오면 나옵니다.</p></div>
  </section>

  <section class="card">
    <h2>3. 차시별 참여</h2>
    <div id="apps"><p class="muted">불러오면 차시마다 제출 수가 나옵니다.</p></div>
    <div id="counts" style="margin-top:12px"></div>
  </section>

  <section class="card">
    <h2>4. 자료 관리</h2>
    <p class="muted">학년도가 끝나면 Firebase 콘솔에서 <code>/wise</code> 경로를 지웁니다.
      백업 시트도 학급 단위 통계만 남기고 개별 행을 지웁니다.</p>
    <div class="note">이 화면의 암호는 가벼운 잠금입니다. 실제 보호는 방 번호와 Firebase 규칙이 합니다.
      방 번호는 학급 밖으로 알리지 않습니다.</div>
  </section>
</section>

</div>
<p class="foot">%(copyright)s</p>

<script>
(function () {
  "use strict";
  var CODE = "%(code)s";
  var DB = "https://remind-c2610-default-rtdb.firebaseio.com";
  var KEY = "wise_admin_rooms";
  var SHEET = "%(sheet)s";
  var SKILLS = [
    { name: "주체성", items: [1, 6] },
    { name: "비판적 사고", items: [2, 5] },
    { name: "윤리적 사고", items: [3] },
    { name: "성찰적 사고", items: [4, 8] },
    { name: "사회·관계적 사고", items: [7] }
  ];
  var SURVEY_ITEMS = %(items)s;
  var APPS = %(apps)s;
  var rows = [];
  var data = {};

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function load() {
    try { rows = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { rows = []; }
  }
  function save() {
    try { localStorage.setItem(KEY, JSON.stringify(rows)); } catch (e) {}
  }
  function onlyDigits(s, n) {
    var out = "";
    for (var i = 0; i < s.length && out.length < n; i++) {
      if (s.charAt(i) >= "0" && s.charAt(i) <= "9") { out += s.charAt(i); }
    }
    return out;
  }

  $("login-btn").onclick = function () {
    if ($("code").value.trim() !== CODE) {
      $("login-msg").textContent = "암호가 다릅니다.";
      return;
    }
    $("login").className = "card hide";
    $("panel").className = "";
    load();
    paintRooms();
  };

  function paintRooms() {
    if (!rows.length) {
      $("rooms").innerHTML = '<p class="muted">등록된 방이 없습니다.</p>';
      return;
    }
    var h = '<table><tr><th>차시</th><th>방 번호</th><th>학급 이름표</th><th>불러온 제출</th></tr>';
    for (var i = 0; i < rows.length; i++) {
      var key = rows[i].app + "/" + rows[i].room;
      h += "<tr><td>" + esc(rows[i].label) + "</td><td>" + esc(rows[i].room) + "</td><td>" +
        esc(rows[i].tag) + "</td><td>" + (data[key] ? data[key].length + "건" : "-") + "</td></tr>";
    }
    $("rooms").innerHTML = h + "</table>";
  }

  /* 시트에서 읽어 온다. fetch 가 막히면 JSONP 로 한 번 더 시도한다. */
  function askSheet(what, done, fail) {
    if (SHEET.indexOf("http") !== 0) { fail("시트 주소가 아직 없습니다."); return; }
    var url = SHEET + "?what=" + what;
    fetch(url)
      .then(function (r) { return r.json(); })
      .then(function (obj) { done(obj); })
      ["catch"](function () {
        var cbName = "wiseCb" + Math.floor(Math.random() * 100000);
        var timer = setTimeout(function () { fail("시트를 읽지 못했습니다."); }, 12000);
        window[cbName] = function (obj) {
          clearTimeout(timer);
          done(obj);
          try { delete window[cbName]; } catch (e) {}
        };
        var sc = document.createElement("script");
        sc.src = url + "&callback=" + cbName;
        sc.onerror = function () { clearTimeout(timer); fail("시트를 읽지 못했습니다."); };
        document.body.appendChild(sc);
      });
  }

  var sheetRooms = [];

  $("pull").onclick = function () {
    $("pull-msg").textContent = "불러오는 중입니다...";
    askSheet("rooms", function (obj) {
      sheetRooms = (obj && obj.rooms) || [];
      $("pull-msg").textContent = "학급 " + sheetRooms.length + "개를 불러왔습니다.";
      paintSheetRooms();
      loadDash();
    }, function (msg) {
      $("pull-msg").innerHTML = esc(msg) +
        " Apps Script 를 누구나 접근으로 배포했는지 확인해 주세요.";
    });
  };

  /* 시트가 돌려주는 시각은 모양이 여러 가지다. 사람이 읽는 모양으로 맞춘다. */
  function when(v) {
    if (!v) { return "-"; }
    var d = new Date(v);
    if (isNaN(d.getTime())) { return String(v).slice(0, 16); }
    function two(n) { return (n < 10 ? "0" : "") + n; }
    return d.getFullYear() + "-" + two(d.getMonth() + 1) + "-" + two(d.getDate()) +
      " " + two(d.getHours()) + ":" + two(d.getMinutes());
  }

  function paintSheetRooms() {
    if (!sheetRooms.length) {
      $("sheetrooms").innerHTML = '<p class="muted">시트에 방 기록이 아직 없습니다. 교사가 방을 만들면 쌓입니다.</p>';
      return;
    }
    var h = '<table><tr><th>차시</th><th>방 번호</th><th>학급 이름표</th><th>만든 때</th></tr>';
    for (var i = 0; i < sheetRooms.length; i++) {
      var r = sheetRooms[i];
      h += "<tr><td>" + esc(r.lesson || r.app) + "</td><td>" + esc(r.room) + "</td><td>" +
        esc(r.tag || "") + "</td><td>" + esc(when(r.at)) + "</td></tr>";
    }
    $("sheetrooms").innerHTML = h + "</table>";
  }

  $("pull-all").onclick = function () {
    if (!sheetRooms.length) { alert("먼저 전체 학급을 불러와 주세요."); return; }
    for (var i = 0; i < sheetRooms.length; i++) {
      var r = sheetRooms[i], found = false;
      for (var k = 0; k < rows.length; k++) {
        if (rows[k].app === r.app && rows[k].room === r.room) { found = true; break; }
      }
      if (found) { continue; }
      rows.push({ app: r.app, label: r.lesson || r.app, room: r.room, tag: r.tag || "" });
    }
    save();
    paintRooms();
    $("load").onclick();
  };

  function loadDash() {
    askSheet("survey", function (obj) { paintDash(obj); },
      function (msg) { $("dash").innerHTML = '<p class="muted">' + esc(msg) + '</p>'; });
    askSheet("counts", function (obj) { paintCounts(obj); }, function () {});
  }

  function paintDash(d) {
    if (!d || !d.items) { $("dash").innerHTML = '<p class="muted">아직 자료가 없습니다.</p>'; return; }
    var h = '<p class="muted">사전 ' + (d.preCount || 0) + '명 · 사후 ' + (d.postCount || 0) +
      '명 · 학생 코드로 이어진 사람 ' + (d.matched || 0) + '명</p>';
    h += '<table><tr><th>문항</th><th>사전</th><th>사후</th><th>변화</th></tr>';
    for (var i = 0; i < d.items.length; i++) {
      var it = d.items[i];
      var diff = (it.pre !== "" && it.post !== "") ? (Math.round((it.post - it.pre) * 100) / 100) : "-";
      h += "<tr><td>" + (i + 1) + "번</td><td>" + (it.pre === "" ? "-" : it.pre) + "</td><td>" +
        (it.post === "" ? "-" : it.post) + "</td><td>" + diff + "</td></tr>";
    }
    h += "</table>";
    if (d.matched) {
      h += '<p style="margin-top:12px">개인 변화 : 올라감 <b>' + d.up + '명</b> · 그대로 ' +
        d.same + '명 · 내려감 ' + d.down + '명 · 평균 변화량 ' + d.meanDiff + '</p>';
      h += '<p class="muted">평균만 보면 오른 사람과 내린 사람이 상쇄됩니다. 세 갈래를 함께 봅니다.</p>';
    }
    $("dash").innerHTML = h;
  }

  function paintCounts(d) {
    if (!d || !d.counts || !d.counts.length) { $("counts").innerHTML = ""; return; }
    var byLesson = {};
    for (var i = 0; i < d.counts.length; i++) {
      var c = d.counts[i];
      if (!byLesson[c.lesson]) { byLesson[c.lesson] = { people: 0, rooms: 0 }; }
      byLesson[c.lesson].people += c.people;
      byLesson[c.lesson].rooms += 1;
    }
    var h = '<h3>시트 기준 차시별 제출</h3><table><tr><th>차시</th><th>학급 수</th><th>제출한 사람</th></tr>';
    var keys = [];
    for (var k in byLesson) { if (byLesson.hasOwnProperty(k)) { keys.push(k); } }
    keys.sort();
    for (var j = 0; j < keys.length; j++) {
      h += "<tr><td>" + esc(keys[j]) + "</td><td>" + byLesson[keys[j]].rooms + "개</td><td>" +
        byLesson[keys[j]].people + "명</td></tr>";
    }
    $("counts").innerHTML = h + "</table>";
  }

  function paintSkills(pre, post) {
    function avgOf(list, nums) {
      var s = 0, n = 0;
      for (var i = 0; i < nums.length; i++) {
        var arr = list[nums[i] - 1] || [];
        for (var k = 0; k < arr.length; k++) { s += arr[k]; n += 1; }
      }
      return n ? s / n : null;
    }
    var h = '<table><tr><th>영역</th><th>사전</th><th>사후</th><th>변화</th><th>사후 수준</th></tr>';
    for (var i = 0; i < SKILLS.length; i++) {
      var a = avgOf(pre, SKILLS[i].items), b = avgOf(post, SKILLS[i].items);
      var d = (a !== null && b !== null) ? (b - a).toFixed(2) : "-";
      var w = b !== null ? Math.round(b * 20) : (a !== null ? Math.round(a * 20) : 0);
      h += "<tr><td>" + esc(SKILLS[i].name) + "</td><td>" + (a === null ? "-" : a.toFixed(2)) +
        "</td><td>" + (b === null ? "-" : b.toFixed(2)) + "</td><td>" + d +
        '</td><td><div class="bar"><i style="width:' + w + '%%"></i></div></td></tr>';
    }
    $("skills").innerHTML = h + "</table>";
  }

  $("add").onclick = function () {
    var room = onlyDigits($("room").value, 6);
    if (room.length !== 6) { alert("방 번호 6자리를 넣어 주세요."); return; }
    var sel = $("app");
    rows.push({ app: sel.value, label: sel.options[sel.selectedIndex].text,
      room: room, tag: $("tag").value.trim() });
    save();
    $("room").value = "";
    paintRooms();
  };

  $("clear").onclick = function () {
    if (!confirm("등록한 방 목록을 지울까요? 저장된 학생 자료는 지워지지 않습니다.")) { return; }
    rows = [];
    data = {};
    save();
    paintRooms();
    $("survey").innerHTML = '<p class="muted">방을 등록하고 불러오기를 누르세요.</p>';
    $("apps").innerHTML = '<p class="muted">불러오면 차시마다 제출 수가 나옵니다.</p>';
  };

  $("load").onclick = function () {
    if (!rows.length) { alert("먼저 방을 등록해 주세요."); return; }
    var left = rows.length;
    data = {};
    for (var i = 0; i < rows.length; i++) {
      (function (r) {
        fetch(DB + "/wise/" + r.app + "/" + r.room + "/entries.json")
          .then(function (res) { return res.json(); })
          .then(function (obj) {
            var list = [];
            for (var k in obj) { if (obj.hasOwnProperty(k)) { list.push(obj[k]); } }
            data[r.app + "/" + r.room] = list;
          })["catch"](function () { data[r.app + "/" + r.room] = []; })
          .then(function () {
            left -= 1;
            if (left <= 0) { paintRooms(); paintSurvey(); paintApps(); }
          });
      })(rows[i]);
    }
  };

  function latestByNick(list) {
    var box = {};
    for (var i = 0; i < list.length; i++) {
      var r = list[i];
      if (!box[r.nick] || (r.at || 0) > (box[r.nick].at || 0)) { box[r.nick] = r; }
    }
    var out = [];
    for (var n in box) { if (box.hasOwnProperty(n)) { out.push(box[n]); } }
    return out;
  }

  function paintSurvey() {
    var pre = [], post = [];
    for (var i = 0; i < SURVEY_ITEMS.length; i++) { pre[i] = []; post[i] = []; }
    var n = 0;
    for (var key in data) {
      if (!data.hasOwnProperty(key) || key.indexOf("survey/") !== 0) { continue; }
      var list = latestByNick(data[key]);
      for (var k = 0; k < list.length; k++) {
        var p = list[k].payload || {};
        if (!p.pick) { continue; }
        n += 1;
        for (var q = 0; q < SURVEY_ITEMS.length; q++) {
          var v = p.pick[q];
          if (v === undefined) { continue; }
          var sc = Number(v) + 1;
          if (q === 0) { sc = 6 - sc; }
          (p.when === "사후" ? post[q] : pre[q]).push(sc);
        }
      }
    }
    if (!n) {
      $("survey").innerHTML = '<p class="muted">설문 방을 등록하면 여기에 나옵니다. ' +
        '차시 목록에서 공통 설문을 고르고 방 번호를 넣으세요.</p>';
      return;
    }
    function avg(a) {
      if (!a.length) { return null; }
      var s = 0;
      for (var i = 0; i < a.length; i++) { s += a[i]; }
      return s / a.length;
    }
    var h = '<p class="muted">응답 ' + n + '명. 1번 문항은 역채점했습니다.</p>' +
      '<table><tr><th>문항</th><th>사전</th><th>사후</th><th>변화</th><th>사후 수준</th></tr>';
    for (var i2 = 0; i2 < SURVEY_ITEMS.length; i2++) {
      var a1 = avg(pre[i2]), a2 = avg(post[i2]);
      var d = (a1 !== null && a2 !== null) ? (a2 - a1).toFixed(2) : "-";
      var pct = a2 !== null ? Math.round(a2 * 20) : 0;
      h += "<tr><td>" + (i2 + 1) + ". " + esc(SURVEY_ITEMS[i2]) + "</td><td>" +
        (a1 === null ? "-" : a1.toFixed(2)) + "</td><td>" + (a2 === null ? "-" : a2.toFixed(2)) +
        "</td><td>" + d + '</td><td><div class="bar"><i style="width:' + pct + '%%"></i></div></td></tr>';
    }
    $("survey").innerHTML = h + "</table>";
    paintSkills(pre, post);
  }

  function paintApps() {
    var h = '<table><tr><th>차시</th><th>학급 이름표</th><th>제출한 사람</th><th>제출 시도</th></tr>';
    var any = false;
    for (var i = 0; i < rows.length; i++) {
      var key = rows[i].app + "/" + rows[i].room;
      var list = data[key] || [];
      any = any || list.length > 0;
      h += "<tr><td>" + esc(rows[i].label) + "</td><td>" + esc(rows[i].tag) + "</td><td>" +
        latestByNick(list).length + "명</td><td>" + list.length + "회</td></tr>";
    }
    $("apps").innerHTML = h + "</table>" +
      (any ? "" : '<p class="muted">아직 제출이 없습니다.</p>');
  }

  $("csv").onclick = function () {
    var lines = ["차시,학급,방번호,닉네임,제출시각,내용"];
    for (var i = 0; i < rows.length; i++) {
      var key = rows[i].app + "/" + rows[i].room;
      var list = data[key] || [];
      for (var k = 0; k < list.length; k++) {
        var r = list[k];
        lines.push([rows[i].label, rows[i].tag, rows[i].room, r.nick,
          new Date(r.at).toLocaleString("ko-KR"), JSON.stringify(r.payload)]
          .map(function (v) { return '"' + String(v).split('"').join('""') + '"'; }).join(","));
      }
    }
    var blob = new Blob(["\\ufeff" + lines.join("\\n")], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "wise_admin.csv";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };
})();
</script>
</body>
</html>
"""


def sheet_endpoint():
    """data/sheet_endpoint.txt 한 줄. 없으면 빈 값으로 두고 화면이 안내를 띄운다."""
    path = os.path.join(T.ROOT, "data", "sheet_endpoint.txt")
    if os.path.exists(path):
        with io.open(path, encoding="utf-8") as f:
            url = f.read().strip()
        if url.startswith("https://"):
            return url
    return ""


def build(data, site):
    import json
    opts = ['<option value="survey">공통 · 사전·사후 설문</option>']
    apps = [{"slug": "survey", "label": "공통 설문"}]
    for l in data["lessons"]:
        opts.append('<option value="%s">%d차시 · %s</option>'
                    % (esc(l["webapp"]["slug"]), l["no"], esc(l["webapp"]["name"])))
        apps.append({"slug": l["webapp"]["slug"], "label": "%d차시" % l["no"]})
    html = PAGE % {
        "program": esc(data["program"]["name"]),
        "copyright": esc(data["program"]["copyrightLine"]),
        "options": "".join(opts),
        "code": esc(admin_code()),
        "items": json.dumps([i["text"] for i in data["survey"]["items"]], ensure_ascii=False),
        "apps": json.dumps(apps, ensure_ascii=False),
        "sheet": sheet_endpoint(),
    }
    path = os.path.join(site, "admin.html")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    print("관리자 화면을 만들었다 : %s" % build(data, site))
    return 0


if __name__ == "__main__":
    sys.exit(main())
