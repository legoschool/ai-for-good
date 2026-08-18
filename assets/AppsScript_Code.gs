/**
 * WISE 수업 웹앱 백업 받는 곳
 *
 * 붙이는 곳 : 백업 시트 → 확장 프로그램 → Apps Script
 * 시트 이름 : 2026. ai적정활용 티처스랩
 *
 * 배포하는 법
 *   1. 이 코드를 통째로 붙여 넣고 저장한다
 *   2. 오른쪽 위 [배포] → [새 배포]
 *   3. 톱니바퀴 → [웹 앱] 선택
 *   4. 다음 실행 사용자 : 나
 *      액세스 권한이 있는 사용자 : 모든 사용자
 *   5. [배포] → 권한 승인 → 나온 웹 앱 URL 을 복사한다
 *
 * 주의
 *   이 주소는 학생 브라우저에서 호출하므로 감출 수 없다.
 *   그래서 아래에서 기록의 모양을 검사해 이상한 것을 걸러 낸다.
 *   진짜 원본은 Firebase 에 있고 이 시트는 백업이다.
 *   이상한 행이 들어와도 원본은 멀쩡하다.
 */

var HEADERS = ['받은시각', '앱', '방코드', '닉네임', '모둠', '제출시각', '내용'];

// 우리가 만든 앱 13개만 받는다. 그 밖의 이름은 버린다.
var ALLOWED = [
  'data-lab', 'verify-lab', 'bias-gallery', 'info-sorter',
  'helper-or-doer', 'signal-judges', 'class-pledge', 'pledge-board',
  'three-step-writing', 'habit-check', 'good-project-board', 'reflect-share',
  'survey'
];

var MAX_ROWS_PER_CALL = 200;

function isSixDigits(s) {
  if (typeof s !== 'string' || s.length !== 6) { return false; }
  for (var i = 0; i < 6; i++) {
    if (s.charAt(i) < '0' || s.charAt(i) > '9') { return false; }
  }
  return true;
}

function looksReal(r) {
  if (!r || typeof r !== 'object') { return false; }
  if (ALLOWED.indexOf(r.app) < 0) { return false; }
  if (!isSixDigits(String(r.room || ''))) { return false; }
  if (typeof r.nick !== 'string' || r.nick.length === 0 || r.nick.length > 12) { return false; }
  if (typeof r.at !== 'number') { return false; }
  // 서버 시간에서 크게 벗어난 것은 버린다
  var now = new Date().getTime();
  if (r.at > now + 300000 || r.at < now - 1000 * 60 * 60 * 24 * 400) { return false; }
  return true;
}

function sheetFor(ss, name) {
  var sheet = ss.getSheetByName(name);
  if (!sheet) {
    sheet = ss.insertSheet(name);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
    sheet.setColumnWidth(1, 150);
    sheet.setColumnWidth(7, 520);
  }
  return sheet;
}

function doPost(e) {
  var lock = LockService.getScriptLock();
  try {
    lock.waitLock(20000);
  } catch (err) {
    return out({ ok: false, error: 'busy' });
  }

  try {
    var body = JSON.parse(e.postData.contents);
    var rows = body.rows || [];
    if (rows.length > MAX_ROWS_PER_CALL) {
      rows = rows.slice(rows.length - MAX_ROWS_PER_CALL);
    }

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var now = new Date();
    var saved = 0;
    var dropped = 0;
    var bucket = {};

    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (!looksReal(r)) { dropped++; continue; }
      if (!bucket[r.app]) { bucket[r.app] = []; }
      bucket[r.app].push([
        now,
        r.app,
        String(r.room),
        r.nick,
        r.group || '',
        new Date(r.at),
        JSON.stringify(r.payload || {})
      ]);
      saved++;
    }

    for (var app in bucket) {
      if (!bucket.hasOwnProperty(app)) { continue; }
      var sheet = sheetFor(ss, app);
      var block = bucket[app];
      sheet.getRange(sheet.getLastRow() + 1, 1, block.length, HEADERS.length).setValues(block);
    }

    return out({ ok: true, saved: saved, dropped: dropped });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

function doGet() {
  return ContentService.createTextOutput('WISE backup endpoint is running.');
}

function out(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

/**
 * 배포 전에 이것을 한 번 실행해 보면 시트가 제대로 만들어지는지 확인할 수 있다.
 * 실행 후 signal-judges 탭에 시험 행이 하나 생긴다. 확인하고 지우면 된다.
 */
function 시험해보기() {
  var fake = {
    postData: {
      contents: JSON.stringify({
        rows: [{
          nick: '시험',
          group: '점검',
          app: 'signal-judges',
          room: '999001',
          at: new Date().getTime(),
          payload: { note: '배포 전 시험' }
        }]
      })
    }
  };
  Logger.log(doPost(fake).getContent());
}
