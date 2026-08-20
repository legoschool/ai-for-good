# -*- coding: utf-8 -*-
"""9차시 3단계 글쓰기 기록판.

여정형으로 만든다. 폼 하나가 아니라 화면 여덟 개를 지나간다.

  이야기 -> 글 공방(허브) -> 주제 고르기 -> 1단계 초고
  -> 질문 만들기 -> 2단계 기록 -> 3단계 다시 쓰기 -> 나란히 보기

설계서는 spec/18_웹앱_설계_L09.md 다.
단 하나의 경험은 AI 에게 던지는 말을 바꾸는 것이다.
"대신 써 줘"가 아니라 "무엇이 부족한지 짚어 줘"로 바꾸는 순간이 이 차시의 전부다.

자물쇠가 뼈대다. 다섯 문장을 넘겨야 질문 만들기가 열리고, 질문을 지어야 기록이 열리고,
기록을 남겨야 다시 쓰기가 열린다. 잠긴 타일을 누르면 열어야 할 화면으로 데려간다.

앱은 AI 를 부르지 않는다. 진짜 AI 는 교사 계정이나 모둠 공용 기기에서 쓴다.

40분 : 이야기 2 + 주제 3 + 초고 12 + 질문 6 + 기록 8 + 다시 쓰기 8 + 나란히 5
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  var TOPICS = [
    "급식을 남기지 않기",
    "우리 반 규칙 한 가지",
    "우리 동네에서 고칠 점",
    "화면 보는 시간 정하기"
  ];

  /* 전부 "짚어 달라"는 말이다. "고쳐 달라"는 말은 넣지 않는다. */
  var ASKS = [
    "내 글에서 근거가 부족한 곳은 어디인가요",
    "읽는 사람이 헷갈릴 문장은 무엇인가요",
    "내 주장과 반대되는 생각은 무엇인가요",
    "빠뜨린 중요한 내용이 있나요",
    "너무 긴 문장은 어디인가요"
  ];

  var BAD_ASKS = ["대신 써 줘", "대신 써줘", "완성해 줘", "완성해줘",
                  "다시 써 줘", "다시 써줘", "글 써 줘", "글 써줘"];

  /* 다듬기 놀이. 대신 써 달라는 말을 짚어 달라는 말로 바꾸는 연습이다. */
  var QUIZ = [
    {q:"어떤 말이 내 글을 지킬까요?",
     opts:["내 독후감 대신 써 줘", "내 독후감에서 근거가 약한 곳을 짚어 줘"], ans:1,
     why:"짚어 달라고 하면 고치는 사람은 나예요."},
    {q:"둘 중 무엇이 더 좋은 질문일까요?",
     opts:["이 글 멋지게 완성해 줘", "이 글에서 읽는 사람이 헷갈릴 곳이 어디야"], ans:1,
     why:"헷갈리는 곳을 알면 내가 고칠 수 있어요."},
    {q:"AI 가 고쳐 준 문장을 그대로 내면 어떻게 될까요?",
     opts:["내 글이 아니게 돼요", "더 좋은 내 글이 돼요"], ans:0,
     why:"설명할 수 있어야 내 글이에요."}
  ];

  var NOTE_ROWS = 5;

  var st = {
    topic: -1, free: "", asks: {}, take: {}, notes: ["", "", "", "", ""],
    quiz: 0, quizOk: 0, quizPick: -1, retort: 0, wasBad: false, badges: {},
    opened: false, saidRestore: false, classAvg: null
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

  /* ---------- 세기 ---------- */

  function sentences(text) {
    var t = String(text || "").replace(/[!?]/g, ".");
    var parts = t.split(".");
    var n = 0;
    for (var i = 0; i < parts.length; i++) {
      if (parts[i].replace(/[ ]/g, "").length > 1) { n++; }
    }
    return n;
  }

  function words(text) {
    var raw = String(text || "").split(/[ ,.]+/);
    var out = [];
    for (var i = 0; i < raw.length; i++) {
      var w = raw[i].trim();
      if (w.length > 1) { out.push(w); }
    }
    return out;
  }

  /* 낱말의 앞 두 글자로 견준다. 우리말은 조사와 어미가 붙어 모양이 자꾸 바뀐다.
     "급식을"과 "급식은"을 다른 낱말로 세면, 잘 고쳐 쓴 글이 처음 생각을 버린 글로 잘못 읽힌다. */
  function stems(text) {
    var w = words(text), out = [], i;
    for (i = 0; i < w.length; i++) { out.push(w[i].slice(0, 2)); }
    return out;
  }

  /* 처음 글에서 그대로 남은 낱말 비율. 점수가 아니라 되돌아보는 자료다. */
  function overlap(a, b) {
    var wa = stems(a), wb = stems(b);
    if (!wa.length || !wb.length) { return 0; }
    var seen = {}, same = 0, i, k;
    for (i = 0; i < wb.length; i++) { seen[wb[i]] = true; }
    for (k = 0; k < wa.length; k++) { if (seen[wa[k]]) { same++; } }
    return Math.round(same * 100 / wa.length);
  }

  function val(id) { return $(id) && $(id).value ? String($(id).value).trim() : ""; }

  function countKeys(obj) {
    var n = 0, k;
    for (k in obj) { if (obj.hasOwnProperty(k) && obj[k]) { n++; } }
    return n;
  }

  function topicName() {
    if (st.topic >= 0) { return TOPICS[st.topic]; }
    return st.free || val("free") || "자유 주제";
  }

  /* ---------- 자물쇠 ---------- */

  function lock1() { return sentences(val("wr1")) >= 5; }

  function lock2() { return lock1() && (countKeys(st.asks) > 0 || val("myask").length > 3); }

  function lock3() { return lock2() && noteText().length > 4; }

  function lockCount() {
    var n = 0;
    if (lock1()) { n++; }
    if (lock2()) { n++; }
    if (lock3()) { n++; }
    return n;
  }

  /* ---------- 그림 ---------- */
  /* 이 차시에만 쓰는 그림이라 여기에 둔다. */

  function doorSvg(open) {
    var lockColor = ["#FF6B5A", "#FFE24B", "#00D45A"];
    var n = open;
    var locks = "";
    for (var i = 0; i < 3; i++) {
      var fill = i < n ? "#00D45A" : "#fff";
      locks += '<g><rect x="196" y="' + (30 + i * 30) + '" width="26" height="20" rx="4" fill="' +
        fill + '" stroke="#111" stroke-width="3"/>' +
        '<path d="M203 ' + (30 + i * 30) + ' v-7 a6 6 0 0 1 12 0 v7" fill="none" stroke="#111" stroke-width="3"/></g>';
    }
    return '<svg class="ws-scene" viewBox="0 0 320 120" aria-hidden="true">' +
      '<rect width="320" height="120" fill="#F6F7F9"/>' +
      '<rect x="18" y="16" width="160" height="92" rx="12" fill="#fff" stroke="#111" stroke-width="3"/>' +
      '<text x="98" y="52" font-size="15" font-weight="800" text-anchor="middle" fill="#111">글 공방</text>' +
      '<path d="M44 70h108M44 84h80" stroke="#111" stroke-width="3" stroke-linecap="round"/>' +
      '<rect x="188" y="14" width="42" height="96" rx="8" fill="' + lockColor[Math.min(n, 2)] +
      '" stroke="#111" stroke-width="3"/>' +
      locks +
      '<circle cx="272" cy="44" r="15" fill="#2B59E0" stroke="#111" stroke-width="3"/>' +
      '<path d="M250 104c0-13 10-20 22-20s22 7 22 20z" fill="#2B59E0" stroke="#111" stroke-width="3"/>' +
      '<text x="272" y="49" font-size="13" font-weight="800" text-anchor="middle" fill="#fff">나</text>' +
      '</svg>';
  }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function topicInner() {
    var h = '<div class="card"><span class="pill">주제</span>' +
      '<h2 style="margin-top:10px">오늘은 무엇에 대해 쓸까요</h2>' +
      '<p class="muted">고른 주제로 다섯 문장을 먼저 써요.</p><div style="margin-top:10px">';
    var i;
    for (i = 0; i < TOPICS.length; i++) {
      h += '<button type="button" class="chip tp" data-p="' + i + '">' + esc(TOPICS[i]) + '</button>';
    }
    h += '</div><label for="free">직접 정하고 싶으면 여기에 써요</label>' +
      '<input id="free" maxlength="40" placeholder="예: 우리 학교 도서관 이용 시간">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-draft" class="ghost">초고 쓰러 가기</button>' +
      '<button type="button" class="plain back">공방으로</button></div></div>';
    return h;
  }

  function askInner() {
    var h = '<div class="card"><span class="pill">질문</span>' +
      '<h2 style="margin-top:10px">AI 에게 무엇을 물을까요</h2>' +
      '<p class="muted">고쳐 달라고 하지 않아요. 무엇이 부족한지만 물어요.</p>' +
      '<div id="quizbox" style="margin-top:10px"></div>' +
      '<h3 style="margin-top:18px">물어볼 질문을 골라요</h3><div style="margin-top:8px">';
    var i;
    for (i = 0; i < ASKS.length; i++) {
      h += '<button type="button" class="chip ak" data-a="' + i + '">' + esc(ASKS[i]) + '</button>';
    }
    h += '</div><label for="myask">내가 직접 만든 질문</label>' +
      '<input id="myask" maxlength="80" placeholder="예: 내 근거 중 약한 것은 무엇인가요">' +
      '<p class="muted" id="askmsg" style="margin-top:8px"></p>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-note" class="ghost">기록하러 가기</button>' +
      '<button type="button" class="plain back">공방으로</button></div></div>';
    return h;
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">자물쇠 세 개가 달린 글 공방</h2>' +
      doorSvg(0) +
      '<p style="margin-top:10px">빈 종이 앞에서 AI 부터 켜면 내 글이 아니게 돼요.</p>' +
      '<p style="margin-top:8px">오늘 여러분은 <b>작가</b>예요. AI 는 짚어 주는 <b>조언가</b>고요.</p>' +
      '<p class="muted" style="margin-top:8px">우리 반 약속 2조항, 내 생각 먼저.</p>' +
      '<p class="muted">첫 자물쇠는 내 생각 다섯 문장으로 열려요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">공방으로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>글 공방</h2>' +
      '<p class="muted">앞 단계를 마쳐야 다음 자물쇠가 열려요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="b-topic">' + wiseIcon("star", 30) +
      '<span>1. 주제 고르기</span><small id="s-topic">무엇에 대해 쓸까요</small></button>' +
      '<button type="button" class="tile" id="b-draft">' + wiseIcon("write", 30) +
      '<span>2. 1단계 초고</span><small id="s-draft">내 생각 다섯 문장</small></button>' +
      '<button type="button" class="tile" id="b-ask">' + wiseIcon("talk", 30) +
      '<span>3. 질문 만들기</span><small id="s-ask">짚어 달라고 물어요</small></button>' +
      '<button type="button" class="tile" id="b-note">' + wiseIcon("rec", 30) +
      '<span>4. 2단계 기록</span><small id="s-note">AI 가 짚어 준 점</small></button>' +
      '<button type="button" class="tile" id="b-rewrite">' + wiseIcon("again", 30) +
      '<span>5. 3단계 다시 쓰기</span><small id="s-rewrite">내 말로 고쳐 써요</small></button>' +
      '<button type="button" class="tile" id="b-compare">' + wiseIcon("check", 30) +
      '<span>6. 나란히 보기</span><small id="s-compare">무엇이 달라졌나요</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>자물쇠와 배지</h3>' +
      '<div id="locks" style="margin-top:8px"></div>' +
      '<div id="badges" class="row" style="margin-top:10px"></div></div>');

    h += q("topic", topicInner());

    h += q("draft",
      '<div class="card"><span class="pill">1단계</span>' +
      '<h2 style="margin-top:10px">내 생각 먼저 쓰기</h2>' +
      '<p class="muted" id="topicline">주제를 먼저 고르면 여기에 보여요.</p>' +
      '<p class="muted">맞춤법은 신경 쓰지 않아도 괜찮아요. 다섯 문장을 넘겨 봐요.</p>' +
      '<textarea id="wr1" maxlength="900" placeholder="내 주장과 그렇게 생각한 까닭을 써요"></textarea>' +
      '<p class="muted" id="m0">0문장</p>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-ask" class="ghost">질문 만들러 가기</button>' +
      '<button type="button" class="plain back">공방으로</button></div>' +
      '<div class="safe">친구 이야기나 사람 이름을 쓰지 않아요. ' +
      '이름, 사진 같은 개인정보는 넣지 않아요.</div></div>');

    h += q("ask", askInner());

    h += q("note",
      '<div class="card"><span class="pill">2단계</span>' +
      '<h2 style="margin-top:10px">AI 가 짚어 준 점을 적어요</h2>' +
      '<p class="muted">한 줄에 하나씩 적어요. 줄마다 받아들일지 정해요.</p>' +
      '<div id="notes" style="margin-top:10px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-rewrite" class="ghost">다시 쓰러 가기</button>' +
      '<button type="button" class="plain back">공방으로</button></div></div>');

    h += q("rewrite",
      '<div class="card"><span class="pill">3단계</span>' +
      '<h2 style="margin-top:10px">내 말로 다시 쓰기</h2>' +
      '<div class="row" style="margin-top:8px">' +
      '<button type="button" id="peek-first" class="plain">처음 글 펼쳐 보기</button></div>' +
      '<div id="firstbox" class="note hide" style="margin-top:10px"></div>' +
      '<p class="muted" style="margin-top:10px">AI 문장을 그대로 옮기지 않아요. 내 말로 써요.</p>' +
      '<textarea id="wr4" maxlength="900" placeholder="짚어 준 것 중에서 받아들일 것만 넣어 다시 써요"></textarea>' +
      '<div id="ovbox" style="margin-top:10px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-compare" class="ghost">나란히 보러 가기</button>' +
      '<button type="button" class="plain back">공방으로</button></div></div>');

    h += q("compare",
      '<div class="card"><span class="pill">나란히</span>' +
      '<h2 style="margin-top:10px">무엇이 달라졌나요</h2>' +
      '<div id="diff"></div>' +
      '<label for="wr5">고치면서 알게 된 것</label>' +
      '<input id="wr5" maxlength="80" placeholder="예: 자료를 넣으니 주장이 단단해졌습니다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">작가 카드로 저장</button>' +
      '<button type="button" id="peek" class="ghost">우리 반과 견주기</button>' +
      '<button type="button" class="plain back">공방으로</button></div>' +
      '<div id="classbox" style="margin-top:12px"></div></div>');

    return h;
  }

  /* ---------- 주제 ---------- */

  function markTopics() {
    var tp = document.querySelectorAll("#activity .tp"), i;
    for (i = 0; i < tp.length; i++) {
      tp[i].className = "chip tp" + (Number(tp[i].getAttribute("data-p")) === st.topic ? " on" : "");
    }
    if ($("topicline")) {
      $("topicline").textContent = "오늘 주제 : " + topicName();
    }
  }

  /* ---------- 다듬기 놀이 ---------- */

  function quizHtml() {
    if (st.quiz >= QUIZ.length) {
      return '<p class="ok">다듬기 놀이 끝. ' + st.quizOk + ' / ' + QUIZ.length + ' 맞혔어요.</p>' +
        '<p class="muted">이제 진짜 질문을 골라 봐요.</p>';
    }
    var item = QUIZ[st.quiz];
    var h = '<p class="muted">다듬기 놀이 ' + (st.quiz + 1) + ' / ' + QUIZ.length + '</p>' +
      '<h3 style="margin:8px 0 10px">' + esc(item.q) + '</h3>';
    var i;
    for (i = 0; i < item.opts.length; i++) {
      var on = (st.quizPick >= 0 && i === item.ans) ? " on" : "";
      h += '<button type="button" class="chip qz' + on + '" data-o="' + i + '">' +
        esc(item.opts[i]) + '</button>';
    }
    if (st.quizPick >= 0) {
      h += '<p class="' + (st.quizPick === item.ans ? "ok" : "warn") + '" style="margin-top:8px">' +
        (st.quizPick === item.ans ? "맞았어요. " : "다시 봐요. ") + esc(item.why) + '</p>' +
        '<div class="row" style="margin-top:8px">' +
        '<button type="button" id="quiz-next">다음</button></div>';
    }
    return h;
  }

  function bindQuiz() {
    if (!$("quizbox")) { return; }
    $("quizbox").innerHTML = quizHtml();
    var opts = document.querySelectorAll("#activity .qz"), i;
    for (i = 0; i < opts.length; i++) {
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
        if (st.quiz >= QUIZ.length && st.quizOk === QUIZ.length) { award("질문 장인"); }
        paintHub();
      };
    }
  }

  function markAsks() {
    var ak = document.querySelectorAll("#activity .ak"), i, a;
    for (i = 0; i < ak.length; i++) {
      a = ak[i].getAttribute("data-a");
      ak[i].className = "chip ak" + (st.asks[a] ? " on" : "");
    }
  }

  /* "대신 써 줘"는 곧바로 되짚는다. 이 되짚기가 9차시의 핵심 장면이다. */
  function checkAsk() {
    if (!$("askmsg")) { return; }
    var ask = val("myask");
    var bad = "", i;
    for (i = 0; i < BAD_ASKS.length; i++) {
      if (ask.indexOf(BAD_ASKS[i]) >= 0) { bad = BAD_ASKS[i]; }
    }
    if (bad) {
      if (!st.wasBad) { st.retort += 1; }
      st.wasBad = true;
      $("askmsg").innerHTML = '<span class="warn">"' + esc(bad) +
        '"는 대신 써 달라는 부탁이에요.<br>"어디가 부족한지 짚어 줘"로 바꾸어 봐요.</span>';
    } else if (ask) {
      st.wasBad = false;
      $("askmsg").innerHTML = '<span class="ok">짚어 달라는 질문이에요. 좋아요.</span>';
    } else {
      st.wasBad = false;
      $("askmsg").textContent = "";
    }
  }

  /* ---------- 2단계 기록 ---------- */

  function readNotes() {
    var i;
    for (i = 0; i < NOTE_ROWS; i++) {
      if ($("nt" + i)) { st.notes[i] = val("nt" + i); }
    }
    return st.notes;
  }

  function noteText() {
    readNotes();
    var out = [], i;
    for (i = 0; i < NOTE_ROWS; i++) {
      if (st.notes[i]) { out.push(st.notes[i]); }
    }
    return out.join(" / ");
  }

  function takeSummary() {
    var yes = [], no = [], i;
    for (i = 0; i < NOTE_ROWS; i++) {
      if (!st.notes[i]) { continue; }
      if (st.take[i] === true) { yes.push(st.notes[i]); }
      if (st.take[i] === false) { no.push(st.notes[i] + (val("wy" + i) ? "(" + val("wy" + i) + ")" : "")); }
    }
    return "받아들일 것 : " + (yes.length ? yes.join(", ") : "없음") +
      " / 받아들이지 않을 것 : " + (no.length ? no.join(", ") : "없음");
  }

  function notesHtml() {
    var h = "", i;
    for (i = 0; i < NOTE_ROWS; i++) {
      h += '<div class="card" style="margin:0 0 10px;padding:14px">' +
        '<label for="nt' + i + '">' + (i + 1) + '번째로 짚어 준 점</label>' +
        '<input id="nt' + i + '" maxlength="80" value="' + esc(st.notes[i] || "") +
        '" placeholder="예: 근거에 자료가 없어요">' +
        '<div class="row" style="margin-top:8px">' +
        '<button type="button" class="chip it' + (st.take[i] === true ? " on" : "") +
        '" data-n="' + i + '" data-v="1" style="width:auto;margin:0">받아들일래요</button>' +
        '<button type="button" class="chip it' + (st.take[i] === false ? " on" : "") +
        '" data-n="' + i + '" data-v="0" style="width:auto;margin:0">안 받아들일래요</button>' +
        '</div>';
      if (st.take[i] === false) {
        h += '<label for="wy' + i + '">안 받아들이는 까닭</label>' +
          '<input id="wy' + i + '" maxlength="60" placeholder="예: 어려운 낱말은 내 말이 아니에요">';
      }
      h += '</div>';
    }
    return h;
  }

  function paintNotes() {
    if (!$("notes")) { return; }
    var whys = {}, i;
    for (i = 0; i < NOTE_ROWS; i++) {
      if ($("wy" + i)) { whys[i] = val("wy" + i); }
    }
    readNotes();
    $("notes").innerHTML = notesHtml();
    for (i = 0; i < NOTE_ROWS; i++) {
      if ($("wy" + i) && whys[i]) { $("wy" + i).value = whys[i]; }
      if ($("nt" + i)) { $("nt" + i).oninput = onType; }
    }
    bindNotes();
  }

  function bindNotes() {
    var its = document.querySelectorAll("#activity .it"), i;
    for (i = 0; i < its.length; i++) {
      its[i].onclick = function () {
        var n = Number(this.getAttribute("data-n"));
        var v = this.getAttribute("data-v") === "1";
        st.take[n] = (st.take[n] === v) ? undefined : v;
        paintNotes();
        paintHub();
      };
    }
  }

  /* ---------- 3단계 ---------- */

  function paintFirst() {
    if (!$("firstbox")) { return; }
    var a = val("wr1");
    $("firstbox").innerHTML = a
      ? '<b>처음 쓴 글</b><br>' + esc(a)
      : '<b>처음 쓴 글이 아직 없어요.</b>';
  }

  function paintOverlap() {
    if (!$("ovbox")) { return; }
    var a = val("wr1"), b = val("wr4");
    if (!a || !b) {
      $("ovbox").innerHTML = '<p class="muted">다시 쓰기 시작하면 여기에 견줌이 나와요.</p>';
      return;
    }
    var ov = overlap(a, b);
    var h = '<p>처음 글에서 그대로 남은 낱말 <b>' + ov + '%</b></p>' + barHtml(ov, 100);
    if (ov > 80) {
      h += '<p class="warn">거의 그대로예요. 짚어 준 것을 반영해 봐요.</p>';
    } else if (ov < 10) {
      h += '<p class="muted">많이 달라졌어요. 내 주장은 그대로인지 살펴봐요.</p>';
    } else {
      h += '<p class="ok">내 생각을 지키면서 고쳤어요.</p>';
    }
    $("ovbox").innerHTML = h;
  }

  /* ---------- 나란히 보기 ---------- */

  function paintDiff() {
    if (!$("diff")) { return; }
    var a = val("wr1"), b = val("wr4");
    if (!a || !b) {
      $("diff").innerHTML = '<p class="muted">1단계와 3단계를 모두 쓰면 여기에서 견주어 볼 수 있어요.</p>';
      return;
    }
    var ov = overlap(a, b);
    var h = '<div class="scroll"><table><tr><th>무엇을</th><th>1단계</th><th>3단계</th></tr>' +
      '<tr><td>문장 수</td><td>' + sentences(a) + '문장</td><td>' + sentences(b) + '문장</td></tr>' +
      '<tr><td>글자 수</td><td>' + a.length + '자</td><td>' + b.length + '자</td></tr>' +
      '<tr><td>받아들인 점</td><td>-</td><td>' + takeCount(true) + '개</td></tr>' +
      '<tr><td>안 받아들인 점</td><td>-</td><td>' + takeCount(false) + '개</td></tr>' +
      '</table></div>';
    h += '<p style="margin-top:10px">그대로 남은 낱말 <b>' + ov + '%</b></p>' + barHtml(ov, 100);
    h += '<div class="note">이 글은 누구의 글인가요. 설명할 수 있으면 내 글이에요.</div>';
    $("diff").innerHTML = h;
  }

  function takeCount(v) {
    var n = 0, i;
    for (i = 0; i < NOTE_ROWS; i++) {
      if (st.notes[i] && st.take[i] === v) { n++; }
    }
    return n;
  }

  function peek() {
    if (!$("classbox")) { return; }
    if (me.solo) {
      $("classbox").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 기록이 없어요. ' +
        '세 단계는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    if ($("peek")) { wiseButtonBusy($("peek"), true, "불러오는 중"); }
    $("classbox").innerHTML = wiseSpinner("우리 반 기록을 불러오는 중이에요") + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      if ($("peek")) { wiseButtonBusy($("peek"), false); }
      var n = 0, ovSum = 0, s0Sum = 0, s3Sum = 0, k, p;
      for (k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        p = data[k].payload || {};
        if (!p.f3) { continue; }
        n++;
        ovSum += p.overlap || 0;
        s0Sum += p.s0 || 0;
        s3Sum += p.s3 || 0;
      }
      if (!n) {
        $("classbox").innerHTML = '<p class="muted">아직 우리 반 기록이 모이지 않았어요.</p>';
        return;
      }
      var mineOv = overlap(val("wr1"), val("wr4"));
      var h = '<p>3단계까지 마친 친구 ' + n + '명이에요.</p>';
      h += wiseBars([
        { label: "우리 반 겹침", value: Math.round(ovSum / n) },
        { label: "내 겹침", value: mineOv }
      ], 560);
      h += '<p class="muted">우리 반 겹침 평균 ' + Math.round(ovSum / n) + '% · 내 겹침 ' +
        mineOv + '%</p>';
      h += '<p class="muted">1단계 평균 ' + Math.round(s0Sum / n) + '문장, 3단계 평균 ' +
        Math.round(s3Sum / n) + '문장이에요.</p>';
      $("classbox").innerHTML = h;
      st.classAvg = { n: n, ov: Math.round(ovSum / n) };
    })["catch"](function () {
      if ($("peek")) { wiseButtonBusy($("peek"), false); }
      $("classbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
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

  function doneSteps() {
    var n = 0;
    if (st.topic >= 0 || val("free")) { n++; }
    if (lock1()) { n++; }
    if (lock2()) { n++; }
    if (lock3()) { n++; }
    if (val("wr4").length >= 20) { n++; }
    if (val("wr5").length >= 5) { n++; }
    return n;
  }

  function paintHud() {
    wiseHud([
      { label: "오늘 할 일", done: doneSteps(), total: 6 },
      { label: "1단계 문장", done: Math.min(sentences(val("wr1")), 5), total: 5 },
      { label: "열린 자물쇠", done: lockCount(), total: 3 }
    ]);
  }

  function lockLine(open, text) {
    return '<p class="' + (open ? "ok" : "muted") + '">' +
      (open ? "열림" : "잠김") + " · " + esc(text) + '</p>';
  }

  function paintHub() {
    if (!$("s-draft")) { return; }
    var s0 = sentences(val("wr1"));

    $("s-topic").textContent = (st.topic >= 0 || val("free")) ? topicName() : "무엇에 대해 쓸까요";
    $("s-draft").textContent = s0 ? (s0 + "문장 썼어요") : "내 생각 다섯 문장";
    var askN = countKeys(st.asks) + (val("myask").length > 3 ? 1 : 0);
    $("s-ask").textContent = lock1()
      ? (askN ? ("질문 " + askN + "개") : "짚어 달라고 물어요")
      : "잠김 · 다섯 문장이 먼저예요";
    $("s-note").textContent = lock2()
      ? (noteRowCount() ? ("적은 줄 " + noteRowCount() + "개") : "AI 가 짚어 준 점")
      : "잠김 · 질문을 먼저 지어요";
    $("s-rewrite").textContent = lock3()
      ? (val("wr4").length ? (val("wr4").length + "자 썼어요") : "내 말로 고쳐 써요")
      : "잠김 · 기록이 먼저예요";
    $("s-compare").textContent = val("wr5") ? "달라진 점을 썼어요" : "무엇이 달라졌나요";

    var tiles = [["b-topic", st.topic >= 0 || !!val("free")], ["b-draft", lock1()],
      ["b-ask", lock2()], ["b-note", lock3()],
      ["b-rewrite", val("wr4").length >= 20], ["b-compare", val("wr5").length >= 5]];
    var i;
    for (i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if ($("locks")) {
      $("locks").innerHTML =
        lockLine(lock1(), "첫째 자물쇠 : 내 생각 다섯 문장") +
        lockLine(lock2(), "둘째 자물쇠 : 짚어 달라는 질문") +
        lockLine(lock3(), "셋째 자물쇠 : AI 가 짚어 준 점 기록");
    }

    if (lock1()) { award("첫 자물쇠"); }
    if (st.quizOk >= QUIZ.length) { award("질문 장인"); }
    if (val("wr4").length >= 20) { award("고쳐 쓴 작가"); }
    if (val("wr5").length >= 5) { award("되돌아본 작가"); }

    var names = badgeList(), h = "", b;
    for (b = 0; b < names.length; b++) {
      h += '<span class="pill">' + esc(names[b]) + '</span> ';
    }
    if ($("badges")) {
      $("badges").innerHTML = names.length ? h
        : '<span class="muted">아직 없어요. 다섯 문장을 넘기면 첫 배지를 받아요.</span>';
    }
    paintHud();
  }

  function noteRowCount() {
    readNotes();
    var n = 0, i;
    for (i = 0; i < NOTE_ROWS; i++) { if (st.notes[i]) { n++; } }
    return n;
  }

  /* ---------- 흐름 ---------- */

  var NOTES_TEXT = {
    story: "빈 종이 앞에서 AI 부터 켜지 않아요.",
    hub: "자물쇠 세 개를 차례로 열어요.",
    topic: "쓰고 싶은 주제를 하나 골라요.",
    draft: "내 생각을 다섯 문장 넘게 써요.",
    ask: "고쳐 달라 말고 짚어 달라고 물어요.",
    note: "AI 가 짚어 준 것을 한 줄씩 적어요.",
    rewrite: "받아들일 것만 넣어 내 말로 써요.",
    compare: "세 글을 견주고 달라진 점을 써요."
  };

  function goLocked(id) {
    if (id === "ask" && !lock1()) {
      wiseToast("먼저 다섯 문장을 넘겨야 열려요.");
      wiseGo("draft");
      return true;
    }
    if (id === "note" && !lock2()) {
      wiseToast(lock1() ? "질문을 먼저 골라요." : "먼저 다섯 문장을 넘겨야 열려요.");
      wiseGo(lock1() ? "ask" : "draft");
      return true;
    }
    if (id === "rewrite" && !lock3()) {
      wiseToast(lock2() ? "짚어 준 점을 한 줄 적어요." : "앞 자물쇠가 아직 잠겨 있어요.");
      wiseGo(lock2() ? "note" : (lock1() ? "ask" : "draft"));
      return true;
    }
    return false;
  }

  function activityEnter(id) {
    if (NOTES_TEXT[id]) { wiseNote(NOTES_TEXT[id]); }
    if (id === "hub") { paintHub(); }
    if (id === "topic") { markTopics(); }
    if (id === "draft") { gate(); }
    if (id === "ask") { bindQuiz(); markAsks(); checkAsk(); }
    if (id === "note") { paintNotes(); }
    if (id === "rewrite") {
      paintFirst();
      if ($("ovbox")) { $("ovbox").innerHTML = wiseSpinner("처음 글과 견주는 중이에요"); }
      softDelay(paintOverlap, 260);
    }
    if (id === "compare") {
      if ($("diff")) { $("diff").innerHTML = wiseSpinner("세 글을 나란히 놓는 중이에요") + wiseSkeleton(3); }
      softDelay(paintDiff, 300);
    }
  }

  function onType() {
    gate();
    paintHub();
  }

  function gate() {
    var s0 = sentences(val("wr1"));
    if ($("m0")) {
      $("m0").innerHTML = s0 + "문장" + (s0 >= 5
        ? ' <span class="ok">첫 자물쇠가 열렸어요</span>'
        : ' <span class="warn">다섯 문장을 넘겨 주세요</span>');
    }
    paintOverlap();
  }

  function activityInit(saved) {
    var i;

    if (saved) {
      if (saved.topic !== undefined && saved.topic >= 0) { st.topic = saved.topic; }
      if (saved.asks) { st.asks = saved.asks; }
      if (saved.take) { st.take = saved.take; }
      if (saved.notes) { st.notes = saved.notes; }
      if (saved.quizOk) { st.quizOk = saved.quizOk; }
      var fill = [["free", saved.free], ["wr1", saved.f0], ["myask", saved.myask],
        ["wr4", saved.f3], ["wr5", saved.f4]];
      for (i = 0; i < fill.length; i++) {
        if (fill[i][1] && $(fill[i][0])) { $(fill[i][0]).value = fill[i][1]; }
      }
      if (saved.f0 || saved.notes) {
        st.saidRestore = true;
        softDelay(function () {
          wiseToast("지난번에 쓰던 글이 남아 있어요. 이어서 하면 돼요.");
        }, 700);
      }
    }

    var ids = ["wr1", "wr4", "wr5", "free", "myask"];
    for (i = 0; i < ids.length; i++) {
      if ($(ids[i])) { $(ids[i]).oninput = onType; }
    }
    if ($("myask")) {
      $("myask").oninput = function () { checkAsk(); paintHub(); };
    }
    if ($("free")) {
      $("free").oninput = function () { st.free = val("free"); markTopics(); paintHub(); };
    }

    var tps = document.querySelectorAll("#activity .tp");
    for (i = 0; i < tps.length; i++) {
      tps[i].onclick = function () {
        st.topic = Number(this.getAttribute("data-p"));
        markTopics();
        paintHub();
        wiseToast("주제를 정했어요 : " + TOPICS[st.topic]);
      };
    }

    var aks = document.querySelectorAll("#activity .ak");
    for (i = 0; i < aks.length; i++) {
      aks[i].onclick = function () {
        var a = this.getAttribute("data-a");
        st.asks[a] = !st.asks[a];
        markAsks();
        paintHub();
      };
    }

    if ($("go-hub")) {
      $("go-hub").onclick = function () {
        if (st.opened) { wiseGo("hub"); return; }
        st.opened = true;
        wiseBusy(true, "공방 문을 여는 중");
        softDelay(function () { wiseBusy(false); wiseGo("hub"); }, 520);
      };
    }
    if ($("b-topic")) { $("b-topic").onclick = function () { wiseGo("topic"); }; }
    if ($("b-draft")) { $("b-draft").onclick = function () { wiseGo("draft"); }; }
    if ($("b-ask")) { $("b-ask").onclick = function () { if (!goLocked("ask")) { wiseGo("ask"); } }; }
    if ($("b-note")) { $("b-note").onclick = function () { if (!goLocked("note")) { wiseGo("note"); } }; }
    if ($("b-rewrite")) {
      $("b-rewrite").onclick = function () { if (!goLocked("rewrite")) { wiseGo("rewrite"); } };
    }
    if ($("b-compare")) { $("b-compare").onclick = function () { wiseGo("compare"); }; }

    if ($("to-draft")) { $("to-draft").onclick = function () { wiseGo("draft"); }; }
    if ($("to-ask")) { $("to-ask").onclick = function () { if (!goLocked("ask")) { wiseGo("ask"); } }; }
    if ($("to-note")) { $("to-note").onclick = function () { if (!goLocked("note")) { wiseGo("note"); } }; }
    if ($("to-rewrite")) {
      $("to-rewrite").onclick = function () { if (!goLocked("rewrite")) { wiseGo("rewrite"); } };
    }
    if ($("to-compare")) { $("to-compare").onclick = function () { wiseGo("compare"); }; }

    if ($("peek-first")) {
      $("peek-first").onclick = function () {
        var open = $("firstbox").className.indexOf("hide") < 0;
        paintFirst();
        $("firstbox").className = open ? "note hide" : "note";
        this.textContent = open ? "처음 글 펼쳐 보기" : "처음 글 접기";
      };
    }

    if ($("save-card")) {
      $("save-card").onclick = function () {
        if (val("wr1").length < 10) {
          wiseToast("먼저 1단계 초고를 써요.");
          wiseGo("draft");
          return;
        }
        var btn = this;
        wiseBusy(true, "작가 카드를 만드는 중");
        softDelay(function () {
          wiseBusy(false);
          wiseButtonBusy(btn, false);
          saveCard();
        }, 500);
      };
    }

    if ($("peek")) { $("peek").onclick = peek; }

    var backs = document.querySelectorAll("#activity .back");
    for (i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }

    markTopics();
    markAsks();
    paintNotes();
    wiseNote(NOTES_TEXT.story);
    wiseGo("story");
    gate();
    paintHub();
  }

  function saveCard() {
    var a = val("wr1"), b = val("wr4");
    wiseCardPng("3단계 글쓰기 " + me.nick, [
      "주제 " + topicName(),
      "1단계 " + sentences(a) + "문장  3단계 " + sentences(b) + "문장",
      "받아들인 점 " + takeCount(true) + "개  안 받아들인 점 " + takeCount(false) + "개",
      "그대로 남은 낱말 " + overlap(a, b) + "%",
      "이 글은 내 글이다. 왜 이렇게 썼는지 말할 수 있다."
    ], "wise_l09_" + me.nick);
  }

  function activityDraft() {
    return {
      topic: st.topic, free: val("free"), asks: st.asks, take: st.take,
      notes: readNotes(), quizOk: st.quizOk,
      f0: val("wr1"), myask: val("myask"), f3: val("wr4"), f4: val("wr5")
    };
  }

  function activityAutofill() {
    st.topic = 0;
    st.asks = { "0": true };
    st.take = { 0: true, 1: false };
    st.notes = ["근거에 자료가 없어요", "문장이 너무 길어요", "", "", ""];
    st.quiz = QUIZ.length;
    st.quizOk = QUIZ.length;
    if ($("wr1")) {
      $("wr1").value = "나는 급식을 남기지 말아야 한다고 생각합니다. 음식을 만드는 데 힘이 듭니다. " +
        "버려진 음식은 쓰레기가 됩니다. 돈도 낭비됩니다. 배고픈 사람도 있습니다.";
    }
    if ($("nt0")) { $("nt0").value = "근거에 자료가 없어요"; }
    if ($("nt1")) { $("nt1").value = "문장이 너무 길어요"; }
    if ($("myask")) { $("myask").value = "내 근거 중 약한 것은 무엇인가요"; }
    if ($("wr4")) {
      $("wr4").value = "급식을 남기지 않으려면 먹을 만큼만 받는 것이 좋습니다. " +
        "우리 학교 잔반을 재어 보니 하루 30킬로그램이 버려졌습니다. 먼저 양을 조절해 봅시다.";
    }
    if ($("wr5")) { $("wr5").value = "자료를 넣으니 주장이 단단해졌습니다."; }
  }

  function activityCollect() {
    var f0 = val("wr1");
    if (sentences(f0) < 5) {
      $("w-msg").innerHTML = '<span class="warn">1단계를 다섯 문장 넘게 써야 해요. 지금 ' +
        sentences(f0) + '문장이에요. 초고 화면으로 데려갈게요.</span>';
      wiseGo("draft");
      return null;
    }
    var f1 = noteText();
    if (f1.length < 5) {
      $("w-msg").innerHTML = '<span class="warn">AI 가 짚어 준 점을 한 줄 적어 주세요. ' +
        '2단계 기록 화면으로 데려갈게요.</span>';
      wiseGo(lock2() ? "note" : "ask");
      return null;
    }
    var f3 = val("wr4");
    if (f3.length < 20) {
      $("w-msg").innerHTML = '<span class="warn">3단계 글을 내 말로 다시 써 주세요. ' +
        '다시 쓰기 화면으로 데려갈게요.</span>';
      wiseGo("rewrite");
      return null;
    }
    var f4 = val("wr5");
    if (f4.length < 5) {
      $("w-msg").innerHTML = '<span class="warn">고치면서 알게 된 것을 한 줄 써 주세요. ' +
        '나란히 보기 화면으로 데려갈게요.</span>';
      wiseGo("compare");
      return null;
    }

    var picks = [], k;
    for (k in st.asks) {
      if (st.asks.hasOwnProperty(k) && st.asks[k]) { picks.push(ASKS[k]); }
    }
    var ov = overlap(f0, f3);
    var badges = badgeList();

    wiseCelebrate("세 자물쇠를 다 열었어요", [
      "주제 <b>" + esc(topicName()) + "</b>",
      "1단계 " + sentences(f0) + "문장에서 3단계 " + sentences(f3) + "문장으로",
      ov > 80 ? "그대로 남은 낱말이 " + ov + "% 예요. 조금 더 고쳐 봐도 좋아요."
        : "그대로 남은 낱말 " + ov + "% · 내 생각을 지키며 고쳤어요",
      "받은 배지 " + (badges.length ? badges.join(", ") : "없음")
    ], "좋아요");

    return {
      topic: topicName(), topicIndex: st.topic,
      f0: f0, asks: picks, myask: val("myask"),
      f1: f1, notes: st.notes, takeYes: takeCount(true), takeNo: takeCount(false),
      f2: takeSummary(), f3: f3, f4: f4,
      s0: sentences(f0), s3: sentences(f3), len0: f0.length, len3: f3.length,
      overlap: ov, quizOk: st.quizOk, retort: st.retort, badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function gather(list) {
    var g = { step1: 0, step2: 0, step3: 0, ovSum: 0, tooSame: 0, retort: 0,
      askCount: {}, topics: {} }, i, p, k, a;
    for (i = 0; i < list.length; i++) {
      p = list[i].payload || {};
      if (p.f0) { g.step1++; }
      if (p.f1) { g.step2++; }
      if (!p.f3) { continue; }
      g.step3++;
      g.ovSum += p.overlap || 0;
      if ((p.overlap || 0) > 80) { g.tooSame++; }
      g.retort += p.retort || 0;
      a = p.asks || [];
      for (k = 0; k < a.length; k++) { g.askCount[a[k]] = (g.askCount[a[k]] || 0) + 1; }
      if (p.topic) { g.topics[p.topic] = (g.topics[p.topic] || 0) + 1; }
    }
    return g;
  }

  function teacherSummary(list) {
    var g = gather(list);
    var h = '<p class="muted">1단계 ' + g.step1 + '명 · 2단계 ' + g.step2 + '명 · 3단계 ' +
      g.step3 + '명 · 되짚은 질문 ' + g.retort + '회</p>';

    h += wiseBars([
      { label: "1단계까지", value: g.step1 },
      { label: "2단계까지", value: g.step2 },
      { label: "3단계까지", value: g.step3 }
    ], 560);

    if (g.step3) {
      h += '<p class="muted">처음 글이 그대로 남은 비율 평균 ' +
        Math.round(g.ovSum / g.step3) + '%</p>';
    }
    if (g.tooSame) {
      h += '<p class="warn">거의 고치지 않은 글 ' + g.tooSame +
        '편이 있다. 무엇을 반영했는지 물어본다.</p>';
    }

    var rows = [], key;
    for (key in g.askCount) {
      if (g.askCount.hasOwnProperty(key)) {
        rows.push({ label: key.slice(0, 14), value: g.askCount[key] });
      }
    }
    if (rows.length) {
      h += '<h3 style="margin-top:16px">많이 고른 질문</h3>' + wiseBars(rows, 560);
    }

    h += '<div class="scroll" style="margin-top:12px"><table>' +
      '<tr><th>닉네임</th><th>주제</th><th>1단계</th><th>3단계</th><th>겹침</th>' +
      '<th>받아들인 점</th><th>알게 된 것</th></tr>';
    var m, p;
    for (m = 0; m < list.length; m++) {
      p = list[m].payload || {};
      if (!p.f0) { continue; }
      h += "<tr><td>" + esc(list[m].nick) + "</td><td>" + esc(p.topic || "-") + "</td><td>" +
        (p.s0 || 0) + "문장</td><td>" + (p.s3 || 0) + "문장</td><td>" +
        (p.overlap === undefined ? "-" : p.overlap + "%") + "</td><td>" +
        (p.takeYes === undefined ? "-" : p.takeYes + "개") + "</td><td>" +
        esc(p.f4 || "") + "</td></tr>";
    }
    h += "</table></div>";
    return h;
  }

  function presentHtml(list) {
    var g = gather(list);
    var h = '<p class="big">3단계까지 ' + g.step3 + '명</p>' +
      '<p class="muted">처음 쓴 글과 다시 쓴 글이 어떻게 달라졌는지 함께 봐요.</p>';
    var shown = 0, i, p;
    for (i = 0; i < list.length && shown < 3; i++) {
      p = list[i].payload || {};
      if (!p.f0 || !p.f3) { continue; }
      shown++;
      h += '<div class="card"><p class="pill">' + esc(list[i].nick) + ' · ' +
        esc(p.topic || "") + '</p>' +
        '<h3 style="margin-top:10px">처음 쓴 글</h3><p style="font-size:20px">' + esc(p.f0) + '</p>' +
        '<h3 style="margin-top:12px">다시 쓴 글</h3><p style="font-size:20px">' + esc(p.f3) + '</p>' +
        '<p class="muted" style="margin-top:8px">그대로 남은 낱말 ' + (p.overlap || 0) +
        '% · 받아들인 점 ' + (p.takeYes || 0) + '개</p></div>';
    }
    if (!shown) { h += '<p class="muted">아직 제출된 글이 없어요.</p>'; }
    return h;
  }
"""
