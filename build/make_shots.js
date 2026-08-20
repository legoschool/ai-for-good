// 웹앱 화면을 자동으로 캡처한다. 교사 안내 자료에 넣을 그림이다.
//
// 크롬 헤드리스로 각 앱의 여정 화면(data-q)을 하나씩 열어 PNG 로 저장한다.
// 앱에 ?shot=화면이름&fill=1 을 붙이면 둘러보기로 들어가 그 화면을 열어 준다.
// 그 통로는 build/webapp_core.py 의 shotMode() 가 만든다.
//
// 사용법 : node build/make_shots.js          (12차시 + 공통 설문 전부)
//          node build/make_shots.js L04      (한 차시만)

"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.dirname(__dirname);
const OUT = path.join(ROOT, "out", "site", "assets", "shots");

const CHROMES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
];

/* 화면 이름을 사람이 읽는 말로 바꾼다. 없으면 이름을 그대로 쓴다. */
const NICE = {
  story: "이야기", hub: "허브", gate: "입장",
  train: "훈련장", sort: "분류실", open: "열람실", cond: "조건 작성소",
  class: "우리 반과 견주기", rule: "수칙 회의실", card: "결과 카드",
  week: "기록칸", scale: "저울칸", ask: "부탁 시험소", vow: "약속 작성소",
  judge: "판정", quiz: "몸풀기", label: "이름표 붙이기", test: "시험",
  starve: "편식 실험", roles: "역할 나누기", report: "성적표",
};

function chrome() {
  for (const p of CHROMES) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error("크롬을 찾지 못했다. CHROMES 목록에 경로를 추가한다.");
}

/* 앱이 가진 여정 화면 이름을 순서대로 뽑는다.
   화면은 자바스크립트가 그리므로 원본 HTML 이 아니라 그려진 DOM 에서 읽는다. */
function questsOf(exe, file) {
  let dom = "";
  try {
    dom = execFileSync(exe, [
      "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
      "--virtual-time-budget=3000", "--dump-dom", fileUrl(file) + "?shot=stage",
    ], { encoding: "utf8", timeout: 60000, maxBuffer: 40 * 1024 * 1024 });
  } catch (e) {
    return [];
  }
  const out = [];
  const re = /data-q="([^"]+)"/g;
  let m;
  while ((m = re.exec(dom))) {
    if (out.indexOf(m[1]) < 0) out.push(m[1]);
  }
  return out;
}

function fileUrl(p) {
  return "file:///" + p.replace(/\\/g, "/").replace(/ /g, "%20").replace(/#/g, "%23");
}

function shoot(exe, url, outPath, size) {
  execFileSync(exe, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--allow-file-access-from-files",
    "--window-size=" + size,
    "--virtual-time-budget=4000",
    "--screenshot=" + outPath,
    url,
  ], { stdio: "ignore", timeout: 60000 });
}

function main() {
  const only = process.argv[2];
  const exe = chrome();
  fs.mkdirSync(OUT, { recursive: true });

  const dirs = fs.readdirSync(path.join(ROOT, "out", "webapp"))
    .filter((d) => (only ? d === only : true));

  const index = {};
  let total = 0;

  for (const id of dirs) {
    const file = path.join(ROOT, "out", "webapp", id, "index.html");
    if (!fs.existsSync(file)) continue;
    const quests = questsOf(exe, file);
    const shots = [];

    /* 1. 입장 화면. 방 번호와 닉네임을 넣는 곳이라 교사에게 먼저 보여 준다. */
    const gate = path.join(OUT, id + "_0_입장.png");
    shoot(exe, fileUrl(file), gate, "1000,1150");
    shots.push({ name: "입장", file: path.basename(gate) });

    /* 2. 여정 화면. 예시값을 채운 상태로 찍는다. */
    quests.forEach((q, i) => {
      if (i >= 7) return;
      const target = path.join(OUT, id + "_" + (i + 1) + "_" + q + ".png");
      shoot(exe, fileUrl(file) + "?shot=" + encodeURIComponent(q) + "&fill=1", target, "1000,1400");
      shots.push({ name: NICE[q] || q, file: path.basename(target) });
    });

    index[id] = shots;
    total += shots.length;
    console.log("찍었다 : " + id + "  " + shots.length + "장");
  }

  const idxPath = path.join(OUT, "index.json");
  let merged = {};
  if (fs.existsSync(idxPath)) {
    try { merged = JSON.parse(fs.readFileSync(idxPath, "utf8")); } catch (e) { merged = {}; }
  }
  Object.keys(index).forEach((k) => { merged[k] = index[k]; });
  fs.writeFileSync(idxPath, JSON.stringify(merged, null, 1), "utf8");

  console.log("");
  console.log("모두 " + total + "장. " + path.relative(ROOT, OUT));
  return 0;
}

process.exit(main());
