# -*- coding: utf-8 -*-
"""HWPX 산출물 검증. 한글이 열 수 있는지, 내용이 lessons.json 과 맞는지 본다."""
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import hwpx
import tasks as T

T.setup_console()

P = hwpx.P
ERRORS = []


def err(m):
    ERRORS.append(m)


REQUIRED_ENTRIES = [
    "mimetype", "settings.xml", "version.xml",
    "Contents/section0.xml", "Contents/header.xml", "Contents/content.hpf",
    "META-INF/container.xml", "META-INF/manifest.xml",
]


def check_container(path):
    if not os.path.exists(path):
        err("파일이 없다 : %s" % path)
        return None
    if not zipfile.is_zipfile(path):
        err("zip 형식이 아니다")
        return None

    z = zipfile.ZipFile(path)
    infos = z.infolist()
    names = [i.filename for i in infos]

    if not infos or infos[0].filename != "mimetype":
        err("mimetype 이 zip 의 첫 항목이 아니다. 한글이 열지 못한다")
    elif infos[0].compress_type != zipfile.ZIP_STORED:
        err("mimetype 이 무압축(STORED)이 아니다. 한글이 열지 못한다")
    else:
        mt = z.read("mimetype").decode("utf-8").strip()
        if "hwp" not in mt:
            err("mimetype 내용이 이상하다 : %s" % mt)

    for need in REQUIRED_ENTRIES:
        if need not in names:
            err("필수 항목이 없다 : %s" % need)

    bad = z.testzip()
    if bad:
        err("깨진 항목이 있다 : %s" % bad)
    return z


def check_section(z):
    try:
        xml = z.read("Contents/section0.xml").decode("utf-8")
    except Exception as e:
        err("section0.xml 을 읽지 못했다 : %s" % e)
        return None, ""

    if not xml.lstrip().startswith("<?xml"):
        err("section0.xml 에 XML 선언이 없다")

    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        err("section0.xml 이 올바른 XML 이 아니다 : %s" % e)
        return None, xml

    if "linesegarray" in xml:
        err("linesegarray 가 남아 있다. 글자가 겹쳐 보인다")

    for entity in ["&nbsp;", "&amp;amp;"]:
        if entity in xml:
            err("잘못된 문자 참조가 있다 : %s" % entity)

    text = "\n".join(hwpx.paragraph_text(p) for p in root)
    return root, text


def check_lesson_content(path, root, text):
    m = re.search(r"WISE_L(\d\d)_", os.path.basename(path))
    if not m:
        return  # 지도안·활동지가 아닌 산출물(해설서 등)은 내용 검사를 건너뛴다

    no = int(m.group(1))
    data = T.load_lessons()
    lesson = [l for l in data["lessons"] if l["no"] == no][0]

    base = os.path.basename(path)
    kind = "활동지" if "_활동지" in base else "지도안"

    if lesson["problem"] not in text:
        err("학습 문제가 본문에 없다 : %s" % lesson["problem"][:30])
    if lesson["shortTitle"] not in text and lesson["title"] not in text:
        err("학습 주제가 본문에 없다 : %s" % lesson["shortTitle"])

    if kind == "지도안":
        for stage in ("도입", "전개", "정리"):
            if stage not in text:
                err("%s 단계가 본문에 없다" % stage)
        for skill in lesson["humanSkills"]["focus"]:
            if skill["name"] not in text:
                err("중점 휴먼스킬이 본문에 없다 : %s" % skill["name"])
        for mark in "☆★△":
            if mark not in text:
                err("준비물 부호 %s 가 본문에 없다" % mark)
    else:
        for sec in lesson["worksheet"]["sections"]:
            if sec not in text:
                err("활동지 항목이 없다 : %s" % sec)
        if "스스로 점검하기" not in text:
            err("자기점검 문항이 없다")
        if lesson["webapp"]["name"] not in text:
            err("웹앱 안내가 없다 : %s" % lesson["webapp"]["name"])
        if lesson["alternative"] not in text:
            err("AI 미사용 대안 활동이 없다")
        if "개인정보" not in text:
            err("개인정보 안내 문구가 없다")

    # 다른 차시 내용이 섞이지 않았는가
    for other in data["lessons"]:
        if other["no"] == no:
            continue
        if other["problem"] in text:
            err("다른 차시(%d) 학습 문제가 섞여 있다" % other["no"])

    # 옛 표기와 금지 표현
    if re.search(r"웹앱[123]", text):
        err("옛 모듈 묶음 표기(웹앱1·2·3)가 남아 있다")
    if "—" in text:
        err("em dash(—) 가 남아 있다")
    for old in ["허용·조건부·제한", "3수준"]:
        if old in text:
            err("옛 3단계 신호등 표현이 남아 있다 : %s" % old)


def main():
    if len(sys.argv) < 2:
        print("사용법 : py -3 build/validate_hwpx.py <경로.hwpx>")
        return 1

    path = sys.argv[1]
    if not os.path.isabs(path):
        path = os.path.join(T.ROOT, path)

    z = check_container(path)
    if z is None:
        print("NG  오류 %d건" % len(ERRORS))
        for e in ERRORS:
            print("  실패  %s" % e)
        return 1

    root, text = check_section(z)
    if root is not None:
        check_lesson_content(path, root, text)

    if ERRORS:
        for e in ERRORS:
            print("실패  %s" % e)
        print("")
        print("NG  오류 %d건" % len(ERRORS))
        return 1

    size = os.path.getsize(path)
    print("OK  %s" % os.path.basename(path))
    print("    %d바이트, 문단 %d개, 글자 %d자" % (size, len(list(root)), len(text)))
    print("    mimetype 무압축 선두, XML 파싱, linesegarray 제거, 내용 일치 확인")
    return 0


if __name__ == "__main__":
    sys.exit(main())
