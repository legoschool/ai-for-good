# -*- coding: utf-8 -*-
"""11차시 AI for Good 프로젝트 : 좋은문제 연구소.

여정형으로 다시 만들었다. 폼 하나가 아니라 화면 아홉 개를 지나간다.

  이야기 → 연구소 허브 → 관찰대(후보 3개와 점수) → 좁히기 작업대
  → 판정실(신호등) → 역할 나누기 → 설계실(절차 4단계) → 마을 게시판 → 계획 카드

이 앱의 단 하나의 경험은 "막연한 불평이 손에 잡히는 문제로 좁혀지는 것"이다.
누가·언제·무엇 때문에를 채우면 한 문장이 조립되고 좁힘 눈금이 오른다.
눈금이 3에 닿기 전에는 판정실과 설계실이 열리지 않는다. 순서가 곧 배움이다.

설계서는 spec/16_웹앱_설계_L11.md 다.
40분 : 이야기 2 + 관찰 8 + 좁히기 8 + 판정 6 + 역할 5 + 설계 8 + 게시판 2 + 카드 1
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  /* 6차시 신호등 네 단계를 그대로 쓴다. 용어를 흔들지 않는다. */
  var SIGNALS = [
    {name:"초록불", say:"그냥 써도 돼", icon:"green", color:"#16a34a"},
    {name:"노랑불", say:"조건을 지키면 돼", icon:"yellow", color:"#eab308"},
    {name:"주황불", say:"아주 조심해서만", icon:"orange", color:"#ea580c"},
    {name:"빨간불", say:"쓰면 안 돼", icon:"red", color:"#dc2626"}
  ];

  var WHYS = [
    "개인정보가 들어가나",
    "우리가 배우는 데 도움이 되나",
    "결과를 우리가 확인할 수 있나",
    "우리 마을 상황에 맞나"
  ];

  var MARKS = [
    {k:"can", t:"우리가 바꿀 수 있나"},
    {k:"many", t:"여러 명에게 도움되나"},
    {k:"check", t:"우리가 직접 확인할 수 있나"}
  ];

  var STEPS = [
    "문제를 겪는 사람에게 물어보기",
    "우리가 아는 것 적어 보기",
    "자료와 사진 모으기",
    "AI에게 아이디어 여러 개 받기",
    "우리 기준으로 걸러 내기",
    "직접 만들어 보기",
    "써 보고 고치기",
    "마을에 알리기"
  ];

  var ROLES = [
    {t:"무엇을 만들지 정하기", human:true},
    {t:"자료 찾아 정리하기", human:false},
    {t:"아이디어 여러 개 떠올리기", human:false},
    {t:"어떤 아이디어를 고를지 결정하기", human:true},
    {t:"글 표현 다듬기", human:false},
    {t:"결과를 책임지기", human:true}
  ];

  var WHO = ["사람", "AI", "둘 다"];
  var WHO_ICON = ["me", "ai", "both"];

  /* 넓은 말. 이 말만 남아 있으면 좁힘 눈금이 다 차지 않는다. */
  var WIDE = ["모두", "다들", "너무", "그냥", "여러 가지", "많이", "항상"];

  var st = {
    scores: {}, pick: -1, signal: -1, why: -1, roles: {}, steps: [],
    cond: "", alt: "", badges: {}, board: null, boardTried: false
  };

  /* ---------- 도우미 ---------- */

  function val(id) { return $(id) ? String($(id).value || "").replace(/^[ ]+/, "").replace(/[ ]+$/, "") : ""; }

  function countOf(obj) {
    var n = 0, k;
    for (k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  /* 화면을 딱딱 갈아 끼우지 않는다. 무엇을 하는 중인지 잠깐 보여 준 뒤 넘어간다.
     움직임을 줄이는 설정이거나 브라우저가 아니면 곧바로 넘어간다. (검사기가 멈추면 안 된다) */
  function softMotion() {
    try {
      if (!window.matchMedia) { return false; }
      return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch (e) { return false; }
  }

  function goSlow(id, text, ms) {
    if (!softMotion()) { wiseGo(id); return; }
    wiseBusy(true, text || "여는 중이에요");
    setTimeout(function () {
      wiseBusy(false);
      wiseGo(id);
    }, ms || 460);
  }

  function candText(i) { return val("cand" + i); }

  /* 노랑·주황이면 조건, 빨강이면 대안이다. 칸은 하나지만 담는 곳은 둘이다. */
  function condKey() { return st.signal === 3 ? "alt" : "cond"; }

  function condText() {
    var typed = val("cond");
    if (typed) { st[condKey()] = typed; }
    return st[condKey()] || "";
  }

  function candCount() {
    var n = 0;
    for (var i = 0; i < 3; i++) { if (candText(i)) { n++; } }
    return n;
  }

  function markCount() {
    var n = 0, k;
    for (k in st.scores) {
      if (!st.scores.hasOwnProperty(k)) { continue; }
      for (var m = 0; m < MARKS.length; m++) {
        if (st.scores[k][MARKS[m].k] !== undefined) { n++; }
      }
    }
    return n;
  }

  function pickedText() {
    if (st.pick >= 0 && candText(st.pick)) { return candText(st.pick); }
    return "";
  }

  /* 좁힘 눈금 0~4. 칸을 채우면 오르고, 넓은 말만 남으면 마지막 한 칸이 오르지 않는다. */
  function narrowScore() {
    var who = val("who"), when = val("when"), what = val("what");
    var n = 0;
    if (who) { n++; }
    if (when) { n++; }
    if (what) { n++; }
    var all = who + when + what;
    var wide = false;
    for (var i = 0; i < WIDE.length; i++) {
      if (all.indexOf(WIDE[i]) >= 0) { wide = true; }
    }
    if (n === 3 && all.length >= 12 && !wide) { n++; }
    return n;
  }

  function oneLine() {
    var who = val("who"), when = val("when"), what = val("what");
    if (!who && !when && !what) { return ""; }
    return (who || "누가") + " " + (when || "언제") + " " + (what || "무엇 때문에") + " 불편합니다.";
  }

  function narrowed() { return narrowScore() >= 3; }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">좋은문제 연구소</h2>' +
      wiseScene("room") +
      '<p style="margin-top:10px">마을 게시판에 불편 신고가 잔뜩 쌓였어요. ' +
      '"급식이 별로예요", "복도가 미끄러워요" 같은 쪽지들이에요.</p>' +
      '<p style="margin-top:8px">오늘 우리 모둠은 <b>좋은문제 연구소</b>의 연구원이에요. ' +
      '조수 로봇 <b>두루</b>가 옆에서 두루 살펴 줘요.</p>' +
      '<p style="margin-top:8px">두루는 답을 주지 않아요. 되물을 뿐이에요. ' +
      '"누가요? 언제요? 무엇 때문에요?"</p>' +
      '<p class="muted" style="margin-top:8px">넓은 말은 아무것도 할 수 없어요. ' +
      '좁혀야 우리가 해 볼 수 있는 문제가 돼요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">연구소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>연구소</h2>' +
      '<p class="muted">관찰대와 좁히기를 먼저 해요. 문제를 좁혀야 판정실과 설계실이 열려요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-obs">' + wiseIcon("rec", 30) +
      '<span>관찰대</span><small id="s-obs">불편 후보 3개 모으기</small></button>' +
      '<button type="button" class="tile" id="t-narrow">' + wiseIcon("write", 30) +
      '<span>좁히기 작업대</span><small id="s-narrow">한 문장으로 좁히기</small></button>' +
      '<button type="button" class="tile" id="t-judge">' + wiseIcon("check", 30) +
      '<span>판정실</span><small id="s-judge">신호등으로 판단하기</small></button>' +
      '<button type="button" class="tile" id="t-role">' + wiseIcon("both", 30) +
      '<span>역할 나누기</span><small id="s-role">사람과 AI의 몫</small></button>' +
      '<button type="button" class="tile" id="t-plan">' + wiseIcon("star", 30) +
      '<span>설계실</span><small id="s-plan">해결 절차 4단계</small></button>' +
      '<button type="button" class="tile" id="t-board">' + wiseIcon("talk", 30) +
      '<span>마을 게시판</span><small id="s-board">다른 모둠의 문제 보기</small></button>' +
      '</div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="t-card" class="ghost">계획 카드 보기</button></div></div>' +
      '<div class="card"><h3>우리 모둠이 받은 배지</h3>' +
      '<div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("obs",
      '<div class="card"><span class="pill">관찰대</span>' +
      '<h2 style="margin-top:10px">불편을 세 개 적어요</h2>' +
      '<p class="muted">우리 학교나 우리 동네에서 겪은 일을 적어요. ' +
      '떠오르지 않으면 오늘 하루를 되짚어 봐요.</p>' + candBlock() +
      '<div id="rank" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-narrow" class="ghost">고른 문제를 좁히러 가기</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("narrow",
      '<div class="card"><span class="pill">작업대</span>' +
      '<h2 style="margin-top:10px">한 문장으로 좁혀요</h2>' +
      '<p class="muted" id="pickedline">고른 문제를 관찰대에서 먼저 골라 주세요.</p>' +
      '<label for="who">누가 (어떤 사람이)</label>' +
      '<input id="who" maxlength="40" placeholder="예: 우리 학교 저학년 동생들이">' +
      '<label for="when">언제</label>' +
      '<input id="when" maxlength="40" placeholder="예: 점심시간 분리배출을 할 때">' +
      '<label for="what">무엇 때문에 불편한가</label>' +
      '<input id="what" maxlength="60" placeholder="예: 어느 통에 넣을지 몰라서">' +
      '<div class="note" id="oneline">칸을 채우면 한 문장이 만들어져요.</div>' +
      '<div id="gauge" style="margin-top:10px"></div>' +
      '<p class="muted" id="doru" style="margin-top:8px"></p>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-judge" class="ghost">판정실로 가기</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("judge",
      '<div class="card"><span class="pill">판정실</span>' +
      '<h2 style="margin-top:10px">이 문제에 AI를 써도 될까요</h2>' +
      '<p class="muted" id="judge-problem"></p>' +
      '<label>신호를 고르세요</label><div id="siglist"></div>' +
      '<label>왜 그렇게 보았나요</label><div id="whylist"></div>' +
      '<div id="condbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-role" class="ghost">역할 나누러 가기</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("role",
      '<div class="card"><span class="pill">역할</span>' +
      '<h2 style="margin-top:10px">사람이 할 일과 AI가 할 일</h2>' +
      '<p class="muted">여섯 가지 일을 나눠 봐요. 정답이 아니라 우리 모둠의 약속이에요.</p>' +
      '<div id="rolelist"></div>' +
      '<p class="note" id="rolemsg" style="margin-top:12px"></p>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-plan" class="ghost">설계실로 가기</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("plan",
      '<div class="card"><span class="pill">설계실</span>' +
      '<h2 style="margin-top:10px">해결 절차 네 단계를 세워요</h2>' +
      '<p class="muted">여덟 장 가운데 네 장을 골라요. 고른 차례가 순서가 되고, ' +
      '위로 단추로 바꿀 수 있어요.</p>' +
      '<div id="chosen"></div>' +
      '<label>절차 카드</label><div id="cardlist"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-card" class="ghost">계획 카드 보기</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("board",
      '<div class="card"><span class="pill">게시판</span>' +
      '<h2 style="margin-top:10px">마을 게시판</h2>' +
      '<p class="muted">같은 방의 다른 모둠이 좁힌 문제를 읽어 봐요. ' +
      '점수와 이름은 띄우지 않아요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="peek">게시판 불러오기</button></div>' +
      '<div id="boardbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">연구소로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">우리 모둠 계획 카드</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">연구소로</button></div></div>' +
      '<div class="safe">사람 얼굴이 담긴 사진은 쓰지 않아요. ' +
      '이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>');

    return h;
  }

  function candBlock() {
    var h = "";
    var ph = ["예: 급식이 많이 남는다", "예: 분리배출이 헷갈린다", "예: 복도가 미끄럽다"];
    for (var i = 0; i < 3; i++) {
      h += '<label for="cand' + i + '">후보 ' + (i + 1) + '</label>' +
        '<input id="cand' + i + '" class="cnd" data-i="' + i + '" maxlength="60" placeholder="' +
        ph[i] + '">';
      for (var m = 0; m < MARKS.length; m++) {
        h += '<div class="row" style="margin:6px 0 0">' +
          '<span class="muted" style="min-width:170px">' + esc(MARKS[m].t) + '</span>';
        for (var v = 1; v <= 3; v++) {
          h += '<button type="button" class="chip sc" data-c="' + i + '" data-k="' + MARKS[m].k +
            '" data-v="' + v + '" style="width:auto;margin:0">' + v + '</button>';
        }
        h += '</div>';
      }
      h += '<div class="row" style="margin:8px 0 14px">' +
        '<button type="button" class="ghost pk" data-i="' + i +
        '" style="width:auto">이 문제로 정하기</button>' +
        '<span class="muted" id="pkmsg' + i + '"></span></div>';
    }
    return h;
  }

  /* ---------- 관찰대 ---------- */

  function paintRank() {
    if (!$("rank")) { return; }
    var rows = [];
    for (var i = 0; i < 3; i++) {
      var t = candText(i);
      if (!t) { continue; }
      var s = st.scores[i] || {};
      var sum = Number(s.can || 0) + Number(s.many || 0) + Number(s.check || 0);
      rows.push({ i: i, t: t, sum: sum, can: Number(s.can || 0),
        many: Number(s.many || 0), check: Number(s.check || 0) });
    }
    if (!rows.length) {
      $("rank").innerHTML = '<p class="muted">후보를 적으면 표가 나와요.</p>';
      return;
    }
    rows.sort(function (a, b) { return b.sum - a.sum; });
    var h = '<div class="scroll"><table><tr><th>후보</th><th>바꿀 수 있나</th>' +
      '<th>도움되나</th><th>확인할 수 있나</th><th>합계</th></tr>';
    for (var k = 0; k < rows.length; k++) {
      h += "<tr><td>" + esc(rows[k].t) + (st.pick === rows[k].i ? ' <span class="pill">고름</span>' : "") +
        "</td><td>" + rows[k].can + "</td><td>" + rows[k].many + "</td><td>" +
        rows[k].check + "</td><td>" + rows[k].sum + "</td></tr>";
    }
    h += "</table></div>";
    if (rows[0].sum) {
      h += '<p class="muted" style="margin-top:8px">점수만 보면 지금 1위는 ' +
        esc(rows[0].t) + ' 예요. 1위가 아닌 것을 골라도 돼요. 까닭을 말할 수 있으면 돼요.</p>';
    }
    $("rank").innerHTML = h;
    for (var p = 0; p < 3; p++) {
      if ($("pkmsg" + p)) {
        $("pkmsg" + p).textContent = st.pick === p ? "이 문제로 정했어요." : "";
      }
    }
  }

  function markChips() {
    var scs = document.querySelectorAll("#activity .sc");
    for (var i = 0; i < scs.length; i++) {
      var c = scs[i].getAttribute("data-c"), k = scs[i].getAttribute("data-k"),
        v = scs[i].getAttribute("data-v");
      var on = st.scores[c] && String(st.scores[c][k]) === String(v);
      scs[i].className = "chip sc" + (on ? " on" : "");
    }
  }

  /* ---------- 좁히기 ---------- */

  function paintNarrow() {
    if (!$("oneline")) { return; }
    var line = oneLine();
    $("oneline").textContent = line ? line : "칸을 채우면 한 문장이 만들어져요.";
    var n = narrowScore();
    if ($("gauge")) {
      var rows = [];
      for (var i = 0; i < 4; i++) {
        rows.push('<span class="tag" style="' +
          (i < n ? 'background:var(--accent-soft);color:var(--accent);font-weight:800' : '') +
          '">' + (i < n ? "채움" : "빈칸") + '</span>');
      }
      $("gauge").innerHTML = '<b>좁힘 눈금 ' + n + ' / 4</b> ' + rows.join(" ") +
        barHtml(n, 4);
    }
    if ($("doru")) {
      var say = "두루 : 누가요? 언제요? 무엇 때문에요?";
      if (n === 3) { say = "두루 : 좋아요. 조금만 더 자세히 쓰면 눈금이 다 차요."; }
      if (n >= 4) { say = "두루 : 이제 우리가 해 볼 수 있는 문제예요. 판정실로 가요."; }
      if (n === 0) { say = "두루 : 넓은 말은 아무것도 할 수 없어요. 한 칸씩 채워 봐요."; }
      $("doru").textContent = say;
    }
    if ($("pickedline")) {
      var p = pickedText();
      $("pickedline").textContent = p
        ? ("고른 문제 : " + p)
        : "고른 문제를 관찰대에서 먼저 골라 주세요.";
    }
    if (narrowed()) { award("문제를 좁힘"); }
  }

  /* ---------- 판정실 ---------- */

  function paintJudge() {
    if (!$("siglist")) { return; }
    if ($("judge-problem")) {
      var line = oneLine();
      $("judge-problem").textContent = line ? line : "먼저 문제를 좁혀 주세요.";
    }
    var h = "";
    for (var s = 0; s < SIGNALS.length; s++) {
      h += '<button type="button" class="chip sig' + (st.signal === s ? " on" : "") +
        '" data-s="' + s + '">' + wiseIcon(SIGNALS[s].icon, 28) + esc(SIGNALS[s].name) +
        ' · ' + esc(SIGNALS[s].say) + '</button>';
    }
    $("siglist").innerHTML = h;
    var sigs = document.querySelectorAll("#activity .sig");
    for (var i = 0; i < sigs.length; i++) {
      sigs[i].onclick = function () {
        st.signal = Number(this.getAttribute("data-s"));
        paintJudge();
        paintHub();
      };
    }
    var wh = "";
    for (var w = 0; w < WHYS.length; w++) {
      wh += '<button type="button" class="chip wy' + (st.why === w ? " on" : "") +
        '" data-w="' + w + '">' + esc(WHYS[w]) + '</button>';
    }
    if ($("whylist")) {
      $("whylist").innerHTML = wh;
      var wys = document.querySelectorAll("#activity .wy");
      for (var k = 0; k < wys.length; k++) {
        wys[k].onclick = function () {
          st.why = Number(this.getAttribute("data-w"));
          paintJudge();
          paintHub();
        };
      }
    }
    paintCond();
    if (st.signal >= 0 && st.why >= 0) { award("판정 완료"); }
  }

  function paintCond() {
    if (!$("condbox")) { return; }
    if (st.signal === 1 || st.signal === 2) {
      $("condbox").innerHTML = '<label for="cond">어떤 조건이면 될까요</label>' +
        '<input id="cond" maxlength="70" value="' + esc(st.cond || "") +
        '" placeholder="예: 남는 양만 세고 이름은 넣지 않는다면">' +
        '<p class="muted" style="margin-top:6px">이 조건은 우리 반 약속과 이어져요.</p>';
    } else if (st.signal === 3) {
      $("condbox").innerHTML = '<div class="note">두루 : AI 없이 할 방법은 무엇일까요?</div>' +
        '<label for="cond">AI 없이 해 볼 방법</label>' +
        '<input id="cond" maxlength="70" value="' + esc(st.alt || "") +
        '" placeholder="예: 직접 세어 보고 손으로 안내판을 만든다">';
    } else {
      $("condbox").innerHTML = "";
      return;
    }
    if ($("cond")) {
      $("cond").oninput = function () { st[condKey()] = this.value; };
    }
  }

  /* ---------- 역할 ---------- */

  function paintRoles() {
    if (!$("rolelist")) { return; }
    var h = "";
    for (var i = 0; i < ROLES.length; i++) {
      h += '<div class="card" style="margin:8px 0;padding:14px"><p style="margin:0 0 8px">' +
        esc(ROLES[i].t) + '</p><div class="row">';
      for (var o = 0; o < WHO.length; o++) {
        h += '<button type="button" class="chip rl' + (st.roles[i] === o ? " on" : "") +
          '" data-r="' + i + '" data-w="' + o + '" style="width:auto;margin:0">' +
          wiseIcon(WHO_ICON[o], 24) + esc(WHO[o]) + '</button>';
      }
      h += '</div></div>';
    }
    $("rolelist").innerHTML = h;
    var els = document.querySelectorAll("#activity .rl");
    for (var k = 0; k < els.length; k++) {
      els[k].onclick = function () {
        st.roles[this.getAttribute("data-r")] = Number(this.getAttribute("data-w"));
        paintRoles();
        paintHub();
      };
    }
    if ($("rolemsg")) {
      var n = countOf(st.roles);
      if (!n) {
        $("rolemsg").textContent = "두루 : 여섯 가지 일을 나눠 봐요.";
      } else {
        var loose = humanLoose();
        $("rolemsg").textContent = loose.length
          ? ("두루 : " + loose.join(", ") + " 는 사람이 하는 것이 우리 반 기준이에요. 그대로 두어도 돼요. 까닭을 말해 봐요.")
          : ("역할을 정한 일 " + n + " / " + ROLES.length + " 개. 사람이 할 일이 또렷해요.");
      }
    }
    if (countOf(st.roles) >= 4) { award("역할 나눔"); }
  }

  /* 사람이 해야 한다고 본 일을 AI 에게 맡긴 항목 */
  function humanLoose() {
    var out = [];
    for (var i = 0; i < ROLES.length; i++) {
      if (!ROLES[i].human) { continue; }
      if (st.roles[i] === 1) { out.push(ROLES[i].t); }
    }
    return out;
  }

  /* ---------- 설계실 ---------- */

  function hasStep(i) {
    for (var k = 0; k < st.steps.length; k++) {
      if (st.steps[k] === i) { return true; }
    }
    return false;
  }

  function paintPlan() {
    if (!$("cardlist")) { return; }
    var h = "";
    for (var i = 0; i < STEPS.length; i++) {
      h += '<button type="button" class="chip stp' + (hasStep(i) ? " on" : "") +
        '" data-i="' + i + '">' + esc(STEPS[i]) + '</button>';
    }
    $("cardlist").innerHTML = h;
    var els = document.querySelectorAll("#activity .stp");
    for (var k = 0; k < els.length; k++) {
      els[k].onclick = function () {
        var v = Number(this.getAttribute("data-i"));
        if (hasStep(v)) {
          var next = [];
          for (var m = 0; m < st.steps.length; m++) {
            if (st.steps[m] !== v) { next.push(st.steps[m]); }
          }
          st.steps = next;
        } else if (st.steps.length >= 4) {
          wiseToast("네 장까지 고를 수 있어요. 한 장을 빼고 골라요.");
          return;
        } else {
          st.steps.push(v);
        }
        paintPlan();
        paintHub();
      };
    }
    paintChosen();
    if (st.steps.length >= 4) { award("설계자"); }
  }

  function paintChosen() {
    if (!$("chosen")) { return; }
    if (!st.steps.length) {
      $("chosen").innerHTML = '<p class="muted">아직 고른 카드가 없어요. 아래에서 네 장을 골라요.</p>';
      return;
    }
    var h = '<div class="fade-in">';
    for (var i = 0; i < st.steps.length; i++) {
      h += '<div class="card" style="margin:8px 0;padding:12px">' +
        '<div class="row" style="justify-content:space-between">' +
        '<span><b>' + (i + 1) + '단계</b> ' + esc(STEPS[st.steps[i]]) + '</span>' +
        '<span><button type="button" class="chip up" data-i="' + i +
        '" style="width:auto;margin:0">위로</button></span></div></div>';
    }
    h += '<p class="muted">고른 카드 ' + st.steps.length + ' / 4</p></div>';
    $("chosen").innerHTML = h;
    var ups = document.querySelectorAll("#activity .up");
    for (var k = 0; k < ups.length; k++) {
      ups[k].onclick = function () {
        var idx = Number(this.getAttribute("data-i"));
        if (idx <= 0) { return; }
        var tmp = st.steps[idx - 1];
        st.steps[idx - 1] = st.steps[idx];
        st.steps[idx] = tmp;
        paintChosen();
      };
    }
  }

  /* ---------- 마을 게시판 ---------- */

  function peek() {
    if (!$("boardbox")) { return; }
    st.boardTried = true;
    if (me.solo) {
      $("boardbox").innerHTML = '<p class="muted">혼자 체험 중에는 다른 모둠 문장이 없어요. ' +
        '나머지는 그대로 해 볼 수 있어요.</p>';
      paintHub();
      return;
    }
    $("boardbox").innerHTML = wiseSpinner("게시판을 읽어 오는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      var rows = [], k;
      for (k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload || {};
        if (!p.oneline) { continue; }
        rows.push({ line: p.oneline, sig: p.signal });
      }
      st.board = rows;
      $("boardbox").innerHTML = boardHtml(rows);
      $("boardbox").className = "fade-in";
      paintHub();
    })["catch"](function () {
      $("boardbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function boardHtml(rows) {
    if (!rows.length) {
      return '<p class="muted">아직 올라온 문장이 없어요. 다른 모둠이 좁히면 여기에 붙어요.</p>';
    }
    var h = "";
    for (var i = 0; i < rows.length && i < 12; i++) {
      var s = rows[i].sig;
      h += '<div class="card" style="margin:8px 0;padding:14px">' +
        '<p style="margin:0">' + esc(rows[i].line) + '</p>' +
        (s >= 0 && SIGNALS[s]
          ? '<p class="muted" style="margin-top:6px">' + esc(SIGNALS[s].name) + ' · ' +
            esc(SIGNALS[s].say) + '</p>'
          : "") + '</div>';
    }
    return h;
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
  }

  function badgeList() {
    var out = [], k;
    for (k in st.badges) { if (st.badges.hasOwnProperty(k)) { out.push(k); } }
    return out;
  }

  function paintHub() {
    if (candCount() >= 3) { award("관찰가"); }
    if (markCount() >= 9) { award("꼼꼼한 연구원"); }

    if ($("s-obs")) {
      $("s-obs").textContent = "적은 후보 " + candCount() + " / 3" +
        (st.pick >= 0 ? " · 고른 문제 있음" : "");
      $("s-narrow").textContent = "좁힘 눈금 " + narrowScore() + " / 4";
      $("s-judge").textContent = narrowed()
        ? (st.signal >= 0 ? esc(SIGNALS[st.signal].name) + " 판정" : "신호등으로 판단하기")
        : "먼저 문제를 좁혀요";
      $("s-role").textContent = "정한 역할 " + countOf(st.roles) + " / " + ROLES.length;
      $("s-plan").textContent = narrowed()
        ? ("고른 절차 " + st.steps.length + " / 4") : "먼저 문제를 좁혀요";
      $("s-board").textContent = st.board ? "게시판을 읽었어요" : "다른 모둠의 문제 보기";

      var tiles = [
        ["t-obs", candCount() >= 3 && st.pick >= 0],
        ["t-narrow", narrowed()],
        ["t-judge", st.signal >= 0 && st.why >= 0],
        ["t-role", countOf(st.roles) >= 4],
        ["t-plan", st.steps.length >= 4],
        ["t-board", !!st.board]
      ];
      for (var i = 0; i < tiles.length; i++) {
        if ($(tiles[i][0])) {
          $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : "");
        }
      }
    }

    var names = badgeList();
    if ($("badges")) {
      if (names.length) {
        var h = "";
        for (var b = 0; b < names.length; b++) {
          h += '<span class="pill">' + esc(names[b]) + '</span> ';
        }
        $("badges").innerHTML = h;
      } else {
        $("badges").innerHTML = '<span class="muted">아직 없어요. 관찰대부터 가 봐요.</span>';
      }
    }
    paintHud();
  }

  function paintHud() {
    wiseHud([
      { label: "후보", done: candCount(), total: 3 },
      { label: "좁힘", done: narrowScore(), total: 4 },
      { label: "절차", done: st.steps.length, total: 4 }
    ]);
  }

  /* 좁히기 전에는 판정실과 설계실을 열지 않는다. 잠금이 이 앱의 뼈대다. */
  function needNarrow(target, text) {
    if (narrowed()) { goSlow(target, text); return; }
    wiseToast("두루 : 먼저 문제를 좁혀요. 눈금이 3에 닿으면 열려요.");
    goSlow("narrow", "좁히기 작업대를 여는 중");
  }

  /* ---------- 계획 카드 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var line = oneLine();
    if (!line) {
      $("mine").innerHTML = '<p class="muted">아직 좁힌 문제가 없어요. 좁히기 작업대부터 가 봐요.</p>';
      return;
    }
    var h = '<div class="fade-in"><p class="big">' + esc(line) + '</p>';
    h += '<p style="margin-top:8px">좁힘 눈금 ' + narrowScore() + ' / 4' +
      (st.signal >= 0 ? ' · ' + esc(SIGNALS[st.signal].name) : "") + '</p>';
    if (st.why >= 0) {
      h += '<p class="muted">고른 근거 : ' + esc(WHYS[st.why]) + '</p>';
    }
    if (condText()) {
      h += '<p class="muted">' + (st.signal === 3 ? "AI 없이 할 방법 : " : "조건 : ") +
        esc(condText()) + '</p>';
    }
    if (st.steps.length) {
      h += '<h3 style="margin-top:12px">해결 절차</h3>';
      for (var i = 0; i < st.steps.length; i++) {
        h += '<p style="margin:4px 0">' + (i + 1) + '. ' + esc(STEPS[st.steps[i]]) + '</p>';
      }
    }
    var human = [];
    for (var r = 0; r < ROLES.length; r++) {
      if (st.roles[r] === 0) { human.push(ROLES[r].t); }
    }
    if (human.length) {
      h += '<p style="margin-top:10px">사람이 할 일 : ' + esc(human.join(", ")) + '</p>';
    }
    h += '</div>';
    $("mine").innerHTML = h;
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "hub") { paintHub(); }
    if (id === "obs") { markChips(); paintRank(); }
    if (id === "narrow") { paintNarrow(); }
    if (id === "judge") { paintJudge(); }
    if (id === "role") { paintRoles(); }
    if (id === "plan") { paintPlan(); }
    if (id === "card") { paintMine(); }
    if (id === "board" && $("boardbox") && !st.board && !st.boardTried) {
      $("boardbox").innerHTML = '<p class="muted">게시판 불러오기를 눌러요.</p>';
    }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.scores) { st.scores = saved.scores; }
      if (saved.pick !== undefined) { st.pick = saved.pick; }
      if (saved.signal !== undefined) { st.signal = saved.signal; }
      if (saved.why !== undefined) { st.why = saved.why; }
      if (saved.roles) { st.roles = saved.roles; }
      if (saved.steps) { st.steps = saved.steps; }
      if (saved.cond) { st.cond = saved.cond; }
      if (saved.alt) { st.alt = saved.alt; }
      var keys = ["cand0", "cand1", "cand2", "who", "when", "what"];
      for (var k = 0; k < keys.length; k++) {
        if (saved[keys[k]] && $(keys[k])) { $(keys[k]).value = saved[keys[k]]; }
      }
    }

    $("go-hub").onclick = function () { goSlow("hub", "연구소 문을 여는 중", 520); };
    $("t-obs").onclick = function () { goSlow("obs", "관찰대를 여는 중"); };
    $("t-narrow").onclick = function () { goSlow("narrow", "작업대를 여는 중"); };
    $("t-judge").onclick = function () { needNarrow("judge", "판정실을 여는 중"); };
    $("t-role").onclick = function () { goSlow("role", "역할 판을 여는 중"); };
    $("t-plan").onclick = function () { needNarrow("plan", "설계실을 여는 중"); };
    $("t-board").onclick = function () { goSlow("board", "게시판을 여는 중"); };
    $("t-card").onclick = function () { goSlow("card", "계획 카드를 만드는 중"); };
    $("to-narrow").onclick = function () { goSlow("narrow", "작업대를 여는 중"); };
    $("to-judge").onclick = function () { needNarrow("judge", "판정실을 여는 중"); };
    $("to-role").onclick = function () { goSlow("role", "역할 판을 여는 중"); };
    $("to-plan").onclick = function () { needNarrow("plan", "설계실을 여는 중"); };
    $("to-card").onclick = function () { goSlow("card", "계획 카드를 만드는 중"); };
    $("peek").onclick = peek;

    var ins = document.querySelectorAll("#activity .cnd");
    for (var i = 0; i < ins.length; i++) {
      ins[i].oninput = function () { paintRank(); paintHub(); };
    }
    var narrowIds = ["who", "when", "what"];
    for (var n = 0; n < narrowIds.length; n++) {
      if ($(narrowIds[n])) {
        $(narrowIds[n]).oninput = function () { paintNarrow(); paintHub(); };
      }
    }
    var scs = document.querySelectorAll("#activity .sc");
    for (var s = 0; s < scs.length; s++) {
      scs[s].onclick = function () {
        var c = this.getAttribute("data-c"), k = this.getAttribute("data-k"),
          v = Number(this.getAttribute("data-v"));
        if (!st.scores[c]) { st.scores[c] = {}; }
        st.scores[c][k] = v;
        markChips();
        paintRank();
        paintHub();
      };
    }
    var pks = document.querySelectorAll("#activity .pk");
    for (var p = 0; p < pks.length; p++) {
      pks[p].onclick = function () {
        var idx = Number(this.getAttribute("data-i"));
        if (!candText(idx)) { wiseToast("먼저 후보를 적어 주세요."); return; }
        st.pick = idx;
        paintRank();
        paintNarrow();
        paintHub();
        wiseToast("이 문제로 정했어요. 이제 좁혀 봐요.");
      };
    }
    $("save-card").onclick = function () {
      var steps = [];
      for (var i = 0; i < st.steps.length; i++) { steps.push((i + 1) + ". " + STEPS[st.steps[i]]); }
      wiseCardPng("AI for Good 계획 " + me.nick, [
        oneLine() || "문제를 좁히는 중입니다",
        st.signal >= 0 ? ("신호 : " + SIGNALS[st.signal].name + " · " + SIGNALS[st.signal].say) : "신호 : 아직",
        steps.length ? steps[0] : "절차 : 아직",
        steps.length > 1 ? steps[1] : "",
        "사람이 정하고 사람이 책임진다."
      ], "wise_l11_" + me.nick);
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var b = 0; b < backs.length; b++) {
      backs[b].onclick = function () { goSlow("hub", "연구소로 돌아가는 중", 300); };
    }

    wiseNote("불편을 세 개 모으고 하나를 골라 좁혀요. 좁혀야 판정실과 설계실이 열려요.");
    wiseGo("story");
    markChips();
    paintRank();
    paintNarrow();
    paintJudge();
    paintRoles();
    paintPlan();
    paintHub();
  }

  function activityDraft() {
    return {
      cand0: candText(0), cand1: candText(1), cand2: candText(2),
      who: val("who"), when: val("when"), what: val("what"),
      scores: st.scores, pick: st.pick, signal: st.signal, why: st.why,
      cond: st.cond || "", alt: st.alt || "", roles: st.roles, steps: st.steps
    };
  }

  function activityAutofill() {
    var fill = {
      cand0: "급식이 많이 남는다", cand1: "분리배출이 헷갈린다", cand2: "복도가 미끄럽다",
      who: "우리 학교 저학년 동생들이", when: "점심시간 분리배출을 할 때",
      what: "어느 통에 넣을지 몰라서"
    };
    for (var k in fill) {
      if (fill.hasOwnProperty(k) && $(k)) { $(k).value = fill[k]; }
    }
    st.scores = { "0": { can: 3, many: 3, check: 2 }, "1": { can: 3, many: 2, check: 3 } };
    st.pick = 1;
    st.signal = 1;
    st.why = 2;
    st.cond = "쓰레기 사진만 찍고 사람은 넣지 않는다면";
    st.alt = "";
    st.roles = { "0": 0, "1": 2, "2": 2, "3": 0 };
    st.steps = [0, 2, 3, 4];
  }

  function activityCollect() {
    if (!candCount()) {
      $("w-msg").innerHTML = '<span class="warn">불편 후보를 적어 주세요. 하나도 없어요.</span>';
      goSlow("obs", "관찰대로 데려가는 중");
      return null;
    }
    if (st.pick < 0 || !pickedText()) {
      $("w-msg").innerHTML = '<span class="warn">후보 가운데 하나를 골라 주세요. ' +
        '"이 문제로 정하기"를 누르면 돼요.</span>';
      goSlow("obs", "관찰대로 데려가는 중");
      return null;
    }
    if (!narrowed()) {
      $("w-msg").innerHTML = '<span class="warn">문제를 더 좁혀 주세요. 좁힘 눈금이 ' +
        narrowScore() + ' 이에요. 3이 되면 제출할 수 있어요.</span>';
      goSlow("narrow", "좁히기 작업대를 여는 중");
      return null;
    }
    if (st.signal < 0 || st.why < 0) {
      $("w-msg").innerHTML = '<span class="warn">신호등 판단과 근거까지 고른 뒤에 제출해요.</span>';
      goSlow("judge", "판정실을 여는 중");
      return null;
    }
    if (st.steps.length < 4) {
      $("w-msg").innerHTML = '<span class="warn">해결 절차 네 단계를 세운 뒤에 제출해요. 지금 ' +
        st.steps.length + '단계예요.</span>';
      goSlow("plan", "설계실을 여는 중");
      return null;
    }

    var steps = [];
    for (var i = 0; i < st.steps.length; i++) { steps.push(STEPS[st.steps[i]]); }
    var loose = humanLoose();
    wiseCelebrate("계획을 세웠어요", [
      esc(oneLine()),
      "신호 <b>" + esc(SIGNALS[st.signal].name) + "</b> · 절차 <b>" + steps.length + "단계</b>",
      loose.length ? ("살펴볼 점 : " + esc(loose.join(", ")) + " 를 AI에게 두었어요.")
        : "결정과 책임은 사람이 맡았어요.",
      "다음 시간에는 이 계획대로 만들어 발표해요."
    ], "좋아요");

    return {
      cands: [candText(0), candText(1), candText(2)],
      scores: st.scores, pick: st.pick, problem: pickedText(),
      who: val("who"), when: val("when"), what: val("what"),
      oneline: oneLine(), narrow: narrowScore(),
      signal: st.signal, signalName: SIGNALS[st.signal].name,
      why: st.why, whyName: WHYS[st.why],
      cond: condText(), condKind: st.signal === 3 ? "대안" : "조건",
      steps: st.steps, stepNames: steps, roles: st.roles, loose: loose,
      badges: badgeList()
    };
  }

  /* ---------- 교사 화면 ---------- */

  function teacherSummary(list) {
    var sig = [0, 0, 0, 0], narrowOk = 0, planOk = 0, looseGroups = 0;
    var stepCount = [];
    for (var s0 = 0; s0 < STEPS.length; s0++) { stepCount.push(0); }

    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (p.signal !== undefined && p.signal >= 0 && sig[p.signal] !== undefined) {
        sig[Number(p.signal)] += 1;
      }
      if (p.narrow >= 3) { narrowOk++; }
      var stp = p.steps || [];
      if (stp.length >= 4) { planOk++; }
      for (var k = 0; k < stp.length; k++) {
        if (stepCount[Number(stp[k])] !== undefined) { stepCount[Number(stp[k])] += 1; }
      }
      if (p.loose && p.loose.length) { looseGroups++; }
    }

    var h = '<p class="muted">제출 ' + list.length + '모둠 · 문제를 좁힌 모둠 ' + narrowOk +
      ' · 절차 4단계를 세운 모둠 ' + planOk + ' · 결정을 AI에 둔 모둠 ' + looseGroups + '</p>';

    var sigRows = [];
    for (var g = 0; g < SIGNALS.length; g++) {
      sigRows.push({ label: SIGNALS[g].name, value: sig[g], color: SIGNALS[g].color });
    }
    h += '<h3 style="margin-top:14px">신호 분포</h3>' + wiseBars(sigRows, 560);

    h += '<h3 style="margin-top:16px">모둠별 계획</h3><div class="scroll"><table>' +
      '<tr><th>모둠</th><th>고른 문제</th><th>한 문장 정의</th><th>좁힘</th><th>신호</th>' +
      '<th>첫 절차</th><th>살펴볼 점</th></tr>';
    var shown = 0;
    for (var m = 0; m < list.length; m++) {
      var q2 = list[m].payload || {};
      if (!q2.oneline && !q2.problem) { continue; }
      shown++;
      var note = [];
      if (q2.narrow !== undefined && q2.narrow < 3) { note.push("더 좁혀야 함"); }
      if (q2.loose && q2.loose.length) { note.push("결정을 AI에 둠"); }
      h += "<tr><td>" + esc(list[m].nick || list[m].group || "") + "</td><td>" +
        esc(q2.problem || "") + "</td><td>" + esc(q2.oneline || "") + "</td><td>" +
        esc(String(q2.narrow === undefined ? "" : q2.narrow)) + "</td><td>" +
        esc(q2.signalName || "") + "</td><td>" +
        esc(q2.stepNames && q2.stepNames.length ? q2.stepNames[0] : "") + "</td><td>" +
        (note.length ? '<span class="warn">' + esc(note.join(", ")) + '</span>' : "") + "</td></tr>";
    }
    if (!shown) {
      h += '<tr><td colspan="7">아직 올라온 계획이 없어요.</td></tr>';
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">많이 고른 절차</h3><div class="scroll"><table>' +
      '<tr><th>절차 카드</th><th>고른 모둠</th></tr>';
    for (var c = 0; c < STEPS.length; c++) {
      h += "<tr><td>" + esc(STEPS[c]) + "</td><td>" + stepCount[c] + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">모둠이 쓴 조건과 대안</h3><div class="scroll"><table>' +
      '<tr><th>모둠</th><th>신호</th><th>무엇</th><th>내용</th></tr>';
    var lines = 0;
    for (var r = 0; r < list.length; r++) {
      var q3 = list[r].payload || {};
      if (!q3.cond) { continue; }
      lines++;
      h += "<tr><td>" + esc(list[r].nick || "") + "</td><td>" + esc(q3.signalName || "") +
        "</td><td>" + esc(q3.condKind || "조건") + "</td><td>" + esc(q3.cond) + "</td></tr>";
    }
    if (!lines) {
      h += '<tr><td colspan="4">아직 조건 문장이 없어요.</td></tr>';
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var h = '<p class="muted">모둠이 좁힌 문제를 함께 읽어요.</p>';
    var shown = 0;
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.oneline) { continue; }
      shown++;
      h += '<div class="card"><p class="pill">' + esc(list[i].nick || "") + '</p>' +
        '<p class="big" style="margin-top:10px">' + esc(p.oneline) + '</p>' +
        '<p class="muted">' + esc(p.signalName || "") +
        (p.stepNames && p.stepNames.length ? ' · 첫 절차 : ' + esc(p.stepNames[0]) : "") +
        '</p></div>';
    }
    if (!shown) {
      h += '<p class="big">아직 올라온 문장이 없어요.</p>';
    }
    return h;
  }
"""
