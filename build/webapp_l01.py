# -*- coding: utf-8 -*-
"""1차시 데이터 실험실.

spec/10_웹앱_설계_L01.md 대로 만든 여정형 앱이다.

  이야기 → 교무실(허브) → 1교시 나라면 → 2교시 이름표 붙이기
  → 3교시 학습과 시험 → 4교시 편식 실험 → 5교시 역할 나누기 → 성적표

학생이 AI 학생 '몽이'의 선생님이 된다.
브라우저 안에서 나이브 베이즈가 실제로 학생의 라벨로 학습한다. 외부 서비스를 부르지 않는다.
라벨을 바꾸면 결과가 바뀌고, 한쪽을 굶기면 정확도가 무너진다.
"""

ACTIVITY = u"""
  /* ---------- 카드 더미 ---------- */
  /* 특징 네 가지로만 이루어진 카드다. 정답을 적어 두지 않는다.
     이름표를 붙이는 것은 사람의 판단이라는 점이 이 차시의 핵심이다. */

  var TRAIN = [
    {id:0, ear:"뾰족", tail:"길다", size:"크다", coat:"어둡다", p:"p00"},
    {id:1, ear:"처짐", tail:"길다", size:"크다", coat:"어둡다", p:"p01"},
    {id:2, ear:"처짐", tail:"길다", size:"작다", coat:"밝다", p:"p10"},
    {id:3, ear:"처짐", tail:"길다", size:"크다", coat:"밝다", p:"p02"},
    {id:4, ear:"처짐", tail:"길다", size:"작다", coat:"밝다", p:"p11"},
    {id:5, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p12"},
    {id:6, ear:"뾰족", tail:"짧다", size:"작다", coat:"어둡다", p:"p03"},
    {id:7, ear:"뾰족", tail:"길다", size:"크다", coat:"어둡다", p:"p13"},
    {id:8, ear:"뾰족", tail:"짧다", size:"작다", coat:"밝다", p:"p04"},
    {id:9, ear:"처짐", tail:"길다", size:"크다", coat:"어둡다", p:"p05"},
    {id:10, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p14"},
    {id:11, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p15"},
    {id:12, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p06"},
    {id:13, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p16"},
    {id:14, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p07"},
    {id:15, ear:"뾰족", tail:"길다", size:"크다", coat:"어둡다", p:"p17"},
    {id:16, ear:"처짐", tail:"길다", size:"작다", coat:"어둡다", p:"p08"},
    {id:17, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p18"},
    {id:18, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p09"},
    {id:19, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p19"}
  ];


  /* 시험 카드에는 답이 정해져 있다. 귀 하나만 보고는 못 맞히는 카드가 섞여 있다.
     그래서 데이터를 줄이면 그 카드부터 틀린다. 이것이 4교시의 핵심이다. */
  var TEST = [
    {id:100, ear:"뾰족", tail:"짧다", size:"작다", coat:"밝다", p:"p20", ans:"강아지"},
    {id:101, ear:"처짐", tail:"짧다", size:"작다", coat:"밝다", p:"p21", ans:"강아지"},
    {id:102, ear:"처짐", tail:"길다", size:"크다", coat:"어둡다", p:"p22", ans:"강아지"},
    {id:103, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p23", ans:"고양이"},
    {id:104, ear:"뾰족", tail:"길다", size:"작다", coat:"어둡다", p:"p24", ans:"고양이"},
    {id:105, ear:"뾰족", tail:"길다", size:"작다", coat:"밝다", p:"p25", ans:"고양이"}
  ];


  var FEATS = ["ear", "tail", "size", "coat"];
  var FEAT_NAME = {ear:"귀 모양", tail:"꼬리 길이", size:"몸집", coat:"털 색"};
  var LABELS = ["강아지", "고양이"];

  var ROLE_ITEMS = [
    "어떤 카드를 모을지 정했다",
    "카드에 이름표를 붙였다",
    "이름표를 보고 규칙을 계산했다",
    "새 카드가 무엇인지 예측했다",
    "무엇을 배우게 할지 결정했다",
    "정확도를 숫자로 계산했다",
    "틀린 까닭이 무엇인지 따져 보았다",
    "데이터를 줄일지 말지 정했다",
    "결과를 보고 다음에 무엇을 할지 정했다",
    "예측 결과를 화면에 표시했다"
  ];

  /* ---------- 그림 ---------- */

  /* 카드 그림은 진짜 사진이다. 파일을 부르지 않고 HTML 안에 넣어 두었다.
     사진은 CC0 · 퍼블릭 도메인만 골랐다. 출처는 성적표 아래 '사진 출처'에 있다. */
  var PHOTOS = __PHOTOS__;

  function petImg(c, big) {
    var w = big ? 300 : 132;
    return '<img class="pet" src="' + (PHOTOS[c.p] || "") + '" alt="동물 사진 카드" ' +
      'style="width:' + w + 'px;max-width:100%;border-radius:14px;border:1px solid var(--line);' +
      'box-shadow:var(--shadow)">';
  }

  /* 몽이. mood 는 new 빈 공책 · learn 배우는 중 · happy 잘함 · sad 헤맴 */
  function mongSvg(mood, size) {
    var s = size || 120;
    var eye = mood === "sad" ? '<path d="M38 44 q6 -6 12 0 M62 44 q6 -6 12 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
      : '<circle cx="42" cy="46" r="5.5" fill="#111"/><circle cx="70" cy="46" r="5.5" fill="#111"/>';
    var mouth = mood === "happy" ? '<path d="M46 62 q10 10 20 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
      : (mood === "sad" ? '<path d="M46 66 q10 -8 20 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
        : '<path d="M48 62 h16" stroke="#111" stroke-width="4" stroke-linecap="round"/>');
    var book = mood === "learn"
      ? '<rect x="30" y="84" width="52" height="24" rx="5" fill="#FFE24B" stroke="#111" stroke-width="3"/>' +
        '<path d="M38 92 h20 M38 100 h30" stroke="#111" stroke-width="3" stroke-linecap="round"/>'
      : '<rect x="30" y="84" width="52" height="24" rx="5" fill="#fff" stroke="#111" stroke-width="3"/>';
    return '<svg viewBox="0 0 112 116" width="' + s + '" height="' + s + '" aria-hidden="true">' +
      '<ellipse cx="56" cy="52" rx="40" ry="38" fill="' + ACCENT + '" opacity=".16"/>' +
      '<circle cx="56" cy="50" r="34" fill="#fff" stroke="#111" stroke-width="3.5"/>' +
      '<path d="M30 28 q10 -14 22 -6 M82 28 q-10 -14 -22 -6" stroke="#111" stroke-width="3" fill="none" stroke-linecap="round"/>' +
      eye + mouth + book + '</svg>';
  }

  function featLine(c) {
    return '귀 ' + c.ear + ' · 꼬리 ' + c.tail + ' · 몸집 ' + c.size + ' · 털 ' + c.coat;
  }

  /* ---------- 나이브 베이즈 ---------- */

  function train(rows) {
    var m = {n:{}, f:{}, total:0};
    var i, k, lab;
    for (i = 0; i < LABELS.length; i++) {
      m.n[LABELS[i]] = 0;
      m.f[LABELS[i]] = {};
      for (k = 0; k < FEATS.length; k++) { m.f[LABELS[i]][FEATS[k]] = {}; }
    }
    for (i = 0; i < rows.length; i++) {
      lab = rows[i].label;
      if (LABELS.indexOf(lab) < 0) { continue; }
      m.n[lab] += 1;
      m.total += 1;
      for (k = 0; k < FEATS.length; k++) {
        var v = rows[i].card[FEATS[k]];
        var box = m.f[lab][FEATS[k]];
        box[v] = (box[v] || 0) + 1;
      }
    }
    return m;
  }

  function score(m, card) {
    var out = {};
    for (var i = 0; i < LABELS.length; i++) {
      var lab = LABELS[i];
      if (m.total === 0) { out[lab] = 0.5; continue; }
      var p = (m.n[lab] + 1) / (m.total + LABELS.length);
      for (var k = 0; k < FEATS.length; k++) {
        var box = m.f[lab][FEATS[k]];
        var hit = box[card[FEATS[k]]] || 0;
        p = p * ((hit + 1) / (m.n[lab] + 2));
      }
      out[lab] = p;
    }
    var sum = out[LABELS[0]] + out[LABELS[1]];
    if (sum <= 0) { return {강아지:0.5, 고양이:0.5}; }
    return {강아지: out["강아지"] / sum, 고양이: out["고양이"] / sum};
  }

  function predict(m, card) {
    var s = score(m, card);
    return {label: s["고양이"] >= s["강아지"] ? "고양이" : "강아지", p: Math.max(s["고양이"], s["강아지"])};
  }

  function evaluate(m) {
    var hit = 0, detail = [];
    for (var i = 0; i < TEST.length; i++) {
      var r = predict(m, TEST[i]);
      var ok = r.label === TEST[i].ans;
      if (ok) { hit++; }
      detail.push({id: TEST[i].id, i: i, got: r.label, ans: TEST[i].ans, ok: ok, p: r.p});
    }
    return {hit: hit, of: TEST.length, pct: Math.round(hit * 100 / TEST.length), detail: detail};
  }

  /* 특징 하나가 어느 쪽으로 얼마나 기울었는지. 몽이의 머릿속을 보여 준다. */
  function tilt(m, card, f) {
    var v = card[f];
    var a = ((m.f["강아지"][f][v] || 0) + 1) / (m.n["강아지"] + 2);
    var b = ((m.f["고양이"][f][v] || 0) + 1) / (m.n["고양이"] + 2);
    var sum = a + b;
    return { cat: sum ? b / sum : 0.5, value: v };
  }

  /* ---------- 상태 ---------- */

  var st = {
    i: 0, pre: 0, preLabel: {}, preWhy: {},
    label: {}, full: null, cut: null, keep: 4, role: {},
    line: "", learned: "", badges: {}, classLabels: null, learning: false
  };

  var REASON = [
    {k:"ear", t:"귀 모양을 보고"},
    {k:"tail", t:"꼬리 길이를 보고"},
    {k:"size", t:"몸집을 보고"},
    {k:"nose", t:"코 색을 보고"}
  ];

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card" style="text-align:center">' + mongSvg("new", 150) +
      '<h2 style="margin-top:10px">몽이가 태어났어요</h2>' +
      '<p style="margin-top:10px">몽이는 아무것도 몰라요. 머릿속이 빈 공책이에요.</p>' +
      '<p style="margin-top:6px">몽이는 <b>사진을 보지 못해요.</b> 카드에 적힌 <b>네 가지</b>만 봐요. 귀, 꼬리, 몸집, 털 색.</p>' +
      '<p style="margin-top:6px">오늘 여러분은 <b>몽이의 선생님</b>이에요. 가르친 대로 몽이가 배웁니다.</p>' +
      '<div class="row" style="justify-content:center;margin-top:16px">' +
      '<button type="button" id="go-hub">교무실로 가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>교무실</h2>' +
      '<p class="muted">다섯 교시를 차례로 해도 되고, 하고 싶은 교시부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-pre">' + wiseIcon("me", 30) +
      '<span>1교시 나라면 어떻게 맞힐까</span><small id="s-pre">사람이 먼저 판단해요</small></button>' +
      '<button type="button" class="tile" id="t-label">' + wiseIcon("write", 30) +
      '<span>2교시 이름표 붙이기</span><small id="s-label">카드 20장</small></button>' +
      '<button type="button" class="tile" id="t-exam">' + wiseIcon("check", 30) +
      '<span>3교시 학습과 시험</span><small id="s-exam">몽이를 가르치고 시험 보기</small></button>' +
      '<button type="button" class="tile" id="t-cut">' + wiseIcon("again", 30) +
      '<span>4교시 편식 실험</span><small id="s-cut">한쪽을 줄이면 어떻게 될까</small></button>' +
      '<button type="button" class="tile" id="t-role">' + wiseIcon("both", 30) +
      '<span>5교시 사람과 AI</span><small id="s-role">누가 무엇을 했나</small></button>' +
      '<button type="button" class="tile" id="t-report">' + wiseIcon("star", 30) +
      '<span>몽이 성적표</span><small id="s-report">오늘의 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("pre",
      '<div class="card"><span class="pill">1교시</span>' +
      '<h2 style="margin-top:10px">나라면 어떻게 맞힐까</h2>' +
      '<p class="muted">몽이를 켜기 전에, 사람인 내가 먼저 판단해 봐요.</p>' +
      '<div id="prebox"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">교무실로</button></div></div>');

    h += q("label",
      '<div class="card"><span class="pill">2교시</span>' +
      '<h2 style="margin-top:10px">카드에 이름표 붙이기</h2>' +
      '<p class="muted">정답은 없어요. 여러분이 붙인 이름표가 몽이의 교과서가 돼요.</p>' +
      '<div id="labelbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="l-prev" class="plain">앞 카드</button>' +
      '<button type="button" id="l-next" class="ghost">다음 카드</button>' +
      '<button type="button" id="l-undo" class="plain">이 카드 지우기</button>' +
      '<span class="muted" id="l-pos"></span></div>' +
      '<div id="classbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="l-peek" class="ghost">우리 반은 어떻게 붙였을까</button>' +
      '<button type="button" class="plain back">교무실로</button></div>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="l-go">3교시로 가기</button></div></div>');

    h += q("exam",
      '<div class="card"><span class="pill">3교시</span>' +
      '<h2 style="margin-top:10px">학습시키고 시험 보기</h2>' +
      '<div id="mong" style="text-align:center;margin:10px 0">' + mongSvg("new", 130) + '</div>' +
      '<div class="row"><button type="button" id="do-train">몽이 학습시키기</button>' +
      '<button type="button" id="do-exam" class="ghost">시험 보기</button></div>' +
      '<div id="exambox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="e-go">4교시로 가기</button>' +
      '<button type="button" class="plain back">교무실로</button></div></div>');

    h += q("cut",
      '<div class="card"><span class="pill">4교시</span>' +
      '<h2 style="margin-top:10px">한쪽 데이터를 줄이면</h2>' +
      '<p class="muted">고양이 카드를 몇 장만 남기고 다시 가르쳐 봐요. 몽이는 어떻게 될까요?</p>' +
      '<label for="keep"><span id="keeptarget">고양이</span> 카드를 <span id="keepnum">4</span>장만 남기기</label>' +
      '<input id="keep" type="range" min="2" max="10" value="4" step="1" style="padding:0">' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="do-cut">줄이고 다시 학습</button></div>' +
      '<div id="cutbox" style="margin-top:12px"></div>' +
      '<label for="cutline">데이터를 줄였더니 어떻게 되었나요</label>' +
      '<input id="cutline" maxlength="80" placeholder="예: 고양이를 자주 틀리게 되었습니다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="c-go">5교시로 가기</button>' +
      '<button type="button" class="plain back">교무실로</button></div></div>');

    h += q("role",
      '<div class="card"><span class="pill">5교시</span>' +
      '<h2 style="margin-top:10px">사람이 한 일과 AI가 한 일</h2>' +
      '<p class="muted">오늘 실제로 있었던 일이에요. 누가 했는지 나눠 봐요.</p>' +
      '<div id="rolebox"></div>' +
      '<label for="learned">몽이를 똑똑하게 만든 것은 무엇인가요</label>' +
      '<input id="learned" maxlength="80" placeholder="예: 이름표를 붙인 우리입니다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="r-go">몽이 성적표 보기</button>' +
      '<button type="button" class="plain back">교무실로</button></div></div>');

    h += q("report",
      '<div class="card"><span class="pill">성적표</span>' +
      '<h2 style="margin-top:10px">몽이 성적표</h2>' +
      '<div id="reportbox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">성적표 그림으로 저장</button>' +
      '<button type="button" class="plain back">교무실로</button></div>' +
      '<div class="note" style="margin-top:12px">정확도는 몽이의 성적이에요. 여러분의 성적이 아니에요.</div>' +
      '<details style="margin-top:12px"><summary class="muted">사진 출처 (CC0 · 퍼블릭 도메인)</summary>' +
      '<div class="scroll" style="margin-top:8px">__CREDITS__</div></details></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.</div>');

    return h;
  }

  /* ---------- 1교시 ---------- */

  function preHtml() {
    if (st.pre >= 3) {
      var h = '<p class="big">세 장을 다 보았어요</p>';
      var count = {};
      for (var k in st.preWhy) {
        if (!st.preWhy.hasOwnProperty(k)) { continue; }
        count[st.preWhy[k]] = (count[st.preWhy[k]] || 0) + 1;
      }
      var rows = [];
      for (var r = 0; r < REASON.length; r++) {
        rows.push({ label: FEAT_NAME[REASON[r].k], value: count[REASON[r].k] || 0 });
      }
      h += wiseBars(rows, 520);
      h += '<p style="margin-top:10px">여러분이 방금 쓴 그 기준을, 이제 몽이에게 가르칩니다.</p>' +
        '<div class="row" style="margin-top:10px"><button type="button" id="pre-go">2교시로 가기</button></div>';
      return h;
    }
    var c = TRAIN[st.pre * 7];
    var h2 = '<p class="muted">' + (st.pre + 1) + ' / 3</p>' +
      '<div style="text-align:center;margin:10px 0">' + petImg(c, true) +
      '<p class="muted">' + esc(featLine(c)) + '</p></div>';
    if (st.preLabel[st.pre] === undefined) {
      h2 += '<div class="row">' +
        '<button type="button" class="chip pk" data-v="강아지" style="width:auto">강아지 같아요</button>' +
        '<button type="button" class="chip pk" data-v="고양이" style="width:auto">고양이 같아요</button></div>';
    } else {
      h2 += '<p class="ok">나는 ' + esc(st.preLabel[st.pre]) + ' 라고 보았어요.</p>' +
        '<label>무엇을 보고 정했나요</label>';
      for (var i = 0; i < REASON.length; i++) {
        h2 += '<button type="button" class="chip rs" data-k="' + REASON[i].k + '">' +
          esc(REASON[i].t) + '</button>';
      }
    }
    return h2;
  }

  function bindPre() {
    $("prebox").innerHTML = preHtml();
    var pks = document.querySelectorAll("#activity .pk");
    for (var i = 0; i < pks.length; i++) {
      pks[i].onclick = function () {
        st.preLabel[st.pre] = this.getAttribute("data-v");
        bindPre();
      };
    }
    var rss = document.querySelectorAll("#activity .rs");
    for (var j = 0; j < rss.length; j++) {
      rss[j].onclick = function () {
        st.preWhy[st.pre] = this.getAttribute("data-k");
        st.pre += 1;
        bindPre();
        paintHub();
      };
    }
    if ($("pre-go")) { $("pre-go").onclick = function () { wiseGo("label"); }; }
  }

  /* ---------- 2교시 ---------- */

  function labelHtml() {
    var c = TRAIN[st.i];
    var mine = st.label[c.id];
    var h = '<div style="text-align:center;margin:6px 0">' + petImg(c, true) +
      '<p class="muted">' + esc(featLine(c)) + '</p></div>' +
      '<div class="row" style="justify-content:center">' +
      '<button type="button" class="chip lb' + (mine === "강아지" ? " on" : "") +
      '" data-v="강아지" style="width:auto">강아지 이름표</button>' +
      '<button type="button" class="chip lb' + (mine === "고양이" ? " on" : "") +
      '" data-v="고양이" style="width:auto">고양이 이름표</button></div>';
    h += '<div style="margin-top:12px">' + barHtml(countLabel(), TRAIN.length) + '</div>' +
      '<p class="muted" style="margin-top:6px">배움 상자 ' + countLabel() + ' / ' + TRAIN.length + '장</p>';
    return h;
  }

  function countLabel() {
    var n = 0;
    for (var k in st.label) { if (st.label.hasOwnProperty(k) && st.label[k]) { n++; } }
    return n;
  }

  function bindLabel() {
    $("labelbox").innerHTML = labelHtml();
    if (slow()) {
      var pic = $("labelbox").querySelector(".pet");
      if (pic) {
        pic.style.animation = "wfade .3s cubic-bezier(.22,.61,.36,1) both";
      }
    }
    if ($("l-pos")) { $("l-pos").textContent = (st.i + 1) + " / " + TRAIN.length; }
    var lbs = document.querySelectorAll("#activity .lb");
    for (var i = 0; i < lbs.length; i++) {
      lbs[i].onclick = function () {
        st.label[TRAIN[st.i].id] = this.getAttribute("data-v");
        if (st.i < TRAIN.length - 1) { st.i += 1; }
        bindLabel();
        paintHub();
        if (countLabel() === TRAIN.length) {
          award("성실한 선생님");
          wiseToast("이름표 스무 장을 다 붙였어요. 3교시로 가 볼까요?");
        }
      };
    }
  }

  function peekLabels() {
    if (me.solo) {
      $("classbox").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 기록이 없어요. ' +
        '이름표 붙이기와 실험은 그대로 해 볼 수 있어요.</p>';
      return;
    }
    $("classbox").innerHTML = wiseSpinner("우리 반 기록을 불러오는 중이에요") + wiseSkeleton(2);
    dbGet(me.room + "/entries").then(function (data) {
      var tally = {};
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var lab = (data[k].payload || {}).labels || {};
        for (var id in lab) {
          if (!lab.hasOwnProperty(id)) { continue; }
          if (!tally[id]) { tally[id] = {강아지: 0, 고양이: 0}; }
          tally[id][lab[id]] += 1;
        }
      }
      st.classLabels = tally;
      $("classbox").innerHTML = classHtml(tally);
      paintHub();
    })["catch"](function () {
      $("classbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function classHtml(tally) {
    var rows = [];
    for (var id in tally) {
      if (!tally.hasOwnProperty(id)) { continue; }
      var t = tally[id], sum = t["강아지"] + t["고양이"];
      if (!sum) { continue; }
      rows.push({ id: id, dog: t["강아지"], cat: t["고양이"],
        gap: Math.abs(t["강아지"] - t["고양이"]) / sum });
    }
    if (!rows.length) { return '<p class="muted">아직 우리 반 이름표가 모이지 않았어요.</p>'; }
    rows.sort(function (a, b) { return a.gap - b.gap; });
    var h = '<h3>우리 반에서 갈린 카드</h3>' +
      '<p class="muted">같은 카드인데 이름표가 갈렸어요. 누가 맞고 틀린 게 아니라 기준이 다른 거예요.</p>' +
      '<div class="scroll"><table><tr><th>카드</th><th>강아지</th><th>고양이</th><th>내 이름표</th></tr>';
    for (var i = 0; i < rows.length && i < 5; i++) {
      var c = TRAIN[Number(rows[i].id)];
      h += "<tr><td>" + (c ? esc(featLine(c)) : rows[i].id) + "</td><td>" + rows[i].dog +
        "</td><td>" + rows[i].cat + "</td><td>" + esc(st.label[rows[i].id] || "-") + "</td></tr>";
    }
    return h + "</table></div>";
  }

  /* ---------- 3교시 ---------- */

  function rows(only) {
    var out = [];
    for (var i = 0; i < TRAIN.length; i++) {
      var lab = st.label[TRAIN[i].id];
      if (!lab) { continue; }
      if (only && lab === "고양이" && out.catCount === undefined) { /* 자리 표시 */ }
      out.push({ card: TRAIN[i], label: lab });
    }
    return out;
  }

  /* 굶길 쪽은 학생이 더 많이 붙인 이름표로 정한다. 그래야 결과가 실제로 무너진다. */
  function starveTarget() {
    var n = {강아지: 0, 고양이: 0};
    for (var k in st.label) {
      if (st.label.hasOwnProperty(k) && st.label[k]) { n[st.label[k]] += 1; }
    }
    return n["고양이"] >= n["강아지"] ? "고양이" : "강아지";
  }

  function starvedRows(keep) {
    var target = starveTarget(), seen = 0, out = [];
    for (var i = 0; i < TRAIN.length; i++) {
      var lab = st.label[TRAIN[i].id];
      if (!lab) { continue; }
      if (lab === target) {
        seen += 1;
        if (seen > keep) { continue; }
      }
      out.push({ card: TRAIN[i], label: lab });
    }
    return out;
  }

  /* 기다리는 시간을 만든다. 결과가 순식간에 튀어나오면 무슨 일이 있었는지 안 보인다.
     움직임을 줄이도록 설정한 기기에서는 기다리지 않는다. */
  function slow() {
    try {
      return !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) { return true; }
  }

  function after(ms, fn) { setTimeout(fn, slow() ? ms : 0); }

  /* 한 장씩 차례로 나타나게 한다. 골격의 wfade 를 그대로 쓴다. */
  function stagger(box, step) {
    if (!box || !slow()) { return; }
    var kids = box.children, gap = step || 90;
    for (var i = 0; i < kids.length; i++) {
      kids[i].style.animation = "wfade .34s cubic-bezier(.22,.61,.36,1) both";
      kids[i].style.animationDelay = (i * gap) + "ms";
    }
  }

  function doTrain() {
    if (countLabel() < 6) {
      wiseToast("이름표를 여섯 장 넘게 붙인 뒤에 학습할 수 있어요.");
      return;
    }
    st.learning = true;
    wiseButtonBusy($("do-train"), true, "가르치는 중");
    $("mong").innerHTML = mongSvg("learn", 130) +
      wiseSpinner("몽이가 카드를 한 장씩 보는 중이에요", true) +
      '<div style="max-width:320px;margin:0 auto">' + barHtml(0, countLabel()) + '</div>';
    var seen = 0, total = countLabel(), box = $("mong");
    var tick = setInterval(function () {
      seen += 1;
      var bar = box.querySelector(".bar > i");
      if (bar) { bar.style.width = Math.min(100, Math.round(seen * 100 / total)) + "%"; }
      if (seen >= total) { clearInterval(tick); }
    }, slow() ? Math.max(40, Math.round(1100 / Math.max(total, 1))) : 1);
    after(1300, function () { clearInterval(tick); finishTrain(); });
  }

  function finishTrain() {
    var m = train(rows());
    st.full = evaluate(m);
    st.full.model = m;
    st.learning = false;
    wiseButtonBusy($("do-train"), false);
    $("mong").innerHTML = mongSvg(st.full.pct >= 60 ? "happy" : "sad", 130) +
      '<p class="muted">' + (st.full.pct >= 60 ? "배웠어요. 시험 볼 준비가 됐어요." : "아직 헷갈려요. 시험을 봐 볼까요?") + '</p>';
    var n = {강아지: 0, 고양이: 0};
    for (var k in st.label) {
      if (st.label.hasOwnProperty(k) && st.label[k]) { n[st.label[k]] += 1; }
    }
    var tip = '<p class="muted">학습을 마쳤어요. 시험 보기를 눌러요.</p>';
    if (n["강아지"] < 3 || n["고양이"] < 3) {
      tip += '<p class="warn">이름표가 한쪽으로 몰렸어요. 몽이는 한쪽만 배웠어요. ' +
        '2교시로 돌아가 다른 쪽 이름표도 붙여 보면 어떤 일이 생길까요?</p>';
    }
    $("exambox").innerHTML = tip;
    paintHub();
  }

  function examHtml() {
    if (!st.full) { return '<p class="muted">먼저 몽이를 학습시켜요.</p>'; }
    var r = st.full;
    var h = '<p class="big">' + r.pct + '점</p>' +
      '<p class="muted">시험 카드 ' + r.of + '장 가운데 ' + r.hit + '장을 맞혔어요.</p>' +
      barHtml(r.hit, r.of);
    h += '<h3 style="margin-top:16px">몽이의 답과 머릿속</h3>';
    for (var i = 0; i < r.detail.length; i++) {
      var d = r.detail[i], c = TEST[d.i];
      h += '<div class="card" style="margin:10px 0;padding:14px">' +
        '<div class="iconrow">' + petImg(c, false) +
        '<div><p style="font-weight:700">몽이 : ' + esc(d.got) + ' (' + Math.round(d.p * 100) + '%)</p>' +
        '<p class="' + (d.ok ? "ok" : "warn") + '">' + (d.ok ? "맞았어요" : "틀렸어요. 정답은 " + esc(d.ans)) + '</p>' +
        '<p class="muted">' + esc(featLine(c)) + '</p></div></div>';
      h += '<div class="scroll" style="margin-top:8px"><table><tr><th>특징</th><th>몽이가 기운 쪽</th><th></th></tr>';
      for (var k = 0; k < FEATS.length; k++) {
        var t = tilt(st.full.model, c, FEATS[k]);
        var pctCat = Math.round(t.cat * 100);
        h += "<tr><td>" + esc(FEAT_NAME[FEATS[k]]) + " " + esc(t.value) + "</td><td>고양이 " +
          pctCat + "%</td><td>" + barHtml(pctCat, 100) + "</td></tr>";
      }
      h += "</table></div></div>";
    }
    return h;
  }

  /* ---------- 4교시 ---------- */

  function doCut() {
    if (!st.full) { wiseToast("3교시에서 먼저 학습과 시험을 마쳐요."); return; }
    st.keep = Number($("keep").value);
    wiseButtonBusy($("do-cut"), true, "다시 가르치는 중");
    $("cutbox").innerHTML = wiseSpinner("카드를 빼고 처음부터 다시 배우는 중이에요", true) + wiseSkeleton(2);
    after(1100, function () {
      var m = train(starvedRows(st.keep));
      st.cut = evaluate(m);
      st.cut.keep = st.keep;
      st.cut.target = starveTarget();
      award("실험가");
      wiseButtonBusy($("do-cut"), false);
      $("cutbox").innerHTML = cutHtml();
      stagger($("cutbox"), 110);
      paintHub();
    });
  }

  function cutHtml() {
    if (!st.cut) { return '<p class="muted">슬라이더를 옮기고 다시 학습을 눌러요.</p>'; }
    var h = wiseBars([
      { label: "전체 학습", value: st.full.pct, color: "#16a34a" },
      { label: "편식 학습", value: st.cut.pct, color: "#dc2626" }
    ], 520);
    h += '<p style="margin-top:10px">' + esc(st.cut.target || "고양이") + ' 카드를 <b>' +
      st.cut.keep + '장</b>만 남겼더니 ' + st.full.pct + '점에서 <b>' + st.cut.pct +
      '점</b>이 되었어요.</p>';
    if (st.cut.pct === st.full.pct) {
      h += '<p class="muted">점수가 그대로예요. 더 줄여 보거나, 2교시로 돌아가 이름표를 고르게 붙여 봐요.</p>';
    }
    var wrong = [];
    for (var i = 0; i < st.cut.detail.length; i++) {
      if (!st.cut.detail[i].ok) { wrong.push(st.cut.detail[i]); }
    }
    if (wrong.length) {
      h += '<h3 style="margin-top:14px">틀린 카드</h3><div class="row">';
      for (var k = 0; k < wrong.length; k++) {
        var c = TEST[wrong[k].i];
        h += '<div class="card" style="margin:0;padding:10px;text-align:center;width:150px">' +
          petImg(c, false) + '<p class="muted" style="font-size:12px">정답 ' + esc(wrong[k].ans) +
          '<br>몽이 ' + esc(wrong[k].got) + '</p></div>';
      }
      h += '</div>';
      h += '<p class="muted" style="margin-top:8px">틀린 카드가 한쪽으로 몰려 있나요? 왜 그럴까요?</p>';
    } else {
      h += '<p class="ok" style="margin-top:10px">이번에는 다 맞혔어요. 더 줄여 볼까요?</p>';
    }
    return h;
  }

  /* ---------- 5교시 ---------- */

  function roleHtml() {
    var h = "";
    for (var i = 0; i < ROLE_ITEMS.length; i++) {
      h += '<div class="card" style="margin:8px 0;padding:12px">' +
        '<p style="margin:0 0 8px;font-weight:600">' + esc(ROLE_ITEMS[i]) + '</p><div class="row">' +
        '<button type="button" class="chip rl' + (st.role[i] === "사람" ? " on" : "") +
        '" data-i="' + i + '" data-v="사람" style="width:auto;margin:0">' + wiseIcon("me", 22) + '사람</button>' +
        '<button type="button" class="chip rl' + (st.role[i] === "AI" ? " on" : "") +
        '" data-i="' + i + '" data-v="AI" style="width:auto;margin:0">' + wiseIcon("ai", 22) + '몽이(AI)</button>' +
        '</div></div>';
    }
    return h;
  }

  function bindRole() {
    $("rolebox").innerHTML = roleHtml();
    var rls = document.querySelectorAll("#activity .rl");
    for (var i = 0; i < rls.length; i++) {
      rls[i].onclick = function () {
        st.role[this.getAttribute("data-i")] = this.getAttribute("data-v");
        bindRole();
        paintHub();
      };
    }
  }

  function roleCount() {
    var n = 0;
    for (var k in st.role) { if (st.role.hasOwnProperty(k)) { n++; } }
    return n;
  }

  /* ---------- 성적표 ---------- */

  function reportHtml() {
    var dog = 0, cat = 0;
    for (var k in st.label) {
      if (!st.label.hasOwnProperty(k)) { continue; }
      if (st.label[k] === "강아지") { dog++; } else if (st.label[k] === "고양이") { cat++; }
    }
    var h = '<div style="text-align:center">' + mongSvg(st.full && st.full.pct >= 60 ? "happy" : "new", 120) + '</div>';
    h += '<div class="scroll"><table>' +
      '<tr><th>이름표</th><td>강아지 ' + dog + '장 · 고양이 ' + cat + '장</td></tr>' +
      '<tr><th>전체 학습</th><td>' + (st.full ? st.full.pct + '점' : '아직') + '</td></tr>' +
      '<tr><th>편식 학습</th><td>' + (st.cut ? st.cut.pct + '점 (' + (st.cut.target || "고양이") +
        ' ' + st.cut.keep + '장)' : '아직') + '</td></tr>' +
      '<tr><th>역할 나누기</th><td>' + roleCount() + ' / ' + ROLE_ITEMS.length + '개</td></tr>' +
      '</table></div>';
    h += '<label for="report-line">오늘 배운 것을 한 줄로</label>' +
      '<input id="report-line" maxlength="80" placeholder="예: 데이터를 누가 주느냐에 따라 AI가 달라진다" value="' +
      esc(st.line) + '">';
    return h;
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
    paintHub();
  }

  function paintHub() {
    if (!$("s-label")) { return; }
    $("s-pre").textContent = st.pre >= 3 ? "세 장을 다 판단했어요" : "사람이 먼저 판단해요";
    $("s-label").textContent = "이름표 " + countLabel() + " / " + TRAIN.length + "장";
    $("s-exam").textContent = st.full ? ("정확도 " + st.full.pct + "점") : "몽이를 가르치고 시험 보기";
    $("s-cut").textContent = st.cut ? ("편식 정확도 " + st.cut.pct + "점") : "한쪽을 줄이면 어떻게 될까";
    $("s-role").textContent = "나눈 항목 " + roleCount() + " / " + ROLE_ITEMS.length + "개";
    $("s-report").textContent = "오늘의 기록";
    var tiles = [["t-pre", st.pre >= 3], ["t-label", countLabel() >= TRAIN.length],
      ["t-exam", !!st.full], ["t-cut", !!st.cut], ["t-role", roleCount() >= 5], ["t-report", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }
    var names = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { names.push(b); } }
    $("badges").innerHTML = names.length
      ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
      : '<span class="muted">아직 없어요. 이름표를 붙이면 받을 수 있어요.</span>';
    wiseHud([
      { label: "이름표", done: countLabel(), total: TRAIN.length },
      { label: "정확도", done: st.full ? st.full.pct : 0, total: 100 },
      { label: "역할 나누기", done: roleCount(), total: ROLE_ITEMS.length }
    ]);
  }

  /* ---------- 흐름 ---------- */

  function activityEnter(id) {
    if (id === "pre") { bindPre(); }
    if (id === "label") { bindLabel(); }
    if (id === "exam") { $("exambox").innerHTML = examHtml(); }
    if (id === "cut") {
      if ($("keeptarget")) { $("keeptarget").textContent = starveTarget(); }
      $("cutbox").innerHTML = cutHtml();
    }
    if (id === "role") { bindRole(); }
    if (id === "report") { $("reportbox").innerHTML = reportHtml(); }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.labels) { st.label = saved.labels; }
      if (saved.roles) { st.role = saved.roles; }
      if (saved.line) { st.line = saved.line; }
    }
    $("go-hub").onclick = function () { wiseGo("hub"); };
    $("t-pre").onclick = function () { wiseGo("pre"); };
    $("t-label").onclick = function () { wiseGo("label"); };
    $("t-exam").onclick = function () { wiseGo("exam"); };
    $("t-cut").onclick = function () { wiseGo("cut"); };
    $("t-role").onclick = function () { wiseGo("role"); };
    $("t-report").onclick = function () { wiseGo("report"); };
    $("l-prev").onclick = function () { if (st.i > 0) { st.i -= 1; bindLabel(); } };
    $("l-next").onclick = function () { if (st.i < TRAIN.length - 1) { st.i += 1; bindLabel(); } };
    $("l-undo").onclick = function () {
      st.label[TRAIN[st.i].id] = "";
      bindLabel();
      paintHub();
    };
    $("l-peek").onclick = peekLabels;
    $("l-go").onclick = function () {
      if (countLabel() < 6) {
        wiseToast("이름표를 여섯 장 넘게 붙인 뒤에 3교시로 가요.");
        return;
      }
      if (countLabel() < TRAIN.length) {
        wiseToast("아직 " + (TRAIN.length - countLabel()) + "장 남았어요. 3교시에서 언제든 돌아올 수 있어요.");
      }
      wiseGo("exam");
    };
    $("e-go").onclick = function () {
      if (!st.full) { wiseToast("먼저 몽이를 학습시키고 시험을 봐요."); return; }
      wiseGo("cut");
    };
    $("c-go").onclick = function () { wiseGo("role"); };
    $("r-go").onclick = function () { wiseGo("report"); };
    $("do-train").onclick = doTrain;
    $("do-exam").onclick = function () {
      if (!st.full) { wiseToast("먼저 몽이를 학습시켜요."); return; }
      wiseButtonBusy($("do-exam"), true, "채점 중");
      $("exambox").innerHTML = wiseSpinner("몽이가 시험 카드를 푸는 중이에요", true) + wiseSkeleton(3);
      after(900, function () {
        wiseButtonBusy($("do-exam"), false);
        $("exambox").innerHTML = examHtml();
        stagger($("exambox"), 110);
        if (st.full.pct >= 80) { award("좋은 선생님"); }
      });
    };
    $("keep").oninput = function () { $("keepnum").textContent = this.value; };
    $("do-cut").onclick = doCut;
    $("save-card").onclick = function () {
      wiseCardPng("몽이 성적표 · " + me.nick, [
        "이름표 " + countLabel() + "장을 붙였어요",
        "전체 학습 " + (st.full ? st.full.pct : 0) + "점",
        "편식 학습 " + (st.cut ? st.cut.pct + "점 (" + (st.cut.target || "고양이") + " " +
          st.cut.keep + "장)" : "안 함"),
        val("report-line") || "오늘 나는 몽이의 선생님이었다"
      ], "wise_l01_" + me.nick);
      award("생각 기록자");
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }
    wiseNote("몽이는 여러분이 가르친 대로 배워요. 이름표부터 붙여 볼까요?");
    wiseGo("story");
    paintHub();
  }

  function val(id) { return $(id) ? $(id).value.trim() : ""; }

  function activityDraft() {
    return { labels: st.label, roles: st.role, line: val("cutline") };
  }

  function activityAutofill() {
    for (var i = 0; i < TRAIN.length; i++) {
      st.label[TRAIN[i].id] = TRAIN[i].ear === "뾰족" ? "고양이" : "강아지";
    }
    var m = train(rows());
    st.full = evaluate(m);
    st.full.model = m;
    st.cut = evaluate(train(starvedRows(2)));
    st.cut.keep = 2;
    for (var r = 0; r < ROLE_ITEMS.length; r++) { st.role[r] = r % 3 === 0 ? "AI" : "사람"; }
    st.pre = 3;
  }

  function activityCollect() {
    if (countLabel() < 10) {
      $("w-msg").innerHTML = '<span class="warn">이름표를 열 장 넘게 붙인 뒤에 제출해요. 지금 ' +
        countLabel() + '장이에요.</span>';
      return null;
    }
    if (!st.full) {
      $("w-msg").innerHTML = '<span class="warn">3교시에서 몽이를 학습시키고 시험을 봐 주세요.</span>';
      return null;
    }
    var badges = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { badges.push(b); } }
    wiseCelebrate("오늘의 수업을 마쳤어요", [
      "이름표 <b>" + countLabel() + "장</b>으로 몽이를 가르쳤어요",
      "전체 학습 <b>" + st.full.pct + "점</b>" +
        (st.cut ? " · 편식 학습 <b>" + st.cut.pct + "점</b>" : ""),
      "몽이는 배운 대로만 답해요.",
      "다음 시간에는 몽이가 지어낸 말을 잡아 봅니다."
    ], "좋아요");
    return {
      pre: { picks: st.preLabel, reasons: st.preWhy },
      labels: st.label,
      acc: { full: st.full.pct, starved: st.cut ? st.cut.pct : null, keep: st.cut ? st.cut.keep : null },
      wrong: (st.cut ? st.cut.detail : st.full.detail).filter(function (d) { return !d.ok; })
        .map(function (d) { return d.id; }),
      roles: st.role, line: val("cutline"),
      learned: val("learned") || val("report-line"),
      badges: badges, labeled: countLabel()
    };
  }

  /* ---------- 교사 화면 ---------- */

  function teacherSummary(list) {
    var full = 0, cut = 0, nFull = 0, nCut = 0, tally = {};
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (p.acc && p.acc.full !== undefined && p.acc.full !== null) { full += p.acc.full; nFull++; }
      if (p.acc && p.acc.starved !== undefined && p.acc.starved !== null) { cut += p.acc.starved; nCut++; }
      var lab = p.labels || {};
      for (var id in lab) {
        if (!lab.hasOwnProperty(id) || !lab[id]) { continue; }
        if (!tally[id]) { tally[id] = {강아지: 0, 고양이: 0}; }
        tally[id][lab[id]] += 1;
      }
    }
    var h = wiseBars([
      { label: "전체 학습 평균", value: nFull ? Math.round(full / nFull) : 0, color: "#16a34a" },
      { label: "편식 학습 평균", value: nCut ? Math.round(cut / nCut) : 0, color: "#dc2626" }
    ], 560);

    var rows2 = [];
    for (var id2 in tally) {
      if (!tally.hasOwnProperty(id2)) { continue; }
      var t = tally[id2], sum = t["강아지"] + t["고양이"];
      if (!sum) { continue; }
      rows2.push({ id: id2, dog: t["강아지"], cat: t["고양이"], gap: Math.abs(t["강아지"] - t["고양이"]) / sum });
    }
    rows2.sort(function (a, b) { return a.gap - b.gap; });
    h += '<h3 style="margin-top:16px">이름표가 갈린 카드</h3>' +
      '<p class="muted">3차시 편향 수업의 재료입니다. 왜 갈렸는지 물어봅니다.</p>' +
      '<div class="scroll"><table><tr><th>카드</th><th>강아지</th><th>고양이</th></tr>';
    for (var r = 0; r < rows2.length && r < 5; r++) {
      var c = TRAIN[Number(rows2[r].id)];
      h += "<tr><td>" + (c ? esc(featLine(c)) : rows2[r].id) + "</td><td>" + rows2[r].dog +
        "</td><td>" + rows2[r].cat + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:16px">학생 기록</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>이름표</th><th>전체</th><th>편식</th><th>배움 문장</th></tr>';
    for (var k = 0; k < list.length; k++) {
      var q2 = list[k].payload || {};
      h += "<tr><td>" + esc(list[k].nick) + "</td><td>" + (q2.labeled || 0) + "장</td><td>" +
        ((q2.acc && q2.acc.full !== undefined) ? q2.acc.full : "-") + "</td><td>" +
        ((q2.acc && q2.acc.starved !== null && q2.acc.starved !== undefined) ? q2.acc.starved : "-") +
        "</td><td>" + esc(q2.learned || "") + "</td></tr>";
    }
    return h + "</table></div>";
  }

  function presentHtml(list) {
    var full = 0, cut = 0, nFull = 0, nCut = 0;
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (p.acc && p.acc.full !== undefined && p.acc.full !== null) { full += p.acc.full; nFull++; }
      if (p.acc && p.acc.starved !== undefined && p.acc.starved !== null) { cut += p.acc.starved; nCut++; }
    }
    var h = '<p class="big">전체 ' + (nFull ? Math.round(full / nFull) : 0) + '점 · 편식 ' +
      (nCut ? Math.round(cut / nCut) : 0) + '점</p>' +
      '<p class="muted">우리 반 몽이들의 평균이에요. 같은 방법인데 데이터만 달랐어요.</p>';
    h += wiseBars([
      { label: "전체 학습", value: nFull ? Math.round(full / nFull) : 0, color: "#16a34a" },
      { label: "편식 학습", value: nCut ? Math.round(cut / nCut) : 0, color: "#dc2626" }
    ], 700);
    h += '<h3 style="margin-top:18px">우리 반이 쓴 배움 문장</h3>';
    for (var k = 0; k < list.length && k < 6; k++) {
      var q3 = list[k].payload || {};
      if (!q3.learned) { continue; }
      h += '<p style="font-size:22px;margin:8px 0">' + esc(q3.learned) + '</p>';
    }
    return h;
  }
"""


def _photos_js():
    """assets/pets 의 사진을 data URI 로 만들어 준다. 외부 파일을 부르지 않는다."""
    import base64, io as _io, json as _json, os
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "..", "assets", "pets")
    cred = _json.load(_io.open(os.path.join(d, "credits.json"), encoding="utf-8"))
    out = []
    for c in cred:
        raw = open(os.path.join(d, c["key"] + ".jpg"), "rb").read()
        out.append('"%s":"data:image/jpeg;base64,%s"' % (c["key"], base64.b64encode(raw).decode("ascii")))
    return "{" + ",".join(out) + "}"


def _credits_html():
    """사진 출처 표. CC0 와 퍼블릭 도메인만 쓴다."""
    import io as _io, json as _json, os
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "..", "assets", "pets")
    cred = _json.load(_io.open(os.path.join(d, "credits.json"), encoding="utf-8"))
    rows = ["<table><tr><th>카드</th><th>사진</th><th>만든 사람</th><th>이용 허락</th></tr>"]
    for i, c in enumerate(cred):
        who = c["creator"] or "이름 없음"
        lic = "CC0" if c["license"] == "cc0" else "퍼블릭 도메인"
        rows.append("<tr><td>%d</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (i + 1, c["title"].replace('"', "'")[:40], who.replace('"', "'"), lic))
    rows.append("</table>")
    return "".join(rows)


ACTIVITY = ACTIVITY.replace("__PHOTOS__", _photos_js()).replace("__CREDITS__", _credits_html())
