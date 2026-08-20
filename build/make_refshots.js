// 참고자료 누리집의 첫 화면을 미리보기 그림으로 찍는다.
//
// 크롬 헤드리스로 각 주소를 열어 PNG 로 저장한다. 인터넷이 필요하다.
// 못 찍은 곳은 조용히 건너뛴다. 그림이 없어도 참고자료 페이지는 글자 카드로 완성된다.
//
// 사용법 : node build/make_refshots.js

"use strict";

const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const ROOT = path.dirname(__dirname);
const OUT = path.join(ROOT, "out", "site", "assets", "refshots");

const CHROMES = [
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
];

function chrome() {
  for (const p of CHROMES) if (fs.existsSync(p)) return p;
  throw new Error("크롬을 찾지 못했다.");
}

function main() {
  const dataPath = path.join(ROOT, "data", "lessons.json");
  const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
  const groups = data.refGroups || [];
  if (!groups.length) {
    console.log("data/lessons.json 에 refGroups 가 없다. 먼저 자료 목록을 적는다.");
    return 0;
  }

  fs.mkdirSync(OUT, { recursive: true });
  const exe = chrome();
  const index = {};
  let ok = 0, fail = 0;

  for (const g of groups) {
    for (const item of g.items || []) {
      const key = item.key;
      if (!key || !item.url) continue;
      const file = key + ".png";
      const target = path.join(OUT, file);
      try {
        execFileSync(exe, [
          "--headless=new", "--disable-gpu", "--hide-scrollbars",
          "--force-device-scale-factor=1", "--window-size=1200,900",
          "--virtual-time-budget=9000", "--screenshot=" + target, item.url,
        ], { stdio: "ignore", timeout: 90000 });
        if (fs.existsSync(target) && fs.statSync(target).size > 3000) {
          index[key] = file;
          ok += 1;
          console.log("찍었다 : " + key);
        } else {
          fail += 1;
          console.log("비었다 : " + key + " (그림 없이 글자 카드로 나간다)");
        }
      } catch (e) {
        fail += 1;
        console.log("못 찍었다 : " + key + " (접속이 막혔거나 느리다)");
      }
    }
  }

  fs.writeFileSync(path.join(OUT, "index.json"), JSON.stringify(index, null, 1), "utf8");
  console.log("");
  console.log("미리보기 " + ok + "장, 건너뜀 " + fail + "곳");
  return 0;
}

process.exit(main());
