'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const web = path.join(__dirname, '../web');
const i18n = require(path.join(web,'i18n.js'));

test('browser primary language and explicit choices have predictable fallbacks', () => {
  assert.equal(i18n.resolve('auto',['zh-TW','en-US']),'zh-CN');
  assert.equal(i18n.resolve('auto',['en-GB','zh-CN']),'en');
  assert.equal(i18n.resolve('auto',['fr-FR','zh-CN']),'en');
  assert.equal(i18n.resolve('invalid',[]),'en');
  assert.equal(i18n.resolve('en',['zh-CN']),'en');
  assert.equal(i18n.resolve('zh-CN',['en-US']),'zh-CN');
});

test('interpolated user text stays verbatim, including braces and replacement tokens', () => {
  const name='我的任务 {id} $& <script>';
  const result=i18n.translate('en','请查看并帮我管理定时任务「{name}」（id: {id}），先展示当前安排。',{name,id:'demo-1'});
  assert.ok(result.includes(name));
  assert.ok(result.includes('(id: demo-1)'));
  assert.equal(i18n.translate('zh-CN','已暂停'),'已暂停');
});

test('system warnings translate without translating embedded task names', () => {
  assert.equal(i18n.systemMessage('en','任务「中文任务」需核对时间配置。'),'Check the time configuration for task “中文任务”.');
  assert.equal(i18n.systemMessage('en','无法解析此任务的时间或周期：未知时区'),"Could not parse this task's time or recurrence: Unknown time zone");
  assert.match(i18n.systemMessage('en','无法读取调度状态（ValueError）；仅展示配置预估。'),/ValueError/);
  assert.equal(i18n.systemMessage('zh-CN','本机时区'),'本机时区');
  assert.equal(i18n.systemMessage('en','future diagnostic'),'future diagnostic');
});

test('all declared static and direct dynamic UI strings have English translations', () => {
  const html=fs.readFileSync(path.join(web,'index.html'),'utf8');
  const app=fs.readFileSync(path.join(web,'app.js'),'utf8');
  const keys=[...html.matchAll(/data-i18n(?:-aria|-placeholder)?="([^"]+)"/g)].map(m=>m[1]);
  keys.push(...[...app.matchAll(/\bt\(['"]([^'"\n]+)['"]/g)].map(m=>m[1]));
  for(const key of keys) assert.ok(Object.hasOwn(i18n.english,key),key);
});

function boot(storage) {
  const nodes=new Map();
  function node(){return {dataset:{},classList:{add(){},toggle(){}},style:{},children:[],value:'',textContent:'',open:false,append(...children){this.children.push(...children);},replaceChildren(...children){this.children=children;},setAttribute(){},addEventListener(event,fn){this[event]=fn;}};}
  const document={documentElement:{lang:''},hidden:false,title:'',querySelector(selector){if(selector==='.week-scroll')return null;if(!nodes.has(selector))nodes.set(selector,node());return nodes.get(selector);},querySelectorAll(){return [];},createElement:node};
  const context=vm.createContext({document,window:{addEventListener(){}},navigator:{languages:['zh-CN']},localStorage:storage,Date,Intl,URLSearchParams,setInterval(){},requestAnimationFrame(){},fetch(){return new Promise(()=>{});}});
  vm.runInContext(fs.readFileSync(path.join(web,'i18n.js'),'utf8'),context);
  vm.runInContext(fs.readFileSync(path.join(web,'app.js'),'utf8'),context);
  return {document,nodes};
}

test('blocked browser storage does not prevent startup or manual language switching', () => {
  const {document,nodes}=boot({getItem(){throw Error('blocked');},setItem(){throw Error('blocked');}});
  assert.equal(document.documentElement.lang,'zh-CN');
  nodes.get('#language').change({target:{value:'en'}});
  assert.equal(document.documentElement.lang,'en');
  assert.equal(document.title,'Scheduled Calendar · Codex');
});

test('saved preference overrides the browser and manual changes are persisted', () => {
  const writes=[];
  const {document,nodes}=boot({getItem(){return 'en';},setItem(...args){writes.push(args);}});
  assert.equal(document.documentElement.lang,'en');
  nodes.get('#language').change({target:{value:'zh-CN'}});
  assert.equal(document.documentElement.lang,'zh-CN');
  assert.deepEqual(writes,[['scheduled-calendar-language','zh-CN']]);
});
