"""Generate only synthetic data for UI testing; never reads the user's Codex data."""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

home=Path(sys.argv[1]).resolve()
today=datetime.now(timezone(timedelta(hours=8)))
names=['每日阅读摘要','产品灵感收集','开源项目更新','每周知识回顾','周末出行计划','项目发布检查','账单归档提醒','早间学习计划','周报草稿整理']
rules=['FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=6;BYMINUTE=15',
       'FREQ=WEEKLY;BYDAY=MO,WE,SA;BYHOUR=20;BYMINUTE=30',
       'FREQ=WEEKLY;BYDAY=TU,FR;BYHOUR=10;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=WE;BYHOUR=18;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=TH;BYHOUR=8;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=MO;BYHOUR=10;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0',
       'FREQ=WEEKLY;BYDAY=FR;BYHOUR=17;BYMINUTE=0']
for i,(name,rule) in enumerate(zip(names,rules)):
    task=dict(id=f'demo-{i}',name=name,prompt='这是一条虚构的界面测试任务，仅用于验证日历展示，不会被执行。',status='PAUSED' if i==7 else 'ACTIVE',rrule=rule+';BYSECOND=0',created_at=int((today-timedelta(days=100)).timestamp()*1000),updated_at=1,timezone='Asia/Shanghai',kind='heartbeat')
    p=home/'automations'/task['id']/'automation.toml';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('\n'.join(f'{k} = {json.dumps(v,ensure_ascii=False)}' for k,v in task.items()))
print(home)
