# -*- coding: utf-8 -*-
"""학생이 읽는 문장의 수준을 검사한다.

이 프로그램의 성취기준은 5·6학년군이다.
다만 3·4학년이 읽어도 막히지 않도록 문장과 낱말을 낮춘다.

두 가지를 나누어 본다.
  눈으로 읽는 글  앱 화면, 활동지 항목, 웹앱 화면 이름   40자 이내
  말로 하는 문장  학습 문제, 교사 발문, 예상 답변        64자 이내
말로 하는 문장은 교사가 소리 내어 읽으므로 길이 기준을 느슨하게 둔다.
낱말 기준은 둘 다 똑같이 적용한다.

사용법 : py -3 build/check_reading.py
"""
import io
import os
import re
import sys

import tasks as T

T.setup_console()

MAX_READ = 40
MAX_SPOKEN = 64
MAX_COMMA = 2

# 이 차시가 가르치는 말이다. 앱 안에서 뜻을 풀어 주면 써도 된다.
TAUGHT = {
    "데이터": [1, 3, 11], "라벨": [1, 11], "학습 데이터": [1],
    "환각": [2], "할루시네이션": [2], "출처": [2, 8, 12], "교차 검증": [2], "검증": [2],
    "편향": [3], "개인정보": [4, 8], "보조": [5], "대행": [5],
    "신호등": [6, 11], "표기": [8, 12], "디지털 웰빙": [10], "성찰": [12],
    "주체성": [5, 7], "모델": [1, 11, 12],
}

# 반드시 바꿔야 할 말. 3·4학년 교육과정 어디에도 나오지 않는다.
HARD = {
    "창제": "만듦", "반포": "널리 알림", "연혁": "지나온 일", "개교": "문을 엶",
    "발췌": "옮겨 온 글", "대조": "견주어 보기", "판정": "가려내기",
    "정합성": "들어맞음", "적합성": "알맞은지", "구성요소": "이루는 것",
    "형평성": "고르게 함", "포용성": "함께 감", "투명성": "밝히기",
    "최적화": "가장 좋게 만들기", "메타인지": "내 생각을 살피는 힘",
    "리터러시": "읽고 쓰는 힘", "준수": "지킴", "도출": "끌어냄",
    "수립": "세움", "상호작용": "주고받기", "가시화": "눈에 보이게 함",
    "문항": "문제", "산출물": "만든 것", "정확도": "맞힌 정도",
}

# 학년에 따라 살펴볼 말. 막지는 않고 어디에 있는지만 알려 준다.
# 괄호 안은 그 말이 교육과정에 처음 나오는 곳이다.
WATCH = {
    "근거": "4학년 국어 주장과 근거",
    "역량": "교사용 말. 학생 화면에는 쓰지 않는다",
    "맥락": "교사용 말. 학생 화면에는 쓰지 않는다",
    "윤리": "교사용 말. 학생 화면에는 쓰지 않는다",
    "적정": "교사용 말. 학생 화면에는 쓰지 않는다",
}

# 이미 교육과정에 있어 그대로 써도 되는 말
# 분류 : 2학년 수학 분류하기
# 모델 : 1·11·12차시가 가르치는 말
# 예측 : 3학년 과학

BR = re.compile(r"<br[ /]*>", re.I)
TAG = re.compile(r"<[^>]*>")
ENT = re.compile(r"&[a-zA-Z]+;")
DECOR = re.compile(r"[☆★△◎·\-\[\]()]")
KOREAN = re.compile(r"[\"']([^\"']*[가-힣][^\"']*)[\"']")
COMMENT = re.compile(r"^[ ]*(/\*|\*|//)")

ISSUES = []


def strip_markup(text):
    """HTML 태그는 학생이 읽는 글자가 아니다. 걷어내고 센다."""
    t = BR.sub("\n", str(text))
    t = TAG.sub(" ", t)
    t = ENT.sub(" ", t)
    return re.sub(r"[ 	]{2,}", " ", t).strip()


def sentences(text):
    if not text:
        return []
    body = strip_markup(text).replace("\\n", "\n")
    parts = re.split(r"(?<=[.?!])[ ]+|\n", body)
    return [p.strip() for p in parts if p.strip()]


def check(text, where, no=None, spoken=False):
    limit = MAX_SPOKEN if spoken else MAX_READ
    kind = "길이(말)" if spoken else "길이(글)"
    for s in sentences(text):
        plain = DECOR.sub("", s).strip()
        if not plain:
            continue
        if len(plain) > limit:
            ISSUES.append((kind, where, "%d자 : %s" % (len(plain), plain[:50])))
        if plain.count(",") > MAX_COMMA:
            ISSUES.append(("쉼표", where, "쉼표 %d개 : %s" % (plain.count(","), plain[:44])))
        for word, better in HARD.items():
            if word in plain and no not in TAUGHT.get(word, []):
                ISSUES.append(("고칠말", where, "%s -> %s : %s" % (word, better, plain[:36])))
        for word, note in WATCH.items():
            if word in plain and no not in TAUGHT.get(word, []):
                ISSUES.append(("살필말", where, "%s (%s) : %s" % (word, note, plain[:30])))


def gather_lessons(data):
    for l in data["lessons"]:
        no, tag = l["no"], "L%02d" % l["no"]
        check(l["problem"], tag + " 학습문제", no, spoken=True)
        for st in ("intro", "develop", "close"):
            for b in l["plan"][st]["blocks"]:
                for t in b.get("turns", []):
                    check(t["q"], tag + " 발문", no, spoken=True)
                    for a in t.get("a", []):
                        check(a, tag + " 예상답변", no, spoken=True)
        for sec in l["worksheet"]["sections"]:
            check(sec, tag + " 활동지", no)
        for sc in l["webapp"]["screens"]:
            check(sc, tag + " 웹앱 화면", no)
        for stp in l["webapp"].get("steps", []):
            check(stp["title"], tag + " 웹앱 단계", no)
            check(stp["ask"], tag + " 웹앱 발문", no, spoken=True)
            check(stp["expect"], tag + " 웹앱 예상답변", no, spoken=True)


def gather_app(path, tag, no):
    """앱 소스에서 학생 화면에 나오는 한글 문자열만 뽑는다."""
    if not os.path.exists(path):
        return
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            if COMMENT.match(line):
                continue
            for m in KOREAN.finditer(line):
                s = strip_markup(m.group(1))
                if len(s) < 6 or "px" in s[:8] or "var(" in s:
                    continue
                check(s, tag, no)


def main():
    data = T.load_lessons()
    gather_lessons(data)
    gather_app(os.path.join(T.ROOT, "build", "webapp_l01.py"), "L01 앱", 1)
    gather_app(os.path.join(T.ROOT, "build", "webapp_l02.py"), "L02 앱", 2)
    gather_app(os.path.join(T.ROOT, "build", "webapp_activities.py"), "공통 앱", None)

    kinds = {}
    for k, where, msg in ISSUES:
        kinds.setdefault(k, []).append((where, msg))

    print("=" * 68)
    print(" 학생이 읽는 문장 수준 검사")
    print(" 눈으로 읽는 글 %d자 · 말로 하는 문장 %d자 · 쉼표 %d개 · 어려운 말 금지"
          % (MAX_READ, MAX_SPOKEN, MAX_COMMA))
    print("=" * 68)

    order = ["길이(글)", "길이(말)", "쉼표", "고칠말", "살필말"]
    shown = 0
    for k in order:
        rows = kinds.get(k, [])
        seen, uniq = set(), []
        for where, msg in rows:
            key = (where, msg[:34])
            if key in seen:
                continue
            seen.add(key)
            uniq.append((where, msg))
        print("")
        print("[%s] %d건" % (k, len(uniq)))
        if not uniq:
            print("  없음")
            continue
        for where, msg in uniq:
            print("  %-20s %s" % (where, msg))
        shown += len(uniq)

    print("")
    print("=" * 68)
    if shown == 0:
        print(" OK  학생이 읽는 문장이 모두 기준을 지킨다")
    else:
        print(" 걸린 곳 %d건. 이 검사는 통과를 막지 않는다. 고칠 곳을 알려 줄 뿐이다." % shown)
    return 0


if __name__ == "__main__":
    sys.exit(main())
