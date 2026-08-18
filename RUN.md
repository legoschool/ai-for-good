# RUN.md — 루프 돌리는 법

**이 파일 하나만 보면 된다.**

---

## 준비 (한 번만)

```bash
py -3 build/validate_data.py     # OK 가 나오면 준비 끝
py -3 build/next_task.py         # 다음 작업 확인
```

Python 3.12 (`python-pptx`, `openpyxl`, `lxml`) 와 Node.js 가 필요하다.
없으면 아래로 깐다.

```bash
winget install --id Python.Python.3.12 -e --scope user
winget install --id OpenJS.NodeJS.LTS -e
py -3 -m pip install python-pptx openpyxl lxml
```

---

## 매 세션 시작할 때

`prompts/P0_오케스트레이터.md` 의 코드 블록을 첫 메시지로 붙여 넣는다.
Claude 가 3줄로 상태를 보고하면 승인한다.

---

## 루프 한 바퀴

```
┌─ ① py -3 build/next_task.py              다음 작업과 읽을 파일 목록
│  ② py -3 build/update_state.py <작업> 진행   시작을 표시
│  ③ 계획 3~6줄 쓰고 만든다                해당 차시 데이터만 읽는다
│  ④ 체크리스트를 한 항목씩 실제로 확인
│  ⑤ 자동 검증 명령 실행
│  ⑥ 실패하면 원인 한 줄 진단 후 수리 (최대 3회)
│     3회 초과 → update_state.py <작업> 막힘 "사유" → 멈추고 보고
└─ ⑦ py -3 build/update_state.py <작업> 완료 "비고"
```

**핵심은 ⑥이다.** 3회 안에 통과하지 못하면 멈춘다.
요구사항을 낮추거나 체크리스트를 고쳐서 통과시키지 않는다.

---

## 올리기

산출물을 고쳤으면 반드시 이것까지 돌린다. 로컬에만 있으면 선생님이 못 본다.

```bash
py -3 build/publish.py "무엇을 고쳤는지"
```

검증 → 커밋 → 올리기 → 사이트 재빌드 대기 → 실제 접속 확인 → 드라이브 사본까지 한 번에 한다.
검증이 실패하면 올리지 않는다.

지금 올라간 것이 최신인지만 보려면 :

```bash
py -3 build/publish.py --check
```

---

## 다시 만들기

산출물을 직접 고치지 않는다. `data/lessons.json` 을 고치고 다시 만든다.

```bash
py -3 build/validate_data.py            # 먼저 통과시킨다

py -3 build/make_lesson_hwpx.py all     # 지도안 12편
py -3 build/make_worksheet_hwpx.py all  # 활동지 12종
py -3 build/make_ppt.py all             # PPT 12세트
py -3 build/make_webapp.py all          # 웹앱 12개 + 공통 설문
py -3 build/make_docs.py all            # 진도표 · 카드 교구 · 해설서
py -3 build/make_site.py                # 통합 웹사이트

py -3 build/verify_all.py               # 80개 검사 한 번에
```

`make_site.py` 는 산출물을 `out/site/files/` 와 `out/site/webapp/` 으로 복사한다.
**다른 것을 다시 만들었으면 사이트도 다시 만든다.**

---

## 명령 모음

```bash
# 현황
py -3 build/next_task.py --status     # 한 줄 요약
py -3 build/next_task.py              # 다음 작업 1개
py -3 build/next_task.py --all        # 전체 (○ 착수 가능, × 선행 대기)

# 상태 변경
py -3 build/update_state.py "L03/지도안" 진행
py -3 build/update_state.py "L03/지도안" 완료 "표 12행 유지 확인"
py -3 build/update_state.py "L03/웹앱 구현" 막힘 "방 코드 복사 3회 실패"

# 사람이 결정한 것 기록
py -3 build/update_state.py --decision "웹앱 백엔드" "Firebase + Sheets 백업" "spec/07"

# 개발용
py -3 build/inspect_hwpx.py           # 원본 HWPX 구조 보기
py -3 build/preview_page.py index.html out/preview.html
```

---

## 사이트 열어 보기

```bash
py -3 -m http.server 8765
```

`http://localhost:8765/out/site/index.html` 로 연다.
그냥 `out/site/index.html` 을 더블클릭해도 열린다.

---

## 배포 전에 할 일

1. `spec/07_웹앱_공통사양.md` 4-3절의 Apps Script 를 백업 시트에 붙이고 웹 앱으로 배포한다.
2. 배포 URL 을 `build/make_webapp.py` 의 `SHEET_ENDPOINT` 에 넣고 `make_webapp.py all` 을 다시 돌린다.
3. Firebase 콘솔에서 `spec/07` 3-5절의 보안 규칙을 넣는다.
4. `py -3 build/verify_all.py` 로 80개 검사를 통과시킨다.
5. `out/site/` 를 통째로 정적 호스팅에 올린다.

---

## 막혔을 때

```bash
py -3 build/next_task.py
# → 막힌 작업이 있으면 새 작업을 내주지 않는다. 사람이 결정해야 한다.
```

`STATE.md` 의 막힘 기록에 시도한 것과 필요한 결정이 적혀 있다.
결정이 내려지면 결정 기록에 남기고 상태를 `대기` 로 되돌린다.

---

2026년 티처스랩 5기 교사연구회 A.N.D (Analog aNd Digital)
