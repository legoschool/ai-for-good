# -*- coding: utf-8 -*-
"""차시별 웹앱 사용 안내 페이지를 만든다.

교사가 이 한 쪽만 보면 수업을 굴릴 수 있게 한다.

  무엇을 하는 앱인가 · 무엇을 배우는가 · 체험하는 법 세 걸음
  · 화면 캡처 갤러리 · 수업 흐름과 발문 · 관련 영상과 기사 · 내려받기

캡처는 `node build/make_shots.js` 가 먼저 만들어 둔 것을 쓴다.
사용법 : py -3 build/make_guide.py
"""
import io
import json
import os
import sys

import tasks as T
from site_nav import top_bar, foot_bar

T.setup_console()

SHOTS = os.path.join("assets", "shots")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shots_index(site):
    path = os.path.join(site, "assets", "shots", "index.json")
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


PAGE = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s · 웹앱 사용 안내</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
%(top)s

<main class="wrap">
<article class="page">

<p class="crumb">%(module)s · %(no)d차시</p>
<h1>%(title)s</h1>
<p class="lead">%(purpose)s</p>

<section class="card">
  <h2>이 앱으로 무엇을 하나</h2>
  <p>%(problem)s</p>
  <div class="pillrow">%(skills)s</div>
</section>

<section class="card">
  <h2>배우는 것</h2>
  <ul>%(learn)s</ul>
</section>

<section class="card">
  <h2>체험하는 법 (세 걸음)</h2>
  <ol class="steps3">
    <li><b>혼자 먼저 해 본다.</b> 앱을 열고 <b>둘러보기</b>를 누른다. 별명을 적지 않아도 바로 들어간다.
      저장되지 않으니 마음껏 눌러 본다.
      <a class="btn" href="../webapp/%(lid)s/index.html" target="_blank" rel="noopener">웹앱 열기</a></li>
    <li><b>수업 직전에 방을 만든다.</b> 앱에서 <b>선생님 화면</b>을 누르고 비밀번호 네 자리를 정한 뒤
      <b>새 방 만들기</b>를 누른다. 여섯 자리 방 번호가 나온다. 칠판에 적는다.</li>
    <li><b>학생이 들어온다.</b> 같은 주소를 열어 방 번호와 별명만 넣는다.
      내 번호 네 자리는 앱이 자동으로 채워 둔다. 제출하면 선생님 화면에 바로 모인다.</li>
  </ol>
  <p class="muted">기기가 모자라면 모둠에 한 대로 함께 하고, 없으면 %(alt)s</p>
</section>

<section class="card">
  <h2>화면 미리 보기</h2>
  <p class="muted">실제 앱 화면입니다. 눌러서 크게 볼 수 있습니다.</p>
  <div class="shots">%(shots)s</div>
</section>

<section class="card">
  <h2>수업 흐름과 발문</h2>
  %(flow)s
</section>

<section class="card">
  <h2>함께 보면 좋은 자료</h2>
  %(refs)s
  <div class="embed-slot">
    <p class="muted"><b>영상이나 카드뉴스를 화면 안에 넣으려면</b>
      <code>data/lessons.json</code> 의 <code>references</code> 항목에
      <code>"embed": "https://www.youtube.com/embed/영상아이디"</code> 처럼 적고 다시 만듭니다.
      캔바는 보기 주소 끝에 <code>?embed</code> 를 붙입니다.
      임베드를 넣어도 여는 링크는 그대로 둡니다. 학교망에서 막히는 곳이 있습니다.</p>
  </div>
</section>

<section class="card">
  <h2>내려받기</h2>
  <div class="dl">
    <a href="../files/WISE_%(lid)s_지도안.hwpx">지도안 한글</a>
    <a href="../files/WISE_%(lid)s_활동지.hwpx">활동지 한글</a>
    <a href="../files/WISE_%(lid)s_수업.pptx">수업 PPT</a>
    <a href="../print/%(lid)s_지도안.html">지도안 인쇄용</a>
    <a href="../print/%(lid)s_활동지.html">활동지 인쇄용</a>
    <a href="../deck/%(lid)s.html">수업 슬라이드</a>
  </div>
</section>

<p class="navrow">
  <a href="../guide/index.html">← 사용 안내 목록</a>
  <a href="../lesson/%(lid)s.html">%(no)d차시 자세히 보기 →</a>
</p>

</article>
</main>
%(foot)s
</body>
</html>
"""

INDEX = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>웹앱 사용 안내</title>
<link rel="stylesheet" href="../assets/style.css">
</head>
<body>
%(top)s
<main class="wrap">
<article class="page">
<h1>웹앱 사용 안내</h1>
<p class="lead">앱을 처음 여는 선생님이 이 쪽만 보고 수업을 끝까지 운영할 수 있도록 적었습니다.
준비, 시작, 수업 중, 마무리, 막혔을 때를 차례로 담았습니다.</p>

<section class="card">
  <h2>한눈에 : 수업 한 시간의 흐름</h2>
  <div class="scroll"><table>
    <tr><th style="width:120px">언제</th><th style="width:150px">누가</th><th>무엇을 한다</th></tr>
    <tr><td><b>하루 전</b></td><td>선생님</td>
      <td>앱을 열어 <b>둘러보기</b>로 끝까지 해 본다. 기기 수와 인터넷을 확인한다.</td></tr>
    <tr><td><b>수업 시작 3분</b></td><td>선생님</td>
      <td><b>선생님 화면 → 새 방 만들기</b>. 여섯 자리 방 번호를 칠판에 적는다.</td></tr>
    <tr><td><b>이어서 2분</b></td><td>학생</td>
      <td>같은 주소를 열어 방 번호와 별명을 넣고 <b>입장하기</b>.</td></tr>
    <tr><td><b>수업 중</b></td><td>학생</td>
      <td>화면에 나오는 순서대로 활동한다. 다 하면 <b>제출하기</b>.</td></tr>
    <tr><td><b>정리 5분</b></td><td>선생님</td>
      <td><b>결과 크게 띄우기</b>로 학급 결과를 함께 본다.</td></tr>
    <tr><td><b>수업 뒤</b></td><td>선생님</td>
      <td><b>방 잠그기</b>. 필요하면 <b>CSV 내려받기</b>.</td></tr>
  </table></div>
  <div class="note"><b>기기가 없어도 수업은 됩니다.</b> 앱은 도구이지 수업 그 자체가 아닙니다.
  차시마다 AI를 쓰지 않는 대안 활동을 지도안에 함께 적어 두었습니다.</div>
</section>

<section class="card">
  <h2>1. 수업 하루 전 (5분)</h2>
  <ol class="steps3">
    <li><b>앱을 열어 혼자 해 봅니다.</b> 차시 카드에서 그 차시 앱을 열고 <b>둘러보기</b>를 누릅니다.
      별명을 적지 않아도 바로 들어갑니다. 이때 넣은 것은 저장되지 않습니다.</li>
    <li><b>끝까지 눌러 봅니다.</b> 학생이 어디에서 멈출지 미리 알 수 있습니다.
      한 차시 앱은 대개 5분에서 8분이면 한 바퀴 돕니다.</li>
    <li><b>기기를 셉니다.</b> 1인 1기기가 아니어도 됩니다. 모둠에 한 대로도 운영합니다.</li>
    <li><b>주소를 미리 열어 둡니다.</b> 학교 태블릿은 즐겨찾기에 넣어 두면 수업 시간이 줄어듭니다.</li>
  </ol>
</section>

<section class="card">
  <h2>2. 수업을 시작할 때 (3분)</h2>
  <ol class="steps3">
    <li>앱 첫 화면에서 <b>선생님 화면</b>을 누릅니다.</li>
    <li><b>선생님 비밀번호 네 자리</b>를 정해서 넣습니다. 이 화면을 다시 열 때만 씁니다.
      학생에게는 알려 주지 않습니다. 잊어버리면 방을 새로 만들면 됩니다.</li>
    <li><b>새 방 만들기</b>를 누릅니다. <b>여섯 자리 방 번호</b>가 나옵니다.</li>
    <li>방 번호를 <b>칠판에 크게</b> 적습니다. <b>복사</b> 단추로 주소를 함께 나눠 줘도 됩니다.</li>
    <li>학생에게 알려 줄 것은 <b>주소와 방 번호 두 가지뿐</b>입니다.</li>
  </ol>
  <div class="note"><b>학생 화면에서 묻는 것</b>은 방 번호와 별명, 모둠(비워도 됨)입니다.
  이름, 학교, 학년, 반, 전화번호는 묻지 않습니다.
  <b>내 번호 네 자리는 앱이 자동으로 만들어</b> 채워 둡니다. 학생이 외울 필요가 없습니다.</div>
</section>

<section class="card">
  <h2>3. 수업 중 : 선생님 화면의 단추</h2>
  <div class="scroll"><table>
    <tr><th style="width:170px">단추</th><th>하는 일</th><th style="width:190px">언제 씁니까</th></tr>
    <tr><td><b>제출 현황 N명</b></td><td>지금까지 제출한 사람 수를 보여 준다</td>
      <td>활동 중에 진도를 볼 때</td></tr>
    <tr><td><b>새로고침</b></td><td>최신 제출을 다시 불러온다</td><td>숫자가 안 늘어 보일 때</td></tr>
    <tr><td><b>결과 크게 띄우기</b></td><td>학급 결과를 큰 화면용으로 띄운다</td>
      <td>정리 단계에서 함께 볼 때</td></tr>
    <tr><td><b>낱낱이 보기</b></td><td>누가 무엇을 냈는지 표로 본다</td>
      <td>개별 지도가 필요할 때만</td></tr>
    <tr><td><b>CSV 내려받기</b></td><td>제출 내용을 파일로 받는다</td><td>수업 뒤 기록으로 남길 때</td></tr>
    <tr><td><b>방 잠그기</b></td><td>더 이상 새 제출을 받지 않는다</td><td>수업이 끝났을 때</td></tr>
  </table></div>
  <p class="muted">선생님 화면은 다시 열 수 있습니다. <b>선생님 화면 → 기존 방 열기</b>에 방 번호를 넣으면 됩니다.</p>
</section>

<section class="card">
  <h2>4. 학생 화면은 이렇게 굴러갑니다</h2>
  <ol class="steps3">
    <li><b>들어가기</b>에서 방 번호와 별명을 넣고 <b>입장하기</b>를 누릅니다.</li>
    <li>활동이 <b>순서대로 열립니다.</b> 앞 단계를 마쳐야 다음이 열리는 차시가 있습니다.
      막힌 칸을 누르면 무엇을 먼저 해야 하는지 앱이 데려다 줍니다.</li>
    <li>쓴 내용은 <b>기기에 자동으로 저장</b>됩니다. 화면을 잘못 닫아도 다시 들어오면 이어서 합니다.</li>
    <li>다 하면 아래쪽 <b>제출하기</b>를 누릅니다. 빈 곳이 있으면 앱이 무엇이 남았는지 알려 줍니다.</li>
    <li>제출한 뒤에도 <b>고쳐서 다시 제출</b>할 수 있습니다.</li>
  </ol>
  <p class="muted">화면 맨 위 띠는 늘 보입니다. 홈, 둘러보기, 그 차시 페이지, 설문으로 갈 수 있고,
  <b>처음부터</b>를 누르면 이 기기에 저장된 내용을 지우고 다시 시작합니다.</p>
</section>

<section class="card">
  <h2>5. 사전·사후 설문 운영</h2>
  <p>같은 여덟 문항을 <b>1차시 전</b>과 <b>12차시 뒤</b>에 묻습니다. 열두 시간의 변화를 보는 자료입니다.</p>
  <ol class="steps3">
    <li><b>사전 설문 방을 하나 만들어</b> 학급 전체가 들어옵니다. 학생은 <b>사전</b>을 고르고 답합니다.</li>
    <li>사전을 마치면 선생님 화면 아래 <b>이어보기 명단</b>(별명과 번호)이 생깁니다.
      <b>한 번 인쇄해 두십시오.</b> 열두 주 뒤의 보험입니다.</li>
    <li>12차시 뒤에는 <b>같은 방 번호</b>를 다시 열어 학생이 <b>사후</b>를 고르고 답합니다.</li>
  </ol>
  <div class="note"><b>번호를 외우게 하지 않습니다.</b> 앱이 번호를 자동으로 만들고 기기에 기억합니다.
  기기가 바뀌어도 학생이 <b>사전 때 쓰던 별명</b>을 그대로 쓰면, 사후에서 앱이 그 기록을 찾아 저절로 이어 줍니다.
  둘 다 안 되면 인쇄해 둔 이어보기 명단에서 번호를 찾아 넣어 주면 됩니다.
  번호가 없어도 답은 학급 평균에 그대로 들어갑니다.</div>
</section>

<section class="card">
  <h2>6. 기기가 모자랄 때</h2>
  <div class="scroll"><table>
    <tr><th style="width:190px">상황</th><th>이렇게 합니다</th></tr>
    <tr><td>기기가 모둠당 한 대</td>
      <td>모둠에서 한 명이 조작하고 나머지가 함께 판단합니다. 별명은 모둠 이름으로 씁니다.</td></tr>
    <tr><td>교사 기기 한 대뿐</td>
      <td>화면을 크게 띄우고 함께 판단합니다. 학생 개인 기록은 활동지에 손으로 남깁니다.</td></tr>
    <tr><td>인터넷이 끊겼을 때</td>
      <td>활동은 그대로 돌아갑니다. 제출만 안 됩니다. 인쇄용 활동지로 대신합니다.</td></tr>
    <tr><td>학교망에서 막힐 때</td>
      <td>영상이나 외부 자료가 안 열리면 참고자료 쪽의 다른 자료로 바꿉니다.</td></tr>
  </table></div>
</section>

<section class="card">
  <h2>7. 막히면 여기를 봅니다</h2>
  <div class="scroll"><table>
    <tr><th style="width:230px">이런 일이 생기면</th><th>이렇게 합니다</th></tr>
    <tr><td>학생이 방 번호를 넣어도 안 들어가진다</td>
      <td>여섯 자리가 맞는지, 방을 잠그지 않았는지 봅니다. 잠갔으면 새 방을 만듭니다.</td></tr>
    <tr><td>제출했는데 선생님 화면에 안 보인다</td>
      <td><b>새로고침</b>을 누릅니다. 학생과 선생님이 같은 방 번호인지 확인합니다.</td></tr>
    <tr><td>학생 화면이 멈춘 것 같다</td>
      <td>같은 단추를 여러 번 누른 경우가 많습니다. 잠시 기다리면 이어집니다.</td></tr>
    <tr><td>기록을 지우고 다시 하고 싶다</td>
      <td>맨 위 띠의 <b>처음부터</b>를 누릅니다. 그 기기에 저장된 내용만 지워집니다.</td></tr>
    <tr><td>선생님 비밀번호를 잊었다</td>
      <td>새 방을 만들면 됩니다. 앞 방의 기록은 그대로 남아 있습니다.</td></tr>
    <tr><td>학생이 자기 별명을 잊었다</td>
      <td>아무 별명이나 다시 써도 활동에는 지장이 없습니다. 이어보기만 안 될 뿐입니다.</td></tr>
  </table></div>
</section>

<section class="card">
  <h2>8. 개인정보에 대한 약속</h2>
  <ul>
    <li>이름, 사진, 학교, 학년, 반, 전화번호를 <b>묻지 않습니다.</b></li>
    <li>저장하는 것은 <b>별명과 답</b>뿐입니다.</li>
    <li>설문 결과는 <b>학급 집계만</b> 보여 줍니다. 개인 응답은 관리자 화면에도 뜨지 않습니다.</li>
    <li>모인 자료는 수업 프로그램을 고치는 데만 쓰고 <b>학년도가 끝나면 지웁니다.</b></li>
  </ul>
</section>

<h2 style="margin:34px 0 6px">차시별 안내</h2>
<p class="muted" style="margin-bottom:14px">차시를 누르면 그 앱의 화면, 활동 순서, 발문, 자료가 나옵니다.</p>
<div class="grid3">%(cards)s</div>

</article>
</main>
%(foot)s
</body>
</html>
"""


def skills_of(lesson):
    out = []
    for s in lesson["humanSkills"]["focus"]:
        out.append('<span class="pill">%s</span>' % esc(s["name"]))
    for s in lesson["humanSkills"].get("support", []):
        out.append('<span class="pill ghost">%s</span>' % esc(s))
    return "".join(out)


def learn_of(lesson):
    out = []
    for s in lesson["humanSkills"]["focus"]:
        out.append("<li><b>%s</b> · %s</li>" % (esc(s["name"]), esc(s["process"])))
    for c in lesson.get("aiComponents", []):
        name = c if isinstance(c, str) else ("%s %s" % (c.get("mark", ""), c.get("name", "")))
        out.append("<li>AI적정활용 구성요소 · %s</li>" % esc(name))
    return "".join(out)


def flow_of(lesson):
    rows = []
    for key, label in [("intro", "도입"), ("develop", "전개"), ("close", "정리")]:
        part = lesson["plan"][key]
        for block in part["blocks"]:
            qs = []
            for turn in block["turns"]:
                if turn.get("q"):
                    qs.append("<li>%s</li>" % esc(turn["q"]))
            rows.append(
                '<div class="flowrow"><div class="flowhead">%s · %s분<br><b>%s</b></div>'
                '<ul class="flowq">%s</ul></div>'
                % (label, part["minutes"], esc(block["heading"]), "".join(qs)))
    return "".join(rows)


def refs_of(lesson, data):
    """그 차시 자료를 먼저 보여 주고 공통 자료를 뒤에 붙인다.
    embed 주소가 있으면 화면 안에 끼워 넣고, 여는 링크도 반드시 함께 둔다.
    학교망에서 임베드가 막혀도 링크로 열 수 있어야 하기 때문이다."""
    mine = [r for r in data.get("references", []) if r.get("lesson") == lesson["id"]]
    common = [r for r in data.get("references", []) if not r.get("lesson")]

    items = []
    for r in mine + common:
        title = esc(r.get("title", "자료"))
        url = esc(r.get("url", ""))
        src = esc(r.get("source", ""))
        note = esc(r.get("note", ""))
        kind = esc(r.get("kind", "자료"))
        embed = esc(r.get("embed", ""))
        box = '<li class="refitem"><span class="tagk">%s</span> ' % kind
        if url:
            box += '<a href="%s" target="_blank" rel="noopener"><b>%s</b></a>' % (url, title)
        else:
            box += "<b>%s</b>" % title
        if src:
            box += ' <span class="muted">%s</span>' % src
        box += "<p>%s</p>" % note
        if embed:
            box += ('<div class="embed"><iframe loading="lazy" src="%s" '
                    'allowfullscreen allow="fullscreen" title="%s"></iframe></div>'
                    '<p class="muted">화면에 안 보이면 학교망이 막은 것입니다. 위 제목을 눌러 새 창으로 엽니다.</p>'
                    % (embed, title))
        items.append(box + "</li>")

    hint = esc(lesson.get("refHint", ""))
    if not items:
        return '<p class="muted">아직 채우지 않았습니다. 권장 자료 : %s</p>' % hint
    return '<ul class="reflist">%s</ul>' % "".join(items)


def shots_of(lid, index):
    rows = []
    for s in index.get(lid, []):
        rows.append(
            '<figure><a href="../%s/%s" target="_blank" rel="noopener">'
            '<img loading="lazy" src="../%s/%s" alt="%s 화면"></a>'
            '<figcaption>%s</figcaption></figure>'
            % (SHOTS.replace("\\", "/"), esc(s["file"]), SHOTS.replace("\\", "/"),
               esc(s["file"]), esc(s["name"]), esc(s["name"])))
    if not rows:
        return '<p class="muted">캡처가 아직 없습니다. <code>node build/make_shots.js</code> 를 돌립니다.</p>'
    return "".join(rows)


def build(data, site):
    index = shots_index(site)
    out_dir = os.path.join(site, "guide")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    cards = []
    made = []
    for lesson in data["lessons"]:
        lid = lesson["id"]
        mod = data["modules"][lesson["module"] - 1]
        html = PAGE % {
            "title": esc(lesson["webapp"]["name"]),
            "lid": lid,
            "no": lesson["no"],
            "module": esc(mod["name"]),
            "purpose": esc(lesson["webapp"]["purpose"]),
            "problem": esc(lesson["problem"]),
            "skills": skills_of(lesson),
            "learn": learn_of(lesson),
            "alt": esc(lesson.get("alternative", "인쇄 자료로 대신합니다.")),
            "shots": shots_of(lid, index),
            "flow": flow_of(lesson),
            "refs": refs_of(lesson, data),
            "top": top_bar("../", "guide/index.html"),
            "foot": foot_bar(esc(data["program"]["copyrightLine"])),
        }
        path = os.path.join(out_dir, "%s.html" % lid)
        with io.open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(html)
        made.append(path)

        first = index.get(lid, [{}])[0].get("file", "")
        thumb = ('<img loading="lazy" src="../%s/%s" alt="">' % (SHOTS.replace("\\", "/"), esc(first))) if first else ""
        cards.append(
            '<a class="gcard" href="%s.html">%s'
            '<span class="gno">%d차시</span><b>%s</b>'
            '<small>%s</small></a>'
            % (lid, thumb, lesson["no"], esc(lesson["webapp"]["name"]),
               esc(lesson["shortTitle"])))

    idx = INDEX % {"cards": "".join(cards),
                   "top": top_bar("../", "guide/index.html"),
                   "foot": foot_bar(esc(data["program"]["copyrightLine"]))}
    ipath = os.path.join(out_dir, "index.html")
    with io.open(ipath, "w", encoding="utf-8", newline="\n") as f:
        f.write(idx)
    made.append(ipath)
    return made


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    made = build(data, site)
    print("웹앱 사용 안내를 만들었다 : %d쪽" % len(made))
    print("  %s" % os.path.relpath(made[-1], T.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
