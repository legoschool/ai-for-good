# -*- coding: utf-8 -*-
"""차시 웹앱의 SPEC.md · PROMPT.md · index.html 을 만든다.

사용법 : py -3 build/make_webapp.py 6
"""
import io
import os
import sys

import site_art as ART
import webapp_art as WART
import tasks as T
import webapp_activities as A
from webapp_l01 import ACTIVITY as L01_ACTIVITY
from webapp_l02 import ACTIVITY as L02_ACTIVITY
from webapp_l03 import ACTIVITY as L03_ACTIVITY
from webapp_l04 import ACTIVITY as L04_ACTIVITY
from webapp_l05 import ACTIVITY as L05_ACTIVITY
from webapp_l06 import ACTIVITY as L06_ACTIVITY
from webapp_l07 import ACTIVITY as L07_ACTIVITY
from webapp_l08 import ACTIVITY as L08_ACTIVITY
from webapp_l09 import ACTIVITY as L09_ACTIVITY
from webapp_l10 import ACTIVITY as L10_ACTIVITY
from webapp_l11 import ACTIVITY as L11_ACTIVITY
from webapp_l12 import ACTIVITY as L12_ACTIVITY
from webapp_core import TEMPLATE

T.setup_console()

SHEET_ID = "1szLUD-hzMwQh7aaae5S9S7OS-hEXMEMj2Vhbd-hjjFM"

# Apps Script 웹 앱 배포 주소. data/sheet_endpoint.txt 에 한 줄로 둔다.
# 파일이 없으면 자리표시자를 쓰고, 앱은 시트 백업만 건너뛴다.
# 이 주소는 학생 브라우저에서 호출하므로 감출 수 없다.
# 이상한 기록은 Apps Script 쪽에서 모양을 검사해 걸러 낸다.
ENDPOINT_FILE = os.path.join(T.ROOT, "data", "sheet_endpoint.txt")
PLACEHOLDER = "PASTE_YOUR_APPS_SCRIPT_DEPLOY_URL"


def sheet_endpoint():
    if os.path.exists(ENDPOINT_FILE):
        with io.open(ENDPOINT_FILE, encoding="utf-8") as f:
            url = f.read().strip()
        if url.startswith("https://"):
            return url
    return PLACEHOLDER


SHEET_ENDPOINT = sheet_endpoint()

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
        # 1차시는 40분을 끌 수 있도록 브라우저 안에서 도는 분류기를 따로 만들었다.
        return L01_ACTIVITY
    if n == 2:
        # 2차시는 교사가 미리 검증한 답변 세트를 담아 생성형 AI 없이 돌아가게 했다.
        return L02_ACTIVITY
    if n == 0:
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
        # 3차시는 학습 데이터 분포를 학생이 바꾸어 결과가 달라지는 것을 직접 본다.
        return L03_ACTIVITY
    if n == 4:
        # 4차시는 카드마다 숨은 위험도를 두고 판단 뒤에 개인 리포트를 돌려준다.
        return L04_ACTIVITY
    if n == 5:
        # 5차시는 생각 축과 결과물 축 두 개로 판단해 경계 사례를 드러낸다.
        return L05_ACTIVITY
    if n == 6:
        # 6차시는 1차 판정, 학급 분포 확인, 2차 판정의 두 라운드로 돈다.
        return L06_ACTIVITY
    if n == 7:
        # 7차시는 금지형 문장을 감지해 조건형으로 바꾸도록 돕는 조항 작성기다.
        crit = ["%s %s" % (c["mark"], c["name"]) for c in data["aiComponents"]]
        return L07_ACTIVITY.replace("__CRITERIA__", A.js(crit))
    if n == 8:
        # 8차시는 화면 안에서 약속 카드를 만들고 표기 없이는 제출되지 않는다.
        return L08_ACTIVITY
    if n == 9:
        # 9차시는 단계 잠금과 문장 비교로 3단계 원칙을 화면이 지키게 한다.
        return L09_ACTIVITY
    if n == 10:
        # 10차시는 익명 자가 점검이다. 개인 리포트는 학생 화면에만 남는다.
        return L10_ACTIVITY
    if n == 11:
        # 11차시는 문제를 좁히는 캔버스와 절차 카드로 프로젝트를 세운다.
        return L11_ACTIVITY
    # 12차시는 발표 카드, 서로에게 남기는 배운 점, 첫 시간과의 성찰 비교다.
    return L12_ACTIVITY


def _unused_form_12():
    return A.form([
        {"label": "완성한 결과물", "ph": ""},
        {"label": "AI가 한 일 / 우리가 한 일", "ph": ""},
        {"label": "지킨 우리 반 약속 조항", "ph": ""},
        {"label": "12차시 성찰문", "hint": "첫 시간과 지금, 생각이 어떻게 달라졌나요", "ph": ""},
    ])


def intro_js(art, line, hint):
    """입장 화면에 깔 소개 그림. 활동 구역 안에 넣어야 공통 골격이 갈라지지 않는다."""
    body = art + u'<p><b>%s</b><br>%s</p>' % (line, hint)
    return u"\n\n  function activityIntro() {\n    return %s;\n  }\n" % A.js(body)


def render_html(lesson, data):
    mod = data["modules"][lesson["module"] - 1]
    accent = mod["color"]
    w = lesson["webapp"]
    activity = activity_for(lesson, data) + WART.ICON_JS + intro_js(
        ART.lesson_art(lesson["no"]),
        "%d차시 · %s" % (lesson["no"], w["name"]),
        "%s 방 코드가 없으면 혼자 체험해 보기로 눌러 봐요." % w["purpose"])
    html = TEMPLATE
    for key, value in [
        ("__ACCENT__", accent),
        ("__ACCENT_SOFT__", SOFT.get(accent, "#f3f4f6")),
        ("__APP_NAME__", lesson["webapp"]["name"]),
        ("__SUBTITLE__", "%d차시 · %s" % (lesson["no"], lesson["shortTitle"])),
        ("__SLUG__", lesson["webapp"]["slug"]),
        ("__LESSON_ID__", lesson["id"]),
        ("__SHEET_ENDPOINT__", SHEET_ENDPOINT),
        ("__COPYRIGHT__", data["program"]["copyrightLine"]),
        ("__ACTIVITY__", activity),
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
    a("## 13개 앱이 함께 갖춘 기능")
    a("")
    a("- **발표 모드** : 교사 화면의 `결과 크게 띄우기` 를 누르면 학급 화면용 큰 글씨로 결과만 보여 준다")
    a("- **자동 임시 저장** : 쓰던 내용을 이 기기에 8초마다 저장한다. 인터넷이 끊겨도 사라지지 않는다")
    a("- **진행 막대** : 활동이 몇 단계 중 어디까지 왔는지 상단에 표시한다")
    a("- **개인 되돌아보기** : 학생 화면에서만 보이는 요약을 준다. 교사 화면에는 학급 집계만 간다")
    a("- **교사 화면 낱낱이 보기** : 표를 접었다 펼 수 있고, 모둠 수와 마지막 제출 시각을 함께 보여 준다")
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
    # 백업 시트 ID 는 공개 자료에 싣지 않는다. 학급 기록이 들어 있는 시트다.
    a("시트 : 선생님이 만든 백업 시트의 ID 를 여기에 넣는다.")
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
    var h = '<div class="card"><h2>내 번호</h2>' +
      '<p class="muted">사전 설문과 사후 설문을 이어 보는 데만 씁니다. ' +
      '앱이 자동으로 만들어 두었어요. <b>외우지 않아도 되고 고치지 않아도 됩니다.</b></p>' +
      '<input id="s-code" inputmode="numeric" maxlength="4" placeholder="자동">' +
      '<p class="muted" id="s-code-msg" style="margin-top:6px"></p>' +
      '<div id="s-link" style="margin-top:10px"></div></div>';
    h += '<div class="card"><h2>언제 하는 설문인가요</h2>' +
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
    h += '<div class="card"><h2>내 응답 요약</h2><div id="myrep">' +
      '<p class="muted">문항에 답하면 여기에 나타나요.</p></div></div>';
    h += '<div class="safe">솔직하게 답해 주세요. 누가 무엇을 골랐는지는 아무에게도 보이지 않아요.</div>';
    return h;
  }

  /* 1번 문항은 역채점한다. 값이 낮을수록 바람직한 응답이기 때문이다. */
  function myScore(obj) {
    var sum = 0, n = 0;
    for (var i = 0; i < ITEMS.length; i++) {
      var v = obj[i];
      if (v === undefined) { continue; }
      var sc = Number(v) + 1;
      if (i === 0) { sc = 6 - sc; }
      sum += sc;
      n++;
    }
    return { avg: n ? sum / n : 0, n: n };
  }

  function paintRep(saved) {
    if (!$("myrep")) { return; }
    var now = myScore(pick);
    if (!now.n) {
      $("myrep").innerHTML = '<p class="muted">문항에 답하면 여기에 나타나요.</p>';
      return;
    }
    var h = '<p class="big">' + now.avg.toFixed(1) + ' / 5.0</p>' +
      '<p class="muted">답한 문항 ' + now.n + ' / ' + ITEMS.length +
      ' · 높을수록 스스로 판단하며 쓰고 있다는 뜻이에요.</p>' +
      barHtml(Math.round(now.avg * 20), 100);
    if (saved && saved.pick && saved.when === "사전" && pick.when === "1") {
      var before = myScore(saved.pick);
      if (before.n) {
        var diff = (now.avg - before.avg).toFixed(1);
        h += '<p style="margin-top:12px">사전 ' + before.avg.toFixed(1) + ' 에서 사후 ' +
          now.avg.toFixed(1) + ' 로 ' + (Number(diff) >= 0 ? "+" : "") + diff + '</p>';
        h += '<p class="muted">이 비교는 이 기기에 남아 있던 내 사전 응답과 견준 거예요. 선생님께는 학급 평균만 갑니다.</p>';
      }
    }
    $("myrep").innerHTML = h;
  }

  var pick = {};

  var prior = null;

  function activityInit(saved) {
    prior = saved;
    if (saved && saved.pick) { pick = saved.pick; }
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      btns[i].onclick = function () {
        pick[this.getAttribute("data-i")] = this.getAttribute("data-v");
        paint();
      };
    }
    if ($("s-code")) {
      var pre = me.code || "";
      if (!pre) {
        try { pre = localStorage.getItem("wise_student_code") || ""; } catch (e) { pre = ""; }
      }
      if (pre) { $("s-code").value = pre; }
      $("s-code").oninput = paintCode;
    }
    wiseNote("사전인지 사후인지 먼저 골라 주세요.");
    if (saved && saved.opens) {
      for (var k = 0; k < OPENS.length; k++) {
        if ($("o" + k) && saved.opens[k]) { $("o" + k).value = saved.opens[k]; }
      }
    }
    paint();
  }

  function paintCode() {
    if (!$("s-code") || !$("s-code-msg")) { return; }
    var raw = $("s-code").value || "";
    var got = "";
    for (var i = 0; i < raw.length && got.length < 4; i++) {
      if (raw.charAt(i) >= "0" && raw.charAt(i) <= "9") { got += raw.charAt(i); }
    }
    if (got.length === 4) {
      $("s-code-msg").innerHTML = '<span class="ok">내 번호는 ' + got +
        ' 이에요. 그대로 두면 됩니다.</span>';
    } else {
      $("s-code-msg").innerHTML = '<span class="warn">번호가 비었어요. ' +
        '아래 단추를 누르면 새로 만들어 줍니다. 번호가 없어도 학급 평균에는 들어가요.</span>';
    }
  }

  /* 열두 주 뒤에 번호를 외우고 있는 아이는 거의 없다.
     그래서 사후를 고르면 같은 방에서 '같은 별명'으로 낸 사전 응답을 찾아 번호를 이어 준다.
     아이는 늘 쓰던 별명만 그대로 쓰면 된다. 못 찾으면 선생님 화면의 명단으로 해결한다. */
  var linkTried = false;

  function sameNick(a, b) {
    return String(a || "").replace(/[ 	]/g, "").toLowerCase() ===
           String(b || "").replace(/[ 	]/g, "").toLowerCase();
  }

  function linkPrior() {
    if (linkTried || me.solo || !me.room || me.room === "solo") { return; }
    linkTried = true;
    var box = $("s-link");
    if (box) { box.innerHTML = '<span class="muted">열두 주 전 기록을 찾는 중이에요...</span>'; }
    dbGet(me.room + "/entries").then(function (data) {
      var found = null;
      for (var k in data || {}) {
        var r = data[k] || {};
        var p = r.payload || {};
        if (p.when === "사전" && sameNick(r.nick, me.nick) && p.code) { found = r; }
      }
      if (!box) { return; }
      if (found) {
        if ($("s-code")) { $("s-code").value = found.payload.code; }
        paintCode();
        box.innerHTML = '<span class="ok">열두 주 전에 <b>' + esc(found.nick) +
          '</b> 이름으로 낸 사전 설문을 찾았어요. 번호를 그대로 이어 붙였습니다.</span>';
      } else {
        box.innerHTML = '<span class="muted">이 방에서 같은 별명으로 낸 사전 설문을 찾지 못했어요. ' +
          '괜찮아요. 그대로 답하면 됩니다. 이어 보기가 필요하면 선생님께 말씀드리세요.</span>';
      }
    })["catch"](function () {
      if (box) { box.innerHTML = ""; }
    });
  }

  function paint() {
    paintCode();
    if (pick.when === "1") { linkPrior(); }
    var btns = document.querySelectorAll("#activity .pick");
    for (var i = 0; i < btns.length; i++) {
      var k = btns[i].getAttribute("data-i");
      var v = btns[i].getAttribute("data-v");
      btns[i].className = "chip pick" + (pick[k] === v ? " on" : "");
    }
    var done = 0;
    for (var q = 0; q < ITEMS.length; q++) { if (pick[q] !== undefined) { done++; } }
    wiseStep(Math.min(2, Math.floor(done * 3 / ITEMS.length)), 3);
    paintRep(prior);
  }

  function activityAutofill() {
    pick.when = "0";
    for (var i = 0; i < ITEMS.length; i++) { pick[i] = String(i %% 5); }
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
    var code = "";
    if ($("s-code")) {
      var raw = $("s-code").value || "";
      for (var c = 0; c < raw.length && code.length < 4; c++) {
        if (raw.charAt(c) >= "0" && raw.charAt(c) <= "9") { code += raw.charAt(c); }
      }
    }
    if (code) {
      try { localStorage.setItem("wise_student_code", code); } catch (e) {}
    }
    return { when: pick.when === "1" ? "사후" : "사전", code: code, pick: pick, opens: opens };
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
    h += "</table></div>";

    /* 이어보기 명단. 아이가 번호를 잊고 별명도 바꿔 버렸을 때 선생님이 쓰는 마지막 안전망이다.
       별명과 번호만 있고 응답 내용은 없다. 사전 설문 뒤에 한 번 인쇄해 두면 된다. */
    var roll = [];
    for (var r = 0; r < list.length; r++) {
      var pr = list[r].payload || {};
      if (pr.when !== "사전") { continue; }
      roll.push({ nick: list[r].nick, code: pr.code || "" });
    }
    if (roll.length) {
      h += '<h3 style="margin-top:22px">이어보기 명단 (사전 ' + roll.length + '명)</h3>';
      h += '<p class="muted">별명과 번호만 있습니다. 답한 내용은 들어 있지 않아요. ' +
        '사전 설문을 마친 뒤 한 번 인쇄해 두면, 열두 주 뒤에 번호를 잊은 학생을 이어 줄 수 있습니다.</p>';
      h += '<div class="scroll"><table><tr><th>별명</th><th>번호</th></tr>';
      for (var q2 = 0; q2 < roll.length; q2++) {
        h += "<tr><td>" + esc(roll[q2].nick) + "</td><td>" + esc(roll[q2].code) + "</td></tr>";
      }
      h += "</table></div>";
    }
    return h;
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
        ("__LESSON_ID__", "L01"),
        ("__SHEET_ENDPOINT__", SHEET_ENDPOINT),
        ("__COPYRIGHT__", data["program"]["copyrightLine"]),
        ("__ACTIVITY__", survey_activity(data) + WART.ICON_JS + intro_js(
            ART.flow_art(),
            "공통 · AI적정활용 자기인식 설문",
            "여덟 문항에 답하면 내 점수를 요약해 줘요. 사전과 사후에 같은 문항으로 물어요.")),
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
    prompt = ["# 공통 웹앱 제작 프롬프트 : AI적정활용 자기인식 설문", "",
              "아래 글을 그대로 붙여 넣으면 같은 앱을 다시 만들 수 있다.", "",
              "```",
              "초등 5·6학년 학급에서 쓸 사전·사후 설문 웹앱을 단일 HTML 파일로 만들어 줘.",
              "외부 CDN을 참조하지 말고 CSS와 JS를 전부 인라인해. Google Sites 소스 코드 삽입에 쓸 거야.",
              "",
              "화면 구성",
              "- 사전(1차시 전)인지 사후(12차시 뒤)인지 먼저 고르게 한다.",
              "- 5점 척도 8문항. 문항은 아래 목록을 그대로 쓴다.",
              "- 자유응답 칸을 둔다.",
              "- 답할 때마다 내 평균 점수를 요약해 보여 준다. 1번 문항은 역채점한다.",
              "- 같은 기기에 사전 응답이 남아 있으면 사후 점수와 견주어 보여 준다.",
              "",
              "저장",
              "- 방 코드 6자리, 비밀번호 4자리, 닉네임으로 입장한다. 실명은 받지 않는다.",
              "- Firebase 실시간 DB에 먼저 쓰고 같은 기록을 Google Sheets에 백업한다.",
              "- 교사 화면에는 문항별 사전 평균, 사후 평균, 변화량만 보여 준다. 개인 응답은 보여 주지 않는다.",
              "",
              "문항"]
    for it in s["items"]:
        prompt.append("%d. %s" % (it["no"], it["text"]))
    prompt += ["```", "", "---", "", data["program"]["copyrightLine"]]
    write(os.path.join(base, "PROMPT.md"), "\n".join(prompt) + "\n")

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
