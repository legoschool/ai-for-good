// 통합 웹사이트 검사.
// 사용법 : node build/check_site.js out/site

"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.dirname(__dirname);
/* 임베드를 허용하는 곳. 여기 적힌 곳만 iframe 으로 끼울 수 있다.
   늘리려면 사람이 정하고 인수인계서에 적는다. */
const EMBED_OK = [
  "www.youtube.com/embed/", "youtube.com/embed/", "www.youtube-nocookie.com/embed/",
  "www.canva.com/design/", "canva.com/design/",
];

const errors = [];
const err = (m) => errors.push(m);

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    const p = path.join(dir, name);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p, out);
    else out.push(p);
  }
  return out;
}

// 그 참조가 <a ...> 안에 있는지 본다. 링크는 허용, script/link/img 는 금지.
function isAnchorHref(html, match) {
  const at = html.indexOf(match);
  if (at < 0) return false;
  const open = html.lastIndexOf("<", at);
  return html.slice(open, at).toLowerCase().startsWith("<a ");
}

function main() {
  const target = process.argv[2] || "out/site";
  const site = path.isAbsolute(target) ? target : path.join(ROOT, target);
  if (!fs.existsSync(site)) {
    console.log("실패  사이트 폴더가 없다 : " + site);
    return 1;
  }

  const data = JSON.parse(fs.readFileSync(path.join(ROOT, "data", "lessons.json"), "utf8"));
  const files = walk(site);
  const pages = files.filter((f) => f.endsWith(".html") && !f.includes(path.sep + "webapp" + path.sep));

  // 1. 있어야 할 페이지
  const need = ["index.html", "apps.html", "survey.html", "about.html",
    "assets/style.css",
    ...data.modules.map((m) => `module/M${m.no}.html`),
    ...data.lessons.map((l) => `lesson/${l.id}.html`)];
  need.forEach((rel) => {
    if (!fs.existsSync(path.join(site, rel))) err("페이지가 없다 : " + rel);
  });

  // 2. 페이지마다 지켜야 할 것
  for (const p of pages) {
    const rel = path.relative(site, p).split(path.sep).join("/");
    const html = fs.readFileSync(p, "utf8");

    if (!/<html lang="ko">/.test(html)) err(`${rel} : lang="ko" 가 없다`);
    if (!/<meta name="viewport"/.test(html)) err(`${rel} : viewport 메타가 없다`);
    if (!/<title>[^<]+<\/title>/.test(html)) err(`${rel} : title 이 비었다`);
    if (!html.includes("CC BY-NC-SA")) err(`${rel} : 저작권 표기가 없다`);
    if (html.includes("—")) err(`${rel} : em dash(—) 를 쓰지 않는다`);

    // 외부 리소스 금지 (학교망 차단). 다만 아래 둘은 허용한다.
    //  1) <a> 로 거는 참고 자료 링크
    //  2) 영상과 카드뉴스 임베드 (아래 EMBED_OK 에 적은 곳만)
    // 임베드는 학교망에서 막힐 수 있으므로 같은 자료의 링크를 반드시 함께 둔다.
    const ext = (html.match(/(src|href)[ ]*=[ ]*["'](https?:)?[/][/][^"']+["']/gi) || [])
      .filter((m) => !isAnchorHref(html, m))
      .filter((m) => !EMBED_OK.some((host) => m.includes(host)));
    if (ext.length) err(`${rel} : 외부 리소스를 참조한다 : ${ext[0]}`);

    // 임베드를 쓴 쪽은 같은 자료를 여는 링크도 함께 두어야 한다
    const frames = html.match(/<iframe[^>]+src[ ]*=[ ]*["']([^"']+)["']/gi) || [];
    if (frames.length && !/<a[^>]+href[ ]*=[ ]*["']https?:/i.test(html)) {
      err(`${rel} : 임베드만 있고 여는 링크가 없다. 학교망에서 막히면 아무것도 안 보인다`);
    }

    // 링크가 실제로 존재하는가
    const links = [...html.matchAll(/(?:href|src)[ ]*=[ ]*"([^"#?:]+)"/g)].map((m) => m[1]);
    for (const href of links) {
      if (!href || href.startsWith("mailto")) continue;
      const abs = path.resolve(path.dirname(p), href);
      if (!fs.existsSync(abs)) err(`${rel} : 끊긴 링크 -> ${href}`);
    }
  }

  // 3. 차시 페이지 내용
  for (const l of data.lessons) {
    const p = path.join(site, "lesson", `${l.id}.html`);
    if (!fs.existsSync(p)) continue;
    const html = fs.readFileSync(p, "utf8");
    const checks = [
      [l.problem, "학습 문제"],
      [l.webapp.name, "웹앱 이름"],
      [l.alternative, "AI 미사용 대안"],
      [`WISE_${l.id}_지도안.hwpx`, "지도안 내려받기"],
      [`WISE_${l.id}_활동지.hwpx`, "활동지 내려받기"],
      [`WISE_${l.id}_수업.pptx`, "PPT 내려받기"],
      [`webapp/${l.id}/index.html`, "웹앱 바로가기"],
    ];
    checks.forEach(([needle, label]) => {
      if (!html.includes(needle.replace(/&/g, "&amp;").replace(/</g, "&lt;"))
        && !html.includes(needle)) {
        err(`lesson/${l.id}.html : ${label} 가 없다`);
      }
    });
    l.humanSkills.focus.forEach((f) => {
      if (!html.includes(f.name)) err(`lesson/${l.id}.html : 휴먼스킬 ${f.name} 가 없다`);
    });
    // 다른 차시 오염
    data.lessons.forEach((o) => {
      if (o.no !== l.no && html.includes(o.problem)) {
        err(`lesson/${l.id}.html : 다른 차시(${o.no}) 내용이 섞여 있다`);
      }
    });
  }

  // 4. 내려받기 파일이 실제로 있는가
  const filesDir = path.join(site, "files");
  let missing = 0;
  for (const l of data.lessons) {
    [`WISE_${l.id}_지도안.hwpx`, `WISE_${l.id}_활동지.hwpx`, `WISE_${l.id}_수업.pptx`]
      .forEach((f) => { if (!fs.existsSync(path.join(filesDir, f))) missing++; });
  }
  if (missing) err(`내려받기 파일 ${missing}개가 사이트 안에 없다`);

  // 5. 웹앱 12개 + 공통
  for (const l of data.lessons) {
    if (!fs.existsSync(path.join(site, "webapp", l.id, "index.html"))) {
      err(`webapp/${l.id}/index.html 이 사이트 안에 없다`);
    }
  }
  if (!fs.existsSync(path.join(site, "webapp", "common", "index.html"))) {
    err("공통 설문 웹앱이 사이트 안에 없다");
  }

  if (errors.length) {
    errors.slice(0, 30).forEach((e) => console.log("실패  " + e));
    if (errors.length > 30) console.log(`  ... 그 밖에 ${errors.length - 30}건`);
    console.log("");
    console.log(`NG  오류 ${errors.length}건`);
    return 1;
  }

  const total = files.length;
  console.log("OK  " + path.relative(ROOT, site));
  console.log(`    페이지 ${pages.length}개, 파일 ${total}개, 끊긴 링크 없음, 외부 참조 없음`);
  console.log("    차시별 학습문제·휴먼스킬·웹앱·자료 내려받기 확인");
  return 0;
}

process.exit(main());
