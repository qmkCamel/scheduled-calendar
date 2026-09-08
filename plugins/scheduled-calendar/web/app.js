'use strict';
const $ = (selector) => document.querySelector(selector);
const el = (tag, cls, text) => { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; };
const state = { date: new Date(), mini: new Date(), view: 'week', filter: 'ACTIVE', search: '', data: null, request: 0 };
const weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
const statuses = { ACTIVE: '已开启', PAUSED: '已暂停', COMPLETED: '已完成', ARCHIVED: '已完成', UNKNOWN: '状态未知' };
const palette = [ ['#edf3e6','#dce8cf','#658151'], ['#eaf1f8','#d9e4ef','#5e7f9d'], ['#f3ecf5','#e8dbec','#9876a4'], ['#fcf2e6','#f0e3cb','#ad8852'], ['#e9f3f0','#d5e7e0','#548b79'] ];
const key = d => `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
const atMidnight = d => new Date(d.getFullYear(), d.getMonth(), d.getDate());
const addDays = (d,n) => new Date(d.getFullYear(), d.getMonth(), d.getDate()+n);
const weekStart = d => addDays(atMidnight(d), -((d.getDay()+6)%7));
const time = d => new Date(d).toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit',hour12:false});
const fullTime = d => d ? new Date(d).toLocaleString('zh-CN',{month:'long',day:'numeric',weekday:'short',hour:'2-digit',minute:'2-digit',hour12:false}) : '暂无记录';
const kindLabel = kind => ({scheduled:'调度器下一次',estimated:'周期预估',paused:'已暂停 · 原计划'}[kind] || '');
function color(node, task) { let hash=0; for(const c of task.id) hash=(hash*31+c.charCodeAt(0))>>>0; const p=palette[hash%palette.length]; ['--event-bg','--event-border','--event-ink'].forEach((v,i)=>node.style.setProperty(v,p[i])); }
function matches(task) { return (state.filter==='ALL' || task.status===state.filter || (state.filter==='COMPLETED' && task.status==='ARCHIVED')) && task.name.toLocaleLowerCase().includes(state.search.toLocaleLowerCase()); }
function tasks() { return (state.data?.tasks || []).filter(matches); }
function events() { const map = new Map(tasks().map(t=>[t.id,t])); return (state.data?.events || []).filter(e=>map.has(e.taskId)).map(e=>({...e,task:map.get(e.taskId),date:new Date(e.start)})); }
function range() { if(state.view==='month') { const start=weekStart(new Date(state.date.getFullYear(),state.date.getMonth(),1)); return [start,addDays(start,42)]; } const start=weekStart(state.date);return [start,addDays(start,state.view==='agenda'?14:7)]; }
function button(text, cls, action) { const b=el('button',cls,text);b.type='button';b.onclick=action;return b; }
function renderMini() {
  $('#mini-title').textContent=`${state.mini.getFullYear()}年 ${state.mini.getMonth()+1}月`;
  const start=weekStart(new Date(state.mini.getFullYear(),state.mini.getMonth(),1));
  const grid=$('#mini-grid');grid.replaceChildren();
  for(let i=0;i<42;i++) { const d=addDays(start,i);const b=button(d.getDate(),' ',()=>{state.date=d;renderMini();refresh();});b.setAttribute('aria-label',key(d));if(d.getMonth()!==state.mini.getMonth())b.classList.add('other');if(key(d)===key(state.date))b.classList.add('chosen');if(key(d)===key(new Date()))b.classList.add('is-today');grid.append(b); }
}
function renderOverview() {
  const all=state.data.tasks;
  for(const [selector,value] of [['active','ACTIVE'],['paused','PAUSED'],['completed','COMPLETED']]) $('#'+selector+'-count').textContent=all.filter(t=>t.status===value || (value==='COMPLETED'&&t.status==='ARCHIVED')).length;
  $('#all-count').textContent=all.length;
  const today=atMidnight(new Date()),start=weekStart(today),end=addDays(start,7);
  const map=new Map(all.map(t=>[t.id,t]));
  const activeEvents=state.data.events.filter(e=>map.get(e.taskId)?.status==='ACTIVE');
  $('#today-count').textContent=activeEvents.filter(e=>key(new Date(e.start))===key(today)).length;
  $('#week-count').textContent=activeEvents.filter(e=>new Date(e.start)>=start&&new Date(e.start)<end).length;
  const next=all.filter(t=>t.status==='ACTIVE'&&t.nextRun&&!t.overdue).sort((a,b)=>new Date(a.nextRun)-new Date(b.nextRun))[0];
  $('#next-title').textContent=next?next.name:'暂无后续任务';$('#next-time').textContent=next?`${fullTime(next.nextRun)} · ${kindLabel(next.nextKind)}`:'持续监控与待核对任务请见日历上方';
  $('#source-text').textContent=`${all.length} 个本地任务 · 每 30 秒刷新`;
  $('.source-card strong').textContent=state.data.demo?'演示数据 · 非真实任务':'本地任务已连接';
  $('#zone').textContent=`◷ ${Intl.DateTimeFormat().resolvedOptions().timeZone}`;
  $('#sync-time').textContent=`更新于 ${time(state.data.syncedAt)}`;
}
function renderLanes() { const lane=$('#monitor-lane');lane.replaceChildren();const attention=tasks().filter(t=>t.monitor||t.overdue||t.exhausted||t.notes.length);lane.hidden=!attention.length;if(!attention.length)return;lane.append(el('span','', '持续监控 / 待核对'));for(const t of attention) lane.append(button(`${t.overdue?'◷ ':t.monitor?'◉ ':'! '}${t.name}`, '',()=>details(t))); }
function eventButton(event) { const b=button('',`calendar-event ${event.kind==='paused'?'paused':''}`,()=>details(event.task,event));color(b,event.task);b.append(el('span','event-time',time(event.start)+(event.kind==='scheduled'?' · ●':event.kind==='paused'?' · 暂停':' · ○')),el('span','event-title',event.task.name));b.setAttribute('aria-label',`${fullTime(event.start)} ${event.task.name} ${kindLabel(event.kind)}`);b.title=`${event.task.name}\n${fullTime(event.start)} · ${kindLabel(event.kind)}`;return b; }
function layoutDay(items) {
  // Minimum visual block height is 58 minutes; allocate lanes for overlapping visual blocks.
  const sorted=items.map(e=>({...e,minute:e.date.getHours()*60+e.date.getMinutes()})).sort((a,b)=>a.minute-b.minute);
  let group=[],until=0;const groups=[];
  for(const e of sorted) {if(group.length&&e.minute>=until){groups.push(group);group=[];until=0;}group.push(e);until=Math.max(until,e.minute+58);}if(group.length)groups.push(group);
  for(const g of groups) {const ends=[];for(const e of g){let lane=ends.findIndex(end=>end<=e.minute);if(lane===-1)lane=ends.length;ends[lane]=e.minute+58;e.lane=lane;}for(const e of g)e.lanes=ends.length;}
  return sorted;
}
function renderWeek(container, list) {
  const start=weekStart(state.date),today=key(new Date());
  const head=el('div','week-header');head.append(el('span','time-zone-mini','24H'));
  const scroll=el('div','week-scroll');const body=el('div','week-body');const ruler=el('div','time-ruler');
  for(let h=0;h<24;h++){const label=el('span','hour-label',`${String(h).padStart(2,'0')}:00`);label.style.top=`${h*60+2}px`;ruler.append(label);}body.append(ruler);
  for(let i=0;i<7;i++){const d=addDays(start,i),isToday=key(d)===today;const heading=el('div','day-heading'+(isToday?' today':''));heading.append(el('span','',weekdays[i]),button(d.getDate(),'',()=>{state.date=d;state.view='agenda';refresh();}));head.append(heading);
    const column=el('div','day-column'+(isToday?' today':''));
    for(const e of layoutDay(list.filter(e=>key(e.date)===key(d)))) {const b=eventButton(e);b.style.top=`${e.minute}px`;b.style.height=`${Math.min(55,1440-e.minute)}px`;b.style.left=`calc(${e.lane*100/e.lanes}% + 4px)`;b.style.width=`calc(${100/e.lanes}% - 8px)`;column.append(b);}
    if(isToday){const now=new Date();const line=el('div','now-line');line.style.top=`${now.getHours()*60+now.getMinutes()}px`;column.append(line);}body.append(column);
  }
  scroll.append(body);container.append(head,scroll);
  requestAnimationFrame(()=>{scroll.scrollTop=state.scrollTop??300;});
}
function renderMonth(container,list) {
  const head=el('div','month-header');weekdays.forEach(d=>head.append(el('span','',d)));const grid=el('div','month-grid');const [start]=range();
  for(let i=0;i<42;i++){const d=addDays(start,i),dayEvents=list.filter(e=>key(e.date)===key(d));const cell=el('div','month-day'+(d.getMonth()!==state.date.getMonth()?' other':'')+(key(d)===key(new Date())?' today':''));cell.append(button(d.getDate(),'month-date',()=>openDay(d)));
    dayEvents.slice(0,3).forEach(e=>{const b=button(`${time(e.start)} ${e.task.name}`,'month-event',()=>details(e.task,e));color(b,e.task);b.title=e.task.name;cell.append(b);});
    if(dayEvents.length>3)cell.append(button(`+${dayEvents.length-3} 项安排`,'more',()=>openDay(d)));grid.append(cell);}
  container.append(head,grid);
}
function openDay(d){state.date=d;state.view='agenda';state.agendaDay=key(d);refresh();}
function renderAgenda(container,list) {
  const area=el('div','agenda');const [start,end]=range();const visible=list.filter(e=>e.date>=start&&e.date<end&&(!state.agendaDay||key(e.date)===state.agendaDay)).sort((a,b)=>a.date-b.date);
  if(!visible.length){const empty=el('div','empty','这段时间没有安排');empty.append(el('small','','可以切换日期，或查看其他任务状态。'));area.append(empty);}
  let last='',group;
  for(const e of visible){const day=key(e.date);if(day!==last){group=el('section','agenda-day');group.append(el('h3','',e.date.toLocaleDateString('zh-CN',{month:'long',day:'numeric',weekday:'long'})));area.append(group);last=day;}
    const row=button('','agenda-row',()=>details(e.task,e));row.append(el('time','',time(e.start)),el('span','',e.task.name),el('small','',kindLabel(e.kind)));group.append(row);}
  const absent=tasks().filter(t=>!visible.some(e=>e.taskId===t.id));
  if(absent.length){const section=el('section','agenda-day');section.append(el('h3','','其他任务 · 本范围无触发日期'));for(const t of absent){const b=button('','task-record',()=>details(t));b.append(el('span','',t.name),el('small','',`${statuses[t.status]||t.status} · ${t.monitor?'持续监控':t.exhausted?'周期已结束，待核对':'本范围无计划'}`));section.append(b);}area.append(section);}
  container.append(area);
}
function render() {
  renderMini();if(!state.data)return;renderOverview();renderLanes();
  $('#mobile-filter').value=state.filter;
  document.querySelectorAll('[data-view]').forEach(b=>{b.classList.toggle('selected',b.dataset.view===state.view);b.setAttribute('aria-pressed',b.dataset.view===state.view);});
  document.querySelectorAll('[data-filter]').forEach(b=>{b.classList.toggle('selected',b.dataset.filter===state.filter);b.setAttribute('aria-pressed',b.dataset.filter===state.filter);});
  const [start,end]=range();
  $('#range-title').textContent=state.view==='month'?`${state.date.getFullYear()}年 ${state.date.getMonth()+1}月`:state.agendaDay?`${state.date.getMonth()+1}月${state.date.getDate()}日`:`${start.getMonth()+1}月${start.getDate()}日 — ${addDays(end,-1).getMonth()+1}月${addDays(end,-1).getDate()}日`;
  $('#week-number').textContent=`${state.date.getFullYear()}`;
  const container=$('#calendar');container.replaceChildren();const list=events();
  if(state.view==='week')renderWeek(container,list);else if(state.view==='month')renderMonth(container,list);else renderAgenda(container,list);
  if(!tasks().length&&state.view!=='agenda'){const empty=el('div','empty','没有匹配的任务');empty.append(el('small','','试试其他关键词或任务状态。'));container.append(empty);}
}
async function refresh() {
  const request=++state.request;const existing=$('.week-scroll');if(existing)state.scrollTop=existing.scrollTop;
  $('#refresh').disabled=true;
  let [start,end]=range();const current=weekStart(new Date());
  // One request for visible dates; current-week metrics are separately refreshed for distant months.
  try {
    const fetchRange=async(s,e)=>{const params=new URLSearchParams({start:s.toISOString(),end:e.toISOString()});const response=await fetch('/api/calendar?'+params,{headers:{'X-Calendar-Token':$('meta[name="calendar-token"]').content}});if(!response.ok)throw Error('读取失败，请点击刷新重试。');return response.json();};
    const data=await fetchRange(start,end);
    if(start>current||end<addDays(current,7)){const currentData=await fetchRange(current,addDays(current,7));const seen=new Set(data.events.map(e=>`${e.taskId}|${e.start}|${e.kind}`));for(const e of currentData.events){const id=`${e.taskId}|${e.start}|${e.kind}`;if(!seen.has(id))data.events.push(e);}}
    if(request!==state.request)return;state.data=data;
    const notices=[...(data.demo?['演示数据 · 以下为虚构任务，不会执行。']:[]),...data.warnings];$('#notice').hidden=!notices.length;$('#notice').textContent=notices.join('\n');render();
  } catch(error) {if(request!==state.request)return;$('#notice').hidden=false;$('#notice').textContent=`同步失败：${error.message}${state.data?' 当前保留上次快照。':''}`;if(!state.data)$('#calendar').replaceChildren(el('div','empty','暂时无法读取任务'));}
  finally{if(request===state.request)$('#refresh').disabled=false;}
}
function details(task,event) {
  const content=$('#details-content');content.replaceChildren();content.append(el('div','detail-kicker','SCHEDULED TASK · LOCAL'),el('h2','detail-title',task.name));
  const meta=el('dl','detail-meta');const fields=[['状态',statuses[task.status]||task.status],['所选日期',event?`${fullTime(event.start)} · ${kindLabel(event.kind)}`:'任务概览'],['下一次运行',task.nextRun?`${fullTime(task.nextRun)} · ${kindLabel(task.nextKind)}`:task.status==='PAUSED'?'暂停中，不会运行':'无已知时间'],['最近运行',fullTime(task.lastRun)],['规则时区',`${task.timezone}${task.timezoneAssumed?'（按本机推定）':''}`],['任务类型',task.kind==='heartbeat'?'回到原任务继续':'独立定时任务']];
  for(const [k,v] of fields)meta.append(el('dt','',k),el('dd','',v));content.append(meta);
  if(task.notes.length)content.append(el('p','detail-warning',task.notes.join('\n')));
  content.append(el('h3','detail-note','任务内容'),el('div','detail-prompt',task.prompt||'无任务说明'));
  if(task.anchorAssumed)content.append(el('p','detail-note','周期未提供明确起点，按任务创建时间估算。有限次数、间隔周期请以 Codex 调度器为准。'));
  content.append(el('p','detail-note','日历只读展示。要调整时间、暂停或继续任务，可复制下方指令发给 Codex。'));
  const copy=button('复制任务管理指令','copy-button',async()=>{const instruction=`请查看并帮我管理定时任务「${task.name}」（id: ${task.id}），先展示当前安排。`;try{await navigator.clipboard.writeText(instruction);copy.textContent='已复制，粘贴给 Codex';}catch{content.append(el('p','detail-prompt',instruction));copy.textContent='请复制上方指令';}});content.append(copy);
  $('#details').showModal();
}
$('#close-details').onclick=()=>$('#details').close();
$('#details').addEventListener('click',e=>{if(e.target===$('#details')){const r=$('#details').getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$('#details').close();}});
$('#refresh').onclick=refresh;
$('#search').addEventListener('input',e=>{state.search=e.target.value;render();});
$('#filters').addEventListener('click',e=>{const b=e.target.closest('[data-filter]');if(b){state.filter=b.dataset.filter;if(state.filter==='COMPLETED')state.view='agenda';render();}});
$('#mobile-filter').addEventListener('change',e=>{state.filter=e.target.value;if(state.filter==='COMPLETED')state.view='agenda';render();});
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{state.view=b.dataset.view;state.agendaDay=null;state.scrollTop=300;refresh();});
function navigate(delta){state.agendaDay=null;state.date=state.view==='month'?new Date(state.date.getFullYear(),state.date.getMonth()+delta,1):addDays(state.date,delta*(state.view==='agenda'?14:7));state.mini=new Date(state.date);refresh();}
$('#prev').onclick=()=>navigate(-1);$('#next').onclick=()=>navigate(1);
$('#today').onclick=()=>{state.date=new Date();state.mini=new Date();state.agendaDay=null;state.scrollTop=Math.max(0,(new Date().getHours()-2)*60);refresh();};
$('#mini-prev').onclick=()=>{state.mini=new Date(state.mini.getFullYear(),state.mini.getMonth()-1,1);renderMini();};$('#mini-next').onclick=()=>{state.mini=new Date(state.mini.getFullYear(),state.mini.getMonth()+1,1);renderMini();};
$('#calendar-nav').onclick=()=>{state.view='week';state.date=new Date();state.agendaDay=null;refresh();};
renderMini();refresh();setInterval(()=>{if(!document.hidden&&!$('#details').open)refresh();},30000);
