# -*- coding: utf-8 -*-
"""8차시 약속 선포 게시판.

spec/17_웹앱_설계_L08.md 대로 만든 여정형 앱이다.

  이야기 → 광장(허브) → 역할 나누기 → 문구 공방 → 고친 곳 남기기
  → 표기표 → 게시판 → 현수막 카드

AI 가 도운 결과물에 내 이름을 걸 수 있게 만드는 것이 이 앱의 단 하나의 경험이다.
표기표 네 칸을 채우지 않으면 현수막이 올라가지 않는다.
사진 업로드 기능은 없다. 글만 다룬다. (결정 Q3)

앞선 차시에서 나온 함정을 피한다.
  - slug 가 pledge-board 다. id 와 속성에 그 문자열을 쓰지 않는다.
  - 막대는 wiseBars 로만 그린다. 캔버스를 직접 부르지 않는다.
  - activityAutofill 을 반드시 둔다.
"""

ACTIVITY = u"""
  /* ---------- 자료 ---------- */

  var JOBS = [
    {t:"주제 정하기", who:"사람"},
    {t:"자료 찾기", who:"둘 다"},
    {t:"문구 초안 만들기", who:"둘 다"},
    {t:"표현 다듬기", who:"둘 다"},
    {t:"그림 아이디어 얻기", who:"둘 다"},
    {t:"어떤 문구를 쓸지 고르기", who:"사람", must:true},
    {t:"사실 확인하기", who:"사람"},
    {t:"결과에 책임지기", who:"사람", must:true}
  ];

  var WHO = ["사람", "AI", "둘 다"];
  var WHO_ICON = ["me", "ai", "both"];

  /* 7차시에서 만든 약속 여덟 조항. 현수막 주제가 된다. */
  var PLEDGES = __PLEDGES__;

  var FRAMES = [
    "___ 할 때는 ___ 하면 된다",
    "우리 반은 ___ 를 먼저 한다",
    "___ 대신 ___ 를 해 본다"
  ];

  var BAN = ["하지 마", "하지말", "금지", "절대", "안 된다", "안된다"];

  var CREDIT = [
    {k:"what", label:"무엇을 AI로 만들었나", ph:"예: 문구 초안 세 개"},
    {k:"tool", label:"어떤 도구를 썼나", ph:"예: 교사 계정 생성형 AI"},
    {k:"human", label:"사람이 한 일", ph:"예: 주제 정하기, 고르기, 다듬기"},
    {k:"checked", label:"확인한 사람", ph:"예: 3모둠 전원과 선생님"}
  ];

  var st = {
    roles: {}, pledge: -1, usedAi: null, notes: {}, list: [], approved: {},
    badges: {}, asked: {}
  };

  /* ---------- 화면 ---------- */

  function q(id, inner) {
    return '<section class="quest" data-q="' + id + '">' + inner + '</section>';
  }

  function activityHtml() {
    var h = "";

    h += q("story",
      '<div class="card"><span class="pill">이야기</span>' +
      '<h2 style="margin-top:10px">선포식 광장</h2>' +
      '<p style="margin-top:10px">지난 시간에 우리 반 약속을 만들었어요. ' +
      '그런데 교실 뒤에 붙여만 두면 아무도 읽지 않아요.</p>' +
      '<p style="margin-top:8px">오늘은 광장에 <b>현수막</b>을 겁니다. ' +
      '현수막은 세 칸을 채워야 올라가요. <b>역할 · 문구 · 표기.</b></p>' +
      '<p style="margin-top:8px">특히 표기가 중요해요. ' +
      '무엇을 AI가 하고 무엇을 우리가 했는지 밝혀야 <b>내 이름을 걸 수 있어요.</b></p>' +
      '<p class="muted" style="margin-top:8px">사진을 올리는 기능은 없어요. ' +
      '포스터는 종이로 만들고, 앱에는 글만 씁니다.</p>' +
      '<div class="row" style="margin-top:14px">' +
      '<button type="button" id="go-hub">광장으로 들어가기</button></div></div>');

    h += q("hub",
      '<div class="card"><h2>광장</h2>' +
      '<p class="muted">현수막 세 칸을 채우면 올릴 수 있어요.</p>' +
      '<div class="g2" style="margin-top:12px">' +
      '<button type="button" class="tile" id="t-role">' + wiseIcon("both", 30) +
      '<span>역할 나누기</span><small id="s-role">여덟 가지 일을 나눠요</small></button>' +
      '<button type="button" class="tile" id="t-copy">' + wiseIcon("write", 30) +
      '<span>문구 공방</span><small id="s-copy">제목과 문구 쓰기</small></button>' +
      '<button type="button" class="tile" id="t-fix">' + wiseIcon("again", 30) +
      '<span>고친 곳 남기기</span><small id="s-fix">AI 초안을 어떻게 고쳤나</small></button>' +
      '<button type="button" class="tile" id="t-credit">' + wiseIcon("check", 30) +
      '<span>표기표</span><small id="s-credit">네 칸을 채워야 게시</small></button>' +
      '<button type="button" class="tile" id="t-board">' + wiseIcon("talk", 30) +
      '<span>게시판</span><small id="s-board">다른 모둠 현수막 읽기</small></button>' +
      '<button type="button" class="tile" id="t-card">' + wiseIcon("star", 30) +
      '<span>현수막 카드</span><small id="s-card">그림으로 저장</small></button>' +
      '</div></div>' +
      '<div class="card"><h3>우리 모둠 배지</h3><div id="badges" class="row" style="margin-top:8px"></div></div>');

    h += q("role",
      '<div class="card"><span class="pill">1단계</span>' +
      '<h2 style="margin-top:10px">역할 나누기</h2>' +
      '<p class="muted">여덟 가지 일을 누가 할지 정해요. 정답은 없지만 우리 반 기준은 있어요.</p>' +
      '<div id="rolebox"></div>' +
      '<div id="rolebar" style="margin-top:12px"></div>' +
      '<p class="muted" id="rolemsg" style="margin-top:8px"></p>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">광장으로</button></div></div>');

    h += q("copy",
      '<div class="card"><span class="pill">2단계</span>' +
      '<h2 style="margin-top:10px">문구 공방</h2>' +
      '<p class="muted">우리 반 약속 가운데 하나를 골라 현수막 주제로 삼아요.</p>' +
      '<div id="plist"></div>' +
      '<label for="c-title">현수막 제목</label>' +
      '<input id="c-title" maxlength="30" placeholder="예: 생각이 먼저">' +
      '<label>문구 틀 (누르면 아래 칸에 들어가요)</label><div class="row">' +
      frameButtons() + '</div>' +
      '<label for="c-body">현수막 문구</label>' +
      '<textarea id="c-body" maxlength="120" placeholder="금지가 아니라 어떤 조건이면 되는지로 써요"></textarea>' +
      '<div id="copymsg" style="margin-top:8px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="c-check" class="ghost">문구 점검하기</button>' +
      '<button type="button" class="plain back">광장으로</button></div></div>');

    h += q("fix",
      '<div class="card"><span class="pill">3단계</span>' +
      '<h2 style="margin-top:10px">고친 곳 남기기</h2>' +
      '<p class="muted">AI 도움을 받았다면 어디를 고쳤는지 남겨요. 이것이 정직한 방법이에요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" class="chip yn" data-y="1" style="width:auto;margin:0">AI 도움을 받았어요</button>' +
      '<button type="button" class="chip yn" data-y="0" style="width:auto;margin:0">우리끼리 썼어요</button>' +
      '</div>' +
      '<div id="fixbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">광장으로</button></div></div>');

    h += q("credit",
      '<div class="card"><span class="pill">4단계</span>' +
      '<h2 style="margin-top:10px">AI 활용 표기표</h2>' +
      '<p class="muted">네 칸을 다 채워야 현수막을 올릴 수 있어요.</p>' +
      creditFields() +
      '<div id="creditmsg" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="c-post">현수막 올리기</button>' +
      '<button type="button" class="plain back">광장으로</button></div></div>');

    h += q("board",
      '<div class="card"><span class="pill">광장</span>' +
      '<h2 style="margin-top:10px">게시판</h2>' +
      '<p class="muted">관리인(선생님)이 확인한 현수막이 크게 걸려요. ' +
      '읽고 배운 점을 한 줄 남겨 주세요.</p>' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="b-load">게시판 불러오기</button></div>' +
      '<div id="boardbox" style="margin-top:12px"></div>' +
      '<div class="row" style="margin-top:12px"><button type="button" class="plain back">광장으로</button></div></div>');

    h += q("card",
      '<div class="card"><span class="pill">기록</span>' +
      '<h2 style="margin-top:10px">우리 모둠 현수막</h2>' +
      '<div id="mine"></div>' +
      '<div class="row" style="margin-top:12px">' +
      '<button type="button" id="save-card" class="ghost">현수막 그림으로 저장</button>' +
      '<button type="button" class="plain back">광장으로</button></div></div>' +
      '<div class="safe">이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요. ' +
      '현수막에는 모둠 이름만 씁니다.</div>');

    return h;
  }

  function frameButtons() {
    var h = "";
    for (var i = 0; i < FRAMES.length; i++) {
      h += '<button type="button" class="chip fr" data-f="' + i +
        '" style="width:auto;margin:0;font-size:14px">' + esc(FRAMES[i]) + '</button>';
    }
    return h;
  }

  function creditFields() {
    var h = "";
    for (var i = 0; i < CREDIT.length; i++) {
      h += '<label for="cr' + i + '">' + esc(CREDIT[i].label) + '</label>' +
        '<input id="cr' + i + '" maxlength="80" placeholder="' + esc(CREDIT[i].ph) + '">';
    }
    return h;
  }

  /* ---------- 1단계 역할 ---------- */

  function roleHtml() {
    var h = "";
    for (var i = 0; i < JOBS.length; i++) {
      h += '<div class="card" style="margin:10px 0;padding:14px">' +
        '<p style="margin:0 0 8px;font-weight:800">' + esc(JOBS[i].t) + '</p><div class="row">';
      for (var w = 0; w < WHO.length; w++) {
        h += '<button type="button" class="chip rl' + (st.roles[i] === w ? " on" : "") +
          '" data-r="' + i + '" data-w="' + w + '" style="width:auto;margin:0">' +
          wiseIcon(WHO_ICON[w], 22) + esc(WHO[w]) + '</button>';
      }
      h += '</div></div>';
    }
    return h;
  }

  function roleCount() {
    var n = 0;
    for (var k in st.roles) { if (st.roles.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function paintRoleBar() {
    if (!$("rolebar")) { return; }
    var c = [0, 0, 0];
    for (var k in st.roles) { if (st.roles.hasOwnProperty(k)) { c[st.roles[k]] += 1; } }
    $("rolebar").innerHTML = wiseBars([
      { label: "사람", value: c[0], color: "#00D45A" },
      { label: "AI", value: c[1], color: "#2B59E0" },
      { label: "둘 다", value: c[2], color: "#FFE24B" }
    ], 520);
    var msg = "나눈 일 " + roleCount() + " / " + JOBS.length + "개.";
    var slip = [];
    for (var i = 0; i < JOBS.length; i++) {
      if (JOBS[i].must && st.roles[i] === 1) { slip.push(JOBS[i].t); }
    }
    if (slip.length) {
      msg += " 결정과 책임은 사람이 하기로 우리 반이 정했어요. 다시 볼 것 : " + slip.join(", ");
    }
    $("rolemsg").textContent = msg;
  }

  function bindRole() {
    $("rolebox").innerHTML = roleHtml();
    var rs = document.querySelectorAll("#activity .rl");
    for (var i = 0; i < rs.length; i++) {
      rs[i].onclick = function () {
        var r = Number(this.getAttribute("data-r")), w = Number(this.getAttribute("data-w"));
        st.roles[r] = w;
        if (JOBS[r].must && w === 1 && !st.asked[r]) {
          st.asked[r] = true;
          wiseToast("결정과 책임은 사람이 하기로 정했어요. 그대로 둘까요?");
        }
        bindRole();
        paintRoleBar();
        paintHub();
        if (roleCount() >= JOBS.length) { award("역할 나눔"); }
      };
    }
    paintRoleBar();
  }

  /* ---------- 2단계 문구 ---------- */

  function pledgeHtml() {
    var h = '<div class="row" style="margin-bottom:10px">';
    for (var i = 0; i < PLEDGES.length; i++) {
      h += '<button type="button" class="chip pl' + (st.pledge === i ? " on" : "") +
        '" data-p="' + i + '" style="width:auto;margin:0;font-size:14px">' +
        esc(PLEDGES[i].mark) + ' ' + esc(PLEDGES[i].name) + '</button>';
    }
    return h + '</div><p class="muted" id="pledgetext">약속을 하나 골라요.</p>';
  }

  function checkCopy() {
    var title = val("c-title"), body = val("c-body");
    var h = "";
    var found = [];
    for (var i = 0; i < BAN.length; i++) {
      if (body.indexOf(BAN[i]) >= 0) { found.push(BAN[i]); }
    }
    var cond = body.indexOf("면") >= 0 || body.indexOf("때") >= 0 || body.indexOf("먼저") >= 0;
    if (!title || body.length < 8) {
      h += '<p class="muted">제목과 문구를 채워요.</p>';
    } else {
      if (found.length) {
        h += '<p class="warn">금지하는 말이 있어요 : ' + esc(found.join(", ")) +
          '. 어떤 조건이면 되는지로 바꿔 봐요.</p>';
      }
      if (!cond) {
        h += '<p class="warn">조건이 보이지 않아요. 언제, 무엇을 먼저 하는지 넣어 봐요.</p>';
      }
      if (!found.length && cond) {
        h += '<p class="ok">조건형 문구예요. 현수막에 걸 수 있어요.</p>';
        award("조건형 문구");
      }
    }
    $("copymsg").innerHTML = h;
  }

  /* ---------- 3단계 고친 곳 ---------- */

  function fixHtml() {
    if (st.usedAi === null) {
      return '<p class="muted">위에서 하나를 골라요.</p>';
    }
    if (st.usedAi === false) {
      return '<p class="ok">우리끼리 썼다고 표기할게요. 표기표에도 그대로 적어요.</p>';
    }
    var h = '<label for="f-draft">AI가 준 문장</label>' +
      '<textarea id="f-draft" maxlength="200" placeholder="받은 그대로 붙여 써요"></textarea>' +
      '<label for="f-fixed">우리가 고친 문장</label>' +
      '<textarea id="f-fixed" maxlength="200" placeholder="우리 말로 바꾼 문장"></textarea>' +
      '<label for="f-why">고친 까닭</label>' +
      '<input id="f-why" maxlength="80" placeholder="예: 우리 반 말투로 바꿨습니다">' +
      '<div class="row" style="margin-top:10px">' +
      '<button type="button" id="f-check" class="ghost">얼마나 고쳤는지 보기</button></div>' +
      '<div id="fixmsg" style="margin-top:10px"></div>';
    return h;
  }

  function words(text) {
    var raw = String(text || "").split(/[ ,.]+/), out = [];
    for (var i = 0; i < raw.length; i++) {
      if (raw[i].trim().length > 1) { out.push(raw[i].trim()); }
    }
    return out;
  }

  function changedPct(a, b) {
    var wa = words(a), wb = words(b);
    if (!wa.length || !wb.length) { return 0; }
    var seen = {}, same = 0;
    for (var i = 0; i < wa.length; i++) { seen[wa[i]] = true; }
    for (var k = 0; k < wb.length; k++) { if (seen[wb[k]]) { same++; } }
    return Math.max(0, 100 - Math.round(same * 100 / wb.length));
  }

  function bindFix() {
    $("fixbox").innerHTML = fixHtml();
    var yns = document.querySelectorAll("#activity .yn");
    for (var i = 0; i < yns.length; i++) {
      yns[i].onclick = function () {
        st.usedAi = this.getAttribute("data-y") === "1";
        var all = document.querySelectorAll("#activity .yn");
        for (var k = 0; k < all.length; k++) {
          all[k].className = "chip yn" +
            ((all[k].getAttribute("data-y") === "1") === st.usedAi ? " on" : "");
        }
        bindFix();
        paintHub();
      };
    }
    if ($("f-check")) {
      $("f-check").onclick = function () {
        var btn = this;
        wiseButtonBusy(btn, true, "견주는 중");
        setTimeout(function () {
          wiseButtonBusy(btn, false);
          var pctv = changedPct(val("f-draft"), val("f-fixed"));
          var msg = '<p>고친 정도 ' + pctv + '%</p>' + barHtml(pctv, 100);
          if (pctv < 20) {
            msg += '<p class="warn">고친 곳이 거의 없어요. 우리 말로 더 바꿔 볼까요?</p>';
          } else {
            msg += '<p class="ok">우리 말로 바꾸었어요. 표기표에 그대로 적어요.</p>';
            award("우리 말로 고침");
          }
          $("fixmsg").innerHTML = msg;
          paintHub();
        }, 420);
      };
    }
  }

  /* ---------- 4단계 표기표 ---------- */

  function creditFilled() {
    var n = 0;
    for (var i = 0; i < CREDIT.length; i++) {
      if (val("cr" + i).length > 1) { n++; }
    }
    return n;
  }

  function paintCredit() {
    if (!$("creditmsg")) { return; }
    var n = creditFilled();
    var ready = n === CREDIT.length && val("c-title") && val("c-body").length > 7;
    var h = '<p class="muted">채운 칸 ' + n + ' / ' + CREDIT.length + '</p>' + barHtml(n, CREDIT.length);
    if (!val("c-title") || val("c-body").length < 8) {
      h += '<p class="warn">문구 공방에서 제목과 문구를 먼저 써 주세요.</p>';
    } else if (n < CREDIT.length) {
      h += '<p class="warn">표기표를 다 채워야 현수막이 올라가요.</p>';
    } else {
      h += '<p class="ok">준비됐어요. 현수막 올리기를 눌러요.</p>';
    }
    $("creditmsg").innerHTML = h;
    if ($("c-post")) { $("c-post").disabled = !ready; }
    if (n === CREDIT.length) { award("표기 완료"); }
  }

  function creditObj() {
    var out = {};
    for (var i = 0; i < CREDIT.length; i++) { out[CREDIT[i].k] = val("cr" + i); }
    return out;
  }

  /* ---------- 게시판 ---------- */

  function loadBoard() {
    if (me.solo) {
      $("boardbox").innerHTML = '<p class="muted">둘러보기 중에는 게시판이 비어 있어요. ' +
        '현수막 만들기는 그대로 해 볼 수 있어요.</p>';
      return;
    }
    $("boardbox").innerHTML = wiseSpinner("게시판을 불러오는 중이에요", true) + wiseSkeleton(3);
    dbGet(me.room + "/entries").then(function (data) {
      st.list = [];
      for (var k in data) {
        if (!data.hasOwnProperty(k)) { continue; }
        var p = data[k].payload;
        if (p && p.title) {
          st.list.push({ key: k, nick: data[k].nick, group: data[k].group, p: p });
        }
      }
      return dbGet(me.room + "/approve");
    }).then(function (ap) {
      st.approved = ap || {};
      $("boardbox").innerHTML = boardHtml();
      bindBoardButtons();
      paintHub();
    })["catch"](function () {
      $("boardbox").innerHTML = '<p class="warn">지금은 불러올 수 없어요. 잠시 뒤 다시 눌러요.</p>';
    });
  }

  function boardHtml() {
    if (!st.list.length) {
      return '<p class="muted">아직 올라온 현수막이 없어요.</p>';
    }
    var h = "";
    for (var i = 0; i < st.list.length; i++) {
      var it = st.list[i];
      var ok = st.approved[it.nick];
      h += '<div class="card" style="margin-bottom:10px' + (ok ? "" : ";opacity:.62") + '">' +
        '<span class="pill">' + esc(it.group || "모둠") + '</span> ' +
        '<span class="tag">' + (ok ? "확인 완료" : "관리인 확인 중") + '</span>' +
        '<p style="font-size:' + (ok ? "22px" : "17px") + ';font-weight:900;margin:10px 0">' +
        esc(it.p.title) + '</p>' +
        '<p style="font-size:' + (ok ? "18px" : "15px") + '">' + esc(it.p.body) + '</p>';
      if (it.p.credit) {
        h += '<p class="muted" style="margin-top:8px">AI 활용 : ' + esc(it.p.credit.what || "") +
          ' · 사람이 한 일 : ' + esc(it.p.credit.human || "") + '</p>';
      }
      if (ok && it.nick !== me.nick) {
        h += '<label for="nt' + i + '">이 현수막에서 배운 점</label>' +
          '<input id="nt' + i + '" maxlength="60" placeholder="한 줄로 남겨요">' +
          '<button type="button" class="chip send" data-i="' + i +
          '" style="width:auto;margin-top:8px">배운 점 보내기</button>';
      }
      h += '</div>';
    }
    return h;
  }

  function bindBoardButtons() {
    var bs = document.querySelectorAll("#activity .send");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () {
        var idx = Number(this.getAttribute("data-i")), btn = this;
        var text = $("nt" + idx) ? val("nt" + idx) : "";
        if (!text) { wiseToast("배운 점을 한 줄 써 주세요."); return; }
        wiseButtonBusy(btn, true, "보내는 중");
        st.notes[st.list[idx].key] = text;
        dbPush(me.room + "/votes", {
          key: st.list[idx].key, nick: me.nick, at: Date.now(), note: text
        }).then(function () {
          wiseButtonBusy(btn, false);
          btn.textContent = "보냈어요";
          btn.className = "chip send on";
          award("함께 읽기");
        })["catch"](function () {
          wiseButtonBusy(btn, false);
          wiseToast("지금은 보낼 수 없어요. 잠시 뒤 다시 눌러요.");
        });
      };
    }
  }

  /* ---------- 현수막 카드 ---------- */

  function paintMine() {
    if (!$("mine")) { return; }
    var title = val("c-title"), body = val("c-body");
    if (!title && !body) {
      $("mine").innerHTML = '<p class="muted">문구 공방에서 제목과 문구를 쓰면 여기에 보여요.</p>';
      return;
    }
    var cr = creditObj();
    var h = '<div class="card" style="background:var(--accent);color:#fff;border-color:var(--line)">' +
      '<p style="font-size:24px;font-weight:900">' + esc(title || "제목을 써요") + '</p>' +
      '<p style="font-size:18px;margin-top:8px">' + esc(body || "문구를 써요") + '</p>' +
      '<p style="margin-top:10px;font-size:13px;opacity:.92">' +
      esc(me.group || me.nick) + ' 모둠</p></div>';
    h += '<div class="scroll" style="margin-top:12px"><table>' +
      '<tr><th>무엇을 AI로</th><td>' + esc(cr.what || "-") + '</td></tr>' +
      '<tr><th>쓴 도구</th><td>' + esc(cr.tool || "-") + '</td></tr>' +
      '<tr><th>사람이 한 일</th><td>' + esc(cr.human || "-") + '</td></tr>' +
      '<tr><th>확인한 사람</th><td>' + esc(cr.checked || "-") + '</td></tr></table></div>';
    $("mine").innerHTML = h;
  }

  /* ---------- 배지와 허브 ---------- */

  function award(name) {
    if (st.badges[name]) { return; }
    st.badges[name] = true;
    wiseToast("배지를 받았어요 : " + name);
    paintHub();
  }

  function noteCount() {
    var n = 0;
    for (var k in st.notes) { if (st.notes.hasOwnProperty(k)) { n++; } }
    return n;
  }

  function paintHub() {
    if (!$("s-role")) { return; }
    $("s-role").textContent = "나눈 일 " + roleCount() + " / " + JOBS.length + "개";
    $("s-copy").textContent = val("c-title") ? ("제목 : " + val("c-title")) : "제목과 문구 쓰기";
    $("s-fix").textContent = st.usedAi === null ? "AI 초안을 어떻게 고쳤나"
      : (st.usedAi ? "AI 도움을 받았다고 표시함" : "우리끼리 썼다고 표시함");
    $("s-credit").textContent = "채운 칸 " + creditFilled() + " / " + CREDIT.length;
    $("s-board").textContent = st.list.length ? ("올라온 현수막 " + st.list.length + "개") : "다른 모둠 현수막 읽기";
    $("s-card").textContent = "그림으로 저장";
    var tiles = [["t-role", roleCount() >= JOBS.length], ["t-copy", !!val("c-title")],
      ["t-fix", st.usedAi !== null], ["t-credit", creditFilled() === CREDIT.length],
      ["t-board", st.list.length > 0], ["t-card", false]];
    for (var i = 0; i < tiles.length; i++) {
      if ($(tiles[i][0])) { $(tiles[i][0]).className = "tile" + (tiles[i][1] ? " done" : ""); }
    }
    var names = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { names.push(b); } }
    $("badges").innerHTML = names.length
      ? names.map(function (n) { return '<span class="pill">' + esc(n) + '</span>'; }).join(" ")
      : '<span class="muted">아직 없어요. 역할 나누기부터 해 볼까요?</span>';
    wiseHud([
      { label: "역할", done: roleCount(), total: JOBS.length },
      { label: "표기", done: creditFilled(), total: CREDIT.length },
      { label: "배운 점 남김", done: noteCount(), total: 3 }
    ]);
  }

  /* ---------- 흐름 ---------- */

  function val(id) { return $(id) ? $(id).value.trim() : ""; }

  function activityEnter(id) {
    if (id === "role") { bindRole(); }
    if (id === "copy") { checkCopy(); }
    if (id === "fix") { bindFix(); }
    if (id === "credit") { paintCredit(); }
    if (id === "card") { paintMine(); }
    if (id === "hub") { paintHub(); }
  }

  function activityInit(saved) {
    if (saved) {
      if (saved.roles) { st.roles = saved.roles; }
      if (saved.pledgeNo !== undefined) { st.pledge = saved.pledgeNo; }
      if (saved.usedAi !== undefined) { st.usedAi = saved.usedAi; }
    }
    $("plist").innerHTML = pledgeHtml();

    $("go-hub").onclick = function () { wiseGo("hub"); };
    $("t-role").onclick = function () { wiseGo("role"); };
    $("t-copy").onclick = function () { wiseGo("copy"); };
    $("t-fix").onclick = function () { wiseGo("fix"); };
    $("t-credit").onclick = function () { wiseGo("credit"); };
    $("t-board").onclick = function () { wiseGo("board"); };
    $("t-card").onclick = function () { wiseGo("card"); };

    var pls = document.querySelectorAll("#activity .pl");
    for (var i = 0; i < pls.length; i++) {
      pls[i].onclick = function () {
        st.pledge = Number(this.getAttribute("data-p"));
        var all = document.querySelectorAll("#activity .pl");
        for (var k = 0; k < all.length; k++) {
          all[k].className = "chip pl" + (Number(all[k].getAttribute("data-p")) === st.pledge ? " on" : "");
        }
        $("pledgetext").textContent = PLEDGES[st.pledge].say;
        paintHub();
      };
    }
    var frs = document.querySelectorAll("#activity .fr");
    for (var f = 0; f < frs.length; f++) {
      frs[f].onclick = function () {
        var t = FRAMES[Number(this.getAttribute("data-f"))];
        if ($("c-body") && !val("c-body")) { $("c-body").value = t; }
        checkCopy();
      };
    }
    $("c-check").onclick = checkCopy;
    if ($("c-title")) { $("c-title").oninput = function () { checkCopy(); paintHub(); }; }
    if ($("c-body")) { $("c-body").oninput = checkCopy; }
    for (var c = 0; c < CREDIT.length; c++) {
      if ($("cr" + c)) { $("cr" + c).oninput = paintCredit; }
    }
    $("b-load").onclick = loadBoard;
    $("c-post").onclick = function () {
      wiseToast("아래 제출하기를 누르면 관리인 확인을 기다립니다.");
      wiseGo("card");
    };
    $("save-card").onclick = function () {
      var cr = creditObj();
      wiseCardPng("우리 반 AI 약속 · " + (me.group || me.nick), [
        val("c-title") || "제목",
        val("c-body") || "문구",
        "AI 활용 : " + (cr.what || "없음"),
        "사람이 한 일 : " + (cr.human || "-"),
        "확인한 사람 : " + (cr.checked || "-")
      ], "wise_l08_" + me.nick);
      award("현수막 저장");
    };
    var backs = document.querySelectorAll("#activity .back");
    for (var b = 0; b < backs.length; b++) {
      backs[b].onclick = function () { wiseGo("hub"); };
    }
    wiseNote("표기표를 채우지 않으면 현수막이 올라가지 않아요.");
    wiseGo("story");
    paintHub();
  }

  function activityDraft() {
    return { roles: st.roles, pledgeNo: st.pledge, usedAi: st.usedAi,
      title: val("c-title"), body: val("c-body") };
  }

  function activityAutofill() {
    for (var i = 0; i < JOBS.length; i++) { st.roles[i] = i % 3; }
    st.roles[5] = 0;
    st.roles[7] = 0;
    st.pledge = 1;
    st.usedAi = true;
    if ($("c-title")) { $("c-title").value = "생각이 먼저"; }
    if ($("c-body")) { $("c-body").value = "숙제를 할 때는 내 생각을 먼저 쓰고 나서 도움을 받는다"; }
    var fill = ["문구 초안 세 개", "교사 계정 생성형 AI", "주제 정하기, 고르기, 다듬기", "3모둠 전원과 선생님"];
    for (var c = 0; c < CREDIT.length; c++) {
      if ($("cr" + c)) { $("cr" + c).value = fill[c]; }
    }
  }

  function activityCollect() {
    if (roleCount() < 4) {
      $("w-msg").innerHTML = '<span class="warn">역할을 네 가지 넘게 나눈 뒤에 제출해요. 지금 ' +
        roleCount() + '개예요.</span>';
      return null;
    }
    if (!val("c-title") || val("c-body").length < 8) {
      $("w-msg").innerHTML = '<span class="warn">현수막 제목과 문구를 써 주세요.</span>';
      return null;
    }
    if (creditFilled() < CREDIT.length) {
      $("w-msg").innerHTML = '<span class="warn">AI 활용 표기표 네 칸을 다 채워야 게시할 수 있어요. ' +
        '지금 ' + creditFilled() + '칸이에요.</span>';
      return null;
    }
    var badges = [];
    for (var b in st.badges) { if (st.badges.hasOwnProperty(b)) { badges.push(b); } }
    wiseCelebrate("현수막을 올렸어요", [
      "제목 <b>" + esc(val("c-title")) + "</b>",
      "표기표 네 칸을 모두 채웠어요.",
      "선생님이 확인하면 광장에 크게 걸려요.",
      "다음 시간에는 내 생각을 먼저 쓰고 AI에게 검토를 받아 봅니다."
    ], "좋아요");
    return {
      roles: st.roles, pledgeNo: st.pledge,
      title: val("c-title"), body: val("c-body"),
      usedAi: st.usedAi,
      draft: val("f-draft"), fixed: val("f-fixed"), whyFix: val("f-why"),
      changed: changedPct(val("f-draft"), val("f-fixed")),
      credit: creditObj(), notes: noteCount(), badges: badges
    };
  }

  /* ---------- 교사 화면 ---------- */

  function teacherSummary(list) {
    var full = 0, aiDecide = 0, changedSum = 0, changedN = 0;
    for (var i = 0; i < list.length; i++) {
      var p = list[i].payload || {};
      if (!p.title) { continue; }
      var cr = p.credit || {};
      if (cr.what && cr.tool && cr.human && cr.checked) { full++; }
      var r = p.roles || {};
      if (r["5"] === 1 || r["7"] === 1) { aiDecide++; }
      if (p.usedAi && p.changed !== undefined) { changedSum += p.changed; changedN++; }
    }
    var h = '<p class="muted">표기표를 다 채운 모둠 ' + full + ' / ' + list.length +
      ' · 고친 정도 평균 ' + (changedN ? Math.round(changedSum / changedN) : 0) + '%</p>';
    if (aiDecide) {
      h += '<p class="warn">고르기나 책임지기를 AI 몫으로 둔 모둠이 ' + aiDecide +
        '개예요. 그 까닭을 물어봅니다.</p>';
    }
    h += '<p class="muted" style="margin-top:8px">확인 도장을 누르면 학생 게시판에 크게 걸립니다.</p>';
    h += '<div class="scroll" style="margin-top:10px"><table>' +
      '<tr><th>모둠</th><th>제목</th><th>문구</th><th>AI 활용</th><th>사람이 한 일</th><th>확인</th></tr>';
    for (var k = 0; k < list.length; k++) {
      var q2 = list[k].payload || {};
      if (!q2.title) { continue; }
      var c2 = q2.credit || {};
      var miss = !(c2.what && c2.tool && c2.human && c2.checked);
      h += "<tr><td>" + esc(list[k].group || list[k].nick) + "</td><td>" + esc(q2.title) +
        "</td><td>" + esc(q2.body) + "</td><td>" +
        (miss ? '<span class="warn">표기 미완</span>' : esc(c2.what)) + "</td><td>" +
        esc(c2.human || "") + '</td><td><button type="button" class="chip ok-stamp" data-n="' +
        esc(list[k].nick) + '" style="width:auto;margin:0">확인 도장</button></td></tr>';
    }
    h += "</table></div>";
    setTimeout(bindStamps, 0);
    return h;
  }

  /* 교사가 누르는 승인 도장. 학생 payload 가 아니라 따로 둔 경로에 쓴다. */
  function bindStamps() {
    var bs = document.querySelectorAll("#t-summary .ok-stamp");
    for (var i = 0; i < bs.length; i++) {
      bs[i].onclick = function () {
        var nick = this.getAttribute("data-n"), btn = this;
        wiseButtonBusy(btn, true, "도장 찍는 중");
        dbPut("approve/" + nick, true).then(function () {
          wiseButtonBusy(btn, false);
          btn.textContent = "확인함";
          btn.className = "chip ok-stamp on";
        })["catch"](function () {
          wiseButtonBusy(btn, false);
          wiseToast("도장을 찍지 못했어요.");
        });
      };
    }
  }

  function presentHtml(list) {
    var h = '<p class="muted">확인한 현수막을 함께 읽어요.</p>';
    var shown = 0;
    for (var i = 0; i < list.length && shown < 6; i++) {
      var p = list[i].payload || {};
      if (!p.title) { continue; }
      shown++;
      h += '<div class="card"><p class="pill">' + esc(list[i].group || list[i].nick) + '</p>' +
        '<p class="big" style="margin-top:10px">' + esc(p.title) + '</p>' +
        '<p style="font-size:22px;margin-top:8px">' + esc(p.body) + '</p>' +
        '<p class="muted" style="margin-top:8px">AI 활용 : ' +
        esc((p.credit || {}).what || "없음") + '</p></div>';
    }
    if (!shown) { h += '<p class="muted">아직 올라온 현수막이 없어요.</p>'; }
    return h;
  }
"""


# 약속 여덟 조항은 lessons.json 에서 가져온다.
# make_webapp.py 는 공유 파일이라 건드리지 않는다. 이 모듈이 스스로 채운다.
import tasks as _T
import webapp_activities as _A

_data = _T.load_lessons()
_pledges = [{"mark": c["mark"], "name": c["name"], "say": c["pledge"]}
            for c in _data["aiComponents"]]
ACTIVITY = ACTIVITY.replace("__PLEDGES__", _A.js(_pledges))
