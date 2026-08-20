# -*- coding: utf-8 -*-
"""웹앱 안에서 쓰는 그림. 활동 구역에 함께 넣는 자바스크립트다.

  wiseIcon(kind, size)   낱개 아이콘. 카드와 버튼 옆에 붙인다
  wiseScene(kind)        설명 그림. 활동 위쪽에 크게 깐다

전부 인라인 SVG 다. 외부 이미지 파일을 부르지 않는다.
함수 선언이므로 활동 코드보다 뒤에 붙어도 활동에서 부를 수 있다.
"""

ICON_JS = u"""
  /* ---------- 그림 ---------- */

  function wiseIcon(kind, size) {
    var s = size || 30;
    var ink = "#111";
    var body = "";
    if (kind === "id") {
      body = '<circle cx="24" cy="18" r="9" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M9 42c0-9 7-14 15-14s15 5 15 14z" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "loc") {
      body = '<path d="M24 5c8 0 14 6 14 14 0 10-14 24-14 24S10 29 10 19c0-8 6-14 14-14z" fill="#2B59E0" stroke="' +
        ink + '" stroke-width="3"/><circle cx="24" cy="19" r="5" fill="#fff"/>';
    } else if (kind === "rel") {
      body = '<circle cx="17" cy="17" r="8" fill="#7B4FE8" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="32" cy="20" r="7" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M6 42c0-8 5-12 11-12s11 4 11 12z" fill="#7B4FE8" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "rec") {
      body = '<rect x="10" y="7" width="28" height="34" rx="4" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M17 17h14M17 25h14M17 33h8" stroke="' + ink + '" stroke-width="3" stroke-linecap="round"/>';
    } else if (kind === "pub") {
      body = '<circle cx="24" cy="24" r="17" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M7 24h34M24 7c6 8 6 26 0 34M24 7c-6 8-6 26 0 34" fill="none" stroke="' + ink + '" stroke-width="2.5"/>';
    } else if (kind === "green") {
      body = '<circle cx="24" cy="24" r="16" fill="#16a34a" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M16 24l6 7 12-14" stroke="#fff" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>';
    } else if (kind === "yellow") {
      body = '<circle cx="24" cy="24" r="16" fill="#eab308" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M24 14v13" stroke="#fff" stroke-width="4" stroke-linecap="round"/>' +
        '<circle cx="24" cy="33" r="2.6" fill="#fff"/>';
    } else if (kind === "orange") {
      body = '<circle cx="24" cy="24" r="16" fill="#ea580c" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M24 13l12 21H12z" fill="#fff" stroke="' + ink + '" stroke-width="2"/>';
    } else if (kind === "red") {
      body = '<circle cx="24" cy="24" r="16" fill="#dc2626" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M16 16l16 16M32 16L16 32" stroke="#fff" stroke-width="4" stroke-linecap="round"/>';
    } else if (kind === "me") {
      body = '<circle cx="24" cy="16" r="8" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M10 42c0-9 6-14 14-14s14 5 14 14z" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "ai") {
      body = '<rect x="9" y="12" width="30" height="24" rx="6" fill="#2B59E0" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="18" cy="24" r="3.4" fill="#fff"/><circle cx="30" cy="24" r="3.4" fill="#fff"/>' +
        '<path d="M24 12V6M18 40h12" stroke="' + ink + '" stroke-width="3" stroke-linecap="round"/>';
    } else if (kind === "both") {
      body = '<circle cx="17" cy="24" r="10" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<rect x="24" y="15" width="18" height="18" rx="5" fill="#2B59E0" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "write") {
      body = '<path d="M10 38l4-11 20-20 7 7-20 20z" fill="#FFE24B" stroke="' + ink + '" stroke-width="3" stroke-linejoin="round"/>' +
        '<path d="M8 42h32" stroke="' + ink + '" stroke-width="3" stroke-linecap="round"/>';
    } else if (kind === "check") {
      body = '<rect x="9" y="9" width="30" height="30" rx="7" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M16 24l6 7 12-15" stroke="#00D45A" stroke-width="4.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>';
    } else if (kind === "again") {
      body = '<path d="M38 24a14 14 0 1 1-5-10.7" fill="none" stroke="' + ink + '" stroke-width="4"/>' +
        '<path d="M36 6v10h-10" fill="none" stroke="' + ink + '" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>';
    } else if (kind === "talk") {
      body = '<rect x="7" y="10" width="34" height="22" rx="8" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M16 32l0 8 9-8z" fill="#fff" stroke="' + ink + '" stroke-width="3" stroke-linejoin="round"/>' +
        '<path d="M15 18h18M15 25h11" stroke="' + ink + '" stroke-width="3" stroke-linecap="round"/>';
    } else if (kind === "moon") {
      body = '<path d="M31 6a18 18 0 1 0 11 30A15 15 0 0 1 31 6z" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "heart") {
      body = '<path d="M24 40S8 30 8 19a8 8 0 0 1 16-3 8 8 0 0 1 16 3c0 11-16 21-16 21z" fill="#FF6B5A" stroke="' +
        ink + '" stroke-width="3" stroke-linejoin="round"/>';
    } else if (kind === "star") {
      body = '<path d="M24 6l5 12 13 1-10 9 3 13-11-7-11 7 3-13-10-9 13-1z" fill="#FFE24B" stroke="' +
        ink + '" stroke-width="3" stroke-linejoin="round"/>';
    } else {
      body = '<circle cx="24" cy="24" r="16" fill="#EBE3D2" stroke="' + ink + '" stroke-width="3"/>';
    }
    return '<svg class="wi" viewBox="0 0 48 48" width="' + s + '" height="' + s +
      '" aria-hidden="true" focusable="false">' + body + '</svg>';
  }

  function wiseScene(kind) {
    var ink = "#111";
    var inner = "";
    if (kind === "axis") {
      inner = '<rect width="320" height="150" fill="#F6F7F9"/>' +
        '<path d="M40 122h250M40 122V16" stroke="' + ink + '" stroke-width="3.5" stroke-linecap="round"/>' +
        '<path d="M282 122l-10-6v12z M40 16l-6 10h12z" fill="' + ink + '"/>' +
        '<rect x="52" y="76" width="72" height="40" rx="10" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="88" y="101" font-size="15" font-weight="800" text-anchor="middle" fill="#111">보조</text>' +
        '<rect x="130" y="56" width="72" height="40" rx="10" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="166" y="81" font-size="15" font-weight="800" text-anchor="middle" fill="#111">경계</text>' +
        '<rect x="206" y="30" width="72" height="40" rx="10" fill="#FF6B5A" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="242" y="55" font-size="15" font-weight="800" text-anchor="middle" fill="#111">대행</text>' +
        '<text x="150" y="142" font-size="13" font-weight="700" text-anchor="middle" fill="#6b7280">생각을 누가 했나</text>' +
        '<text x="14" y="70" font-size="13" font-weight="700" fill="#6b7280" transform="rotate(-90 14 70)">결과물</text>';
    } else if (kind === "steps3") {
      inner = '<rect width="320" height="120" fill="#F6F7F9"/>' +
        '<rect x="12" y="28" width="86" height="60" rx="14" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="55" y="64" font-size="15" font-weight="800" text-anchor="middle">내 생각</text>' +
        '<rect x="117" y="28" width="86" height="60" rx="14" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="160" y="64" font-size="15" font-weight="800" text-anchor="middle">AI 검토</text>' +
        '<rect x="222" y="28" width="86" height="60" rx="14" fill="#2B59E0" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="265" y="64" font-size="15" font-weight="800" text-anchor="middle" fill="#fff">내 말로</text>' +
        '<path d="M100 58h15M205 58h15" stroke="' + ink + '" stroke-width="4" stroke-linecap="round"/>';
    } else if (kind === "signal") {
      inner = '<rect width="320" height="120" fill="#F6F7F9"/>' +
        '<rect x="16" y="18" width="288" height="84" rx="18" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="70" cy="60" r="22" fill="#16a34a" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="130" cy="60" r="22" fill="#eab308" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="190" cy="60" r="22" fill="#ea580c" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="250" cy="60" r="22" fill="#dc2626" stroke="' + ink + '" stroke-width="3"/>';
    } else if (kind === "room") {
      inner = '<rect width="320" height="120" fill="#F6F7F9"/>' +
        '<rect x="16" y="26" width="120" height="68" rx="14" fill="#fff" stroke="' + ink + '" stroke-width="3"/>' +
        '<text x="76" y="58" font-size="14" font-weight="800" text-anchor="middle">방 코드</text>' +
        '<text x="76" y="80" font-size="20" font-weight="900" text-anchor="middle" fill="#2B59E0">482913</text>' +
        '<path d="M144 60h28" stroke="' + ink + '" stroke-width="4" stroke-linecap="round"/>' +
        '<path d="M166 52l10 8-10 8z" fill="' + ink + '"/>' +
        '<circle cx="212" cy="48" r="14" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M192 94c0-12 9-18 20-18s20 6 20 18z" fill="#00D45A" stroke="' + ink + '" stroke-width="3"/>' +
        '<circle cx="272" cy="48" r="14" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>' +
        '<path d="M252 94c0-12 9-18 20-18s20 6 20 18z" fill="#FFE24B" stroke="' + ink + '" stroke-width="3"/>';
    } else {
      inner = '<rect width="320" height="120" fill="#F6F7F9"/>';
    }
    var vb = kind === "axis" ? "0 0 320 150" : "0 0 320 120";
    return '<svg class="ws-scene" viewBox="' + vb + '" aria-hidden="true">' + inner + '</svg>';
  }
"""

CSS_EXTRA = u"""
#wise-app .wi{vertical-align:middle;margin-right:8px;flex:none}
#wise-app .ws-scene{display:block;width:100%;height:auto;border:2px solid var(--line);
border-radius:14px;background:#fff;margin:10px 0 4px}
#wise-app .chip .wi{margin-right:10px}
#wise-app .iconrow{display:flex;align-items:center;gap:8px}
"""
