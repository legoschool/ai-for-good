# -*- coding: utf-8 -*-
"""7차시 우리 반 AI 약속.

spec/16_웹앱_설계_L07.md 대로 만든 여정형 앱이다.

  이야기 → 회의실(허브) → 1교시 여덟 기준 우리 말로 → 2교시 조항 쓰기
  → 3교시 제안 모으기 → 4교시 투표 → 5교시 묶기와 확정 → 약속 카드

단 하나의 경험 : 자기가 쓴 '하지 마라' 문장이 교실 상황에서 막히는 것을 보고,
'이런 조건이면 된다'로 직접 고쳐 본다. 금지 목록은 외우면 끝나지만 조건은 판단 기준이 된다.
옳고 그름을 매기지 않는다. 서기 캐릭터 또박이는 상황에 넣어 보고 결과만 보여 준다.
"""

ACTIVITY = u"""
  /* ---------- 기준과 재료 ---------- */

  var CRITERIA = __CRITERIA__;

  /* 여덟 기준을 우리 말로 옮긴 보기. 정답을 매기지 않는다. 고른 것이 그 모둠의 뜻이 된다. */
  var MEANS = [
    ["공부에 도움이 될 때만 쓴다", "재미있으면 언제든 쓴다", "숙제를 빨리 끝내려고 쓴다"],
    ["내 생각을 먼저 만들고 나서 물어본다", "AI가 먼저 답을 주면 그대로 쓴다", "어려우면 바로 맡긴다"],
    ["선생님이 정한 방법을 함께 지킨다", "AI가 정한 대로 수업한다", "각자 마음대로 쓴다"],
    ["사람이 할 일과 AI가 할 일을 나눈다", "AI가 다 하게 둔다", "사람이 전부 다시 한다"],
    ["AI 답을 다른 자료로 확인한다", "AI 답을 그대로 믿는다", "확인은 어른만 한다"],
    ["결과에 내가 책임을 진다", "AI 탓으로 돌린다", "아무도 책임지지 않는다"],
    ["마음이 힘들 때는 사람에게 말한다", "마음이 힘들 때 AI와만 이야기한다", "참고 넘어간다"],
    ["누구나 쓸 수 있게 방법을 알려 준다", "잘 쓰는 사람만 쓴다", "형편이 되는 사람만 쓴다"]
  ];

  var FRAMES = [
    "___ 할 때는 ___ 하면 된다",
    "먼저 ___ 하고 나서 AI에게 도움을 받는다",
    "___ 인 경우에는 ___ 를 반드시 확인한다",
    "___ 는 사람이 정하고 ___ 만 맡긴다"
  ];

  var BAN_WORDS = ["하지 마", "하지말", "하지 말", "금지", "안 된다", "안된다",
    "쓰지 마", "쓰지말", "쓰지 말", "절대", "못 쓴다", "못쓴다"];
  var COND_WORDS = ["면", "때", "경우", "먼저", "대신", "뒤에", "나서"];

  /* 또박이가 문장을 넣어 보는 교실 상황 세 개 */
  var SITUATIONS = [
    { key: "stuck", icon: "write", title: "숙제를 하다 막혔을 때",
      ask: "이 약속대로면 무엇을 하면 되나요?",
      hint: ["먼저", "내가", "생각", "쓰고", "묻", "질문", "확인", "도움"] },
    { key: "claim", icon: "check", title: "친구가 AI로 만든 그림을 자기가 그렸다고 할 때",
      ask: "이 약속이 무엇을 알려 주나요?",
      hint: ["밝힌", "표시", "적는다", "말한다", "알린다", "책임", "출처"] },
    { key: "sad", icon: "heart", title: "마음이 힘들어 누군가에게 말하고 싶을 때",
      ask: "이 약속대로면 누구에게 말하나요?",
      hint: ["사람", "선생님", "어른", "친구", "부모", "상담"] }
  ];

  /* 혼자 체험일 때 투표 연습에 쓰는 예시 제안. 실제 학급 자료가 아니다. */
  var SAMPLES = [
    { key: "s0", group: "1모둠", crit: 0, clause: "수업 시간에는 배우는 데 도움이 될 때만 AI를 쓴다" },
    { key: "s1", group: "2모둠", crit: 1, clause: "숙제가 막힐 때는 내가 먼저 세 줄을 쓰고 나서 AI에게 묻는다" },
    { key: "s2", group: "3모둠", crit: 3, clause: "무엇을 만들지는 사람이 정하고 다듬는 일만 AI에게 맡긴다" },
    { key: "s3", group: "4모둠", crit: 4, clause: "AI 답을 쓸 때는 교과서나 누리집에서 한 번 더 확인한다" },
    { key: "s4", group: "5모둠", crit: 5, clause: "AI 도움을 받은 부분은 어디인지 밝히고 결과는 내가 책임진다" },
    { key: "s5", group: "6모둠", crit: 6, clause: "마음이 힘들 때는 AI 말고 선생님이나 어른에게 먼저 말한다" },
    { key: "s6", group: "7모둠", crit: 7, clause: "잘 모르는 친구가 있으면 쓰는 방법을 함께 알려 준다" },
    { key: "s7", group: "8모둠", crit: 2, clause: "선생님이 정한 방법이 있는 시간에는 그 방법을 함께 지킨다" }
  ];

  var st = {
    mi: 0, mean: {}, crit: 0, first: "", clause: "", fixed: false, trial: null,
    list: [], votes: {}, board: [], merge: "", learned: "", badges: {}, loaded: false, busy: false
  };

  /* ---------- 그림 ---------- */

  /* 또박이. 학급 서기다. mood 는 wait 기다림 · think 넣어 보는 중 · ok 조건형 · hmm 금지형 */
  function ddSvg(mood, size) {
    var s = size || 120;
    var eye = mood === "hmm"
      ? '<path d="M40 46 q6 5 12 0 M64 46 q6 5 12 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
      : '<circle cx="44" cy="46" r="5.5" fill="#111"/><circle cx="70" cy="46" r="5.5" fill="#111"/>';
    var mouth = mood === "ok"
      ? '<path d="M46 62 q11 11 22 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
      : (mood === "hmm"
        ? '<path d="M46 66 q11 -8 22 0" stroke="#111" stroke-width="4" fill="none" stroke-linecap="round"/>'
        : '<path d="M48 63 h18" stroke="#111" stroke-width="4" stroke-linecap="round"/>');
    var pen = mood === "think"
      ? '<path d="M86 74 l14 -14" stroke="#111" stroke-width="5" stroke-linecap="round"/>' +
        '<circle cx="102" cy="58" r="4" fill="#FFE24B" stroke="#111" stroke-width="3"/>'
      : '<path d="M86 78 l12 -6" stroke="#111" stroke-width="5" stroke-linecap="round"/>';
    return '<svg viewBox="0 0 116 118" width="' + s + '" height="' + s + '" aria-hidden="true">' +
      '<rect x="18" y="82" width="62" height="26" rx="6" fill="#fff" stroke="#111" stroke-width="3.5"/>' +
      '<path d="M26 90 h30 M26 99 h42" stroke="#111" stroke-width="3" stroke-linecap="round"/>' +
      '<circle cx="57" cy="50" r="33" fill="#fff" stroke="#111" stroke-width="3.5"/>' +
      '<path d="M32 26 q12 -12 24 -4 M82 26 q-12 -12 -24 -4" stroke="#111" stroke-width="3" fill="none" stroke-linecap="round"/>' +
      eye + mouth + pen + '</svg>';
  }

  /* 빈 약속 판. 채운 칸 수만큼 글씨가 들어간다. */
  function boardSvg(filled) {
    var h = '<svg viewBox="0 0 320 150" width="100%" height="150" aria-hidden="true">' +
      '<rect x="4" y="4" width="312" height="142" rx="12" fill="#fff" stroke="#111" stroke-width="4"/>';
    for (var i = 0; i < 8; i++) {
      var x = 20 + (i % 4) * 74, y = 34 + Math.floor(i / 4) * 56;
      var on = i < filled;
      h += '<rect x="' + x + '" y="' + y + '" width="64" height="40" rx="8" fill="' +
        (on ? "#FFE24B" : "#F4EEE0") + '" stroke="#111" stroke-width="3"/>';
      h += '<text x="' + (x + 32) + '" y="' + (y + 26) + '" text-anchor="middle" font-size="17" ' +
        'font-weight="800" fill="#111">' + (i + 1) + '</text>';
    }
    return h + '</svg>';
  }

  /* ---------- 문장 살피기 ---------- */

  function findBan(text) {
    var out = [];
    for (var i = 0; i < BAN_WORDS.length; i++) {
      if (text.indexOf(BAN_WORDS[i]) >= 0) { out.push(BAN_WORDS[i]); }
    }
    return out;
  }

  function hasCond(text) {
    for (var i = 0; i < COND_WORDS.length; i++) {
      if (text.indexOf(COND_WORDS[i]) >= 0) { return true; }
    }
    return false;
  }

  function hasHint(text, hints) {
    for (var i = 0; i < hints.length; i++) {
      if (text.indexOf(hints[i]) >= 0) { return true; }
    }
    return false;
  }

  /* 상황 세 개에 넣어 본 결과. 옳고 그름이 아니라 '답이 나오는가' 만 본다. */
  function tryClause(text) {
    var ban = findBan(text), cond = hasCond(text), out = {};
    for (var i = 0; i < SITUATIONS.length; i++) {
      var s = SITUATIONS[i];
      if (ban.length) {
        out[s.key] = { state: "stop", say: "무엇을 하면 되는지는 알 수 없어요." };
      } else if (!cond) {
        out[s.key] = { state: "stop", say: "언제 그렇게 하는지가 없어서 이 상황에서는 쓸 수 없어요." };
      } else if (hasHint(text, s.hint)) {
        out[s.key] = { state: "go", say: text };
      } else {
        out[s.key] = { state: "part", say: "이 약속은 이 상황까지는 다루지 않아요. 다른 조항이 맡습니다." };
      }
    }
    out.ban = ban;
    out.cond = cond;
    return out;
  }

  function goCount(t) {
    var n = 0;
    for (var i = 0; i < SITUATIONS.length; i++) {
      if (t && t[SITUATIONS[i].key] && t[SITUATIONS[i].key].state === "go") { n++; }
    }
    return n;
  }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card" style="text-align:center">' + ddSvg("wait", 150) +
      '<h2 style="margin-top:10px">약속 판이 비어 있어요</h2>' +
      '<p style="margin-top:10px">지난 시간에 우리 반은 같은 상황을 서로 다르게 보았어요.</p>' +
      '<p style="margin-top:6px">매번 헷갈리지 않으려면 <b>우리가 함께 정한 기준</b>이 있어야 해요.</p>' +
      '<p style="margin-top:6px">저는 서기 <b>또박이</b>예요. 옳고 그름은 제가 정하지 않아요. ' +
      '여러분이 쓴 문장을 <b>교실 상황에 넣어 보고</b> 결과만 보여 줄게요.</p>' +
      '<div style="margin-top:12px">' + boardSvg(0) + '</div>' +
      '<div class="row" style="justify-content:center;margin-top:16px">' +
      '<button type="button" id="go-hub">회의실로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>우리 반 약속 회의실</h2>' +
      '<p class="muted">차례대로 해도 되고, 하고 싶은 교시부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-sense">' + wiseIcon("book", 30) +
      '<span>1교시 여덟 기준 우리 말로</span><small id="s-sense">0 / 8</small></button>' +
      '<button type="button" class="tile" id="t-draft">' + wiseIcon("write", 30) +
      '<span>2교시 우리 조항 쓰기</span><small id="s-draft">아직 안 썼어요</small></button>' +
      '<button type="button" class="tile" id="t-gather">' + wiseIcon("pub", 30) +
      '<span>3교시 제안 모으기</span><small id="s-gather">우리 반이 낸 약속</small></button>' +
      '<button type="button" class="tile" id="t-vote">' + wiseIcon("star", 30) +
      '<span>4교시 투표하기</span><small id="s-vote">남은 표 3</small></button>' +
      '<button type="button" class="tile" id="t-board">' + wiseIcon("rec", 30) +
      '<span>5교시 8조항 확정</span><small id="s-board">0 / 8칸</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("heart", 30) +
      '<span>우리 반 약속 카드</span><small id="s-card">오늘의 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("sense",
      '<div class="card"><span class="pill">1교시</span>' +
      '<h2 style="margin-top:10px">어른 말을 우리 말로</h2>' +
      '<p class="muted">여덟 가지 기준이에요. 맞고 틀림을 매기지 않아요. 우리 반이 쓸 말로 고르면 돼요.</p>' +
      '<div id="sensebox"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="m-prev" class="plain">앞 기준</button>' +
      '<button type="button" id="m-next" class="ghost">다음 기준</button>' +
      '<span class="muted" id="m-pos"></span></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="sense-go">2교시로 가기</button>' +
      '<button type="button" class="plain back">회의실로</button></div></div>');

    h += q("draft",
      '<div class="card"><span class="pill">2교시</span>' +
      '<h2 style="margin-top:10px">우리 조항 쓰기</h2>' +
      '<p class="muted">금지하는 말로 써도 괜찮아요. 또박이가 상황에 넣어 보고 어떻게 되는지 보여 줄게요.</p>' +
      '<label for="crit">우리 모둠이 맡은 기준</label>' +
      '<select id="crit"></select>' +
      '<p class="note" id="meanline" style="margin-top:10px"></p>' +
      '<div class="row" style="margin-top:10px" id="frames"></div>' +
      '<label for="claus">우리 반이 지킬 약속 문장</label>' +
      '<textarea id="claus" maxlength="200" placeholder="예: 숙제가 막힐 때는 내가 먼저 세 줄을 쓰고 나서 AI에게 묻는다"></textarea>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="try">상황에 넣어 보기</button>' +
      '<button type="button" id="keep" class="ghost">이 문장으로 정하기</button></div>' +
      '<div id="trybox" style="margin-top:12px"></div>' +
      '<div id="beforeafter" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="draft-go">3교시로 가기</button>' +
      '<button type="button" class="plain back">회의실로</button></div></div>');

    h += q("gather",
      '<div class="card"><span class="pill">3교시</span>' +
      '<h2 style="margin-top:10px">우리 반이 낸 약속</h2>' +
      '<p class="muted">기준별로 모았어요. 내 것에는 표시가 붙어요.</p>' +
      '<div class="row"><button type="button" id="reload" class="ghost">새로 불러오기</button></div>' +
      '<div id="listbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="gather-go">4교시로 가기</button>' +
      '<button type="button" class="plain back">회의실로</button></div></div>');

    h += q("vote",
      '<div class="card"><span class="pill">4교시</span>' +
      '<h2 style="margin-top:10px">세 표를 나누어 주세요</h2>' +
      '<p class="muted">한 사람이 3표예요. 같은 약속에 두 표를 줄 수 없어요. ' +
      '우리 모둠 것에만 몰아 주지 않기로 해요.</p>' +
      '<div class="row"><span class="pill" id="left">남은 표 3</span></div>' +
      '<div id="votebox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="vote-go">5교시로 가기</button>' +
      '<button type="button" class="plain back">회의실로</button></div></div>');

    h += q("board",
      '<div class="card"><span class="pill">5교시</span>' +
      '<h2 style="margin-top:10px">우리 반 8조항 판</h2>' +
      '<p class="muted">표를 많이 받은 약속부터 칸에 넣어요. 비슷한 두 약속은 하나로 묶어도 돼요.</p>' +
      '<div id="boardpic"></div>' +
      '<div id="boardbox" style="margin-top:10px"></div>' +
      '<label for="mergeline">묶은 까닭이나 남기고 싶은 소수 의견</label>' +
      '<input id="mergeline" maxlength="80" placeholder="예: 3모둠과 5모둠 약속을 하나로 합쳤습니다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="board-go">약속 카드 보기</button>' +
      '<button type="button" class="plain back">회의실로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">약속 카드</span>' +
      '<h2 style="margin-top:10px">우리 반 AI 약속</h2>' +
      '<div id="cardbox"></div>' +
      '<label for="learned">오늘 배운 것을 한 줄로</label>' +
      '<input id="learned" maxlength="80" placeholder="예: 금지보다 조건이 오래 간다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" class="plain back">회의실로</button></div>' +
      '<div class="note" style="margin-top:12px">약속은 지키려고 만드는 것이에요. ' +
      '다음 시간부터 이 카드로 우리를 점검해요.</div></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요. ' +
      '약속 문장에 친구 이름을 넣지 않아요.</div>');

    return h;
  }

  /* ---------- 1교시 ---------- */

  function senseHtml() {
    var i = st.mi, opts = MEANS[i], h = "";
    h += '<div class="card" style="margin-top:12px;padding:16px">' +
      '<p class="pill">' + esc(CRITERIA[i]) + '</p>' +
      '<p class="muted" style="margin-top:8px">우리 반 말로 하면 어느 쪽인가요?</p>';
    for (var k = 0; k < opts.length; k++) {
      h += '<button type="button" class="chip mn' + (st.mean[i] === k ? " on" : "") +
        '" data-k="' + k + '">' + esc(opts[k]) + '</button>';
    }
    h += '</div>';
    h += '<div style="margin-top:12px">' + barHtml(countMean(), CRITERIA.length) + '</div>' +
      '<p class="muted" style="margin-top:6px">우리 말로 옮긴 기준 ' + countMean() + ' / ' + CRITERIA.length + '개</p>';
    return h;
  }

  function countMean() {
    var n = 0;
    for (var k in st.mean) { if (st.mean.hasOwnProperty(k) && st.mean[k] !== undefined) { n++; } }
    return n;
  }

  function bindSense() {
    $("sensebox").innerHTML = senseHtml();
    if ($("m-pos")) { $("m-pos").textContent = (st.mi + 1) + " / " + CRITERIA.length; }
    var ms = document.querySelectorAll("#activity .mn");
    for (var i = 0; i < ms.length; i++) {
      ms[i].onclick = function () {
        st.mean[st.mi] = Number(this.getAttribute("data-k"));
        if (st.mi < CRITERIA.length - 1) { st.mi += 1; }
        bindSense();
        paintHub();
        if (countMean() === CRITERIA.length) {
          award("말 옮긴 사람");
          wiseToast("여덟 기준을 우리 말로 다 옮겼어요.");
        }
      };
    }
  }

  /* ---------- 2교시 ---------- */

  function meanLine() {
    var i = Number($("crit") ? $("crit").value : st.crit);
    if (st.mean[i] === undefined) {
      return "이 기준은 아직 우리 말로 옮기지 않았어요. 1교시에서 골라도 되고 그냥 써도 돼요.";
    }
    return "우리 말로 : " + MEANS[i][st.mean[i]];
  }

  function paintTry(t) {
    var h = '<div class="card" style="padding:16px">' +
      '<div class="iconrow">' + ddSvg(goCount(t) >= 2 ? "ok" : "hmm", 78) +
      '<p style="font-weight:800">또박이가 세 상황에 넣어 봤어요</p></div>';
    for (var i = 0; i < SITUATIONS.length; i++) {
      var s = SITUATIONS[i], r = t[s.key];
      var mark = r.state === "go" ? '<span class="ok">답이 나와요</span>'
        : (r.state === "part" ? '<span class="warn">여기까지는 아니에요</span>'
          : '<span class="warn">막혔어요</span>');
      h += '<div style="margin-top:12px;padding-top:10px;border-top:2px solid var(--line)">' +
        '<div class="iconrow">' + wiseIcon(s.icon, 22) + '<b>' + esc(s.title) + '</b></div>' +
        '<p class="muted" style="margin-top:4px">' + esc(s.ask) + '</p>' +
        '<p style="margin-top:4px">' + mark + ' · ' + esc(r.say) + '</p></div>';
    }
    if (t.ban.length) {
      h += '<p class="warn" style="margin-top:12px">금지하는 말이 들어 있어요 : ' + esc(t.ban.join(", ")) + '</p>' +
        '<p class="muted">"쓰지 마" 대신 "어떤 때에 어떻게 하면 되는지"로 바꾸어 봐요. ' +
        '금지는 그 말이 없는 상황에서 쓸 수 없어요.</p>';
    } else if (!t.cond) {
      h += '<p class="warn" style="margin-top:12px">언제 그렇게 하는지가 없어요. ' +
        '"~할 때는", "먼저 ~하고 나서" 를 넣어 봐요.</p>';
    } else {
      h += '<p class="ok" style="margin-top:12px">조건이 들어 있어요. 세 상황 가운데 ' +
        goCount(t) + '곳에서 답이 나왔어요.</p>' +
        '<p class="muted">한 조항이 모든 상황을 다룰 수는 없어요. 그래서 여덟 조항이 필요해요.</p>';
    }
    h += '</div>';
    $("trybox").innerHTML = h;
    var kids = $("trybox").firstChild ? $("trybox").firstChild.children : null;
    if (kids && slow()) {
      for (var k = 0; k < kids.length; k++) {
        kids[k].style.animation = "wfade .3s cubic-bezier(.22,.61,.36,1) both";
        kids[k].style.animationDelay = (k * 90) + "ms";
      }
    }
  }

  function paintBeforeAfter() {
    if (!st.first || !st.clause || st.first === st.clause) { $("beforeafter").innerHTML = ""; return; }
    $("beforeafter").innerHTML = '<div class="card" style="padding:16px">' +
      '<p class="muted">처음 쓴 문장</p><p style="text-decoration:line-through">' + esc(st.first) + '</p>' +
      '<p class="muted" style="margin-top:8px">고친 문장</p><p><b>' + esc(st.clause) + '</b></p></div>';
  }

  /* ---------- 3·4교시 ---------- */

  function proposals() {
    if (me.solo) { return SAMPLES.slice(0); }
    return st.list;
  }

  function listHtml() {
    var ps = proposals();
    if (!ps.length) {
      return '<p class="muted">아직 올라온 약속이 없어요. 2교시에서 문장을 정하고 제출하면 여기에 모여요.</p>';
    }
    var byCrit = {}, i;
    for (i = 0; i < ps.length; i++) {
      var c = ps[i].crit || 0;
      if (!byCrit[c]) { byCrit[c] = []; }
      byCrit[c].push(ps[i]);
    }
    var h = "";
    for (var c2 = 0; c2 < CRITERIA.length; c2++) {
      if (!byCrit[c2]) { continue; }
      h += '<div class="card" style="padding:14px;margin-top:10px"><p class="pill">' + esc(CRITERIA[c2]) + '</p>';
      for (i = 0; i < byCrit[c2].length; i++) {
        var p = byCrit[c2][i];
        h += '<p style="margin-top:8px">' + esc(p.clause) +
          ' <span class="tag">' + esc(p.group || "모둠 없음") + '</span>' +
          (p.mine ? ' <span class="tag">내 제안</span>' : "") + '</p>';
      }
      h += '</div>';
    }
    return h;
  }

  function voteHtml() {
    var ps = proposals();
    if (!ps.length) {
      return '<p class="muted">투표할 약속이 아직 없어요. 3교시에서 먼저 불러와 주세요.</p>';
    }
    var h = "";
    for (var i = 0; i < ps.length; i++) {
      var p = ps[i], on = st.votes[p.key] ? " on" : "";
      h += '<button type="button" class="chip vt' + on + '" data-k="' + esc(p.key) + '">' +
        esc(p.clause) + ' <span class="tag">' + esc(p.group || "모둠 없음") + '</span></button>';
    }
    return h;
  }

  function voteLeft() {
    var used = 0;
    for (var k in st.votes) { if (st.votes.hasOwnProperty(k) && st.votes[k]) { used++; } }
    return 3 - used;
  }

  function loadList() {
    if (me.solo) {
      st.loaded = true;
      $("listbox").innerHTML = '<p class="note">혼자 체험 중이에요. 우리 반 대신 <b>예시 제안 여덟 개</b>로 ' +
        '투표를 연습해 볼 수 있어요.</p>' + listHtml();
      return;
    }
    $("listbox").innerHTML = wiseSpinner("우리 반 제안을 불러오는 중이에요", true) + wiseSkeleton(3);
    wiseButtonBusy($("reload"), true, "불러오는 중");
    dbGet(me.room + "/entries").then(function (data) {
      st.list = [];
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload || {};
        if (!p.clause) { continue; }
        st.list.push({ key: k, group: data[k].group || "", crit: p.crit || 0,
          clause: p.clause, mine: data[k].nick === me.nick });
      }
      st.loaded = true;
      wiseButtonBusy($("reload"), false);
      $("listbox").innerHTML = listHtml();
      paintHub();
    })["catch"](function () {
      wiseButtonBusy($("reload"), false);
      $("listbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤에 다시 눌러 주세요.</p>';
    });
  }

  /* ---------- 5교시 ---------- */

  function tally() {
    var ps = proposals(), out = [];
    for (var i = 0; i < ps.length; i++) {
      out.push({ key: ps[i].key, clause: ps[i].clause, group: ps[i].group,
        mine: st.votes[ps[i].key] ? 1 : 0 });
    }
    out.sort(function (a, b) { return b.mine - a.mine; });
    return out;
  }

  function boardHtml() {
    var ps = tally();
    if (!ps.length) { return '<p class="muted">먼저 3교시에서 제안을 불러와 주세요.</p>'; }
    var h = '<p class="muted">칸에 넣을 약속을 골라요. 여덟 개까지 들어가요.</p>';
    for (var i = 0; i < ps.length; i++) {
      var inBoard = false;
      for (var b = 0; b < st.board.length; b++) { if (st.board[b] === ps[i].key) { inBoard = true; } }
      h += '<button type="button" class="chip bd' + (inBoard ? " on" : "") + '" data-k="' + esc(ps[i].key) + '">' +
        (inBoard ? "판에 있음 · " : "") + esc(ps[i].clause) +
        ' <span class="tag">' + esc(ps[i].group || "모둠 없음") + '</span>' +
        (ps[i].mine ? ' <span class="tag">내 표</span>' : "") + '</button>';
    }
    return h;
  }

  function cardHtml() {
    var lines = boardLines();
    if (!lines.length) {
      return '<p class="muted">아직 판이 비어 있어요. 5교시에서 약속을 골라 넣어 주세요.</p>';
    }
    var h = '<div class="card" style="padding:16px"><p class="pill">우리 반 AI 약속</p>';
    for (var i = 0; i < lines.length; i++) {
      h += '<p style="margin-top:8px"><b>' + (i + 1) + '.</b> ' + esc(lines[i]) + '</p>';
    }
    h += '</div>';
    return h;
  }

  function boardLines() {
    var ps = proposals(), out = [];
    for (var i = 0; i < st.board.length; i++) {
      for (var j = 0; j < ps.length; j++) {
        if (ps[j].key === st.board[i]) { out.push(ps[j].clause); }
      }
    }
    return out;
  }

  /* ---------- 기다리는 표시 ---------- */

  function slow() {
    try {
      return !(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) { return true; }
  }

  function after(ms, fn) { setTimeout(fn, slow() ? ms : 0); }

  /* 목록을 지우지 않고 흐리게만 한다. 화면이 멈춘 것처럼 보이지 않게 하고,
     겹쳐 눌러도 그리는 중간에 끊기지 않게 한다. */
  function busyBox(box, text) {
    if (!box) { return; }
    st.busy = true;
    box.style.opacity = ".45";
    var tag = box.querySelector(".busyline");
    if (!tag) {
      tag = document.createElement("div");
      tag.className = "loading busyline";
      box.insertBefore(tag, box.firstChild);
    }
    tag.innerHTML = '<span class="spin"></span><span>' + esc(text) + '</span>';
    setTimeout(function () { box.style.opacity = "1"; }, slow() ? 420 : 0);
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    paintHub();
    wiseToast("배지를 받았어요 : " + name);
  }

  function paintHub() {
    if ($("s-sense")) { $("s-sense").textContent = countMean() + " / " + CRITERIA.length; }
    if ($("s-draft")) {
      $("s-draft").textContent = st.clause ? (st.fixed ? "고쳐서 정했어요" : "정했어요") : "아직 안 썼어요";
    }
    if ($("s-gather")) { $("s-gather").textContent = proposals().length + "개 모임"; }
    if ($("s-vote")) { $("s-vote").textContent = "남은 표 " + voteLeft(); }
    if ($("s-board")) { $("s-board").textContent = st.board.length + " / 8칸"; }
    var tiles = [["t-sense", countMean() === CRITERIA.length], ["t-draft", !!st.clause],
      ["t-gather", proposals().length > 0], ["t-vote", voteLeft() < 3],
      ["t-board", st.board.length >= 3], ["t-card", st.board.length >= 3]];
    for (var i = 0; i < tiles.length; i++) {
      var el = $(tiles[i][0]);
      if (el) { el.className = "tile" + (tiles[i][1] ? " done" : ""); }
    }
    if ($("badges")) {
      var b = "";
      for (var k in st.badges) { if (st.badges.hasOwnProperty(k)) { b += '<span class="tag">' + esc(k) + '</span>'; } }
      $("badges").innerHTML = b || '<span class="muted">아직 없어요. 하나씩 모아 봐요.</span>';
    }
    wiseHud([
      { label: "기준 옮기기", done: countMean(), total: CRITERIA.length },
      { label: "쓴 표", done: 3 - voteLeft(), total: 3 },
      { label: "약속 판", done: st.board.length, total: 8 }
    ]);
    if ($("boardpic")) { $("boardpic").innerHTML = boardSvg(st.board.length); }
  }

  /* ---------- 들어가고 나가기 ---------- */

  function activityEnter(id) {
    if (id === "sense") { bindSense(); }
    if (id === "draft") {
      $("meanline").textContent = meanLine();
      paintBeforeAfter();
    }
    if (id === "gather") {
      if (!st.loaded) { loadList(); } else { $("listbox").innerHTML = listHtml(); }
    }
    if (id === "vote") {
      $("votebox").innerHTML = voteHtml();
      bindVote();
      $("left").textContent = "남은 표 " + voteLeft();
    }
    if (id === "board") {
      $("boardbox").innerHTML = boardHtml();
      bindBoard();
      $("boardpic").innerHTML = boardSvg(st.board.length);
    }
    if (id === "card") { $("cardbox").innerHTML = cardHtml(); }
  }

  function bindVote() {
    var vs = document.querySelectorAll("#activity .vt");
    for (var i = 0; i < vs.length; i++) {
      vs[i].onclick = function () {
        if (st.busy) { return; }
        var key = this.getAttribute("data-k");
        if (st.votes[key]) {
          delete st.votes[key];
        } else if (voteLeft() <= 0) {
          wiseToast("표를 다 썼어요. 준 표를 다시 눌러 거두면 돼요.");
          return;
        } else {
          st.votes[key] = true;
        }
        busyBox($("votebox"), "표를 세는 중이에요");
        after(400, function () {
          $("votebox").innerHTML = voteHtml();
          bindVote();
          $("left").textContent = "남은 표 " + voteLeft();
          if (voteLeft() === 0) { award("세 표를 다 쓴 사람"); }
          paintHub();
          st.busy = false;
        });
      };
    }
  }

  function bindBoard() {
    var bs = document.querySelectorAll("#activity .bd");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () {
        if (st.busy) { return; }
        var key = this.getAttribute("data-k"), at = -1;
        for (var j = 0; j < st.board.length; j++) { if (st.board[j] === key) { at = j; } }
        if (at >= 0) {
          st.board.splice(at, 1);
        } else if (st.board.length >= 8) {
          wiseToast("여덟 칸이 다 찼어요. 하나를 빼고 넣어요.");
          return;
        } else {
          st.board.push(key);
        }
        busyBox($("boardbox"), "판에 옮겨 적는 중이에요");
        after(450, function () {
          $("boardbox").innerHTML = boardHtml();
          bindBoard();
          $("boardpic").innerHTML = boardSvg(st.board.length);
          if (st.board.length >= 8) { award("판을 채운 사람"); }
          paintHub();
          st.busy = false;
        });
      };
    }
  }

  /* ---------- 시작 ---------- */

  function activityInit(saved) {
    if (saved) {
      if (saved.mean) { st.mean = saved.mean; }
      if (saved.clause) { st.clause = saved.clause; }
      if (saved.first) { st.first = saved.first; }
      if (saved.board) { st.board = saved.board; }
      if (saved.votes) { st.votes = saved.votes; }
    }
    var sel = $("crit"), h = "";
    for (var i = 0; i < CRITERIA.length; i++) {
      h += '<option value="' + i + '">' + esc(CRITERIA[i]) + '</option>';
    }
    sel.innerHTML = h;
    sel.onchange = function () { st.crit = Number(this.value); $("meanline").textContent = meanLine(); };

    var fh = "";
    for (var f = 0; f < FRAMES.length; f++) {
      fh += '<button type="button" class="chip fr" data-f="' + f +
        '" style="width:auto;margin:0">' + esc(FRAMES[f]) + '</button>';
    }
    $("frames").innerHTML = fh;
    var frs = document.querySelectorAll("#activity .fr");
    for (var k = 0; k < frs.length; k++) {
      frs[k].onclick = function () {
        var t = $("claus");
        t.value = FRAMES[Number(this.getAttribute("data-f"))];
        t.focus();
      };
    }

    $("go-hub").onclick = function () { wiseGo("hub"); };
    $("t-sense").onclick = function () { wiseGo("sense"); };
    $("t-draft").onclick = function () { wiseGo("draft"); };
    $("t-gather").onclick = function () { wiseGo("gather"); };
    $("t-vote").onclick = function () { wiseGo("vote"); };
    $("t-board").onclick = function () { wiseGo("board"); };
    $("t-card").onclick = function () { wiseGo("card"); };
    $("m-prev").onclick = function () { if (st.mi > 0) { st.mi -= 1; bindSense(); } };
    $("m-next").onclick = function () { if (st.mi < CRITERIA.length - 1) { st.mi += 1; bindSense(); } };
    $("sense-go").onclick = function () { wiseGo("draft"); };
    $("draft-go").onclick = function () {
      if (!st.clause) { wiseToast("먼저 문장을 쓰고 '이 문장으로 정하기'를 눌러요."); return; }
      wiseGo("gather");
    };
    $("gather-go").onclick = function () { wiseGo("vote"); };
    $("vote-go").onclick = function () { wiseGo("board"); };
    $("board-go").onclick = function () { wiseGo("card"); };
    $("reload").onclick = loadList;

    $("try").onclick = function () {
      var text = $("claus").value.trim();
      if (text.length < 6) { wiseToast("문장을 조금 더 써 주세요."); return; }
      if (!st.first) { st.first = text; }
      wiseButtonBusy($("try"), true, "넣어 보는 중");
      $("trybox").innerHTML = wiseSpinner("또박이가 세 상황에 넣어 보는 중이에요", true) + wiseSkeleton(3);
      after(900, function () {
        st.trial = tryClause(text);
        wiseButtonBusy($("try"), false);
        paintTry(st.trial);
        award("넣어 본 사람");
      });
    };

    $("keep").onclick = function () {
      var text = $("claus").value.trim();
      if (text.length < 6) { wiseToast("문장을 조금 더 써 주세요."); return; }
      if (text.indexOf("이름") >= 0 && findBan(text).length === 0 && text.indexOf("별명") < 0) {
        wiseToast("친구 이름이 들어가지 않게 살펴 주세요.");
      }
      if (!st.first) { st.first = text; }
      st.clause = text;
      st.crit = Number($("crit").value);
      st.trial = tryClause(text);
      st.fixed = (st.first !== st.clause) && findBan(st.first).length > 0 && findBan(st.clause).length === 0;
      paintTry(st.trial);
      paintBeforeAfter();
      paintHub();
      if (st.fixed) { award("금지를 조건으로 바꾼 사람"); }
      wiseToast("우리 모둠 약속으로 정했어요.");
    };

    $("save-card").onclick = function () {
      var lines = boardLines();
      if (!lines.length) { wiseToast("판을 먼저 채워요."); return; }
      var out = [];
      for (var i = 0; i < lines.length && i < 8; i++) { out.push((i + 1) + ". " + lines[i]); }
      wiseCardPng("우리 반 AI 약속 · " + me.nick, out, "우리반_AI약속.png");
    };

    wiseNote("약속 판이 비어 있어요. 여덟 칸을 우리 손으로 채워 봐요.");
    wiseGo("story");
    paintHub();
  }

  function val(id) { return $(id) ? $(id).value.trim() : ""; }

  function activityDraft() {
    return { mean: st.mean, clause: st.clause, first: st.first, board: st.board, votes: st.votes };
  }

  function activityAutofill() {
    for (var i = 0; i < CRITERIA.length; i++) { st.mean[i] = 0; }
    st.crit = 1;
    st.first = "숙제를 AI에게 시키면 안 된다";
    st.clause = "숙제가 막힐 때는 내가 먼저 세 줄을 쓰고 나서 AI에게 묻는다";
    st.trial = tryClause(st.clause);
    st.fixed = true;
    var ps = proposals();
    for (var v = 0; v < ps.length && v < 3; v++) { st.votes[ps[v].key] = true; }
    st.board = [];
    for (var b = 0; b < ps.length && b < 8; b++) { st.board.push(ps[b].key); }
  }

  function activityCollect() {
    if (!st.clause) {
      $("w-msg").innerHTML = '<span class="warn">2교시에서 우리 모둠 약속 문장을 정한 뒤에 제출해요.</span>';
      wiseGo("draft");
      return null;
    }
    if (!st.trial) { st.trial = tryClause(st.clause); }
    if (countMean() < 3) {
      $("w-msg").innerHTML = '<span class="warn">1교시에서 기준을 세 개 넘게 우리 말로 옮긴 뒤에 제출해요. 지금 ' +
        countMean() + '개예요.</span>';
      wiseGo("sense");
      return null;
    }
    var badges = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { badges.push(b); } }
    var trial = {};
    for (var s = 0; s < SITUATIONS.length; s++) {
      trial[SITUATIONS[s].key] = st.trial[SITUATIONS[s].key].state === "go";
    }
    wiseCelebrate("우리 반 약속에 한 줄을 보탰어요", [
      "우리 모둠 약속 : <b>" + esc(st.clause) + "</b>",
      st.fixed ? "금지하는 말을 <b>조건</b>으로 바꾸었어요." : "조건이 담긴 문장으로 냈어요.",
      "약속 판에 <b>" + st.board.length + "칸</b>을 채웠어요.",
      "다음 시간에는 이 약속을 다른 사람에게 알려 봐요."
    ], "좋아요");
    return {
      means: st.mean, crit: st.crit, first: st.first, clause: st.clause,
      fixed: st.fixed, trial: trial, votes: keysOf(st.votes), board: st.board,
      merge: val("mergeline"), learned: val("learned"), badges: badges
    };
  }

  function keysOf(o) {
    var out = [];
    for (var k in o) { if (o.hasOwnProperty(k) && o[k]) { out.push(k); } }
    return out;
  }

  /* ---------- 교사 화면 ---------- */

  function teacherSummary(list) {
    var fixed = 0, withClause = 0, byCrit = {}, votes = {}, texts = {}, i, j;
    for (i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (p.clause) {
        withClause++;
        var c = p.crit || 0;
        if (!byCrit[c]) { byCrit[c] = []; }
        byCrit[c].push({ clause: p.clause, group: list[i].group || "", fixed: !!p.fixed });
        texts[list[i].key || ("k" + i)] = p.clause;
      }
      if (p.fixed) { fixed++; }
      var vs = p.votes || [];
      for (j = 0; j < vs.length; j++) { votes[vs[j]] = (votes[vs[j]] || 0) + 1; }
    }
    var h = '<p class="big">' + withClause + '개 조항 · 조건형으로 고친 사람 ' + fixed + '명</p>' +
      '<p class="muted">조건형 전환은 학급 전체 숫자만 봅니다. 누가 고쳤는지는 보여 주지 않습니다.</p>';

    var rank = [];
    for (var key in votes) {
      if (!votes.hasOwnProperty(key)) { continue; }
      rank.push({ key: key, n: votes[key], text: texts[key] || key });
    }
    rank.sort(function (a, b) { return b.n - a.n; });
    if (rank.length) {
      var bars = [];
      for (i = 0; i < rank.length && i < 8; i++) {
        bars.push({ label: String(rank[i].text).slice(0, 18), value: rank[i].n, color: "#00D45A" });
      }
      h += '<h3 style="margin-top:18px">표를 많이 받은 약속</h3>' + wiseBars(bars, 560);
    }

    h += '<h3 style="margin-top:18px">기준별 제안</h3><div class="scroll"><table>' +
      '<tr><th>기준</th><th>제안 수</th><th>문장</th></tr>';
    for (var c2 = 0; c2 < CRITERIA.length; c2++) {
      if (!byCrit[c2]) { continue; }
      var ss = [];
      for (i = 0; i < byCrit[c2].length; i++) {
        ss.push(esc(byCrit[c2][i].clause) + ' <span class="tag">' + esc(byCrit[c2][i].group) + '</span>');
      }
      h += '<tr><td>' + esc(CRITERIA[c2]) + '</td><td>' + byCrit[c2].length + '</td><td>' +
        ss.join("<br>") + '</td></tr>';
    }
    h += '</table></div>';
    h += '<p class="muted" style="margin-top:10px">소수 의견도 지우지 않습니다. ' +
      '판에 못 오른 제안은 교실 뒤에 그대로 붙여 둡니다.</p>';
    return h;
  }

  function presentHtml(list) {
    var votes = {}, texts = {}, i, j;
    for (i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (p.clause) { texts[list[i].key || ("k" + i)] = p.clause; }
      var vs = p.votes || [];
      for (j = 0; j < vs.length; j++) { votes[vs[j]] = (votes[vs[j]] || 0) + 1; }
    }
    var rank = [];
    for (var key in votes) {
      if (!votes.hasOwnProperty(key)) { continue; }
      rank.push({ n: votes[key], text: texts[key] || "" });
    }
    rank.sort(function (a, b) { return b.n - a.n; });
    var h = '<p class="big">우리 반 AI 약속</p>';
    if (!rank.length) {
      return h + '<p class="muted">아직 표가 모이지 않았어요.</p>';
    }
    for (i = 0; i < rank.length && i < 8; i++) {
      if (!rank[i].text) { continue; }
      h += '<p style="font-size:26px;margin:10px 0"><b>' + (i + 1) + '.</b> ' + esc(rank[i].text) +
        ' <span class="tag">' + rank[i].n + '표</span></p>';
    }
    return h;
  }
"""
