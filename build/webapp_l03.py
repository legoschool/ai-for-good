# -*- coding: utf-8 -*-
"""3차시 편향 관찰 갤러리.

여정형으로 만든다. 폼 하나가 아니라 화면 여덟 개를 지나간다.

  이야기 -> 탐정 사무소(허브) -> 짐작하기 -> 그림 공장 12장
  -> 세어 보기 -> 사진 창고에서 비율 바꾸기 -> 마음 살피기 -> 탐정 수첩

설계서는 spec/12_웹앱_설계_L03.md 다.
학생이 편견을 직접 만들고 직접 없애는 것이 이 앱의 단 하나의 경험이다.
그림은 브라우저 안에서 SVG 로 그린다. 외부 이미지 생성 서비스를 부르지 않는다.
뽑기는 무작위가 아니라 몫으로 나눈다. 창고 비율이 82% 면 열두 장 중 열 장이 남성이다.

40분 : 이야기 2 + 짐작 4 + 관찰 7 + 세어 보기 8 + 창고 9 + 마음 6 + 수첩 4
"""

ACTIVITY = u"""
  /* ---------- 학습 데이터 분포 ---------- */
  /* 실제 이미지 생성 서비스에서 되풀이해 보고된 치우침을 본떠 만든 값이다.
     아이들에게 "AI가 원래 그렇다"가 아니라 "데이터가 그랬다"를 보여 주는 것이 목적이다. */

  var JOBS = [
    {id:"doctor", name:"의사", data:{m:82, y:64, light:78},
     note:"창고 사진 100장 가운데 82장이 남성이었어요."},
    {id:"nurse", name:"간호사", data:{m:11, y:72, light:74},
     note:"창고 사진 100장 가운데 11장만 남성이었어요."},
    {id:"cook", name:"요리사", data:{m:76, y:55, light:70},
     note:"주방 사진 100장 가운데 76장이 남성이었어요."},
    {id:"teacher", name:"선생님", data:{m:34, y:58, light:80},
     note:"학교 사진 100장 가운데 34장이 남성이었어요."},
    {id:"science", name:"과학자", data:{m:79, y:48, light:83},
     note:"과학자 사진 100장 가운데 79장이 남성이었어요. 나이 든 얼굴도 많았어요."}
  ];

  var GUESSES = ["0장에서 2장", "3장에서 5장", "6장 안팎", "7장에서 9장", "10장에서 12장"];
  var GUESS_MID = [1, 4, 6, 8, 11];

  var RATIOS = [0, 25, 50, 75, 100];

  var WHO = [
    "의사를 꿈꾸는 여자 어린이",
    "간호사를 꿈꾸는 남자 어린이",
    "피부색이 다른 친구",
    "나이 든 어른",
    "그 직업으로 일하는 사람",
    "그 그림을 본 우리 모두"
  ];

  var N = 12;

  var st = {
    job: -1, guess: -1, counted: -1, ratio: -1,
    cards: [], after: [], shown: false, checked: false,
    who: {}, badges: {}, classAvg: null
  };

  /* ---------- 뽑기 ---------- */

  function shuffled(n) {
    var a = [], i, j, t;
    for (i = 0; i < n; i++) { a.push(i); }
    for (i = n - 1; i > 0; i--) {
      j = Math.floor(Math.random() * (i + 1));
      t = a[i]; a[i] = a[j]; a[j] = t;
    }
    return a;
  }

  function quota(percent) { return Math.round(N * percent / 100); }

  /* 창고 비율대로 열두 장을 만든다. 자리만 섞는다.
     무작위로 뽑으면 세어 보기가 매번 흔들려 비율을 바꾼 효과가 묻힌다. */
  function draw(job, malePercent) {
    var mp = (malePercent === null || malePercent === undefined) ? job.data.m : malePercent;
    var out = [], i, idx;
    for (i = 0; i < N; i++) { out.push({ m: false, y: false, light: 1, job: job.id }); }

    idx = shuffled(N);
    var mn = quota(mp);
    for (i = 0; i < mn; i++) { out[idx[i]].m = true; }

    idx = shuffled(N);
    var yn = quota(job.data.y);
    for (i = 0; i < yn; i++) { out[idx[i]].y = true; }

    idx = shuffled(N);
    var ln = quota(job.data.light);
    var mid = ln + Math.round((N - ln) / 2);
    for (i = 0; i < N; i++) {
      out[idx[i]].light = i < ln ? 2 : (i < mid ? 1 : 0);
    }
    return out;
  }

  function countOf(cards) {
    var c = { m: 0, f: 0, young: 0, old: 0, light: 0, mid: 0, dark: 0 }, i, p;
    for (i = 0; i < cards.length; i++) {
      p = cards[i];
      if (p.m) { c.m++; } else { c.f++; }
      if (p.y) { c.young++; } else { c.old++; }
      if (p.light === 2) { c.light++; } else if (p.light === 1) { c.mid++; } else { c.dark++; }
    }
    return c;
  }

  function countKeys(obj) {
    var n = 0, k;
    for (k in obj) { if (obj.hasOwnProperty(k) && obj[k]) { n++; } }
    return n;
  }

  /* ---------- 기다림 ---------- */
  /* 그림을 뽑는 일은 사실 눈 깜짝할 새에 끝난다. 그래도 한 박자 쉬어 준다.
     공장이 일하는 동안을 보여 주어야 "내가 시켰고 공장이 그렸다"가 몸에 남는다.
     움직임을 줄여 달라고 한 기기에서는 기다리지 않고 곧바로 보여 준다. */

  function reducedMotion() {
    try {
      return !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);
    } catch (e) { return false; }
  }

  function softDelay(fn, ms) {
    if (reducedMotion() || !ms) { fn(); return; }
    setTimeout(fn, ms);
  }

  /* ---------- 그림 ---------- */
  /* 이 차시에만 쓰는 그림이라 여기에 둔다. 실제 사진은 쓰지 않는다. */

  function personSvg(p) {
    var skin = p.light === 0 ? "#8D5524" : (p.light === 1 ? "#C68642" : "#F1C27D");
    var hair = p.m ? "#2f2f2f" : "#4a2f1f";
    var cloth = (p.job === "doctor" || p.job === "nurse") ? "#e6f0ff" : "#dbeafe";
    var longHair = p.m ? "" :
      '<path d="M26 42 q0 26 6 30 M74 42 q0 26 -6 30" stroke="' + hair +
      '" stroke-width="7" fill="none" stroke-linecap="round"/>';
    var gray = p.y ? "" : '<path d="M30 34 q20 -10 40 0" stroke="#dcdcdc" stroke-width="5" fill="none"/>';
    return '<svg viewBox="0 0 100 100" width="82" height="82" aria-hidden="true">' +
      '<rect x="18" y="70" width="64" height="30" rx="14" fill="' + cloth + '" stroke="#111" stroke-width="3"/>' +
      longHair +
      '<circle cx="50" cy="46" r="24" fill="' + skin + '" stroke="#111" stroke-width="3"/>' +
      '<path d="M26 40 q24 -22 48 0 q-6 -18 -24 -18 q-18 0 -24 18z" fill="' + hair + '"/>' +
      gray +
      '<circle cx="41" cy="48" r="3" fill="#111"/><circle cx="59" cy="48" r="3" fill="#111"/>' +
      '<path d="M43 58 q7 6 14 0" stroke="#111" stroke-width="3" fill="none" stroke-linecap="round"/>' +
      '</svg>';
  }

  function factorySvg() {
    return '<svg class="ws-scene" viewBox="0 0 320 120" aria-hidden="true">' +
      '<rect width="320" height="120" fill="#F6F7F9"/>' +
      '<rect x="14" y="34" width="108" height="66" rx="12" fill="#fff" stroke="#111" stroke-width="3"/>' +
      '<text x="68" y="60" font-size="14" font-weight="800" text-anchor="middle" fill="#111">사진 창고</text>' +
      '<rect x="30" y="72" width="22" height="16" rx="3" fill="#2B59E0" stroke="#111" stroke-width="2.5"/>' +
      '<rect x="58" y="72" width="22" height="16" rx="3" fill="#2B59E0" stroke="#111" stroke-width="2.5"/>' +
      '<rect x="86" y="72" width="22" height="16" rx="3" fill="#FFE24B" stroke="#111" stroke-width="2.5"/>' +
      '<path d="M128 66h30" stroke="#111" stroke-width="4" stroke-linecap="round"/>' +
      '<path d="M152 58l10 8-10 8z" fill="#111"/>' +
      '<rect x="168" y="26" width="88" height="74" rx="12" fill="#00D45A" stroke="#111" stroke-width="3"/>' +
      '<text x="212" y="58" font-size="14" font-weight="800" text-anchor="middle" fill="#111">그림 공장</text>' +
      '<text x="212" y="80" font-size="13" font-weight="700" text-anchor="middle" fill="#111">따라 그려요</text>' +
      '<path d="M262 66h22" stroke="#111" stroke-width="4" stroke-linecap="round"/>' +
      '<path d="M278 58l10 8-10 8z" fill="#111"/>' +
      '<rect x="292" y="46" width="20" height="40" rx="4" fill="#fff" stroke="#111" stroke-width="3"/>' +
      '</svg>';
  }

  function tagLine(p) {
    return (p.m ? "남성" : "여성") + " · " + (p.y ? "젊은 얼굴" : "나이 든 얼굴") + " · " +
      (p.light === 2 ? "밝은 피부" : (p.light === 1 ? "중간 피부" : "어두운 피부"));
  }

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function guestInner() {
    var h = '<div class="card"><span class="pill">짐작</span>' +
      '<h2 style="margin-top:10px">어떤 직업을 조사할까요</h2>' +
      '<div class="row" style="margin-top:10px">';
    var i;
    for (i = 0; i < JOBS.length; i++) {
      h += '<button type="button" class="chip jb" data-j="' + i +
        '" style="width:auto;margin:0">' + esc(JOBS[i].name) + '</button>';
    }
    h += '</div>' +
      '<h3 style="margin-top:18px">열두 장 중 남성이 몇 장 나올까요</h3>' +
      '<p class="muted">짐작은 틀려도 좋아요. 짐작이 있어야 놀랄 수 있어요.</p>' +
      '<div style="margin-top:10px">';
    for (i = 0; i < GUESSES.length; i++) {
      h += '<button type="button" class="chip gs" data-g="' + i + '">' + esc(GUESSES[i]) + '</button>';
    }
    h += '</div><p class="muted" id="guessmsg" style="margin-top:8px"></p>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-draw" class="ghost">그림 공장으로 가기</button>' +
      '<button type="button" class="plain back">사무소로</button></div></div>';
    return h;
  }

  function storeInner() {
    var h = '<div class="card"><span class="pill">창고</span>' +
      '<h2 style="margin-top:10px">사진 창고를 열어요</h2>' +
      '<p class="muted">공장이 그리는 방법은 그대로예요. 창고 사진 비율만 바꿔 봐요.</p>' +
      '<h3 style="margin-top:14px">창고의 남성 사진 비율</h3><div style="margin-top:8px">';
    var i;
    for (i = 0; i < RATIOS.length; i++) {
      h += '<button type="button" class="chip rt" data-t="' + i + '">' +
        RATIOS[i] + '% 로 바꾸기</button>';
    }
    h += '</div><div class="row" style="margin-top:12px">' +
      '<button type="button" id="redraw">이 데이터로 다시 뽑기</button>' +
      '<button type="button" class="plain back">사무소로</button></div>' +
      '<div id="storebox" style="margin-top:12px"></div>' +
      '<label for="changed">한 줄 쓰기</label>' +
      '<input id="changed" maxlength="80" ' +
      'placeholder="예: 그리는 방법은 그대로인데 창고 사진을 바꾸었더니 결과가 달라졌습니다">' +
      '<div class="note">그러면 처음 그 그림은 누구의 잘못일까요?</div></div>';
    return h;
  }

  function whoInner() {
    var h = '<div class="card"><span class="pill">마음</span>' +
      '<h2 style="margin-top:10px">누가 불편해질까요</h2>' +
      '<p class="muted">여러 사람을 고를 수 있어요.</p><div style="margin-top:10px">';
    var i;
    for (i = 0; i < WHO.length; i++) {
      h += '<button type="button" class="chip wh" data-w="' + i + '">' + esc(WHO[i]) + '</button>';
    }
    h += '</div>' +
      '<label for="why">이런 그림이 나온 까닭은</label>' +
      '<textarea id="why" maxlength="300" placeholder="창고 사진과 이어서 써 봐요"></textarea>' +
      '<label for="fix">결과가 한쪽으로 몰리면 우리는</label>' +
      '<input id="fix" maxlength="80" placeholder="예: 다시 물어보고 다른 자료와 견주어 봅니다">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" class="plain back">사무소로</button></div>' +
      '<div class="safe">친구 이야기나 사람 이름을 쓰지 않아요. ' +
      '이름, 사진 같은 개인정보는 넣지 않아요.</div></div>';
    return h;
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">그림 공장과 편견 탐정</h2>' +
      factorySvg() +
      '<p style="margin-top:10px">그림 공장에 직업 이름을 말하면 그림 열두 장이 나와요. ' +
      '그런데 나오는 사람이 자꾸 비슷해요.</p>' +
      '<p style="margin-top:8px">오늘 여러분은 <b>편견 탐정</b>이에요. ' +
      '공장을 나무라기 전에 <b>공장 뒤 사진 창고</b>를 열어 봐요.</p>' +
      '<p class="muted" style="margin-top:8px">공장은 나쁜 마음이 없어요. ' +
      '창고에 있는 사진을 그대로 흉내 낼 뿐이에요.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">탐정 사무소로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>탐정 사무소</h2>' +
      '<p class="muted">순서대로 해도 되고, 하고 싶은 곳부터 해도 돼요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="b-guess">' + wiseIcon("star", 30) +
      '<span>1. 짐작하기</span><small id="s-guess">직업을 고르고 미리 짐작해요</small></button>' +
      '<button type="button" class="tile" id="b-draw">' + wiseIcon("ai", 30) +
      '<span>2. 그림 공장</span><small id="s-draw">열두 장을 뽑아 관찰해요</small></button>' +
      '<button type="button" class="tile" id="b-num">' + wiseIcon("check", 30) +
      '<span>3. 세어 보기</span><small id="s-num">남성이 몇 장인지 세어요</small></button>' +
      '<button type="button" class="tile" id="b-store">' + wiseIcon("again", 30) +
      '<span>4. 사진 창고</span><small id="s-store">창고를 바꾸고 다시 뽑아요</small></button>' +
      '<button type="button" class="tile" id="b-who">' + wiseIcon("heart", 30) +
      '<span>5. 마음 살피기</span><small id="s-who">누가 불편해질까요</small></button>' +
      '<button type="button" class="tile" id="b-book">' + wiseIcon("rec", 30) +
      '<span>6. 탐정 수첩</span><small id="s-book">오늘의 내 기록</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>내가 받은 배지</h3>' +
      '<div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("guess", guestInner());

    h += q("draw",
      '<div class="card"><span class="pill">관찰</span>' +
      '<h2 style="margin-top:10px">그림 공장</h2>' +
      '<p class="muted">이 앱은 인터넷으로 그림을 만들지 않아요. ' +
      '창고에 넣어 둔 사진 비율대로 열두 장을 그려 줘요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="gen">열두 장 뽑기</button>' +
      '<button type="button" id="tags" class="ghost">태그 보기</button></div>' +
      '<p class="muted" id="genmsg" style="margin-top:8px"></p>' +
      '<div id="gallery" class="row" style="gap:8px;margin-top:8px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="to-num" class="ghost">세어 보러 가기</button>' +
      '<button type="button" class="plain back">사무소로</button></div></div>');

    h += q("num",
      '<div class="card"><span class="pill">세어 보기</span>' +
      '<h2 style="margin-top:10px">남성이 몇 장이었나요</h2>' +
      '<p class="muted">눈으로 먼저 세어 보고 적어요. 맞고 틀림을 매기지 않아요.</p>' +
      '<label for="cnt">내가 센 남성 그림 수 (0장에서 12장)</label>' +
      '<input id="cnt" inputmode="numeric" maxlength="2" placeholder="예: 9">' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="check">맞춰 보기</button>' +
      '<button type="button" class="plain back">사무소로</button></div>' +
      '<div id="numbox" style="margin-top:12px"></div></div>');

    h += q("store", storeInner());
    h += q("who", whoInner());

    h += q("book",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">나의 탐정 수첩</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">카드 그림으로 저장</button>' +
      '<button type="button" id="peek" class="ghost">우리 반과 견주기</button>' +
      '<button type="button" class="plain back">사무소로</button></div>' +
      '<div id="classbox" style="margin-top:12px"></div></div>');

    return h;
  }

  /* ---------- 그림 공장 ---------- */

  function galleryHtml(cards) {
    if (!cards.length) {
      return '<p class="muted">아직 뽑지 않았어요. 열두 장 뽑기를 눌러요.</p>';
    }
    var h = "", i;
    for (i = 0; i < cards.length; i++) {
      h += '<div class="card fade-in" style="width:106px;margin:0;padding:8px;text-align:center;' +
        'animation-delay:' + (i * 0.05).toFixed(2) + 's">' +
        personSvg(cards[i]) +
        (st.shown ? '<p class="muted" style="font-size:12px;margin-top:4px">' +
          esc(tagLine(cards[i])) + '</p>' : "") +
        '</div>';
    }
    return h;
  }

  function paintGallery() {
    if ($("gallery")) { $("gallery").innerHTML = galleryHtml(st.cards); }
    if ($("tags")) { $("tags").textContent = st.shown ? "태그 가리기" : "태그 보기"; }
  }

  /* ---------- 세어 보기 ---------- */

  function axisTable(c) {
    return '<div class="scroll"><table>' +
      '<tr><th>무엇을</th><th>한쪽</th><th>다른 쪽</th><th>치우침</th></tr>' +
      '<tr><td>성별</td><td>남성 ' + c.m + '장</td><td>여성 ' + c.f + '장</td><td>' +
      barHtml(c.m, N) + '</td></tr>' +
      '<tr><td>나이</td><td>젊은 얼굴 ' + c.young + '장</td><td>나이 든 얼굴 ' + c.old +
      '장</td><td>' + barHtml(c.young, N) + '</td></tr>' +
      '<tr><td>피부색</td><td>밝은 피부 ' + c.light + '장</td><td>중간·어두운 피부 ' +
      (c.mid + c.dark) + '장</td><td>' + barHtml(c.light, N) + '</td></tr>' +
      '</table></div>';
  }

  function paintNum() {
    if (!$("numbox")) { return; }
    if (!st.cards.length) {
      $("numbox").innerHTML = '<p class="muted">먼저 그림 공장에서 열두 장을 뽑아요.</p>';
      return;
    }
    if (!st.checked) {
      $("numbox").innerHTML = '<p class="muted">센 수를 적고 맞춰 보기를 눌러요.</p>';
      return;
    }
    var c = countOf(st.cards);
    var gap = Math.abs(st.counted - c.m);
    var h = '<div class="scroll"><table><tr><th>내 짐작</th><th>내가 센 수</th><th>실제</th></tr>' +
      '<tr><td>' + (st.guess >= 0 ? esc(GUESSES[st.guess]) : "짐작 안 함") + '</td><td>' +
      (st.counted >= 0 ? st.counted + '장' : "-") + '</td><td>' + c.m + '장</td></tr></table></div>';
    h += '<p class="' + (gap === 0 ? "ok" : "muted") + '" style="margin-top:10px">' +
      (gap === 0 ? "딱 맞았어요. 눈썰미가 좋아요." : "실제와 " + gap + "장 차이예요. 괜찮아요.") + '</p>';
    h += '<p style="margin-top:10px">' + esc(JOBS[st.job < 0 ? 0 : st.job].note) + '</p>';
    h += axisTable(c);
    h += '<div class="note">공장이 아니라 창고를 봐야 해요. 다음은 사진 창고예요.</div>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="to-store" class="ghost">사진 창고로 가기</button></div>';
    $("numbox").innerHTML = h;
    if ($("to-store")) { $("to-store").onclick = function () { wiseGo("store"); }; }
  }

  /* ---------- 사진 창고 ---------- */

  function paintStore() {
    if (!$("storebox")) { return; }
    markRatio();
    if (!st.cards.length) {
      $("storebox").innerHTML = '<p class="muted">먼저 그림 공장에서 열두 장을 뽑아요.</p>';
      return;
    }
    var before = countOf(st.cards);
    var h = '<p class="muted">지금 창고는 남성 사진 ' + JOBS[st.job < 0 ? 0 : st.job].data.m +
      '% 예요. 바꿀 비율을 고르고 다시 뽑기를 눌러요.</p>';
    if (!st.after.length) {
      $("storebox").innerHTML = h;
      return;
    }
    var afterC = countOf(st.after);
    h += wiseBars([
      { label: "바꾸기 전 남성", value: before.m },
      { label: "바꾼 뒤 남성", value: afterC.m }
    ], 560);
    h += '<div class="scroll" style="margin-top:10px"><table>' +
      '<tr><th>무엇을</th><th>바꾸기 전</th><th>바꾼 뒤</th></tr>' +
      '<tr><td>남성</td><td>' + before.m + '장</td><td>' + afterC.m + '장</td></tr>' +
      '<tr><td>여성</td><td>' + before.f + '장</td><td>' + afterC.f + '장</td></tr>' +
      '</table></div>';
    h += '<div class="row" style="gap:8px;margin-top:10px">';
    var i;
    for (i = 0; i < st.after.length; i++) {
      h += '<div class="card" style="width:92px;margin:0;padding:6px;text-align:center">' +
        personSvg(st.after[i]) + '</div>';
    }
    h += '</div>';
    h += '<p class="ok" style="margin-top:10px">공장은 그대로예요. 창고만 바꾸었는데 결과가 달라졌어요.</p>';
    $("storebox").innerHTML = h;
  }

  function markRatio() {
    var rt = document.querySelectorAll("#activity .rt"), i, t;
    for (i = 0; i < rt.length; i++) {
      t = Number(rt[i].getAttribute("data-t"));
      rt[i].className = "chip rt" + (st.ratio === RATIOS[t] ? " on" : "");
    }
  }

  /* ---------- 마음 살피기 ---------- */

  function markWho() {
    var wh = document.querySelectorAll("#activity .wh"), i, w;
    for (i = 0; i < wh.length; i++) {
      w = wh[i].getAttribute("data-w");
      wh[i].className = "chip wh" + (st.who[w] ? " on" : "");
    }
  }

  /* ---------- 탐정 수첩 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    if (!st.cards.length) {
      $("mine").innerHTML = '<p class="muted">아직 뽑은 그림이 없어요. 그림 공장부터 가 봐요.</p>';
      return;
    }
    var c = countOf(st.cards);
    var rows = [{ label: "처음 남성", value: c.m }, { label: "처음 여성", value: c.f }];
    if (st.after.length) {
      var a = countOf(st.after);
      rows.push({ label: "바꾼 뒤 남성", value: a.m });
      rows.push({ label: "바꾼 뒤 여성", value: a.f });
    }
    var h = '<p>조사한 직업 <b>' + esc(JOBS[st.job < 0 ? 0 : st.job].name) + '</b> · 뽑은 그림 ' +
      st.cards.length + '장</p>';
    h += wiseBars(rows, 560);
    h += '<p style="margin-top:10px">내 짐작 ' +
      (st.guess >= 0 ? esc(GUESSES[st.guess]) : "짐작 안 함") + ' · 실제 남성 ' + c.m +
      '장 · 고른 사람 ' + countKeys(st.who) + '명</p>';
    if (st.after.length) {
      h += '<p>창고를 ' + st.ratio + '% 로 바꾼 뒤 남성 ' + countOf(st.after).m +
        '장 · 여성 ' + countOf(st.after).f + '장이 되었어요.</p>';
    } else {
      h += '<p class="muted">창고는 아직 바꾸지 않았어요. 사진 창고에서 바꿔 보면 결과가 달라져요.</p>';
    }
    $("mine").innerHTML = h;
  }

  function peek() {
    if (!$("classbox")) { return; }
    if (me.solo) {
      $("classbox").innerHTML = '<p class="muted">둘러보기 중에는 우리 반 기록이 없어요. ' +
        '관찰과 창고 바꾸기는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    if ($("peek")) { wiseButtonBusy($("peek"), true, "불러오는 중"); }
    $("classbox").innerHTML = wiseSpinner("우리 반 기록을 불러오는 중이에요") + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      if ($("peek")) { wiseButtonBusy($("peek"), false); }
      var n = 0, guessSum = 0, guessN = 0, realSum = 0, afterSum = 0, afterN = 0, k, p;
      for (k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        p = data[k].payload || {};
        if (!p.count) { continue; }
        n++;
        realSum += p.count.m || 0;
        if (p.guess !== undefined && p.guess !== null && p.guess >= 0) {
          guessSum += GUESS_MID[p.guess] || 0;
          guessN++;
        }
        if (p.after) { afterSum += p.after.m || 0; afterN++; }
      }
      if (!n) {
        $("classbox").innerHTML = '<p class="muted">아직 우리 반 기록이 모이지 않았어요.</p>';
        return;
      }
      var h = '<p>우리 반 ' + n + '명 기준이에요.</p>';
      h += wiseBars([
        { label: "짐작 평균", value: guessN ? Math.round(guessSum / guessN) : 0 },
        { label: "실제 평균", value: Math.round(realSum / n) },
        { label: "바꾼 뒤 평균", value: afterN ? Math.round(afterSum / afterN) : 0 }
      ], 560);
      h += '<p class="muted">열두 장 중 남성 그림 수예요. 창고를 바꾼 학생은 ' + afterN + '명이에요.</p>';
      $("classbox").innerHTML = h;
      st.classAvg = { n: n, real: realSum / n };
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
    if (st.guess >= 0) { n++; }
    if (st.cards.length) { n++; }
    if (st.checked) { n++; }
    if (st.after.length) { n++; }
    if (countKeys(st.who)) { n++; }
    if (val("why").length >= 5) { n++; }
    return n;
  }

  function paintHud() {
    wiseHud([
      { label: "오늘 할 일", done: doneSteps(), total: 6 },
      { label: "뽑은 그림", done: st.cards.length, total: N },
      { label: "고른 사람", done: countKeys(st.who), total: WHO.length }
    ]);
  }

  function paintHub() {
    if (!$("s-guess")) { return; }
    $("s-guess").textContent = st.job >= 0
      ? (JOBS[st.job].name + " · " + (st.guess >= 0 ? GUESSES[st.guess] : "짐작 전"))
      : "직업을 고르고 미리 짐작해요";
    $("s-draw").textContent = st.cards.length
      ? ("뽑은 그림 " + st.cards.length + "장") : "열두 장을 뽑아 관찰해요";
    $("s-num").textContent = st.checked
      ? ("내가 센 수 " + st.counted + "장") : "남성이 몇 장인지 세어요";
    $("s-store").textContent = st.after.length
      ? ("창고를 " + st.ratio + "% 로 바꿔 봤어요") : "창고를 바꾸고 다시 뽑아요";
    $("s-who").textContent = countKeys(st.who)
      ? ("고른 사람 " + countKeys(st.who) + "명") : "누가 불편해질까요";
    $("s-book").textContent = "오늘의 내 기록";

    var tiles = [["b-guess", st.guess >= 0], ["b-draw", st.cards.length > 0],
      ["b-num", st.checked], ["b-store", st.after.length > 0],
      ["b-who", countKeys(st.who) > 0], ["b-book", false]];
    var i;
    for (i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }

    if (st.guess >= 0) { award("짐작한 탐정"); }
    if (st.after.length) { award("창고를 연 탐정"); }
    if (countKeys(st.who) >= 2) { award("마음을 살핀 탐정"); }

    var names = badgeList(), b, h = "";
    for (b = 0; b < names.length; b++) {
      h += '<span class="pill">' + esc(names[b]) + '</span> ';
    }
    if ($("badges")) {
      $("badges").innerHTML = names.length ? h
        : '<span class="muted">아직 없어요. 짐작부터 해 보면 받을 수 있어요.</span>';
    }
    paintHud();
  }

  /* ---------- 흐름 ---------- */

  function val(id) { return $(id) && $(id).value ? String($(id).value).trim() : ""; }

  var NOTES = {
    story: "공장을 나무라기 전에 창고를 열어 보는 이야기예요.",
    hub: "여섯 가지 일을 골라서 해요. 창고를 바꾸는 것이 오늘의 핵심이에요.",
    guess: "직업을 고르고, 몇 장이 나올지 먼저 짐작해 봐요.",
    draw: "열두 장을 뽑고 눈으로 먼저 세어 봐요.",
    num: "내가 센 수를 적고 실제와 견주어 봐요.",
    store: "창고 비율을 바꾸고 다시 뽑아 전후를 견주어 봐요.",
    who: "누가 불편해질지 고르고, 까닭을 한 줄 써요.",
    book: "오늘 기록을 카드로 저장하고 제출해요."
  };

  function activityEnter(id) {
    if (NOTES[id]) { wiseNote(NOTES[id]); }
    if (id === "hub") { paintHub(); }
    if (id === "draw") { paintGallery(); }
    if (id === "num") { paintNum(); }
    if (id === "store") { paintStore(); }
    if (id === "who") { markWho(); }
    if (id === "book") { paintMine(); }
  }

  function markJobs() {
    var jobs = document.querySelectorAll("#activity .jb"), i;
    for (i = 0; i < jobs.length; i++) {
      jobs[i].className = "chip jb" + (Number(jobs[i].getAttribute("data-j")) === st.job ? " on" : "");
    }
  }

  function markGuess() {
    var gs = document.querySelectorAll("#activity .gs"), i;
    for (i = 0; i < gs.length; i++) {
      gs[i].className = "chip gs" + (Number(gs[i].getAttribute("data-g")) === st.guess ? " on" : "");
    }
  }

  function activityInit(saved) {
    var i;

    if (saved) {
      if (saved.jobIndex !== undefined && saved.jobIndex >= 0) { st.job = saved.jobIndex; }
      if (saved.guess !== undefined && saved.guess >= 0) { st.guess = saved.guess; }
      if (saved.who) { st.who = saved.who; }
      if (saved.why && $("why")) { $("why").value = saved.why; }
      if (saved.fix && $("fix")) { $("fix").value = saved.fix; }
      if (saved.changed && $("changed")) { $("changed").value = saved.changed; }
      if (saved.jobIndex !== undefined || saved.why) {
        softDelay(function () {
          wiseToast("지난번에 조사하던 것이 남아 있어요.");
        }, 700);
      }
    }

    var jobs = document.querySelectorAll("#activity .jb");
    for (i = 0; i < jobs.length; i++) {
      jobs[i].onclick = function () {
        st.job = Number(this.getAttribute("data-j"));
        st.cards = [];
        st.after = [];
        st.checked = false;
        st.counted = -1;
        if ($("cnt")) { $("cnt").value = ""; }
        markJobs();
        if ($("guessmsg")) {
          $("guessmsg").textContent = JOBS[st.job].name +
            "을 골랐어요. 열두 장 중 남성이 몇 장일지 골라 봐요.";
        }
        paintGallery();
        paintHub();
      };
    }

    var gs = document.querySelectorAll("#activity .gs");
    for (i = 0; i < gs.length; i++) {
      gs[i].onclick = function () {
        if (st.job < 0) { wiseToast("먼저 직업을 골라요."); return; }
        st.guess = Number(this.getAttribute("data-g"));
        markGuess();
        if ($("guessmsg")) {
          $("guessmsg").textContent = "짐작을 적어 두었어요. 이제 그림 공장으로 가 봐요.";
        }
        paintHub();
      };
    }

    var rt = document.querySelectorAll("#activity .rt");
    for (i = 0; i < rt.length; i++) {
      rt[i].onclick = function () {
        st.ratio = RATIOS[Number(this.getAttribute("data-t"))];
        markRatio();
        wiseToast("창고를 " + st.ratio + "% 로 맞췄어요. 다시 뽑기를 눌러요.");
      };
    }

    var wh = document.querySelectorAll("#activity .wh");
    for (i = 0; i < wh.length; i++) {
      wh[i].onclick = function () {
        var w = this.getAttribute("data-w");
        st.who[w] = !st.who[w];
        markWho();
        paintHub();
      };
    }

    if ($("go-hub")) { $("go-hub").onclick = function () { wiseGo("hub"); }; }
    if ($("b-guess")) { $("b-guess").onclick = function () { wiseGo("guess"); }; }
    if ($("b-draw")) { $("b-draw").onclick = function () { wiseGo("draw"); }; }
    if ($("b-num")) { $("b-num").onclick = function () { wiseGo("num"); }; }
    if ($("b-store")) { $("b-store").onclick = function () { wiseGo("store"); }; }
    if ($("b-who")) { $("b-who").onclick = function () { wiseGo("who"); }; }
    if ($("b-book")) { $("b-book").onclick = function () { wiseGo("book"); }; }
    if ($("to-draw")) { $("to-draw").onclick = function () { wiseGo("draw"); }; }
    if ($("to-num")) { $("to-num").onclick = function () { wiseGo("num"); }; }

    if ($("gen")) {
      $("gen").onclick = function () {
        if (st.job < 0) { wiseToast("먼저 짐작하기에서 직업을 골라요."); wiseGo("guess"); return; }
        var btn = this;
        st.after = [];
        st.checked = false;
        st.counted = -1;
        if ($("cnt")) { $("cnt").value = ""; }
        wiseButtonBusy(btn, true, "그리는 중");
        if ($("genmsg")) { $("genmsg").textContent = ""; }
        if ($("gallery")) {
          $("gallery").innerHTML = wiseSpinner("공장이 " + JOBS[st.job].name +
            " 그림을 그리는 중이에요", true) + wiseSkeleton(3);
        }
        softDelay(function () {
          st.cards = draw(JOBS[st.job], null);
          wiseButtonBusy(btn, false);
          if ($("genmsg")) {
            $("genmsg").textContent = JOBS[st.job].name +
              " 열두 장을 뽑았어요. 무엇이 많은지 눈으로 세어 봐요.";
          }
          wiseNote("열두 장이 나왔어요. 눈으로 먼저 세어 봐요.");
          paintGallery();
          paintHub();
        }, 900);
      };
    }

    if ($("tags")) {
      $("tags").onclick = function () {
        st.shown = !st.shown;
        paintGallery();
      };
    }

    if ($("check")) {
      $("check").onclick = function () {
        if (!st.cards.length) { wiseToast("먼저 열두 장을 뽑아요."); wiseGo("draw"); return; }
        var v = val("cnt");
        var n = Number(v);
        if (!v || isNaN(n) || n < 0 || n > N) {
          wiseToast("0장에서 12장 사이 숫자를 적어요.");
          return;
        }
        var btn = this;
        wiseButtonBusy(btn, true, "맞춰 보는 중");
        if ($("numbox")) { $("numbox").innerHTML = wiseSpinner("세어 본 수와 맞춰 보는 중이에요"); }
        softDelay(function () {
          st.counted = Math.round(n);
          st.checked = true;
          if (st.counted === countOf(st.cards).m) { award("눈썰미"); }
          wiseButtonBusy(btn, false);
          paintNum();
          paintHub();
        }, 600);
      };
    }

    if ($("redraw")) {
      $("redraw").onclick = function () {
        if (!st.cards.length) { wiseToast("먼저 열두 장을 뽑아요."); wiseGo("draw"); return; }
        if (st.ratio < 0) { wiseToast("바꿀 비율을 먼저 골라요."); return; }
        var btn = this;
        wiseButtonBusy(btn, true, "다시 그리는 중");
        if ($("storebox")) {
          $("storebox").innerHTML = wiseSpinner("창고 사진을 " + st.ratio +
            "% 로 바꾸고 다시 그리는 중이에요", true) + wiseSkeleton(3);
        }
        softDelay(function () {
          st.after = draw(JOBS[st.job < 0 ? 0 : st.job], st.ratio);
          wiseButtonBusy(btn, false);
          paintStore();
          paintHub();
        }, 1100);
      };
    }

    if ($("save-card")) {
      $("save-card").onclick = function () {
        if (!st.cards.length) {
          wiseToast("먼저 그림 공장에서 열두 장을 뽑아요.");
          wiseGo("draw");
          return;
        }
        var c = countOf(st.cards);
        var a = st.after.length ? countOf(st.after) : null;
        wiseBusy(true, "수첩 카드를 만드는 중");
        softDelay(function () {
          wiseBusy(false);
          saveCard(c, a);
        }, 500);
      };
    }

    function saveCard(c, a) {
      wiseCardPng("편견 탐정 수첩 " + me.nick, [
          "조사한 직업 " + (st.job >= 0 ? JOBS[st.job].name : "고르지 않음"),
          "내 짐작 " + (st.guess >= 0 ? GUESSES[st.guess] : "짐작 안 함"),
          "실제 남성 " + c.m + "장  여성 " + c.f + "장",
          a ? ("창고를 " + st.ratio + "% 로 바꾼 뒤 남성 " + a.m + "장")
            : "창고는 아직 바꾸지 않았어요",
          "고른 사람 " + countKeys(st.who) + "명",
          "공장이 아니라 창고를 바꾸면 결과가 달라진다."
        ], "wise_l03_" + me.nick);
    }

    if ($("peek")) { $("peek").onclick = peek; }

    var backs = document.querySelectorAll("#activity .back");
    for (i = 0; i < backs.length; i++) {
      backs[i].onclick = function () { wiseGo("hub"); };
    }

    markJobs();
    markGuess();
    markWho();
    markRatio();
    wiseNote(NOTES.story);
    wiseGo("story");
    paintHub();
    paintGallery();
    paintMine();
  }

  function activityDraft() {
    return {
      jobIndex: st.job, guess: st.guess, who: st.who,
      why: val("why"), fix: val("fix"), changed: val("changed")
    };
  }

  function activityAutofill() {
    st.job = 0;
    st.guess = 3;
    st.cards = draw(JOBS[0], null);
    st.ratio = 50;
    st.after = draw(JOBS[0], 50);
    st.counted = countOf(st.cards).m;
    st.checked = true;
    st.who = { "0": true, "2": true };
    if ($("cnt")) { $("cnt").value = String(st.counted); }
    if ($("why")) { $("why").value = "창고에 남성 사진이 훨씬 많았기 때문입니다."; }
    if ($("fix")) { $("fix").value = "다시 물어보고 다른 자료와 견주어 봅니다."; }
    if ($("changed")) { $("changed").value = "창고 사진을 바꾸었더니 결과가 달라졌습니다."; }
  }

  function activityCollect() {
    if (!st.cards.length) {
      $("w-msg").innerHTML = '<span class="warn">먼저 그림 공장에서 열두 장을 뽑아 관찰해요. ' +
        '그림 공장 화면으로 데려갈게요.</span>';
      wiseGo("draw");
      return null;
    }
    if (!st.checked || st.counted < 0) {
      $("w-msg").innerHTML = '<span class="warn">세어 보기에서 남성이 몇 장인지 적고 맞춰 봐요. ' +
        '세어 보기 화면으로 데려갈게요.</span>';
      wiseGo("num");
      return null;
    }
    var why = val("why");
    if (why.length < 5) {
      $("w-msg").innerHTML = '<span class="warn">이런 그림이 나온 까닭을 한 줄 써 주세요. ' +
        '마음 살피기 화면으로 데려갈게요.</span>';
      wiseGo("who");
      return null;
    }
    if (!countKeys(st.who)) {
      $("w-msg").innerHTML = '<span class="warn">누가 불편해질지 한 사람 이상 골라 주세요. ' +
        '마음 살피기 화면으로 데려갈게요.</span>';
      wiseGo("who");
      return null;
    }

    var c = countOf(st.cards);
    var whoList = [], k;
    for (k in st.who) { if (st.who.hasOwnProperty(k) && st.who[k]) { whoList.push(Number(k)); } }
    var badges = badgeList();

    wiseCelebrate("조사를 마쳤어요", [
      "조사한 직업 <b>" + esc(JOBS[st.job < 0 ? 0 : st.job].name) + "</b>",
      "실제 남성 <b>" + c.m + "장</b> · 내 짐작 " +
        (st.guess >= 0 ? esc(GUESSES[st.guess]) : "짐작 안 함"),
      st.after.length
        ? ("창고를 " + st.ratio + "% 로 바꾸니 남성 " + countOf(st.after).m + "장이 되었어요")
        : "다음에는 창고도 바꾸어 봐요",
      "받은 배지 " + (badges.length ? badges.join(", ") : "없음")
    ], "좋아요");

    return {
      job: JOBS[st.job < 0 ? 0 : st.job].name,
      jobIndex: st.job < 0 ? 0 : st.job,
      guess: st.guess,
      counted: st.counted,
      count: c,
      ratio: st.after.length ? st.ratio : null,
      after: st.after.length ? countOf(st.after) : null,
      who: whoList,
      why: why,
      changed: val("changed"),
      fix: val("fix"),
      badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function gather(list) {
    var g = { n: 0, jobs: {}, guessSum: 0, guessN: 0, realSum: 0, afterSum: 0, afterN: 0,
      beforeOfChanged: 0, who: [0, 0, 0, 0, 0, 0] }, i, p, j, k;
    for (i = 0; i < list.length; i++) {
      p = list[i].payload || {};
      if (!p.count) { continue; }
      g.n++;
      j = p.job || "고르지 않음";
      if (!g.jobs[j]) { g.jobs[j] = { n: 0, m: 0 }; }
      g.jobs[j].n++;
      g.jobs[j].m += p.count.m || 0;
      g.realSum += p.count.m || 0;
      if (p.guess !== undefined && p.guess !== null && p.guess >= 0) {
        g.guessSum += GUESS_MID[p.guess] || 0;
        g.guessN++;
      }
      if (p.after) {
        g.afterSum += p.after.m || 0;
        g.beforeOfChanged += p.count.m || 0;
        g.afterN++;
      }
      if (p.who && p.who.length) {
        for (k = 0; k < p.who.length; k++) {
          if (g.who[p.who[k]] !== undefined) { g.who[p.who[k]] += 1; }
        }
      }
    }
    return g;
  }

  function teacherSummary(list) {
    var g = gather(list);
    var h = '<p class="muted">제출 ' + list.length + '명 · 그림을 뽑아 기록한 학생 ' + g.n +
      '명 · 창고를 바꿔 본 학생 ' + g.afterN + '명</p>';

    if (g.n) {
      h += wiseBars([
        { label: "학급 짐작 평균", value: g.guessN ? Math.round(g.guessSum / g.guessN) : 0 },
        { label: "실제 평균", value: Math.round(g.realSum / g.n) },
        { label: "창고를 바꾼 뒤", value: g.afterN ? Math.round(g.afterSum / g.afterN) : 0 }
      ], 560);
      h += '<p class="muted">열두 장 중 남성 그림 수다. 짐작과 실제의 차이가 이 차시의 이야깃거리다.</p>';
    }

    h += '<div class="scroll" style="margin-top:12px"><table>' +
      '<tr><th>조사한 직업</th><th>학생</th><th>열두 장 중 남성 평균</th></tr>';
    var k, j;
    for (k in g.jobs) {
      if (!g.jobs.hasOwnProperty(k)) { continue; }
      j = g.jobs[k];
      h += "<tr><td>" + esc(k) + "</td><td>" + j.n + "명</td><td>" +
        (j.n ? (j.m / j.n).toFixed(1) : "-") + "장</td></tr>";
    }
    h += "</table></div>";

    var rows = [], i;
    for (i = 0; i < WHO.length; i++) {
      rows.push({ label: WHO[i].slice(0, 12), value: g.who[i] });
    }
    h += '<h3 style="margin-top:16px">불편해질 사람으로 고른 것</h3>' + wiseBars(rows, 560);

    h += '<h3 style="margin-top:16px">학생이 쓴 원인 문장</h3><div class="scroll"><table>' +
      '<tr><th>닉네임</th><th>이런 그림이 나온 까닭</th><th>우리가 할 일</th></tr>';
    var m, p;
    for (m = 0; m < list.length; m++) {
      p = list[m].payload || {};
      if (!p.why) { continue; }
      h += "<tr><td>" + esc(list[m].nick) + "</td><td>" + esc(p.why) + "</td><td>" +
        esc(p.fix || "") + "</td></tr>";
    }
    h += "</table></div>";
    return h;
  }

  function presentHtml(list) {
    var g = gather(list);
    var h = '<p class="big">짐작 ' + (g.guessN ? Math.round(g.guessSum / g.guessN) : 0) +
      '장 · 실제 ' + (g.n ? Math.round(g.realSum / g.n) : 0) + '장</p>' +
      '<p class="muted">열두 장 중 남성 그림 수예요. 학생 ' + g.n + '명 기준.</p>';

    if (g.afterN) {
      h += '<p class="muted">창고를 바꿔 본 학생 ' + g.afterN + '명만 견준 값이에요.</p>';
      h += wiseBars([
        { label: "창고 바꾸기 전", value: Math.round(g.beforeOfChanged / g.afterN) },
        { label: "창고 바꾼 뒤", value: Math.round(g.afterSum / g.afterN) }
      ], 700);
    }

    h += '<h3 style="margin-top:18px">우리가 찾아낸 까닭</h3>';
    var k, p, shown = 0;
    for (k = 0; k < list.length && shown < 6; k++) {
      p = list[k].payload || {};
      if (!p.why) { continue; }
      shown++;
      h += '<p style="font-size:22px;margin:8px 0">' + esc(p.why) + '</p>';
    }
    if (!shown) {
      h += '<p class="muted">아직 쓴 문장이 없어요.</p>';
    }
    return h;
  }
"""
