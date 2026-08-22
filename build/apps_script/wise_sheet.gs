/**
 * WISE 수업 기록용 Apps Script.
 *
 * 하는 일 세 가지.
 *   1. setup()      시트에 탭과 머리글을 만든다. 한 번만 실행한다.
 *   2. doPost(e)    웹앱이 보낸 제출·설문·방 생성을 알맞은 탭에 쌓는다.
 *   3. doGet(e)     관리자 화면이 방 목록과 설문 집계를 읽어 간다.
 *
 * 설계 근거 : spec/20_기록과_효과성_측정.md
 * 붙여 넣는 법 : 같은 문서의 4절과 인수인계서 3-3 절을 본다.
 *
 * 2026년 G-DEAL A.N.D · CC BY-NC-SA
 */

var SHEET_ID = '1szLUD-hzMwQh7aaae5S9S7OS-hEXMEMj2Vhbd-hjjFM';

/* 앱 slug 를 차시 아이디로 바꾼다. lessons.json 과 같아야 한다. */
var APP_TO_LESSON = {
  'data-lab': 'L01',
  'verify-lab': 'L02',
  'bias-gallery': 'L03',
  'info-sorter': 'L04',
  'helper-or-doer': 'L05',
  'signal-judges': 'L06',
  'class-pledge': 'L07',
  'pledge-board': 'L08',
  'three-step-writing': 'L09',
  'habit-check': 'L10',
  'good-project-board': 'L11',
  'reflect-share': 'L12',
  'survey': '설문'
};

var HEAD_ROOMS = ['시각', '앱', '차시', '방코드', '학급이름표', '비고'];

var HEAD_SURVEY = ['시각', '방코드', '학생코드', '닉네임', '사전사후',
  '문항1', '문항2', '문항3', '문항4', '문항5', '문항6', '문항7', '문항8',
  '주체성', '비판적사고', '윤리적사고', '성찰적사고', '사회관계적사고', '전체평균',
  '자유응답1', '자유응답2'];

var HEAD_ALL = ['시각', '앱', '차시', '방코드', '학생코드', '닉네임', '모둠', '지표요약', 'payload원문'];

/* 차시별 탭의 지표 컬럼. 앞 네 칸(시각·방코드·학생코드·닉네임)은 자동으로 붙는다. */
var LESSON_COLS = {
  L01: ['라벨수', '정확도전체', '정확도편식', '남긴카드', '배움문장'],
  L02: ['검증단계수', '찾은환각수', '몸풀기점수'],
  L03: ['짐작', '세어본수', '창고비율', '바꾼횟수'],
  L04: ['판단카드수', '기준일치수', '안전감각', '되돌리기상자', '생각바꿈', '조건수', '수칙수'],
  L05: ['판정수', '고친수', '경계사례수', '규칙수'],
  L06: ['판정수', '생각바꿈', '조건수', '몸풀기점수'],
  L07: ['조항수', '금지형고침', '투표수'],
  L08: ['제목유무', '문구유무', '표기유무', '고친횟수'],
  L09: ['1단계글자수', '2단계글자수', '3단계글자수', '받아들인수', '버린수'],
  L10: ['사용일수', '보조수', '대행수', '대행비율', '못하는일수', '말할사람수', '약속수'],
  L11: ['후보수', '고른문제', '좁힘여부', '신호등', '조건수'],
  L12: ['결과물유무', '사람이한일', 'AI가한일', '지킨약속', '성찰길이']
};

/* 설문 문항을 휴먼스킬 영역으로 묶는다. 번호는 1부터다. */
var SKILL_ITEMS = {
  '주체성': [1, 6],
  '비판적사고': [2, 5],
  '윤리적사고': [3],
  '성찰적사고': [4, 8],
  '사회관계적사고': [7]
};

/* ---------- 준비 ---------- */

function book() {
  return SpreadsheetApp.openById(SHEET_ID);
}

function tab(name, head) {
  var ss = book();
  var sh = ss.getSheetByName(name);
  if (!sh) {
    sh = ss.insertSheet(name);
  }
  if (head && sh.getLastRow() === 0) {
    sh.getRange(1, 1, 1, head.length).setValues([head]);
    sh.getRange(1, 1, 1, head.length).setFontWeight('bold').setBackground('#eef2ff');
    sh.setFrozenRows(1);
  }
  return sh;
}

/** 시트에서 한 번만 실행한다. 탭과 머리글을 만든다. 이미 있으면 그대로 둔다. */
function setup() {
  tab('방목록', HEAD_ROOMS);
  tab('설문', HEAD_SURVEY);
  tab('제출_통합', HEAD_ALL);
  for (var lid in LESSON_COLS) {
    if (!LESSON_COLS.hasOwnProperty(lid)) { continue; }
    tab(lid, ['시각', '방코드', '학생코드', '닉네임'].concat(LESSON_COLS[lid]));
  }
  return '탭과 머리글을 만들었습니다.';
}

/* ---------- 받기 ---------- */

function doPost(e) {
  var out = { ok: true, saved: 0 };
  try {
    var body = JSON.parse(e.postData.contents);

    /* 교사가 방을 만들었다는 알림 */
    var rooms = body.rooms || [];
    for (var r = 0; r < rooms.length; r++) {
      saveRoom(rooms[r]);
      out.saved += 1;
    }

    /* 학생 제출 */
    var rows = body.rows || [];
    for (var i = 0; i < rows.length; i++) {
      saveRow(rows[i]);
      out.saved += 1;
    }
  } catch (err) {
    out.ok = false;
    out.error = String(err);
  }
  return ContentService.createTextOutput(JSON.stringify(out))
    .setMimeType(ContentService.MimeType.JSON);
}

function saveRoom(room) {
  if (!room || !room.room) { return; }
  var lid = APP_TO_LESSON[room.app] || room.app || '';
  tab('방목록', HEAD_ROOMS).appendRow([
    stamp(room.at), room.app || '', lid, "'" + String(room.room),
    room.tag || '', room.note || ''
  ]);
}

function saveRow(rec) {
  if (!rec || !rec.app) { return; }
  var lid = APP_TO_LESSON[rec.app] || rec.app;
  var p = rec.payload || {};

  if (rec.app === 'survey') {
    saveSurvey(rec, p);
  } else if (LESSON_COLS[lid]) {
    var vals = metricsFor(lid, p);
    tab(lid, ['시각', '방코드', '학생코드', '닉네임'].concat(LESSON_COLS[lid]))
      .appendRow([stamp(rec.at), "'" + String(rec.room || ''), codeOf(rec), rec.nick || ''].concat(vals));
  }

  tab('제출_통합', HEAD_ALL).appendRow([
    stamp(rec.at), rec.app, lid, "'" + String(rec.room || ''), codeOf(rec),
    rec.nick || '', rec.group || '', summaryOf(lid, p), JSON.stringify(p).slice(0, 40000)
  ]);
}

function saveSurvey(rec, p) {
  var pick = p.pick || {};
  var items = [];
  for (var i = 0; i < 8; i++) {
    var v = pick[i];
    if (v === undefined || v === null || v === '') {
      items.push('');
      continue;
    }
    var score = Number(v) + 1;
    if (i === 0) { score = 6 - score; }   /* 1번은 역채점한다 */
    items.push(score);
  }

  var skills = [];
  var names = ['주체성', '비판적사고', '윤리적사고', '성찰적사고', '사회관계적사고'];
  var all = [], n;
  for (var s = 0; s < names.length; s++) {
    var nums = SKILL_ITEMS[names[s]], sum = 0, cnt = 0;
    for (var k = 0; k < nums.length; k++) {
      var val = items[nums[k] - 1];
      if (val === '') { continue; }
      sum += val;
      cnt += 1;
      all.push(val);
    }
    skills.push(cnt ? round1(sum / cnt) : '');
  }
  var total = '';
  if (all.length) {
    var t = 0;
    for (n = 0; n < all.length; n++) { t += all[n]; }
    total = round1(t / all.length);
  }

  var opens = p.opens || [];
  tab('설문', HEAD_SURVEY).appendRow([
    stamp(rec.at), "'" + String(rec.room || ''), codeOf(rec), rec.nick || '',
    p.when || '사전'
  ].concat(items).concat(skills).concat([total, opens[0] || '', opens[1] || '']));
}

/* ---------- 지표 뽑기 ---------- */

function metricsFor(lid, p) {
  var acc = p.acc || {};
  if (lid === 'L01') {
    return [count(p.labels), acc.full || '', acc.starved || '', acc.keep || '', p.learned || ''];
  }
  if (lid === 'L02') {
    return [count(p.steps) || len(p.verdicts), p.caught || len(p.hunt), p.quizOk || ''];
  }
  if (lid === 'L03') {
    return [p.guess || '', p.counted || '', p.ratio || '', p.changed || ''];
  }
  if (lid === 'L04') {
    return [p.judged || 0, p.hit || 0, pctOf(p.hit, p.judged), p.leaked || 0,
      p.changed || 0, count(p.cond), len(p.rules)];
  }
  if (lid === 'L05') {
    return [p.judged || 0, p.fixed || 0, count(p.zones), len(p.rules)];
  }
  if (lid === 'L06') {
    return [p.judged || 0, p.changed || 0, count(p.cond), p.quizOk || ''];
  }
  if (lid === 'L07') {
    return [len(p.board) || count(p.clause), p.fixed || 0, len(p.votes)];
  }
  if (lid === 'L08') {
    return [yn(p.title), yn(p.body), yn(p.credit), p.changed || 0];
  }
  if (lid === 'L09') {
    return [textLen(p.f0), textLen(p.f1), textLen(p.f2), len(p.takeYes), len(p.takeNo)];
  }
  if (lid === 'L10') {
    return [p.usedDays || 0, p.assist || 0, p.agent || 0, p.agentPct || 0,
      len(p.cant), len(p.who), len(p.vows)];
  }
  if (lid === 'L11') {
    return [len(p.cands), p.problem || p.pick || '', yn(p.narrow),
      p.signalName || p.signal || '', count(p.cond)];
  }
  if (lid === 'L12') {
    return [yn(p.made || p.title), p.who || '', p.aiDecide || '', len(p.kept), textLen(p.growth || p.after)];
  }
  return [];
}

function summaryOf(lid, p) {
  var cols = LESSON_COLS[lid];
  if (!cols) { return ''; }
  var vals = metricsFor(lid, p), out = [];
  for (var i = 0; i < cols.length && i < vals.length; i++) {
    if (vals[i] === '' || vals[i] === undefined) { continue; }
    out.push(cols[i] + ' ' + vals[i]);
  }
  return out.join(' · ');
}

/* ---------- 관리자 화면이 읽는 곳 ---------- */

function doGet(e) {
  var what = (e && e.parameter && e.parameter.what) || 'rooms';
  var data;
  if (what === 'survey') {
    data = surveySummary();
  } else if (what === 'counts') {
    data = submitCounts();
  } else {
    data = roomList();
  }
  var body = JSON.stringify(data);
  var cb = e && e.parameter && e.parameter.callback;
  if (cb) {
    return ContentService.createTextOutput(cb + '(' + body + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService.createTextOutput(body).setMimeType(ContentService.MimeType.JSON);
}

/** 방목록. 같은 앱·방코드는 처음 것만 남긴다. */
function roomList() {
  var sh = book().getSheetByName('방목록');
  if (!sh || sh.getLastRow() < 2) { return { rooms: [] }; }
  var vals = sh.getRange(2, 1, sh.getLastRow() - 1, HEAD_ROOMS.length).getValues();
  var seen = {}, out = [];
  for (var i = 0; i < vals.length; i++) {
    var app = String(vals[i][1] || ''), room = String(vals[i][3] || '').replace(/^'/, '');
    if (!app || !room) { continue; }
    var key = app + '/' + room;
    if (seen[key]) { continue; }
    seen[key] = true;
    out.push({ at: String(vals[i][0]), app: app, lesson: String(vals[i][2] || ''),
      room: room, tag: String(vals[i][4] || '') });
  }
  return { rooms: out };
}

/** 설문 집계. 개인 응답은 내보내지 않는다. 학생코드는 매칭 수를 세는 데만 쓴다. */
function surveySummary() {
  var sh = book().getSheetByName('설문');
  if (!sh || sh.getLastRow() < 2) { return { pre: 0, post: 0, items: [], skills: {}, matched: 0 }; }
  var vals = sh.getRange(2, 1, sh.getLastRow() - 1, HEAD_SURVEY.length).getValues();
  var pre = [], post = [], preByCode = {}, postByCode = {};
  var i, k;
  for (i = 0; i < 8; i++) { pre.push([]); post.push([]); }

  for (i = 0; i < vals.length; i++) {
    var row = vals[i];
    var when = String(row[4] || '사전');
    var code = String(row[2] || '');
    var arr = when === '사후' ? post : pre;
    for (k = 0; k < 8; k++) {
      var v = row[5 + k];
      if (v === '' || v === null) { continue; }
      arr[k].push(Number(v));
    }
    var total = row[18];
    if (code && total !== '' && total !== null) {
      (when === '사후' ? postByCode : preByCode)[code] = Number(total);
    }
  }

  var items = [];
  for (k = 0; k < 8; k++) {
    items.push({ no: k + 1, pre: mean(pre[k]), post: mean(post[k]),
      preN: pre[k].length, postN: post[k].length });
  }

  var up = 0, same = 0, down = 0, diffs = [];
  for (var code2 in preByCode) {
    if (!preByCode.hasOwnProperty(code2) || postByCode[code2] === undefined) { continue; }
    var d = postByCode[code2] - preByCode[code2];
    diffs.push(d);
    if (d > 0.05) { up += 1; } else if (d < -0.05) { down += 1; } else { same += 1; }
  }

  return { items: items, matched: diffs.length, up: up, same: same, down: down,
    meanDiff: mean(diffs), preCount: countRows(vals, '사전'), postCount: countRows(vals, '사후') };
}

/** 차시별 제출 인원. 방코드별로 센다. */
function submitCounts() {
  var sh = book().getSheetByName('제출_통합');
  if (!sh || sh.getLastRow() < 2) { return { counts: [] }; }
  var vals = sh.getRange(2, 1, sh.getLastRow() - 1, HEAD_ALL.length).getValues();
  var map = {};
  for (var i = 0; i < vals.length; i++) {
    var lid = String(vals[i][2] || ''), room = String(vals[i][3] || '').replace(/^'/, '');
    var nick = String(vals[i][5] || '');
    if (!lid || !room) { continue; }
    var key = lid + '|' + room;
    if (!map[key]) { map[key] = {}; }
    map[key][nick] = true;
  }
  var out = [];
  for (var key2 in map) {
    if (!map.hasOwnProperty(key2)) { continue; }
    var parts = key2.split('|');
    out.push({ lesson: parts[0], room: parts[1], people: count(map[key2]) });
  }
  return { counts: out };
}

/* ---------- 작은 도구 ---------- */

function stamp(at) {
  var d = at ? new Date(Number(at)) : new Date();
  return Utilities.formatDate(d, 'Asia/Seoul', 'yyyy-MM-dd HH:mm:ss');
}

function codeOf(rec) {
  var c = rec.code || (rec.payload && rec.payload.code) || '';
  return c ? "'" + String(c) : '';
}

function count(obj) {
  if (!obj) { return 0; }
  var n = 0;
  for (var k in obj) { if (obj.hasOwnProperty(k)) { n += 1; } }
  return n;
}

function len(arr) {
  return arr && arr.length ? arr.length : 0;
}

function textLen(s) {
  return s ? String(s).length : 0;
}

function yn(v) {
  return v ? 'O' : 'X';
}

function pctOf(a, b) {
  if (!b) { return 0; }
  return Math.round((Number(a) || 0) * 100 / Number(b));
}

function round1(x) {
  return Math.round(x * 10) / 10;
}

function mean(arr) {
  if (!arr || !arr.length) { return ''; }
  var s = 0;
  for (var i = 0; i < arr.length; i++) { s += arr[i]; }
  return round1(s / arr.length);
}

function countRows(vals, when) {
  var n = 0;
  for (var i = 0; i < vals.length; i++) {
    if (String(vals[i][4] || '사전') === when) { n += 1; }
  }
  return n;
}

/* ================================================================
   정리 도구. 시트 편집기에서 사람이 직접 실행한다. 웹앱은 부르지 않는다.
   ---------------------------------------------------------------
   1) 점검하기()      무엇이 몇 줄 겹쳤는지 보여만 준다. 아무것도 바꾸지 않는다.
   2) 겹친행지우기()  시각까지 똑같은 행만 지운다. 안전한 정리다.
   3) 최신만남기기()  방·닉네임마다 마지막 제출만 남긴다. 고쳐 낸 것이 있을 때 쓴다.

   ※ 지우기 전에 파일 > 사본 만들기 로 사본을 떠 두는 것을 권한다.
   ================================================================ */

/** 차시 탭 이름 목록. */
function lessonTabs_() {
  var out = [];
  for (var lid in LESSON_COLS) { if (LESSON_COLS.hasOwnProperty(lid)) { out.push(lid); } }
  return out;
}

/** 탭 하나를 읽어 머리글을 뺀 값과 크기를 돌려준다. */
function body_(name) {
  var sh = book().getSheetByName(name);
  if (!sh || sh.getLastRow() < 2) { return null; }
  var w = sh.getLastColumn();
  return { sh: sh, w: w, vals: sh.getRange(2, 1, sh.getLastRow() - 1, w).getValues() };
}

/** 남길 행만 다시 써 넣는다. */
function rewrite_(b, keep) {
  b.sh.getRange(2, 1, b.vals.length, b.w).clearContent();
  if (keep.length) { b.sh.getRange(2, 1, keep.length, b.w).setValues(keep); }
}

/** 탭마다 어떤 칸이 '누구의 어느 제출인가'를 가리키는지. 0부터 센다. */
var KEYS_ = {
  '설문':      { room: 1, nick: 3, when: 4, time: 0 },
  '제출_통합': { room: 3, nick: 5, when: -1, time: 0 },
  '차시':      { room: 1, nick: 3, when: -1, time: 0 }
};

function keyOf_(name) { return KEYS_[name] || KEYS_['차시']; }

function sameKey_(row, k, withTime) {
  var parts = [String(row[k.room]), String(row[k.nick])];
  if (k.when >= 0) { parts.push(String(row[k.when])); }
  if (withTime) { parts.push(String(row[k.time])); }
  return parts.join('|');
}

/** 무엇이 겹쳤는지 세어만 본다. */
function 점검하기() {
  var names = ['설문', '제출_통합'].concat(lessonTabs_());
  var out = [];
  for (var i = 0; i < names.length; i++) {
    var b = body_(names[i]);
    if (!b) { out.push(names[i] + ' : 비어 있음'); continue; }
    var k = keyOf_(names[i]), seen = {}, dup = 0, people = {};
    for (var r = 0; r < b.vals.length; r++) {
      if (!String(b.vals[r][k.nick])) { continue; }
      var full = sameKey_(b.vals[r], k, true);
      if (seen[full]) { dup += 1; } else { seen[full] = true; }
      people[sameKey_(b.vals[r], k, false)] = true;
    }
    out.push(names[i] + ' : 행 ' + b.vals.length + ' · 사람 ' + count(people) + ' · 똑같이 겹친 행 ' + dup);
  }
  var msg = out.join('
');
  Logger.log(msg);
  return msg;
}

/** 시각까지 똑같은 행만 지운다. */
function 겹친행지우기() {
  var names = ['설문', '제출_통합'].concat(lessonTabs_());
  var out = [];
  for (var i = 0; i < names.length; i++) {
    var b = body_(names[i]);
    if (!b) { continue; }
    var k = keyOf_(names[i]), seen = {}, keep = [];
    for (var r = 0; r < b.vals.length; r++) {
      if (!String(b.vals[r][k.nick])) { keep.push(b.vals[r]); continue; }
      var key = sameKey_(b.vals[r], k, true);
      if (seen[key]) { continue; }
      seen[key] = true;
      keep.push(b.vals[r]);
    }
    var gone = b.vals.length - keep.length;
    if (gone) { rewrite_(b, keep); }
    out.push(names[i] + ' : ' + gone + '행 지움 (' + keep.length + '행 남음)');
  }
  var msg = out.join('
');
  Logger.log(msg);
  return msg;
}

/** 방·닉네임(설문은 사전사후까지)마다 마지막 제출만 남긴다. */
function 최신만남기기() {
  var names = ['설문', '제출_통합'].concat(lessonTabs_());
  var out = [];
  for (var i = 0; i < names.length; i++) {
    var b = body_(names[i]);
    if (!b) { continue; }
    var k = keyOf_(names[i]), last = {};
    for (var r = 0; r < b.vals.length; r++) {
      if (!String(b.vals[r][k.nick])) { continue; }
      var key = sameKey_(b.vals[r], k, false);
      var t = String(b.vals[r][k.time]);
      if (!last[key] || t >= last[key].t) { last[key] = { t: t, row: b.vals[r] }; }
    }
    var keep = [];
    for (var r2 = 0; r2 < b.vals.length; r2++) {
      if (!String(b.vals[r2][k.nick])) { keep.push(b.vals[r2]); continue; }
      var key2 = sameKey_(b.vals[r2], k, false);
      if (last[key2] && last[key2].row === b.vals[r2]) { keep.push(b.vals[r2]); }
    }
    var gone = b.vals.length - keep.length;
    if (gone) { rewrite_(b, keep); }
    out.push(names[i] + ' : ' + gone + '행 지움 (' + keep.length + '행 남음)');
  }
  var msg = out.join('
');
  Logger.log(msg);
  return msg;
}

/** 방코드 6자리·학생코드 4자리의 앞자리 0 을 되살리고 텍스트로 굳힌다.
    정리 함수가 값을 다시 쓸 때 0 이 떨어져 나가는 것을 바로잡는다. */
function 코드되살리기() {
  var plan = [{ name: '설문', room: 1, code: 2 },
              { name: '제출_통합', room: 3, code: 4 },
              { name: '방목록', room: 3, code: -1 }];
  var tabs = lessonTabs_();
  for (var i = 0; i < tabs.length; i++) { plan.push({ name: tabs[i], room: 1, code: 2 }); }
  var out = [];
  for (var p = 0; p < plan.length; p++) {
    var b = body_(plan[p].name);
    if (!b) { continue; }
    var changed = 0;
    for (var r = 0; r < b.vals.length; r++) {
      var before = String(b.vals[r][plan[p].room]);
      var after = pad_(before, 6);
      if (after !== before) { b.vals[r][plan[p].room] = after; changed += 1; }
      if (plan[p].code >= 0) {
        var cb = String(b.vals[r][plan[p].code]);
        var ca = pad_(cb, 4);
        if (ca !== cb) { b.vals[r][plan[p].code] = ca; changed += 1; }
      }
    }
    b.sh.getRange(2, plan[p].room + 1, b.vals.length, 1).setNumberFormat('@');
    if (plan[p].code >= 0) { b.sh.getRange(2, plan[p].code + 1, b.vals.length, 1).setNumberFormat('@'); }
    b.sh.getRange(2, 1, b.vals.length, b.w).setValues(b.vals);
    out.push(plan[p].name + ' : ' + changed + '칸 되살림');
  }
  var msg = out.join('
');
  Logger.log(msg);
  return msg;
}

function pad_(v, n) {
  var s = String(v == null ? '' : v).replace(/^'/, '').trim();
  if (!s || !/^[0-9]+$/.test(s)) { return s; }
  while (s.length < n) { s = '0' + s; }
  return s;
}

/** 값만 지워져 남은 빈 줄을 실제로 없앤다. */
function 빈행지우기() {
  var names = ['방목록'].concat(allTabs_()), out = [];
  for (var i = 0; i < names.length; i++) {
    var sh = book().getSheetByName(names[i]);
    if (!sh || sh.getLastRow() < 2) { continue; }
    var vals = sh.getRange(2, 1, sh.getLastRow() - 1, sh.getLastColumn()).getValues();
    var live = 0;
    for (var r = 0; r < vals.length; r++) {
      for (var c = 0; c < vals[r].length; c++) {
        if (String(vals[r][c]).length) { live = r + 1; break; }
      }
    }
    var gone = vals.length - live;
    if (gone > 0) { sh.deleteRows(live + 2, gone); }
    out.push(names[i] + ' : 빈 줄 ' + gone + '개 없앰 (' + live + '줄 남음)');
  }
  var msg = out.join('
');
  Logger.log(msg);
  return msg;
}

function allTabs_() { return ['설문', '제출_통합'].concat(lessonTabs_()); }
