# -*- coding: utf-8 -*-
"""사이트에 쓰는 그림. 전부 인라인 SVG 다.

외부 이미지 파일을 쓰지 않는다. 학교망에서 막히지 않고, 파일 하나로 옮겨도 그림이 따라간다.
선 굵기와 색은 site_css.py 의 팔레트를 따른다. 검정 테두리 3, 면은 단색이다.

  lesson_art(no)   차시 대표 그림 12종 (viewBox 0 0 320 180)
  hero_art()       홈 머리 그림
  flow_art()       생각 먼저 3단계 그림
  signal_art()     신호등 네 단계 그림
  icon(kind)       자료 종류 아이콘
"""

INK = "#111111"
WHITE = "#FFFFFF"
GREEN = "#00D45A"
BLUE = "#2B59E0"
PURPLE = "#7B4FE8"
SUN = "#FFE24B"
CREAM = "#F4EEE0"
RED = "#FF6B5A"


def _svg(inner, vb="0 0 320 180", cls="art"):
    return (u'<svg class="%s" viewBox="%s" role="img" aria-hidden="true" '
            u'preserveAspectRatio="xMidYMid slice">%s</svg>' % (cls, vb, inner))


def _kid(x, y, s, skin, cloth):
    """작은 사람. s 는 크기 배수다."""
    return (u'<g transform="translate(%d,%d) scale(%s)">'
            u'<rect x="-16" y="16" width="32" height="26" rx="12" fill="%s" stroke="%s" stroke-width="3"/>'
            u'<circle cx="0" cy="0" r="15" fill="%s" stroke="%s" stroke-width="3"/>'
            u'<circle cx="-5" cy="-2" r="2.4" fill="%s"/><circle cx="5" cy="-2" r="2.4" fill="%s"/>'
            u'<path d="M-5 6 q5 4 10 0" stroke="%s" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
            u'</g>' % (x, y, s, cloth, INK, skin, INK, INK, INK, INK))


def _card(x, y, w, h, fill, rot=0):
    return (u'<rect x="%d" y="%d" width="%d" height="%d" rx="6" fill="%s" stroke="%s" '
            u'stroke-width="3" transform="rotate(%d %d %d)"/>'
            % (x, y, w, h, fill, INK, rot, x + w // 2, y + h // 2))


def _bubble(x, y, w, h, fill):
    return (u'<g><rect x="%d" y="%d" width="%d" height="%d" rx="12" fill="%s" stroke="%s" stroke-width="3"/>'
            u'<path d="M%d %d l0 16 l16 -16z" fill="%s" stroke="%s" stroke-width="3" stroke-linejoin="round"/></g>'
            % (x, y, w, h, fill, INK, x + 18, y + h, fill, INK))


# ---------------------------------------------------------------- 차시 그림

def _l01():
    """카드 더미가 상자로 들어가 결과가 나온다."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(_card(18, 40, 44, 58, WHITE, -8))
    s.append(_card(34, 52, 44, 58, SUN, 4))
    s.append(u'<text x="56" y="88" font-size="20" font-weight="800" fill="%s">?</text>' % INK)
    s.append(u'<rect x="112" y="52" width="86" height="70" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (BLUE, INK))
    s.append(u'<path d="M126 96 h58 M126 82 h44 M126 68 h30" stroke="%s" stroke-width="5" '
             u'stroke-linecap="round"/>' % WHITE)
    s.append(u'<path d="M84 86 h22 M198 86 h20" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M100 78 l8 8 -8 8z M214 78 l8 8 -8 8z" fill="%s"/>' % INK)
    s.append(_card(230, 48, 62, 46, GREEN))
    s.append(u'<path d="M244 72 l10 11 20 -22" stroke="%s" stroke-width="6" fill="none" '
             u'stroke-linecap="round" stroke-linejoin="round"/>' % INK)
    s.append(_card(230, 104, 62, 40, WHITE))
    s.append(u'<path d="M244 118 l22 20 M266 118 l-22 20" stroke="%s" stroke-width="5" '
             u'stroke-linecap="round"/>' % RED)
    return _svg("".join(s))


def _l02():
    """같은 질문에 다른 답 두 개. 돋보기로 확인한다."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(_bubble(20, 24, 130, 52, WHITE))
    s.append(u'<path d="M36 44 h96 M36 58 h68" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    s.append(_bubble(20, 104, 130, 52, SUN))
    s.append(u'<path d="M36 124 h96 M36 138 h54" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    s.append(u'<text x="168" y="60" font-size="26" font-weight="900" fill="%s">A</text>' % BLUE)
    s.append(u'<text x="168" y="142" font-size="26" font-weight="900" fill="%s">B</text>' % PURPLE)
    s.append(u'<circle cx="248" cy="86" r="38" fill="none" stroke="%s" stroke-width="7"/>' % INK)
    s.append(u'<circle cx="248" cy="86" r="30" fill="%s" opacity=".35"/>' % GREEN)
    s.append(u'<path d="M276 116 l24 24" stroke="%s" stroke-width="10" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M234 86 l9 10 18 -20" stroke="%s" stroke-width="6" fill="none" '
             u'stroke-linecap="round" stroke-linejoin="round"/>' % INK)
    return _svg("".join(s))


def _l03():
    """한쪽으로 몰린 사람들. 데이터가 치우쳐 있다."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    xs = [(40, BLUE), (78, BLUE), (116, BLUE), (154, BLUE), (192, BLUE)]
    for x, c in xs:
        s.append(_kid(x, 62, "0.72", WHITE, c))
    s.append(_kid(258, 62, "0.72", WHITE, SUN))
    s.append(u'<rect x="24" y="118" width="184" height="18" rx="9" fill="%s" stroke="%s" stroke-width="3"/>'
             % (BLUE, INK))
    s.append(u'<rect x="238" y="118" width="40" height="18" rx="9" fill="%s" stroke="%s" stroke-width="3"/>'
             % (SUN, INK))
    s.append(u'<text x="24" y="158" font-size="15" font-weight="800" fill="%s">많이 배운 쪽</text>' % INK)
    s.append(u'<text x="226" y="158" font-size="15" font-weight="800" fill="%s">적게 배운 쪽</text>' % INK)
    return _svg("".join(s))


def _l04():
    """자물쇠와 카드 세 칸."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="26" y="70" width="72" height="60" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (SUN, INK))
    s.append(u'<path d="M44 70 v-14 a18 18 0 0 1 36 0 v14" fill="none" stroke="%s" stroke-width="7"/>' % INK)
    s.append(u'<circle cx="62" cy="98" r="9" fill="%s" stroke="%s" stroke-width="3"/>' % (WHITE, INK))
    labels = [(126, GREEN), (192, SUN), (258, RED)]
    for x, c in labels:
        s.append(u'<rect x="%d" y="52" width="52" height="80" rx="10" fill="%s" stroke="%s" '
                 u'stroke-width="3"/>' % (x, c, INK))
    s.append(u'<path d="M140 96 l10 10 18 -22" stroke="%s" stroke-width="6" fill="none" '
             u'stroke-linecap="round" stroke-linejoin="round"/>' % INK)
    s.append(u'<text x="206" y="102" font-size="26" font-weight="900" fill="%s">?</text>' % INK)
    s.append(u'<path d="M272 84 l24 24 M296 84 l-24 24" stroke="%s" stroke-width="6" '
             u'stroke-linecap="round"/>' % INK)
    return _svg("".join(s))


def _l05():
    """연필을 내가 쥐는가, 대신 쥐어 주는가."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="18" y="28" width="130" height="124" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    s.append(u'<path d="M36 62 h94 M36 82 h94 M36 102 h60" stroke="%s" stroke-width="5" '
             u'stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M96 132 l40 -40 14 14 -40 40 -18 4z" fill="%s" stroke="%s" stroke-width="3" '
             u'stroke-linejoin="round"/>' % (GREEN, INK))
    s.append(u'<text x="30" y="26" font-size="14" font-weight="800" fill="%s">보조</text>' % INK)

    s.append(u'<rect x="174" y="28" width="130" height="124" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    s.append(u'<rect x="192" y="52" width="94" height="70" rx="8" fill="%s" stroke="%s" stroke-width="3"/>'
             % (PURPLE, INK))
    s.append(u'<path d="M206 78 h66 M206 96 h48" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % WHITE)
    s.append(u'<text x="186" y="26" font-size="14" font-weight="800" fill="%s">대행</text>' % INK)
    s.append(u'<text x="238" y="146" font-size="13" font-weight="800" fill="%s">AI가 다 함</text>' % INK)
    return _svg("".join(s))


def _l06():
    """신호등 네 등."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="112" y="16" width="96" height="148" rx="18" fill="%s" stroke="%s" stroke-width="3"/>'
             % (INK, INK))
    colors = [GREEN, SUN, "#FF9F45", RED]
    for i, c in enumerate(colors):
        s.append(u'<circle cx="160" cy="%d" r="14" fill="%s" stroke="%s" stroke-width="3"/>'
                 % (42 + i * 34, c, WHITE))
    s.append(u'<path d="M84 42 h-46 M84 76 h-46 M84 110 h-46 M84 144 h-46" stroke="%s" '
             u'stroke-width="4" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M236 42 h46 M236 76 h46 M236 110 h46 M236 144 h46" stroke="%s" '
             u'stroke-width="4" stroke-linecap="round"/>' % INK)
    return _svg("".join(s))


def _l07():
    """약속 종이와 손들기."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="26" y="22" width="150" height="136" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    s.append(u'<text x="44" y="52" font-size="17" font-weight="900" fill="%s">우리 반 약속</text>' % INK)
    for i in range(4):
        y = 74 + i * 22
        s.append(u'<circle cx="48" cy="%d" r="6" fill="%s" stroke="%s" stroke-width="2.5"/>'
                 % (y - 4, GREEN, INK))
        s.append(u'<path d="M62 %d h96" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % (y - 4, INK))
    hands = [(212, 108, GREEN), (250, 96, BLUE), (288, 112, PURPLE)]
    for x, y, c in hands:
        s.append(u'<path d="M%d %d v-34 a8 8 0 0 1 16 0 v34z" fill="%s" stroke="%s" stroke-width="3" '
                 u'stroke-linejoin="round"/>' % (x, y, c, INK))
        s.append(u'<rect x="%d" y="%d" width="24" height="26" rx="8" fill="%s" stroke="%s" '
                 u'stroke-width="3"/>' % (x - 4, y - 2, c, INK))
    return _svg("".join(s))


def _l08():
    """게시판에 붙은 약속 카드."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="20" y="20" width="280" height="120" rx="10" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    cards = [(38, 38, GREEN, -4), (128, 44, SUN, 3), (216, 36, PURPLE, -2)]
    for x, y, c, r in cards:
        s.append(_card(x, y, 68, 78, c, r))
    s.append(u'<path d="M40 152 h240" stroke="%s" stroke-width="6" stroke-linecap="round"/>' % INK)
    s.append(u'<circle cx="72" cy="40" r="5" fill="%s" stroke="%s" stroke-width="2.5"/>' % (WHITE, INK))
    s.append(u'<circle cx="162" cy="46" r="5" fill="%s" stroke="%s" stroke-width="2.5"/>' % (WHITE, INK))
    s.append(u'<circle cx="250" cy="38" r="5" fill="%s" stroke="%s" stroke-width="2.5"/>' % (WHITE, INK))
    return _svg("".join(s))


def _l09():
    """내 글, 붙임쪽지, 다시 쓴 글."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<rect x="18" y="30" width="82" height="118" rx="8" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    s.append(u'<path d="M32 58 h54 M32 76 h54 M32 94 h38" stroke="%s" stroke-width="4.5" '
             u'stroke-linecap="round"/>' % INK)
    s.append(u'<text x="26" y="26" font-size="13" font-weight="800" fill="%s">1단계</text>' % INK)

    s.append(_card(118, 54, 76, 72, SUN, -5))
    s.append(u'<path d="M134 84 h44 M134 100 h30" stroke="%s" stroke-width="4.5" '
             u'stroke-linecap="round"/>' % INK)
    s.append(u'<text x="120" y="44" font-size="13" font-weight="800" fill="%s">2단계</text>' % INK)

    s.append(u'<rect x="212" y="30" width="88" height="118" rx="8" fill="%s" stroke="%s" stroke-width="3"/>'
             % (GREEN, INK))
    s.append(u'<path d="M228 58 h56 M228 76 h56 M228 94 h56 M228 112 h34" stroke="%s" '
             u'stroke-width="4.5" stroke-linecap="round"/>' % INK)
    s.append(u'<text x="220" y="26" font-size="13" font-weight="800" fill="%s">3단계</text>' % INK)
    s.append(u'<path d="M104 90 h8 M198 90 h8" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    return _svg("".join(s))


def _l10():
    """달과 화면 시간, 그리고 막대 리포트."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<circle cx="62" cy="60" r="30" fill="%s" stroke="%s" stroke-width="3"/>' % (SUN, INK))
    s.append(u'<circle cx="74" cy="52" r="24" fill="%s"/>' % CREAM)
    s.append(u'<rect x="30" y="106" width="70" height="46" rx="8" fill="%s" stroke="%s" stroke-width="3"/>'
             % (WHITE, INK))
    s.append(u'<path d="M46 130 h38" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    bars = [(150, 40, GREEN), (188, 70, BLUE), (226, 28, PURPLE), (264, 56, SUN)]
    for x, h, c in bars:
        s.append(u'<rect x="%d" y="%d" width="30" height="%d" rx="6" fill="%s" stroke="%s" '
                 u'stroke-width="3"/>' % (x, 140 - h, h, c, INK))
    s.append(u'<path d="M138 148 h164" stroke="%s" stroke-width="4" stroke-linecap="round"/>' % INK)
    s.append(u'<text x="138" y="40" font-size="14" font-weight="800" fill="%s">내 리포트</text>' % INK)
    return _svg("".join(s))


def _l11():
    """돋보기로 문제를 찾고 절차 카드를 세운다."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(u'<circle cx="72" cy="72" r="40" fill="%s" stroke="%s" stroke-width="7"/>' % (WHITE, INK))
    s.append(u'<path d="M100 100 l26 26" stroke="%s" stroke-width="10" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M60 74 q12 -18 24 0" stroke="%s" stroke-width="5" fill="none" '
             u'stroke-linecap="round"/>' % RED)
    s.append(u'<circle cx="72" cy="56" r="5" fill="%s"/>' % INK)
    steps = [(150, GREEN), (190, BLUE), (230, PURPLE), (270, SUN)]
    for i, (x, c) in enumerate(steps):
        s.append(u'<rect x="%d" y="%d" width="34" height="34" rx="8" fill="%s" stroke="%s" '
                 u'stroke-width="3"/>' % (x, 118 - i * 22, c, INK))
        s.append(u'<text x="%d" y="%d" font-size="15" font-weight="900" fill="%s">%d</text>'
                 % (x + 11, 141 - i * 22, INK, i + 1))
    return _svg("".join(s))


def _l12():
    """발표하는 아이와 자라난 생각."""
    s = [u'<rect width="320" height="180" fill="%s"/>' % CREAM]
    s.append(_kid(74, 86, "1.5", WHITE, GREEN))
    s.append(u'<rect x="98" y="70" width="14" height="34" rx="7" fill="%s" stroke="%s" stroke-width="3"/>'
             % (INK, INK))
    s.append(u'<path d="M105 104 v22" stroke="%s" stroke-width="4"/>' % INK)
    s.append(_bubble(150, 22, 150, 60, WHITE))
    s.append(u'<path d="M168 44 h110 M168 62 h72" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M164 152 l34 -30 30 22 44 -50" fill="none" stroke="%s" stroke-width="7" '
             u'stroke-linecap="round" stroke-linejoin="round"/>' % BLUE)
    s.append(u'<circle cx="272" cy="94" r="8" fill="%s" stroke="%s" stroke-width="3"/>' % (SUN, INK))
    return _svg("".join(s))


_LESSON = {1: _l01, 2: _l02, 3: _l03, 4: _l04, 5: _l05, 6: _l06,
           7: _l07, 8: _l08, 9: _l09, 10: _l10, 11: _l11, 12: _l12}


def lesson_art(no, cls="art"):
    """cls 를 kv-art 로 주면 keyvis 안에 꽉 차게 깔린다."""
    fn = _LESSON.get(no)
    out = fn() if fn else _svg(u'<rect width="320" height="180" fill="%s"/>' % CREAM)
    if cls != "art":
        out = out.replace('class="art"', 'class="%s"' % cls, 1)
    return out


# ---------------------------------------------------------------- 그 밖의 그림

def hero_art():
    """홈 머리 그림. 아이와 화면, 그리고 생각 풍선."""
    s = [u'<rect x="14" y="30" width="180" height="126" rx="14" fill="%s" stroke="%s" stroke-width="4"/>'
         % (WHITE, INK)]
    s.append(u'<rect x="34" y="52" width="140" height="18" rx="9" fill="%s"/>' % CREAM)
    s.append(u'<rect x="34" y="82" width="104" height="14" rx="7" fill="%s"/>' % CREAM)
    s.append(u'<rect x="34" y="108" width="126" height="14" rx="7" fill="%s"/>' % CREAM)
    s.append(u'<path d="M84 156 h40 v14 h-40z" fill="%s" stroke="%s" stroke-width="4"/>' % (CREAM, INK))
    s.append(_kid(246, 96, "1.7", WHITE, GREEN))
    s.append(u'<g>')
    s.append(u'<ellipse cx="250" cy="34" rx="52" ry="30" fill="%s" stroke="%s" stroke-width="4"/>'
             % (SUN, INK))
    s.append(u'<text x="250" y="42" font-size="24" font-weight="900" fill="%s" '
             u'text-anchor="middle">생각</text>' % INK)
    s.append(u'<circle cx="212" cy="66" r="8" fill="%s" stroke="%s" stroke-width="3"/>' % (SUN, INK))
    s.append(u'<circle cx="200" cy="80" r="5" fill="%s" stroke="%s" stroke-width="3"/>' % (SUN, INK))
    s.append(u'</g>')
    return _svg("".join(s), vb="0 0 320 180", cls="hero-art")


def flow_art():
    """생각 먼저 3단계."""
    boxes = [(10, GREEN, "내 생각 먼저"), (116, SUN, "AI 검토"), (222, BLUE, "내 말로 다시")]
    s = []
    for x, c, label in boxes:
        s.append(u'<rect x="%d" y="30" width="88" height="64" rx="12" fill="%s" stroke="%s" '
                 u'stroke-width="3"/>' % (x, c, INK))
        s.append(u'<text x="%d" y="112" font-size="14" font-weight="800" fill="%s" '
                 u'text-anchor="middle">%s</text>' % (x + 44, INK, label))
    s.append(u'<path d="M102 62 h10 M208 62 h10" stroke="%s" stroke-width="5" stroke-linecap="round"/>' % INK)
    s.append(u'<path d="M108 54 l10 8 -10 8z M214 54 l10 8 -10 8z" fill="%s"/>' % INK)
    return _svg("".join(s), vb="0 0 320 130", cls="art flow")


def signal_art(color, label):
    """신호등 한 등. 홈과 둘러보기에서 쓴다."""
    s = [u'<circle cx="40" cy="40" r="30" fill="%s" stroke="%s" stroke-width="4"/>' % (color, INK)]
    s.append(u'<circle cx="30" cy="30" r="8" fill="%s" opacity=".55"/>' % WHITE)
    return _svg("".join(s), vb="0 0 80 80", cls="art sig")


ICONS = {
    "지도안": u'<rect x="14" y="8" width="52" height="64" rx="8" fill="{w}" stroke="{i}" stroke-width="4"/>'
              u'<path d="M26 28 h28 M26 42 h28 M26 56 h18" stroke="{i}" stroke-width="4" stroke-linecap="round"/>',
    "활동지": u'<rect x="12" y="10" width="56" height="60" rx="8" fill="{y}" stroke="{i}" stroke-width="4"/>'
              u'<path d="M24 32 h20 M24 46 h32" stroke="{i}" stroke-width="4" stroke-linecap="round"/>'
              u'<path d="M46 26 l10 10 -14 14 -12 2 2 -12z" fill="{w}" stroke="{i}" stroke-width="3" '
              u'stroke-linejoin="round"/>',
    "PPT": u'<rect x="8" y="14" width="64" height="44" rx="6" fill="{b}" stroke="{i}" stroke-width="4"/>'
           u'<path d="M40 58 v10 M28 72 h24" stroke="{i}" stroke-width="4" stroke-linecap="round"/>'
           u'<path d="M22 44 l12 -14 10 10 12 -16" fill="none" stroke="{w}" stroke-width="4" '
           u'stroke-linecap="round" stroke-linejoin="round"/>',
    "웹앱": u'<rect x="10" y="10" width="60" height="60" rx="12" fill="{g}" stroke="{i}" stroke-width="4"/>'
            u'<circle cx="30" cy="34" r="6" fill="{i}"/><circle cx="50" cy="34" r="6" fill="{i}"/>'
            u'<path d="M28 52 q12 10 24 0" stroke="{i}" stroke-width="4" fill="none" stroke-linecap="round"/>',
}


def icon(kind):
    tpl = ICONS.get(kind)
    if not tpl:
        return ""
    inner = tpl.format(i=INK, w=WHITE, y=SUN, b=BLUE, g=GREEN)
    return _svg(inner, vb="0 0 80 80", cls="art icon")
