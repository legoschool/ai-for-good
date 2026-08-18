# -*- coding: utf-8 -*-
"""1차시 데이터 실험실.

브라우저 안에서 실제로 도는 분류기다. 외부 라이브러리를 쓰지 않는다.
학생이 카드에 라벨을 붙이면 그 라벨로 나이브 베이즈가 학습하고,
시험 카드로 정확도를 재고, 한쪽 데이터를 줄이면 결과가 무너지는 것을 보여 준다.

40분을 다섯 단계로 나눈다. 4 + 10 + 11 + 10 + 5 분.
"""

ACTIVITY = u"""
  /* ---------- 카드 더미 ---------- */
  /* 특징 네 가지로만 이루어진 카드다. 정답을 적어 두지 않는다.
     이름표를 붙이는 것은 사람의 판단이라는 점이 이 차시의 핵심이다. */

  var TRAIN = [
    {id:0,  ear:"뾰족", tail:"길다", size:"작다", nose:"분홍"},
    {id:1,  ear:"처짐", tail:"짧다", size:"크다", nose:"검정"},
    {id:2,  ear:"뾰족", tail:"길다", size:"작다", nose:"검정"},
    {id:3,  ear:"처짐", tail:"길다", size:"크다", nose:"검정"},
    {id:4,  ear:"뾰족", tail:"짧다", size:"작다", nose:"분홍"},
    {id:5,  ear:"처짐", tail:"짧다", size:"크다", nose:"분홍"},
    {id:6,  ear:"뾰족", tail:"길다", size:"크다", nose:"분홍"},
    {id:7,  ear:"처짐", tail:"길다", size:"작다", nose:"검정"},
    {id:8,  ear:"뾰족", tail:"짧다", size:"작다", nose:"검정"},
    {id:9,  ear:"처짐", tail:"짧다", size:"크다", nose:"검정"},
    {id:10, ear:"뾰족", tail:"길다", size:"작다", nose:"분홍"},
    {id:11, ear:"처짐", tail:"길다", size:"크다", nose:"분홍"},
    {id:12, ear:"뾰족", tail:"짧다", size:"크다", nose:"검정"},
    {id:13, ear:"처짐", tail:"짧다", size:"작다", nose:"분홍"},
    {id:14, ear:"뾰족", tail:"길다", size:"작다", nose:"검정"},
    {id:15, ear:"처짐", tail:"길다", size:"크다", nose:"검정"},
    {id:16, ear:"뾰족", tail:"짧다", size:"작다", nose:"분홍"},
    {id:17, ear:"처짐", tail:"짧다", size:"크다", nose:"분홍"},
    {id:18, ear:"뾰족", tail:"길다", size:"크다", nose:"검정"},
    {id:19, ear:"처짐", tail:"길다", size:"작다", nose:"분홍"}
  ];

  /* 시험 카드에는 답이 정해져 있다. 앞의 넷은 분명하고 뒤의 둘은 애매하다. */
  var TEST = [
    {id:100, ear:"뾰족", tail:"길다", size:"작다", nose:"분홍", ans:"고양이"},
    {id:101, ear:"처짐", tail:"짧다", size:"크다", nose:"검정", ans:"강아지"},
    {id:102, ear:"뾰족", tail:"짧다", size:"작다", nose:"검정", ans:"고양이"},
    {id:103, ear:"처짐", tail:"길다", size:"크다", nose:"분홍", ans:"강아지"},
    {id:104, ear:"뾰족", tail:"길다", size:"크다", nose:"분홍", ans:"고양이"},
    {id:105, ear:"처짐", tail:"짧다", size:"작다", nose:"검정", ans:"강아지"}
  ];

  var FEATS = ["ear", "tail", "size", "nose"];
  var FEAT_NAME = {ear:"귀 모양", tail:"꼬리 길이", size:"몸집", nose:"코 색"};
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

  /* ---------- 카드 그리기 ---------- */

  function faceSvg(c, big) {
    var r = c.size === "크다" ? 30 : 23;
    var w = big ? 132 : 108;
    var noseColor = c.nose === "검정" ? "#222" : "#F58AA8";
    var ears = c.ear === "뾰족"
      ? '<path d="M' + (50 - r * 0.8) + ' ' + (52 - r * 0.55) + ' L' + (50 - r * 0.95) + ' ' + (50 - r * 1.5) +
        ' L' + (50 - r * 0.15) + ' ' + (52 - r * 0.9) + ' Z" fill="#F2C48A" stroke="#111" stroke-width="3" stroke-linejoin="round"/>' +
        '<path d="M' + (50 + r * 0.8) + ' ' + (52 - r * 0.55) + ' L' + (50 + r * 0.95) + ' ' + (50 - r * 1.5) +
        ' L' + (50 + r * 0.15) + ' ' + (52 - r * 0.9) + ' Z" fill="#F2C48A" stroke="#111" stroke-width="3" stroke-linejoin="round"/>'
      : '<ellipse cx="' + (50 - r * 0.92) + '" cy="' + (54 + r * 0.15) + '" rx="' + (r * 0.34) + '" ry="' + (r * 0.72) +
        '" fill="#D9A06A" stroke="#111" stroke-width="3"/>' +
        '<ellipse cx="' + (50 + r * 0.92) + '" cy="' + (54 + r * 0.15) + '" rx="' + (r * 0.34) + '" ry="' + (r * 0.72) +
        '" fill="#D9A06A" stroke="#111" stroke-width="3"/>';
    var tail = c.tail === "길다"
      ? '<path d="M78 76 q22 -6 16 -30" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>'
      : '<path d="M78 76 q10 -3 9 -12" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>';
    return '<svg viewBox="0 0 100 100" width="' + w + '" height="' + w + '" aria-hidden="true">' +
      tail + ears +
      '<circle cx="50" cy="56" r="' + r + '" fill="#FBE3C2" stroke="#111" stroke-width="3.5"/>' +
      '<circle cx="' + (50 - r * 0.36) + '" cy="' + (56 - r * 0.16) + '" r="3.6" fill="#111"/>' +
      '<circle cx="' + (50 + r * 0.36) + '" cy="' + (56 - r * 0.16) + '" r="3.6" fill="#111"/>' +
      '<ellipse cx="50" cy="' + (58 + r * 0.28) + '" rx="5" ry="4" fill="' + noseColor + '" stroke="#111" stroke-width="2"/>' +
      '</svg>';
  }

  function featLine(c) {
    return '귀 ' + c.ear + ' · 꼬리 ' + c.tail + ' · 몸집 ' + c.size + ' · 코 ' + c.nose;
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
      detail.push({id: TEST[i].id, got: r.label, ans: TEST[i].ans, ok: ok, p: r.p});
    }
    return {hit: hit, of: TEST.length, detail: detail};
  }

  /* 어떤 특징이 판단을 가장 크게 갈랐는지 본다 */
  function evidence(m) {
    var out = [];
    for (var k = 0; k < FEATS.length; k++) {
      var f = FEATS[k], gap = 0, vals = {};
      for (var i = 0; i < TRAIN.length; i++) { vals[TRAIN[i][f]] = 1; }
      for (var v in vals) {
        if (!vals.hasOwnProperty(v)) { continue; }
        var a = ((m.f["강아지"][f][v] || 0) + 1) / (m.n["강아지"] + 2);
        var b = ((m.f["고양이"][f][v] || 0) + 1) / (m.n["고양이"] + 2);
        gap = Math.max(gap, Math.abs(a - b));
      }
      out.push({f: f, name: FEAT_NAME[f], gap: gap});
    }
    out.sort(function (x, y) { return y.gap - x.gap; });
    return out;
  }

  /* ---------- 상태 ---------- */

  var step = 1;
  var STEPS = [
    {no:1, t:"나라면 어떻게 맞힐까", m:4},
    {no:2, t:"카드에 이름표 붙이기", m:10},
    {no:3, t:"학습시키고 시험 보기", m:11},
    {no:4, t:"한쪽 데이터를 줄이면", m:10},
    {no:5, t:"사람이 한 일, AI가 한 일", m:5}
  ];
  var guess = {};      /* 1단계 학생 예측 */
  var label = {};      /* 2단계 라벨 */
  var full = null;     /* 3단계 결과 */
  var cut = null;      /* 4단계 결과 */
  var keepCat = 3;
  var role = {};       /* 5단계 분류 */

  /* ---------- 화면 ---------- */

  function activityHtml() {
    var h = '<div class="card"><div class="row" id="stepbar"></div>' +
      '<p class="muted" id="steptip" style="margin-top:8px"></p></div>' +
      '<div id="stage1"></div><div id="stage2"></div><div id="stage3"></div>' +
      '<div id="stage4"></div><div id="stage5"></div>' +
      '<div class="card"><div class="row">' +
      '<button type="button" id="prevStep" class="plain" style="width:auto">이전 단계</button>' +
      '<button type="button" id="nextStep" class="ghost" style="width:auto">다음 단계</button>' +
      '</div></div>';
    return h;
  }

  function stepBar() {
    var h = "";
    for (var i = 0; i < STEPS.length; i++) {
      var s = STEPS[i];
      h += '<button type="button" class="chip stepbtn' + (step === s.no ? " on" : "") +
        '" data-s="' + s.no + '" style="width:auto;margin:0">' +
        s.no + ". " + esc(s.t) + " <span style=\\"opacity:.6\\">" + s.m + "분</span></button>";
    }
    $("stepbar").innerHTML = h;
    var bs = document.querySelectorAll("#stepbar .stepbtn");
    for (var j = 0; j < bs.length; j++) {
      bs[j].onclick = function () { go(Number(this.getAttribute("data-s"))); };
    }
    var tips = ["", "카드 세 장을 먼저 맞혀 봅니다. AI는 아직 켜지 않았어요.",
      "카드 20장에 이름표를 붙입니다. 이것이 학습 데이터가 됩니다.",
      "학습 버튼을 누르면 진짜로 배웁니다. 시험 카드 여섯 장으로 확인해요.",
      "고양이 카드를 줄이고 다시 배우게 합니다. 무엇이 달라지나요?",
      "오늘 있었던 일을 사람 칸과 AI 칸으로 나눕니다."];
    $("steptip").textContent = tips[step];
  }

  function go(n) {
    if (n < 1 || n > 5) { return; }
    if (n >= 3 && labeled() < 10) {
      $("w-msg").innerHTML = '<span class="warn">이름표를 10장 넘게 붙여야 배울 수 있어요. 지금 ' + labeled() + '장이에요.</span>';
      n = 2;
    }
    step = n;
    for (var i = 1; i <= 5; i++) {
      var el = $("stage" + i);
      if (el) { el.style.display = (i === step ? "block" : "none"); }
    }
    stepBar();
    if (step === 3) { renderTrain(); }
    if (step === 4) { renderCut(); }
    window.scrollTo(0, 0);
  }

  function labeled() {
    var n = 0;
    for (var k in label) { if (label.hasOwnProperty(k) && label[k]) { n++; } }
    return n;
  }

  /* 1단계 */
  function build1() {
    var pick = [TRAIN[0], TRAIN[1], TRAIN[6]];
    var h = '<div class="card"><h2>여러분이라면 무엇이라고 할까요</h2>' +
      '<p class="muted">아직 AI를 켜지 않았어요. 사람이 먼저 판단해 봅니다.</p><div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(210px,1fr));margin-top:12px">';
    for (var i = 0; i < pick.length; i++) {
      var c = pick[i];
      h += '<div class="bucket" style="text-align:center">' + faceSvg(c, true) +
        '<p class="muted" style="font-size:13px">' + esc(featLine(c)) + '</p><div class="row" style="justify-content:center">';
      for (var j = 0; j < LABELS.length; j++) {
        h += '<button type="button" class="chip g1" data-c="' + c.id + '" data-v="' + LABELS[j] +
          '" style="width:auto;margin:4px 2px">' + LABELS[j] + "</button>";
      }
      h += "</div></div>";
    }
    h += '</div><label for="why1">무엇을 보고 정했나요</label>' +
      '<input id="why1" maxlength="60" placeholder="예: 귀 모양을 보고 정했습니다"></div>';
    $("stage1").innerHTML = h;
    var bs = document.querySelectorAll("#stage1 .g1");
    for (var k = 0; k < bs.length; k++) {
      bs[k].onclick = function () {
        guess[this.getAttribute("data-c")] = this.getAttribute("data-v");
        paint1();
      };
    }
    paint1();
  }

  function paint1() {
    var bs = document.querySelectorAll("#stage1 .g1");
    for (var i = 0; i < bs.length; i++) {
      var c = bs[i].getAttribute("data-c"), v = bs[i].getAttribute("data-v");
      bs[i].className = "chip g1" + (guess[c] === v ? " on" : "");
    }
  }

  /* 2단계 */
  function build2() {
    var h = '<div class="card"><h2>카드 20장에 이름표를 붙여요</h2>' +
      '<p class="muted">붙인 이름표가 그대로 학습 데이터가 됩니다. 사람마다 다르게 볼 수 있어요.</p>' +
      '<p id="cnt" style="font-weight:700;margin-top:8px"></p></div>' +
      '<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(168px,1fr))">';
    for (var i = 0; i < TRAIN.length; i++) {
      var c = TRAIN[i];
      h += '<div class="card" style="text-align:center;padding:12px">' + faceSvg(c, false) +
        '<p class="muted" style="font-size:12px;line-height:1.5">' + esc(featLine(c)) + '</p><div class="row" style="justify-content:center">';
      for (var j = 0; j < LABELS.length; j++) {
        h += '<button type="button" class="chip lb" data-c="' + c.id + '" data-v="' + LABELS[j] +
          '" style="width:auto;margin:3px 2px;padding:8px 12px">' + LABELS[j] + "</button>";
      }
      h += "</div></div>";
    }
    h += "</div>";
    $("stage2").innerHTML = h;
    var bs = document.querySelectorAll("#stage2 .lb");
    for (var k = 0; k < bs.length; k++) {
      bs[k].onclick = function () {
        label[this.getAttribute("data-c")] = this.getAttribute("data-v");
        paint2();
      };
    }
    paint2();
  }

  function paint2() {
    var bs = document.querySelectorAll("#stage2 .lb");
    for (var i = 0; i < bs.length; i++) {
      var c = bs[i].getAttribute("data-c"), v = bs[i].getAttribute("data-v");
      bs[i].className = "chip lb" + (label[c] === v ? " on" : "");
    }
    var dog = 0, cat = 0;
    for (var k in label) {
      if (!label.hasOwnProperty(k)) { continue; }
      if (label[k] === "강아지") { dog++; }
      if (label[k] === "고양이") { cat++; }
    }
    if ($("cnt")) {
      $("cnt").textContent = "붙인 이름표 " + (dog + cat) + " / 20    강아지 " + dog + "장, 고양이 " + cat + "장";
    }
  }

  function rows(limitCat) {
    var out = [], cat = 0;
    for (var i = 0; i < TRAIN.length; i++) {
      var lab = label[TRAIN[i].id];
      if (!lab) { continue; }
      if (lab === "고양이") {
        cat++;
        if (limitCat !== null && cat > limitCat) { continue; }
      }
      out.push({card: TRAIN[i], label: lab});
    }
    return out;
  }

  /* 3단계 */
  function build3() {
    $("stage3").innerHTML = '<div class="card"><h2>학습시키고 시험 보기</h2>' +
      '<p class="muted">여러분이 붙인 이름표로 배웁니다. 시험 카드 여섯 장은 답이 정해져 있어요.</p>' +
      '<button type="button" id="doTrain" style="margin-top:12px">학습시키기</button></div>' +
      '<div id="res3"></div>';
    $("doTrain").onclick = renderTrain;
  }

  function testHtml(res) {
    var h = '<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(158px,1fr))">';
    for (var i = 0; i < TEST.length; i++) {
      var d = res.detail[i], c = TEST[i];
      h += '<div class="card" style="text-align:center;padding:12px;border-color:' +
        (d.ok ? "#16a34a" : "#dc2626") + '">' + faceSvg(c, false) +
        '<p style="font-weight:700">' + esc(d.got) + '</p>' +
        '<p class="muted" style="font-size:12.5px">정답 ' + esc(d.ans) + ' · ' +
        Math.round(d.p * 100) + '% 확신</p>' +
        '<p style="font-weight:700;color:' + (d.ok ? "#15803d" : "#b91c1c") + '">' +
        (d.ok ? "맞음" : "틀림") + "</p></div>";
    }
    return h + "</div>";
  }

  function renderTrain() {
    var m = train(rows(null));
    full = evaluate(m);
    full.model = {dog: m.n["강아지"], cat: m.n["고양이"]};
    var ev = evidence(m);
    var h = '<div class="card"><h2>시험 결과</h2>' +
      '<p style="font-size:26px;font-weight:800">' + full.hit + " / " + full.of +
      ' <span style="font-size:16px;font-weight:600;color:var(--muted)">(' +
      Math.round(full.hit * 100 / full.of) + '%)</span></p>' +
      '<p class="muted">배운 카드 : 강아지 ' + m.n["강아지"] + '장, 고양이 ' + m.n["고양이"] + '장</p></div>';
    h += '<div class="card"><h2>AI는 무엇을 보고 판단했나요</h2>';
    for (var i = 0; i < ev.length; i++) {
      h += '<p style="margin-top:8px">' + esc(ev[i].name) + '</p><div class="bar"><i style="width:' +
        Math.round(ev[i].gap * 100 / (ev[0].gap || 1)) + '%"></i></div>';
    }
    h += '<p class="muted" style="margin-top:10px">막대가 길수록 강아지와 고양이를 크게 갈라 준 특징이에요.</p></div>';
    h += '<div class="card"><h2>시험 카드 여섯 장</h2>' + testHtml(full) + "</div>";
    $("res3").innerHTML = h;
  }

  /* 4단계 */
  function build4() {
    $("stage4").innerHTML = '<div class="card"><h2>고양이 카드를 줄이면 어떻게 될까요</h2>' +
      '<p class="muted">붙인 이름표 중 고양이를 몇 장만 남기고 다시 배우게 합니다.</p>' +
      '<label for="keep">남길 고양이 카드 수 : <b id="keepN">3</b>장</label>' +
      '<input id="keep" type="range" min="1" max="10" value="3" style="padding:0">' +
      '<button type="button" id="doCut" style="margin-top:12px">줄여서 다시 학습</button></div>' +
      '<div id="res4"></div>' +
      '<div class="card"><label for="why4">왜 이런 결과가 나왔을까요</label>' +
      '<textarea id="why4" maxlength="300" placeholder="예: 고양이를 적게 배워서 고양이를 자주 틀렸습니다"></textarea></div>';
    $("keep").oninput = function () { keepCat = Number(this.value); $("keepN").textContent = keepCat; };
    $("doCut").onclick = renderCut;
  }

  function renderCut() {
    if (!full) { renderTrain(); }
    var m = train(rows(keepCat));
    cut = evaluate(m);
    cut.keep = keepCat;
    cut.model = {dog: m.n["강아지"], cat: m.n["고양이"]};
    var drop = full.hit - cut.hit;
    var h = '<div class="card"><h2>줄이고 나서</h2>' +
      '<p style="font-size:26px;font-weight:800">' + cut.hit + " / " + cut.of +
      ' <span style="font-size:16px;font-weight:600;color:' + (drop > 0 ? "#b91c1c" : "var(--muted)") + '">' +
      (drop > 0 ? "이전보다 " + drop + "개 더 틀림" : "변화 없음") + "</span></p>" +
      '<p class="muted">배운 카드 : 강아지 ' + cut.model.dog + '장, 고양이 ' + cut.model.cat + '장</p></div>';
    var flipped = [];
    for (var i = 0; i < TEST.length; i++) {
      if (full.detail[i].ok && !cut.detail[i].ok) { flipped.push(TEST[i].ans); }
    }
    if (flipped.length) {
      h += '<div class="safe">맞히다가 틀리게 바뀐 카드가 ' + flipped.length + '장이에요. 모두 ' +
        esc(flipped.join(", ")) + ' 카드입니다.</div>';
    }
    h += '<div class="card"><h2>시험 카드 여섯 장</h2>' + testHtml(cut) + "</div>";
    $("res4").innerHTML = h;
  }

  /* 5단계 */
  function build5() {
    var h = '<div class="card"><h2>사람이 한 일과 AI가 한 일</h2>' +
      '<p class="muted">오늘 있었던 일을 나눠 봅시다.</p></div>';
    for (var i = 0; i < ROLE_ITEMS.length; i++) {
      h += '<div class="card" style="padding:12px 14px"><p style="font-weight:600">' + esc(ROLE_ITEMS[i]) +
        '</p><div class="row">';
      var opts = ["사람이 했다", "AI가 했다"];
      for (var j = 0; j < opts.length; j++) {
        h += '<button type="button" class="chip rl" data-i="' + i + '" data-v="' + j +
          '" style="width:auto;margin:0">' + opts[j] + "</button>";
      }
      h += "</div></div>";
    }
    h += '<div class="card"><label for="learn">오늘 알게 된 점을 한 문장으로 써요</label>' +
      '<textarea id="learn" maxlength="200" placeholder="예: AI는 사람이 준 데이터로 배우고, 데이터에 따라 결과가 달라집니다"></textarea></div>';
    $("stage5").innerHTML = h;
    var bs = document.querySelectorAll("#stage5 .rl");
    for (var k = 0; k < bs.length; k++) {
      bs[k].onclick = function () {
        role[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint5();
      };
    }
    paint5();
  }

  function paint5() {
    var bs = document.querySelectorAll("#stage5 .rl");
    for (var i = 0; i < bs.length; i++) {
      var k = bs[i].getAttribute("data-i"), v = bs[i].getAttribute("data-v");
      bs[i].className = "chip rl" + (role[k] === v ? " on" : "");
    }
  }

  /* ---------- 공통 고리 ---------- */

  function activityInit(saved) {
    if (saved) {
      guess = saved.guess || {};
      label = saved.label || {};
      role = saved.role || {};
      keepCat = saved.keepCat || 3;
    }
    build1(); build2(); build3(); build4(); build5();
    if (saved) {
      if (saved.why1 && $("why1")) { $("why1").value = saved.why1; }
      if (saved.why4 && $("why4")) { $("why4").value = saved.why4; }
      if (saved.learn && $("learn")) { $("learn").value = saved.learn; }
      if ($("keep")) { $("keep").value = keepCat; $("keepN").textContent = keepCat; }
    }
    $("prevStep").onclick = function () { go(step - 1); };
    $("nextStep").onclick = function () { go(step + 1); };
    go(1);
  }

  function activityCollect() {
    if (labeled() < 10) {
      $("w-msg").innerHTML = '<span class="warn">이름표를 10장 넘게 붙여 주세요. 지금 ' + labeled() + '장이에요.</span>';
      go(2);
      return null;
    }
    if (!full) { renderTrain(); }
    if (!cut) { renderCut(); }
    var learn = $("learn") ? $("learn").value.trim() : "";
    if (!learn) {
      $("w-msg").innerHTML = '<span class="warn">마지막 칸에 오늘 알게 된 점을 한 문장 써 주세요.</span>';
      go(5);
      return null;
    }
    return {
      guess: guess,
      why1: $("why1") ? $("why1").value.trim() : "",
      label: label,
      labeled: labeled(),
      full: {hit: full.hit, of: full.of, model: full.model},
      keepCat: keepCat,
      cut: {hit: cut.hit, of: cut.of, model: cut.model},
      why4: $("why4") ? $("why4").value.trim() : "",
      role: role,
      learn: learn
    };
  }

  /* 자동 검사용. 수업 화면에는 영향이 없다. */
  function activityAutofill() {
    for (var i = 0; i < TRAIN.length; i++) {
      label[TRAIN[i].id] = (i % 2 === 0) ? "고양이" : "강아지";
    }
    for (var j = 0; j < ROLE_ITEMS.length; j++) { role[j] = "0"; }
    if ($("learn")) { $("learn").value = "AI는 사람이 준 데이터로 배웁니다."; }
    if ($("why1")) { $("why1").value = "귀 모양을 보고 정했습니다."; }
    if ($("why4")) { $("why4").value = "고양이를 적게 배웠기 때문입니다."; }
    renderTrain();
    renderCut();
  }

  function teacherSummary(list) {
    var fullSum = 0, cutSum = 0, n = 0, split = {}, learns = [];
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.full) { continue; }
      n++;
      fullSum += p.full.hit;
      cutSum += p.cut ? p.cut.hit : 0;
      if (p.learn) { learns.push({nick: list[i].nick, t: p.learn}); }
      for (var k in p.label) {
        if (!p.label.hasOwnProperty(k)) { continue; }
        if (!split[k]) { split[k] = {강아지:0, 고양이:0}; }
        split[k][p.label[k]] = (split[k][p.label[k]] || 0) + 1;
      }
    }
    if (!n) { return '<p class="muted">아직 제출이 없어요.</p>'; }
    var h = '<div class="scroll"><table><tr><th>항목</th><th>학급 평균</th></tr>' +
      "<tr><td>전체 데이터로 학습</td><td>" + (fullSum / n).toFixed(1) + " / 6</td></tr>" +
      "<tr><td>고양이 데이터를 줄인 뒤</td><td>" + (cutSum / n).toFixed(1) + " / 6</td></tr>" +
      "<tr><td>제출한 사람</td><td>" + n + "명</td></tr></table></div>";

    var rowsOut = [];
    for (var id in split) {
      if (!split.hasOwnProperty(id)) { continue; }
      var a = split[id]["강아지"] || 0, b = split[id]["고양이"] || 0, tot = a + b;
      if (tot < 2) { continue; }
      var minority = Math.min(a, b) / tot;
      rowsOut.push({id: id, a: a, b: b, s: minority});
    }
    rowsOut.sort(function (x, y) { return y.s - x.s; });
    h += '<h3 style="margin-top:14px">의견이 갈린 카드</h3><div class="scroll"><table>' +
      "<tr><th>카드</th><th>강아지</th><th>고양이</th></tr>";
    for (var r = 0; r < Math.min(5, rowsOut.length); r++) {
      h += "<tr><td>" + rowsOut[r].id + "번</td><td>" + rowsOut[r].a + "</td><td>" + rowsOut[r].b + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:14px">오늘 알게 된 점</h3>';
    for (var q = 0; q < Math.min(8, learns.length); q++) {
      h += '<p style="margin:6px 0"><span class="pill">' + esc(learns[q].nick) + "</span> " + esc(learns[q].t) + "</p>";
    }
    return h;
  }
"""
