# -*- coding: utf-8 -*-
"""6차시 AI 신호등 판정단.

여정형으로 만든다. 폼 하나가 아니라 화면 여덟 개를 지나간다.

  이야기 → 판정소 허브 → 신호 익히기 놀이 → 1차 판정 20장
  → 우리 반과 견주기 → 2차 판정 → 조건 작성소 → 판정단 카드와 완료

판정마다 근거를 골라야 넘어간다. 근거 없는 감이 판단으로 굳지 않게 한다.
바꾼 판정은 지우지 않고 남긴다. 생각을 바꾼 것이 이 차시의 성과이기 때문이다.
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  var SIGNALS = [
    {name:"초록불", say:"그냥 써도 돼", icon:"green"},
    {name:"노랑불", say:"조건을 지키면 돼", icon:"yellow"},
    {name:"주황불", say:"아주 조심해서만", icon:"orange"},
    {name:"빨간불", say:"쓰면 안 돼", icon:"red"}
  ];

  var REASONS = [
    "내 생각을 대신하게 되나",
    "기록이 남아 되돌리기 어렵나",
    "다른 사람에게 영향을 주나",
    "내가 배우는 데 도움이 되나"
  ];

  var CARDS = [
    "숙제를 AI가 다 써 준다",
    "모르는 개념을 다시 설명해 달라고 한다",
    "친구와 다툰 일을 AI에게만 말한다",
    "발표 아이디어를 여러 개 받아 본다",
    "AI로 만든 그림을 표기하고 쓴다",
    "친구 사진을 넣어 그림을 만든다",
    "독후감을 AI가 완성한다",
    "글의 표현을 다듬어 달라고 한다",
    "시험 문제를 AI로 미리 풀어 본다",
    "조사 자료의 출처를 확인해 달라고 한다",
    "친구 이름을 넣어 고민을 물어본다",
    "어려운 낱말 뜻을 물어본다",
    "일기를 AI가 대신 쓴다",
    "내 주장을 쓴 뒤 근거가 부족한지 물어본다",
    "힘든 마음을 AI에게만 털어놓는다",
    "번역을 부탁하고 어색한 곳을 내가 고친다",
    "모둠 발표 자료를 AI가 전부 만든다",
    "학급 규칙 아이디어를 받아 함께 고른다",
    "수행평가 답을 AI에게 받는다",
    "AI가 알려 준 사실을 교과서와 대조한다"
  ];

  /* 신호 익히기 놀이. 정답이 분명한 것만 넣는다. 판정 활동의 준비 운동이다. */
  var QUIZ = [
    {q:"노랑불은 어떤 뜻일까요?", opts:["그냥 써도 돼", "조건을 지키면 돼", "쓰면 안 돼"], ans:1,
     why:"노랑불은 조건을 지키면 써도 된다는 뜻이에요."},
    {q:"주황불과 빨간불은 무엇이 다를까요?",
     opts:["주황은 아주 조심해서만, 빨강은 아예 안 돼", "둘은 똑같아요", "주황이 더 세게 막아요"], ans:0,
     why:"주황은 조건이 아주 까다로운 것이고, 빨강은 하지 않는 것이에요."},
    {q:"신호를 정하는 사람은 누구일까요?", opts:["AI", "우리 반", "아무도 아니에요"], ans:1,
     why:"기준을 정하는 사람은 사람이에요. 우리 반이 함께 정해요."}
  ];

  var st = {
    i: 0, round: 1, first: {}, second: {}, why: {}, cond: {}, badges: {},
    quiz: 0, quizOk: 0, quizPick: -1, classDist: null, done20: false, opened: false,
    order: null
  };

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
      '<h2 style="margin-top:10px">신호등 마을 판정소</h2>' +
      wiseScene("signal") +
      '<p style="margin-top:10px">우리 반이 AI를 쓸 때마다 물음이 생겨요. ' +
      '"이건 써도 될까?" 마을 사람들은 늘 다투었어요.</p>' +
      '<p style="margin-top:8px">그래서 판정소가 문을 열었어요. ' +
      '오늘 여러분은 <b>판정단원</b>이 되어 상황 카드 스무 장을 판정해요.</p>' +
      '<p class="muted" style="margin-top:8px">정답은 미리 정해져 있지 않아요. ' +
      '까닭을 댈 수 있으면 그것이 우리 반의 기준이 돼요.</p>' +
      '<div class="row" style="margin-top:14px"><button type="button" id="go-hub">판정소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>판정소</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-quiz">' + wiseIcon("star", 30) +
      '<span>신호 익히기 놀이</span><small id="s-quiz">세 문제로 몸풀기</small></button>' +
      '<button type="button" class="tile" id="t-judge">' + wiseIcon("check", 30) +
      '<span>1차 판정하기</span><small id="s-judge">상황 카드 20장</small></button>' +
      '<button type="button" class="tile" id="t-class">' + wiseIcon("talk", 30) +
      '<span>우리 반과 견주기</span><small id="s-class">갈린 카드 찾기</small></button>' +
      '<button type="button" class="tile" id="t-again">' + wiseIcon("again", 30) +
      '<span>2차 판정하기</span><small id="s-again">생각이 바뀌었다면</small></button>' +
      '<button type="button" class="tile" id="t-cond">' + wiseIcon("write", 30) +
      '<span>조건 작성소</span><small id="s-cond">노랑과 주황에 조건 달기</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("id", 30) +
      '<span>판정단 카드</span><small id="s-card">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("quiz",
      '<div class="card"><span class="pill">몸풀기</span><h2 style="margin-top:10px">신호 익히기 놀이</h2>' +
      '<div id="quizbox"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">판정소로</button></div></div>');

    h += q("judge",
      '<div class="card"><span class="pill" id="round-tag">1차 판정</span>' +
      '<h2 style="margin-top:10px" id="judge-title">상황 카드를 판정해요</h2>' +
      '<div id="stage6"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="prev" class="plain">앞 카드</button>' +
      '<button type="button" id="next" class="ghost">다음 카드</button>' +
      '<span class="muted" id="pos"></span></div>' +
      '<div class="row" style="margin-top:10px"><button type="button" class="plain back">판정소로</button></div></div>');

    h += q("class",
      '<div class="card"><span class="pill">함께 보기</span><h2 style="margin-top:10px">우리 반은 어떻게 보았을까</h2>' +
      '<p class="muted">의견이 갈린 카드부터 보여 줘요. 다른 생각을 들어 보고 2차 판정을 해요.</p>' +
      '<div class="row" style="margin-top:10px"><button type="button" id="peek">우리 반 분포 불러오기</button>' +
      '<button type="button" id="to-again" class="ghost">2차 판정 시작</button></div>' +
      '<div id="dist" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:10px"><button type="button" class="plain back">판정소로</button></div></div>');

    h += q("cond",
      '<div class="card"><span class="pill">작성소</span><h2 style="margin-top:10px">조건을 달아요</h2>' +
      '<p class="muted">노랑불과 주황불로 판정한 카드에 "어떤 조건이면 되는가"를 씁니다. ' +
      '이 문장이 7차시 우리 반 약속의 재료가 돼요.</p>' +
      '<div id="conds"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">판정소로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span><h2 style="margin-top:10px">나의 판정단 카드</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">판정소로</button></div></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>');

    return h;
  }

  /* ---------- 몸풀기 놀이 ---------- */

  function quizHtml() {
    if (st.quiz >= QUIZ.length) {
      return '<p class="big">' + st.quizOk + ' / ' + QUIZ.length + '</p>' +
        '<p class="muted">몸풀기 끝. 이제 진짜 판정을 해 봐요.</p>' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" id="quiz-go">1차 판정하러 가기</button></div>';
    }
    var item = QUIZ[st.quiz];
    var h = '<p class="muted">' + (st.quiz + 1) + ' / ' + QUIZ.length + '</p>' +
      '<h3 style="margin:8px 0 12px">' + esc(item.q) + '</h3>';
    for (var i = 0; i < item.opts.length; i++) {
      var mark = "";
      if (st.quizPick >= 0) {
        if (i === item.ans) { mark = " on"; }
      }
      h += '<button type="button" class="chip qz' + mark + '" data-o="' + i + '">' +
        esc(item.opts[i]) + '</button>';
    }
    if (st.quizPick >= 0) {
      h += '<p class="' + (st.quizPick === item.ans ? "ok" : "warn") + '" style="margin-top:10px">' +
        (st.quizPick === item.ans ? "맞았어요. " : "다시 봐요. ") + esc(item.why) + '</p>' +
        '<div class="row" style="margin-top:10px"><button type="button" id="quiz-next">다음</button></div>';
    }
    return h;
  }

  function bindQuiz() {
    $("quizbox").innerHTML = quizHtml();
    var opts = document.querySelectorAll("#activity .qz");
    for (var i = 0; i < opts.length; i++) {
      opts[i].onclick = function () {
        if (st.quizPick >= 0) { return; }
        st.quizPick = Number(this.getAttribute("data-o"));
        if (st.quizPick === QUIZ[st.quiz].ans) { st.quizOk += 1; }
        bindQuiz();
      };
    }
    if ($("quiz-next")) {
      $("quiz-next").onclick = function () { st.quiz += 1; st.quizPick = -1; bindQuiz(); paintHub(); };
    }
    if ($("quiz-go")) {
      $("quiz-go").onclick = function () {
        if (st.quizOk === QUIZ.length) { award("몸풀기 완주"); }
        wiseGo("judge");
      };
    }
  }

  /* ---------- 판정 ---------- */

  function cardHtml(i) {
    var h = '<div class="card" style="margin:12px 0 0">' +
      '<h3 style="font-size:20px">' + esc(CARDS[i]) + '</h3>' +
      '<label>신호를 고르세요</label>';
    for (var s = 0; s < SIGNALS.length; s++) {
      h += '<button type="button" class="chip pick" data-c="' + i + '" data-b="' + s + '">' +
        wiseIcon(SIGNALS[s].icon, 28) + esc(SIGNALS[s].name) + ' · ' + esc(SIGNALS[s].say) + '</button>';
    }
    h += '<label>왜 그렇게 보았나요</label>';
    for (var r = 0; r < REASONS.length; r++) {
      h += '<button type="button" class="chip why" data-c="' + i + '" data-r="' + r + '">' +
        esc(REASONS[r]) + '</button>';
    }
    if (st.round === 2 && st.first[i] !== undefined) {
      h += '<p class="muted" style="margin-top:10px">1차에서 나는 ' +
        esc(SIGNALS[st.first[i]].name) + '으로 보았어요.</p>';
    }
    h += '<p id="saved6" style="margin-top:10px;min-height:26px"></p>';
    h += '</div>';
    return h;
  }

  function bind() {
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      picks[i].onclick = function () {
        var c = this.getAttribute("data-c"), b = Number(this.getAttribute("data-b"));
        if (st.round === 1) { st.first[c] = b; } else { st.second[c] = b; }
        mark();
        updatePos();
        paintMine();
        paintConds();
        paintHub();
        advanceIfReady(c);
      };
    }
    var whys = document.querySelectorAll("#activity .why");
    for (var j = 0; j < whys.length; j++) {
      whys[j].onclick = function () {
        var c = this.getAttribute("data-c");
        st.why[c] = Number(this.getAttribute("data-r"));
        mark();
        paintHub();
        advanceIfReady(c);
      };
    }
    mark();
  }

  function advanceIfReady(c) {
    var cur = st.round === 1 ? st.first : st.second;
    if (cur[c] === undefined || st.why[c] === undefined) { return; }
    if (st.i >= CARDS.length - 1) {
      showSaved("마지막 카드까지 판정했어요.");
      return;
    }
    showSaved("기록했어요. 다음 카드로 넘어가요.");
    softDelay(function () {
      if (st.i < CARDS.length - 1) { st.i += 1; paint(); }
    }, 520);
  }

  function showSaved(text) {
    if (!$("saved6")) { return; }
    $("saved6").innerHTML = '<span class="ok">' + esc(text) + '</span>';
    $("saved6").className = "fade-in";
  }

  function mark() {
    var cur = st.round === 1 ? st.first : st.second;
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      var c = picks[i].getAttribute("data-c"), b = Number(picks[i].getAttribute("data-b"));
      picks[i].className = "chip pick" + (cur[c] === b ? " on" : "");
    }
    var whys = document.querySelectorAll("#activity .why");
    for (var j = 0; j < whys.length; j++) {
      var c2 = whys[j].getAttribute("data-c"), r = Number(whys[j].getAttribute("data-r"));
      whys[j].className = "chip why" + (st.why[c2] === r ? " on" : "");
    }
  }

  function paint() {
    if ($("stage6")) {
      $("stage6").innerHTML = cardHtml(cur());
      $("stage6").className = "fade-in";
      bind();
    }
    if ($("pos")) {
      $("pos").textContent = (st.i + 1) + " / " + CARDS.length + " · 판정한 카드 " +
        countOf(st.round === 1 ? st.first : st.second) + "장";
    }
    if ($("round-tag")) { $("round-tag").textContent = st.round === 1 ? "1차 판정" : "2차 판정"; }
    if ($("prev")) { $("prev").disabled = st.i <= 0; }
    if ($("next")) { $("next").disabled = st.i >= CARDS.length - 1; }
    paintHud();
  }

  /* 지금 보고 있는 카드 번호. 2차 판정에서는 갈린 카드부터 도는 차례가 따로 있다. */
  function cur() {
    if (st.order && st.order[st.i] !== undefined) { return st.order[st.i]; }
    return st.i;
  }

  /* 학급 분포를 보았으면 갈린 카드를 앞에 세운다. 보지 않았으면 원래 차례로 둔다. */
  function buildOrder() {
    if (!st.classDist) { st.order = null; return false; }
    var scored = [], rest = [], i;
    for (i = 0; i < CARDS.length; i++) {
      if (st.classDist[i]) { scored.push(i); } else { rest.push(i); }
    }
    if (!scored.length) { st.order = null; return false; }
    scored.sort(function (a, b) {
      return splitScore(st.classDist[a]) - splitScore(st.classDist[b]);
    });
    st.order = scored.concat(rest);
    return true;
  }

  function startRound2() {
    if (countOf(st.first) < 5) {
      wiseToast("1차 판정을 다섯 장 넘게 마친 뒤에 열려요.");
      return;
    }
    st.round = 2;
    st.i = 0;
    if (buildOrder()) {
      wiseNote("의견이 갈린 카드부터 보여 줘요. 생각이 달라졌으면 색을 바꿔요.");
    } else {
      wiseNote("우리 반 분포를 아직 보지 않았어요. 원래 차례로 다시 판정해요.");
    }
    wiseGo("judge");
  }

  function updatePos() {
    if (!$("pos")) { return; }
    $("pos").textContent = (st.i + 1) + " / " + CARDS.length + " · 판정한 카드 " +
      countOf(st.round === 1 ? st.first : st.second) + "장";
  }

  function countOf(obj) {
    var n = 0;
    for (var k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function changedCount() {
    var n = 0;
    for (var k in st.second) {
      if (st.second.hasOwnProperty(k) && st.first[k] !== undefined && st.first[k] !== st.second[k]) { n++; }
    }
    return n;
  }

  function paintHud() {
    wiseHud([
      { label: "판정", done: countOf(st.first), total: CARDS.length },
      { label: "근거", done: countOf(st.why), total: CARDS.length },
      { label: "생각 바꾼 카드", done: changedCount(), total: CARDS.length }
    ]);
  }

  /* 글자를 칠 때마다 허브 전체를 다시 그리지 않는다. 숫자 한 칸만 고친다. */
  function paintHubQuiet() {
    if ($("s-cond")) { $("s-cond").textContent = "조건을 쓴 카드 " + countOf(st.cond) + "장"; }
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
    paintHub();
  }

  function paintHub() {
    if (!$("s-judge")) { return; }
    $("s-quiz").textContent = st.quiz >= QUIZ.length ? ("맞힌 문제 " + st.quizOk + " / " + QUIZ.length) : "세 문제로 몸풀기";
    $("s-judge").textContent = "판정한 카드 " + countOf(st.first) + " / " + CARDS.length;
    $("s-class").textContent = st.classDist ? "우리 반 분포를 보았어요" : "갈린 카드 찾기";
    $("s-again").textContent = countOf(st.second) ? ("다시 판정한 카드 " + countOf(st.second) + "장") : "생각이 바뀌었다면";
    $("s-cond").textContent = "조건을 쓴 카드 " + countOf(readCond()) + "장";
    $("s-card").textContent = "오늘의 내 기록";
    var tiles = [["t-judge", countOf(st.first) >= 10], ["t-quiz", st.quiz >= QUIZ.length],
      ["t-class", !!st.classDist], ["t-again", countOf(st.second) > 0],
      ["t-cond", countOf(readCond()) > 0], ["t-card", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }
    var names = [];
    for (var k in st.badges) { if (st.badges.hasOwnProperty(k)) { names.push(k); } }
    $("badges").innerHTML = names.length
      ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
      : '<span class="muted">아직 없어요. 판정을 해 보면 받을 수 있어요.</span>';

    if (countOf(st.first) >= 10) { award("판정단원"); }
    if (countOf(st.why) >= 10) { award("근거 왕"); }
    if (changedCount() >= 1) { award("생각을 바꾼 용기"); }
    if (countOf(st.cond) >= 3) { award("조건 작가"); }
    if (countOf(st.first) >= CARDS.length && !st.done20) {
      st.done20 = true;
      award("스무 장 완주");
      wiseCelebrate("스무 장을 다 판정했어요", [
        "이제 우리 반과 견줘 보고, 생각이 달라졌으면 2차 판정을 해 봐요."
      ], "좋아요");
    }
    paintHud();
  }

  /* ---------- 우리 반 분포 ---------- */

  function peek() {
    if (me.solo) {
      $("dist").innerHTML = '<p class="muted">혼자 체험 중에는 우리 반 분포가 없어요. ' +
        '판정과 조건 쓰기는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    $("dist").innerHTML = wiseSpinner("우리 반 판정을 모으는 중이에요", true) + wiseSkeleton(4);
    wiseButtonBusy($("peek"), true, "불러오는 중");
    dbGet(me.room + "/entries").then(function (data) {
      var tally = {};
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload || {};
        var f = p.second || p.first || {};
        for (var c in f) {
          if (!f.hasOwnProperty(c)) { continue; }
          if (!tally[c]) { tally[c] = [0, 0, 0, 0]; }
          tally[c][Number(f[c])] += 1;
        }
      }
      st.classDist = tally;
      wiseButtonBusy($("peek"), false);
      $("dist").innerHTML = distHtml(tally);
      $("dist").className = "fade-in";
      paintHub();
    })["catch"](function () {
      wiseButtonBusy($("peek"), false);
      $("dist").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function distHtml(tally) {
    var keys = [];
    for (var c in tally) { if (tally.hasOwnProperty(c)) { keys.push(c); } }
    if (!keys.length) { return '<p class="muted">아직 우리 반 판정이 모이지 않았어요.</p>'; }
    keys.sort(function (a, b) { return splitScore(tally[a]) - splitScore(tally[b]); });
    var h = '<div class="scroll"><table>' +
      '<tr><th>상황</th><th>초록</th><th>노랑</th><th>주황</th><th>빨강</th><th>나</th></tr>';
    for (var i = 0; i < keys.length && i < 8; i++) {
      var c2 = keys[i], t = tally[c2];
      var mineV = st.second[c2] !== undefined ? st.second[c2] : st.first[c2];
      var split = splitScore(t) < 0.6;
      h += "<tr><td>" + esc(CARDS[c2]) + (split ? ' <span class="warn">갈림</span>' : "") +
        "</td><td>" + t[0] + "</td><td>" + t[1] + "</td><td>" + t[2] + "</td><td>" + t[3] + "</td><td>" +
        (mineV === undefined ? "-" : esc(SIGNALS[mineV].name)) + "</td></tr>";
    }
    return h + "</table></div>";
  }

  function splitScore(arr) {
    var sum = arr[0] + arr[1] + arr[2] + arr[3];
    if (!sum) { return 1; }
    return Math.max(arr[0], arr[1], arr[2], arr[3]) / sum;
  }

  /* ---------- 조건 작성소 ---------- */

  function paintConds() {
    if (!$("conds")) { return; }
    stashCond();
    var cur = countOf(st.second) ? st.second : st.first;
    var h = "", n = 0;
    for (var i = 0; i < CARDS.length; i++) {
      var v = cur[i];
      if (v !== 1 && v !== 2) { continue; }
      n++;
      h += '<label for="cd' + i + '">' + esc(CARDS[i]) + ' · ' + esc(SIGNALS[v].name) + '</label>' +
        '<input id="cd' + i + '" maxlength="70" value="' + esc(st.cond[i] || "") +
        '" placeholder="예: 출처를 확인하고 내 말로 다시 쓴다면">';
    }
    if (!n) {
      h = '<p class="muted">노랑불이나 주황불로 판정한 카드가 아직 없어요. ' +
        '판정을 더 해 보면 여기에 칸이 생겨요.</p>';
    }
    $("conds").innerHTML = h;
    bindCond();
  }

  /* 화면을 다시 그리기 전에 쓴 조건을 상태로 옮긴다. 입력이 날아가지 않게 한다. */
  function stashCond() {
    for (var i = 0; i < CARDS.length; i++) {
      var el = $("cd" + i);
      if (el && typeof el.value === "string") {
        var v = el.value.trim();
        if (v) { st.cond[i] = v; }
        else if (el.parentNode && st.cond[i]) { delete st.cond[i]; }
      }
    }
  }

  function bindCond() {
    for (var i = 0; i < CARDS.length; i++) {
      var el = $("cd" + i);
      if (!el) { continue; }
      el.oninput = function () {
        stashCond();
        paintHubQuiet();
      };
    }
  }

  function readCond() {
    stashCond();
    return st.cond;
  }

  /* ---------- 판정단 카드 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var cur = countOf(st.second) ? st.second : st.first;
    var c = [0, 0, 0, 0], n = 0;
    for (var k in cur) {
      if (!cur.hasOwnProperty(k)) { continue; }
      c[cur[k]] += 1;
      n++;
    }
    if (!n) { $("mine").innerHTML = '<p class="muted">아직 판정한 카드가 없어요.</p>'; return; }
    var rows = [];
    for (var s = 0; s < 4; s++) {
      rows.push({ label: SIGNALS[s].name, value: c[s],
        color: ["#16a34a", "#eab308", "#ea580c", "#dc2626"][s] });
    }
    var h = wiseBars(rows, 560);
    h += '<p style="margin-top:10px">판정한 카드 ' + n + '장 · 근거를 고른 카드 ' + countOf(st.why) +
      '장 · 생각을 바꾼 카드 ' + changedCount() + '장</p>';
    if (changedCount()) {
      h += '<p class="ok">생각을 바꾼 것은 잘못이 아니에요. 근거가 더 좋아진 거예요.</p>';
    }
    $("mine").innerHTML = h;
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "quiz") { bindQuiz(); }
    if (id === "judge") {
      if ($("stage6")) { $("stage6").innerHTML = wiseSpinner("상황 카드를 꺼내는 중이에요") + wiseSkeleton(3); }
      softDelay(paint, 200);
    }
    if (id === "cond") { paintConds(); }
    if (id === "card") {
      if ($("mine")) { $("mine").innerHTML = wiseSpinner("오늘 기록을 모으는 중이에요") + wiseSkeleton(3); }
      softDelay(paintMine, 240);
    }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.first) { st.first = saved.first; }
      if (saved.second) { st.second = saved.second; }
      if (saved.why) { st.why = saved.why; }
      if (saved.cond) { st.cond = saved.cond; }
      if (saved.quizOk) { st.quizOk = saved.quizOk; }
      if (countOf(st.first) >= CARDS.length) { st.done20 = true; }
      if (countOf(st.first)) {
        wiseToast("지난번에 판정하던 것이 남아 있어요. 이어서 하면 돼요.");
      }
    }
    $("go-hub").onclick = function () {
      if (st.opened) { wiseGo("hub"); return; }
      st.opened = true;
      wiseBusy(true, "판정소 문을 여는 중");
      softDelay(function () { wiseBusy(false); wiseGo("hub"); }, 520);
    };
    $("t-quiz").onclick = function () { wiseGo("quiz"); };
    $("t-judge").onclick = function () {
      st.round = 1; st.i = 0; st.order = null;
      wiseNote("판정소를 돌아다니며 스무 장을 판정해요. 신호와 근거를 모두 고르면 다음 카드로 넘어가요.");
      wiseGo("judge");
    };
    $("t-class").onclick = function () { wiseGo("class"); };
    $("t-again").onclick = startRound2;
    $("t-cond").onclick = function () { wiseGo("cond"); };
    $("t-card").onclick = function () { wiseGo("card"); };
    $("prev").onclick = function () { if (st.i > 0) { st.i -= 1; paint(); } };
    $("next").onclick = function () { if (st.i < CARDS.length - 1) { st.i += 1; paint(); } };
    $("peek").onclick = peek;
    $("to-again").onclick = startRound2;
    $("save-card").onclick = function () {
      var btn = this;
      wiseButtonBusy(btn, true, "그림 만드는 중");
      var cur = countOf(st.second) ? st.second : st.first;
      var c = [0, 0, 0, 0];
      for (var k in cur) { if (cur.hasOwnProperty(k)) { c[cur[k]] += 1; } }
      wiseCardPng("AI 신호등 판정단 " + me.nick, [
        "초록불 " + c[0] + "장  노랑불 " + c[1] + "장",
        "주황불 " + c[2] + "장  빨간불 " + c[3] + "장",
        "근거를 고른 카드 " + countOf(st.why) + "장",
        "생각을 바꾼 카드 " + changedCount() + "장",
        "오늘 나는 까닭을 들어 판정했다."
      ], "wise_l06_" + me.nick);
      wiseButtonBusy(btn, false);
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }
    wiseNote("판정소를 돌아다니며 스무 장을 판정해요. 신호와 근거를 모두 고르면 다음 카드로 넘어가요.");
    wiseGo("story");
    paintHub();
    paintMine();
    paintConds();
  }

  function activityDraft() {
    return { first: st.first, second: st.second, why: st.why, cond: readCond(), quizOk: st.quizOk };
  }

  function activityAutofill() {
    for (var i = 0; i < 8; i++) {
      st.first[i] = i % 4;
      st.why[i] = i % 4;
    }
    st.second[0] = 3;
    st.cond[1] = "출처를 밝히고 내 말로 다시 쓴다면";
    st.cond[2] = "선생님께 먼저 말하고 쓴다면";
    paintConds();
    paintMine();
    paintHub();
  }

  function activityCollect() {
    var n1 = countOf(st.first);
    if (n1 < 5) {
      $("w-msg").innerHTML = '<span class="warn">상황 카드를 다섯 장 넘게 판정한 뒤에 제출해요. 지금 ' +
        n1 + '장이에요.</span>';
      return null;
    }
    var noWhy = 0;
    for (var k in st.first) {
      if (st.first.hasOwnProperty(k) && st.why[k] === undefined) { noWhy++; }
    }
    if (noWhy > n1 / 2) {
      $("w-msg").innerHTML = '<span class="warn">근거를 고르지 않은 판정이 ' + noWhy +
        '장이에요. 근거를 함께 골라 주세요.</span>';
      return null;
    }
    var badges = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { badges.push(b); } }
    wiseCelebrate("판정을 마쳤어요", [
      "판정한 카드 <b>" + n1 + "장</b>",
      "생각을 바꾼 카드 <b>" + changedCount() + "장</b>",
      "받은 배지 " + (badges.length ? badges.join(", ") : "없음"),
      "다음 시간에는 이 조건들을 모아 우리 반 약속을 만들어요."
    ], "좋아요");
    return {
      first: st.first, second: st.second, why: st.why, cond: readCond(),
      judged: n1, changed: changedCount(), quizOk: st.quizOk, badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function tally(list) {
    var rows = [];
    for (var i = 0; i < CARDS.length; i++) {
      var c = [0, 0, 0, 0], sum = 0;
      for (var k = 0; k < list.length; k++) {
        var p = list[k].payload || {};
        var f = (p.second && p.second[i] !== undefined) ? p.second : (p.first || {});
        if (f[i] === undefined) { continue; }
        c[Number(f[i])] += 1;
        sum++;
      }
      rows.push({ i: i, c: c, sum: sum, agree: sum ? splitScore(c) : 1 });
    }
    return rows;
  }

  function teacherSummary(list) {
    var rows = tally(list);
    var changed = 0, whyCount = [0, 0, 0, 0], conds = 0;
    for (var k = 0; k < list.length; k++) {
      var p = list[k].payload || {};
      changed += p.changed || 0;
      var w = p.why || {};
      for (var q2 in w) { if (w.hasOwnProperty(q2)) { whyCount[Number(w[q2])] += 1; } }
      var cd = p.cond || {};
      for (var c3 in cd) { if (cd.hasOwnProperty(c3) && cd[c3]) { conds++; } }
    }
    var h = '<p class="muted">2차 판정에서 생각을 바꾼 횟수 ' + changed + '회 · 학생이 쓴 조건 ' +
      conds + '개</p>';

    var reasonRows = [];
    for (var r = 0; r < REASONS.length; r++) {
      reasonRows.push({ label: REASONS[r].slice(0, 12), value: whyCount[r] });
    }
    h += wiseBars(reasonRows, 560);

    h += '<div class="scroll" style="margin-top:12px"><table><tr><th>상황</th><th>초록</th><th>노랑</th>' +
      '<th>주황</th><th>빨강</th><th>살펴볼 점</th></tr>';
    for (var i = 0; i < rows.length; i++) {
      if (!rows[i].sum) { continue; }
      h += "<tr><td>" + esc(CARDS[rows[i].i]) + "</td><td>" + rows[i].c[0] + "</td><td>" +
        rows[i].c[1] + "</td><td>" + rows[i].c[2] + "</td><td>" + rows[i].c[3] + "</td><td>" +
        (rows[i].agree < 0.6 ? '<span class="warn">의견 갈림</span>' : "") + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">학생이 쓴 조건</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>상황</th><th>조건</th></tr>';
    for (var m = 0; m < list.length; m++) {
      var cc = (list[m].payload || {}).cond || {};
      for (var key in cc) {
        if (!cc.hasOwnProperty(key) || !cc[key]) { continue; }
        h += "<tr><td>" + esc(list[m].nick) + "</td><td>" + esc(CARDS[key] || key) +
          "</td><td>" + esc(cc[key]) + "</td></tr>";
      }
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var rows = tally(list);
    rows.sort(function (a, b) { return a.agree - b.agree; });
    var h = '<p class="muted">의견이 가장 갈린 상황이에요. 근거를 들어 이야기해 봐요.</p>';
    for (var i = 0; i < rows.length && i < 3; i++) {
      var r = rows[i];
      if (!r.sum) { continue; }
      var bars = [];
      for (var s = 0; s < 4; s++) {
        bars.push({ label: SIGNALS[s].name, value: r.c[s],
          color: ["#16a34a", "#eab308", "#ea580c", "#dc2626"][s] });
      }
      h += '<div class="card"><p class="big">' + esc(CARDS[r.i]) + '</p>' +
        wiseBars(bars, 700) + '</div>';
    }
    return h;
  }
"""
