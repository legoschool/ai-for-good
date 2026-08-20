# -*- coding: utf-8 -*-
"""5차시 보조·대행 정비소.

여정형으로 다시 만들었다. 폼 하나가 아니라 화면 여덟 개를 지나간다.

  이야기 → 정비소 허브 → 몸풀기 → 판별대 12장
  → 우리 반과 견주기 → 정비 작업대(조건 붙이기) → 정비 수칙 → 점검원 카드

이 앱의 단 하나의 경험은 "대행을 보조로 고쳐 보는 것"이다.
두 축(생각을 누가 했나, 결과물을 누가 만들었나)으로 판정한 뒤,
경계와 대행으로 나온 장면에 조건 한 줄을 붙여 보조로 옮긴다.
그 조건 문장이 6·7차시 약속의 재료가 된다.

설계서는 spec/15_웹앱_설계_L05.md 다.
40분 : 이야기 2 + 몸풀기 3 + 판별 12 + 견주기 5 + 정비 8 + 수칙 5 + 정리 5
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  /* 인쇄 교구 「AI 활용 장면 카드 12장」과 글자까지 같다.
     make_webapp.py 의 SCENE_CARDS 를 고치면 여기도 같이 고친다. */
  var SCENES = [
    "독후감을 다 써 달라고 했다",
    "어려운 낱말의 뜻을 물었다",
    "수학 문제 푸는 방법을 물었다",
    "수학 숙제 답을 그대로 받아 적었다",
    "글을 다듬어 달라고 했다",
    "발표할 주제 아이디어를 여러 개 받았다",
    "일기를 대신 써 달라고 했다",
    "모르는 개념을 다시 설명해 달라고 했다",
    "그림을 대신 그려서 미술 숙제로 냈다",
    "포스터 배경 그림을 만들어 배치는 내가 했다",
    "친구에게 보낼 사과 편지를 통째로 만들었다",
    "조사한 내용이 맞는지 다시 확인해 달라고 했다"
  ];

  var AXIS = ["내가 했다", "반반이다", "AI가 했다"];
  var AXIS_ICON = ["me", "both", "ai"];

  var WHYS = [
    "내가 생각할 기회를 뺏기나",
    "마지막 결정을 누가 하나",
    "내가 배우는 데 도움이 되나",
    "결과를 내 것이라 말할 수 있나"
  ];

  var RULES = [
    "무엇을 쓸지 정하기",
    "사실인지 확인하기",
    "마지막 결정하기",
    "내 말로 다시 쓰기",
    "누구에게 보일지 정하기",
    "틀린 곳 고치기",
    "친구 마음을 살피기",
    "AI를 쓴 사실 밝히기"
  ];

  /* 몸풀기. 정답이 분명한 것만 넣는다. */
  var QUIZ = [
    {q:"자전거 보조바퀴는 보조일까요, 대행일까요?",
     opts:["보조예요", "대행이에요", "둘 다 아니에요"], ans:0,
     why:"보조예요. 페달은 내가 밟으니까요."},
    {q:"자전거를 대신 타 주는 사람은 어떤가요?",
     opts:["보조예요", "대행이에요", "더 빨리 배워요"], ans:1,
     why:"대행이에요. 나는 타는 법을 배우지 못해요."},
    {q:"보조와 대행을 가르는 것은 무엇일까요?",
     opts:["걸린 시간", "생각과 마지막 결정을 누가 했는가", "결과물이 얼마나 멋진가"], ans:1,
     why:"생각과 마지막 결정을 누가 했는지가 기준이에요."}
  ];

  var ZONES = [
    {name:"보조", say:"덜컹이가 내 생각을 도왔어요.", color:"#16a34a"},
    {name:"경계", say:"조건을 붙여야 보조가 돼요.", color:"#eab308"},
    {name:"대행", say:"덜컹이가 내 일을 대신했어요.", color:"#dc2626"}
  ];

  var st = {
    i: 0, think: {}, make: {}, why: {}, cond: {}, rules: [], line: "",
    quiz: 0, quizOk: 0, quizPick: -1, classDist: null, badges: {}, nudged: false
  };

  /* ---------- 도우미 ---------- */

  function trim(s) {
    return String(s).replace(/^[ ]+/, "").replace(/[ ]+$/, "");
  }

  /* 화면이 딱딱 넘어가지 않게 한다. 짧은 기다림과 스피너를 두고 넘어간다.
     조각은 골격 것을 쓴다. (wiseBusy · wiseSpinner · wiseSkeleton · .fade-in)
     움직임을 줄이는 설정이거나 브라우저가 아니면 곧바로 넘어간다. */
  function softMotion() {
    if (!window.matchMedia) { return false; }
    return !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function wait(text, ms, fn) {
    if (!softMotion()) { fn(); return; }
    wiseBusy(true, text || "잠시만요");
    setTimeout(function () {
      wiseBusy(false);
      fn();
    }, ms || 400);
  }

  function goSoft(id, text, ms) {
    wait(text, ms || 380, function () { wiseGo(id); });
  }

  function zoneOf(t, m) {
    var sum = Number(t) + Number(m);
    if (sum <= 1) { return 0; }
    if (sum <= 3) { return 1; }
    return 2;
  }

  function zoneOfScene(i) {
    if (st.think[i] === undefined || st.make[i] === undefined) { return -1; }
    return zoneOf(st.think[i], st.make[i]);
  }

  function countOf(obj) {
    var n = 0, k;
    for (k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function judged() {
    var n = 0;
    for (var i = 0; i < SCENES.length; i++) {
      if (zoneOfScene(i) >= 0) { n++; }
    }
    return n;
  }

  function readCond() {
    var out = {}, k;
    for (k in st.cond) {
      if (st.cond.hasOwnProperty(k) && trim(st.cond[k])) { out[k] = trim(st.cond[k]); }
    }
    for (var i = 0; i < SCENES.length; i++) {
      var el = $("cd" + i);
      if (el && el.value && trim(el.value)) { out[i] = trim(el.value); }
    }
    return out;
  }

  /* 조건을 붙여 보조로 옮긴 장면 수 */
  function fixedCount() {
    var c = readCond(), n = 0, k;
    for (k in c) {
      if (!c.hasOwnProperty(k)) { continue; }
      if (zoneOfScene(k) >= 1) { n++; }
    }
    return n;
  }

  /* 조건을 붙일 수 있는 장면 수. 경계와 대행만 해당한다. */
  function fixableCount() {
    var n = 0;
    for (var i = 0; i < SCENES.length; i++) {
      if (zoneOfScene(i) >= 1) { n++; }
    }
    return n;
  }

  function zoneTally() {
    var t = [0, 0, 0];
    for (var i = 0; i < SCENES.length; i++) {
      var z = zoneOfScene(i);
      if (z >= 0) { t[z] += 1; }
    }
    return t;
  }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">두바퀴 마을 정비소</h2>' +
      wiseScene("axis") +
      '<p style="margin-top:10px">보조바퀴를 달면 페달은 내가 밟아요. ' +
      '누가 대신 타 주면 나는 타는 법을 못 배워요.</p>' +
      '<p style="margin-top:8px">오늘 정비소에 AI 조수 로봇 <b>덜컹이</b>가 왔어요. ' +
      '덜컹이는 일을 잘하는데, 자기가 도와준 것인지 대신해 준 것인지 몰라요.</p>' +
      '<p style="margin-top:8px">여러분은 정비소 <b>점검원</b>이에요. ' +
      '장면 카드 열두 장을 판정하고, 대행이 된 장면은 조건을 붙여 보조로 고쳐 줘요.</p>' +
      '<p class="muted" style="margin-top:8px">정답은 미리 정해져 있지 않아요. ' +
      '까닭을 댈 수 있으면 그것이 우리 반의 기준이 돼요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">정비소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>정비소</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-quiz">' + wiseIcon("star", 30) +
      '<span>몸풀기</span><small id="s-quiz">세 문제로 감 잡기</small></button>' +
      '<button type="button" class="tile" id="t-judge">' + wiseIcon("check", 30) +
      '<span>판별대</span><small id="s-judge">장면 카드 12장</small></button>' +
      '<button type="button" class="tile" id="t-class">' + wiseIcon("talk", 30) +
      '<span>우리 반과 견주기</span><small id="s-class">갈린 장면 찾기</small></button>' +
      '<button type="button" class="tile" id="t-fix">' + wiseIcon("write", 30) +
      '<span>정비 작업대</span><small id="s-fix">조건을 붙여 보조로</small></button>' +
      '<button type="button" class="tile" id="t-rule">' + wiseIcon("again", 30) +
      '<span>정비 수칙</span><small id="s-rule">사람이 꼭 할 일 3가지</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("id", 30) +
      '<span>점검원 카드</span><small id="s-card">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3>' +
      '<div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("quiz",
      '<div class="card"><span class="pill">몸풀기</span>' +
      '<h2 style="margin-top:10px">보조바퀴 시험</h2>' +
      '<div id="quizbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("judge",
      '<div class="card"><span class="pill">판별대</span>' +
      '<h2 style="margin-top:10px">장면을 두 축으로 판정해요</h2>' +
      '<p class="muted">칸 하나만 고르는 대신 생각과 결과물을 나누어 봐요. ' +
      '같은 장면도 어디까지 내가 했는지에 따라 달라져요.</p>' +
      '<div id="stage5"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="prev" class="plain">앞 장면</button>' +
      '<button type="button" id="next" class="ghost">다음 장면</button>' +
      '<span class="muted" id="pos"></span></div>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("class",
      '<div class="card"><span class="pill">함께 보기</span>' +
      '<h2 style="margin-top:10px">우리 반은 어떻게 보았을까</h2>' +
      '<p class="muted">의견이 갈린 장면부터 보여 줘요. 다른 생각을 들어 보고 판정을 바꿔도 돼요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="peek">우리 반 분포 불러오기</button>' +
      '<button type="button" id="to-fix" class="ghost">정비 작업대로</button></div>' +
      '<div id="dist" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("fix",
      '<div class="card"><span class="pill">작업대</span>' +
      '<h2 style="margin-top:10px">조건을 붙여 보조로 옮겨요</h2>' +
      '<p class="muted">경계와 대행으로 판정한 장면이 여기로 올라와요. ' +
      '"이렇게 하면 보조가 돼요"를 한 줄로 써요.</p>' +
      '<div id="fixhud" class="note"></div>' +
      '<div id="fixlist" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("rule",
      '<div class="card"><span class="pill">수칙</span>' +
      '<h2 style="margin-top:10px">사람이 꼭 할 일 3가지</h2>' +
      '<p class="muted">어떤 경우에도 사람이 해야 하는 일을 세 가지 골라요.</p>' +
      '<div id="rulelist" style="margin-top:10px"></div>' +
      '<div id="rulebox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">나의 점검원 카드</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>');

    return h;
  }

  /* ---------- 몸풀기 ---------- */

  function quizHtml() {
    if (st.quiz >= QUIZ.length) {
      return '<p class="big">' + st.quizOk + ' / ' + QUIZ.length + '</p>' +
        '<p class="muted">몸풀기 끝. 이제 진짜 판정을 해 봐요.</p>' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" id="quiz-go">판별대로 가기</button></div>';
    }
    var item = QUIZ[st.quiz];
    var h = '<p class="muted">' + (st.quiz + 1) + ' / ' + QUIZ.length + '</p>' +
      '<h3 style="margin:8px 0 12px">' + esc(item.q) + '</h3>';
    for (var i = 0; i < item.opts.length; i++) {
      var on = (st.quizPick >= 0 && i === item.ans) ? " on" : "";
      h += '<button type="button" class="chip qz' + on + '" data-o="' + i + '">' +
        esc(item.opts[i]) + '</button>';
    }
    if (st.quizPick >= 0) {
      h += '<p class="' + (st.quizPick === item.ans ? "ok" : "warn") + '" style="margin-top:10px">' +
        (st.quizPick === item.ans ? "맞았어요. " : "다시 봐요. ") + esc(item.why) + '</p>' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" id="quiz-next">다음</button></div>';
    }
    return h;
  }

  function bindQuiz() {
    if (!$("quizbox")) { return; }
    $("quizbox").innerHTML = '<div class="fade-in">' + quizHtml() + '</div>';
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
      $("quiz-next").onclick = function () {
        wait("다음 문제를 꺼내는 중", 320, function () {
          st.quiz += 1; st.quizPick = -1; bindQuiz(); paintHub();
        });
      };
    }
    if ($("quiz-go")) {
      $("quiz-go").onclick = function () {
        if (st.quizOk === QUIZ.length) { award("몸풀기 만점"); }
        goSoft("judge", "장면 카드를 꺼내는 중");
      };
    }
  }

  /* ---------- 판별대 ---------- */

  function sceneHtml(i) {
    var h = '<div class="card fade-in" style="margin:12px 0 0">' +
      '<h3 style="font-size:21px">' + esc(SCENES[i]) + '</h3>' +
      '<label>생각은 누가 했나요</label>';
    for (var a = 0; a < AXIS.length; a++) {
      h += '<button type="button" class="chip pick" data-c="' + i + '" data-b="' + a + '">' +
        wiseIcon(AXIS_ICON[a], 26) + esc(AXIS[a]) + '</button>';
    }
    h += '<label>결과물은 누가 만들었나요</label>';
    for (var b = 0; b < AXIS.length; b++) {
      h += '<button type="button" class="chip mk" data-c="' + i + '" data-m="' + b + '">' +
        wiseIcon(AXIS_ICON[b], 26) + esc(AXIS[b]) + '</button>';
    }
    h += '<p id="verdict" class="note" style="margin-top:12px"></p>';
    h += '<label>왜 그렇게 보았나요</label>';
    for (var r = 0; r < WHYS.length; r++) {
      h += '<button type="button" class="chip why" data-c="' + i + '" data-r="' + r + '">' +
        esc(WHYS[r]) + '</button>';
    }
    h += '</div>';
    return h;
  }

  function bindScene() {
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      picks[i].onclick = function () {
        st.think[this.getAttribute("data-c")] = this.getAttribute("data-b");
        afterJudge();
      };
    }
    var mks = document.querySelectorAll("#activity .mk");
    for (var j = 0; j < mks.length; j++) {
      mks[j].onclick = function () {
        st.make[this.getAttribute("data-c")] = this.getAttribute("data-m");
        afterJudge();
      };
    }
    var whys = document.querySelectorAll("#activity .why");
    for (var k = 0; k < whys.length; k++) {
      whys[k].onclick = function () {
        var c = this.getAttribute("data-c");
        st.why[c] = Number(this.getAttribute("data-r"));
        afterJudge();
        if (zoneOfScene(c) >= 0 && st.i < SCENES.length - 1) {
          wait("다음 장면을 가져오는 중", 460, function () { st.i += 1; paintScene(); });
        }
      };
    }
    mark();
  }

  function afterJudge() {
    mark();
    paintHub();
    paintFix();
    paintMine();
  }

  function mark() {
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      var c = picks[i].getAttribute("data-c"), b = picks[i].getAttribute("data-b");
      picks[i].className = "chip pick" + (st.think[c] === b ? " on" : "");
    }
    var mks = document.querySelectorAll("#activity .mk");
    for (var j = 0; j < mks.length; j++) {
      var c2 = mks[j].getAttribute("data-c"), m = mks[j].getAttribute("data-m");
      mks[j].className = "chip mk" + (st.make[c2] === m ? " on" : "");
    }
    var whys = document.querySelectorAll("#activity .why");
    for (var k = 0; k < whys.length; k++) {
      var c3 = whys[k].getAttribute("data-c"), r = Number(whys[k].getAttribute("data-r"));
      whys[k].className = "chip why" + (st.why[c3] === r ? " on" : "");
    }
    if ($("verdict")) {
      var z = zoneOfScene(st.i);
      if (z >= 0) {
        $("verdict").innerHTML = '<span class="pill">' + esc(ZONES[z].name) + '</span> ' +
          esc(ZONES[z].say);
      } else {
        $("verdict").textContent = "두 축을 모두 골라야 덜컹이가 답해요.";
      }
    }
  }

  function paintScene() {
    if ($("stage5")) { $("stage5").innerHTML = sceneHtml(st.i); bindScene(); }
    if ($("pos")) {
      $("pos").textContent = (st.i + 1) + " / " + SCENES.length + " · 판정한 장면 " +
        judged() + "장";
    }
    paintHud();
  }

  function paintHud() {
    wiseHud([
      { label: "판정", done: judged(), total: SCENES.length },
      { label: "근거", done: countOf(st.why), total: SCENES.length },
      { label: "보조로 옮김", done: fixedCount(), total: fixableCount() }
    ]);
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
    if (!$("s-judge")) { return; }
    $("s-quiz").textContent = st.quiz >= QUIZ.length
      ? ("맞힌 문제 " + st.quizOk + " / " + QUIZ.length) : "세 문제로 감 잡기";
    $("s-judge").textContent = "판정한 장면 " + judged() + " / " + SCENES.length;
    $("s-class").textContent = st.classDist ? "우리 반 분포를 보았어요" : "갈린 장면 찾기";
    $("s-fix").textContent = "보조로 옮긴 장면 " + fixedCount() + "장";
    $("s-rule").textContent = st.rules.length
      ? ("고른 수칙 " + st.rules.length + " / 3") : "사람이 꼭 할 일 3가지";
    $("s-card").textContent = "오늘의 내 기록";

    var tiles = [
      ["t-quiz", st.quiz >= QUIZ.length],
      ["t-judge", judged() >= 6],
      ["t-class", !!st.classDist],
      ["t-fix", fixedCount() > 0],
      ["t-rule", st.rules.length >= 3],
      ["t-card", false]
    ];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if (judged() >= 6) { award("판별사"); }
    if (countOf(st.why) >= 6) { award("근거왕"); }
    if (fixedCount() >= 3) { award("정비사"); }
    if (st.rules.length >= 3) { award("수칙 세움"); }

    var names = badgeList();
    if ($("badges")) {
      if (names.length) {
        var h = "";
        for (var b = 0; b < names.length; b++) {
          h += '<span class="pill">' + esc(names[b]) + '</span> ';
        }
        $("badges").innerHTML = h;
      } else {
        $("badges").innerHTML = '<span class="muted">아직 없어요. 판정을 해 보면 받을 수 있어요.</span>';
      }
    }
    paintHud();
  }

  /* ---------- 우리 반과 견주기 ---------- */

  function peek() {
    if (!$("dist")) { return; }
    if (me.solo) {
      $("dist").innerHTML = '<p class="muted">혼자 체험 중에는 우리 반 분포가 없어요. ' +
        '판정과 조건 쓰기는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    $("dist").innerHTML = wiseSpinner("우리 반 판정을 모으는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      var tallyMap = {}, k;
      for (k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload || {};
        var th = p.think || {}, mk = p.make || {}, c;
        for (c in th) {
          if (!th.hasOwnProperty(c) || mk[c] === undefined) { continue; }
          if (!tallyMap[c]) { tallyMap[c] = [0, 0, 0]; }
          tallyMap[c][zoneOf(th[c], mk[c])] += 1;
        }
      }
      st.classDist = tallyMap;
      $("dist").innerHTML = distHtml(tallyMap);
      paintHub();
    })["catch"](function () {
      $("dist").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function agreeScore(arr) {
    var sum = arr[0] + arr[1] + arr[2];
    if (!sum) { return 1; }
    return Math.max(arr[0], arr[1], arr[2]) / sum;
  }

  function distHtml(tallyMap) {
    var keys = [], c;
    for (c in tallyMap) { if (tallyMap.hasOwnProperty(c)) { keys.push(c); } }
    if (!keys.length) {
      return '<p class="muted">아직 우리 반 판정이 모이지 않았어요. 잠시 뒤 다시 눌러요.</p>';
    }
    keys.sort(function (a, b) { return agreeScore(tallyMap[a]) - agreeScore(tallyMap[b]); });
    var h = '<div class="scroll"><table>' +
      '<tr><th>장면</th><th>보조</th><th>경계</th><th>대행</th><th>나</th></tr>';
    for (var i = 0; i < keys.length && i < 8; i++) {
      var k = keys[i], t = tallyMap[k], mineZ = zoneOfScene(k);
      var split = agreeScore(t) < 0.6;
      h += "<tr><td>" + esc(SCENES[k] || k) +
        (split ? ' <span class="warn">갈림</span>' : "") + "</td><td>" +
        t[0] + "</td><td>" + t[1] + "</td><td>" + t[2] + "</td><td>" +
        (mineZ < 0 ? "-" : esc(ZONES[mineZ].name)) + "</td></tr>";
    }
    return h + "</table></div>";
  }

  /* ---------- 정비 작업대 ---------- */

  function fixNote(total) {
    if (!$("fixhud")) { return; }
    $("fixhud").textContent = "고칠 장면 " + total + "장 가운데 " + fixedCount() +
      "장을 보조로 옮겼어요.";
  }

  function paintFix() {
    if (!$("fixlist")) { return; }
    var cond = readCond();
    var h = "", n = 0;
    for (var i = 0; i < SCENES.length; i++) {
      var z = zoneOfScene(i);
      if (z < 1) { continue; }
      n++;
      var val = cond[i] ? cond[i] : "";
      h += '<label for="cd' + i + '">' + esc(SCENES[i]) + ' · ' + esc(ZONES[z].name) +
        (val ? ' <span class="ok">보조로 옮김</span>' : "") + '</label>' +
        '<input id="cd' + i + '" class="cdin" data-i="' + i + '" maxlength="70" value="' +
        esc(val) + '" placeholder="예: 내가 먼저 쓰고 다듬기만 맡긴다면">';
    }
    if (!n) {
      h = '<p class="muted">경계나 대행으로 판정한 장면이 아직 없어요. ' +
        '판별대에서 장면을 더 판정해 봐요.</p>';
    }
    $("fixlist").innerHTML = h;
    fixNote(n);
    var ins = document.querySelectorAll("#activity .cdin");
    for (var k = 0; k < ins.length; k++) {
      ins[k].oninput = function () {
        st.cond[this.getAttribute("data-i")] = this.value;
        fixNote(n);
        paintHud();
      };
    }
  }

  /* ---------- 정비 수칙 ---------- */

  function hasRule(i) {
    for (var k = 0; k < st.rules.length; k++) {
      if (st.rules[k] === i) { return true; }
    }
    return false;
  }

  function paintRules() {
    if (!$("rulelist")) { return; }
    var h = "";
    for (var i = 0; i < RULES.length; i++) {
      h += '<button type="button" class="chip rl' + (hasRule(i) ? " on" : "") +
        '" data-i="' + i + '">' + esc(RULES[i]) + '</button>';
    }
    $("rulelist").innerHTML = h;
    var els = document.querySelectorAll("#activity .rl");
    for (var k = 0; k < els.length; k++) {
      els[k].onclick = function () {
        var v = Number(this.getAttribute("data-i"));
        if (hasRule(v)) {
          var next = [];
          for (var m = 0; m < st.rules.length; m++) {
            if (st.rules[m] !== v) { next.push(st.rules[m]); }
          }
          st.rules = next;
        } else if (st.rules.length >= 3) {
          wiseToast("세 가지까지 고를 수 있어요. 하나를 빼고 골라요.");
          return;
        } else {
          st.rules.push(v);
        }
        paintRules();
        paintHub();
      };
    }
    paintRuleBox();
  }

  function paintRuleBox() {
    if (!$("rulebox")) { return; }
    if (st.rules.length >= 3) {
      $("rulebox").innerHTML = '<label for="learn">한 줄로 정리해요</label>' +
        '<input id="learn" maxlength="60" value="' + esc(st.line || "") +
        '" placeholder="예: AI에게 맡겨도 마지막 결정은 내가 한다">' +
        '<p class="muted" style="margin-top:8px">이 문장은 활동지 4번 칸에 그대로 옮겨 적어요.</p>';
      if ($("learn")) {
        $("learn").oninput = function () { st.line = this.value; };
      }
    } else {
      $("rulebox").innerHTML = '<p class="muted" style="margin-top:10px">세 가지를 고르면 ' +
        '한 줄 쓰기 칸이 열려요. 지금 ' + st.rules.length + '가지를 골랐어요.</p>';
    }
  }

  function readLine() {
    if ($("learn") && $("learn").value) { return trim($("learn").value); }
    return st.line ? trim(st.line) : "";
  }

  /* ---------- 점검원 카드 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var t = zoneTally(), n = judged();
    if (!n) {
      $("mine").innerHTML = '<p class="muted">아직 판정한 장면이 없어요. 판별대부터 가 봐요.</p>';
      return;
    }
    var rows = [];
    for (var z = 0; z < 3; z++) {
      rows.push({ label: ZONES[z].name, value: t[z], color: ZONES[z].color });
    }
    var h = wiseBars(rows, 560);
    h += '<p style="margin-top:10px">판정한 장면 ' + n + '장 · 근거를 고른 장면 ' +
      countOf(st.why) + '장 · 조건을 붙여 보조로 옮긴 장면 ' + fixedCount() + '장</p>';
    if (fixedCount()) {
      h += '<p class="ok">대행도 조건을 붙이면 보조가 돼요. 그 조건이 우리 반 약속의 재료예요.</p>';
    }
    if (st.rules.length >= 3) {
      var names = [];
      for (var r = 0; r < st.rules.length; r++) { names.push(RULES[st.rules[r]]); }
      h += '<p style="margin-top:8px">내가 세운 수칙 : ' + esc(names.join(", ")) + '</p>';
    }
    $("mine").innerHTML = h;
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "quiz") { bindQuiz(); }
    if (id === "judge") { paintScene(); }
    if (id === "class") { paintHub(); }
    if (id === "fix") { paintFix(); }
    if (id === "rule") { paintRules(); }
    if (id === "card") { paintMine(); }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.think) { st.think = saved.think; }
      if (saved.make) { st.make = saved.make; }
      if (saved.why) { st.why = saved.why; }
      if (saved.cond) { st.cond = saved.cond; }
      if (saved.rules) { st.rules = saved.rules; }
      if (saved.line) { st.line = saved.line; }
    }
    $("go-hub").onclick = function () { goSoft("hub", "정비소 문을 여는 중", 520); };
    $("t-quiz").onclick = function () { goSoft("quiz", "몸풀기 문제를 꺼내는 중"); };
    $("t-judge").onclick = function () { goSoft("judge", "장면 카드를 꺼내는 중"); };
    $("t-class").onclick = function () { goSoft("class", "우리 반 자리를 펴는 중"); };
    $("t-fix").onclick = function () { goSoft("fix", "작업대를 여는 중"); };
    $("t-rule").onclick = function () { goSoft("rule", "수칙 판을 여는 중"); };
    $("t-card").onclick = function () { goSoft("card", "점검원 카드를 만드는 중"); };
    $("prev").onclick = function () { if (st.i > 0) { st.i -= 1; paintScene(); } };
    $("next").onclick = function () { if (st.i < SCENES.length - 1) { st.i += 1; paintScene(); } };
    $("peek").onclick = peek;
    $("to-fix").onclick = function () { goSoft("fix", "작업대를 여는 중"); };
    $("save-card").onclick = function () {
      var t = zoneTally();
      wiseCardPng("보조·대행 점검원 " + me.nick, [
        "보조 " + t[0] + "장  경계 " + t[1] + "장  대행 " + t[2] + "장",
        "조건을 붙여 보조로 옮긴 장면 " + fixedCount() + "장",
        "근거를 고른 장면 " + countOf(st.why) + "장",
        readLine() ? readLine() : "오늘 나는 도움과 대신함을 갈라 보았다."
      ], "wise_l05_" + me.nick);
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { goSoft("hub", "정비소로 돌아가는 중", 300); };
    }
    wiseNote("장면을 판정하고, 대행이 된 장면에 조건을 붙여 보조로 고쳐 줘요.");
    wiseGo("story");
    paintHub();
    paintRules();
    paintFix();
    paintMine();
  }

  function activityDraft() {
    return { think: st.think, make: st.make, why: st.why, cond: readCond(),
      rules: st.rules, line: readLine() };
  }

  function activityAutofill() {
    var demo = [
      [2, 2], [0, 0], [1, 0], [2, 2], [1, 1], [1, 0],
      [2, 2], [0, 0], [2, 2], [0, 1]
    ];
    for (var i = 0; i < demo.length; i++) {
      st.think[i] = String(demo[i][0]);
      st.make[i] = String(demo[i][1]);
      st.why[i] = i % WHYS.length;
    }
    st.cond[0] = "내가 먼저 쓰고 다듬기만 맡긴다면";
    st.cond[4] = "내 주장과 근거를 내가 쓴 뒤라면";
    st.rules = [0, 1, 2];
    st.line = "AI에게 맡겨도 마지막 결정은 내가 한다";
  }

  function activityCollect() {
    var n = judged();
    if (n < 5) {
      $("w-msg").innerHTML = '<span class="warn">장면을 다섯 장 넘게 판정한 뒤에 제출해요. 지금 ' +
        n + '장이에요.</span>';
      goSoft("judge", "판별대로 데려가는 중");
      return null;
    }
    var noWhy = 0;
    for (var i = 0; i < SCENES.length; i++) {
      if (zoneOfScene(i) >= 0 && st.why[i] === undefined) { noWhy++; }
    }
    if (noWhy > n / 2) {
      $("w-msg").innerHTML = '<span class="warn">근거를 고르지 않은 장면이 ' + noWhy +
        '장이에요. 근거를 함께 골라 주세요.</span>';
      goSoft("judge", "판별대로 데려가는 중");
      return null;
    }
    /* 이 차시의 핵심은 대행을 보조로 고쳐 보는 것이다.
       고칠 장면이 있는데 하나도 고치지 않았으면 한 번만 데려가서 권한다. 막지는 않는다. */
    if (!st.nudged && fixableCount() > 0 && fixedCount() === 0) {
      st.nudged = true;
      $("w-msg").innerHTML = '<span class="warn">경계와 대행으로 놓은 장면이 ' + fixableCount() +
        '장 있어요. 조건을 한 줄 붙여 보조로 옮겨 보고 다시 제출해요. ' +
        '그래도 괜찮으면 한 번 더 누르면 돼요.</span>';
      goSoft("fix", "작업대를 여는 중");
      return null;
    }

    if (st.rules.length < 3) {
      $("w-msg").innerHTML = '<span class="warn">정비 수칙에서 사람이 꼭 할 일 세 가지를 ' +
        '고른 뒤에 제출해요. 지금 ' + st.rules.length + '가지예요.</span>';
      goSoft("rule", "수칙 판을 여는 중");
      return null;
    }
    var t = zoneTally();
    var names = [];
    for (var r = 0; r < st.rules.length; r++) { names.push(RULES[st.rules[r]]); }
    wiseCelebrate("점검을 마쳤어요", [
      "판정한 장면 <b>" + n + "장</b>",
      "조건을 붙여 보조로 옮긴 장면 <b>" + fixedCount() + "장</b>",
      "내가 세운 수칙 " + esc(names.join(", ")),
      "다음 시간에는 네 가지 신호로 더 자세히 나눠 봐요."
    ], "좋아요");
    return {
      think: st.think, make: st.make, why: st.why, cond: readCond(),
      rules: st.rules, line: readLine(), zones: t, judged: n,
      fixed: fixedCount(), quizOk: st.quizOk, badges: badgeList()
    };
  }

  /* ---------- 교사 화면 ---------- */

  function tally(list) {
    var rows = [];
    for (var i = 0; i < SCENES.length; i++) {
      var c = [0, 0, 0], sum = 0;
      for (var k = 0; k < list.length; k++) {
        var p = list[k].payload || {};
        var th = p.think || {}, mk = p.make || {};
        if (th[i] === undefined || mk[i] === undefined) { continue; }
        c[zoneOf(th[i], mk[i])] += 1;
        sum++;
      }
      rows.push({ i: i, c: c, sum: sum, agree: sum ? agreeScore(c) : 1 });
    }
    return rows;
  }

  function teacherSummary(list) {
    var rows = tally(list);
    var fixed = 0, ruled = 0, whyCount = [0, 0, 0, 0], ruleCount = [];
    for (var r0 = 0; r0 < RULES.length; r0++) { ruleCount.push(0); }
    for (var k = 0; k < list.length; k++) {
      var p = list[k].payload || {};
      fixed += p.fixed || 0;
      if (p.rules && p.rules.length >= 3) { ruled++; }
      var w = p.why || {}, key;
      for (key in w) {
        if (w.hasOwnProperty(key) && whyCount[Number(w[key])] !== undefined) {
          whyCount[Number(w[key])] += 1;
        }
      }
      var rs = p.rules || [];
      for (var m = 0; m < rs.length; m++) {
        if (ruleCount[Number(rs[m])] !== undefined) { ruleCount[Number(rs[m])] += 1; }
      }
    }
    var h = '<p class="muted">제출 ' + list.length + '명 · 조건을 붙여 보조로 옮긴 장면 ' +
      fixed + '장 · 수칙 세 가지를 세운 학생 ' + ruled + '명</p>';

    var whyRows = [];
    for (var a = 0; a < WHYS.length; a++) {
      whyRows.push({ label: WHYS[a].slice(0, 12), value: whyCount[a] });
    }
    h += '<h3 style="margin-top:14px">고른 근거</h3>' + wiseBars(whyRows, 560);

    h += '<h3 style="margin-top:16px">장면별 판정</h3>' +
      '<div class="scroll"><table><tr><th>장면</th><th>보조</th><th>경계</th><th>대행</th>' +
      '<th>살펴볼 점</th></tr>';
    var shown = 0;
    for (var i = 0; i < rows.length; i++) {
      if (!rows[i].sum) { continue; }
      shown++;
      h += "<tr><td>" + esc(SCENES[rows[i].i]) + "</td><td>" + rows[i].c[0] + "</td><td>" +
        rows[i].c[1] + "</td><td>" + rows[i].c[2] + "</td><td>" +
        (rows[i].agree < 0.6 ? '<span class="warn">의견 갈림</span>' : "") + "</td></tr>";
    }
    if (!shown) {
      h += '<tr><td colspan="5">아직 판정이 모이지 않았어요.</td></tr>';
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">사람이 꼭 할 일</h3><div class="scroll"><table>' +
      '<tr><th>수칙</th><th>고른 학생</th></tr>';
    for (var b = 0; b < RULES.length; b++) {
      h += "<tr><td>" + esc(RULES[b]) + "</td><td>" + ruleCount[b] + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">학생이 쓴 조건</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>장면</th><th>조건</th></tr>';
    var lines = 0;
    for (var c = 0; c < list.length; c++) {
      var cc = (list[c].payload || {}).cond || {}, ck;
      for (ck in cc) {
        if (!cc.hasOwnProperty(ck) || !cc[ck]) { continue; }
        lines++;
        h += "<tr><td>" + esc(list[c].nick) + "</td><td>" + esc(SCENES[ck] || ck) +
          "</td><td>" + esc(cc[ck]) + "</td></tr>";
      }
    }
    if (!lines) {
      h += '<tr><td colspan="3">아직 조건 문장이 없어요.</td></tr>';
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var rows = tally(list);
    rows.sort(function (a, b) { return a.agree - b.agree; });
    var h = '<p class="muted">의견이 가장 갈린 장면이에요. 까닭을 들어 보고 조건을 붙여 봐요.</p>';
    var shown = 0;
    for (var i = 0; i < rows.length && shown < 3; i++) {
      if (!rows[i].sum) { continue; }
      shown++;
      var bars = [];
      for (var z = 0; z < 3; z++) {
        bars.push({ label: ZONES[z].name, value: rows[i].c[z], color: ZONES[z].color });
      }
      h += '<div class="card"><p class="big">' + esc(SCENES[rows[i].i]) + '</p>' +
        wiseBars(bars, 700) + '</div>';
    }
    if (!shown) {
      h += '<p class="big">아직 판정이 모이지 않았어요.</p>';
    }
    h += '<h3 style="margin-top:18px">대행을 보조로 바꾼 조건</h3>';
    var said = 0;
    for (var k = 0; k < list.length && said < 5; k++) {
      var cc = (list[k].payload || {}).cond || {}, ck;
      for (ck in cc) {
        if (!cc.hasOwnProperty(ck) || !cc[ck] || said >= 5) { continue; }
        said++;
        h += '<p style="font-size:22px;margin:8px 0">' + esc(cc[ck]) + '</p>';
      }
    }
    if (!said) {
      h += '<p class="muted">조건 문장이 모이면 여기에 크게 띄워요.</p>';
    }
    return h;
  }
"""
