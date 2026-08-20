# -*- coding: utf-8 -*-
"""4차시 정보 분류 카드 : 정보 지킴이 본부.

여정형으로 만든다. 폼 하나가 아니라 화면 아홉 개를 지나간다.

  이야기 → 본부 허브 → 훈련장 → 분류실 24장 → 열람실(되돌리기 상자)
  → 조건 작성소 → 우리 반과 견주기 → 수칙 회의실 → 지킴이 카드

분류실에서는 정답을 보여 주지 않는다. 감으로 나눈 뒤 열람실에서 카드가 열린다.
빨간 카드를 초록문으로 보냈으면 되돌리기 상자에 담기고, 상자는 열리지 않는다.
한 번 넘어간 정보는 돌아오지 않는다는 것을 말이 아니라 화면으로 겪게 한다.

설계서 : spec/13_웹앱_설계_L04.md
40분 : 이야기 2 + 훈련장 4 + 분류실 12 + 열람실 8 + 조건 4 + 견주기 4 + 수칙 5 + 카드 1
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */
  /* r 은 숨은 위험도다. 0 초록문 · 1 노랑문 · 2 빨간문.
     학생에게 미리 보여 주지 않는다. 열람실에서만 펼친다. */

  var KINDS = { id: "나를 알아보는 것", loc: "있는 곳", rel: "다른 사람",
    rec: "기록으로 남는 것", pub: "이미 알려진 것" };

  var DOORS = [
    { name: "초록문", say: "넣어도 돼", icon: "green" },
    { name: "노랑문", say: "조건을 지키면 돼", icon: "yellow" },
    { name: "빨간문", say: "넣으면 안 돼", icon: "red" }
  ];

  var CARDS = [
    {t:"내 이름", k:"id", r:2, w:"이름 하나만으로도 다른 정보와 붙으면 나를 찾아낼 수 있어요."},
    {t:"내 사진", k:"id", r:2, w:"얼굴은 바꿀 수 없는 정보예요. 한 번 퍼지면 되돌리기 어려워요."},
    {t:"집 주소", k:"loc", r:2, w:"사는 곳은 나를 직접 찾아올 수 있게 하는 정보예요."},
    {t:"부모님 전화번호", k:"id", r:2, w:"가족의 정보는 내가 마음대로 넘길 수 있는 것이 아니에요."},
    {t:"내 아이디와 비밀번호", k:"id", r:2, w:"비밀번호는 어떤 서비스에도 그대로 넣지 않아요."},
    {t:"친구 사진", k:"rel", r:2, w:"다른 사람의 정보는 그 친구의 허락 없이는 쓸 수 없어요."},
    {t:"친구와 다툰 이야기", k:"rel", r:2, w:"친구 이야기는 내 이야기가 아니에요. 이름을 지워도 알아볼 수 있어요."},
    {t:"친구 이름", k:"rel", r:2, w:"내 친구의 이름을 넣을지 정하는 사람은 내가 아니라 친구예요."},
    {t:"우리 반 단체 사진", k:"rel", r:2, w:"여러 사람이 함께 찍힌 사진은 모두의 허락이 필요해요."},
    {t:"내 성적", k:"rec", r:2, w:"성적은 나에 대한 평가 기록이에요. 남기면 오래 따라다녀요."},
    {t:"몸무게와 키", k:"id", r:2, w:"몸에 대한 정보는 민감해요. 놀림거리가 될 수 있어요."},
    {t:"학교 이름", k:"loc", r:1, w:"학교만으로는 어렵지만 학년, 이름과 붙으면 나를 찾을 수 있어요."},
    {t:"학원 이름", k:"loc", r:1, w:"몇 시에 어디 있는지가 드러나요. 시간과 함께 쓰지 않아요."},
    {t:"우리 반 시간표", k:"loc", r:1, w:"언제 어디 있는지 알려 주는 정보가 될 수 있어요."},
    {t:"내 생일", k:"id", r:1, w:"생일은 비밀번호 찾기 질문에 자주 쓰여요. 연도까지는 넣지 않아요."},
    {t:"내가 쓴 글", k:"rec", r:1, w:"내 글은 내 것이지만, 어디에 쓰이는지 확인하고 넣어요."},
    {t:"내가 그린 그림", k:"rec", r:1, w:"내 작품도 학습에 쓰일 수 있어요. 표기하고 쓰는 습관을 들여요."},
    {t:"가족 이야기", k:"rel", r:1, w:"가족도 다른 사람이에요. 이름과 사연을 함께 넣지 않아요."},
    {t:"우리 학교 위치", k:"loc", r:1, w:"이미 알려진 정보라도 나와 묶이면 위치가 되니 조심해요."},
    {t:"모르는 낱말", k:"pub", r:0, w:"누구의 것도 아닌 정보예요. 마음껏 물어봐도 돼요."},
    {t:"교과서에 나온 문제", k:"pub", r:0, w:"공개된 학습 자료예요. 풀이 과정을 물어보면 좋아요."},
    {t:"오늘 급식 메뉴", k:"pub", r:0, w:"누구나 아는 정보예요. 위험하지 않아요."},
    {t:"좋아하는 가수", k:"pub", r:0, w:"취향은 나를 특정하지 않아요. 다만 너무 자세히 쓰지는 않아요."},
    {t:"내가 읽은 책 제목", k:"pub", r:0, w:"책 제목은 공개된 정보예요. 추천을 받아 보아도 좋아요."}
  ];

  var SURE = ["확실해요", "헷갈려요"];

  var WHYS = ["나를 찾아낼 수 있어서", "다른 사람의 것이라서", "기록이 남아서", "되돌릴 수 없어서"];

  /* 훈련장. 판단 활동의 준비 운동이다. 답이 분명한 것만 넣는다. */
  var QUIZ = [
    {q:"나를 알아볼 수 있게 하는 정보는 무엇일까요?",
     opts:["오늘 급식 메뉴", "내 이름과 사진", "교과서에 나온 문제"], ans:1,
     why:"이름과 사진은 나를 바로 찾아낼 수 있게 해요."},
    {q:"친구 이야기를 AI에 넣을지 정하는 사람은 누구일까요?",
     opts:["나", "그 친구", "AI"], ans:1,
     why:"다른 사람의 정보는 그 사람의 것이에요. 내가 정할 수 없어요."},
    {q:"한 번 넣은 정보는 내가 지울 수 있을까요?",
     opts:["언제든 지울 수 있어요", "지우기 어려울 때가 많아요", "하루 뒤에 저절로 사라져요"], ans:1,
     why:"넣은 정보는 어딘가에 남을 수 있어요. 그래서 넣기 전에 생각해요."}
  ];

  /* 수칙 보기. 전부 조건형이다. 금지 목록으로 쓰지 않는다. */
  var RULES = [
    "이름 대신 별명을 쓴다",
    "친구 이야기는 넣지 않는다",
    "사진은 올리지 않고 글로 설명한다",
    "넣기 전에 한 번 더 읽어 본다",
    "헷갈리면 선생님께 여쭤본다",
    "비밀번호는 어디에도 넣지 않는다",
    "학교와 학원 이름은 지우고 물어본다",
    "AI가 준 답은 내 말로 다시 쓴다"
  ];

  var st = {
    i: 0, choice: {}, sure: {}, why: {}, again: {}, rules: {},
    condCache: {}, ruleCache: {},
    quiz: 0, quizOk: 0, quizPick: -1, classDist: null, badges: {}, opened: false
  };

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  /* 화면을 딱딱 갈아 끼우지 않는다. 무엇을 하는 중인지 잠깐 보여 준 뒤 넘어간다.
     움직임을 줄이는 설정이면 기다리지 않고 바로 넘어간다. */
  function reducedMotion() {
    try {
      return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) { return false; }
  }

  function goSlow(id, text, ms) {
    if (reducedMotion()) { wiseGo(id); return; }
    wiseBusy(true, text || "여는 중이에요");
    setTimeout(function () {
      wiseBusy(false);
      wiseGo(id);
    }, ms || 520);
  }

  function doorCard(b) {
    return '<div class="card" style="margin:0"><div class="iconrow">' + wiseIcon(DOORS[b].icon, 34) +
      '<b>' + esc(DOORS[b].name) + '</b></div>' +
      '<p class="muted" style="margin-top:6px">' + esc(DOORS[b].say) + '</p></div>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">정보 지킴이 본부</h2>' +
      '<p style="margin-top:10px">본부에는 문이 세 개 있어요. 문 너머는 AI 나라예요.</p>' +
      '<div class="g2" style="margin-top:12px">' + doorCard(0) + doorCard(1) + doorCard(2) + '</div>' +
      '<p style="margin-top:12px">오늘 여러분은 <b>새싹 지킴이</b>예요. ' +
      '정보 카드 스물네 장을 어느 문으로 보낼지 정해요.</p>' +
      '<p class="muted" style="margin-top:8px">한 가지만 기억해요. ' +
      '문을 넘어간 정보는 본부도 다시 데려오지 못해요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">본부로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>정보 지킴이 본부</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-train">' + wiseIcon("star", 30) +
      '<span>훈련장</span><small id="s-train">세 문제로 몸풀기</small></button>' +
      '<button type="button" class="tile" id="t-sort">' + wiseIcon("check", 30) +
      '<span>분류실</span><small id="s-sort">정보 카드 24장</small></button>' +
      '<button type="button" class="tile" id="t-open">' + wiseIcon("rec", 30) +
      '<span>열람실</span><small id="s-open">카드를 열어 봐요</small></button>' +
      '<button type="button" class="tile" id="t-cond">' + wiseIcon("write", 30) +
      '<span>조건 작성소</span><small id="s-cond">노랑문 카드에 조건 달기</small></button>' +
      '<button type="button" class="tile" id="t-class">' + wiseIcon("talk", 30) +
      '<span>우리 반과 견주기</span><small id="s-class">갈린 카드 찾기</small></button>' +
      '<button type="button" class="tile" id="t-rule">' + wiseIcon("heart", 30) +
      '<span>수칙 회의실</span><small id="s-rule">지킴이 수칙 5개</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("id", 30) +
      '<span>지킴이 카드</span><small id="s-card">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("train",
      '<div class="card"><span class="pill">몸풀기</span>' +
      '<h2 style="margin-top:10px">훈련장</h2>' +
      '<div id="quizbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">본부로</button></div></div>');

    h += q("sort",
      '<div class="card"><span class="pill">분류실</span>' +
      '<h2 style="margin-top:10px">이 정보를 어느 문으로 보낼까요</h2>' +
      '<p class="muted">고르고 나서 얼마나 확신하는지도 눌러요. 정답은 아직 알려 주지 않아요.</p>' +
      '<div id="deck"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="prev" class="plain">앞 카드</button>' +
      '<button type="button" id="next" class="ghost">다음 카드</button>' +
      '<span class="muted" id="pos"></span></div>' +
      '<div style="margin-top:12px" id="sortbar"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-open" class="ghost">열람실로 가기</button>' +
      '<button type="button" class="plain back">본부로</button></div>' +
      '<div class="safe">카드에 적힌 것만 골라요. 진짜 내 정보나 친구 정보를 쓰는 칸은 없어요.</div></div>');

    h += q("open",
      '<div class="card"><span class="pill">열람실</span>' +
      '<h2 style="margin-top:10px">카드를 열어 봐요</h2>' +
      '<div id="report"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="back-sort" class="ghost">분류실로 돌아가기</button>' +
      '<button type="button" class="plain back">본부로</button></div></div>');

    h += q("cond",
      '<div class="card"><span class="pill">작성소</span>' +
      '<h2 style="margin-top:10px">조건을 한 줄씩 써요</h2>' +
      '<p class="muted">어떤 조건이면 넣어도 되는지를 써요. 금지가 아니라 조건이 우리의 기준이에요.</p>' +
      '<div id="condbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">본부로</button></div>' +
      '<div class="safe">조건을 쓸 때에도 진짜 이름이나 사진 이야기는 넣지 않아요.</div></div>');

    h += q("class",
      '<div class="card"><span class="pill">함께 보기</span>' +
      '<h2 style="margin-top:10px">우리 반은 어떻게 보았을까</h2>' +
      '<p class="muted">의견이 갈린 카드부터 보여 줘요. 다른 생각을 들어 보고 다시 판단해도 돼요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="peek">우리 반 분포 불러오기</button></div>' +
      '<div id="dist" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" class="plain back">본부로</button></div></div>');

    h += q("rule",
      '<div class="card"><span class="pill">회의실</span>' +
      '<h2 style="margin-top:10px">개인정보 지킴이 수칙 5개</h2>' +
      '<p class="muted">보기에서 골라도 되고, 우리 모둠 말로 써도 돼요. 다섯 개를 채우면 회의가 끝나요.</p>' +
      '<div id="rulebox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">본부로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">나의 지킴이 카드</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">본부로</button></div></div>');

    return h;
  }

  /* ---------- 훈련장 ---------- */

  function quizHtml() {
    if (st.quiz >= QUIZ.length) {
      return '<p class="big">' + st.quizOk + ' / ' + QUIZ.length + '</p>' +
        '<p class="muted">몸풀기 끝. 이제 분류실로 가요.</p>' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" id="quiz-go">분류실로 가기</button></div>';
    }
    var item = QUIZ[st.quiz];
    var h = '<p class="muted">' + (st.quiz + 1) + ' / ' + QUIZ.length + '</p>' +
      '<h3 style="margin:8px 0 12px">' + esc(item.q) + '</h3>';
    for (var i = 0; i < item.opts.length; i++) {
      var mark = (st.quizPick >= 0 && i === item.ans) ? " on" : "";
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
    if (!$("quizbox")) { return; }
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
      $("quiz-next").onclick = function () {
        st.quiz += 1;
        st.quizPick = -1;
        bindQuiz();
        paintHub();
      };
    }
    if ($("quiz-go")) {
      $("quiz-go").onclick = function () {
        if (st.quizOk === QUIZ.length) { award("훈련 통과"); }
        goSlow("sort", "분류실 문을 여는 중이에요");
      };
    }
  }

  /* ---------- 분류실 ---------- */

  function cardHtml(i) {
    var c = CARDS[i];
    var h = '<div class="card fade-in" style="margin:12px 0 0"><span class="tag">' + esc(KINDS[c.k]) + '</span>' +
      '<div class="iconrow" style="margin-top:10px">' + wiseIcon(c.k, 44) +
      '<h3 style="font-size:22px">' + esc(c.t) + '</h3></div>' +
      '<label>어느 문으로 보낼까요</label>';
    for (var b = 0; b < DOORS.length; b++) {
      h += '<button type="button" class="chip pick" data-c="' + i + '" data-b="' + b + '">' +
        wiseIcon(DOORS[b].icon, 26) + esc(DOORS[b].name) + ' · ' + esc(DOORS[b].say) + '</button>';
    }
    h += '<label>얼마나 확신하나요</label><div class="row">';
    for (var s = 0; s < SURE.length; s++) {
      h += '<button type="button" class="chip sure" data-c="' + i + '" data-s="' + s +
        '" style="width:auto;margin:0">' + esc(SURE[s]) + '</button>';
    }
    h += '</div>';
    if (st.again[i]) {
      h += '<p class="ok" style="margin-top:10px">열람실에서 생각을 바꾼 카드예요.</p>';
    }
    h += '</div>';
    return h;
  }

  function paintDeck() {
    if ($("deck")) { $("deck").innerHTML = cardHtml(st.i); bindCard(); }
    paintProgress();
  }

  /* 카드를 다시 그리지 않고 숫자와 막대만 고친다. 고른 즉시 반응하게 한다. */
  function paintProgress() {
    if ($("pos")) {
      $("pos").textContent = (st.i + 1) + " / " + CARDS.length + " · 나눈 카드 " + count(st.choice) + "장";
    }
    if ($("sortbar")) { $("sortbar").innerHTML = barHtml(count(st.choice), CARDS.length); }
    paintHud();
  }

  function count(obj) {
    var n = 0;
    for (var k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function bindCard() {
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      picks[i].onclick = function () {
        var c = this.getAttribute("data-c");
        st.choice[c] = this.getAttribute("data-b");
        markCard();
        paintProgress();
        paintHub();
        if (st.sure[c] !== undefined) { stepNext(c); }
      };
    }
    var sures = document.querySelectorAll("#activity .sure");
    for (var j = 0; j < sures.length; j++) {
      sures[j].onclick = function () {
        var c2 = this.getAttribute("data-c");
        st.sure[c2] = this.getAttribute("data-s");
        markCard();
        paintProgress();
        paintHub();
        if (st.choice[c2] !== undefined) { stepNext(c2); }
      };
    }
    markCard();
  }

  /* 문과 확신도를 둘 다 누른 카드에서만 다음 장으로 넘어간다. */
  function stepNext(c) {
    if (Number(c) !== st.i) { return; }
    if (st.i >= CARDS.length - 1) {
      paintProgress();
      wiseToast("마지막 카드예요. 열람실에서 카드를 열어 봐요.");
      return;
    }
    if (st.stepping) { return; }
    st.stepping = true;
    /* 고른 표시를 눈으로 확인할 틈을 준 뒤 다음 카드로 넘긴다. */
    setTimeout(function () {
      st.stepping = false;
      if (st.i < CARDS.length - 1) { st.i += 1; }
      paintDeck();
    }, reducedMotion() ? 0 : 340);
  }

  function markCard() {
    var picks = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < picks.length; i++) {
      var c = picks[i].getAttribute("data-c"), b = picks[i].getAttribute("data-b");
      picks[i].className = "chip pick" + (st.choice[c] === b ? " on" : "");
    }
    var sures = document.querySelectorAll("#activity .sure");
    for (var j = 0; j < sures.length; j++) {
      var c2 = sures[j].getAttribute("data-c"), s = sures[j].getAttribute("data-s");
      sures[j].className = "chip sure" + (st.sure[c2] === s ? " on" : "");
    }
  }

  function paintHud() {
    var items = [{ label: "카드", done: count(st.choice), total: CARDS.length }];
    /* 까닭 칸은 열람실을 연 뒤에만 띄운다. 열기 전에는 셀 것이 없다. */
    var needWhy = leakList().length;
    if (st.opened && needWhy) {
      items.push({ label: "까닭", done: whyDone(), total: needWhy });
    }
    items.push({ label: "수칙", done: readRules().length, total: 5 });
    wiseHud(items);
  }

  /* ---------- 열람실 ---------- */

  function score() {
    var hit = 0, judged = 0, kind = {};
    for (var i = 0; i < CARDS.length; i++) {
      var v = st.choice[i];
      if (v === undefined) { continue; }
      judged++;
      if (!kind[CARDS[i].k]) { kind[CARDS[i].k] = { n: 0, hit: 0 }; }
      kind[CARDS[i].k].n += 1;
      if (Number(v) === CARDS[i].r) {
        hit++;
        kind[CARDS[i].k].hit += 1;
      }
    }
    return { hit: hit, judged: judged, kind: kind };
  }

  /* 되돌리기 상자에 담기는 카드. 기준은 빨간문인데 다른 문으로 보낸 것이다. */
  function leakList() {
    var out = [];
    for (var i = 0; i < CARDS.length; i++) {
      var v = st.choice[i];
      if (v === undefined) { continue; }
      if (CARDS[i].r === 2 && Number(v) < 2) { out.push(i); }
    }
    return out;
  }

  /* 기준과 달랐던 나머지 카드. 되돌리기 상자에 담긴 것은 빼고 센다. */
  function missList() {
    var out = [];
    for (var i = 0; i < CARDS.length; i++) {
      var v = st.choice[i];
      if (v === undefined) { continue; }
      if (Number(v) === CARDS[i].r) { continue; }
      if (CARDS[i].r === 2 && Number(v) < 2) { continue; }
      out.push(i);
    }
    return out;
  }

  /* 까닭을 골라야 하는 카드 전부. 되돌리기 상자와 한 번 더 볼 카드를 합친다. */
  function openList() {
    return leakList().concat(missList());
  }

  function whyDone() {
    var list = openList(), n = 0;
    for (var i = 0; i < list.length; i++) {
      if (st.why[list[i]] !== undefined) { n++; }
    }
    return n;
  }

  function whyBlock(i) {
    var h = '<p class="muted" style="margin-top:8px">왜 조심해야 할까요</p>';
    for (var r = 0; r < WHYS.length; r++) {
      h += '<button type="button" class="chip whyc' + (Number(st.why[i]) === r ? " on" : "") +
        '" data-c="' + i + '" data-r="' + r + '">' + esc(WHYS[r]) + '</button>';
    }
    if (st.why[i] !== undefined) {
      h += '<p style="margin-top:8px">' + esc(CARDS[i].w) + '</p>';
    }
    return h;
  }

  function cardLine(i) {
    return '<p class="muted">나는 ' + esc(DOORS[Number(st.choice[i])].name) + ' · 기준은 ' +
      esc(DOORS[CARDS[i].r].name) + '</p>';
  }

  function openCardHtml(i) {
    return '<div class="card" style="margin:10px 0 0"><span class="tag">' + esc(KINDS[CARDS[i].k]) +
      '</span><h3 style="margin-top:8px">' + esc(CARDS[i].t) + '</h3>' + cardLine(i) + whyBlock(i) +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" class="chip redo" data-c="' + i + '" style="width:auto;margin:0">' +
      (st.again[i] ? "생각을 바꿨어요" : "생각을 바꿀래요") + '</button></div></div>';
  }

  function reportHtml() {
    var s = score();
    if (s.judged < 4) {
      return '<p class="muted">분류실에서 카드를 네 장 넘게 나눈 뒤에 열려요. ' +
        '지금 ' + s.judged + '장이에요.</p>';
    }
    st.opened = true;
    var leaks = leakList(), miss = missList();

    var h = '<p class="big">' + s.hit + ' / ' + s.judged + '</p>' +
      '<p class="muted">기준과 같게 보낸 카드예요. 이 숫자는 내가 조심하는 정도를 보는 눈금이에요. ' +
      '사람의 등급이 아니에요.</p>' + barHtml(s.hit, s.judged);

    h += '<div class="card" style="margin-top:16px;border-color:#dc2626">' +
      '<div class="iconrow">' + wiseIcon("red", 32) + '<h3>되돌리기 상자</h3></div>';
    if (!leaks.length) {
      h += '<p class="ok" style="margin-top:8px">상자가 비어 있어요. 빨간문 카드를 모두 막아 냈어요.</p>';
    } else {
      h += '<p style="margin-top:8px">빨간문 카드 <b>' + leaks.length + '장</b>이 다른 문으로 넘어갔어요. ' +
        '상자는 열리지 않아요. 이미 넘어간 정보는 돌아오지 않아요.</p>';
      for (var m = 0; m < leaks.length; m++) {
        h += openCardHtml(leaks[m]);
      }
    }
    h += '</div>';

    if (miss.length) {
      h += '<h3 style="margin-top:16px">한 번 더 볼 카드</h3>';
      for (var p = 0; p < miss.length && p < 6; p++) {
        h += openCardHtml(miss[p]);
      }
      if (miss.length > 6) {
        h += '<p class="muted" style="margin-top:8px">여섯 장만 먼저 펼쳤어요. ' +
          '고치고 나면 다음 카드가 이어서 나와요. 남은 카드 ' + (miss.length - 6) + '장.</p>';
      }
    }

    h += '<h3 style="margin-top:16px">유형별로 보면</h3><div class="scroll"><table>' +
      '<tr><th>유형</th><th>나눈 카드</th><th>기준과 같음</th></tr>';
    for (var k in s.kind) {
      if (!s.kind.hasOwnProperty(k)) { continue; }
      h += "<tr><td>" + esc(KINDS[k]) + "</td><td>" + s.kind[k].n + "</td><td>" +
        s.kind[k].hit + "</td></tr>";
    }
    h += "</table></div>";
    return h;
  }

  function paintReport() {
    if (!$("report")) { return; }
    $("report").innerHTML = reportHtml();
    if ($("report").className.indexOf("fade-in") < 0) { $("report").className = "fade-in"; }
    var whys = document.querySelectorAll("#activity .whyc");
    for (var i = 0; i < whys.length; i++) {
      whys[i].onclick = function () {
        st.why[this.getAttribute("data-c")] = Number(this.getAttribute("data-r"));
        paintReport();
        paintHub();
      };
    }
    var redos = document.querySelectorAll("#activity .redo");
    for (var j = 0; j < redos.length; j++) {
      redos[j].onclick = function () {
        var c = this.getAttribute("data-c");
        st.again[c] = true;
        st.choice[c] = String(CARDS[c].r);
        wiseToast("생각을 바꾼 카드로 남겼어요.");
        paintReport();
        paintCond();
        paintHub();
      };
    }
    paintHud();
  }

  /* ---------- 조건 작성소 ---------- */

  function cacheCond() {
    for (var i = 0; i < CARDS.length; i++) {
      var el = $("cd" + i);
      if (el && el.value && el.value.trim()) { st.condCache[i] = el.value.trim(); }
    }
  }

  function paintCond() {
    if (!$("condbox")) { return; }
    cacheCond();
    var h = "", n = 0;
    for (var i = 0; i < CARDS.length; i++) {
      if (st.choice[i] !== "1") { continue; }
      n++;
      h += '<label for="cd' + i + '">' + esc(CARDS[i].t) + '</label>' +
        '<input id="cd' + i + '" maxlength="60" placeholder="예: 이름을 지우고 상황만 쓴다면">';
    }
    if (!n) {
      h = '<p class="muted">노랑문으로 보낸 카드가 아직 없어요. 분류실에서 카드를 더 나눠 보아요.</p>';
    }
    h += '<p class="note" id="condhint">조건은 "무엇을 하면 되는가"로 써요.</p>';
    $("condbox").innerHTML = h;
    for (var j = 0; j < CARDS.length; j++) {
      if ($("cd" + j) && st.condCache[j]) { $("cd" + j).value = st.condCache[j]; }
      if ($("cd" + j)) {
        $("cd" + j).oninput = function () {
          cacheCond();
          hintCond();
          paintHub();
        };
      }
    }
    hintCond();
  }

  /* 금지형으로 쓴 조건을 조건형으로 바꾸도록 돕는다. 고쳐 쓰라고만 하고 막지 않는다. */
  var BANWORDS = ["하지 마", "하지마", "안 돼", "안돼", "금지", "쓰지 마", "쓰지마"];

  function hintCond() {
    if (!$("condhint")) { return; }
    var found = "";
    for (var i = 0; i < CARDS.length; i++) {
      var v = st.condCache[i];
      if (!v) { continue; }
      for (var b = 0; b < BANWORDS.length; b++) {
        if (v.indexOf(BANWORDS[b]) >= 0) { found = BANWORDS[b]; break; }
      }
      if (found) { break; }
    }
    $("condhint").innerHTML = found
      ? ('"' + esc(found) + '" 처럼 막는 말이 보여요. ' +
         '"어떤 조건이면 되는가" 로 바꾸어 써 볼까요. 예: 이름을 지우고 상황만 쓴다면')
      : '조건은 "무엇을 하면 되는가" 로 써요.';
  }

  /* 화면에 없는 칸도 값을 잃지 않게 캐시와 합쳐서 돌려준다. */
  function readCond() {
    cacheCond();
    var out = {};
    for (var k in st.condCache) {
      if (!st.condCache.hasOwnProperty(k)) { continue; }
      if (st.choice[k] !== "1") { continue; }
      if (st.condCache[k]) { out[k] = st.condCache[k]; }
    }
    return out;
  }

  /* ---------- 수칙 회의실 ---------- */

  function ruleHtml() {
    var h = '<p class="muted">보기에서 고르면 눌린 표시가 생겨요.</p>';
    for (var i = 0; i < RULES.length; i++) {
      h += '<button type="button" class="chip rl' + (st.rules[i] ? " on" : "") +
        '" data-r="' + i + '">' + esc(RULES[i]) + '</button>';
    }
    h += '<label for="rx0">우리 모둠 말로 쓰기 1</label>' +
      '<input id="rx0" maxlength="40" placeholder="예: 넣기 전에 짝과 한 번 확인한다">' +
      '<label for="rx1">우리 모둠 말로 쓰기 2</label>' +
      '<input id="rx1" maxlength="40" placeholder="예: 헷갈리면 노랑문으로 보낸다">' +
      '<p class="note" id="rulecount"></p>';
    return h;
  }

  function cacheRules() {
    for (var j = 0; j < 2; j++) {
      var el = $("rx" + j);
      if (!el) { continue; }
      var v = el.value ? el.value.trim() : "";
      if (v) { st.ruleCache["rx" + j] = v; } else if (el.value === "") { st.ruleCache["rx" + j] = ""; }
    }
  }

  function readRules() {
    cacheRules();
    var out = [];
    for (var i = 0; i < RULES.length; i++) {
      if (st.rules[i]) { out.push(RULES[i]); }
    }
    for (var j = 0; j < 2; j++) {
      var v = st.ruleCache["rx" + j];
      if (v) { out.push(v); }
    }
    return out;
  }

  function paintRules() {
    if (!$("rulebox")) { return; }
    $("rulebox").innerHTML = ruleHtml();
    for (var j = 0; j < 2; j++) {
      if ($("rx" + j) && st.ruleCache["rx" + j]) { $("rx" + j).value = st.ruleCache["rx" + j]; }
    }
    var chips = document.querySelectorAll("#activity .rl");
    for (var i = 0; i < chips.length; i++) {
      chips[i].onclick = function () {
        var r = this.getAttribute("data-r");
        if (st.rules[r]) {
          st.rules[r] = false;
        } else if (readRules().length >= 5) {
          wiseToast("수칙은 다섯 개까지예요. 바꾸려면 고른 것을 눌러 빼요.");
          return;
        } else {
          st.rules[r] = true;
        }
        paintRules();
        paintHub();
      };
    }
    for (var k = 0; k < 2; k++) {
      var box = $("rx" + k);
      if (box) {
        box.oninput = function () {
          countRules();
          paintHub();
        };
      }
    }
    countRules();
  }

  function countRules() {
    if (!$("rulecount")) { return; }
    var n = readRules().length;
    $("rulecount").innerHTML = n >= 5
      ? "다섯 개를 채웠어요. 회의 끝."
      : ("지금 " + n + "개예요. 다섯 개를 채워 봐요.");
    if (n >= 5) { award("수칙 다섯"); }
  }

  /* ---------- 우리 반과 견주기 ---------- */

  function peek() {
    if (!$("dist")) { return; }
    if (me.solo) {
      $("dist").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 분포가 없어요. ' +
        '카드 나누기와 수칙 정하기는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    wiseButtonBusy($("peek"), true, "불러오는 중");
    $("dist").innerHTML = wiseSpinner("우리 반 기록을 모으는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      var tallyMap = {};
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var ch = (data[k].payload || {}).choice || {};
        for (var c in ch) {
          if (!ch.hasOwnProperty(c)) { continue; }
          if (!tallyMap[c]) { tallyMap[c] = [0, 0, 0]; }
          tallyMap[c][Number(ch[c])] += 1;
        }
      }
      st.classDist = tallyMap;
      wiseButtonBusy($("peek"), false);
      $("dist").innerHTML = distHtml(tallyMap);
      paintHub();
    })["catch"](function () {
      wiseButtonBusy($("peek"), false);
      $("dist").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function agreeOf(arr) {
    var sum = arr[0] + arr[1] + arr[2];
    if (!sum) { return 1; }
    return Math.max(arr[0], arr[1], arr[2]) / sum;
  }

  function distHtml(tallyMap) {
    var keys = [];
    for (var c in tallyMap) { if (tallyMap.hasOwnProperty(c)) { keys.push(c); } }
    if (!keys.length) { return '<p class="muted">아직 우리 반 기록이 모이지 않았어요.</p>'; }
    keys.sort(function (a, b) { return agreeOf(tallyMap[a]) - agreeOf(tallyMap[b]); });
    var h = '<div class="scroll"><table><tr><th>정보 카드</th><th>초록문</th><th>노랑문</th>' +
      '<th>빨간문</th><th>나</th></tr>';
    for (var i = 0; i < keys.length && i < 8; i++) {
      var c2 = keys[i], t = tallyMap[c2];
      if (!CARDS[c2]) { continue; }
      var mineV = st.choice[c2];
      h += "<tr><td>" + esc(CARDS[c2].t) +
        (agreeOf(t) < 0.7 ? ' <span class="warn">갈림</span>' : "") + "</td><td>" +
        t[0] + "</td><td>" + t[1] + "</td><td>" + t[2] + "</td><td>" +
        (mineV === undefined ? "-" : esc(DOORS[Number(mineV)].name)) + "</td></tr>";
    }
    return h + "</table></div>";
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
  }

  function badgeNames() {
    var out = [];
    for (var k in st.badges) { if (st.badges.hasOwnProperty(k)) { out.push(k); } }
    return out;
  }

  function paintHub() {
    if (!$("s-sort")) { return; }
    var judged = count(st.choice);
    var rules = readRules().length;
    var conds = count(readCond());
    $("s-train").textContent = st.quiz >= QUIZ.length
      ? ("맞힌 문제 " + st.quizOk + " / " + QUIZ.length) : "세 문제로 몸풀기";
    $("s-sort").textContent = "나눈 카드 " + judged + " / " + CARDS.length;
    $("s-open").textContent = st.opened
      ? ("되돌리기 상자 " + leakList().length + "장") : "카드를 열어 봐요";
    $("s-cond").textContent = "조건을 쓴 카드 " + conds + "장";
    $("s-class").textContent = st.classDist ? "우리 반 분포를 보았어요" : "갈린 카드 찾기";
    $("s-rule").textContent = "정한 수칙 " + rules + " / 5";
    $("s-card").textContent = "오늘의 내 기록";

    var tiles = [["t-train", st.quiz >= QUIZ.length], ["t-sort", judged >= CARDS.length],
      ["t-open", st.opened], ["t-cond", conds > 0],
      ["t-class", !!st.classDist], ["t-rule", rules >= 5], ["t-card", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if (judged >= CARDS.length) { award("카드 24장"); }
    if (whyDone() >= 3) { award("까닭 대기"); }
    if (count(st.again) >= 1) { award("생각을 바꾼 용기"); }

    var names = badgeNames();
    if ($("badges")) {
      $("badges").innerHTML = names.length
        ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
        : '<span class="muted">아직 없어요. 훈련장부터 해 보면 받을 수 있어요.</span>';
    }
    paintHud();
  }

  /* ---------- 지킴이 카드 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var s = score();
    if (!s.judged) {
      $("mine").innerHTML = '<p class="muted">아직 나눈 카드가 없어요. 분류실부터 가 볼까요.</p>';
      return;
    }
    var c = [0, 0, 0];
    for (var k in st.choice) {
      if (st.choice.hasOwnProperty(k)) { c[Number(st.choice[k])] += 1; }
    }
    var rows = [
      { label: DOORS[0].name, value: c[0], color: "#16a34a" },
      { label: DOORS[1].name, value: c[1], color: "#eab308" },
      { label: DOORS[2].name, value: c[2], color: "#dc2626" }
    ];
    var h = wiseBars(rows, 560);
    h += '<p style="margin-top:10px">나눈 카드 ' + s.judged + '장 · 기준과 같음 ' + s.hit +
      '장 · 되돌리기 상자 ' + leakList().length + '장 · 생각을 바꾼 카드 ' + count(st.again) + '장</p>';
    var rules = readRules();
    if (rules.length) {
      h += '<h3 style="margin-top:14px">내가 정한 수칙</h3><ul style="margin:8px 0 0 18px">';
      for (var i = 0; i < rules.length; i++) { h += "<li>" + esc(rules[i]) + "</li>"; }
      h += "</ul>";
    }
    var names = badgeNames();
    h += '<p style="margin-top:12px">받은 배지 : ' + (names.length ? esc(names.join(", ")) : "아직 없어요") + '</p>';
    h += '<div class="note" style="margin-top:12px">다음 시간부터는 AI를 언제 어디까지 쓸지 우리가 정해요.</div>';
    $("mine").innerHTML = h;
  }

  /* ---------- 흐름 ---------- */

  function hintFor(id) {
    if (id === "sort") { return "문을 고르고 확신도까지 누르면 다음 카드로 넘어가요."; }
    if (id === "open") { return "기준과 달랐던 카드를 보고, 왜 조심해야 하는지 까닭을 골라요."; }
    if (id === "cond") { return "금지가 아니라 조건을 쓰는 것이 우리 반의 방식이에요."; }
    if (id === "rule") { return "다섯 개를 채우면 회의가 끝나요."; }
    if (id === "class") { return "우리 반과 견주어 보고 생각이 바뀌면 열람실에서 바꿔요."; }
    return "본부에서 하고 싶은 곳을 골라요.";
  }

  function activityEnter(id) {
    if (id === "train") { bindQuiz(); }
    if (id === "sort") { paintDeck(); }
    if (id === "open") { paintReport(); }
    if (id === "cond") { paintCond(); }
    if (id === "rule") { paintRules(); }
    if (id === "card") { paintMine(); }
    if (id === "hub") { paintHub(); }
    wiseNote(hintFor(id));
  }

  function openGate() {
    if (count(st.choice) < 4) {
      wiseToast("카드를 네 장 넘게 나눈 뒤에 열려요.");
      return;
    }
    goSlow("open", "카드를 여는 중이에요", 600);
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.choice) { st.choice = saved.choice; }
      if (saved.sure) { st.sure = saved.sure; }
      if (saved.why) { st.why = saved.why; }
      if (saved.cond) { st.condCache = saved.cond; }
      if (saved.rulePick) { st.rules = saved.rulePick; }
      if (saved.ruleText) { st.ruleCache = saved.ruleText; }
    }

    $("go-hub").onclick = function () { goSlow("hub", "본부 문을 여는 중이에요", 560); };
    $("t-train").onclick = function () { goSlow("train", "훈련장으로 가는 중이에요"); };
    $("t-sort").onclick = function () { goSlow("sort", "분류실 문을 여는 중이에요"); };
    $("t-open").onclick = openGate;
    $("t-cond").onclick = function () { goSlow("cond", "작성소로 가는 중이에요"); };
    $("t-class").onclick = function () { goSlow("class", "우리 반 기록을 찾는 중이에요"); };
    $("t-rule").onclick = function () { goSlow("rule", "회의실로 가는 중이에요"); };
    $("t-card").onclick = function () { goSlow("card", "지킴이 카드를 그리는 중이에요"); };

    $("prev").onclick = function () { if (st.i > 0) { st.i -= 1; paintDeck(); } };
    $("next").onclick = function () { if (st.i < CARDS.length - 1) { st.i += 1; paintDeck(); } };
    $("to-open").onclick = openGate;
    $("back-sort").onclick = function () { goSlow("sort", "분류실로 돌아가는 중이에요"); };
    $("peek").onclick = peek;
    $("save-card").onclick = saveCard;

    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { goSlow("hub", "본부로 돌아가는 중이에요", 420); };
    }

    wiseGo("story");
    paintHub();
  }

  function saveCard() {
    var s = score();
    var rules = readRules();
    wiseCardPng("정보 지킴이 " + me.nick, [
      "나눈 카드 " + s.judged + "장 중 기준과 같음 " + s.hit + "장",
      "되돌리기 상자 " + leakList().length + "장",
      "생각을 바꾼 카드 " + count(st.again) + "장",
      "내 수칙 : " + (rules.length ? rules[0] : "아직 정하지 않았어요"),
      "한 번 넘어간 정보는 돌아오지 않는다."
    ], "wise_l04_" + me.nick);
  }

  function activityDraft() {
    return {
      choice: st.choice, sure: st.sure, why: st.why,
      cond: readCond(), rulePick: st.rules, ruleText: st.ruleCache, rules: readRules()
    };
  }

  function activityAutofill() {
    for (var i = 0; i < CARDS.length; i++) {
      st.choice[i] = String(CARDS[i].r);
      st.sure[i] = i % 3 === 0 ? "1" : "0";
    }
    /* 되돌리기 상자가 비면 열람실 화면을 검사하지 못한다. 한 장은 일부러 흘린다. */
    st.choice[0] = "0";
    st.why[0] = 3;
    st.quiz = QUIZ.length;
    st.quizOk = QUIZ.length;
    st.rules = { 0: true, 1: true, 3: true };
    st.ruleCache = { rx0: "넣기 전에 짝과 한 번 확인한다", rx1: "헷갈리면 노랑문으로 보낸다" };
  }

  function activityCollect() {
    var judged = count(st.choice);
    if (judged < 8) {
      $("w-msg").innerHTML = '<span class="warn">카드를 여덟 장 넘게 나눈 뒤에 제출해요. 지금 ' +
        judged + '장이에요.</span>';
      return null;
    }
    /* 까닭은 되돌리기 상자에 담긴 카드에만 묻는다. 많아도 세 개까지다. */
    var leakNow = leakList();
    var needWhy = Math.min(3, leakNow.length), gotWhy = 0;
    for (var v = 0; v < leakNow.length; v++) {
      if (st.why[leakNow[v]] !== undefined) { gotWhy++; }
    }
    if (gotWhy < needWhy) {
      $("w-msg").innerHTML = st.opened
        ? ('<span class="warn">되돌리기 상자에 담긴 카드의 까닭을 ' + needWhy +
           '개 골라 주세요. 지금 ' + gotWhy + '개예요.</span>')
        : '<span class="warn">열람실에서 카드를 먼저 열어 봐요. 놓친 카드의 까닭을 고르면 제출할 수 있어요.</span>';
      return null;
    }
    var rules = readRules();
    if (rules.length < 3) {
      $("w-msg").innerHTML = '<span class="warn">지킴이 수칙을 세 개 넘게 정한 뒤에 제출해요. 지금 ' +
        rules.length + '개예요.</span>';
      return null;
    }
    var s = score();
    var leaks = leakList();
    var unsure = 0;
    for (var k in st.sure) { if (st.sure.hasOwnProperty(k) && st.sure[k] === "1") { unsure++; } }

    wiseCelebrate("지킴이 임무를 마쳤어요", [
      "나눈 카드 <b>" + judged + "장</b>",
      "되돌리기 상자 <b>" + leaks.length + "장</b>",
      "정한 수칙 <b>" + rules.length + "개</b>",
      "다음 시간부터는 AI를 언제 어디까지 쓸지 우리가 정해요."
    ], "좋아요");

    return {
      choice: st.choice, sure: st.sure, why: st.why, cond: readCond(),
      rules: rules, rulePick: st.rules, ruleText: st.ruleCache,
      judged: judged, hit: s.hit, unsure: unsure,
      changed: count(st.again), leaked: leaks.length, quizOk: st.quizOk,
      badges: badgeNames()
    };
  }

  /* ---------- 교사 화면 ---------- */

  function tally(list) {
    var rows = [];
    for (var i = 0; i < CARDS.length; i++) {
      var c = [0, 0, 0], sum = 0;
      for (var k = 0; k < list.length; k++) {
        var ch = (list[k].payload || {}).choice || {};
        if (ch[i] === undefined) { continue; }
        c[Number(ch[i])] += 1;
        sum++;
      }
      rows.push({ i: i, c: c, sum: sum, agree: sum ? agreeOf(c) : 1, risk: CARDS[i].r });
    }
    return rows;
  }

  function teacherSummary(list) {
    var rows = tally(list);
    var hit = 0, judged = 0, changed = 0, leaked = 0;
    var whyCount = [0, 0, 0, 0];
    for (var k = 0; k < list.length; k++) {
      var p = list[k].payload || {};
      hit += p.hit || 0;
      judged += p.judged || 0;
      changed += p.changed || 0;
      leaked += p.leaked || 0;
      var w = p.why || {};
      for (var c in w) {
        if (!w.hasOwnProperty(c)) { continue; }
        var wi = Number(w[c]);
        if (wi >= 0 && wi < WHYS.length) { whyCount[wi] += 1; }
      }
    }
    var h = '<p class="muted">학급 안전 감각 ' + pct(hit, judged) + '% · 되돌리기 상자에 담긴 카드 ' +
      leaked + '장 · 생각을 바꾼 횟수 ' + changed + '회</p>' + barHtml(hit, judged);

    var whyRows = [];
    for (var r = 0; r < WHYS.length; r++) {
      whyRows.push({ label: WHYS[r], value: whyCount[r] });
    }
    h += '<h3 style="margin-top:16px">고른 까닭</h3>' + wiseBars(whyRows, 560);

    h += '<h3 style="margin-top:16px">카드별 분포</h3><div class="scroll"><table>' +
      '<tr><th>정보 카드</th><th>초록문</th><th>노랑문</th><th>빨간문</th><th>살펴볼 점</th></tr>';
    for (var i = 0; i < rows.length; i++) {
      var row = rows[i];
      if (!row.sum) { continue; }
      var flag = "";
      if (row.risk === 2 && row.c[0] > 0) {
        flag = '<span class="warn">빨간문 카드를 ' + row.c[0] + '명이 초록문으로 보냄</span>';
      } else if (row.agree < 0.7) {
        flag = '<span class="warn">의견 갈림</span>';
      }
      h += "<tr><td>" + esc(CARDS[row.i].t) + "</td><td>" + row.c[0] + "</td><td>" + row.c[1] +
        "</td><td>" + row.c[2] + "</td><td>" + flag + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">학생이 쓴 조건</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>정보 카드</th><th>조건</th></tr>';
    var condRows = 0;
    for (var m = 0; m < list.length; m++) {
      var cd = (list[m].payload || {}).cond || {};
      for (var key in cd) {
        if (!cd.hasOwnProperty(key) || !cd[key]) { continue; }
        condRows++;
        h += "<tr><td>" + esc(list[m].nick) + "</td><td>" +
          esc(CARDS[key] ? CARDS[key].t : key) + "</td><td>" + esc(cd[key]) + "</td></tr>";
      }
    }
    if (!condRows) { h += '<tr><td colspan="3">아직 쓴 조건이 없다.</td></tr>'; }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">모인 지킴이 수칙</h3>' + ruleTableHtml(list);
    return h;
  }

  function ruleTally(list) {
    var tallyMap = {}, order = [];
    for (var i = 0; i < list.length; i++) {
      var rs = (list[i].payload || {}).rules || [];
      for (var j = 0; j < rs.length; j++) {
        var key = String(rs[j]);
        if (!key) { continue; }
        if (tallyMap[key] === undefined) { tallyMap[key] = 0; order.push(key); }
        tallyMap[key] += 1;
      }
    }
    order.sort(function (a, b) { return tallyMap[b] - tallyMap[a]; });
    var out = [];
    for (var k = 0; k < order.length; k++) {
      out.push({ text: order[k], n: tallyMap[order[k]] });
    }
    return out;
  }

  function ruleTableHtml(list) {
    var rows = ruleTally(list);
    if (!rows.length) { return '<p class="muted">아직 모인 수칙이 없다.</p>'; }
    var h = '<div class="scroll"><table><tr><th>수칙</th><th>고른 사람</th></tr>';
    for (var i = 0; i < rows.length && i < 12; i++) {
      h += "<tr><td>" + esc(rows[i].text) + "</td><td>" + rows[i].n + "명</td></tr>";
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var rows = tally(list);
    rows.sort(function (a, b) {
      var ra = (a.risk === 2 && a.c[0] > 0) ? -1 : a.agree;
      var rb = (b.risk === 2 && b.c[0] > 0) ? -1 : b.agree;
      return ra - rb;
    });
    var h = '<p class="muted">먼저 볼 카드예요. 왜 그렇게 보았는지 까닭을 들어 봐요.</p>';
    for (var i = 0; i < rows.length && i < 3; i++) {
      var row = rows[i];
      if (!row.sum) { continue; }
      var bars = [
        { label: DOORS[0].name, value: row.c[0], color: "#16a34a" },
        { label: DOORS[1].name, value: row.c[1], color: "#eab308" },
        { label: DOORS[2].name, value: row.c[2], color: "#dc2626" }
      ];
      h += '<div class="card"><p class="big">' + esc(CARDS[row.i].t) + '</p>' +
        wiseBars(bars, 700) +
        '<p class="muted" style="margin-top:8px">' + esc(CARDS[row.i].w) + '</p></div>';
    }
    var rules = ruleTally(list);
    if (rules.length) {
      h += '<div class="card"><h2>우리 반 지킴이 수칙</h2><ul style="margin:10px 0 0 20px">';
      for (var r = 0; r < rules.length && r < 5; r++) {
        h += '<li>' + esc(rules[r].text) + ' <span class="pill">' + rules[r].n + '명</span></li>';
      }
      h += '</ul></div>';
    }
    return h;
  }
"""
