
const fs = require('fs');
const path = require('path');
const DIR = path.resolve(__dirname, '..', 'docs');
const files = fs.readdirSync(DIR).filter(f => f.endsWith('.html') && f !== 'index.html');
const NL = '\\r?\\n';

let allOk = true;
for (const f of files) {
  const html = fs.readFileSync(path.join(DIR, f), 'utf8');
  const problems = [];

  // 1) real JS eval of every speakParagraph([...]) array literal
  const re = new RegExp('speakParagraph\\(\\[([\\s\\S]*?)\\]\\)', 'g');
  let m, arrays = [];
  while ((m = re.exec(html)) !== null) {
    let arr;
    try { arr = eval('[' + m[1] + ']'); }
    catch (e) { problems.push('JS syntax error: ' + e.message); continue; }
    if (!Array.isArray(arr)) { problems.push('not an array'); continue; }
    if (arr.some(x => typeof x !== 'string' || !x.trim())) problems.push('non-string/empty item');
    arrays.push(arr);
  }
  if (arrays.length !== 3) problems.push('expected 3 paragraph arrays, got ' + arrays.length);

  // 2) rendered sentence-text must equal the JS array contents (tags stripped)
  const blocks = html.split('<div class="paragraph-container">').slice(1);
  if (blocks.length !== 3) problems.push('expected 3 paragraph containers, got ' + blocks.length);
  blocks.forEach((b, i) => {
    const rx = new RegExp('<div class="sentence-text">' + NL + '([\\s\\S]*?)' + NL + '        <\\/div>', 'g');
    const texts = [...b.matchAll(rx)].map(x => x[1].replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim());
    const arr = arrays[i] || [];
    if (texts.length !== arr.length) { problems.push('P' + (i+1) + ' count ' + texts.length + '/' + arr.length); return; }
    for (let k = 0; k < texts.length; k++) {
      if (texts[k] !== arr[k].replace(/\s+/g, ' ').trim())
        problems.push('P' + (i+1) + 'S' + (k+1) + ':\n      HTML=' + texts[k] + '\n      JS  =' + arr[k]);
    }
  });

  // 3) popups
  const prx = new RegExp('sentence-grammar-pop">' + NL + '          <strong>[\\s\\S]*?<\\/strong><br>' + NL + '          ([\\s\\S]*?)' + NL + '        <\\/div>', 'g');
  const pops = [...html.matchAll(prx)].map(x => x[1]);
  const blockTotal = (html.match(/class="sentence-block"/g) || []).length;
  if (pops.length !== blockTotal) problems.push('popup count ' + pops.length + '/' + blockTotal);
  pops.forEach((p, i) => {
    if (p.length < 80) problems.push('popup ' + (i+1) + ' too short (' + p.length + ')');
    if (p.includes('</li>')) problems.push('popup ' + (i+1) + ' stray </li>');
    if (!/1\./.test(p) || !/2\./.test(p)) problems.push('popup ' + (i+1) + ' missing numbered points');
  });

  // 4) w-tap spans all inside sentence-text
  const tapAll = (html.match(/class="w-tap/g) || []).length;
  const tapIn = blocks.join('').match(/class="w-tap/g) || [];
  if (tapAll !== tapIn.length) problems.push('w-tap outside sentences: ' + (tapAll - tapIn.length));
  if (tapAll < 9) problems.push('too few highlighted words: ' + tapAll);

  // 5) attribution + index link
  if (!html.includes('cambridgeenglish.org/Images/506886-a2-key-2020-vocabulary-list.pdf')) problems.push('missing PDF citation');
  if (!html.includes('108')) problems.push('missing 108 reference');
  if (!html.includes('href="index.html"')) problems.push('missing index link');

  // 6) script functions
  ['function speakText', 'function speakParagraph', 'function populateVoiceList', 'function updateRateLabel']
    .forEach(fn => { if (!html.includes(fn)) problems.push('missing ' + fn); });

  const ok = problems.length === 0;
  allOk = allOk && ok;
  console.log((ok ? 'OK   ' : 'FAIL ') + f.padEnd(36) +
    ' blocks=' + blockTotal + ' pops=' + pops.length + ' taps=' + tapAll +
    (problems.length ? '\n  - ' + problems.join('\n  - ') : ''));
}
console.log('\nALL LESSONS PASS: ' + allOk);
