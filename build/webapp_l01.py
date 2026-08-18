# -*- coding: utf-8 -*-
"""1차시 데이터 실험실.

브라우저 안에서 실제로 도는 분류기다. 외부 라이브러리를 쓰지 않는다.

설계의 요점
  카드에는 소리가 적혀 있다. 학생은 소리를 듣고 이름표를 붙인다.
  AI 는 그림만 본다. 귀, 꼬리, 몸집, 코 색 네 가지다. 소리는 보지 못한다.
  그래서 귀가 처진 고양이와 귀가 뾰족한 강아지가 섞여 있어도 사람은 맞히지만
  AI 는 본 적 없는 모습을 만나면 틀린다.

  4단계에서 '큰 고양이' 카드를 빼면 AI 는 큰 고양이를 한 번도 못 본다.
  그러면 큰 고양이 시험 카드를 강아지라고 답한다.
  적게 배우면 틀린다가 아니라, 못 본 것은 틀린다가 이 차시의 장면이다.

40분을 다섯 단계로 나눈다. 4 + 10 + 11 + 10 + 5 분.
"""

ACTIVITY = u"""
  /* ---------- 카드 더미 ----------
     snd 는 학생만 본다. 이름표를 붙일 때 쓰는 단서다.
     AI 가 배우는 것은 FEATS 네 가지뿐이다. 소리는 넣지 않는다.
     귀가 처진 고양이와 귀가 뾰족한 강아지를 일부러 섞었다. */

  var TRAIN = [
    {id:0,  snd:"야옹", ear:"뾰족", tail:"길다", size:"작다", nose:"분홍"},
    {id:1,  snd:"야옹", ear:"뾰족", tail:"짧다", size:"작다", nose:"검정"},
    {id:2,  snd:"야옹", ear:"뾰족", tail:"길다", size:"작다", nose:"검정"},
    {id:3,  snd:"야옹", ear:"뾰족", tail:"짧다", size:"작다", nose:"분홍"},
    {id:4,  snd:"야옹", ear:"뾰족", tail:"길다", size:"작다", nose:"분홍"},
    {id:5,  snd:"야옹", ear:"처짐", tail:"길다", size:"작다", nose:"분홍"},
    {id:6,  snd:"야옹", ear:"처짐", tail:"짧다", size:"작다", nose:"검정"},
    {id:7,  snd:"야옹", ear:"뾰족", tail:"길다", size:"크다", nose:"검정"},
    {id:8,  snd:"야옹", ear:"뾰족", tail:"짧다", size:"크다", nose:"분홍"},
    {id:9,  snd:"야옹", ear:"뾰족", tail:"길다", size:"크다", nose:"분홍"},
    {id:10, snd:"멍",   ear:"처짐", tail:"짧다", size:"크다", nose:"검정"},
    {id:11, snd:"멍",   ear:"처짐", tail:"길다", size:"크다", nose:"검정"},
    {id:12, snd:"멍",   ear:"처짐", tail:"짧다", size:"크다", nose:"분홍"},
    {id:13, snd:"멍",   ear:"처짐", tail:"길다", size:"크다", nose:"분홍"},
    {id:14, snd:"멍",   ear:"처짐", tail:"짧다", size:"크다", nose:"검정"},
    {id:15, snd:"멍",   ear:"뾰족", tail:"길다", size:"크다", nose:"검정"},
    {id:16, snd:"멍",   ear:"뾰족", tail:"짧다", size:"크다", nose:"분홍"},
    {id:17, snd:"멍",   ear:"처짐", tail:"길다", size:"작다", nose:"분홍"},
    {id:18, snd:"멍",   ear:"처짐", tail:"짧다", size:"작다", nose:"검정"},
    {id:19, snd:"멍",   ear:"처짐", tail:"길다", size:"크다", nose:"검정"}
  ];

  /* 시험 카드에는 소리가 없다. AI 처럼 그림만 보고 맞혀야 한다.
     5번은 큰 고양이다. 4단계에서 이 카드가 뒤집힌다. */
  var TEST = [
    {id:100, ear:"뾰족", tail:"길다", size:"작다", nose:"분홍", ans:"고양이"},
    {id:101, ear:"처짐", tail:"짧다", size:"크다", nose:"검정", ans:"강아지"},
    {id:102, ear:"처짐", tail:"길다", size:"작다", nose:"분홍", ans:"고양이"},
    {id:103, ear:"뾰족", tail:"짧다", size:"크다", nose:"검정", ans:"강아지"},
    {id:104, ear:"뾰족", tail:"길다", size:"크다", nose:"분홍", ans:"고양이"},
    {id:105, ear:"처짐", tail:"짧다", size:"작다", nose:"검정", ans:"강아지"}
  ];

  var FEATS = ["ear", "tail", "size", "nose"];
  var FEAT_NAME = {ear:"귀 모양", tail:"꼬리 길이", size:"몸집", nose:"코 색"};
  var LABELS = ["강아지", "고양이"];

  /* 4단계에서 빼 볼 수 있는 것 */
  var CUTS = [
    {key:"none",    name:"빼지 않기",             test:function () { return false; }},
    {key:"bigcat",  name:"몸집이 큰 고양이 빼기",  test:function (c, lab) { return lab === "고양이" && c.size === "크다"; }},
    {key:"floppy",  name:"귀가 처진 고양이 빼기",  test:function (c, lab) { return lab === "고양이" && c.ear === "처짐"; }},
    {key:"smalldog",name:"몸집이 작은 강아지 빼기", test:function (c, lab) { return lab === "강아지" && c.size === "작다"; }}
  ];

  var ROLE_ITEMS = [
    "어떤 카드를 모을지 정했다",
    "소리를 듣고 이름표를 붙였다",
    "이름표를 보고 규칙을 계산했다",
    "새 카드가 무엇인지 예측했다",
    "무엇을 배우게 할지 결정했다",
    "맞힌 개수를 세었다",
    "틀린 까닭이 무엇인지 따져 보았다",
    "어떤 카드를 뺄지 정했다",
    "결과를 보고 다음에 무엇을 할지 정했다",
    "예측 결과를 화면에 표시했다"
  ];

  /* ---------- 카드 그리기 ---------- */

  function faceSvg(c, big) {
    var r = c.size === "크다" ? 30 : 22;
    var w = big ? 132 : 104;
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
      ? '<path d="M78 78 q24 -6 18 -32" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>'
      : '<path d="M78 78 q11 -3 10 -13" fill="none" stroke="#111" stroke-width="5" stroke-linecap="round"/>';
    return '<svg viewBox="0 0 100 100" width="' + w + '" height="' + w + '" aria-hidden="true">' +
      tail + ears +
      '<circle cx="50" cy="58" r="' + r + '" fill="#FBE3C2" stroke="#111" stroke-width="3.5"/>' +
      '<circle cx="' + (50 - r * 0.36) + '" cy="' + (58 - r * 0.16) + '" r="3.6" fill="#111"/>' +
      '<circle cx="' + (50 + r * 0.36) + '" cy="' + (58 - r * 0.16) + '" r="3.6" fill="#111"/>' +
      '<ellipse cx="50" cy="' + (60 + r * 0.28) + '" rx="5" ry="4" fill="' + noseColor + '" stroke="#111" stroke-width="2"/>' +
      '</svg>';
  }

  function featLine(c) {
    return '귀 ' + c.ear + ' · 꼬리 ' + c.tail + ' · 몸집 ' + c.size + ' · 코 ' + c.nose;
  }

  function soundTag(c) {
    return '<p style="font-weight:800;font-size:17px;margin:2px 0">소리 : ' + esc(c.snd) + '</p>';
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
    {no:3, t:"가르치고 시험 보기", m:11},
    {no:4, t:"못 본 것은 어떻게 될까", m:10},
    {no:5, t:"사람이 한 일, AI가 한 일", m:5}
  ];
  var guess = {};
  var label = {};
  var full = null;
  var cut = null;
  var cutKey = "bigcat";
  var role = {};

  /* ---------- 화면 ---------- */

  function activityHtml() {
    return '<div class="card"><div class="row" id="stepbar"></div>' +
      '<p class="muted" id="steptip" style="margin-top:8px"></p></div>' +
      '<div id="stage1"></div><div id="stage2"></div><div id="stage3"></div>' +
      '<div id="stage4"></div><div id="stage5"></div>' +
      '<div class="card"><div class="row">' +
      '<button type="button" id="prevStep" class="plain" style="width:auto">이전 단계</button>' +
      '<button type="button" id="nextStep" class="ghost" style="width:auto">다음 단계</button>' +
      '</div></div>';
  }

  function stepBar() {
    var h = "";
    for (var i = 0; i < STEPS.length; i++) {
      var s = STEPS[i];
      h += '<button type="button" class="chip stepbtn' + (step === s.no ? " on" : "") +
        '" data-s="' + s.no + '" style="width:auto;margin:0">' +
        s.no + ". " + esc(s.t) + ' <span style="opacity:.6">' + s.m + "분</span></button>";
    }
    $("stepbar").innerHTML = h;
    var bs = document.querySelectorAll("#stepbar .stepbtn");
    for (var j = 0; j < bs.length; j++) {
      bs[j].onclick = function () { go(Number(this.getAttribute("data-s"))); };
    }
    var tips = ["",
      "카드 세 장을 먼저 맞혀 봅니다. AI는 아직 켜지 않았어요.",
      "소리를 듣고 이름표를 붙여요. 이것이 학습 데이터가 됩니다.",
      "AI는 그림만 봅니다. 소리는 여러분만 들었어요.",
      "어떤 카드를 빼 보면 AI가 무엇을 못 배우게 될까요?",
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
    var pick = [TEST[0], TEST[1], TEST[4]];
    var h = '<div class="card"><h2>여러분이라면 무엇이라고 할까요</h2>' +
      '<p class="muted">아직 AI를 켜지 않았어요. 소리도 없어요. 그림만 보고 정해 봅시다.</p>' +
      '<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(210px,1fr));margin-top:12px">';
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
    var h = '<div class="card"><h2>소리를 듣고 이름표를 붙여요</h2>' +
      '<p class="muted">야옹은 고양이, 멍은 강아지예요. 귀 모양만 보면 헷갈리는 카드가 섞여 있어요.</p>' +
      '<p id="cnt" style="font-weight:800;margin-top:8px"></p></div>' +
      '<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(168px,1fr))">';
    for (var i = 0; i < TRAIN.length; i++) {
      var c = TRAIN[i];
      h += '<div class="card" style="text-align:center;padding:12px">' + faceSvg(c, false) +
        soundTag(c) +
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

  function cutRule(key) {
    for (var i = 0; i < CUTS.length; i++) { if (CUTS[i].key === key) { return CUTS[i]; } }
    return CUTS[0];
  }

  function rows(key) {
    var rule = key ? cutRule(key) : null;
    var out = [];
    for (var i = 0; i < TRAIN.length; i++) {
      var lab = label[TRAIN[i].id];
      if (!lab) { continue; }
      if (rule && rule.test(TRAIN[i], lab)) { continue; }
      out.push({card: TRAIN[i], label: lab});
    }
    return out;
  }

  /* 3단계 */
  function build3() {
    $("stage3").innerHTML = '<div class="card"><h2>가르치고 시험 보기</h2>' +
      '<p class="muted">AI는 그림만 봅니다. 귀, 꼬리, 몸집, 코 색 네 가지예요. ' +
      '소리는 여러분만 들었어요.</p>' +
      '<button type="button" id="doTrain" style="margin-top:12px">가르치기</button></div>' +
      '<div id="res3"></div>';
    $("doTrain").onclick = renderTrain;
  }

  function testHtml(res) {
    var h = '<div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(158px,1fr))">';
    for (var i = 0; i < TEST.length; i++) {
      var d = res.detail[i], c = TEST[i];
      h += '<div class="card" style="text-align:center;padding:12px;border-color:' +
        (d.ok ? "#0B7A3B" : "#B0450A") + '">' + faceSvg(c, false) +
        '<p style="font-weight:800">' + esc(d.got) + '</p>' +
        '<p class="muted" style="font-size:12.5px">정답 ' + esc(d.ans) + ' · ' +
        Math.round(d.p * 100) + '% 확신</p>' +
        '<p style="font-weight:800;color:' + (d.ok ? "#0B7A3B" : "#B0450A") + '">' +
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
      '<p style="font-size:28px;font-weight:900">' + full.hit + " / " + full.of +
      ' <span style="font-size:16px;font-weight:700;color:var(--muted)">(' +
      Math.round(full.hit * 100 / full.of) + '%)</span></p>' +
      '<p class="muted">배운 카드 : 강아지 ' + m.n["강아지"] + '장, 고양이 ' + m.n["고양이"] + '장</p></div>';
    h += '<div class="card"><h2>AI는 무엇을 보고 판단했나요</h2>';
    for (var i = 0; i < ev.length; i++) {
      h += '<p style="margin-top:8px;font-weight:700">' + esc(ev[i].name) + '</p><div class="bar"><i style="width:' +
        Math.round(ev[i].gap * 100 / (ev[0].gap || 1)) + '%"></i></div>';
    }
    h += '<p class="muted" style="margin-top:10px">막대가 길수록 크게 갈라 준 특징이에요. ' +
      '소리는 없어요. AI가 못 봤으니까요.</p></div>';
    h += '<div class="card"><h2>시험 카드 여섯 장</h2>' + testHtml(full) + "</div>";
    $("res3").innerHTML = h;
  }

  /* 4단계 */
  function build4() {
    var h = '<div class="card"><h2>어떤 카드를 빼 볼까요</h2>' +
      '<p class="muted">뺀 카드는 AI가 한 번도 못 봅니다. 무엇이 달라지는지 봅시다.</p>' +
      '<div class="row" style="margin-top:12px">';
    for (var i = 0; i < CUTS.length; i++) {
      h += '<button type="button" class="chip ct" data-k="' + CUTS[i].key +
        '" style="width:auto;margin:0">' + esc(CUTS[i].name) + "</button>";
    }
    h += '</div></div><div id="res4"></div>' +
      '<div class="card"><label for="why4">왜 이런 결과가 나왔을까요</label>' +
      '<textarea id="why4" maxlength="300" placeholder="예: 큰 고양이를 한 번도 못 봐서 큰 것은 강아지라고 했습니다"></textarea></div>';
    $("stage4").innerHTML = h;
    var bs = document.querySelectorAll("#stage4 .ct");
    for (var k = 0; k < bs.length; k++) {
      bs[k].onclick = function () { cutKey = this.getAttribute("data-k"); renderCut(); };
    }
  }

  function renderCut() {
    if (!full) { renderTrain(); }
    var rule = cutRule(cutKey);
    var kept = rows(cutKey);
    var m = train(kept);
    cut = evaluate(m);
    cut.key = cutKey;
    cut.model = {dog: m.n["강아지"], cat: m.n["고양이"]};

    var bs = document.querySelectorAll("#stage4 .ct");
    for (var b = 0; b < bs.length; b++) {
      bs[b].className = "chip ct" + (bs[b].getAttribute("data-k") === cutKey ? " on" : "");
    }

    var removed = rows(null).length - kept.length;
    var drop = full.hit - cut.hit;
    var h = '<div class="card"><h2>' + esc(rule.name) + '</h2>' +
      '<p class="muted">뺀 카드 ' + removed + '장. AI는 이 카드를 한 번도 못 봤어요.</p>' +
      '<p style="font-size:28px;font-weight:900;margin-top:8px">' + cut.hit + " / " + cut.of +
      ' <span style="font-size:16px;font-weight:700;color:' + (drop > 0 ? "#B0450A" : "var(--muted)") + '">' +
      (drop > 0 ? "이전보다 " + drop + "개 더 틀림" : "변화 없음") + "</span></p>" +
      '<p class="muted">배운 카드 : 강아지 ' + cut.model.dog + '장, 고양이 ' + cut.model.cat + '장</p></div>';

    var flipped = [];
    for (var i = 0; i < TEST.length; i++) {
      if (full.detail[i].ok && !cut.detail[i].ok) {
        flipped.push((i + 1) + "번 " + TEST[i].ans + "(" + TEST[i].size + ")");
      }
    }
    if (flipped.length) {
      h += '<div class="safe">맞히다가 틀리게 바뀐 카드 : ' + esc(flipped.join(", ")) +
        "<br>AI가 못 본 모습이라 엉뚱하게 답했어요.</div>";
    }
    h += '<div class="card"><h2>시험 카드 여섯 장</h2>' + testHtml(cut) + "</div>";
    $("res4").innerHTML = h;
  }

  /* 5단계 */
  function build5() {
    var h = '<div class="card"><h2>사람이 한 일과 AI가 한 일</h2>' +
      '<p class="muted">오늘 있었던 일을 나눠 봅시다.</p></div>';
    for (var i = 0; i < ROLE_ITEMS.length; i++) {
      h += '<div class="card" style="padding:12px 14px"><p style="font-weight:700">' + esc(ROLE_ITEMS[i]) +
        '</p><div class="row">';
      var opts = ["사람이 했다", "AI가 했다"];
      for (var j = 0; j < opts.length; j++) {
        h += '<button type="button" class="chip rl" data-i="' + i + '" data-v="' + j +
          '" style="width:auto;margin:0">' + opts[j] + "</button>";
      }
      h += "</div></div>";
    }
    h += '<div class="card"><label for="learn">오늘 알게 된 점을 한 문장으로 써요</label>' +
      '<textarea id="learn" maxlength="200" placeholder="예: AI는 못 본 것을 맞히지 못합니다"></textarea></div>';
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
      cutKey = saved.cutKey || "bigcat";
    }
    build1(); build2(); build3(); build4(); build5();
    if (saved) {
      if (saved.why1 && $("why1")) { $("why1").value = saved.why1; }
      if (saved.why4 && $("why4")) { $("why4").value = saved.why4; }
      if (saved.learn && $("learn")) { $("learn").value = saved.learn; }
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
      cutKey: cutKey,
      cut: {hit: cut.hit, of: cut.of, model: cut.model, key: cut.key},
      why4: $("why4") ? $("why4").value.trim() : "",
      role: role,
      learn: learn
    };
  }

  function activityAutofill() {
    for (var i = 0; i < TRAIN.length; i++) {
      label[TRAIN[i].id] = (TRAIN[i].snd === "야옹") ? "고양이" : "강아지";
    }
    for (var j = 0; j < ROLE_ITEMS.length; j++) { role[j] = "0"; }
    if ($("learn")) { $("learn").value = "AI는 못 본 것을 맞히지 못합니다."; }
    if ($("why1")) { $("why1").value = "귀 모양을 보고 정했습니다."; }
    if ($("why4")) { $("why4").value = "큰 고양이를 한 번도 못 봤기 때문입니다."; }
    cutKey = "bigcat";
    renderTrain();
    renderCut();
  }

  function teacherSummary(list) {
    var fullSum = 0, cutSum = 0, n = 0, split = {}, learns = [], pickCut = {};
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.full) { continue; }
      n++;
      fullSum += p.full.hit;
      cutSum += p.cut ? p.cut.hit : 0;
      if (p.cutKey) { pickCut[p.cutKey] = (pickCut[p.cutKey] || 0) + 1; }
      if (p.learn) { learns.push({nick: list[i].nick, t: p.learn}); }
      for (var k in p.label) {
        if (!p.label.hasOwnProperty(k)) { continue; }
        if (!split[k]) { split[k] = {강아지:0, 고양이:0}; }
        split[k][p.label[k]] = (split[k][p.label[k]] || 0) + 1;
      }
    }
    if (!n) { return '<p class="muted">아직 제출이 없어요.</p>'; }
    var h = '<div class="scroll"><table><tr><th>항목</th><th>학급 평균</th></tr>' +
      "<tr><td>전체 데이터로 배웠을 때</td><td>" + (fullSum / n).toFixed(1) + " / 6</td></tr>" +
      "<tr><td>카드를 빼고 배웠을 때</td><td>" + (cutSum / n).toFixed(1) + " / 6</td></tr>" +
      "<tr><td>제출한 사람</td><td>" + n + "명</td></tr></table></div>";

    h += '<h3 style="margin-top:14px">무엇을 빼 보았나</h3><div class="scroll"><table><tr><th>뺀 것</th><th>고른 사람</th></tr>';
    for (var c = 0; c < CUTS.length; c++) {
      h += "<tr><td>" + esc(CUTS[c].name) + "</td><td>" + (pickCut[CUTS[c].key] || 0) + "명</td></tr>";
    }
    h += "</table></div>";

    var rowsOut = [];
    for (var id in split) {
      if (!split.hasOwnProperty(id)) { continue; }
      var a = split[id]["강아지"] || 0, b = split[id]["고양이"] || 0, tot = a + b;
      if (tot < 2) { continue; }
      rowsOut.push({id: id, a: a, b: b, s: Math.min(a, b) / tot});
    }
    rowsOut.sort(function (x, y) { return y.s - x.s; });
    h += '<h3 style="margin-top:14px">이름표가 갈린 카드</h3><div class="scroll"><table>' +
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
