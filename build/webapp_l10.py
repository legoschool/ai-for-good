# -*- coding: utf-8 -*-
"""10차시 사용 습관 자가 점검 : 하루 정비소.

여정형으로 만든다. 폼 한 장이 아니라 화면 여덟 개를 지나간다.

  이야기 → 정비소 허브 → 기록칸(일주일) → 저울칸(보조·대행)
  → 부탁 시험소(또또에게 부탁해 보기) → 약속 작성소 → 우리 반(익명) → 정비 완료증

이 앱의 심장은 부탁 시험소다. 학생이 또또에게 직접 부탁했다가 거절당한다.
"그건 제가 못 해요. 사람이 하는 일이에요." 를 듣고 나서야
"힘들 때는 누구에게 말할까" 가 훈계가 아니라 자기가 찾아낸 답이 된다.

안전 규칙(spec/06 5절)이 다른 모든 것보다 우선한다.
  - 개인 응답을 교사 화면에 띄우지 않는다. 골격의 낱낱이 보기도 이 차시에서는 끈다.
  - 모든 화면에 "힘든 마음은 AI가 아니라 믿을 수 있는 어른에게 먼저 말해요" 를 고정한다.
  - 사용량으로 등수를 매기지 않는다. 많이 썼다는 말을 화면에 쓰지 않는다.

설계서 : spec/19_웹앱_설계_L10.md
40분 : 이야기 2 + 기록칸 8 + 저울칸 8 + 부탁 시험소 8 + 약속 8 + 우리 반 4 + 완료증 2
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  var SAFE_LINE = "힘든 마음은 AI가 아니라 믿을 수 있는 어른에게 먼저 말해요.";

  var DAYS = ["월", "화", "수", "목", "금", "토", "일"];
  var LEVELS = ["안 썼어요", "조금 썼어요", "많이 썼어요"];

  var SCENES = [
    { t: "숙제를 대신 시켰어요", icon: "write" },
    { t: "모르는 것을 설명해 달라고 했어요", icon: "talk" },
    { t: "쓴 글을 다듬어 달라고 했어요", icon: "write" },
    { t: "그림을 만들어 달라고 했어요", icon: "star" },
    { t: "다른 나라 말로 옮겨 달라고 했어요", icon: "again" },
    { t: "문제의 답을 그대로 받았어요", icon: "check" },
    { t: "아이디어를 여러 개 받았어요", icon: "both" },
    { t: "심심해서 이야기 상대를 했어요", icon: "heart" }
  ];

  /* can : 0 할 수 있어요 · 1 반만 할 수 있어요 · 2 그건 제가 못 해요 */
  var ASKS = [
    { t: "이 낱말을 다시 설명해 줘", can: 0, say: "쉬운 말로 다시 풀어 줄게요." },
    { t: "이 문장을 다른 나라 말로 옮겨 줘", can: 0, say: "어색한 곳은 직접 고쳐 주세요." },
    { t: "아이디어를 다섯 개만 줘", can: 0, say: "고르는 것은 여러분이 해요." },
    { t: "이 이야기를 짧게 줄여 줘", can: 0, say: "빠진 것이 없는지는 읽어 봐 주세요." },
    { t: "비슷한 문제를 하나 더 만들어 줘", can: 0, say: "풀이는 여러분이 해야 늘어요." },
    { t: "발표 순서를 정리해 줘", can: 0, say: "무엇을 말할지는 여러분이 정해요." },
    { t: "이게 사실인지 확인해 줘", can: 1,
      say: "저도 틀릴 때가 있어요. 교과서나 어른에게 한 번 더 확인해 주세요." },
    { t: "내 글을 더 좋게 고쳐 줘", can: 1,
      say: "표현은 도울 수 있지만, 하고 싶은 말은 여러분 것이에요." },
    { t: "친구와 화해하게 해 줘", can: 2,
      say: "마음을 푸는 일은 사람이 해요." },
    { t: "나를 안아 줘", can: 2,
      say: "저는 손이 없어요. 곁에 있는 사람이 해 줄 수 있어요." },
    { t: "나 대신 약속을 지켜 줘", can: 2,
      say: "책임은 사람이 지는 것이에요." },
    { t: "운동장에서 대신 뛰어 줘", can: 2,
      say: "직접 겪는 일은 여러분만 할 수 있어요." }
  ];

  var WHO = ["가족", "선생님", "친한 친구", "상담 선생님", "117 학교폭력 신고"];

  /* 보기 약속. 전부 언제 어떻게 할지가 들어 있다. */
  var VOWS = [
    "자기 전 30분은 화면을 끈다",
    "숙제할 때는 내 생각을 세 줄 먼저 쓴다",
    "AI가 알려 준 사실은 한 번 더 확인한다",
    "AI가 쓴 문장은 내 말로 바꾸어 쓴다",
    "고민이 생기면 사람에게 먼저 말한다",
    "모르는 낱말은 먼저 짐작해 보고 물어본다",
    "하루에 한 가지는 AI 없이 해 본다",
    "쓰기 전에 무엇을 부탁할지 정하고 연다"
  ];

  /* 약속이 구체적인지 볼 때 찾는 말. 시간이나 상황이 들어 있으면 통과다. */
  var WHENWORDS = ["때", "전에", "뒤에", "후에", "분", "시간", "동안", "하루", "아침",
    "저녁", "밤", "주말", "숙제", "수업", "자기 전", "먼저"];

  var st = {
    days: {}, scenes: {}, judge: {}, asked: {}, cant: {}, who: {}, vows: {},
    vowCache: {}, swap: "", badges: {}, classData: null, thinking: false
  };

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner +
      '<div class="safe">' + SAFE_LINE + '</div></section>';
  }

  /* 8-6절. 화면을 딱딱 갈아 끼우지 않는다. 0.6초를 넘기지 않는다.
     움직임을 줄이는 기기와 검사기에서는 기다리지 않는다. */
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
    }, ms || 480);
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">하루 정비소</h2>' +
      '<div class="iconrow" style="margin-top:12px">' + wiseIcon("ai", 44) +
      '<p style="margin:0"><b>또또</b>가 문을 열고 기다려요. 하루를 마치고 들르는 작은 정비소예요.</p></div>' +
      '<p style="margin-top:12px">또또는 여러분의 일주일을 함께 살펴봐요. ' +
      '많이 썼다고 나무라지 않아요. 숫자만 보여 주고, 정하는 사람은 여러분이에요.</p>' +
      '<div class="note" style="margin-top:12px">여기서는 이름을 묻지 않아요. ' +
      '누가 무엇을 골랐는지는 선생님도 볼 수 없어요. 우리 반 전체 숫자만 모여요.</div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="story-go">정비소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>하루 정비소</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-week">' + wiseIcon("rec", 30) +
      '<span>기록칸</span><small id="s-week">일주일을 눌러 봐요</small></button>' +
      '<button type="button" class="tile" id="t-scale">' + wiseIcon("both", 30) +
      '<span>저울칸</span><small id="s-scale">보조와 대행 가르기</small></button>' +
      '<button type="button" class="tile" id="t-ask">' + wiseIcon("ai", 30) +
      '<span>부탁 시험소</span><small id="s-ask">또또에게 부탁해 보기</small></button>' +
      '<button type="button" class="tile" id="t-vow">' + wiseIcon("write", 30) +
      '<span>약속 작성소</span><small id="s-vow">내 약속 3가지</small></button>' +
      '<button type="button" class="tile" id="t-class">' + wiseIcon("talk", 30) +
      '<span>우리 반</span><small id="s-class">익명 집계 보기</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("star", 30) +
      '<span>정비 완료증</span><small id="s-card">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("week",
      '<div class="card"><span class="pill">기록칸</span>' +
      '<h2 style="margin-top:10px">이번 주에 AI를 얼마나 썼나요</h2>' +
      '<p class="muted">기억나는 대로 골라요. 정확한 숫자를 세지 않아도 돼요.</p>' +
      '<div id="weekbox" style="margin-top:10px"></div>' +
      '<p class="note" id="weekline"></p>' +
      '<h3 style="margin-top:16px">이번 주에 해 본 것을 골라요</h3>' +
      '<p class="muted">고른 장면은 저울칸에서 하나씩 갈라 봐요.</p>' +
      '<div id="scenebox" style="margin-top:8px"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="week-go">저울칸으로 가기</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("scale",
      '<div class="card"><span class="pill">저울칸</span>' +
      '<h2 style="margin-top:10px">내가 한 일과 AI가 한 일</h2>' +
      '<p class="muted">고른 장면을 하나씩 갈라요. 옳고 그름을 매기는 것이 아니에요.</p>' +
      '<div id="scalebox" style="margin-top:10px"></div>' +
      '<div id="scaleview" style="margin-top:12px"></div>' +
      '<div id="swapbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="scale-go">부탁 시험소로 가기</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("ask",
      '<div class="card"><span class="pill">부탁 시험소</span>' +
      '<h2 style="margin-top:10px">또또에게 부탁해 봐요</h2>' +
      '<p class="muted">눌러 보면 또또가 답해요. 할 수 있는 것도 있고, 못 하는 것도 있어요.</p>' +
      '<div id="askbox" style="margin-top:10px"></div>' +
      '<div id="answerbox" style="margin-top:12px"></div>' +
      '<div id="cantbox" style="margin-top:12px"></div>' +
      '<div id="whobox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="ask-go">약속 작성소로 가기</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("vow",
      '<div class="card"><span class="pill">작성소</span>' +
      '<h2 style="margin-top:10px">내 디지털 웰빙 약속 3가지</h2>' +
      '<p class="muted">언제 어떻게 지킬지가 들어가면 지키기 쉬워요.</p>' +
      '<div id="vowbox" style="margin-top:10px"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="vow-go">우리 반 보러 가기</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("class",
      '<div class="card"><span class="pill">함께 보기</span>' +
      '<h2 style="margin-top:10px">우리 반은 어땠을까</h2>' +
      '<p class="muted">누가 무엇을 골랐는지는 아무에게도 보이지 않아요. 전체 숫자만 모여요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="peek">우리 반 집계 불러오기</button></div>' +
      '<div id="classbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="class-go">완료증 받으러 가기</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">정비 완료증</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">완료증 그림으로 저장</button>' +
      '<button type="button" class="plain back">정비소로</button></div></div>');

    return h;
  }

  /* ---------- 작은 도구 ---------- */

  function count(obj) {
    var n = 0;
    for (var k in obj) { if (obj.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function keysOf(obj) {
    var out = [];
    for (var k in obj) { if (obj.hasOwnProperty(k) && obj[k]) { out.push(k); } }
    return out;
  }

  function usedDays() {
    var n = 0;
    for (var d = 0; d < DAYS.length; d++) {
      if (st.days[d] !== undefined && Number(st.days[d]) > 0) { n++; }
    }
    return n;
  }

  function judged() {
    var n = 0;
    for (var k in st.judge) {
      if (st.judge.hasOwnProperty(k) && st.scenes[k]) { n++; }
    }
    return n;
  }

  function sideCount(side) {
    var n = 0;
    for (var k in st.judge) {
      if (st.judge.hasOwnProperty(k) && st.scenes[k] && st.judge[k] === side) { n++; }
    }
    return n;
  }

  /* ---------- 기록칸 ---------- */

  function paintWeek() {
    if (!$("weekbox")) { return; }
    var h = "";
    for (var d = 0; d < DAYS.length; d++) {
      h += '<div class="card" style="margin:8px 0;padding:12px 14px">' +
        '<b>' + esc(DAYS[d]) + '요일</b><div class="row" style="margin-top:8px">';
      for (var v = 0; v < LEVELS.length; v++) {
        h += '<button type="button" class="chip dy' + (Number(st.days[d]) === v ? " on" : "") +
          '" data-d="' + d + '" data-v="' + v + '" style="width:auto;margin:0">' +
          esc(LEVELS[v]) + '</button>';
      }
      h += '</div></div>';
    }
    $("weekbox").innerHTML = h;
    bindClass("dy", function (el) {
      st.days[el.getAttribute("data-d")] = Number(el.getAttribute("data-v"));
      paintWeek();
      paintHub();
    });

    var sh = "";
    for (var s = 0; s < SCENES.length; s++) {
      sh += '<button type="button" class="chip sc' + (st.scenes[s] ? " on" : "") +
        '" data-s="' + s + '">' + wiseIcon(SCENES[s].icon, 26) + esc(SCENES[s].t) + '</button>';
    }
    $("scenebox").innerHTML = sh;
    bindClass("sc", function (el) {
      var s2 = el.getAttribute("data-s");
      if (st.scenes[s2]) {
        st.scenes[s2] = false;
        delete st.judge[s2];
      } else {
        st.scenes[s2] = true;
      }
      paintWeek();
      paintScale();
      paintHub();
    });
    paintWeekLine();
  }

  function paintWeekLine() {
    if (!$("weekline")) { return; }
    var marked = count(st.days), picked = count(keysOf(st.scenes));
    if (!marked) {
      $("weekline").innerHTML = "일곱 칸을 눌러 이번 주를 채워 봐요.";
      return;
    }
    $("weekline").innerHTML = "표시한 칸 " + marked + " / 7 · 이번 주에 AI를 쓴 날은 " +
      usedDays() + "일이에요. 고른 장면은 " + picked + "개예요.";
  }

  /* ---------- 저울칸 ---------- */

  function paintScale() {
    if (!$("scalebox")) { return; }
    var picked = keysOf(st.scenes);
    if (!picked.length) {
      $("scalebox").innerHTML = '<p class="muted">기록칸에서 장면을 먼저 골라요. ' +
        '고른 장면이 여기에 하나씩 나와요.</p>';
      $("scaleview").innerHTML = "";
      $("swapbox").innerHTML = "";
      return;
    }
    var h = "";
    for (var i = 0; i < picked.length; i++) {
      var s = picked[i];
      h += '<div class="card fade-in" style="margin:8px 0;padding:14px">' +
        '<div class="iconrow">' + wiseIcon(SCENES[s].icon, 30) +
        '<b>' + esc(SCENES[s].t) + '</b></div><div class="row" style="margin-top:10px">' +
        '<button type="button" class="chip jd' + (st.judge[s] === "assist" ? " on" : "") +
        '" data-j="' + s + '" data-side="assist" style="width:auto;margin:0">' +
        wiseIcon("me", 24) + '보조 · 내가 하고 도움만 받았어요</button>' +
        '<button type="button" class="chip jd' + (st.judge[s] === "agent" ? " on" : "") +
        '" data-j="' + s + '" data-side="agent" style="width:auto;margin:0">' +
        wiseIcon("ai", 24) + '대행 · AI가 대신했어요</button></div></div>';
    }
    $("scalebox").innerHTML = h;
    bindClass("jd", function (el) {
      st.judge[el.getAttribute("data-j")] = el.getAttribute("data-side");
      paintScale();
      paintHub();
    });
    paintScaleView();
    paintSwap();
  }

  function paintScaleView() {
    if (!$("scaleview")) { return; }
    var a = sideCount("assist"), b = sideCount("agent"), all = a + b;
    if (!all) {
      $("scaleview").innerHTML = '<p class="muted">하나씩 가르면 여기에 저울 눈금이 나와요.</p>';
      return;
    }
    var h = '<div class="card fade-in" style="margin:0"><h3>저울 눈금</h3>' +
      '<p style="margin-top:8px">' + wiseIcon("me", 24) + '보조 ' + a + '개</p>' + barHtml(a, all) +
      '<p style="margin-top:10px">' + wiseIcon("ai", 24) + '대행 ' + b + '개</p>' + barHtml(b, all) +
      '<p class="big" style="margin-top:12px">대행 ' + pct(b, all) + '%</p>' +
      '<p class="muted">많고 적음을 매기는 숫자가 아니에요. 지금 내 모습이에요.</p></div>';
    $("scaleview").innerHTML = h;
  }

  function paintSwap() {
    if (!$("swapbox")) { return; }
    var agents = [];
    for (var k in st.judge) {
      if (st.judge.hasOwnProperty(k) && st.scenes[k] && st.judge[k] === "agent") { agents.push(k); }
    }
    if (!agents.length) {
      $("swapbox").innerHTML = "";
      return;
    }
    var h = '<div class="card fade-in" style="margin:0"><h3>하나만 바꾼다면</h3>' +
      '<p class="muted">대행이었던 것 중에 보조로 바꾸고 싶은 것을 하나 골라요. ' +
      '약속 작성소에서 문장 후보로 나와요.</p>';
    for (var i = 0; i < agents.length; i++) {
      h += '<button type="button" class="chip sw' + (st.swap === agents[i] ? " on" : "") +
        '" data-w="' + agents[i] + '">' + esc(SCENES[agents[i]].t) + '</button>';
    }
    $("swapbox").innerHTML = h + '</div>';
    bindClass("sw", function (el) {
      var w = el.getAttribute("data-w");
      st.swap = (st.swap === w) ? "" : w;
      paintSwap();
      paintVow();
      paintHub();
    });
  }

  /* ---------- 부탁 시험소 ---------- */

  function paintAsk() {
    if (!$("askbox")) { return; }
    var h = "";
    for (var i = 0; i < ASKS.length; i++) {
      h += '<button type="button" class="chip ak' + (st.asked[i] ? " on" : "") +
        '" data-a="' + i + '">' + esc(ASKS[i].t) +
        (st.asked[i] ? " · 물어봤어요" : "") + '</button>';
    }
    $("askbox").innerHTML = h;
    bindClass("ak", function (el) { askToto(Number(el.getAttribute("data-a"))); });
    paintCant();
    paintWho();
  }

  /* 또또가 곧바로 답하면 대답을 읽지 않는다. 잠깐 생각하는 시간을 둔다. */
  function askToto(i) {
    if (st.thinking) { return; }
    st.asked[i] = true;
    if (!$("answerbox")) { return; }
    if (reducedMotion()) {
      showAnswer(i);
      return;
    }
    st.thinking = true;
    $("answerbox").innerHTML = wiseSpinner("또또가 생각하는 중이에요", true) + wiseSkeleton(2);
    setTimeout(function () {
      st.thinking = false;
      showAnswer(i);
    }, 800);
  }

  function showAnswer(i) {
    var a = ASKS[i];
    var mark = a.can === 2 ? "red" : (a.can === 1 ? "yellow" : "green");
    var head = a.can === 2 ? "그건 제가 못 해요" : (a.can === 1 ? "반만 할 수 있어요" : "할 수 있어요");
    if (a.can === 2 && !st.cant[i]) {
      st.cant[i] = true;
      wiseToast("못 하는 일 목록에 담았어요.");
    }
    if ($("answerbox")) {
      $("answerbox").innerHTML = '<div class="card fade-in" style="margin:0">' +
        '<p class="muted">' + esc(a.t) + '</p>' +
        '<div class="iconrow" style="margin-top:8px">' + wiseIcon(mark, 32) +
        '<h3 style="margin:0">' + esc(head) + '</h3></div>' +
        '<p style="margin-top:8px">' + esc(a.say) + '</p></div>';
    }
    paintAskChips();
    paintCant();
    paintWho();
    paintHub();
  }

  function paintAskChips() {
    var chips = document.querySelectorAll("#activity .ak");
    for (var i = 0; i < chips.length; i++) {
      var k = chips[i].getAttribute("data-a");
      chips[i].className = "chip ak" + (st.asked[k] ? " on" : "");
    }
  }

  function paintCant() {
    if (!$("cantbox")) { return; }
    var got = keysOf(st.cant);
    if (!got.length) {
      $("cantbox").innerHTML = '<p class="muted">또또가 못 한다고 답한 것이 여기에 쌓여요. ' +
        '세 가지를 찾으면 다음이 열려요.</p>';
      return;
    }
    var h = '<div class="card fade-in" style="margin:0"><h3>AI가 못 하는 일 ' +
      got.length + ' / 3</h3><ul style="margin:8px 0 0 18px">';
    for (var i = 0; i < got.length; i++) {
      h += "<li>" + esc(ASKS[got[i]].t) + "</li>";
    }
    $("cantbox").innerHTML = h + "</ul></div>";
  }

  function paintWho() {
    if (!$("whobox")) { return; }
    if (keysOf(st.cant).length < 3) {
      $("whobox").innerHTML = "";
      return;
    }
    var h = '<div class="card fade-in" style="margin:0"><h3>그럼 이런 일은 누구에게 말할까요</h3>' +
      '<p class="muted">여러 개를 골라도 돼요.</p>';
    for (var i = 0; i < WHO.length; i++) {
      h += '<button type="button" class="chip wh' + (st.who[i] ? " on" : "") +
        '" data-h="' + i + '">' + wiseIcon(i === 4 ? "heart" : "me", 26) + esc(WHO[i]) + '</button>';
    }
    h += '<div class="safe" style="font-size:18px;font-weight:700">' + SAFE_LINE +
      ' 혼자 참지 않아도 돼요.</div></div>';
    $("whobox").innerHTML = h;
    bindClass("wh", function (el) {
      var k = el.getAttribute("data-h");
      st.who[k] = !st.who[k];
      paintWho();
      paintHub();
    });
  }

  /* ---------- 약속 작성소 ---------- */

  /* 칸에 글이 있을 때만 담는다. 지우는 것은 아래 oninput 이 맡는다.
     화면에 없는 칸이 캐시를 지우면 써 둔 약속이 사라진다. */
  function cacheVows() {
    for (var j = 0; j < 2; j++) {
      var el = $("vx" + j);
      if (!el) { continue; }
      var v = el.value ? el.value.trim() : "";
      if (v) { st.vowCache["vx" + j] = v; }
    }
  }

  function readVows() {
    cacheVows();
    var out = [];
    for (var i = 0; i < VOWS.length; i++) {
      if (st.vows[i]) { out.push(VOWS[i]); }
    }
    for (var j = 0; j < 2; j++) {
      var v = st.vowCache["vx" + j];
      if (v) { out.push(v); }
    }
    return out;
  }

  function paintVow() {
    if (!$("vowbox")) { return; }
    cacheVows();
    var h = "";
    if (st.swap) {
      h += '<div class="note">저울칸에서 고른 것 : ' + esc(SCENES[st.swap].t) +
        '. 이것을 보조로 바꾸는 약속을 하나 써 볼까요.</div>';
    }
    for (var i = 0; i < VOWS.length; i++) {
      h += '<button type="button" class="chip vw' + (st.vows[i] ? " on" : "") +
        '" data-v="' + i + '">' + esc(VOWS[i]) + '</button>';
    }
    h += '<label for="vx0">내 말로 쓰기 1</label>' +
      '<input id="vx0" maxlength="40" placeholder="예: 숙제할 때는 내 생각을 세 줄 먼저 쓴다">' +
      '<label for="vx1">내 말로 쓰기 2</label>' +
      '<input id="vx1" maxlength="40" placeholder="예: 저녁 아홉 시 뒤에는 묻지 않는다">' +
      '<p class="note" id="vowcount"></p>';
    $("vowbox").innerHTML = h;
    for (var j = 0; j < 2; j++) {
      if ($("vx" + j) && st.vowCache["vx" + j]) { $("vx" + j).value = st.vowCache["vx" + j]; }
    }
    bindClass("vw", function (el) {
      var v = el.getAttribute("data-v");
      if (st.vows[v]) {
        st.vows[v] = false;
      } else if (readVows().length >= 3) {
        wiseToast("약속은 세 개까지예요. 바꾸려면 고른 것을 눌러 빼요.");
        return;
      } else {
        st.vows[v] = true;
      }
      paintVow();
      paintHub();
    });
    for (var k = 0; k < 2; k++) {
      var box = $("vx" + k);
      if (box) {
        box.setAttribute("data-vx", String(k));
        box.oninput = function () {
          var key = "vx" + this.getAttribute("data-vx");
          st.vowCache[key] = this.value ? this.value.trim() : "";
          countVows();
          paintHub();
        };
      }
    }
    countVows();
  }

  function countVows() {
    if (!$("vowcount")) { return; }
    var list = readVows();
    var vague = "";
    for (var j = 0; j < 2; j++) {
      var v = st.vowCache["vx" + j];
      if (!v) { continue; }
      var ok = false;
      for (var w = 0; w < WHENWORDS.length; w++) {
        if (v.indexOf(WHENWORDS[w]) >= 0) { ok = true; break; }
      }
      if (!ok) { vague = v; }
    }
    var h = list.length >= 3 ? "세 개를 정했어요. 작성 끝." :
      ("지금 " + list.length + "개예요. 세 개를 채워 봐요.");
    if (vague) {
      h += ' 언제 지킬지도 넣어 볼까요. 예: 자기 전 30분은 화면을 끈다';
    }
    $("vowcount").innerHTML = h;
    if (list.length >= 3) { award("약속 셋"); }
  }

  /* ---------- 우리 반 (익명) ---------- */

  function peek() {
    if (!$("classbox")) { return; }
    if (me.solo) {
      $("classbox").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 집계가 없어요. ' +
        '나머지 활동은 그대로 해 볼 수 있어요.</p>';
      return;
    }
    wiseButtonBusy($("peek"), true, "모으는 중");
    $("classbox").innerHTML = wiseSpinner("우리 반 기록을 모으는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      st.classData = summarize(data);
      wiseButtonBusy($("peek"), false);
      $("classbox").innerHTML = classHtml(st.classData);
      paintHub();
    })["catch"](function () {
      wiseButtonBusy($("peek"), false);
      $("classbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  /* 방 데이터를 합계로만 바꾼다. 닉네임을 여기서 버린다. */
  function summarize(data) {
    var out = { n: 0, assist: 0, agent: 0, cant: {}, who: {}, vows: {}, days: [0, 0, 0, 0, 0, 0, 0, 0] };
    for (var k in data) {
      if (!data.hasOwnProperty(k)) { continue; }
      var p = data[k].payload || {};
      out.n += 1;
      out.assist += p.assist || 0;
      out.agent += p.agent || 0;
      var ud = Number(p.usedDays || 0);
      if (ud >= 0 && ud <= 7) { out.days[ud] += 1; }
      var c = p.cant || [];
      for (var i = 0; i < c.length; i++) { out.cant[c[i]] = (out.cant[c[i]] || 0) + 1; }
      var w = p.who || [];
      for (var j = 0; j < w.length; j++) { out.who[w[j]] = (out.who[w[j]] || 0) + 1; }
      var v = p.vows || [];
      for (var m = 0; m < v.length; m++) { out.vows[v[m]] = (out.vows[v[m]] || 0) + 1; }
    }
    return out;
  }

  function topRows(map, limit) {
    var keys = [];
    for (var k in map) { if (map.hasOwnProperty(k)) { keys.push(k); } }
    keys.sort(function (a, b) { return map[b] - map[a]; });
    var out = [];
    for (var i = 0; i < keys.length && i < (limit || 5); i++) {
      out.push({ text: keys[i], n: map[keys[i]] });
    }
    return out;
  }

  function listHtml(title, rows, empty) {
    if (!rows.length) { return '<h3 style="margin-top:16px">' + title + '</h3><p class="muted">' + empty + '</p>'; }
    var h = '<h3 style="margin-top:16px">' + title + '</h3><div class="scroll"><table>' +
      '<tr><th>내용</th><th>고른 사람</th></tr>';
    for (var i = 0; i < rows.length; i++) {
      h += "<tr><td>" + esc(rows[i].text) + "</td><td>" + rows[i].n + "명</td></tr>";
    }
    return h + "</table></div>";
  }

  function classHtml(sum) {
    if (!sum.n) { return '<p class="muted">아직 우리 반 기록이 모이지 않았어요.</p>'; }
    var all = sum.assist + sum.agent;
    var h = '<div class="card fade-in" style="margin:0"><h3>우리 반 저울</h3>' +
      '<p style="margin-top:8px">' + wiseIcon("me", 24) + '보조 ' + sum.assist + '개</p>' +
      barHtml(sum.assist, all || 1) +
      '<p style="margin-top:10px">' + wiseIcon("ai", 24) + '대행 ' + sum.agent + '개</p>' +
      barHtml(sum.agent, all || 1) +
      '<p class="big" style="margin-top:12px">우리 반 대행 ' + pct(sum.agent, all) + '%</p>' +
      '<p class="muted">낸 사람 ' + sum.n + '명. 누가 무엇을 골랐는지는 보이지 않아요.</p></div>';
    h += listHtml("우리 반이 찾은 AI가 못 하는 일", topRows(sum.cant, 5), "아직 없어요.");
    h += listHtml("많이 고른 약속", topRows(sum.vows, 5), "아직 없어요.");
    return h;
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
    if (!$("s-week")) { return; }
    var marked = count(st.days), picked = keysOf(st.scenes).length;
    var cants = keysOf(st.cant).length, whos = keysOf(st.who).length;
    var vows = readVows().length;

    $("s-week").textContent = "표시한 칸 " + marked + " / 7 · 고른 장면 " + picked + "개";
    $("s-scale").textContent = picked ? ("가른 장면 " + judged() + " / " + picked) : "기록칸을 먼저 해요";
    $("s-ask").textContent = "찾은 것 " + cants + " / 3" + (whos ? (" · 말할 사람 " + whos + "명") : "");
    $("s-vow").textContent = "정한 약속 " + vows + " / 3";
    $("s-class").textContent = st.classData ? "우리 반 집계를 보았어요" : "익명 집계 보기";
    $("s-card").textContent = "오늘의 내 기록";

    var tiles = [["t-week", marked >= 7 && picked > 0], ["t-scale", picked > 0 && judged() >= picked],
      ["t-ask", cants >= 3 && whos > 0], ["t-vow", vows >= 3],
      ["t-class", !!st.classData], ["t-card", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if (marked >= 7) { award("일주일 기록"); }
    if (picked > 0 && judged() >= picked) { award("저울 맞추기"); }
    if (cants >= 3) { award("못 하는 일 찾기"); }
    if (whos > 0) { award("사람에게 말하기"); }

    var names = badgeNames();
    if ($("badges")) {
      $("badges").innerHTML = names.length
        ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
        : '<span class="muted">아직 없어요. 기록칸부터 해 보면 받을 수 있어요.</span>';
    }
    paintHud();
  }

  function paintHud() {
    var items = [{ label: "기록", done: count(st.days), total: 7 }];
    var picked = keysOf(st.scenes).length;
    if (picked) { items.push({ label: "저울", done: judged(), total: picked }); }
    items.push({ label: "못 하는 일", done: keysOf(st.cant).length, total: 3 });
    items.push({ label: "약속", done: readVows().length, total: 3 });
    wiseHud(items);
  }

  /* ---------- 완료증 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var picked = keysOf(st.scenes).length;
    if (!count(st.days) && !picked) {
      $("mine").innerHTML = '<p class="muted">아직 기록이 없어요. 기록칸부터 가 볼까요.</p>';
      return;
    }
    var a = sideCount("assist"), b = sideCount("agent");
    var cants = keysOf(st.cant), whos = keysOf(st.who), vows = readVows();
    var h = '<p class="big">' + usedDays() + '일</p>' +
      '<p class="muted">이번 주에 AI를 쓴 날이에요. 많고 적음을 매기지 않아요.</p>';
    if (a + b) {
      h += '<p style="margin-top:12px">보조 ' + a + '개 · 대행 ' + b + '개 · 대행 ' +
        pct(b, a + b) + '%</p>' + barHtml(a, a + b);
    }
    if (cants.length) {
      h += '<h3 style="margin-top:14px">또또가 못 한다고 답한 것</h3><ul style="margin:8px 0 0 18px">';
      for (var i = 0; i < cants.length; i++) { h += "<li>" + esc(ASKS[cants[i]].t) + "</li>"; }
      h += "</ul>";
    }
    if (whos.length) {
      var names = [];
      for (var w = 0; w < whos.length; w++) { names.push(WHO[whos[w]]); }
      h += '<p style="margin-top:10px">힘들 때 말할 사람 : ' + esc(names.join(", ")) + '</p>';
    }
    if (vows.length) {
      h += '<h3 style="margin-top:14px">내 약속</h3><ul style="margin:8px 0 0 18px">';
      for (var v = 0; v < vows.length; v++) { h += "<li>" + esc(vows[v]) + "</li>"; }
      h += "</ul>";
    }
    var bs = badgeNames();
    h += '<p style="margin-top:12px">받은 배지 : ' + (bs.length ? esc(bs.join(", ")) : "아직 없어요") + '</p>';
    h += '<div class="note" style="margin-top:12px">다음 시간에는 AI로 우리 마을의 문제를 도와요.</div>';
    $("mine").innerHTML = h;
  }

  function saveCard() {
    var a = sideCount("assist"), b = sideCount("agent");
    var cants = keysOf(st.cant), vows = readVows();
    wiseCardPng("하루 정비소 " + me.nick, [
      "이번 주에 AI를 쓴 날 " + usedDays() + "일",
      "보조 " + a + "개 · 대행 " + b + "개",
      "AI가 못 하는 일 : " + (cants.length ? ASKS[cants[0]].t : "아직 못 찾았어요"),
      "내 약속 : " + (vows.length ? vows[0] : "아직 정하지 않았어요"),
      SAFE_LINE
    ], "wise_l10_" + me.nick);
  }

  /* ---------- 흐름 ---------- */

  function bindClass(cls, fn) {
    var els = document.querySelectorAll("#activity ." + cls);
    for (var i = 0; i < els.length; i++) {
      els[i].onclick = function () { fn(this); };
    }
  }

  function hintFor(id) {
    if (id === "week") { return "일곱 칸을 누르고, 이번 주에 해 본 장면을 골라요."; }
    if (id === "scale") { return "고른 장면을 보조와 대행으로 갈라요. 옳고 그름이 아니에요."; }
    if (id === "ask") { return "또또에게 부탁해 봐요. 못 한다고 답하는 것이 오늘의 답이에요."; }
    if (id === "vow") { return "언제 어떻게 지킬지가 들어가면 지키기 쉬워요."; }
    if (id === "class") { return "우리 반 전체 숫자만 보여요. 개인 답은 아무에게도 보이지 않아요."; }
    return "정비소에서 하고 싶은 곳을 골라요.";
  }

  function activityEnter(id) {
    if (id === "week") { paintWeek(); }
    if (id === "scale") { paintScale(); }
    if (id === "ask") { paintAsk(); }
    if (id === "vow") { paintVow(); }
    if (id === "card") { paintMine(); }
    if (id === "hub") { paintHub(); }
    wiseNote(hintFor(id));
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.days) { st.days = saved.days; }
      if (saved.scenePick) { st.scenes = saved.scenePick; }
      if (saved.judge) { st.judge = saved.judge; }
      if (saved.cantPick) { st.cant = saved.cantPick; }
      if (saved.whoPick) { st.who = saved.whoPick; }
      if (saved.vowPick) { st.vows = saved.vowPick; }
      if (saved.vowText) { st.vowCache = saved.vowText; }
      if (saved.swap) { st.swap = saved.swap; }
    }

    $("story-go").onclick = function () { goSlow("hub", "정비소 문을 여는 중이에요", 560); };
    $("t-week").onclick = function () { goSlow("week", "기록칸으로 가는 중이에요"); };
    $("t-scale").onclick = function () { goSlow("scale", "저울을 꺼내는 중이에요"); };
    $("t-ask").onclick = function () { goSlow("ask", "또또를 부르는 중이에요"); };
    $("t-vow").onclick = function () { goSlow("vow", "작성소로 가는 중이에요"); };
    $("t-class").onclick = function () { goSlow("class", "우리 반 기록을 찾는 중이에요"); };
    $("t-card").onclick = function () { goSlow("card", "완료증을 쓰는 중이에요"); };

    $("week-go").onclick = function () { goSlow("scale", "저울을 꺼내는 중이에요"); };
    $("scale-go").onclick = function () { goSlow("ask", "또또를 부르는 중이에요"); };
    $("ask-go").onclick = function () { goSlow("vow", "작성소로 가는 중이에요"); };
    $("vow-go").onclick = function () { goSlow("class", "우리 반 기록을 찾는 중이에요"); };
    $("class-go").onclick = function () { goSlow("card", "완료증을 쓰는 중이에요"); };
    $("peek").onclick = peek;
    $("save-card").onclick = saveCard;

    var backs = document.querySelectorAll("#activity .back");
    for (var i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { goSlow("hub", "정비소로 돌아가는 중이에요", 420); };
    }

    wiseGo("story");
    paintHub();
  }

  function activityDraft() {
    return {
      days: st.days, scenePick: st.scenes, judge: st.judge, cantPick: st.cant,
      whoPick: st.who, vowPick: st.vows, vowText: st.vowCache, swap: st.swap
    };
  }

  function activityAutofill() {
    for (var d = 0; d < DAYS.length; d++) { st.days[d] = d % 3; }
    st.scenes = { 0: true, 1: true, 5: true };
    st.judge = { 0: "agent", 1: "assist", 5: "agent" };
    st.asked = { 8: true, 9: true, 10: true };
    st.cant = { 8: true, 9: true, 10: true };
    st.who = { 0: true, 1: true };
    st.vows = { 0: true, 1: true };
    st.vowCache = { vx0: "저녁 아홉 시 뒤에는 묻지 않는다", vx1: "" };
    st.swap = "0";
  }

  /* 제출이 막히면 무엇이 모자란지 알려 주고 그 화면으로 데려간다. */
  function stop(msg, screen, text) {
    $("w-msg").innerHTML = '<span class="warn">' + msg + '</span>';
    if (screen) { goSlow(screen, text || "그 화면으로 데려갈게요", 420); }
    return null;
  }

  function activityCollect() {
    var marked = count(st.days);
    if (marked < 7) {
      return stop("기록칸에서 일곱 칸을 모두 눌러요. 지금 " + marked + "칸이에요.",
        "week", "기록칸으로 가는 중이에요");
    }
    var picked = keysOf(st.scenes);
    if (picked.length < 2) {
      return stop("이번 주에 해 본 장면을 두 개 이상 골라요.", "week", "기록칸으로 가는 중이에요");
    }
    if (judged() < picked.length) {
      return stop("저울칸에서 고른 장면을 모두 갈라요. 고른 " + picked.length + "개 가운데 " +
        judged() + "개를 갈랐어요.", "scale", "저울을 꺼내는 중이에요");
    }
    var cants = keysOf(st.cant);
    if (cants.length < 3) {
      return stop("부탁 시험소에서 또또가 못 한다고 답하는 것을 세 가지 찾아요. 지금 " +
        cants.length + "가지 찾았어요.", "ask", "또또를 부르는 중이에요");
    }
    var whos = keysOf(st.who);
    if (!whos.length) {
      return stop("힘들 때 말할 사람을 한 명 이상 골라요.", "ask", "또또를 부르는 중이에요");
    }
    var vows = readVows();
    if (vows.length < 3) {
      return stop("약속을 세 개 정한 뒤에 제출해요. 지금 " + vows.length + "개예요.",
        "vow", "작성소로 가는 중이에요");
    }

    var a = sideCount("assist"), b = sideCount("agent");
    var cantText = [], whoText = [];
    for (var i = 0; i < cants.length; i++) { cantText.push(ASKS[cants[i]].t); }
    for (var j = 0; j < whos.length; j++) { whoText.push(WHO[whos[j]]); }

    wiseCelebrate("정비를 마쳤어요", [
      "이번 주에 AI를 쓴 날 <b>" + usedDays() + "일</b>",
      "보조 <b>" + a + "개</b> · 대행 <b>" + b + "개</b>",
      "정한 약속 <b>" + vows.length + "개</b>",
      SAFE_LINE
    ], "좋아요");

    return {
      days: st.days, scenePick: st.scenes, judge: st.judge,
      cantPick: st.cant, whoPick: st.who, vowPick: st.vows, vowText: st.vowCache,
      cant: cantText, who: whoText, vows: vows, swap: st.swap ? SCENES[st.swap].t : "",
      usedDays: usedDays(), assist: a, agent: b, agentPct: pct(b, a + b),
      badges: badgeNames()
    };
  }

  /* ---------- 교사 화면 (익명 집계만) ---------- */

  /* 골격의 낱낱이 보기는 개인 응답을 그대로 펼친다.
     10차시는 안전 규칙 5절에 따라 그 화면을 쓰지 않는다.
     골격을 고치지 않고 이 차시에서만 감춘다. */
  function hideDetail() {
    if ($("t-detail")) {
      $("t-detail").style.display = "none";
      $("t-detail").textContent = "낱낱이 보기 없음";
    }
    if ($("t-wrap")) { $("t-wrap").className = "scroll hide"; }
    if ($("t-table")) { $("t-table").innerHTML = ""; }
  }

  function teacherSummary(list) {
    hideDetail();
    var data = {};
    for (var i = 0; i < list.length; i++) { data[i] = list[i]; }
    var sum = summarize(data);

    var h = '<p class="muted">이 차시는 <b>익명 집계만</b> 보여 줍니다. ' +
      '개인 응답과 낱낱이 보기는 이 화면에 나타나지 않습니다.</p>';
    if (!sum.n) { return h + '<p class="muted">아직 제출이 없습니다.</p>'; }

    var all = sum.assist + sum.agent;
    h += '<h3>우리 반 저울</h3>' + wiseBars([
      { label: "보조", value: sum.assist, color: "#16a34a" },
      { label: "대행", value: sum.agent, color: "#ea580c" }
    ], 560);
    h += '<p style="margin-top:8px">학급 평균 대행 비율 ' + pct(sum.agent, all) + '% · 낸 사람 ' +
      sum.n + '명</p>';

    var dayRows = [];
    for (var d = 0; d <= 7; d++) {
      if (sum.days[d]) { dayRows.push({ label: d + "일", value: sum.days[d] }); }
    }
    if (dayRows.length) {
      h += '<h3 style="margin-top:16px">이번 주에 쓴 날 (인원)</h3>' + wiseBars(dayRows, 560) +
        '<p class="muted">많이 쓴 학생을 짚지 않는다. 학급의 모습만 본다.</p>';
    }

    h += listHtml("우리 반이 찾은 AI가 못 하는 일", topRows(sum.cant, 8), "아직 없다.");
    h += listHtml("힘들 때 말하겠다고 한 곳", topRows(sum.who, 8), "아직 없다.");
    h += listHtml("많이 고른 약속", topRows(sum.vows, 10), "아직 없다.");
    h += '<p class="muted" style="margin-top:12px">직접 쓴 약속도 닉네임 없이 위 목록에 함께 모입니다. ' +
      '도움이 필요해 보이는 학생은 수업 뒤 개별 면담으로 연결합니다.</p>';
    h += '<div class="safe">내려받는 CSV 에는 닉네임과 응답이 그대로 들어 있습니다. ' +
      '학급 통계만 남기고 개별 행은 지웁니다. 화면에서는 개인 응답을 보여 주지 않습니다.</div>';
    return h;
  }

  function presentHtml(list) {
    var data = {};
    for (var i = 0; i < list.length; i++) { data[i] = list[i]; }
    var sum = summarize(data);
    var all = sum.assist + sum.agent;
    var h = '<div class="card"><h2>우리 반 저울</h2>' +
      '<p class="big">대행 ' + pct(sum.agent, all) + '%</p>' +
      wiseBars([
        { label: "보조", value: sum.assist, color: "#16a34a" },
        { label: "대행", value: sum.agent, color: "#ea580c" }
      ], 700) +
      '<p class="muted">누가 무엇을 냈는지는 보이지 않습니다.</p></div>';

    var rows = topRows(sum.cant, 5);
    if (rows.length) {
      h += '<div class="card"><h2>AI가 못 하는 일</h2><ul style="margin:10px 0 0 20px">';
      for (var r = 0; r < rows.length; r++) {
        h += '<li>' + esc(rows[r].text) + ' <span class="pill">' + rows[r].n + '명</span></li>';
      }
      h += '</ul></div>';
    }
    h += '<div class="card"><p class="big">' + SAFE_LINE + '</p></div>';
    return h;
  }
"""
