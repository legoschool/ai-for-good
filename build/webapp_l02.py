# -*- coding: utf-8 -*-
"""2차시 AI 검증 실험실.

spec/11_웹앱_설계_L02.md 대로 만든 여정형 앱이다.

  이야기 → 검증소(허브) → 훈련소 → 검증실 → 환각 사냥 → 우리 반 판정 → 검증관 카드

학생이 검증관이 되어 몽이의 답변을 심사한다.
생성형 AI 를 실시간으로 부르지 않는다. 답변 세트는 교사가 미리 확인한 것을 담는다.
자신감 수치가 정확도가 아니라는 것이 이 차시의 함정이다.
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */
  /* 전부 교과서 수준에서 확인할 수 있는 것만 담는다.
     wrong 은 답변을 조각으로 나눈 것이고, bad 는 틀린 조각의 번호다. */

  var ITEMS = [
    {
      q: "한글은 언제 반포되었나요?",
      say: ["세종대왕은", "1443년에", "한글을", "온 백성에게", "반포했습니다."],
      bad: [1],
      conf: 98,
      source: "옛날 책에서 본 것 같습니다. 어디였는지는 잘 모르겠습니다.",
      check: "교과서",
      truth: "1443년은 한글을 만든 해예요. 백성에게 알린 해는 1446년입니다.",
      why: "만든 해와 알린 해가 다릅니다. 몽이는 두 해를 하나로 섞었어요."
    },
    {
      q: "태양계 행성은 몇 개인가요?",
      say: ["태양계에는", "아홉 개의", "행성이", "있습니다."],
      bad: [1],
      conf: 95,
      source: "예전 자료에서 배웠습니다. 최근 것은 확인하지 못했습니다.",
      check: "교과서",
      truth: "여덟 개예요. 2006년에 명왕성이 행성에서 빠졌습니다.",
      why: "오래된 자료로 배우면 바뀐 사실을 모릅니다."
    },
    {
      q: "물은 몇 도에서 끓나요?",
      say: ["물은", "언제나", "100도에서", "끓습니다."],
      bad: [1],
      conf: 99,
      source: "과학 상식이라고만 알고 있습니다.",
      check: "교과서",
      truth: "1기압일 때 100도예요. 높은 산에서는 100도보다 낮은 온도에서 끓습니다.",
      why: "조건을 빼고 말하면 반쯤만 맞는 답이 됩니다."
    },
    {
      q: "독도는 어느 행정구역에 속하나요?",
      say: ["독도는", "강원도에", "속합니다."],
      bad: [1],
      conf: 92,
      source: "동해에 있다는 것만 알고 있었습니다.",
      check: "공공 누리집",
      truth: "경상북도 울릉군에 속합니다.",
      why: "가까운 것을 근거로 짐작하면 틀립니다. 공공 누리집에서 확인해야 합니다."
    },
    {
      q: "우리 학교 급식 잔반량은 하루에 얼마인가요?",
      say: ["우리 학교는", "하루 42.7킬로그램의", "잔반이", "나옵니다."],
      bad: [0, 1],
      conf: 89,
      source: "정확한 출처가 없습니다. 비슷한 학교 자료를 참고했습니다.",
      check: "선생님·어른",
      truth: "AI 는 우리 학교 잔반량을 알 수 없어요. 영양 선생님께 여쭤봐야 합니다.",
      why: "알 수 없는 것을 숫자까지 붙여 말하는 것이 환각의 전형입니다."
    }
  ];

  /* 훈련소. 같은 물음에 답 두 개를 놓고 진짜를 고른다. */
  var TRAIN = [
    {
      q: "세종대왕이 한글을 만든 까닭은?",
      a: {t:"백성이 글을 쉽게 익혀 뜻을 펴게 하려고 만들었습니다.", conf: 71, ok: true},
      b: {t:"중국 글자를 더 빨리 쓰려고 만들었습니다.", conf: 97, ok: false},
      why: "자신감이 높다고 맞는 답이 아니에요. 97%라고 말한 쪽이 틀렸습니다."
    },
    {
      q: "우리나라에서 가장 큰 섬은?",
      a: {t:"제주도입니다.", conf: 64, ok: true},
      b: {t:"울릉도입니다.", conf: 93, ok: false},
      why: "짧고 단호한 말투가 정확함을 뜻하지 않습니다."
    },
    {
      q: "내일 우리 반 급식 메뉴는?",
      a: {t:"저는 알 수 없어요. 학교 급식 안내를 보아야 합니다.", conf: 55, ok: true},
      b: {t:"내일은 카레라이스와 요구르트가 나옵니다.", conf: 90, ok: false},
      why: "모른다고 말하는 답이 더 좋은 답일 때가 있습니다."
    }
  ];

  var METHODS = ["교과서", "공공 누리집", "선생님·어른"];
  var STAMPS = [
    {name: "사실", icon: "check"},
    {name: "의심", icon: "again"},
    {name: "거짓", icon: "red"}
  ];

  var st = {
    tr: 0, trOk: 0, trPick: "",
    i: 0, step: {}, method: {}, note: {}, verdict: {}, asked: {},
    huntI: 0, huntPick: {}, huntDone: {},
    badges: {}, classDist: null
  };

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">사실 검증소</h2>' +
      '<div class="card" style="margin:12px 0;background:var(--accent-soft)">' +
      '<p style="font-size:19px;font-weight:700">"한글은 1443년에 반포되었습니다."</p>' +
      '<p class="muted" style="margin-top:6px">몽이 · 자신감 98%</p></div>' +
      '<p>몽이는 아주 자신 있게 말해요. 그런데 이 말은 <b>틀렸어요.</b></p>' +
      '<p style="margin-top:8px">몽이는 배운 것만 알아요. 배우지 못한 것도 아는 것처럼 말할 때가 있어요. ' +
      '이것을 <b>환각</b>이라고 불러요.</p>' +
      '<p style="margin-top:8px">오늘 여러분은 <b>검증관</b>이 되어 몽이의 답을 심사해요. ' +
      '도장은 세 개예요. 사실, 의심, 거짓.</p>' +
      '<div class="row" style="margin-top:14px"><button type="button" id="go-hub">검증소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>검증소</h2>' +
      '<p class="muted">훈련소부터 하면 쉬워요. 순서를 바꿔도 괜찮아요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-train">' + wiseIcon("star", 30) +
      '<span>훈련소</span><small id="s-train">진짜와 가짜 고르기 3문항</small></button>' +
      '<button type="button" class="tile" id="t-verify">' + wiseIcon("check", 30) +
      '<span>검증실</span><small id="s-verify">3단계로 확인하고 도장 찍기</small></button>' +
      '<button type="button" class="tile" id="t-hunt">' + wiseIcon("write", 30) +
      '<span>환각 사냥</span><small id="s-hunt">틀린 조각을 짚어 내기</small></button>' +
      '<button type="button" class="tile" id="t-class">' + wiseIcon("talk", 30) +
      '<span>우리 반 판정</span><small id="s-class">갈린 문항 보기</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("id", 30) +
      '<span>검증관 카드</span><small id="s-card">오늘의 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("train",
      '<div class="card"><span class="pill">훈련소</span>' +
      '<h2 style="margin-top:10px">어느 쪽이 진짜일까</h2>' +
      '<div id="trainbox"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">검증소로</button></div></div>');

    h += q("verify",
      '<div class="card"><span class="pill">검증실</span>' +
      '<h2 style="margin-top:10px" id="v-title">몽이의 답을 심사해요</h2>' +
      '<div id="verifybox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="v-prev" class="plain">앞 문항</button>' +
      '<button type="button" id="v-next" class="ghost">다음 문항</button>' +
      '<span class="muted" id="v-pos"></span></div>' +
      '<div class="row" style="margin-top:10px"><button type="button" class="plain back">검증소로</button></div></div>');

    h += q("hunt",
      '<div class="card"><span class="pill">환각 사냥</span>' +
      '<h2 style="margin-top:10px">틀린 조각을 짚어 봐요</h2>' +
      '<p class="muted">문장을 눌러 표시해요. 다 고르면 확인을 누릅니다.</p>' +
      '<div id="huntbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="h-prev" class="plain">앞 문항</button>' +
      '<button type="button" id="h-next" class="ghost">다음 문항</button>' +
      '<span class="muted" id="h-pos"></span></div>' +
      '<div class="row" style="margin-top:10px"><button type="button" class="plain back">검증소로</button></div></div>');

    h += q("class",
      '<div class="card"><span class="pill">함께 보기</span>' +
      '<h2 style="margin-top:10px">우리 반은 어떻게 판정했을까</h2>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="peek">우리 반 판정 불러오기</button></div>' +
      '<div id="dist" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:10px"><button type="button" class="plain back">검증소로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">나의 검증관 카드</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">인증서 그림으로 저장</button>' +
      '<button type="button" class="plain back">검증소로</button></div></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>');

    return h;
  }

  /* ---------- 훈련소 ---------- */

  function trainHtml() {
    if (st.tr >= TRAIN.length) {
      return '<p class="big">' + st.trOk + ' / ' + TRAIN.length + '</p>' +
        '<p class="muted">자신감 수치는 정확도가 아니에요. 몽이는 틀릴 때도 당당해요.</p>' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" id="train-go">검증실로 가기</button></div>';
    }
    var t = TRAIN[st.tr];
    var h = '<p class="muted">' + (st.tr + 1) + ' / ' + TRAIN.length + '</p>' +
      '<h3 style="margin:8px 0 12px">' + esc(t.q) + '</h3>';
    var opts = [["a", t.a], ["b", t.b]];
    for (var i = 0; i < opts.length; i++) {
      var key = opts[i][0], o = opts[i][1];
      var mark = "";
      if (st.trPick) { mark = o.ok ? " on" : ""; }
      h += '<button type="button" class="chip tr' + mark + '" data-k="' + key + '">' +
        esc(o.t) + '<br><span class="muted">몽이 자신감 ' + o.conf + '%</span></button>';
    }
    if (st.trPick) {
      var picked = st.trPick === "a" ? t.a : t.b;
      h += '<p class="' + (picked.ok ? "ok" : "warn") + '" style="margin-top:10px">' +
        (picked.ok ? "맞았어요. " : "다시 봐요. ") + esc(t.why) + '</p>' +
        '<div class="row" style="margin-top:10px"><button type="button" id="train-next">다음</button></div>';
    }
    return h;
  }

  function bindTrain() {
    $("trainbox").innerHTML = trainHtml();
    var opts = document.querySelectorAll("#activity .tr");
    for (var i = 0; i < opts.length; i++) {
      opts[i].onclick = function () {
        if (st.trPick) { return; }
        st.trPick = this.getAttribute("data-k");
        var t = TRAIN[st.tr];
        if ((st.trPick === "a" ? t.a : t.b).ok) { st.trOk += 1; }
        bindTrain();
      };
    }
    if ($("train-next")) {
      $("train-next").onclick = function () {
        st.tr += 1;
        st.trPick = "";
        bindTrain();
        paintHub();
        if (st.tr >= TRAIN.length) { award("훈련 수료"); }
      };
    }
    if ($("train-go")) { $("train-go").onclick = function () { wiseGo("verify"); }; }
  }

  /* ---------- 검증실 ---------- */

  function sayLine(item) {
    return item.say.join(" ");
  }

  function stepDone(i, name) {
    var box = st.step[i] || [];
    for (var k = 0; k < box.length; k++) { if (box[k] === name) { return true; } }
    return false;
  }

  function markStep(i, name) {
    if (!st.step[i]) { st.step[i] = []; }
    if (!stepDone(i, name)) { st.step[i].push(name); }
  }

  function verifyHtml() {
    var i = st.i, item = ITEMS[i];
    var h = '<div class="card" style="margin:12px 0;background:var(--accent-soft)">' +
      '<p class="muted">' + esc(item.q) + '</p>' +
      '<p style="font-size:19px;font-weight:700;margin-top:6px">' + esc(sayLine(item)) + '</p>' +
      '<p class="muted" style="margin-top:6px">몽이 · 자신감 ' + item.conf + '%</p></div>';

    h += '<h3>1단계 출처 확인</h3>';
    if (st.asked[i]) {
      h += '<p class="note">몽이 : ' + esc(item.source) + '</p>';
    } else {
      h += '<button type="button" class="chip ask">출처를 물어보기</button>';
    }

    h += '<h3 style="margin-top:14px">2단계 대조하기</h3>' +
      '<p class="muted">어떤 방법으로 확인할까요</p>';
    for (var m = 0; m < METHODS.length; m++) {
      h += '<button type="button" class="chip mth' + (st.method[i] === METHODS[m] ? " on" : "") +
        '" data-m="' + esc(METHODS[m]) + '">' + esc(METHODS[m]) + '</button>';
    }
    if (st.method[i]) {
      h += '<p class="note" style="margin-top:8px">' + esc(item.check) + '에서 확인한 것 : ' +
        esc(item.truth) + '</p>';
    }

    h += '<h3 style="margin-top:14px">3단계 내 말로 정리</h3>' +
      '<input id="note' + i + '" maxlength="80" placeholder="확인한 것을 한 줄로 써요" value="' +
      esc(st.note[i] || "") + '">';

    var ready = st.asked[i] && st.method[i] && (st.note[i] || "").length > 2;
    h += '<h3 style="margin-top:16px">도장 찍기</h3>';
    if (!ready) {
      h += '<p class="muted">세 단계를 마치면 도장이 열려요.</p>';
    }
    h += '<div class="row">';
    for (var s = 0; s < STAMPS.length; s++) {
      h += '<button type="button" class="chip stamp' + (st.verdict[i] === STAMPS[s].name ? " on" : "") +
        '" data-v="' + esc(STAMPS[s].name) + '" style="width:auto;margin:0"' +
        (ready ? "" : " disabled") + '>' + wiseIcon(STAMPS[s].icon, 24) + esc(STAMPS[s].name) + '</button>';
    }
    h += '</div>';

    if (st.verdict[i]) {
      h += '<div class="card" style="margin-top:12px;border-color:var(--accent)">' +
        '<p class="ok">확인한 사실</p><p style="font-size:18px;margin-top:6px">' + esc(item.truth) + '</p>' +
        '<p class="muted" style="margin-top:6px">' + esc(item.why) + '</p></div>';
    }
    return h;
  }

  function bindVerify() {
    $("verifybox").innerHTML = verifyHtml();
    if ($("v-pos")) {
      $("v-pos").textContent = (st.i + 1) + " / " + ITEMS.length + " · 도장 찍은 문항 " + verdictCount() + "개";
    }
    var asks = document.querySelectorAll("#activity .ask");
    for (var a = 0; a < asks.length; a++) {
      asks[a].onclick = function () {
        var btn = this;
        wiseButtonBusy(btn, true, "몽이에게 묻는 중");
        setTimeout(function () {
          st.asked[st.i] = true;
          markStep(st.i, "출처");
          bindVerify();
        }, 520);
      };
    }
    var mths = document.querySelectorAll("#activity .mth");
    for (var m = 0; m < mths.length; m++) {
      mths[m].onclick = function () {
        var btn = this, pick = this.getAttribute("data-m");
        wiseButtonBusy(btn, true, pick + " 확인 중");
        setTimeout(function () {
          st.method[st.i] = pick;
          markStep(st.i, "대조");
          bindVerify();
        }, 620);
      };
    }
    var note = $("note" + st.i);
    if (note) {
      note.oninput = function () {
        st.note[st.i] = this.value.trim();
        if (this.value.trim().length > 2) { markStep(st.i, "내 말"); }
      };
      note.onblur = function () { bindVerify(); };
    }
    var stamps = document.querySelectorAll("#activity .stamp");
    for (var s = 0; s < stamps.length; s++) {
      stamps[s].onclick = function () {
        if (this.disabled) { return; }
        st.verdict[st.i] = this.getAttribute("data-v");
        bindVerify();
        paintHub();
        if (verdictCount() >= 3) { award("검증관"); }
      };
    }
  }

  function verdictCount() {
    var n = 0;
    for (var k in st.verdict) { if (st.verdict.hasOwnProperty(k)) { n++; } }
    return n;
  }

  /* ---------- 환각 사냥 ---------- */

  function huntHtml() {
    var i = st.huntI, item = ITEMS[i];
    var picks = st.huntPick[i] || {};
    var h = '<p class="muted">' + esc(item.q) + '</p><div class="row" style="margin-top:10px">';
    for (var k = 0; k < item.say.length; k++) {
      h += '<button type="button" class="chip pc' + (picks[k] ? " on" : "") +
        '" data-p="' + k + '" style="width:auto;margin:0">' + esc(item.say[k]) + '</button>';
    }
    h += '</div>';
    if (!st.huntDone[i]) {
      h += '<div class="row" style="margin-top:12px">' +
        '<button type="button" id="h-check">확인하기</button></div>';
    } else {
      var r = huntScore(i);
      h += '<div class="card" style="margin-top:12px">' +
        '<p><b>잡아냄 ' + r.hit + '</b> · 놓침 ' + r.miss + ' · 잘못 짚음 ' + r.wrong + '</p>' +
        '<p class="muted" style="margin-top:6px">틀린 곳 : ' + esc(badWords(item)) + '</p>' +
        '<p style="margin-top:6px">' + esc(item.truth) + '</p></div>';
    }
    return h;
  }

  function badWords(item) {
    var out = [];
    for (var k = 0; k < item.bad.length; k++) { out.push(item.say[item.bad[k]]); }
    return out.join(" / ");
  }

  function huntScore(i) {
    var item = ITEMS[i], picks = st.huntPick[i] || {};
    var hit = 0, wrong = 0, miss = 0;
    for (var k = 0; k < item.say.length; k++) {
      var isBad = false;
      for (var b = 0; b < item.bad.length; b++) { if (item.bad[b] === k) { isBad = true; } }
      if (picks[k] && isBad) { hit++; }
      if (picks[k] && !isBad) { wrong++; }
      if (!picks[k] && isBad) { miss++; }
    }
    return { hit: hit, wrong: wrong, miss: miss, perfect: miss === 0 && wrong === 0 && hit > 0 };
  }

  function caughtCount() {
    var n = 0;
    for (var k in st.huntDone) {
      if (st.huntDone.hasOwnProperty(k) && huntScore(Number(k)).perfect) { n++; }
    }
    return n;
  }

  function bindHunt() {
    $("huntbox").innerHTML = huntHtml();
    if ($("h-pos")) {
      $("h-pos").textContent = (st.huntI + 1) + " / " + ITEMS.length + " · 정확히 잡은 문항 " + caughtCount() + "개";
    }
    var pcs = document.querySelectorAll("#activity .pc");
    for (var i = 0; i < pcs.length; i++) {
      pcs[i].onclick = function () {
        if (st.huntDone[st.huntI]) { return; }
        var k = Number(this.getAttribute("data-p"));
        if (!st.huntPick[st.huntI]) { st.huntPick[st.huntI] = {}; }
        st.huntPick[st.huntI][k] = !st.huntPick[st.huntI][k];
        bindHunt();
      };
    }
    if ($("h-check")) {
      $("h-check").onclick = function () {
        var btn = this;
        wiseButtonBusy(btn, true, "채점하는 중");
        setTimeout(function () {
          st.huntDone[st.huntI] = true;
          bindHunt();
          paintHub();
          if (caughtCount() >= 2) { award("환각 사냥꾼"); }
        }, 420);
      };
    }
  }

  /* ---------- 우리 반 판정 ---------- */

  function peek() {
    if (me.solo) {
      $("dist").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 판정이 없어요. ' +
        '검증과 사냥은 그대로 해 볼 수 있어요.</p>';
      return;
    }
    $("dist").innerHTML = wiseSpinner("우리 반 판정을 불러오는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      var tally = {};
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var v = (data[k].payload || {}).verdicts || {};
        for (var i in v) {
          if (!v.hasOwnProperty(i)) { continue; }
          if (!tally[i]) { tally[i] = {사실: 0, 의심: 0, 거짓: 0}; }
          tally[i][v[i]] = (tally[i][v[i]] || 0) + 1;
        }
      }
      st.classDist = tally;
      $("dist").innerHTML = distHtml(tally);
      paintHub();
    })["catch"](function () {
      $("dist").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function distHtml(tally) {
    var keys = [];
    for (var i in tally) { if (tally.hasOwnProperty(i)) { keys.push(i); } }
    if (!keys.length) { return '<p class="muted">아직 우리 반 판정이 모이지 않았어요.</p>'; }
    keys.sort(function (a, b) { return agree(tally[a]) - agree(tally[b]); });
    var h = '<p class="muted">판정이 갈린 문항부터 보여 줘요.</p><div class="scroll"><table>' +
      '<tr><th>문항</th><th>사실</th><th>의심</th><th>거짓</th><th>내 도장</th></tr>';
    for (var k = 0; k < keys.length; k++) {
      var t = tally[keys[k]];
      h += "<tr><td>" + esc(ITEMS[keys[k]] ? ITEMS[keys[k]].q : keys[k]) + "</td><td>" +
        (t["사실"] || 0) + "</td><td>" + (t["의심"] || 0) + "</td><td>" + (t["거짓"] || 0) +
        "</td><td>" + esc(st.verdict[keys[k]] || "-") + "</td></tr>";
    }
    return h + "</table></div>";
  }

  function agree(t) {
    var sum = (t["사실"] || 0) + (t["의심"] || 0) + (t["거짓"] || 0);
    if (!sum) { return 1; }
    return Math.max(t["사실"] || 0, t["의심"] || 0, t["거짓"] || 0) / sum;
  }

  /* ---------- 검증관 카드 ---------- */

  function methodCount() {
    var box = {};
    for (var k in st.method) {
      if (!st.method.hasOwnProperty(k)) { continue; }
      box[st.method[k]] = (box[st.method[k]] || 0) + 1;
    }
    return box;
  }

  function paintMine() {
    if (!$("mine")) { return; }
    var box = methodCount(), rows = [];
    for (var m = 0; m < METHODS.length; m++) {
      rows.push({ label: METHODS[m], value: box[METHODS[m]] || 0 });
    }
    var h = wiseBars(rows, 520);
    h += '<p style="margin-top:10px">도장 찍은 문항 ' + verdictCount() + ' / ' + ITEMS.length +
      '개 · 정확히 잡아낸 환각 ' + caughtCount() + '개 · 훈련소 ' + st.trOk + ' / ' + TRAIN.length + '</p>';
    if (caughtCount()) {
      h += '<p class="ok">그럴듯한 거짓말을 잡아냈어요. 확인하면 쓸 수 있어요.</p>';
    }
    $("mine").innerHTML = h;
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
    paintHub();
  }

  function paintHub() {
    if (!$("s-verify")) { return; }
    $("s-train").textContent = st.tr >= TRAIN.length
      ? ("맞힌 문제 " + st.trOk + " / " + TRAIN.length) : "진짜와 가짜 고르기 3문항";
    $("s-verify").textContent = "도장 찍은 문항 " + verdictCount() + " / " + ITEMS.length;
    $("s-hunt").textContent = "정확히 잡은 문항 " + caughtCount() + "개";
    $("s-class").textContent = st.classDist ? "우리 반 판정을 보았어요" : "갈린 문항 보기";
    $("s-card").textContent = "오늘의 기록";
    var tiles = [["t-train", st.tr >= TRAIN.length], ["t-verify", verdictCount() >= 3],
      ["t-hunt", caughtCount() >= 2], ["t-class", !!st.classDist], ["t-card", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }
    var names = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { names.push(b); } }
    $("badges").innerHTML = names.length
      ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
      : '<span class="muted">아직 없어요. 훈련소부터 해 볼까요?</span>';
    wiseHud([
      { label: "검증", done: verdictCount(), total: ITEMS.length },
      { label: "잡아낸 환각", done: caughtCount(), total: ITEMS.length },
      { label: "훈련소", done: st.trOk, total: TRAIN.length }
    ]);
    paintMine();
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "train") { bindTrain(); }
    if (id === "verify") { bindVerify(); }
    if (id === "hunt") { bindHunt(); }
    if (id === "card") { paintMine(); }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.verdicts) { st.verdict = saved.verdicts; }
      if (saved.notes) { st.note = saved.notes; }
      if (saved.methods0) { st.method = saved.methods0; }
    }
    $("go-hub").onclick = function () { wiseGo("hub"); };
    $("t-train").onclick = function () { wiseGo("train"); };
    $("t-verify").onclick = function () { wiseGo("verify"); };
    $("t-hunt").onclick = function () { wiseGo("hunt"); };
    $("t-class").onclick = function () { wiseGo("class"); };
    $("t-card").onclick = function () { wiseGo("card"); };
    $("v-prev").onclick = function () { if (st.i > 0) { st.i -= 1; bindVerify(); } };
    $("v-next").onclick = function () { if (st.i < ITEMS.length - 1) { st.i += 1; bindVerify(); } };
    $("h-prev").onclick = function () { if (st.huntI > 0) { st.huntI -= 1; bindHunt(); } };
    $("h-next").onclick = function () { if (st.huntI < ITEMS.length - 1) { st.huntI += 1; bindHunt(); } };
    $("peek").onclick = peek;
    $("save-card").onclick = function () {
      wiseCardPng("AI 검증관 인증서 · " + me.nick, [
        "도장 찍은 문항 " + verdictCount() + " / " + ITEMS.length,
        "정확히 잡아낸 환각 " + caughtCount() + "개",
        "훈련소 " + st.trOk + " / " + TRAIN.length,
        "확인하면 쓸 수 있다."
      ], "wise_l02_" + me.nick);
      award("기록하는 검증관");
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }
    wiseNote("자신감 수치가 높다고 맞는 답이 아니에요. 세 단계로 확인해요.");
    wiseGo("story");
    paintHub();
  }

  function activityDraft() {
    return { verdicts: st.verdict, notes: st.note, methods0: st.method };
  }

  function activityAutofill() {
    for (var i = 0; i < ITEMS.length; i++) {
      st.asked[i] = true;
      st.method[i] = ITEMS[i].check;
      st.note[i] = "확인했습니다";
      st.verdict[i] = i === 0 ? "거짓" : (i % 2 ? "의심" : "거짓");
      st.step[i] = ["출처", "대조", "내 말"];
      st.huntPick[i] = {};
      for (var b = 0; b < ITEMS[i].bad.length; b++) { st.huntPick[i][ITEMS[i].bad[b]] = true; }
      st.huntDone[i] = true;
    }
    st.tr = TRAIN.length;
    st.trOk = TRAIN.length;
  }

  function activityCollect() {
    if (verdictCount() < 3) {
      $("w-msg").innerHTML = '<span class="warn">문항 세 개 넘게 도장을 찍은 뒤에 제출해요. 지금 ' +
        verdictCount() + '개예요.</span>';
      return null;
    }
    var hunt = {};
    for (var k in st.huntDone) {
      if (st.huntDone.hasOwnProperty(k)) { hunt[k] = huntScore(Number(k)); }
    }
    var badges = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { badges.push(b); } }
    wiseCelebrate("검증을 마쳤어요", [
      "도장 찍은 문항 <b>" + verdictCount() + "개</b>",
      "정확히 잡아낸 환각 <b>" + caughtCount() + "개</b>",
      "자신감 수치는 정확도가 아니에요.",
      "다음 시간에는 AI의 치우침을 데이터에서 찾아봅니다."
    ], "좋아요");
    return {
      train: { ok: st.trOk },
      verdicts: st.verdict, steps: st.step, notes: st.note,
      methods: methodCount(), hunt: hunt, caught: caughtCount(),
      badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function teacherSummary(list) {
    var tally = {}, mbox = {}, caught = 0, n = 0;
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.verdicts) { continue; }
      n++;
      caught += p.caught || 0;
      for (var k in p.verdicts) {
        if (!p.verdicts.hasOwnProperty(k)) { continue; }
        if (!tally[k]) { tally[k] = {사실: 0, 의심: 0, 거짓: 0}; }
        tally[k][p.verdicts[k]] = (tally[k][p.verdicts[k]] || 0) + 1;
      }
      var m = p.methods || {};
      for (var mk in m) { if (m.hasOwnProperty(mk)) { mbox[mk] = (mbox[mk] || 0) + m[mk]; } }
    }
    var h = '<p class="muted">제출 ' + n + '명 · 정확히 잡아낸 환각 평균 ' +
      (n ? (caught / n).toFixed(1) : 0) + '개</p>';

    var rows = [];
    for (var mm = 0; mm < METHODS.length; mm++) {
      rows.push({ label: METHODS[mm], value: mbox[METHODS[mm]] || 0 });
    }
    h += wiseBars(rows, 560);

    h += '<div class="scroll" style="margin-top:12px"><table>' +
      '<tr><th>문항</th><th>사실</th><th>의심</th><th>거짓</th><th>살펴볼 점</th></tr>';
    for (var q2 = 0; q2 < ITEMS.length; q2++) {
      var t = tally[q2];
      if (!t) { continue; }
      h += "<tr><td>" + esc(ITEMS[q2].q) + "</td><td>" + (t["사실"] || 0) + "</td><td>" +
        (t["의심"] || 0) + "</td><td>" + (t["거짓"] || 0) + "</td><td>" +
        (agree(t) < 0.6 ? '<span class="warn">판정 갈림</span>' :
          ((t["사실"] || 0) > 0 ? '<span class="warn">사실로 본 학생 있음</span>' : "")) + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">학생이 쓴 정리 문장</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>문항</th><th>내 말로 정리</th></tr>';
    for (var s = 0; s < list.length; s++) {
      var notes = (list[s].payload || {}).notes || {};
      for (var nk in notes) {
        if (!notes.hasOwnProperty(nk) || !notes[nk]) { continue; }
        h += "<tr><td>" + esc(list[s].nick) + "</td><td>" +
          esc(ITEMS[nk] ? ITEMS[nk].q : nk) + "</td><td>" + esc(notes[nk]) + "</td></tr>";
      }
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var tally = {};
    for (var i = 0; i < list.length; i++) {
      var v = (list[i].payload || {}).verdicts || {};
      for (var k in v) {
        if (!v.hasOwnProperty(k)) { continue; }
        if (!tally[k]) { tally[k] = {사실: 0, 의심: 0, 거짓: 0}; }
        tally[k][v[k]] = (tally[k][v[k]] || 0) + 1;
      }
    }
    var last = ITEMS.length - 1;
    var t = tally[last] || {사실: 0, 의심: 0, 거짓: 0};
    var h = '<p class="big">' + esc(ITEMS[last].q) + '</p>' +
      wiseBars([
        { label: "사실", value: t["사실"] || 0, color: "#16a34a" },
        { label: "의심", value: t["의심"] || 0, color: "#eab308" },
        { label: "거짓", value: t["거짓"] || 0, color: "#dc2626" }
      ], 700) +
      '<p class="muted" style="margin-top:10px">' + esc(ITEMS[last].truth) + '</p>';
    h += '<h3 style="margin-top:18px">우리 반이 쓴 정리 문장</h3>';
    var shown = 0;
    for (var s = 0; s < list.length && shown < 5; s++) {
      var notes = (list[s].payload || {}).notes || {};
      for (var nk in notes) {
        if (!notes.hasOwnProperty(nk) || !notes[nk] || shown >= 5) { continue; }
        shown++;
        h += '<p style="font-size:20px;margin:8px 0">' + esc(notes[nk]) + '</p>';
      }
    }
    return h;
  }
"""
