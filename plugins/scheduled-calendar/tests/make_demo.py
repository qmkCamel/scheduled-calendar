"""Generate only synthetic data for UI testing; never reads the user's Codex data."""
import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('home',type=Path)
parser.add_argument('--language',choices=['en','zh-CN'],default='zh-CN')
args=parser.parse_args()
home=args.home.resolve()
today=datetime.now(timezone(timedelta(hours=8)))
names=['每日阅读摘要','产品灵感收集','开源项目更新','每周知识回顾','周末出行计划','项目发布检查','账单归档提醒','早间学习计划','周报草稿整理']
if args.language == 'en':
    names=['Daily reading digest','Product ideas','Open-source updates','Weekly learning review','Weekend plans','Release checklist','Bill archive reminder','Morning study','Weekly report draft']
prompt = 'Synthetic UI test task. This is only a calendar demo and will not run.' if args.language == 'en' else '这是一条虚构的界面测试任务，仅用于验证日历展示，不会被执行。'
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
    task=dict(id=f'demo-{i}',name=name,prompt=prompt,status='PAUSED' if i==7 else 'ACTIVE',rrule=rule+';BYSECOND=0',created_at=int((today-timedelta(days=100)).timestamp()*1000),updated_at=1,timezone='Asia/Shanghai',kind='heartbeat')
    p=home/'automations'/task['id']/'automation.toml';p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text('\n'.join(f'{k} = {json.dumps(v,ensure_ascii=False)}' for k,v in task.items()))
print(home)
