// 학생이 하는 대로 앱을 처음부터 끝까지 돌려 본다.
// 구조가 아니라 수업이 의도대로 굴러가는지를 본다.
//
// 사용법 : node build/walkthrough.js L01
//          node build/walkthrough.js L02

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.dirname(__dirname);

function activitySource(file) {
  const py = fs.readFileSync(path.join(ROOT, "build", file), "utf8");
  const m = py.match(/ACTIVITY = u"""([\s\S]*?)"""\s*$/);
  if (!m) throw new Error("ACTIVITY 를 찾지 못했다 : " + file);
  // 파이썬이 읽은 뒤의 모습으로 되돌린다
  return m[1].replace(/\\\\n/g, "\\n").replace(/\\\\"/g, '\\"');
}

function sandbox(extra) {
  const el = () => ({
    value: "", textContent: "", innerHTML: "", className: "", style: {},
    disabled: false, onclick: null, oninput: null,
    getAttribute() { return undefined; }, setAttribute() {},
  });
  const reg = {};
  const base = {
    $: (id) => (reg[id] = reg[id] || el()),
    esc: (s) => String(s == null ? "" : s),
    document: { querySelectorAll: () => [], getElementById: (id) => (reg[id] = reg[id] || el()) },
    window: { scrollTo() {} },
    me: { room: "solo", nick: "시험", group: "", solo: true },
    Math, JSON, Number, String, Date, console,
    dbGet: () => Promise.resolve({}), dbPush: () => Promise.resolve({}),
  };
  return Object.assign(base, extra || {});
}

function runL01() {
  const src = activitySource("webapp_l01.py");
  const ctx = sandbox();
  vm.createContext(ctx);
  new vm.Script(src + "\nthis.__api = {TRAIN, TEST, CUTS, train, evaluate, predict, evidence, rows, label, FEAT_NAME};")
    .runInContext(ctx);
  const A = ctx.__api;

  console.log("=".repeat(66));
  console.log(" 1차시 데이터 실험실 : 학생처럼 돌려 보기");
  console.log("=".repeat(66));

  // 2단계. 학생은 소리를 듣고 이름표를 붙인다.
  A.TRAIN.forEach((c) => { A.label[c.id] = (c.snd === "야옹") ? "고양이" : "강아지"; });
  const dogs = A.TRAIN.filter((c) => A.label[c.id] === "강아지").length;
  const cats = A.TRAIN.length - dogs;
  console.log("");
  console.log("2단계. 귀 모양을 보고 이름표를 붙였다");
  console.log("  강아지 " + dogs + "장, 고양이 " + cats + "장");

  // 3단계. 전체로 학습
  const full = A.evaluate(A.train(A.rows(null)));
  console.log("");
  console.log("3단계. 전체 데이터로 배우고 시험");
  console.log("  정확도 " + full.hit + " / " + full.of);
  full.detail.forEach((d, i) => {
    console.log("    시험" + (i + 1) + "  " + (d.ok ? "맞음" : "틀림") +
      "  (" + d.got + " / 정답 " + d.ans + ", 확신 " + Math.round(d.p * 100) + "%)");
  });
  const ev = A.evidence(A.train(A.rows(null)));
  console.log("  가장 크게 갈라 준 특징 : " + ev.map((e) => e.name).join(" > "));

  // 4단계. 무엇을 빼면 무엇이 깨지는가
  console.log("");
  console.log("4단계. 어떤 카드를 빼면");
  console.log("  뺀 것                      정확도  맞히다 틀리게 바뀐 카드");
  let anyBreak = null;
  A.CUTS.forEach((rule) => {
    const cutRows = A.rows(rule.key);
    const cut = A.evaluate(A.train(cutRows));
    const flipped = [];
    for (let i = 0; i < A.TEST.length; i++) {
      if (full.detail[i].ok && !cut.detail[i].ok) {
        flipped.push((i + 1) + "번 " + A.TEST[i].ans + "(" + A.TEST[i].size + ")");
      }
    }
    if (flipped.length && !anyBreak) anyBreak = rule.name;
    const removed = A.rows(null).length - cutRows.length;
    console.log("  " + rule.name.padEnd(22) + " " + cut.hit + " / " + cut.of +
      "   " + (flipped.length ? flipped.join(", ") : "없음") + "   (뺀 카드 " + removed + "장)");
  });
  const firstBreak = anyBreak;

  console.log("");
  console.log("-".repeat(66));
  if (firstBreak === null) {
    console.log(" 문제  무엇을 빼도 정확도가 떨어지지 않는다.");
    console.log("       이 차시의 핵심 장면인 '못 본 것은 틀린다' 가 일어나지 않는다.");
    return 1;
  }
  console.log(" OK  '" + firstBreak + "' 를 고르면 AI가 틀리기 시작한다.");
  console.log("     수업에서 이 장면이 실제로 일어난다.");
  return 0;
}

function runL02() {
  const src = activitySource("webapp_l02.py");
  const ctx = sandbox();
  vm.createContext(ctx);
  new vm.Script(src + "\nthis.__api = {ITEMS, VERDICT_LABEL};").runInContext(ctx);
  const A = ctx.__api;

  console.log("=".repeat(66));
  console.log(" 2차시 AI 검증 실험실 : 학생처럼 돌려 보기");
  console.log("=".repeat(66));

  let bad = 0;
  A.ITEMS.forEach((it, i) => {
    console.log("");
    console.log((i + 1) + ". " + it.q);
    console.log("   가 : " + it.a);
    console.log("   나 : " + it.b);
    console.log("   자료 : " + String(it.src).split("\n")[0]);
    console.log("   맞는 답 : " + A.VERDICT_LABEL[it.verdict] + "   (" + it.kind + ")");

    // 자료 안에 답을 가릴 근거가 실제로 들어 있는가
    const src2 = String(it.src);
    const win = it.verdict === "a" ? it.a : (it.verdict === "b" ? it.b : null);
    if (win) {
      const nums = (win.match(/[0-9,]{3,}/g) || []);
      const found = nums.filter((n) => src2.indexOf(n) >= 0);
      if (nums.length && !found.length) {
        console.log("   문제  자료에 맞는 답을 가릴 근거가 없다. 학생이 확인할 수 없다.");
        bad++;
      }
    }
    if (it.verdict === "both" && src2.indexOf("790") < 0) {
      console.log("   문제  둘 다 맞다는 것을 보여 줄 자료가 부족하다.");
      bad++;
    }
    ["창제", "반포", "개교", "연혁", "발췌"].forEach((w) => {
      if ((it.q + it.a + it.b + src2 + it.why).indexOf(w) >= 0) {
        console.log("   문제  어려운 말이 남아 있다 : " + w);
        bad++;
      }
    });
  });

  // 다섯 문항이 서로 다른 방식으로 틀리는가
  const kinds = new Set(A.ITEMS.map((it) => it.kind));
  console.log("");
  console.log("-".repeat(66));
  console.log(" 틀리는 방식 " + kinds.size + "가지 : " + [...kinds].join(" / "));
  if (kinds.size < A.ITEMS.length) {
    console.log(" 문제  겹치는 방식이 있다. 문항마다 다른 실패를 보여 주어야 한다.");
    bad++;
  }
  const verdicts = A.ITEMS.map((it) => it.verdict);
  console.log(" 정답 분포 : 가 " + verdicts.filter((v) => v === "a").length +
    ", 나 " + verdicts.filter((v) => v === "b").length +
    ", 둘 다 " + verdicts.filter((v) => v === "both").length);
  if (verdicts.filter((v) => v === "b").length === A.ITEMS.length) {
    console.log(" 문제  답이 늘 나 쪽이다. 학생이 규칙을 외워 버린다.");
    bad++;
  }

  console.log("");
  if (bad) {
    console.log(" 걸린 곳 " + bad + "건");
    return 1;
  }
  console.log(" OK  다섯 문항이 서로 다르게 틀리고, 자료로 확인할 수 있다.");
  return 0;
}

const which = (process.argv[2] || "").toUpperCase();
if (which === "L01") process.exit(runL01());
else if (which === "L02") process.exit(runL02());
else {
  console.log("사용법 : node build/walkthrough.js L01 | L02");
  process.exit(1);
}
