// 웹앱 스모크 테스트.
// 실제로 터졌던 결함 10건을 검사한다. (spec/09_웹앱_결함목록.md)
// 사용법 : node build/smoke_webapp.js out/webapp/L06

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.dirname(__dirname);
const errors = [];
const err = (m) => errors.push(m);

function main() {
  const target = process.argv[2];
  if (!target) {
    console.log("사용법 : node build/smoke_webapp.js <out/webapp/L06>");
    return 1;
  }
  const dir = path.isAbsolute(target) ? target : path.join(ROOT, target);
  const file = path.join(dir, "index.html");

  if (!fs.existsSync(file)) {
    console.log("실패  index.html 이 없다 : " + file);
    return 1;
  }
  const html = fs.readFileSync(file, "utf8");
  const lessons = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "lessons.json"), "utf8"));
  const id = path.basename(dir);
  const lesson = lessons.lessons.find((l) => l.id === id);

  // 1. 외부 참조가 없어야 한다 (학교망 차단·CSP)
  const ext = html.match(/(src|href)[ ]*=[ ]*["'](https?:)?[/][/][^"']+["']/gi) || [];
  if (ext.length) err("외부 리소스를 참조한다 : " + ext.slice(0, 3).join(", "));
  if (/<script[^>]+src=/i.test(html)) err("외부 스크립트 태그가 있다");
  if (/<link[^>]+stylesheet/i.test(html)) err("외부 스타일시트가 있다");

  // 2. Apps Script 가 파괴하는 역슬래시 이스케이프
  const scripts = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]);
  const js = scripts.join("\n");
  const badEscapes = js.match(/\/[^/\n]*\\[dsw][^/\n]*\/[gimsuy]*/g) || [];
  if (badEscapes.length) {
    err("정규식에 역슬래시 이스케이프가 있다 (Apps Script 가 깨뜨린다) : " + badEscapes.slice(0, 3).join(", "));
  }

  // 3. 자바스크립트 문법이 성립하는가
  scripts.forEach((s, i) => {
    try {
      new vm.Script(s);
    } catch (e) {
      err(`script[${i}] 문법 오류 : ${e.message}`);
    }
  });

  // 4. 필수 UI 요소
  const required = [
    ["w-room", "방 코드 입력"],
    ["w-pw", "비밀번호 입력"],
    ["w-nick", "닉네임 입력"],
    ["w-enter", "입장 버튼"],
    ["w-solo", "혼자 체험 경로"],
    ["w-teacher", "교사 화면 진입"],
    ["w-submit", "제출 버튼"],
    ["t-make", "새 방 만들기"],
    ["t-copy", "방 코드 복사 버튼"],
    ["t-csv", "CSV 내려받기"],
    ["t-lock", "방 잠그기"],
  ];
  required.forEach(([id_, label]) => {
    if (!html.includes(`id="${id_}"`)) err(`${label}(#${id_}) 가 없다`);
  });

  // 5. 필수 함수
  ["activityHtml", "activityCollect", "activityInit", "teacherSummary"].forEach((fn) => {
    if (!js.includes("function " + fn)) err(`${fn}() 가 없다`);
  });

  // 6. 저장 경로와 백업
  if (!js.includes("remind-c2610-default-rtdb.firebaseio.com")) err("Firebase 주소가 없다");
  if (!js.includes("/wise/")) err("Firebase 경로가 /wise 아래로 격리되지 않았다");
  if (!js.includes("sheetBackup")) err("Google Sheets 백업 함수가 없다");
  if (!js.includes('mode: "no-cors"')) err("Sheets 백업이 no-cors 모드가 아니다");
  if (!js.includes("getAnalytics")) { /* 정상 */ } else err("Analytics 를 붙이면 안 된다");

  // 7. 개인정보
  [/실명/, /학번/, /전화번호[ ]*<\/label>/, /type=["']file["']/].forEach((re) => {
    if (re.test(html)) err("개인정보 또는 파일 업로드 입력이 있다 : " + re);
  });

  // 8. 접근성·화면
  if (!/font-size:16px/.test(html) && !/font-size:1[6-9]px/.test(html)) {
    err("기본 글자 크기가 16px 이상인지 확인되지 않는다");
  }
  if (!/min-height:(4[89]|[5-9][0-9]|[1-9][0-9]{2})px/.test(html)) err("누르는 곳 최소 높이(48px 이상) 지정이 없다");
  if (!/overflow-x:auto/.test(html)) err("넓은 표를 위한 가로 스크롤 상자가 없다");
  if (!/prefers-reduced-motion/.test(html)) err("prefers-reduced-motion 대응이 없다");

  // 9. 안전 문구
  if (lesson) {
    if (lesson.no === 10) {
      if (!html.includes("믿을 수 있는 어른에게 먼저 말해요")) err("10차시 안전 문구가 없다");
      if (/개인 응답/.test(js) === false && /익명/.test(js) === false) {
        err("10차시는 익명 집계임을 화면에 밝혀야 한다");
      }
    } else if (!html.includes("개인정보는 넣지 않아요")) {
      err("입장 화면 개인정보 안내 문구가 없다");
    }
    if (!html.includes(lesson.webapp.name)) err("앱 이름이 화면에 없다 : " + lesson.webapp.name);
    if (!js.includes(`"${lesson.webapp.slug}"`)) err("slug 가 lessons.json 과 다르다");
  }

  // 10. 저작권과 금지 표현
  if (!html.includes("CC BY-NC-SA")) err("저작권 표기가 없다");
  if (html.includes("—")) err("em dash(—) 를 쓰지 않는다");

  // 부속 문서
  ["SPEC.md", "PROMPT.md"].forEach((f) => {
    if (!fs.existsSync(path.join(dir, f))) err(`${f} 가 없다`);
  });

  if (errors.length) {
    errors.forEach((e) => console.log("실패  " + e));
    console.log("");
    console.log(`NG  오류 ${errors.length}건`);
    return 1;
  }

  console.log("OK  " + path.relative(ROOT, file));
  console.log(`    ${Math.round(html.length / 1024)}KB 단일 파일, 외부 참조 없음, 문법 통과`);
  console.log("    방코드·복사·혼자체험·교사대시보드·CSV·잠그기 확인");
  console.log("    Firebase /wise 격리, Sheets no-cors 백업, 안전 문구 확인");
  return 0;
}

process.exit(main());
