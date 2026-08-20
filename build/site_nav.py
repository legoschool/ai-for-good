# -*- coding: utf-8 -*-
"""사이트 머리띠와 바닥글. 한 곳에서만 만든다.

머리띠를 페이지마다 따로 적으면 목록이 갈라지고, 안쪽 폭(.wrap)이 빠져
글자가 화면 맨 왼쪽에 붙는다. 참고자료와 사용 안내가 그랬다.
새 페이지를 만들 때는 반드시 여기 top_bar() 와 foot_bar() 를 쓴다.
"""

NAV = [
    ("index.html", "홈"),
    ("browse.html", "둘러보기"),
    ("module/M1.html", "발견"),
    ("module/M2.html", "판단"),
    ("module/M3.html", "실천"),
    ("skills.html", "인간중심 사고"),
    ("apps.html", "12차시 웹앱"),
    ("guide/index.html", "사용 안내"),
    ("refs.html", "참고자료"),
    ("survey.html", "자기인식 진단"),
    ("admin.html", "관리자"),
    ("about.html", "소개"),
]


def nav_links(up="", current=""):
    """머리띠 안의 링크 묶음. up 은 위로 올라가는 만큼의 '../' 이다."""
    return "".join(
        '<a href="%s%s"%s>%s</a>'
        % (up, href, ' aria-current="page"' if href == current else "", label)
        for href, label in NAV)


def top_bar(up="", current=""):
    """사이트 공통 머리띠. 안쪽 폭(.wrap)이 있어야 본문과 왼쪽 끝이 맞는다."""
    return (u'<header class="top"><div class="wrap">'
            u'<a class="brand" href="%sindex.html">WISE <em>AI적정활용</em></a>'
            u'<nav class="nav">%s</nav>'
            u'</div></header>' % (up, nav_links(up, current)))


def foot_bar(copyright_line):
    """사이트 공통 바닥글."""
    return u'<footer><div class="wrap"><p>%s</p></div></footer>' % copyright_line
