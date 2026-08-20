# -*- coding: utf-8 -*-
"""12차시 프로젝트 발표와 성찰.

여정형으로 만든다. 폼 하나가 아니라 화면 아홉 장을 지나간다.

  이야기 → 전시장 허브 → 부스 차리기 → 표기표 만들기 → 약속 점검
  → 전시장 둘러보기 → 돌아보기 → 수료 카드 → 제출

이 앱의 핵심은 표기표다. 프로젝트를 만든 여덟 단계를 우리·함께·AI 로 나누면
표기 문장이 자라난다. 마지막 결정을 AI 로 두면 화면이 되묻는다.

6차시에서 겪은 사고를 되풀이하지 않는다.
  - 글을 쓰는 화면은 한 번만 그리고 다시 그리지 않는다.
  - 목록을 새로 고쳐도 쓰던 글은 상태에 담아 두었다가 되살린다.
  - 기다리는 자리에는 반드시 회전 표시나 뼈대를 깐다.
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  var STEPS = [
    "무엇을 만들지 정하기",
    "자료 모으기",
    "아이디어 여러 개 내기",
    "글과 문구 쓰기",
    "그림과 사진 만들기",
    "사실인지 확인하기",
    "넣을 것과 뺄 것 고르기",
    "마지막으로 결정하기"
  ];

  var ROLES = [
    { key: "me", name: "우리가 했어요", icon: "me" },
    { key: "both", name: "함께 했어요", icon: "both" },
    { key: "ai", name: "AI가 했어요", icon: "ai" }
  ];

  var PLEDGES = [
    "내 생각을 먼저 쓰고 나서 도움을 받았다",
    "AI가 알려 준 사실을 확인했다",
    "개인정보를 넣지 않았다",
    "AI가 한 일을 밝혔다",
    "마지막 결정은 우리가 했다"
  ];

  var DECIDE = STEPS.length - 1;

  var FIELDS = ["title", "made", "who", "broke", "before", "after", "vow"];

  var st = {
    text: {}, role: {}, kept: {}, notes: {}, noteDraft: {}, list: [], mine: [],
    badges: {}, opened: false, labeled: false, quiet: false
  };

  /* ---------- 도우미 ---------- */

  function val(id) {
    if ($(id) && $(id).parentNode) { return String($(id).value || "").trim(); }
    return String(st.text[id] || "").trim();
  }

  /* 화면에 쓴 글을 상태로 옮긴다. 나가기와 다시 그리기에서 글이 사라지지 않게 한다. */
  function stashText() {
    for (var i = 0; i < FIELDS.length; i++) {
      var el = $(FIELDS[i]);
      if (el && typeof el.value === "string") { st.text[FIELDS[i]] = String(el.value); }
    }
  }

  function countOf(obj) {
    var n = 0;
    for (var k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  /* 화면이 뚝뚝 끊기지 않게 아주 짧게 뜸을 들인다.
     움직임을 줄이기로 한 기기에서는 기다리지 않고 바로 그린다. */
  function softDelay(fn, ms) {
    var reduce = false;
    try {
      reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) {}
    if (reduce) { fn(); return; }
    setTimeout(fn, ms || 220);
  }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">전시장 여는 날</h2>' +
      wiseScene("room") +
      '<p style="margin-top:10px">열두 시간이 지났어요. 오늘은 우리가 만든 것을 여는 날이에요.</p>' +
      '<p style="margin-top:8px">1차시에 만났던 강아지 <b>몽이</b>가 첫 손님으로 왔어요. ' +
      '몽이는 부스마다 같은 것을 물어봐요. "이건 누가 했어요?"</p>' +
      '<p class="muted" style="margin-top:8px">그 물음에 답하는 표가 <b>표기표</b>예요. ' +
      '표기표를 걸어야 부스가 열려요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">전시장으로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>전시장</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-booth">' + wiseIcon("write", 30) +
      '<span>부스 차리기</span><small id="s-booth">제목과 만든 것</small></button>' +
      '<button type="button" class="tile" id="t-label">' + wiseIcon("both", 30) +
      '<span>표기표 만들기</span><small id="s-label">여덟 단계 나누기</small></button>' +
      '<button type="button" class="tile" id="t-pledge">' + wiseIcon("check", 30) +
      '<span>약속 점검</span><small id="s-pledge">지킨 조항 고르기</small></button>' +
      '<button type="button" class="tile" id="t-tour">' + wiseIcon("talk", 30) +
      '<span>전시장 둘러보기</span><small id="s-tour">배운 점 남기기</small></button>' +
      '<button type="button" class="tile" id="t-back2">' + wiseIcon("again", 30) +
      '<span>돌아보기</span><small id="s-back2">첫 시간의 나와 지금의 나</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("star", 30) +
      '<span>수료 카드</span><small id="s-card">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3>' +
      '<div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("booth",
      '<div class="card"><span class="pill">1</span>' +
      '<h2 style="margin-top:10px">부스 차리기</h2>' +
      '<p class="muted">무엇을 만들었는지 짧게 적어요. 자랑이 아니라 소개예요.</p>' +
      '<label for="title">우리 프로젝트 제목</label>' +
      '<input id="title" maxlength="40" placeholder="예: 급식 남기지 않기 캠페인">' +
      '<label for="made">우리가 만든 것</label>' +
      '<textarea id="made" maxlength="300" placeholder="무엇을 만들었는지 두세 줄로 써요"></textarea>' +
      '<label for="who">누구에게 도움이 되나요</label>' +
      '<input id="who" maxlength="80" placeholder="예: 1학년 동생들, 급식실 선생님">' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="booth-next">표기표 만들러 가기</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>');

    h += q("label",
      '<div class="card"><span class="pill">2</span>' +
      '<h2 style="margin-top:10px">표기표 만들기</h2>' +
      '<p class="muted">여덟 단계를 누가 했는지 골라요. 고를 때마다 표기 문장이 자라나요.</p>' +
      '<div id="roles"></div>' +
      '<div id="labelbox" style="margin-top:14px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="label-next">약속 점검하러 가기</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>');

    var pl = '<div class="card"><span class="pill">3</span>' +
      '<h2 style="margin-top:10px">약속 점검</h2>' +
      '<p class="muted">7차시에 우리가 만든 약속 가운데 실제로 지킨 것을 골라요.</p>';
    for (var i = 0; i < PLEDGES.length; i++) {
      pl += '<button type="button" class="chip kept" data-k="' + i + '">' +
        wiseIcon("check", 26) + esc(PLEDGES[i]) + '</button>';
    }
    pl += '<div id="keptbar" style="margin-top:10px"></div>' +
      '<label for="broke">지키기 어려웠던 것</label>' +
      '<input id="broke" maxlength="80" placeholder="솔직하게 써도 괜찮아요">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="pledge-next">전시장 둘러보러 가기</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>';
    h += q("pledge", pl);

    h += q("tour",
      '<div class="card"><span class="pill">4</span>' +
      '<h2 style="margin-top:10px">전시장 둘러보기</h2>' +
      '<p class="muted">다른 부스를 보고 배운 점을 한 줄씩 남겨요. 잘잘못을 매기지 않아요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="reload">부스 목록 새로고침</button></div>' +
      '<div id="booths" style="margin-top:12px"></div></div>' +
      '<div class="card"><h3>나에게 온 배운 점</h3>' +
      '<div id="mynotes" style="margin-top:8px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="tour-next">돌아보러 가기</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>');

    h += q("back2",
      '<div class="card"><span class="pill">5</span>' +
      '<h2 style="margin-top:10px">돌아보기</h2>' +
      '<p class="muted">첫 시간의 나와 지금의 나를 나란히 두고 써요.</p>' +
      '<label for="before">1차시에 나는 이렇게 생각했다</label>' +
      '<textarea id="before" maxlength="400" placeholder="그때 나는 AI를 어떤 것이라고 보았나요"></textarea>' +
      '<label for="after">지금 나는 이렇게 생각한다</label>' +
      '<textarea id="after" maxlength="400" placeholder="지금의 내 생각을 내 말로 써요"></textarea>' +
      '<div id="growth" style="margin-top:12px"></div>' +
      '<label for="vow">앞으로 지킬 한 가지</label>' +
      '<input id="vow" maxlength="80" placeholder="예: 숙제할 때 내 생각을 먼저 세 줄 쓴다">' +
      '<div class="note">열두 시간을 마쳤으니 <b>사후 설문</b>을 해요. 답은 이름 없이 모여요.' +
      ' <a href="../common/index.html" target="_blank" rel="noopener">사후 설문 열기</a></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="back2-next">수료 카드 보러 가기</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">6</span>' +
      '<h2 style="margin-top:10px">수료 카드</h2>' +
      '<div id="mycard"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">전시장으로</button></div></div>');

    return h;
  }

  /* ---------- 표기표 ---------- */

  function paintRoles() {
    if (!$("roles")) { return; }
    var h = "";
    for (var i = 0; i < STEPS.length; i++) {
      h += '<div class="card" style="margin:10px 0 0;padding:14px">' +
        '<h3 style="font-size:19px">' + (i + 1) + '. ' + esc(STEPS[i]) + '</h3>';
      for (var r = 0; r < ROLES.length; r++) {
        var on = st.role[i] === ROLES[r].key ? " on" : "";
        h += '<button type="button" class="chip rl' + on + '" data-s="' + i + '" data-r="' +
          ROLES[r].key + '">' + wiseIcon(ROLES[r].icon, 26) + esc(ROLES[r].name) + '</button>';
      }
      h += '</div>';
    }
    $("roles").innerHTML = h;
    $("roles").className = "fade-in";
    bindRoles();
  }

  function bindRoles() {
    var bs = document.querySelectorAll("#activity .rl");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () {
        var s = Number(this.getAttribute("data-s"));
        st.role[s] = this.getAttribute("data-r");
        markRoles();
        paintLabel();
        paintHub();
      };
    }
  }

  function markRoles() {
    var bs = document.querySelectorAll("#activity .rl");
    for (var i = 0; i < bs.length; i++) {
      var s = Number(bs[i].getAttribute("data-s"));
      var r = bs[i].getAttribute("data-r");
      bs[i].className = "chip rl" + (st.role[s] === r ? " on" : "");
    }
  }

  function stepsBy(role) {
    var out = [];
    for (var i = 0; i < STEPS.length; i++) {
      if (st.role[i] === role) { out.push(STEPS[i]); }
    }
    return out;
  }

  /* 표기 문장에 쓸 목록. 마지막 결정 단계는 따로 말하므로 여기서 뺀다. */
  function stepsExceptDecide(role) {
    var out = [];
    for (var i = 0; i < STEPS.length; i++) {
      if (i !== DECIDE && st.role[i] === role) { out.push(STEPS[i]); }
    }
    return out;
  }

  /* 표기 문장. 고른 만큼만 자라난다. 다 고르면 마지막 줄이 붙는다. */
  function labelText() {
    var ai = stepsExceptDecide("ai"), both = stepsExceptDecide("both"), ours = stepsExceptDecide("me");
    var s = "이 결과물은 ";
    if (ai.length) { s += "AI에게 " + ai.join(", ") + "를 맡겼어요. "; }
    else if (countOf(st.role)) { s += "AI에게 맡긴 단계가 없어요. "; }
    if (both.length) { s += both.join(", ") + "는 AI와 함께 했어요. "; }
    if (ours.length) { s += ours.join(", ") + "는 우리가 했어요. "; }
    if (st.role[DECIDE]) {
      s += "마지막 결정은 " +
        (st.role[DECIDE] === "ai" ? "AI가" : (st.role[DECIDE] === "both" ? "함께" : "우리가")) +
        " 했어요.";
    }
    return s;
  }

  function paintLabel() {
    if (!$("labelbox")) { return; }
    var done = countOf(st.role);
    var h = '<h3>표기 문장</h3>' + barHtml(done, STEPS.length) +
      '<p class="muted" style="margin-top:6px">' + done + ' / ' + STEPS.length + ' 단계</p>';
    if (!done) {
      h += '<p class="muted">아직 고른 단계가 없어요. 첫 단계부터 골라 봐요.</p>';
    } else {
      h += '<div class="note">' + esc(labelText()) + '</div>';
    }
    if (st.role[DECIDE] === "ai") {
      h += '<div class="safe"><b>마지막 결정을 AI가 했나요?</b> ' +
        '무엇을 넣고 뺄지 고르는 일까지는 AI가 도울 수 있어요. ' +
        '그렇지만 마지막 결정은 사람이 하기로 했어요. 다시 한 번 볼까요?</div>';
    }
    $("labelbox").innerHTML = h;
    $("labelbox").className = "fade-in";
    if (done >= STEPS.length && !st.labeled) {
      st.labeled = true;
      award("표기 완료");
      wiseToast("표기표를 걸었어요. 이제 손님을 받아요.");
    }
  }

  /* ---------- 약속 ---------- */

  function bindPledges() {
    var ks = document.querySelectorAll("#activity .kept");
    for (var i = 0; i < ks.length; i++) {
      ks[i].onclick = function () {
        var key = this.getAttribute("data-k");
        st.kept[key] = !st.kept[key];
        markPledges();
        paintKeptBar();
        paintHub();
      };
    }
    markPledges();
    paintKeptBar();
  }

  function markPledges() {
    var ks = document.querySelectorAll("#activity .kept");
    for (var i = 0; i < ks.length; i++) {
      var k = ks[i].getAttribute("data-k");
      ks[i].className = "chip kept" + (st.kept[k] ? " on" : "");
    }
  }

  function keptCount() {
    var n = 0;
    for (var k in st.kept) { if (st.kept.hasOwnProperty(k) && st.kept[k]) { n++; } }
    return n;
  }

  function keptList() {
    var out = [];
    for (var i = 0; i < PLEDGES.length; i++) {
      if (st.kept[i]) { out.push(PLEDGES[i]); }
    }
    return out;
  }

  function paintKeptBar() {
    if (!$("keptbar")) { return; }
    var n = keptCount();
    $("keptbar").innerHTML = barHtml(n, PLEDGES.length) +
      '<p class="muted" style="margin-top:6px">지킨 약속 ' + n + ' / ' + PLEDGES.length + '</p>' +
      (n ? "" : '<p class="muted">하나도 못 골라도 괜찮아요. 어려웠던 것을 쓰는 것도 점검이에요.</p>');
  }

  /* ---------- 전시장 둘러보기 ---------- */

  /* 목록을 다시 그리기 전에 쓰던 글을 상태로 옮긴다. 6차시에서 겪은 사고를 막는다. */
  function stashNotes() {
    for (var i = 0; i < st.list.length; i++) {
      var el = $("nt" + i);
      if (el && typeof el.value === "string") {
        var v = String(el.value).trim();
        if (v) { st.noteDraft[st.list[i].key] = v; }
        else if (el.parentNode && st.noteDraft[st.list[i].key]) {
          delete st.noteDraft[st.list[i].key];
        }
      }
    }
  }

  function reload() {
    if (me.solo) {
      $("booths").innerHTML = '<p class="muted">혼자 체험 중에는 다른 부스가 없어요. ' +
        '표기표와 돌아보기는 그대로 해 볼 수 있어요.</p>';
      $("mynotes").innerHTML = '<p class="muted">혼자 체험 중에는 받은 배운 점이 없어요.</p>';
      return;
    }
    stashNotes();
    $("booths").innerHTML = wiseSpinner("전시장을 여는 중이에요", true) + wiseSkeleton(4);
    wiseButtonBusy($("reload"), true, "불러오는 중");
    dbGet(me.room + "/entries").then(function (data) {
      st.list = [];
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload;
        if (p && p.title && data[k].nick !== me.nick) {
          st.list.push({ key: k, nick: data[k].nick, group: data[k].group, p: p });
        }
      }
      wiseButtonBusy($("reload"), false);
      paintBooths();
      loadMyNotes();
    })["catch"](function () {
      wiseButtonBusy($("reload"), false);
      $("booths").innerHTML = '<p class="warn">지금은 목록을 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function paintBooths() {
    if (!$("booths")) { return; }
    if (!st.list.length) {
      $("booths").innerHTML = '<p class="muted">아직 다른 부스가 없어요. ' +
        '친구들이 제출하면 여기에 보여요.</p>';
      return;
    }
    var h = "";
    for (var i = 0; i < st.list.length; i++) {
      var it = st.list[i];
      var sent = st.notes[it.key];
      h += '<div class="card" style="margin-bottom:10px">' +
        '<span class="pill">' + esc(it.group || it.nick) + '</span>' +
        '<p style="margin:8px 0 4px;font-size:19px;font-weight:900">' + esc(it.p.title) + '</p>' +
        '<p class="muted">' + esc(it.p.made || "") + '</p>' +
        (it.p.label ? '<p class="tag" style="margin-top:8px">' + esc(it.p.label) + '</p>' : "") +
        '<label for="nt' + i + '">이 부스에서 배운 점</label>' +
        '<input id="nt' + i + '" maxlength="80" value="' +
        esc(st.noteDraft[it.key] || sent || "") + '" placeholder="한 줄로 남겨요">' +
        '<div class="row" style="margin-top:8px">' +
        '<button type="button" class="ghost send" data-i="' + i + '">' +
        (sent ? "다시 보내기" : "배운 점 보내기") + '</button></div></div>';
    }
    $("booths").innerHTML = h;
    $("booths").className = "fade-in";
    bindBooths();
  }

  function bindBooths() {
    var ins = document.querySelectorAll("#activity #booths input");
    for (var i = 0; i < ins.length; i++) {
      ins[i].oninput = stashNotes;
    }
    var bs = document.querySelectorAll("#activity .send");
    for (var j = 0; j < bs.length; j++) {
      bs[j].onclick = function () {
        var idx = Number(this.getAttribute("data-i"));
        var it = st.list[idx];
        if (!it) { return; }
        var text = $("nt" + idx) ? String($("nt" + idx).value).trim() : "";
        if (!text) { wiseToast("배운 점을 한 줄 써 주세요."); return; }
        var btn = this;
        wiseButtonBusy(btn, true, "보내는 중");
        st.notes[it.key] = text;
        st.noteDraft[it.key] = text;
        dbPush(me.room + "/votes", {
          key: it.key, to: it.nick, nick: me.nick, at: Date.now(), note: text
        }).then(function () {
          wiseButtonBusy(btn, false);
          btn.textContent = "보냈어요";
          wiseToast("배운 점을 보냈어요.");
          paintHub();
        })["catch"](function () {
          wiseButtonBusy(btn, false);
          wiseToast("지금은 보낼 수 없어요. 잠시 뒤 다시 눌러요.");
        });
      };
    }
  }

  /* 나에게 온 배운 점. 보낸 사람 닉네임은 적지 않는다. */
  function loadMyNotes() {
    if (!$("mynotes") || me.solo) { return; }
    $("mynotes").innerHTML = wiseSpinner("배운 점을 모으는 중이에요");
    dbGet(me.room + "/votes").then(function (data) {
      st.mine = [];
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        if (data[k] && data[k].to === me.nick && data[k].note) { st.mine.push(data[k].note); }
      }
      var h = "";
      if (!st.mine.length) {
        h = '<p class="muted">아직 온 것이 없어요. 조금 기다려 봐요.</p>';
      } else {
        for (var i = 0; i < st.mine.length && i < 12; i++) {
          h += '<p class="note" style="margin-top:8px">' + esc(st.mine[i]) + '</p>';
        }
      }
      $("mynotes").innerHTML = h;
      $("mynotes").className = "fade-in";
    })["catch"](function () {
      $("mynotes").innerHTML = '<p class="muted">지금은 불러올 수 없어요.</p>';
    });
  }

  /* ---------- 돌아보기 ---------- */

  function words(text) {
    var raw = String(text || "").split(/[ ,.]+/);
    var out = [];
    for (var i = 0; i < raw.length; i++) {
      if (raw[i].trim().length > 1) { out.push(raw[i].trim()); }
    }
    return out;
  }

  function newWords(before, after) {
    var wb = words(before), wa = words(after);
    if (!wa.length) { return 0; }
    var seen = {}, stem = {}, i;
    for (i = 0; i < wb.length; i++) {
      seen[wb[i]] = true;
      stem[wb[i].slice(0, 2)] = true;
    }
    var fresh = 0;
    for (i = 0; i < wa.length; i++) {
      if (!seen[wa[i]] && !stem[wa[i].slice(0, 2)]) { fresh++; }
    }
    return Math.round(fresh * 100 / wa.length);
  }

  function paintGrowth() {
    if (!$("growth")) { return; }
    var b = val("before"), a = val("after");
    if (!b || !a) {
      $("growth").innerHTML = '<p class="muted">두 칸을 모두 쓰면 무엇이 달라졌는지 보여 줘요.</p>';
      return;
    }
    var fresh = newWords(b, a);
    var h = '<p>지금 글에 새로 들어온 말 ' + fresh + '%</p>' + barHtml(fresh, 100);
    if (fresh > 60) {
      h += '<p class="ok">생각이 많이 자랐어요. 무엇이 그렇게 만들었는지도 써 보면 좋아요.</p>';
    } else if (fresh < 20) {
      h += '<p class="muted">처음 생각을 지키고 있어요. 왜 바뀌지 않았는지도 좋은 성찰이에요.</p>';
    } else {
      h += '<p class="ok">처음 생각 위에 새로운 것이 더해졌어요.</p>';
    }
    $("growth").innerHTML = h;
  }

  /* ---------- 수료 카드 ---------- */

  function paintCard() {
    if (!$("mycard")) { return; }
    var title = val("title");
    if (!title) {
      $("mycard").innerHTML = '<p class="muted">부스를 먼저 차려요. 제목을 쓰면 카드가 만들어져요.</p>';
      return;
    }
    var rows = [
      { label: "우리가", value: stepsBy("me").length, color: "#059669" },
      { label: "함께", value: stepsBy("both").length, color: "#2563eb" },
      { label: "AI가", value: stepsBy("ai").length, color: "#d97706" }
    ];
    var h = '<p class="big">' + esc(title) + '</p>' +
      '<p class="muted" style="margin-top:6px">' + esc(val("who") || "우리 반") +
      '을 위해 만들었어요.</p>' + wiseBars(rows, 560);
    if (countOf(st.role)) {
      h += '<div class="note" style="margin-top:10px">' + esc(labelText()) + '</div>';
    }
    h += '<p style="margin-top:10px">지킨 약속 ' + keptCount() + ' / ' + PLEDGES.length +
      '장 · 보낸 배운 점 ' + countOf(st.notes) + '개</p>';
    if (val("vow")) {
      h += '<p class="ok">앞으로 지킬 한 가지 : ' + esc(val("vow")) + '</p>';
    }
    $("mycard").innerHTML = h;
    $("mycard").className = "fade-in";
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    if (st.quiet) { return; }
    wiseToast("배지를 받았어요 : " + name);
    paintHub();
  }

  function badgeList() {
    var out = [];
    for (var k in st.badges) { if (st.badges.hasOwnProperty(k)) { out.push(k); } }
    return out;
  }

  function paintHub() {
    if (!$("s-booth")) { return; }
    var roleDone = countOf(st.role);
    $("s-booth").textContent = val("title") ? val("title") : "제목과 만든 것";
    $("s-label").textContent = "표기한 단계 " + roleDone + " / " + STEPS.length;
    $("s-pledge").textContent = "지킨 약속 " + keptCount() + " / " + PLEDGES.length;
    $("s-tour").textContent = countOf(st.notes)
      ? ("보낸 배운 점 " + countOf(st.notes) + "개") : "배운 점 남기기";
    $("s-back2").textContent = val("after") ? "성찰을 썼어요" : "첫 시간의 나와 지금의 나";
    $("s-card").textContent = "오늘의 내 기록";

    var tiles = [
      ["t-booth", !!(val("title") && val("made"))],
      ["t-label", roleDone >= STEPS.length],
      ["t-pledge", keptCount() > 0],
      ["t-tour", countOf(st.notes) > 0],
      ["t-back2", val("after").length >= 10],
      ["t-card", false]
    ];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if (val("title") && val("made")) { award("부스 차림"); }
    if (keptCount() >= 3) { award("약속 지킴"); }
    if (countOf(st.notes) >= 2) { award("이웃 응원"); }
    if (val("before") && val("after").length >= 10) { award("돌아보기"); }

    var names = badgeList();
    $("badges").innerHTML = names.length
      ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
      : '<span class="muted">아직 없어요. 부스를 차리면 받을 수 있어요.</span>';

    wiseHud([
      { label: "표기", done: roleDone, total: STEPS.length },
      { label: "약속", done: keptCount(), total: PLEDGES.length },
      { label: "배운 점", done: countOf(st.notes), total: 3 }
    ]);
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "label") {
      if ($("roles")) {
        $("roles").innerHTML = wiseSpinner("표기표를 꺼내는 중이에요") + wiseSkeleton(3);
      }
      softDelay(function () { paintRoles(); paintLabel(); }, 200);
    }
    if (id === "pledge") { markPledges(); paintKeptBar(); }
    if (id === "tour") { reload(); }
    if (id === "back2") { paintGrowth(); }
    if (id === "card") {
      if ($("mycard")) {
        $("mycard").innerHTML = wiseSpinner("오늘 기록을 모으는 중이에요") + wiseSkeleton(3);
      }
      softDelay(paintCard, 240);
    }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    var i, id;
    for (i = 0; i < FIELDS.length; i++) {
      id = FIELDS[i];
      if (st.text[id] === undefined && saved && saved[id]) { st.text[id] = saved[id]; }
      if ($(id)) {
        if (st.text[id]) { $(id).value = st.text[id]; }
        $(id).oninput = function () { stashText(); paintGrowth(); paintHub(); };
      }
    }
    if (saved) {
      if (saved.role) { st.role = saved.role; }
      if (saved.keptMap) { st.kept = saved.keptMap; }
      if (saved.notes) { st.notes = saved.notes; }
      if (countOf(st.role) >= STEPS.length) { st.labeled = true; }
      if (saved.title || countOf(st.role)) { st.restored = true; }
    }

    $("go-hub").onclick = function () {
      if (st.opened) { wiseGo("hub"); return; }
      st.opened = true;
      wiseBusy(true, "전시장 문을 여는 중");
      softDelay(function () { wiseBusy(false); wiseGo("hub"); }, 520);
    };
    $("t-booth").onclick = function () { wiseGo("booth"); };
    $("t-label").onclick = function () { wiseGo("label"); };
    $("t-pledge").onclick = function () { wiseGo("pledge"); };
    $("t-tour").onclick = function () { wiseGo("tour"); };
    $("t-back2").onclick = function () { wiseGo("back2"); };
    $("t-card").onclick = function () { wiseGo("card"); };

    $("booth-next").onclick = function () {
      if (!val("title")) { wiseToast("프로젝트 제목을 먼저 써 주세요."); return; }
      wiseGo("label");
    };
    $("label-next").onclick = function () { wiseGo("pledge"); };
    $("pledge-next").onclick = function () { wiseGo("tour"); };
    $("tour-next").onclick = function () { wiseGo("back2"); };
    $("back2-next").onclick = function () { wiseGo("card"); };
    $("reload").onclick = reload;

    $("save-card").onclick = function () {
      var btn = this;
      if (!val("title")) { wiseToast("부스를 먼저 차려요."); return; }
      wiseButtonBusy(btn, true, "그림 만드는 중");
      wiseCardPng("12차시 수료 카드 " + me.nick, [
        val("title"),
        "AI가 한 단계 " + stepsBy("ai").length + "개, 함께 " + stepsBy("both").length +
          "개, 우리가 " + stepsBy("me").length + "개",
        "지킨 약속 " + keptCount() + " / " + PLEDGES.length + "장",
        "앞으로 지킬 한 가지 : " + (val("vow") || "다음 시간에 정할게요"),
        "마지막 결정은 사람이 한다."
      ], "wise_l12_" + me.nick);
      wiseButtonBusy(btn, false);
    };

    var backs = document.querySelectorAll("#activity .back");
    for (i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }

    bindPledges();
    wiseNote(st.restored
      ? "<b>지난번에 쓰던 것이 남아 있어요.</b> 이어서 하면 돼요."
      : "발표는 자랑이 아니라 무엇을 어떻게 했는지 밝히는 자리예요.");
    wiseGo("story");
    st.quiet = true;
    paintHub();
    st.quiet = false;
    paintGrowth();
  }

  function activityDraft() {
    stashText();
    return {
      title: val("title"), made: val("made"), who: val("who"), broke: val("broke"),
      before: val("before"), after: val("after"), vow: val("vow"),
      role: st.role, keptMap: st.kept, notes: st.notes
    };
  }

  function activityAutofill() {
    var fill = {
      title: "급식 남기지 않기 캠페인",
      made: "먹을 양을 고르는 안내판을 만들었습니다",
      who: "1학년 동생들",
      broke: "확인을 자꾸 잊었습니다",
      before: "AI가 숙제를 대신해 주면 편할 것 같다고 생각했습니다",
      after: "내 생각을 먼저 만들고 나서 도움을 받아야 내 것이 된다고 생각합니다",
      vow: "숙제할 때 내 생각을 먼저 세 줄 씁니다"
    };
    for (var k in fill) {
      if (!fill.hasOwnProperty(k)) { continue; }
      st.text[k] = fill[k];
      if ($(k)) { $(k).value = fill[k]; }
    }
    for (var i = 0; i < STEPS.length; i++) {
      st.role[i] = i === 2 ? "ai" : (i % 3 === 1 ? "both" : "me");
    }
    st.kept["0"] = true;
    st.kept["2"] = true;
    st.kept["4"] = true;
    paintLabel();
    paintKeptBar();
    paintHub();
  }

  function activityCollect() {
    if (!val("title") || !val("made")) {
      $("w-msg").innerHTML = '<span class="warn">부스 차리기에서 제목과 만든 것을 써 주세요.</span>';
      return null;
    }
    var roleDone = countOf(st.role);
    if (roleDone < STEPS.length) {
      $("w-msg").innerHTML = '<span class="warn">표기표를 마저 채워요. 지금 ' + roleDone +
        ' / ' + STEPS.length + ' 단계예요.</span>';
      return null;
    }
    if (val("after").length < 10) {
      $("w-msg").innerHTML = '<span class="warn">돌아보기에서 지금의 내 생각을 써 주세요.</span>';
      return null;
    }
    award("12차시 수료");
    var badges = badgeList();
    wiseCelebrate("열두 시간을 마쳤어요", [
      "지킨 약속 <b>" + keptCount() + "장</b> · 보낸 배운 점 <b>" + countOf(st.notes) + "개</b>",
      "받은 배지 " + (badges.length ? esc(badges.join(", ")) : "없음"),
      "사후 설문까지 하면 오늘 할 일이 모두 끝나요."
    ], "좋아요");
    return {
      title: val("title"), made: val("made"), who: val("who"),
      role: st.role, label: labelText(), aiDecide: st.role[DECIDE] === "ai",
      kept: keptList(), broke: val("broke"),
      before: val("before"), after: val("after"), next: val("vow"),
      growth: newWords(val("before"), val("after")),
      notesSent: countOf(st.notes), badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function roleTally(list) {
    var rows = [], i, k;
    for (i = 0; i < STEPS.length; i++) { rows.push({ me: 0, both: 0, ai: 0 }); }
    for (k = 0; k < list.length; k++) {
      var r = (list[k].payload || {}).role || {};
      for (i = 0; i < STEPS.length; i++) {
        if (r[i] === "me") { rows[i].me += 1; }
        else if (r[i] === "both") { rows[i].both += 1; }
        else if (r[i] === "ai") { rows[i].ai += 1; }
      }
    }
    return rows;
  }

  function teacherSummary(list) {
    var n = 0, notes = 0, growth = 0, aiDecide = 0, keptMap = {}, i, k;
    for (i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.title) { continue; }
      n++;
      notes += p.notesSent || 0;
      growth += p.growth || 0;
      if (p.aiDecide) { aiDecide += 1; }
      var kk = p.kept || [];
      for (k = 0; k < kk.length; k++) { keptMap[kk[k]] = (keptMap[kk[k]] || 0) + 1; }
    }
    var h = '<p class="muted">발표 ' + n + '건 · 서로 보낸 배운 점 ' + notes + '개 · ' +
      '성찰에 새로 들어온 말 평균 ' + (n ? Math.round(growth / n) : 0) + '%</p>';
    if (aiDecide) {
      h += '<div class="safe"><b>마지막 결정을 AI 로 표기한 학생 ' + aiDecide + '명.</b> ' +
        '정리 발문에서 이 대목을 함께 이야기한다.</div>';
    }

    var rows = roleTally(list);
    h += '<h3 style="margin-top:16px">단계별로 누가 했나</h3><div class="scroll"><table>' +
      '<tr><th>단계</th><th>우리가</th><th>함께</th><th>AI가</th></tr>';
    for (i = 0; i < STEPS.length; i++) {
      h += "<tr><td>" + esc(STEPS[i]) + "</td><td>" + rows[i].me + "</td><td>" +
        rows[i].both + "</td><td>" + rows[i].ai + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">발표 순서와 표기 문장</h3><div class="scroll"><table>' +
      '<tr><th>차례</th><th>모둠</th><th>제목</th><th>표기 문장</th><th>앞으로 지킬 것</th></tr>';
    var order = 0;
    for (i = 0; i < list.length; i++) {
      var q2 = list[i].payload || {};
      if (!q2.title) { continue; }
      order++;
      h += "<tr><td>" + order + "</td><td>" + esc(list[i].group || list[i].nick) + "</td><td>" +
        esc(q2.title) + "</td><td>" + esc(q2.label || "") + "</td><td>" +
        esc(q2.next || "") + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">지켰다고 고른 약속</h3><div class="scroll"><table>' +
      '<tr><th>약속</th><th>고른 사람</th></tr>';
    for (var key in keptMap) {
      if (!keptMap.hasOwnProperty(key)) { continue; }
      h += "<tr><td>" + esc(key) + "</td><td>" + keptMap[key] + "명</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">지키기 어려웠던 것</h3><div class="scroll"><table>' +
      '<tr><th>모둠</th><th>어려웠던 것</th></tr>';
    for (i = 0; i < list.length; i++) {
      var b = (list[i].payload || {}).broke;
      if (!b) { continue; }
      h += "<tr><td>" + esc(list[i].group || list[i].nick) + "</td><td>" + esc(b) + "</td></tr>";
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var h = '<p class="muted">발표 순서예요. 표기 문장을 함께 읽어요.</p>';
    var order = 0, i;
    for (i = 0; i < list.length && order < 6; i++) {
      var p = list[i].payload || {};
      if (!p.title) { continue; }
      order++;
      h += '<div class="card"><span class="pill">' + order + ' · ' +
        esc(list[i].group || list[i].nick) + '</span>' +
        '<p class="big" style="margin-top:8px">' + esc(p.title) + '</p>' +
        (p.label ? '<p style="margin-top:8px">' + esc(p.label) + '</p>' : "") + '</div>';
    }
    var shown = 0;
    h += '<h3 style="margin-top:16px">첫 시간과 지금</h3>';
    for (i = 0; i < list.length && shown < 5; i++) {
      var r = list[i].payload || {};
      if (!r.after) { continue; }
      shown++;
      h += '<div class="card">' +
        (r.before ? '<p class="muted">처음 : ' + esc(r.before) + '</p>' : "") +
        '<p class="big" style="margin-top:8px">' + esc(r.after) + '</p></div>';
    }
    if (!order && !shown) { h += '<p class="muted">아직 제출이 없어요.</p>'; }
    return h;
  }
"""
