# -*- coding: utf-8 -*-
"""차시별 활동 화면 5종. 12개 앱이 이 중 하나를 쓴다."""
import json


def js(value):
    return json.dumps(value, ensure_ascii=False)


def buckets(cards, buckets_, ask_reason=True):
    """카드를 N칸으로 나누고 까닭을 쓴다. (4·5·6차시)"""
    return u"""
  var CARDS = %s;
  var BUCKETS = %s;
  var ASK_REASON = %s;

  function activityHtml() {
    var h = '<div class="card"><h2>카드를 알맞은 칸에 놓아요</h2>' +
      '<p class="muted">칸을 고르면 색이 바뀌어요. 왜 그렇게 생각했는지도 한 줄 써 주세요.</p></div>';
    for (var i = 0; i < CARDS.length; i++) {
      h += '<div class="card"><h3>' + (i + 1) + '. ' + esc(CARDS[i]) + '</h3><div class="row">';
      for (var b = 0; b < BUCKETS.length; b++) {
        h += '<button type="button" class="chip pick" data-c="' + i + '" data-b="' + b +
          '" style="width:auto;margin:0">' + esc(BUCKETS[b].label) + '</button>';
      }
      h += '</div>';
      if (ASK_REASON) {
        h += '<label for="r' + i + '">왜 그렇게 생각했나요</label>' +
          '<input id="r' + i + '" maxlength="80" placeholder="한 줄로 써요">';
      }
      h += '</div>';
    }
    return h;
  }

  var choice = {};

  function activityInit(saved) {
    if (saved && saved.choice) { choice = saved.choice; }
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      btns[i].onclick = function () {
        var c = this.getAttribute("data-c");
        choice[c] = this.getAttribute("data-b");
        paint();
      };
    }
    if (saved && saved.reasons) {
      for (var k in saved.reasons) {
        if (saved.reasons.hasOwnProperty(k) && $("r" + k)) { $("r" + k).value = saved.reasons[k]; }
      }
    }
    paint();
  }

  function paint() {
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      var c = btns[i].getAttribute("data-c");
      var b = btns[i].getAttribute("data-b");
      btns[i].className = "chip pick" + (choice[c] === b ? " on" : "");
    }
  }

  function activityCollect() {
    var done = 0, reasons = {};
    for (var i = 0; i < CARDS.length; i++) {
      if (choice[i] !== undefined) { done++; }
      if (ASK_REASON && $("r" + i)) { reasons[i] = $("r" + i).value.trim(); }
    }
    if (done === 0) {
      $("w-msg").innerHTML = '<span class="warn">카드를 하나라도 놓아 주세요.</span>';
      return null;
    }
    return { choice: choice, reasons: reasons, done: done, total: CARDS.length };
  }

  function teacherSummary(list) {
    var h = '<div class="scroll"><table><tr><th>카드</th>';
    for (var b = 0; b < BUCKETS.length; b++) { h += "<th>" + esc(BUCKETS[b].label) + "</th>"; }
    h += "<th>갈림</th></tr>";
    for (var i = 0; i < CARDS.length; i++) {
      var counts = [], max = 0, sum = 0;
      for (var b = 0; b < BUCKETS.length; b++) { counts[b] = 0; }
      for (var k = 0; k < list.length; k++) {
        var v = list[k].payload && list[k].payload.choice ? list[k].payload.choice[i] : undefined;
        if (v !== undefined) { counts[v] = (counts[v] || 0) + 1; sum++; }
      }
      for (var b2 = 0; b2 < BUCKETS.length; b2++) { if (counts[b2] > max) { max = counts[b2]; } }
      var split = sum > 0 && max / sum < 0.7;
      h += "<tr><td>" + esc(CARDS[i]) + "</td>";
      for (var b3 = 0; b3 < BUCKETS.length; b3++) { h += "<td>" + counts[b3] + "</td>"; }
      h += "<td>" + (split ? '<span class="warn">의견 갈림</span>' : "") + "</td></tr>";
    }
    return h + "</table></div>";
  }
""" % (js(cards), js(buckets_), "true" if ask_reason else "false")


def form(fields, gated=False):
    """단계별 기록판. gated 면 앞 단계를 채워야 다음이 열린다. (1·2·3·9·11·12차시)"""
    return u"""
  var FIELDS = %s;
  var GATED = %s;

  function activityHtml() {
    var h = "";
    for (var i = 0; i < FIELDS.length; i++) {
      var f = FIELDS[i];
      h += '<div class="card" id="fc' + i + '"><h2>' + (i + 1) + '. ' + esc(f.label) + '</h2>';
      if (f.hint) { h += '<p class="muted">' + esc(f.hint) + '</p>'; }
      h += '<textarea id="f' + i + '" maxlength="600" placeholder="' + esc(f.ph || "") + '"></textarea>';
      h += '</div>';
    }
    return h;
  }

  function activityInit(saved) {
    for (var i = 0; i < FIELDS.length; i++) {
      if (saved && saved.values && saved.values[i] && $("f" + i)) {
        $("f" + i).value = saved.values[i];
      }
      if ($("f" + i)) { $("f" + i).oninput = gate; }
    }
    gate();
  }

  function gate() {
    if (!GATED) { return; }
    var open = true;
    for (var i = 0; i < FIELDS.length; i++) {
      var box = $("fc" + i), ta = $("f" + i);
      if (!box || !ta) { continue; }
      ta.disabled = !open;
      box.style.opacity = open ? "1" : "0.45";
      if (open && ta.value.trim().length < 5) { open = false; }
    }
  }

  function activityCollect() {
    var values = [], filled = 0;
    for (var i = 0; i < FIELDS.length; i++) {
      var v = $("f" + i) ? $("f" + i).value.trim() : "";
      values.push(v);
      if (v) { filled++; }
    }
    if (filled === 0) {
      $("w-msg").innerHTML = '<span class="warn">한 칸이라도 써 주세요.</span>';
      return null;
    }
    return { values: values, filled: filled, total: FIELDS.length };
  }

  function teacherSummary(list) {
    var h = '<div class="scroll"><table><tr><th>단계</th><th>쓴 사람</th><th>진행</th></tr>';
    for (var i = 0; i < FIELDS.length; i++) {
      var n = 0;
      for (var k = 0; k < list.length; k++) {
        var v = list[k].payload && list[k].payload.values ? list[k].payload.values[i] : "";
        if (v) { n++; }
      }
      var pct = list.length ? Math.round(n * 100 / list.length) : 0;
      h += "<tr><td>" + esc(FIELDS[i].label) + "</td><td>" + n + "명</td>" +
        '<td><div class="bar"><i style="width:' + pct + '%%"></i></div></td></tr>';
    }
    return h + "</table></div>";
  }
""" % (js(fields), "true" if gated else "false")


def selfcheck(items, promises=3):
    """익명 자가 점검. 개인 결과를 교사 화면에 띄우지 않는다. (10차시)"""
    return u"""
  var ITEMS = %s;
  var PROMISES = %d;

  function activityHtml() {
    var h = '<div class="card"><h2>일주일 동안 나는 어땠나요</h2>' +
      '<p class="muted">솔직하게 골라 주세요. 누가 무엇을 골랐는지는 아무에게도 보이지 않아요.</p></div>';
    for (var i = 0; i < ITEMS.length; i++) {
      h += '<div class="card"><h3>' + esc(ITEMS[i]) + '</h3><div class="row">';
      var opts = ["거의 없음", "가끔", "자주", "아주 자주"];
      for (var o = 0; o < opts.length; o++) {
        h += '<button type="button" class="chip pick" data-i="' + i + '" data-v="' + o +
          '" style="width:auto;margin:0">' + opts[o] + '</button>';
      }
      h += '</div></div>';
    }
    h += '<div class="card"><h2>AI가 못 하는 일</h2>' +
      '<textarea id="cant" maxlength="300" placeholder="예: 친구와 화해하기"></textarea></div>';
    h += '<div class="card"><h2>내 디지털 웰빙 약속</h2>';
    for (var p = 0; p < PROMISES; p++) {
      h += '<label for="p' + p + '">약속 ' + (p + 1) + '</label>' +
        '<input id="p' + p + '" maxlength="80" placeholder="구체적으로 써요">';
    }
    h += '</div>';
    h += '<div class="safe">힘든 마음은 AI가 아니라 믿을 수 있는 어른에게 먼저 말해요.</div>';
    return h;
  }

  var pick = {};

  function activityInit(saved) {
    if (saved && saved.pick) { pick = saved.pick; }
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      btns[i].onclick = function () {
        pick[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint();
      };
    }
    if (saved) {
      if (saved.cant && $("cant")) { $("cant").value = saved.cant; }
      for (var p = 0; p < PROMISES; p++) {
        if (saved.promises && saved.promises[p] && $("p" + p)) { $("p" + p).value = saved.promises[p]; }
      }
    }
    paint();
  }

  function paint() {
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      var k = btns[i].getAttribute("data-i");
      var v = btns[i].getAttribute("data-v");
      btns[i].className = "chip pick" + (pick[k] === v ? " on" : "");
    }
  }

  function activityCollect() {
    var promises = [];
    for (var p = 0; p < PROMISES; p++) {
      promises.push($("p" + p) ? $("p" + p).value.trim() : "");
    }
    var n = 0;
    for (var k in pick) { if (pick.hasOwnProperty(k)) { n++; } }
    if (n === 0) {
      $("w-msg").innerHTML = '<span class="warn">하나라도 골라 주세요.</span>';
      return null;
    }
    return { pick: pick, cant: $("cant") ? $("cant").value.trim() : "", promises: promises };
  }

  function teacherSummary(list) {
    var h = '<p class="muted">개인 응답은 보이지 않습니다. 학급 익명 집계만 표시합니다.</p>';
    h += '<div class="scroll"><table><tr><th>항목</th><th>거의 없음</th><th>가끔</th><th>자주</th><th>아주 자주</th></tr>';
    for (var i = 0; i < ITEMS.length; i++) {
      var c = [0, 0, 0, 0];
      for (var k = 0; k < list.length; k++) {
        var v = list[k].payload && list[k].payload.pick ? list[k].payload.pick[i] : undefined;
        if (v !== undefined) { c[v]++; }
      }
      h += "<tr><td>" + esc(ITEMS[i]) + "</td><td>" + c[0] + "</td><td>" + c[1] +
        "</td><td>" + c[2] + "</td><td>" + c[3] + "</td></tr>";
    }
    return h + "</table></div>";
  }
""" % (js(items), promises)


def vote(criteria):
    """조항을 제안하고 투표한다. (7차시)"""
    return u"""
  var CRITERIA = %s;
  var proposals = [];

  function activityHtml() {
    var h = '<div class="card"><h2>우리 모둠이 맡은 기준</h2>' +
      '<label for="crit">기준 고르기</label><select id="crit">';
    for (var i = 0; i < CRITERIA.length; i++) {
      h += '<option value="' + i + '">' + esc(CRITERIA[i]) + "</option>";
    }
    h += '</select>' +
      '<label for="mean">우리 말로 바꾼 뜻</label>' +
      '<input id="mean" maxlength="80" placeholder="예: 내 생각을 먼저 만들라는 뜻">' +
      '<label for="claus">우리 반이 지킬 약속 문장</label>' +
      '<textarea id="claus" maxlength="200" placeholder="하지 마라 대신 이렇게 하면 된다로 써요"></textarea>' +
      '<p class="muted">제출하면 아래 목록에 올라가고, 학급이 투표할 수 있어요.</p></div>';
    h += '<div class="card"><h2>제안된 약속에 투표하기</h2>' +
      '<div class="row"><button type="button" id="reload" class="ghost">목록 새로고침</button></div>' +
      '<div id="plist" style="margin-top:12px"></div></div>';
    return h;
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.crit !== undefined && $("crit")) { $("crit").value = saved.crit; }
      if (saved.mean && $("mean")) { $("mean").value = saved.mean; }
      if (saved.clause && $("claus")) { $("claus").value = saved.clause; }
    }
    $("reload").onclick = reload;
    reload();
  }

  function reload() {
    if (me.solo) { $("plist").innerHTML = '<p class="muted">혼자 체험 중에는 목록이 없어요.</p>'; return; }
    dbGet(me.room + "/entries").then(function (data) {
      proposals = [];
      for (var k in data) {
        if (data.hasOwnProperty(k) && data[k].payload && data[k].payload.clause) {
          proposals.push({ key: k, nick: data[k].nick, p: data[k].payload });
        }
      }
      render();
    })["catch"](function () {});
  }

  function render() {
    if (!proposals.length) { $("plist").innerHTML = '<p class="muted">아직 제안이 없어요.</p>'; return; }
    var h = "";
    for (var i = 0; i < proposals.length; i++) {
      var p = proposals[i];
      h += '<div class="card" style="margin-bottom:8px"><span class="pill">' +
        esc(CRITERIA[p.p.crit] || "") + '</span><p style="margin:8px 0">' + esc(p.p.clause) + '</p>' +
        '<button type="button" class="ghost vote" data-k="' + esc(p.key) + '">이 약속에 찬성</button></div>';
    }
    $("plist").innerHTML = h;
    var vs = document.querySelectorAll("#plist .vote");
    for (var j = 0; j < vs.length; j++) {
      vs[j].onclick = function () {
        var key = this.getAttribute("data-k");
        dbPush(me.room + "/votes", { key: key, nick: me.nick, at: Date.now() });
        this.textContent = "찬성했어요";
        this.disabled = true;
      };
    }
  }

  function activityCollect() {
    var clause = $("claus") ? $("claus").value.trim() : "";
    if (clause.length < 5) {
      $("w-msg").innerHTML = '<span class="warn">약속 문장을 써 주세요.</span>';
      return null;
    }
    return {
      crit: Number($("crit").value),
      mean: $("mean").value.trim(),
      clause: clause
    };
  }

  function teacherSummary(list) {
    var h = '<div class="scroll"><table><tr><th>기준</th><th>제안된 약속</th><th>제안자</th></tr>';
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.clause) { continue; }
      h += "<tr><td>" + esc(CRITERIA[p.crit] || "") + "</td><td>" + esc(p.clause) +
        "</td><td>" + esc(list[i].nick) + "</td></tr>";
    }
    return h + "</table></div>";
  }
""" % (js(criteria),)


def board():
    """교사 승인 뒤 공개되는 게시판. 이미지 업로드 없음. (8차시)"""
    return u"""
  function activityHtml() {
    return '<div class="card"><h2>역할 나누기</h2>' +
      '<label for="human">사람이 할 일</label>' +
      '<textarea id="human" maxlength="300" placeholder="예: 문구 정하기, 배치 정하기"></textarea>' +
      '<label for="ai">AI에게 맡길 일</label>' +
      '<textarea id="ai" maxlength="300" placeholder="예: 배경 그림 만들기"></textarea></div>' +
      '<div class="card"><h2>우리 모둠 캠페인 문구</h2>' +
      '<label for="title">제목</label><input id="title" maxlength="60">' +
      '<label for="body">문구</label><textarea id="body" maxlength="400"></textarea></div>' +
      '<div class="card"><h2>AI 활용 표기</h2>' +
      '<p class="muted">무엇을 AI로 만들었는지 밝히는 것이 정직한 방법이에요.</p>' +
      '<textarea id="credit" maxlength="300" placeholder="예: 배경 그림은 AI로 만들고 배치는 우리가 다시 잡았습니다"></textarea></div>' +
      '<div class="safe">사진 올리기 기능은 없어요. 완성한 자료는 인쇄물이나 선생님 화면으로 함께 봐요.</div>';
  }

  function activityInit(saved) {
    var ids = ["human", "ai", "title", "body", "credit"];
    for (var i = 0; i < ids.length; i++) {
      if (saved && saved[ids[i]] && $(ids[i])) { $(ids[i]).value = saved[ids[i]]; }
    }
  }

  function activityCollect() {
    var out = {}, ids = ["human", "ai", "title", "body", "credit"];
    for (var i = 0; i < ids.length; i++) { out[ids[i]] = $(ids[i]) ? $(ids[i]).value.trim() : ""; }
    if (!out.title || !out.body) {
      $("w-msg").innerHTML = '<span class="warn">제목과 문구를 써 주세요.</span>';
      return null;
    }
    if (!out.credit) {
      $("w-msg").innerHTML = '<span class="warn">AI 활용 표기를 빠뜨렸어요. 무엇을 AI로 만들었는지 써 주세요.</span>';
      return null;
    }
    out.approved = false;
    return out;
  }

  function teacherSummary(list) {
    var h = '<p class="muted">교사가 승인한 것만 학급에 공개합니다.</p>';
    h += '<div class="scroll"><table><tr><th>모둠</th><th>제목</th><th>문구</th><th>AI 활용 표기</th></tr>';
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      h += "<tr><td>" + esc(list[i].group || list[i].nick) + "</td><td>" + esc(p.title) +
        "</td><td>" + esc(p.body) + "</td><td>" +
        (p.credit ? esc(p.credit) : '<span class="warn">표기 없음</span>') + "</td></tr>";
    }
    return h + "</table></div>";
  }
"""
