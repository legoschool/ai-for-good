# -*- coding: utf-8 -*-
"""차시 수업용 PPTX 를 만든다. 발표자 노트에 교사 발문을 그대로 넣는다.

사용법 : py -3 build/make_ppt.py 3
"""
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Emu, Inches, Pt

import tasks as T

T.setup_console()

FONT = "맑은 고딕"
W, H = Inches(13.333), Inches(7.5)

INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x6B, 0x72, 0x80)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
BAND = RGBColor(0xF3, 0xF4, 0xF6)


def hex_to_rgb(s):
    s = s.lstrip("#")
    return RGBColor(int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def rect(slide, x, y, w, h, fill):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def text(slide, x, y, w, h, runs, size=24, bold=False, color=INK,
         align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.25):
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    if isinstance(runs, str):
        runs = [runs]
    for i, line in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        r = p.add_run()
        r.text = line
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.name = FONT
        r.font.color.rgb = color
    return box


def note(slide, lines):
    tf = slide.notes_slide.notes_text_frame
    tf.text = lines[0] if lines else ""
    for line in lines[1:]:
        tf.add_paragraph().text = line


def turn_lines(block):
    out = ["◎ " + block["heading"]]
    for t in block.get("turns", []):
        out.append("- " + t["q"])
        for a in t.get("a", []):
            out.append("  · " + a)
    return out


def build(lesson, data):
    prs = Presentation()
    prs.slide_width, prs.slide_height = W, H
    mod = data["modules"][lesson["module"] - 1]
    accent = hex_to_rgb(mod["color"])
    M = Inches(0.9)
    CW = W - M * 2

    # 1. 표지
    s = blank(prs)
    rect(s, 0, 0, W, Inches(0.28), accent)
    text(s, M, Inches(2.0), CW, Inches(0.6),
         "%d차시  ·  모듈%d %s" % (lesson["no"], mod["no"], mod["name"]),
         size=22, color=accent, bold=True)
    text(s, M, Inches(2.7), CW, Inches(1.6), lesson["title"], size=48, bold=True)
    text(s, M, Inches(4.5), CW, Inches(1.0), lesson["problem"], size=22, color=MUTED)
    text(s, M, H - Inches(1.0), CW, Inches(0.5),
         data["program"]["copyrightLine"], size=12, color=MUTED)
    note(s, ["오늘 배울 것을 한 문장으로 소개한다.", lesson["problem"]])

    # 2. 학습 문제
    s = blank(prs)
    rect(s, 0, Inches(2.4), W, Inches(2.7), BAND)
    text(s, M, Inches(1.5), CW, Inches(0.6), "학습 문제", size=22, color=accent, bold=True)
    text(s, M, Inches(2.9), CW, Inches(1.8), lesson["problem"], size=34, bold=True)
    note(s, ["학습 문제를 함께 소리 내어 읽는다."])

    # 3. 동기 유발
    intro = lesson["plan"]["intro"]
    for b in intro["blocks"]:
        if b["heading"] == "학습 문제 확인":
            continue
        s = blank(prs)
        rect(s, 0, 0, Inches(0.22), H, accent)
        text(s, M, Inches(0.8), CW, Inches(0.6), "도입 · " + b["heading"],
             size=20, color=accent, bold=True)
        qs = [t["q"] for t in b.get("turns", [])]
        text(s, M, Inches(1.9), CW, Inches(4.2), qs, size=28, spacing=1.6)
        note(s, turn_lines(b) + ["", "준비물"] + intro["materials"])

    # 4. 전개 활동
    for b in lesson["plan"]["develop"]["blocks"]:
        s = blank(prs)
        rect(s, 0, 0, Inches(0.22), H, accent)
        text(s, M, Inches(0.8), CW, Inches(0.6), b["heading"], size=26, color=accent, bold=True)
        qs = [t["q"] for t in b.get("turns", [])]
        text(s, M, Inches(2.0), CW, Inches(4.2), qs, size=26, spacing=1.7)
        note(s, turn_lines(b) + ["", "준비물·유의점"] + lesson["plan"]["develop"]["materials"])

    # 5. 웹앱 안내
    w = lesson["webapp"]
    s = blank(prs)
    rect(s, 0, 0, Inches(0.22), H, accent)
    text(s, M, Inches(0.8), CW, Inches(0.6), "오늘 쓰는 웹앱", size=20, color=accent, bold=True)
    text(s, M, Inches(1.6), CW, Inches(0.9), w["name"], size=38, bold=True)
    text(s, M, Inches(2.7), CW, Inches(1.0), w["purpose"], size=20, color=MUTED)
    text(s, M, Inches(4.0), CW, Inches(2.2),
         ["· " + x for x in w["screens"]], size=20, spacing=1.5)
    note(s, ["방 코드를 만들어 화면에 크게 띄운다.",
             "혼자 체험 경로도 함께 안내한다.",
             "교사 화면 : " + w.get("teacherView", "")])

    # 5-1. 웹앱 단계별 안내. steps 가 있는 차시만 만든다.
    for st in w.get("steps", []):
        s = blank(prs)
        rect(s, 0, 0, Inches(0.22), H, accent)
        rect(s, W - Inches(2.3), Inches(0.7), Inches(1.4), Inches(0.55), accent)
        text(s, W - Inches(2.3), Inches(0.72), Inches(1.4), Inches(0.5),
             "%d분" % st["minutes"], size=20, bold=True, color=PAPER, align=PP_ALIGN.CENTER)
        text(s, M, Inches(0.8), CW - Inches(2.4), Inches(0.5),
             "%d단계" % st["no"], size=18, color=accent, bold=True)
        text(s, M, Inches(1.5), CW, Inches(0.9), st["title"], size=36, bold=True)
        text(s, M, Inches(2.7), CW, Inches(1.6), st["what"], size=20, color=MUTED, spacing=1.5)
        text(s, M, Inches(4.5), CW, Inches(1.2), st["ask"], size=26, bold=True)
        note(s, ["%d단계 · %d분" % (st["no"], st["minutes"]),
                 st["what"], "", "발문 : " + st["ask"], "예상 답변 : " + st["expect"]])

    # 6. AI 미사용 대안
    s = blank(prs)
    rect(s, 0, Inches(2.3), W, Inches(2.6), BAND)
    text(s, M, Inches(1.4), CW, Inches(0.6), "기기가 없어도 함께합니다",
         size=20, color=accent, bold=True)
    text(s, M, Inches(2.8), CW, Inches(1.8), lesson["alternative"], size=24)
    note(s, ["1인 1기기가 아니어도 모두 참여하게 한다."] + lesson["cautions"])

    # 7. 정리
    close = lesson["plan"]["close"]
    for b in close["blocks"]:
        s = blank(prs)
        rect(s, 0, 0, Inches(0.22), H, accent)
        text(s, M, Inches(0.8), CW, Inches(0.6), "정리 · " + b["heading"],
             size=20, color=accent, bold=True)
        qs = [t["q"] for t in b.get("turns", [])]
        text(s, M, Inches(2.0), CW, Inches(3.6), qs, size=28, spacing=1.6)
        note(s, turn_lines(b) + ["", "준비물"] + close["materials"])

    # 8. 오늘의 배움
    s = blank(prs)
    rect(s, 0, 0, Inches(0.22), H, accent)
    text(s, M, Inches(1.0), CW, Inches(0.6), "오늘의 배움", size=20, color=accent, bold=True)
    know = [f["knowledge"] for f in lesson["humanSkills"]["focus"]]
    text(s, M, Inches(2.0), CW, Inches(3.2), ["· " + k for k in know], size=24, spacing=1.6)
    text(s, M, H - Inches(1.0), CW, Inches(0.5),
         data["program"]["copyrightLine"], size=12, color=MUTED)
    note(s, ["오늘 배운 것을 학생이 한 문장으로 말하게 한다."])

    return prs


def make(no):
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == no][0]
    prs = build(lesson, data)
    out_dir = os.path.join(T.ROOT, "out", "ppt")
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    out = os.path.join(out_dir, "WISE_%s_수업.pptx" % lesson["id"])
    prs.save(out)
    print("만들었다 : %s  (슬라이드 %d장)" % (out, len(prs.slides.__iter__.__self__._sldIdLst)))
    return out


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/make_ppt.py <차시번호|all>")
        return 1
    if sys.argv[1] == "all":
        for n in range(1, 13):
            make(n)
        return 0
    make(int(sys.argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
