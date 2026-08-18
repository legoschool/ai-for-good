# -*- coding: utf-8 -*-
"""2차시 AI 검증 실험실.

생성형 AI 계정이 없어도 돌아간다. 교사가 미리 검증한 답변 세트를 앱에 담았다.
학생이 실제 서비스에 질문을 넣지 않으므로 개인 이름이 새어 나갈 일도 없다.

다섯 문항이 서로 다른 방식으로 틀린다.
연도 오류, 범위가 흐릿한 질문, 없는 출처, 지역 정보 오류, 자릿수 오류.
"""

ACTIVITY = u"""
  /* ---------- 문항 세트 ----------
     verdict 는 어느 쪽이 맞는 답인가이다. 틀린 쪽이 아니다. 5단계에서만 보여 준다.
     kind 는 어떤 방식으로 틀렸는지를 나타낸다. */

  var ITEMS = [
    {
      id: 0,
      q: "세종대왕이 훈민정음을 만든 때는 언제인가요?",
      a: "1443년에 만들었습니다. 널리 알린 것은 1446년입니다.",
      b: "1420년에 만들어 그해 바로 널리 알렸습니다.",
      src: "초등 사회 교과서에서 옮겨 온 글입니다.\\n훈민정음은 1443년에 만들어졌습니다.\\n널리 알린 것은 1446년입니다.",
      srcName: "초등 사회 교과서",
      verdict: "a",
      kind: "연도를 지어냈어요",
      why: "가 쪽이 교과서와 같아요. 나 쪽은 연도를 지어냈어요."
    },
    {
      id: 1,
      q: "우리나라에서 가장 긴 강은 무엇인가요?",
      a: "낙동강입니다. 길이는 약 510km입니다.",
      b: "압록강입니다. 길이는 약 790km입니다.",
      src: "나라에서 만든 지리 누리집에서 옮겨 온 글입니다.\\n한반도에서 가장 긴 강은 압록강입니다. 약 790km입니다.\\n남한에서 가장 긴 강은 낙동강입니다. 약 510km입니다.",
      srcName: "국가 지리 정보 누리집",
      verdict: "both",
      kind: "물음이 흐릿해서 갈렸어요",
      why: "둘 다 틀리지 않았어요. 한반도 전체인지 남한만인지 정하지 않아서 갈렸어요."
    },
    {
      id: 2,
      q: "초등학생이 읽을 만한 밤하늘 관찰 책을 알려 주세요.",
      a: "여러 권이 있습니다. 도서관 검색으로 직접 확인해 보시기 바랍니다.",
      b: "『밤하늘의 지도』(하늘출판사, 2019)를 추천합니다. 초등 5학년 필독서입니다.",
      src: "학교 도서관에서 찾아본 결과입니다.\\n『밤하늘의 지도』는 나오지 않습니다.\\n하늘출판사도 나오지 않습니다.",
      srcName: "학교 도서관 검색",
      verdict: "a",
      kind: "없는 책을 지어냈어요",
      why: "나 쪽은 책 이름과 연도까지 붙여서 아주 그럴듯해요. 그런데 찾아보면 없어요."
    },
    {
      id: 3,
      q: "우리 학교는 언제 문을 열었나요?",
      a: "1952년 4월에 문을 열었습니다.",
      b: "1961년 4월에 문을 열었습니다.",
      src: "학교 누리집에서 옮겨 온 글입니다.\\n1961년 4월 1일에 문을 열었습니다.\\n1962년 2월에 첫 졸업식을 했습니다.",
      srcName: "학교 누리집",
      verdict: "b",
      kind: "우리 동네 일을 잘못 알아요",
      why: "나 쪽이 학교 누리집과 같아요. 우리 동네 일은 자료가 적어서 AI가 자주 틀려요."
    },
    {
      id: 4,
      q: "지구에서 달까지의 거리는 얼마인가요?",
      a: "약 384,400km입니다.",
      b: "약 38,400km입니다.",
      src: "초등 과학 교과서에서 옮겨 온 글입니다.\\n지구에서 달까지는 약 384,400km입니다.",
      srcName: "초등 과학 교과서",
      verdict: "a",
      kind: "자릿수를 틀렸어요",
      why: "가 쪽이 맞아요. 나 쪽은 0 하나가 빠졌어요. 숫자는 자릿수를 꼭 봐야 해요."
    }
  ];

  /* 1단계에서 먼저 보여 주는 그럴듯한 답 */
  var HOOK = ITEMS[2];

  var VERDICT_LABEL = {a: "가 쪽이 맞아요", b: "나 쪽이 맞아요", both: "둘 다 틀리지 않았어요"};

  /* ---------- 상태 ---------- */

  var step = 1;
  var STEPS = [
    {no:1, t:"나는 믿을까", m:5},
    {no:2, t:"같은 질문, 다른 답", m:11},
    {no:3, t:"자료와 맞춰 보기", m:12},
    {no:4, t:"환각 사례 카드", m:7},
    {no:5, t:"결과와 정리", m:5}
  ];

  var trust = null;      /* 1단계 투표 */
  var suspect = {};      /* 2단계 어느 쪽이 의심스러운가 */
  var diffNote = {};     /* 2단계 다른 곳 */
  var checked = {};      /* 3단계 검증 3단계 체크 */
  var verdict = {};      /* 3단계 판정 */
  var myWord = {};       /* 3단계 내 말로 정리 */
  var cards = [{}, {}];  /* 4단계 사례 카드 */

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
      "확인하기 전에는 사람도 속습니다. 먼저 느낌으로 골라 보세요.",
      "두 도구가 내놓은 답입니다. 어디가 다른지 찾아보세요.",
      "자료가 이 안에 있어요. 직접 맞춰 봅시다.",
      "찾아낸 환각을 카드 두 장에 남깁니다.",
      "맞았는지 보고 배운 것을 한 문장으로 씁니다."];
    $("steptip").textContent = tips[step];
  }

  function go(n) {
    if (n < 1 || n > 5) { return; }
    if (n >= 5 && judged() < 3) {
      $("w-msg").innerHTML = '<span class="warn">물음을 3개 넘게 골라야 결과를 볼 수 있어요. 지금 ' + judged() + '개예요.</span>';
      n = 3;
    }
    step = n;
    for (var i = 1; i <= 5; i++) {
      var el = $("stage" + i);
      if (el) { el.style.display = (i === step ? "block" : "none"); }
    }
    stepBar();
    if (step === 5) { renderResult(); }
    window.scrollTo(0, 0);
  }

  function judged() {
    var n = 0;
    for (var k in verdict) { if (verdict.hasOwnProperty(k) && verdict[k]) { n++; } }
    return n;
  }

  /* 1단계 */
  function build1() {
    $("stage1").innerHTML = '<div class="card"><h2>이 답을 믿어도 될까요</h2>' +
      '<p class="muted">' + esc(HOOK.q) + '</p>' +
      '<div class="bucket" style="margin-top:12px"><p style="font-size:18px">' + esc(HOOK.b) + '</p></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" class="chip tv" data-v="believe" style="width:auto;margin:0">믿을 만하다</button>' +
      '<button type="button" class="chip tv" data-v="doubt" style="width:auto;margin:0">의심스럽다</button>' +
      '<button type="button" class="chip tv" data-v="check" style="width:auto;margin:0">확인해 봐야 안다</button>' +
      '</div>' +
      '<label for="why1">무엇을 보고 그렇게 생각했나요</label>' +
      '<input id="why1" maxlength="70" placeholder="예: 출판사와 연도까지 있어서 진짜 같습니다">' +
      '<div class="safe">이 답에는 함정이 있어요. 3단계에서 확인해 봅시다.</div></div>';
    var bs = document.querySelectorAll("#stage1 .tv");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () { trust = this.getAttribute("data-v"); paint1(); };
    }
    paint1();
  }

  function paint1() {
    var bs = document.querySelectorAll("#stage1 .tv");
    for (var i = 0; i < bs.length; i++) {
      bs[i].className = "chip tv" + (trust === bs[i].getAttribute("data-v") ? " on" : "");
    }
  }

  /* 2단계 */
  function build2() {
    var h = '<div class="card"><h2>같은 물음에 두 도구가 이렇게 답했어요</h2>' +
      '<p class="muted">도구 이름은 가와 나로만 적었습니다. 어느 회사인지가 아니라 답이 다르다는 점이 중요해요.</p></div>';
    for (var i = 0; i < ITEMS.length; i++) {
      var it = ITEMS[i];
      h += '<div class="card"><h3>' + (i + 1) + ". " + esc(it.q) + "</h3>" +
        '<div class="grid" style="grid-template-columns:1fr 1fr;margin-top:10px">' +
        '<div class="bucket"><h3>도구 가</h3><p>' + esc(it.a) + "</p></div>" +
        '<div class="bucket"><h3>도구 나</h3><p>' + esc(it.b) + "</p></div></div>" +
        '<label for="d' + i + '">두 답이 어디가 다른가요</label>' +
        '<input id="d' + i + '" maxlength="80" placeholder="예: 연도가 다릅니다">' +
        '<div class="row" style="margin-top:10px">' +
        '<button type="button" class="chip sp" data-i="' + i + '" data-v="a" style="width:auto;margin:0">가가 의심스럽다</button>' +
        '<button type="button" class="chip sp" data-i="' + i + '" data-v="b" style="width:auto;margin:0">나가 의심스럽다</button>' +
        '<button type="button" class="chip sp" data-i="' + i + '" data-v="none" style="width:auto;margin:0">모르겠다</button>' +
        "</div></div>";
    }
    $("stage2").innerHTML = h;
    var bs = document.querySelectorAll("#stage2 .sp");
    for (var k = 0; k < bs.length; k++) {
      bs[k].onclick = function () {
        suspect[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint2();
      };
    }
    paint2();
  }

  function paint2() {
    var bs = document.querySelectorAll("#stage2 .sp");
    for (var i = 0; i < bs.length; i++) {
      var k = bs[i].getAttribute("data-i"), v = bs[i].getAttribute("data-v");
      bs[i].className = "chip sp" + (suspect[k] === v ? " on" : "");
    }
  }

  /* 3단계 */
  function build3() {
    var h = '<div class="card"><h2>확인하는 세 걸음</h2>' +
      '<p class="muted">① 어디서 나온 말인지 보기<br>② 교과서와 맞춰 보기<br>③ 내 말로 정리하기</p></div>';
    for (var i = 0; i < ITEMS.length; i++) {
      var it = ITEMS[i];
      h += '<div class="card"><h3>' + (i + 1) + ". " + esc(it.q) + "</h3>" +
        '<div class="grid" style="grid-template-columns:1fr 1fr;margin-top:8px">' +
        '<div class="bucket"><h3>가</h3><p style="font-size:14px">' + esc(it.a) + "</p></div>" +
        '<div class="bucket"><h3>나</h3><p style="font-size:14px">' + esc(it.b) + "</p></div></div>" +
        '<div class="row" style="margin-top:12px">' +
        '<button type="button" class="chip ck" data-i="' + i + '" data-k="0" style="width:auto;margin:0">① 어디서 나온 말인지 봤다</button>' +
        '<button type="button" class="chip ck" data-i="' + i + '" data-k="1" style="width:auto;margin:0">② 자료와 맞춰 봤다</button>' +
        "</div>" +
        '<button type="button" class="ghost srcBtn" data-i="' + i + '" style="margin-top:10px">자료 열기 · ' +
        esc(it.srcName) + "</button>" +
        '<div id="src' + i + '" class="safe" style="display:none">' + esc(it.src) + "</div>" +
        '<label>맞춰 보니 어느 쪽이 맞나요</label><div class="row">' +
        '<button type="button" class="chip vd" data-i="' + i + '" data-v="a" style="width:auto;margin:0">가 쪽이 맞아요</button>' +
        '<button type="button" class="chip vd" data-i="' + i + '" data-v="b" style="width:auto;margin:0">나 쪽이 맞아요</button>' +
        '<button type="button" class="chip vd" data-i="' + i + '" data-v="both" style="width:auto;margin:0">둘 다 틀리지 않았어요</button>' +
        "</div>" +
        '<label for="w' + i + '">③ 내 말로 정리하기</label>' +
        '<input id="w' + i + '" maxlength="90" placeholder="확인한 내용을 한 줄로 써요">' +
        "</div>";
    }
    $("stage3").innerHTML = h;

    var sb = document.querySelectorAll("#stage3 .srcBtn");
    for (var s = 0; s < sb.length; s++) {
      sb[s].onclick = function () {
        var i = this.getAttribute("data-i");
        var box = $("src" + i);
        var open = box.style.display !== "none";
        box.style.display = open ? "none" : "block";
        this.textContent = (open ? "자료 열기 · " : "자료 닫기 · ") + ITEMS[i].srcName;
        if (!open) { checked[i + "-1"] = true; paint3(); }
      };
    }
    var cb = document.querySelectorAll("#stage3 .ck");
    for (var c = 0; c < cb.length; c++) {
      cb[c].onclick = function () {
        var key = this.getAttribute("data-i") + "-" + this.getAttribute("data-k");
        checked[key] = !checked[key];
        paint3();
      };
    }
    var vb = document.querySelectorAll("#stage3 .vd");
    for (var v = 0; v < vb.length; v++) {
      vb[v].onclick = function () {
        verdict[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint3();
      };
    }
    paint3();
  }

  function paint3() {
    var cb = document.querySelectorAll("#stage3 .ck");
    for (var i = 0; i < cb.length; i++) {
      var key = cb[i].getAttribute("data-i") + "-" + cb[i].getAttribute("data-k");
      cb[i].className = "chip ck" + (checked[key] ? " on" : "");
    }
    var vb = document.querySelectorAll("#stage3 .vd");
    for (var j = 0; j < vb.length; j++) {
      var k = vb[j].getAttribute("data-i"), v = vb[j].getAttribute("data-v");
      vb[j].className = "chip vd" + (verdict[k] === v ? " on" : "");
    }
  }

  /* 4단계 */
  function build4() {
    var h = '<div class="card"><h2>환각 사례 카드 두 장</h2>' +
      '<p class="muted">AI가 사실이 아닌 것을 사실처럼 말한 경우를 골라 적어요.</p></div>';
    for (var n = 0; n < 2; n++) {
      h += '<div class="card"><h3>카드 ' + (n + 1) + '</h3>' +
        '<label for="cq' + n + '">어떤 질문이었나요</label>' +
        '<select id="cq' + n + '"><option value="">고르세요</option>';
      for (var i = 0; i < ITEMS.length; i++) {
        h += '<option value="' + i + '">' + esc(ITEMS[i].q) + "</option>";
      }
      h += "</select>" +
        '<label for="cw' + n + '">무엇이 틀렸나요</label>' +
        '<input id="cw' + n + '" maxlength="80" placeholder="예: 없는 책 이름을 지어냈습니다">' +
        '<label for="ch' + n + '">어떻게 확인했나요</label>' +
        '<input id="ch' + n + '" maxlength="80" placeholder="예: 도서관에서 검색해 보니 없었습니다">' +
        "</div>";
    }
    $("stage4").innerHTML = h;
  }

  /* 5단계 */
  function build5() {
    $("stage5").innerHTML = '<div id="res5"></div>' +
      '<div class="card"><label for="learn">AI의 답을 받았을 때 가장 먼저 할 일은 무엇인가요</label>' +
      '<textarea id="learn" maxlength="200" placeholder="예: 어디서 나온 이야기인지 출처를 확인하는 일입니다"></textarea></div>';
  }

  function renderResult() {
    var hit = 0, n = 0, h = '<div class="card"><h2>내가 고른 것과 맞는 답</h2><div class="scroll"><table>' +
      "<tr><th>물음</th><th>내가 고른 것</th><th>맞는 답</th><th>어떻게 틀렸나</th></tr>";
    for (var i = 0; i < ITEMS.length; i++) {
      var it = ITEMS[i], mine = verdict[i];
      if (!mine) {
        h += "<tr><td>" + esc(it.q) + '</td><td class="muted">안 함</td><td>' +
          esc(VERDICT_LABEL[it.verdict]) + "</td><td>" + esc(it.kind) + "</td></tr>";
        continue;
      }
      n++;
      var ok = mine === it.verdict;
      if (ok) { hit++; }
      h += "<tr><td>" + esc(it.q) + '</td><td style="color:' + (ok ? "#15803d" : "#b91c1c") + '">' +
        esc(VERDICT_LABEL[mine]) + (ok ? " ✓" : " ✗") + "</td><td>" +
        esc(VERDICT_LABEL[it.verdict]) + "</td><td>" + esc(it.kind) + "</td></tr>";
    }
    h += "</table></div>";
    h += '<p style="font-size:22px;font-weight:800;margin-top:12px">' + hit + " / " + n + " 맞음</p></div>";

    h += '<div class="card"><h2>왜 그럴까요</h2>';
    for (var j = 0; j < ITEMS.length; j++) {
      h += '<p style="margin:10px 0"><b>' + esc(ITEMS[j].q) + "</b><br>" +
        '<span class="muted">' + esc(ITEMS[j].why) + "</span></p>";
    }
    h += "</div>";

    if (trust === "believe") {
      h += '<div class="safe">1단계에서 믿을 만하다고 하셨죠. 출판사와 연도까지 붙으면 사람도 속습니다. ' +
        "그래서 확인이 필요합니다.</div>";
    }
    $("res5").innerHTML = h;
  }

  /* ---------- 공통 고리 ---------- */

  function activityInit(saved) {
    if (saved) {
      trust = saved.trust || null;
      suspect = saved.suspect || {};
      checked = saved.checked || {};
      verdict = saved.verdict || {};
    }
    build1(); build2(); build3(); build4(); build5();
    if (saved) {
      if (saved.why1 && $("why1")) { $("why1").value = saved.why1; }
      if (saved.learn && $("learn")) { $("learn").value = saved.learn; }
      var i;
      for (i = 0; i < ITEMS.length; i++) {
        if (saved.diffNote && saved.diffNote[i] && $("d" + i)) { $("d" + i).value = saved.diffNote[i]; }
        if (saved.myWord && saved.myWord[i] && $("w" + i)) { $("w" + i).value = saved.myWord[i]; }
      }
      if (saved.cards) {
        for (i = 0; i < 2; i++) {
          var c = saved.cards[i] || {};
          if ($("cq" + i) && c.q !== undefined) { $("cq" + i).value = c.q; }
          if ($("cw" + i) && c.what) { $("cw" + i).value = c.what; }
          if ($("ch" + i) && c.how) { $("ch" + i).value = c.how; }
        }
      }
    }
    $("prevStep").onclick = function () { go(step - 1); };
    $("nextStep").onclick = function () { go(step + 1); };
    go(1);
  }

  function collectText() {
    var i;
    for (i = 0; i < ITEMS.length; i++) {
      diffNote[i] = $("d" + i) ? $("d" + i).value.trim() : "";
      myWord[i] = $("w" + i) ? $("w" + i).value.trim() : "";
    }
    for (i = 0; i < 2; i++) {
      cards[i] = {
        q: $("cq" + i) ? $("cq" + i).value : "",
        what: $("cw" + i) ? $("cw" + i).value.trim() : "",
        how: $("ch" + i) ? $("ch" + i).value.trim() : ""
      };
    }
  }

  function activityCollect() {
    collectText();
    if (judged() < 3) {
      $("w-msg").innerHTML = '<span class="warn">물음을 3개 넘게 골라 주세요. 지금 ' + judged() + '개예요.</span>';
      go(3);
      return null;
    }
    var made = 0;
    for (var i = 0; i < 2; i++) { if (cards[i].what) { made++; } }
    if (made < 1) {
      $("w-msg").innerHTML = '<span class="warn">환각 사례 카드를 한 장이라도 써 주세요.</span>';
      go(4);
      return null;
    }
    var learn = $("learn") ? $("learn").value.trim() : "";
    if (!learn) {
      $("w-msg").innerHTML = '<span class="warn">마지막 칸에 배운 것을 한 문장 써 주세요.</span>';
      go(5);
      return null;
    }
    var hit = 0, n = 0;
    for (var j = 0; j < ITEMS.length; j++) {
      if (!verdict[j]) { continue; }
      n++;
      if (verdict[j] === ITEMS[j].verdict) { hit++; }
    }
    return {
      trust: trust,
      why1: $("why1") ? $("why1").value.trim() : "",
      suspect: suspect,
      diffNote: diffNote,
      checked: checked,
      verdict: verdict,
      myWord: myWord,
      score: {hit: hit, of: n},
      cards: cards,
      learn: learn
    };
  }

  /* 자동 검사용. 수업 화면에는 영향이 없다. */
  function activityAutofill() {
    trust = "check";
    for (var i = 0; i < ITEMS.length; i++) {
      suspect[i] = "b";
      verdict[i] = ITEMS[i].verdict;
      checked[i + "-0"] = true;
      checked[i + "-1"] = true;
      if ($("d" + i)) { $("d" + i).value = "연도가 다릅니다."; }
      if ($("w" + i)) { $("w" + i).value = "교과서와 맞춰 보았습니다."; }
    }
    if ($("cq0")) { $("cq0").value = "2"; }
    if ($("cw0")) { $("cw0").value = "없는 책 이름을 지어냈습니다."; }
    if ($("ch0")) { $("ch0").value = "도서관에서 검색해 보니 없었습니다."; }
    if ($("why1")) { $("why1").value = "출판사와 연도까지 있어서 진짜 같았습니다."; }
    if ($("learn")) { $("learn").value = "어디서 나온 이야기인지 출처를 먼저 확인합니다."; }
  }

  function teacherSummary(list) {
    var n = 0, sum = 0, of = 0, dist = {}, cardList = [], learns = [];
    var i, j;
    for (i = 0; i < ITEMS.length; i++) { dist[i] = {a:0, b:0, both:0}; }
    for (i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.verdict) { continue; }
      n++;
      if (p.score) { sum += p.score.hit; of += p.score.of; }
      for (var k in p.verdict) {
        if (!p.verdict.hasOwnProperty(k)) { continue; }
        if (dist[k] && dist[k][p.verdict[k]] !== undefined) { dist[k][p.verdict[k]]++; }
      }
      if (p.cards) {
        for (j = 0; j < p.cards.length; j++) {
          if (p.cards[j] && p.cards[j].what) {
            cardList.push({nick: list[i].nick, what: p.cards[j].what, how: p.cards[j].how});
          }
        }
      }
      if (p.learn) { learns.push({nick: list[i].nick, t: p.learn}); }
    }
    if (!n) { return '<p class="muted">아직 제출이 없어요.</p>'; }

    var h = '<p style="font-weight:700">제출 ' + n + '명 · 학급 정답률 ' +
      (of ? Math.round(sum * 100 / of) : 0) + "%</p>";
    h += '<div class="scroll"><table><tr><th>물음</th><th>가</th><th>나</th><th>둘 다</th><th>맞는 답</th></tr>';
    for (i = 0; i < ITEMS.length; i++) {
      h += "<tr><td>" + esc(ITEMS[i].q) + "</td><td>" + dist[i].a + "</td><td>" + dist[i].b +
        "</td><td>" + dist[i].both + "</td><td>" + esc(VERDICT_LABEL[ITEMS[i].verdict]) + "</td></tr>";
    }
    h += "</table></div>";

    h += '<h3 style="margin-top:14px">학생이 만든 환각 사례 카드</h3>';
    for (i = 0; i < Math.min(8, cardList.length); i++) {
      h += '<p style="margin:6px 0"><span class="pill">' + esc(cardList[i].nick) + "</span> " +
        esc(cardList[i].what) + ' <span class="muted">(' + esc(cardList[i].how) + ")</span></p>";
    }

    h += '<h3 style="margin-top:14px">가장 먼저 할 일</h3>';
    for (i = 0; i < Math.min(8, learns.length); i++) {
      h += '<p style="margin:6px 0"><span class="pill">' + esc(learns[i].nick) + "</span> " +
        esc(learns[i].t) + "</p>";
    }
    return h;
  }
"""
