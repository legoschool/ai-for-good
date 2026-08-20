# -*- coding: utf-8 -*-
"""참고자료 모음 페이지를 만든다.

교사가 "이 수업의 근거가 어디에서 왔나"를 한 쪽에서 보게 한다.

  자료 카드 (미리보기 그림 + 소개 + 여는 링크 + 쓰이는 차시)
  · 차시별로 어떤 자료가 어디에 들어가 있는지 표

미리보기 그림은 `node build/make_refshots.js` 가 찍어 둔 것을 쓴다.
없으면 글자 카드로 나온다. 그림이 없어도 페이지는 완성된다.

사용법 : py -3 build/make_refs.py
"""
import io
import json
import os
import sys

import tasks as T

T.setup_console()


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def shot_index(site):
    path = os.path.join(site, "assets", "refshots", "index.json")
    if not os.path.exists(path):
        return {}
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


PAGE = u"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>참고자료 모음 · %(program)s</title>
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <a class="brand" href="index.html">WISE</a>
  <nav>
    <a href="browse.html">둘러보기</a>
    <a href="guide/index.html">웹앱 사용 안내</a>
    <a href="apps.html">웹앱 모음</a>
    <a href="refs.html" class="now">참고자료</a>
  </nav>
</header>

<main class="wrap">
<article class="page">

<h1>참고자료 모음</h1>
<p class="lead">이 수업이 어디에서 나왔는지, 무엇을 더 보면 되는지 한자리에 모았습니다.
각 자료가 <b>몇 차시에 어떻게 쓰이는지</b>도 함께 적었습니다.</p>

<section class="card">
  <h2>먼저 읽을 것</h2>
  <p>자료는 세 갈래입니다. <b>바탕</b>은 이 수업의 뿌리가 된 곳이고,
  <b>수업 자료</b>는 차시에서 실제로 쓰는 것이며, <b>기준</b>은 판단이 갈릴 때 근거로 삼는 문서입니다.</p>
  <p class="muted">링크는 자주 바뀝니다. 수업 하루 전에 한 번 열어 봅니다.</p>
  <div class="note"><b>미리보기 그림에 대하여</b><br>
  각 누리집의 첫 화면을 갈무리한 것입니다. 저작권은 해당 기관에 있으며,
  수업 자료를 찾아가도록 돕는 <b>교육 목적</b>으로만 싣습니다.
  그림마다 출처를 적었고, 누르면 원래 누리집으로 갑니다.
  자료를 쓸 때에는 기관 이름과 주소를 함께 밝힙니다.</div>
</section>

%(groups)s

<section class="card">
  <h2>차시별로 어디에 들어 있나</h2>
  <div class="scroll">
  <table class="reftable">
    <tr><th style="width:78px">차시</th><th style="width:150px">주제</th>
        <th>쓰는 자료</th><th style="width:230px">수업 어디에서</th></tr>
    %(rows)s
  </table>
  </div>
  <p class="muted">차시 페이지와 웹앱 사용 안내 페이지에도 같은 자료가 그 차시 것만 골라 실려 있습니다.</p>
</section>

<p class="navrow">
  <a href="guide/index.html">← 웹앱 사용 안내</a>
  <a href="index.html">홈으로 →</a>
</p>

</article>
</main>
<footer class="foot">%(copyright)s</footer>
</body>
</html>
"""


def card_html(item, shots):
    """자료 카드 하나. 미리보기 그림이 있으면 함께 보여 준다."""
    key = item.get("key", "")
    shot = shots.get(key)
    pic = ('<figure class="refpic"><a href="%s" target="_blank" rel="noopener">'
           '<img loading="lazy" src="assets/refshots/%s" alt="%s 첫 화면"></a>'
           '<figcaption>출처 : %s 누리집 화면 갈무리</figcaption></figure>'
           % (esc(item["url"]), esc(shot), esc(item["title"]),
              esc(item.get("org", "해당 기관")))) if shot else ""
    used = ""
    if item.get("lessons"):
        chips = "".join('<a class="lchip" href="lesson/%s.html">%s</a>'
                        % (esc(l), esc(l.replace("L", "") + "차시").lstrip("0"))
                        for l in item["lessons"])
        used = '<p class="usedin"><b>쓰이는 차시</b> %s</p>' % chips
    return (u'<article class="refcard">%s<div class="refbody">'
            u'<p class="reforg">%s</p>'
            u'<h3><a href="%s" target="_blank" rel="noopener">%s</a></h3>'
            u'<p>%s</p>'
            u'<p class="muted">%s</p>%s'
            u'<p class="refurl">%s</p>'
            u'</div></article>'
            % (pic, esc(item.get("org", "")), esc(item["url"]), esc(item["title"]),
               esc(item.get("intro", "")), esc(item.get("use", "")), used,
               esc(item["url"])))


def build(data, site):
    shots = shot_index(site)
    groups = data.get("refGroups", [])
    lessons = {l["id"]: l for l in data["lessons"]}

    gh = []
    for g in groups:
        cards = "".join(card_html(it, shots) for it in g.get("items", []))
        gh.append(u'<section class="card"><h2>%s</h2><p class="muted">%s</p>'
                  u'<div class="refgrid">%s</div></section>'
                  % (esc(g["name"]), esc(g.get("note", "")), cards))

    rows = []
    for l in data["lessons"]:
        mine = [r for r in data.get("references", []) if r.get("lesson") == l["id"]]
        if mine:
            names = "<br>".join(
                '<a href="%s" target="_blank" rel="noopener">%s</a> <span class="muted">%s</span>'
                % (esc(r["url"]), esc(r["title"]), esc(r.get("source", "")))
                for r in mine)
            where = "<br>".join(esc(r.get("note", "")) for r in mine)
        else:
            names = '<span class="muted">아직 고르지 않았습니다</span>'
            where = esc(l.get("refHint", ""))
        rows.append(u"<tr><td><b>%d차시</b></td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (l["no"], esc(l["shortTitle"]), names, where))

    html = PAGE % {
        "program": esc(data["program"]["name"]),
        "groups": "".join(gh),
        "rows": "".join(rows),
        "copyright": esc(data["program"]["copyrightLine"]),
    }
    path = os.path.join(site, "refs.html")
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(html)
    return path


def main():
    data = T.load_lessons()
    site = os.path.join(T.ROOT, "out", "site")
    path = build(data, site)
    print("참고자료 모음을 만들었다 : %s" % os.path.relpath(path, T.ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
