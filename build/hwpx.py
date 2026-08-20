# -*- coding: utf-8 -*-
"""HWPX 제자리 수정 도구.

한글이 설치되어 있지 않으므로 원본을 복사해 고치는 방식만 쓴다.
빈 상태에서 새로 조립하면 한글이 보안 경고를 띄운다. (CLAUDE.md 3-1절)
"""
import io
import os
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile

import tasks as T

HP = "http://www.hancom.co.kr/hwpml/2011/paragraph"
HS = "http://www.hancom.co.kr/hwpml/2011/section"
P = "{%s}" % HP

NAMESPACES = {
    "ha": "http://www.hancom.co.kr/hwpml/2011/app",
    "hp": HP,
    "hp10": "http://www.hancom.co.kr/hwpml/2016/paragraph",
    "hs": HS,
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
    "hhs": "http://www.hancom.co.kr/hwpml/2011/history",
    "hm": "http://www.hancom.co.kr/hwpml/2011/master-page",
    "hpf": "http://www.hancom.co.kr/schema/2011/hpf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "opf": "http://www.idpf.org/2007/opf/",
    "ooxmlchart": "http://www.hancom.co.kr/hwpml/2016/ooxmlchart",
    "hwpunitchar": "http://www.hancom.co.kr/hwpml/2016/HwpUnitChar",
    "epub": "http://www.idpf.org/2007/ops",
    "config": "http://www.hancom.co.kr/hwpml/2011/config",
}

DECL = "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>\n"

BASE = os.path.join(T.ROOT, "assets", "base_지도안.hwpx")

HEADER_PARAGRAPHS = 10   # 표지 문단 수
PARAGRAPHS_PER_LESSON = 4


def register():
    for prefix, uri in NAMESPACES.items():
        ET.register_namespace(prefix, uri)


def paragraph_text(p):
    return "".join(t.text or "" for t in p.iter(P + "t"))


def strip_linesegarray(el):
    """글자가 겹치지 않도록 줄 배치 캐시를 지운다. 한글이 다시 계산한다."""
    removed = 0
    for parent in el.iter():
        for child in list(parent):
            if child.tag == P + "linesegarray":
                parent.remove(child)
                removed += 1
    return removed


def replace_text(el, mapping):
    """hp:t 노드의 텍스트를 바꾼다. 정확히 같은 것 먼저, 그다음 부분 치환."""
    changed = 0
    for t in el.iter(P + "t"):
        if not t.text:
            continue
        original = t.text
        if original in mapping:
            t.text = mapping[original]
        else:
            new = original
            for old, rep in mapping.items():
                if old and old in new:
                    new = new.replace(old, rep)
            t.text = new
        if t.text != original:
            changed += 1
    return changed


def set_para_text(par, value):
    """문단의 첫 hp:t 에 값을 넣고 나머지는 비운다."""
    nodes = list(par.iter(P + "t"))
    if not nodes:
        return False
    nodes[0].text = value
    for n in nodes[1:]:
        n.text = ""
    return True


def clone_para(template, value, para_pr=None):
    """문단을 복제해 글을 갈아 넣는다. 표 안팎 모두에서 쓴다."""
    import copy as _copy
    par = _copy.deepcopy(template)
    strip_linesegarray(par)
    set_para_text(par, value)
    if para_pr is not None:
        par.set("paraPrIDRef", str(para_pr))
    return par


def cell_of(tbl, col, row):
    """(열, 행) 주소로 셀을 찾는다. 병합된 셀은 시작 주소로 찾는다."""
    for tr in tbl.findall(P + "tr"):
        for tc in tr.findall(P + "tc"):
            addr = tc.find(P + "cellAddr")
            if addr is None:
                continue
            if int(addr.get("colAddr")) == col and int(addr.get("rowAddr")) == row:
                return tc
    return None


def fill_cell(tc, lines):
    """셀 안의 문단을 lines 로 다시 채운다.

    lines 는 (paraPrIDRef, 글) 쌍이거나 문자열이다.
    셀 안에서만 문단을 복제하므로 셀 주소가 어긋나지 않는다.
    """
    if tc is None:
        return 0
    sub = tc.find(P + "subList")
    if sub is None:
        return 0
    paras = sub.findall(P + "p")
    if not paras:
        return 0
    template = paras[0]
    for extra in paras[1:]:
        sub.remove(extra)

    norm = []
    for item in lines:
        if isinstance(item, tuple):
            norm.append(item)
        else:
            norm.append((None, item))
    if not norm:
        norm = [(None, "")]

    first_pr, first_text = norm[0]
    set_para_text(template, first_text)
    strip_linesegarray(template)
    if first_pr is not None:
        template.set("paraPrIDRef", str(first_pr))
    for pr, text in norm[1:]:
        sub.append(clone_para(template, text, pr))
    return len(norm)


def load_section(path=BASE):
    register()
    with zipfile.ZipFile(path) as z:
        xml = z.read("Contents/section0.xml").decode("utf-8")
    return ET.fromstring(xml)


def slice_lesson(root, lesson_no, keep_cover=True):
    """표지 + 해당 차시 문단만 남긴다."""
    kids = list(root)
    start = HEADER_PARAGRAPHS + (lesson_no - 1) * PARAGRAPHS_PER_LESSON
    end = start + PARAGRAPHS_PER_LESSON
    if end > len(kids):
        raise ValueError("차시 %d 문단 범위가 원본을 벗어난다" % lesson_no)

    keep = (kids[:HEADER_PARAGRAPHS] if keep_cover else []) + kids[start:end]
    keep_ids = {id(k) for k in keep}
    for k in kids:
        if id(k) not in keep_ids:
            root.remove(k)
    return root


def serialize(root):
    body = ET.tostring(root, encoding="unicode")
    return DECL + body


def write_hwpx(out_path, section_xml, prv_text=None, base=BASE):
    """원본의 모든 항목을 그대로 옮기고 section0.xml 만 갈아끼운다."""
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    with zipfile.ZipFile(base) as src:
        infos = src.infolist()
        payload = {i.filename: src.read(i.filename) for i in infos}

    payload["Contents/section0.xml"] = section_xml.encode("utf-8")
    if prv_text is not None:
        payload["Preview/PrvText.txt"] = prv_text.encode("utf-8")[:4096]

    tmp = out_path + ".tmp"
    with zipfile.ZipFile(tmp, "w") as dst:
        # mimetype 은 반드시 첫 항목이고 무압축이어야 한다
        mime = zipfile.ZipInfo("mimetype")
        mime.compress_type = zipfile.ZIP_STORED
        dst.writestr(mime, payload["mimetype"])
        for i in infos:
            if i.filename == "mimetype":
                continue
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = i.external_attr
            dst.writestr(zi, payload[i.filename])

    if os.path.exists(out_path):
        os.remove(out_path)
    shutil.move(tmp, out_path)
    return out_path
