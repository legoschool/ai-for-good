# -*- coding: utf-8 -*-
"""차시 웹앱의 SPEC.md · PROMPT.md · index.html 을 만든다.

사용법 : py -3 build/make_webapp.py 6
"""
import io
import os
import sys

import tasks as T
import webapp_activities as A
from webapp_core import TEMPLATE

T.setup_console()

SHEET_ENDPOINT = "PASTE_YOUR_APPS_SCRIPT_DEPLOY_URL"
SHEET_ID = "1szLUD-hzMwQh7aaae5S9S7OS-hEXMEMj2Vhbd-hjjFM"

SOFT = {"#2563eb": "#eff6ff", "#d97706": "#fffbeb", "#059669": "#ecfdf5"}

SIGNAL_BUCKETS = [
    {"label": "초록 · 그냥 써도 돼"},
    {"label": "노랑 · 조건을 지키면 돼"},
    {"label": "주황 · 아주 조심해서만"},
    {"label": "빨강 · 쓰면 안 돼"},
]

INFO_CARDS = [
    "내 이름", "내 사진", "집 주소", "학교 이름", "친구 이름", "친구와 다툰 이야기",
    "내가 쓴 글", "모르는 낱말", "교과서에 나온 문제", "우리 반 시간표",
    "부모님 전화번호", "내 생일", "학원 이름", "내가 그린 그림", "오늘 급식 메뉴",
    "내 성적", "우리 학교 위치", "좋아하는 가수", "친구 사진", "내 아이디와 비밀번호",
    "가족 이야기", "내가 읽은 책 제목", "몸무게와 키", "우리 반 단체 사진",
]

SCENE_CARDS = [
    "독후감을 다 써 달라고 했다", "어려운 낱말의 뜻을 물었다",
    "수학 문제 푸는 방법을 물었다", "수학 숙제 답을 그대로 받아 적었다",
    "글을 다듬어 달라고 했다", "발표할 주제 아이디어를 여러 개 받았다",
    "일기를 대신 써 달라고 했다", "모르는 개념을 다시 설명해 달라고 했다",
    "그림을 대신 그려서 미술 숙제로 냈다", "포스터 배경 그림을 만들어 배치는 내가 했다",
    "친구에게 보낼 사과 편지를 통째로 만들었다", "조사한 내용이 맞는지 다시 확인해 달라고 했다",
]

SITUATION_CARDS = [
    "숙제를 AI가 다 써 준다", "모르는 개념을 다시 설명해 달라고 한다",
    "친구와 다툰 일을 AI에게만 말한다", "발표 아이디어를 여러 개 받아 본다",
    "AI로 만든 그림을 표기하고 쓴다", "친구 사진을 넣어 그림을 만든다",
    "독후감을 AI가 완성한다", "글의 표현을 다듬어 달라고 한다",
    "시험 문제를 AI로 미리 풀어 본다", "조사 자료의 출처를 확인해 달라고 한다",
    "친구 이름을 넣어 고민을 물어본다", "어려운 낱말 뜻을 물어본다",
    "일기를 AI가 대신 쓴다", "내 주장을 쓴 뒤 근거가 부족한지 물어본다",
    "힘든 마음을 AI에게만 털어놓는다", "번역을 부탁하고 어색한 곳을 내가 고친다",
    "모둠 발표 자료를 AI가 전부 만든다", "학급 규칙 아이디어를 받아 함께 고른다",
    "수행평가 답을 AI에게 받는다", "AI가 알려 준 사실을 교과서와 대조한다",
]

HABIT_ITEMS = [
    "숙제할 때 AI를 썼다",
    "모르는 것을 스스로 생각하기 전에 AI에게 먼저 물었다",
    "AI의 답을 확인하지 않고 그대로 썼다",
    "친구나 선생님 대신 AI에게 이야기했다",
    "자기 전에 화면을 오래 보았다",
]


def activity_for(lesson, data):
    n = lesson["no"]
    if n == 1:
        return A.form([
            {"label": "우리 모둠이 모은 데이터", "hint": "무엇을 몇 장 모았는지 써요.", "ph": "예: 강아지 사진 20장, 고양이 사진 20장"},
            {"label": "붙인 라벨", "ph": "예: 강아지 / 고양이"},
            {"label": "데이터를 줄였더니 어떻게 되었나요", "ph": "예: 적게 배운 쪽을 자주 틀렸습니다"},
            {"label": "사람이 한 일과 AI가 한 일", "ph": "사람 : ... / AI : ..."},
        ])
    if n == 2:
        return A.form([
            {"label": "내가 던진 질문", "ph": "사실을 확인할 수 있는 질문으로 써요"},
            {"label": "도구 A의 답 / 도구 B의 답", "ph": "두 답이 어떻게 달랐나요"},
            {"label": "검증 3단계 기록", "hint": "출처 확인 → 교과서·공공 누리집 대조 → 내 말로 정리", "ph": "1) ... 2) ... 3) ..."},
            {"label": "찾아낸 환각 사례 2가지", "ph": "무엇이 틀렸고 어떻게 확인했는지 써요"},
        ])
    if n == 3:
        return A.form([
            {"label": "관찰한 사례", "ph": "예: 의사와 간호사 그림"},
            {"label": "치우쳐 보이는 곳", "ph": "무엇이 한쪽으로 몰려 있었나요"},
            {"label": "원인은 데이터의 무엇일까", "hint": "1차시에서 데이터를 줄였을 때를 떠올려요.", "ph": ""},
            {"label": "누가 불편해질까", "ph": ""},
        ])
    if n == 4:
        return A.buckets(INFO_CARDS, [
            {"label": "넣어도 돼"}, {"label": "조건을 지키면 돼"}, {"label": "넣으면 안 돼"}])
    if n == 5:
        return A.buckets(SCENE_CARDS, [{"label": "보조"}, {"label": "대행"}])
    if n == 6:
        return A.buckets(SITUATION_CARDS, SIGNAL_BUCKETS)
    if n == 7:
        return A.vote(["%s %s" % (c["mark"], c["name"]) for c in data["aiComponents"]])
    if n == 8:
        return A.board()
    if n == 9:
        return A.form([
            {"label": "1단계 내 생각 먼저 쓰기", "hint": "5문장으로 써요. 이 칸을 채워야 다음이 열려요.", "ph": ""},
            {"label": "2단계 AI가 짚어 준 점", "hint": "고쳐 달라고 하지 말고 무엇이 부족한지 물어요.", "ph": ""},
            {"label": "받아들일 것과 받아들이지 않을 것", "ph": ""},
            {"label": "3단계 내 말로 다시 쓰기", "ph": ""},
            {"label": "무엇이 달라졌나요", "ph": ""},
        ], gated=True)
    if n == 10:
        return A.selfcheck(HABIT_ITEMS, promises=3)
    if n == 11:
        return A.form([
            {"label": "우리 모둠이 모은 문제 3개", "ph": ""},
            {"label": "고른 문제와 한 문장 정의", "hint": "누가, 언제, 무엇 때문에 불편한지 써요.", "ph": ""},
            {"label": "신호등 판단과 근거", "hint": "초록·노랑·주황·빨강 중 무엇이고 왜 그런가요", "ph": ""},
            {"label": "해결 절차 4단계", "ph": "1) ... 2) ... 3) ... 4) ..."},
        ])
    return A.form([
        {"label": "완성한 결과물", "ph": ""},
        {"label": "AI가 한 일 / 우리가 한 일", "ph": ""},
        {"label": "지킨 우리 반 약속 조항", "ph": ""},
        {"label": "12차시 성찰문", "hint": "첫 시간과 지금, 생각이 어떻게 달라졌나요", "ph": ""},
    ])


def render_html(lesson, data):
    mod = data["modules"][lesson["module"] - 1]
    accent = mod["color"]
    html = TEMPLATE
    for key, value in [
        ("__ACCENT__", accent),
        ("__ACCENT_SOFT__", SOFT.get(accent, "#f3f4f6")),
        ("__APP_NAME__", lesson["webapp"]["name"]),
        ("__SUBTITLE__", "%d차시 · %s" % (lesson["no"], lesson["shortTitle"])),
        ("__SLUG__", lesson["webapp"]["slug"]),
        ("__SHEET_ENDPOINT__", SHEET_ENDPOINT),
        ("__COPYRIGHT__", data["program"]["copyrightLine"]),
        ("__ACTIVITY__", activity_for(lesson, data)),
    ]:
        html = html.replace(key, value)
    return html


def render_spec(lesson, data):
    w = lesson["webapp"]
    L = []
    a = L.append
    a("# %d차시 웹앱 구성안 : %s" % (lesson["no"], w["name"]))
    a("")
    a("- 차시 : %d차시 %s" % (lesson["no"], lesson["shortTitle"]))
    a("- 학습 문제 : %s" % lesson["problem"])
    a("- slug : `%s`" % w["slug"])
    a("- 산출 경로 : `out/webapp/%s/index.html`" % lesson["id"])
    a("")
    a("## 무엇을 하는 앱인가")
    a("")
    a(w["purpose"])
    a("")
    a("## 화면")
    a("")
    for i, s in enumerate(w["screens"], 1):
        a("%d. %s" % (i, s))
    a("")
    a("## 교사 화면")
    a("")
    a(w.get("teacherView", ""))
    a("")
    if w.get("note"):
        a("## 이 앱만의 규칙")
        a("")
        a(w["note"])
        a("")
    a("## 공통 사양 (12개 앱이 같다)")
    a("")
    a("`spec/07_웹앱_공통사양.md` 를 그대로 따른다.")
    a("")
    a("- 방 코드 6자리 + 비밀번호 4자리 + 닉네임 입장, 혼자 체험 경로, 교사 대시보드")
    a("- Firebase 실시간 DB `/wise/%s/<방코드>/` + Google Sheets 백업" % w["slug"])
    a("- Google Sites 소스 코드 삽입용 단일 HTML. 외부 CDN 참조 없음")
    a("- 실명·학번·연락처를 수집하지 않는다")
    a("")
    a("## 저장하는 것")
    a("")
    a("```json")
    a('{ "nick": "닉네임", "group": "모둠", "app": "%s",' % w["slug"])
    a('  "room": "방코드", "at": 0, "payload": { } }')
    a("```")
    a("")
    a("## 지도 유의점")
    a("")
    for c in lesson["cautions"]:
        a("- %s" % c)
    a("")
    a("## 기기가 없을 때")
    a("")
    a(lesson["alternative"])
    a("")
    a("---")
    a("")
    a(data["program"]["copyrightLine"])
    return "\n".join(L) + "\n"


def render_prompt(lesson, data):
    w = lesson["webapp"]
    L = []
    a = L.append
    a("# %d차시 웹앱 제작 프롬프트 : %s" % (lesson["no"], w["name"]))
    a("")
    a("> 이 프롬프트 자체가 산출물이다. 선생님이 각자 고쳐 쓸 수 있도록 통째로 복사해 붙여 넣게 만들었다.")
    a("> 아래 코드 블록을 AI 도구에 그대로 붙여 넣으면 같은 앱이 다시 만들어진다.")
    a("")
    a("---")
    a("")
    a("```")
    a("초등 5·6학년 수업에서 쓸 웹앱을 만들어 줘.")
    a("HTML 파일 하나로 끝나야 하고, 외부 라이브러리나 CDN을 절대 참조하지 마.")
    a("Google Sites 의 소스 코드 삽입 기능에 그대로 붙여 넣을 것이다.")
    a("")
    a("[수업 맥락]")
    a("%d차시 %s" % (lesson["no"], lesson["shortTitle"]))
    a("학습 문제 : %s" % lesson["problem"])
    a("앱 이름 : %s" % w["name"])
    a("하는 일 : %s" % w["purpose"])
    a("")
    a("[화면]")
    for i, s in enumerate(w["screens"], 1):
        a("%d. %s" % (i, s))
    a("")
    a("[반드시 지킬 것]")
    a("1. 방 코드 6자리 + 비밀번호 4자리 + 닉네임으로 입장한다.")
    a("   방 코드 옆에 복사 버튼을 반드시 둔다.")
    a("2. 방 코드 없이 들어가는 '혼자 체험해 보기' 경로를 둔다.")
    a("   혼자 체험은 서버에 쓰지 않고 이 기기에만 저장한다.")
    a("3. 닉네임 중복을 막지 마라. 같은 닉네임이면 기존 기록을 이어받게 한다.")
    a("4. 교사가 화면을 닫아도 방이 사라지면 안 된다. 방 상태는 서버에 남는다.")
    a("5. 교사 화면에 제출 현황, 집계, CSV 내려받기, 방 잠그기를 둔다.")
    a("6. 실명, 학번, 연락처, 이메일을 묻지 마라. 사진 업로드 기능을 넣지 마라.")
    a("7. 글자 16px 이상, 누르는 곳은 44px 이상. 태블릿에서 손가락으로 쓴다.")
    a("8. 색만으로 뜻을 구분하지 마라. 색과 글자를 함께 쓴다.")
    a("9. 밝은 배경 하나로 통일한다. 교실 프로젝터에서 어두운 화면은 안 보인다.")
    a("10. 가로 스크롤이 생기면 안 된다. 넓은 표는 자체 스크롤 상자에 넣는다.")
    a("11. 정규식에 역슬래시 이스케이프(\\d, \\s, \\w)를 쓰지 마라.")
    a("    [0-9], [ \\t], [A-Za-z0-9_] 처럼 문자 클래스로 써라.")
    a("    Apps Script 로 옮길 때 역슬래시가 깨진다.")
    a("")
    a("[데이터 저장]")
    a("Firebase 실시간 DB 를 REST 로 직접 호출한다. SDK 를 붙이지 마라.")
    a("주소 : https://remind-c2610-default-rtdb.firebaseio.com")
    a("경로 : /wise/%s/<방코드>/entries" % w["slug"])
    a("실시간 갱신은 3초 폴링으로 한다. SSE 스트리밍은 학교망에서 끊긴다.")
    a("")
    a("같은 기록을 Google Sheets 에도 백업한다.")
    a("시트 : %s" % SHEET_ID)
    a("Apps Script 웹앱 주소로 fetch POST 하되 mode 는 no-cors,")
    a("Content-Type 은 text/plain 으로 보낸다. 응답을 읽지 마라.")
    a("백업이 실패해도 학생 화면이 멈추면 안 된다. catch 로 삼키고 넘어가라.")
    a("")
    a("[저장 형태]")
    a('{ "nick": "", "group": "", "app": "%s", "room": "", "at": 0, "payload": {} }' % w["slug"])
    a("payload 안에만 이 차시 고유 내용을 넣는다.")
    a("")
    a("[안전 문구]")
    if lesson["no"] == 10:
        a("모든 화면 아래에 이 문구를 고정한다.")
        a("  힘든 마음은 AI가 아니라 믿을 수 있는 어른에게 먼저 말해요.")
        a("개인 응답을 교사 화면에 띄우지 마라. 학급 익명 집계만 보여 준다.")
    else:
        a("입장 화면에 이 문구를 둔다.")
        a("  이름, 사진, 친구 이야기 같은 개인정보는 넣지 않아요.")
    a("")
    a("[말투]")
    a("학생에게 보이는 문장은 초등 5·6학년이 읽는 문장으로 써라.")
    a("한 문장 40자 이내, 존댓말 청유형으로 쓴다.")
    a("em dash 를 쓰지 마라.")
    a("```")
    a("")
    a("---")
    a("")
    a("## 고쳐 쓰는 법")
    a("")
    a("- 카드나 항목을 바꾸려면 위 프롬프트의 `[화면]` 부분을 고쳐 다시 돌린다.")
    a("- 우리 학교 상황에 맞춰 문구를 바꾸려면 `[수업 맥락]` 만 바꾸면 된다.")
    a("- 만들어진 파일은 Google Sites 에서 `삽입 → 소스 코드 삽입` 으로 붙여 넣는다.")
    a("")
    a("---")
    a("")
    a(data["program"]["copyrightLine"])
    return "\n".join(L) + "\n"


def write(path, text):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def make(no):
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == no][0]
    base = os.path.join(T.ROOT, "out", "webapp", lesson["id"])

    write(os.path.join(base, "SPEC.md"), render_spec(lesson, data))
    write(os.path.join(base, "PROMPT.md"), render_prompt(lesson, data))
    write(os.path.join(base, "index.html"), render_html(lesson, data))

    size = os.path.getsize(os.path.join(base, "index.html"))
    print("만들었다 : %s  (%s, index.html %d바이트)" % (base, lesson["webapp"]["name"], size))
    return base


def survey_activity(data):
    s = data["survey"]
    items = [i["text"] for i in s["items"]]
    opens = [o["text"] for o in s["openItems"]]
    return u"""
  var ITEMS = %s;
  var OPENS = %s;
  var OPTS = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"];

  function activityHtml() {
    var h = '<div class="card"><h2>언제 하는 설문인가요</h2>' +
      '<div class="row">' +
      '<button type="button" class="chip pick" data-i="when" data-v="0" style="width:auto;margin:0">사전 (1차시 전)</button>' +
      '<button type="button" class="chip pick" data-i="when" data-v="1" style="width:auto;margin:0">사후 (12차시 뒤)</button>' +
      '</div></div>';
    for (var i = 0; i < ITEMS.length; i++) {
      h += '<div class="card"><h3>' + (i + 1) + '. ' + esc(ITEMS[i]) + '</h3><div class="row">';
      for (var o = 0; o < OPTS.length; o++) {
        h += '<button type="button" class="chip pick" data-i="' + i + '" data-v="' + o +
          '" style="width:auto;margin:0">' + OPTS[o] + '</button>';
      }
      h += '</div></div>';
    }
    for (var k = 0; k < OPENS.length; k++) {
      h += '<div class="card"><h3>' + esc(OPENS[k]) + '</h3>' +
        '<textarea id="o' + k + '" maxlength="400"></textarea></div>';
    }
    h += '<div class="safe">솔직하게 답해 주세요. 누가 무엇을 골랐는지는 아무에게도 보이지 않아요.</div>';
    return h;
  }

  var pick = {};

  function activityInit(saved) {
    if (saved && saved.pick) { pick = saved.pick; }
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      btns[i].onclick = function () {
        pick[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint();
      };
    }
    if (saved && saved.opens) {
      for (var k = 0; k < OPENS.length; k++) {
        if ($("o" + k) && saved.opens[k]) { $("o" + k).value = saved.opens[k]; }
      }
    }
    paint();
  }

  function paint() {
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      var k = btns[i].getAttribute("data-i");
      var v = btns[i].getAttribute("data-v");
      btns[i].className = "chip pick" + (pick[k] === v ? " on" : "");
    }
  }

  function activityCollect() {
    var answered = 0;
    for (var i = 0; i < ITEMS.length; i++) { if (pick[i] !== undefined) { answered++; } }
    if (answered < ITEMS.length) {
      $("w-msg").innerHTML = '<span class="warn">아직 답하지 않은 문항이 ' +
        (ITEMS.length - answered) + '개 있어요.</span>';
      return null;
    }
    var opens = [];
    for (var k = 0; k < OPENS.length; k++) {
      opens.push($("o" + k) ? $("o" + k).value.trim() : "");
    }
    return { when: pick.when === "1" ? "사후" : "사전", pick: pick, opens: opens };
  }

  function teacherSummary(list) {
    var pre = [], post = [];
    for (var i = 0; i < ITEMS.length; i++) { pre[i] = []; post[i] = []; }
    for (var k = 0; k < list.length; k++) {
      var p = list[k].payload || {};
      if (!p.pick) { continue; }
      for (var i2 = 0; i2 < ITEMS.length; i2++) {
        var v = p.pick[i2];
        if (v === undefined) { continue; }
        var score = Number(v) + 1;
        if (i2 === 0) { score = 6 - score; }
        (p.when === "사후" ? post[i2] : pre[i2]).push(score);
      }
    }
    function avg(arr) {
      if (!arr.length) { return null; }
      var s = 0;
      for (var i = 0; i < arr.length; i++) { s += arr[i]; }
      return s / arr.length;
    }
    var h = '<p class="muted">1번 문항은 역채점하여 계산합니다. 개인 응답은 보이지 않습니다.</p>';
    h += '<div class="scroll"><table><tr><th>문항</th><th>사전 평균</th><th>사후 평균</th><th>변화량</th></tr>';
    for (var i3 = 0; i3 < ITEMS.length; i3++) {
      var a1 = avg(pre[i3]), a2 = avg(post[i3]);
      var d = (a1 !== null && a2 !== null) ? (a2 - a1).toFixed(2) : "-";
      h += "<tr><td>" + (i3 + 1) + ". " + esc(ITEMS[i3]) + "</td><td>" +
        (a1 === null ? "-" : a1.toFixed(2)) + "</td><td>" +
        (a2 === null ? "-" : a2.toFixed(2)) + "</td><td>" + d + "</td></tr>";
    }
    return h + "</table></div>";
  }
""" % (A.js(items), A.js(opens))


def make_common():
    data = T.load_lessons()
    base = os.path.join(T.ROOT, "out", "webapp", "common")
    html = TEMPLATE
    for key, value in [
        ("__ACCENT__", "#1d4ed8"),
        ("__ACCENT_SOFT__", "#eff6ff"),
        ("__APP_NAME__", "AI적정활용 자기인식 설문"),
        ("__SUBTITLE__", "공통 · 1차시 전과 12차시 뒤에 같은 8문항"),
        ("__SLUG__", "survey"),
        ("__SHEET_ENDPOINT__", SHEET_ENDPOINT),
        ("__COPYRIGHT__", data["program"]["copyrightLine"]),
        ("__ACTIVITY__", survey_activity(data)),
    ]:
        html = html.replace(key, value)
    write(os.path.join(base, "index.html"), html)

    s = data["survey"]
    spec = ["# 공통 웹앱 구성안 : AI적정활용 자기인식 설문", "",
            "- slug : `survey`", "- 산출 경로 : `out/webapp/common/index.html`",
            "- 쓰는 때 : 1차시 전(사전), 12차시 뒤(사후)", "",
            "## 무엇을 하는 앱인가", "",
            "같은 8문항을 사전과 사후에 묻고, 학급 평균의 변화량을 자동으로 계산한다.",
            "1번 문항은 역채점한다. 값이 낮아질수록 바람직한 변화이기 때문이다.", "",
            "## 문항", ""]
    for i in s["items"]:
        spec.append("%d. %s  (%s · %s)" % (i["no"], i["text"], i["skill"], i["scoring"]))
    spec += ["", "## 자유응답", ""]
    for o in s["openItems"]:
        spec.append("- %s (%s)" % (o["text"], o["when"]))
    spec += ["", "## 교사 화면", "",
             "문항별 사전 평균, 사후 평균, 변화량을 표로 보여 준다.",
             "개인 응답은 표시하지 않는다. 학급 단위 통계만 쓴다.", "",
             "## 공통 사양", "",
             "`spec/07_웹앱_공통사양.md` 를 그대로 따른다.", "",
             "---", "", data["program"]["copyrightLine"]]
    write(os.path.join(base, "SPEC.md"), "\n".join(spec) + "\n")
    print("만들었다 : %s  (사전·사후 설문)" % base)
    return base


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/make_webapp.py <차시번호|all|common>")
        return 1
    if sys.argv[1] == "common":
        make_common()
        return 0
    if sys.argv[1] == "all":
        for n in range(1, 13):
            make(n)
        make_common()
        return 0
    make(int(sys.argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
