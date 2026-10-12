/* test_eb.js — 錯字本 (SRS / 滾動過關) 行為測試
   用法：node test_eb.js
   從產出的課文頁抽出 <script>，在假瀏覽器環境執行後驗證錯字本邏輯。 */
'use strict';
const fs = require('fs');
const path = require('path');

const PAGE = path.join(__dirname, '..', 'docs', '01-new-term-at-school.html');

let pass = 0, fail = 0;
function ok(cond, msg) {
  if (cond) { pass++; console.log('  ok   ' + msg); }
  else { fail++; console.log('  FAIL ' + msg); }
}

/* ---- 假瀏覽器 ---- */
const store = {};
function makeDoc() {
  const els = {};
  function el(id) {
    if (els[id]) return els[id];
    const e = {
      id, textContent: '', innerHTML: '', value: '', hidden: false,
      style: {}, className: '',
      _attrs: {},
      classList: {
        _s: new Set(),
        add(c) { this._s.add(c); }, remove(c) { this._s.delete(c); },
        contains(c) { return this._s.has(c); }
      },
      setAttribute(k, v) { this._attrs[k] = String(v); },
      getAttribute(k) { return k in this._attrs ? this._attrs[k] : null; },
      hasAttribute(k) { return k in this._attrs; },
      removeAttribute(k) { delete this._attrs[k]; },
      addEventListener() {}, contains() { return false; },
      querySelector() { return null; }, querySelectorAll() { return []; },
      focus() {}, closest() { return null; }
    };
    els[id] = e;
    return e;
  }
  return {
    _els: els,
    getElementById: (id) => el(id),
    querySelector: () => null,
    querySelectorAll: () => [],
    addEventListener() {},
    createElement: () => ({ set textContent(v) { this._t = v; }, get innerHTML() { return String(this._t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;'); } })
  };
}

const localStorage = {
  _d: {},
  getItem(k) { return k in this._d ? this._d[k] : null; },
  setItem(k, v) { this._d[k] = String(v); },
  removeItem(k) { delete this._d[k]; }
};

const doc = makeDoc();
const console_ = console;

function loadPage() {
  const html = fs.readFileSync(PAGE, 'utf8');
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
  const main = scripts[0];
  if (!/errbook_v1/.test(main)) throw new Error('錯字本程式碼不在第一個 script 內 (scripts=' + scripts.length + ')');
  const synth = { speak() {}, cancel() {}, resume() {}, getVoices() { return []; }, onvoiceschanged: null };
  const sandbox = {
    document: doc, localStorage, window: { speechSynthesis: synth, addEventListener() {} },
    speechSynthesis: synth, console: console_,
    SpeechSynthesisUtterance: function () {},
    alert() {}, confirm() { return true; },
    setTimeout, clearTimeout, Date, Math, JSON, parseInt, parseFloat,
    String, Number, Array, Object, RegExp, isNaN
  };
  const fn = new Function(...Object.keys(sandbox), main + '\n;return {ebAdd, ebGradeRec, ebLoad, ebDue, ebNorm, ebCatchTyped, ebSave, EB_PASS, ebRender, ebStart, ebGrade, ebShow, ebAddManual, ebResetSession};');
  return fn(...Object.values(sandbox));
}

console.log('== 錯字本 (SRS) ==');

let api;
try {
  api = loadPage();
  ok(true, '頁面 script 可在假環境執行');
} catch (e) {
  ok(false, '頁面 script 執行失敗: ' + e.message);
  console.log('\n' + pass + ' passed, ' + fail + ' failed');
  process.exit(1);
}

const { ebAdd, ebGradeRec, ebLoad, ebDue, ebNorm, ebCatchTyped, ebSave, EB_PASS } = api;

/* --- 基本 --- */
ok(typeof ebAdd === 'function', 'ebAdd 存在');
ok(typeof ebGradeRec === 'function', 'ebGradeRec 存在');
ok(EB_PASS === 3, '滾動過關門檻為連續答對 3 次');

localStorage.removeItem('errbook_v1');

/* --- 加入 --- */
const r1 = ebAdd('stomachache', 'she had a stomachache', '肚子痛');
ok(r1 && r1.w === 'stomachache', 'ebAdd 收錄單字');
ok(r1.n === 1, '首次收錄 n=1');
ok(r1.ok === 0, '連續答對歸零');
ok(r1.g === false, '尚未過關');
ok(r1.due <= Date.now(), '剛加入即到期（今天就要複習）');

/* --- 重複加入 → 累加、拉回今天 --- */
const r2 = ebAdd('stomachache', 'she had a stomachache', '');
ok(r2.n === 2, '重複加入累加次數 n=2');
ok(ebLoad().length === 1, '同一字不會重複建檔');

/* --- 忘了 → 間隔回今天、ease 下降 --- */
const before = ebLoad()[0].e;
const rec = grade(false);
ok(rec.ok === 0, '答錯後連續答對歸零');
ok(rec.due <= Date.now(), '答錯後今天就到期');
ok(rec.e < before, '答錯後難度係數下降');
ok(rec.g === false, '答錯後過關狀態清除');

/* --- 記得 → 短間隔滾動，未滿 3 次不算過關 --- */
// 與 UI 一致：grade 之後要存檔（ebGradeRec 只計算，ebGrade 負責 ebSave）
function grade(ok) {
  const l = ebLoad();
  ebGradeRec(l[0], ok);
  ebSave(l);
  return ebLoad()[0];
}

const a = grade(true);
ok(a.ok === 1, '答對後連對 =1');
ok(a.g === false, '連對 1 次尚未過關');
ok(a.due > Date.now() + 0.9 * 86400000, '連對 1 次 → 間隔 1 天');

const b = grade(true);
ok(b.ok === 2, '連對 =2');
ok(b.g === false, '連對 2 次尚未過關');
ok(b.due > Date.now() + 1.9 * 86400000, '連對 2 次 → 間隔 2 天');

const c = grade(true);
ok(c.ok === 3, '連對 =3');
ok(c.g === true, '連對 3 次 → 滾動過關');
ok(c.i >= 7, '過關後間隔拉長到 ≥7 天');
ok(c.due > Date.now() + 6.9 * 86400000, '過關後到期時間在 7 天後');

/* --- 過關後答錯 → 退回未過關、今天再出現 --- */
const d = grade(false);
ok(d.g === false, '過關後答錯退回未過關');
ok(d.ok === 0, '過關後答錯連對歸零');
ok(d.due <= Date.now(), '過關後答錯今天再到期');

/* --- ebDue 篩選 --- */
localStorage.removeItem('errbook_v1');
ebAdd('alpha', 'x alpha', '');
ebAdd('beta', 'x beta', '');
let list = ebLoad();
list[1].due = Date.now() + 10 * 86400000;   // beta 明天以後
ebSave(list);
ok(ebDue().length === 1, 'ebDue 只回傳到期的字');
ok(ebDue()[0].w === 'alpha', '到期的是 alpha');

/* --- ebNorm 寬鬆正規化 --- */
ok(ebNorm("Don't!") === "don't", 'ebNorm 保留撇號、去標點大小寫');
ok(ebNorm('  Hello,  ') === 'hello', 'ebNorm 去空白與標點');

/* --- ebCatchTyped 抓打錯的字 --- */
localStorage.removeItem('errbook_v1');
const typed = ['our', 'new', 'term', 'start', 'next', 'monday'];
const target = ['our', 'new', 'term', 'starts', 'next', 'monday'];
const bad = ebCatchTyped(typed, target, 'Our new term starts next Monday.');
ok(bad.length === 1, '逐字比對抓出 1 個錯字');
ok(bad[0].target === 'starts', '錯字的正解是 starts');
ok(ebLoad().length === 1, '錯字已收進錯字本');
ok(ebLoad()[0].w === 'starts', '收錄的是正解字');
ok(ebLoad()[0].ctx.indexOf('starts') >= 0, '保留原始句子做為脈絡');

/* 全對不收 */
localStorage.removeItem('errbook_v1');
ok(ebCatchTyped(target, target, 's').length === 0, '全對時不收錄');
ok(ebLoad().length === 0, '全對時錯字本仍為空');

/* 大小寫／標點寬鬆 */
localStorage.removeItem('errbook_v1');
ok(ebCatchTyped(['Starts,'], ['starts'], 's').length === 0, '大小寫與標點差異不算錯');

/* --- UI 渲染不噴錯 --- */
try {
  api.ebRender();
  ok(true, 'ebRender() 可執行');
} catch (e) {
  ok(false, 'ebRender() 例外: ' + e.message);
}
try {
  api.ebStart();
  api.ebShow();
  api.ebGrade(true);
  ok(true, 'ebStart/ebShow/ebGrade 可執行');
} catch (e) {
  ok(false, '複習流程例外: ' + e.message);
}
try {
  api.ebAddManual && api.ebAddManual();
  api.ebResetSession();
  ok(true, '手動加入與重設流程可執行');
} catch (e) {
  ok(false, '手動加入流程例外: ' + e.message);
}

console.log('\nerror notebook: ' + pass + ' passed, ' + fail + ' failed');
process.exit(fail ? 1 : 0);
