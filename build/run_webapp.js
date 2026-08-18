// 웹앱을 DOM 흉내 위에서 실제로 실행해 본다.
// 문법만이 아니라 런타임 오류와 활동 화면 동작까지 잡는다.
// 사용법 : node build/run_webapp.js out/webapp/L06

"use strict";

const fs = require("fs");
const path = require("path");
const vm = require("vm");

const ROOT = path.dirname(__dirname);

/* ---------- 아주 작은 DOM 흉내 ---------- */

function makeElement(id) {
  const el = {
    id,
    value: "",
    textContent: "",
    innerHTML: "",
    disabled: false,
    className: "",
    style: {},
    children: [],
    onclick: null,
    oninput: null,
    _attrs: {},
    getAttribute(k) { return this._attrs[k]; },
    setAttribute(k, v) { this._attrs[k] = v; },
    appendChild(c) { this.children.push(c); return c; },
    removeChild(c) { this.children = this.children.filter((x) => x !== c); },
    select() {},
    click() { if (this.onclick) this.onclick.call(this); },
  };
  return el;
}

function parseButtons(html) {
  // data-* 를 가진 버튼을 클래스별로 모아 둔다
  const picks = [];
  const byClass = {};
  const re = /<button[^>]*class="([^"]*)"[^>]*>/g;
  let m;
  while ((m = re.exec(html))) {
    const tag = m[0];
    const el = makeElement("");
    const attrs = tag.match(/data-([a-z]+)="([^"]*)"/g) || [];
    if (!attrs.length) continue;
    attrs.forEach((a) => {
      const [, k, v] = a.match(/data-([a-z]+)="([^"]*)"/);
      el.setAttribute("data-" + k, v);
    });
    el.className = m[1];
    m[1].split(/[ ]+/).forEach((c) => {
      if (!c) return;
      if (!byClass[c]) byClass[c] = [];
      byClass[c].push(el);
    });
    if (m[1].indexOf("pick") !== -1) picks.push(el);
  }
  return { picks, byClass };
}

function buildSandbox() {
  const store = {};
  const registry = {};

  const document = {
    _picks: [],
    _byClass: {},
    getElementById(id) {
      if (!registry[id]) registry[id] = makeElement(id);
      return registry[id];
    },
    querySelectorAll(sel) {
      // 마지막 낱말이 클래스 이름이다. 그 이름으로 모아 둔 목록을 돌려준다.
      const cls = sel.trim().split(/[ ]+/).pop().replace(/^[.]/, "");
      if (document._byClass[cls]) return document._byClass[cls];
      if (sel.indexOf("pick") !== -1) return document._picks;
      return [];
    },
    createElement() { return makeElement(""); },
    body: makeElement("body"),
  };

  const win = { scrollTo: () => {} };
  const sandbox = {
    window: win,
    scrollTo: () => {},
    document,
    navigator: { clipboard: null },
    localStorage: {
      getItem: (k) => (k in store ? store[k] : null),
      setItem: (k, v) => { store[k] = String(v); },
    },
    fetch: () => Promise.resolve({ json: () => Promise.resolve({}) }),
    setInterval: () => 0,
    clearInterval: () => {},
    setTimeout: () => 0,
    alert: () => {},
    prompt: () => "",
    Blob: function () {},
    URL: { createObjectURL: () => "blob:x" },
    Date,
    Math,
    JSON,
    Number,
    String,
    console,
  };
  sandbox.globalThis = sandbox;
  win.__wiseTest = null;
  return { sandbox, document, registry };
}

/* ---------- 실행 ---------- */

function main() {
  const target = process.argv[2];
  if (!target) {
    console.log("사용법 : node build/run_webapp.js <out/webapp/L06>");
    return 1;
  }
  const dir = path.isAbsolute(target) ? target : path.join(ROOT, target);
  const file = path.join(dir, "index.html");
  const html = fs.readFileSync(file, "utf8");
  const js = [...html.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/gi)].map((m) => m[1]).join("\n");

  const { sandbox, document } = buildSandbox();
  const errors = [];

  try {
    vm.createContext(sandbox);
    new vm.Script(js).runInContext(sandbox);
  } catch (e) {
    console.log("실패  실행 중 오류 : " + e.message);
    return 1;
  }

  const t = sandbox.window.__wiseTest;
  if (!t) {
    console.log("실패  테스트 통로(__wiseTest)가 없다");
    return 1;
  }

  // 1. 활동 화면이 그려지는가
  let markup = "";
  try {
    markup = t.activityHtml();
  } catch (e) {
    errors.push("activityHtml() 오류 : " + e.message);
  }
  if (!markup || markup.length < 100) errors.push("활동 화면이 비어 있다");

  // 2. 초기화가 도는가
  const parsed = parseButtons(markup);
  document._picks = parsed.picks;
  document._byClass = parsed.byClass;
  try {
    t.activityInit(null);
  } catch (e) {
    errors.push("activityInit() 오류 : " + e.message);
  }

  // 3. 빈 상태로 제출하면 막아야 한다
  try {
    t.setMe({ room: "solo", nick: "테스트", group: "", solo: true });
    const empty = t.activityCollect();
    if (empty !== null) errors.push("아무것도 안 쓴 채 제출이 통과된다");
  } catch (e) {
    errors.push("activityCollect() 오류 : " + e.message);
  }

  // 4. 채워 넣으면 제출이 되는가
  try {
    // 활동이 자체 채우기를 제공하면 그것을 쓴다. 1차시처럼 단계가 여러 개인 앱용이다.
    if (typeof t.activityAutofill === "function") t.activityAutofill();

    // 문항 묶음(data-c / data-i)마다 하나씩 골라 준다. 전부 답해야 통과하는 앱이 있다.
    const groups = new Map();
    document._picks.forEach((p) => {
      const key = p.getAttribute("data-c") !== undefined
        ? "c:" + p.getAttribute("data-c")
        : "i:" + p.getAttribute("data-i");
      if (!groups.has(key)) groups.set(key, p);
    });
    groups.forEach((p) => p.click());
    for (let i = 0; i < 8; i++) {
      const f = document.getElementById("f" + i);
      if (f) f.value = "테스트 입력입니다. 충분히 길게 씁니다.";
      const p = document.getElementById("p" + i);
      if (p) p.value = "약속 " + i;
      const r = document.getElementById("r" + i);
      if (r) r.value = "근거";
    }
    ["claus", "mean", "cant", "human", "ai", "title", "body", "credit"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.value = "테스트 내용입니다.";
    });
    const got = t.activityCollect();
    if (got === null) errors.push("정상 입력인데도 제출이 막힌다");
  } catch (e) {
    errors.push("제출 경로 오류 : " + e.message);
  }

  // 5. 교사 집계가 도는가
  try {
    const summary = t.teacherSummary([
      { nick: "가", group: "1모둠", at: Date.now(), payload: { choice: { 0: "0" }, values: ["ㄱ"], pick: { 0: "1" }, clause: "약속", title: "제목", body: "문구", credit: "표기" } },
      { nick: "나", group: "2모둠", at: Date.now(), payload: { choice: { 0: "1" }, values: ["ㄴ"], pick: { 0: "2" }, clause: "약속2", title: "제목2", body: "문구2", credit: "표기2" } },
    ]);
    if (!summary || summary.length < 30) errors.push("교사 집계 화면이 비어 있다");
  } catch (e) {
    errors.push("teacherSummary() 오류 : " + e.message);
  }

  if (errors.length) {
    errors.forEach((e) => console.log("실패  " + e));
    console.log("");
    console.log(`NG  오류 ${errors.length}건`);
    return 1;
  }

  console.log("OK  " + path.relative(ROOT, file) + "  실행 검사");
  console.log(`    활동 화면 ${markup.length}자, 빈 제출 차단, 정상 제출 통과, 교사 집계 동작`);
  return 0;
}

process.exit(main());
