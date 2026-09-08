import json
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from calendar_data import calendar_payload, read_tasks

UTC = timezone.utc
def dt(s): return datetime.fromisoformat(s.replace('Z', '+00:00'))
def ms(s): return int(dt(s).timestamp()*1000)


class CalendarTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.home = Path(self.temp.name)
        self.start = dt('2026-09-07T00:00:00+08:00')
        self.end = self.start+timedelta(days=7)
        self.now = dt('2026-09-08T08:00:00+08:00')

    def tearDown(self): self.temp.cleanup()

    def task(self, id='one', **overrides):
        row = dict(id=id, name='测试任务', prompt='<script>do not execute</script>', status='ACTIVE',
                   rrule='FREQ=WEEKLY;BYDAY=MO,WE;BYHOUR=10;BYMINUTE=0;BYSECOND=0',
                   created_at=ms('2026-09-01T09:00:00+08:00'), updated_at=1,
                   kind='heartbeat', timezone='Asia/Shanghai')
        row.update(overrides)
        p=self.home/'automations'/id/'automation.toml';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text('\n'.join(f'{k} = {json.dumps(v,ensure_ascii=False)}' for k,v in row.items()))
        return row

    def database(self, rows):
        p=self.home/'sqlite'/'codex-dev.db';p.parent.mkdir(exist_ok=True)
        with closing(sqlite3.connect(p)) as c:
            c.execute('CREATE TABLE automations (id TEXT PRIMARY KEY, name TEXT, status TEXT, rrule TEXT, created_at INTEGER, updated_at INTEGER, next_run_at INTEGER, last_run_at INTEGER)')
            for r in rows:
                keys=[k for k in r if k in ('id','name','status','rrule','created_at','updated_at','next_run_at','last_run_at')]
                c.execute('INSERT INTO automations ('+','.join(keys)+') VALUES ('+','.join('?' for k in keys)+')',[r[k] for k in keys])
            c.commit()

    def payload(self): return calendar_payload(self.home,self.start,self.end,self.now)

    def test_weekly_local_time(self):
        self.task();data=self.payload()
        self.assertEqual([e['start'] for e in data['events']],['2026-09-07T10:00:00+08:00','2026-09-09T10:00:00+08:00'])
        self.assertFalse(data['coverage']['cloud'])

    def test_count_never_restarts_each_month(self):
        self.task(rrule='FREQ=DAILY;COUNT=2;BYHOUR=10;BYMINUTE=0;BYSECOND=0')
        data=self.payload();self.assertEqual(data['events'],[]);self.assertTrue(data['tasks'][0]['exhausted'])

    def test_one_off_scheduler_survives_expired_rule(self):
        row=self.task(rrule='FREQ=YEARLY;COUNT=1;BYMONTH=9;BYMONTHDAY=2;BYHOUR=10;BYMINUTE=0;BYSECOND=0')
        self.database([{**row,'next_run_at':ms('2026-09-08T09:00:00+08:00')}])
        data=self.payload();self.assertEqual(len(data['events']),1);self.assertEqual(data['events'][0]['kind'],'scheduled')

    def test_paused_has_no_next_run(self):
        row=self.task(status='PAUSED');self.database([{**row,'next_run_at':ms('2026-09-09T10:00:00+08:00')}])
        data=self.payload();self.assertIsNone(data['tasks'][0]['nextRun']);self.assertTrue(all(e['kind']=='paused' for e in data['events']))

    def test_completed_never_generates_events(self):
        self.task(status='COMPLETED');data=self.payload();self.assertEqual(data['events'],[]);self.assertEqual(data['tasks'][0]['status'],'COMPLETED')

    def test_newer_file_does_not_reuse_stale_db_next(self):
        row=self.task(updated_at=10);self.database([{**row,'updated_at':1,'status':'PAUSED','next_run_at':ms('2026-09-08T09:00:00+08:00')}])
        data=self.payload();self.assertEqual(data['tasks'][0]['status'],'ACTIVE');self.assertEqual(data['tasks'][0]['nextKind'],'estimated')

    def test_newer_db_configuration_wins(self):
        row=self.task();self.database([{**row,'updated_at':10,'status':'PAUSED'}]);self.assertEqual(self.payload()['tasks'][0]['status'],'PAUSED')

    def test_bad_toml_does_not_hide_good_task(self):
        self.task();p=self.home/'automations/bad/automation.toml';p.parent.mkdir();p.write_text('not toml')
        data=self.payload();self.assertEqual(len(data['tasks']),1);self.assertTrue(any('bad' in w for w in data['warnings']))

    def test_unknown_rule_is_visible_error(self):
        self.task(rrule='FREQ=NOTREAL');data=self.payload();self.assertTrue(data['warnings']);self.assertTrue(data['tasks'][0]['notes'])

    def test_wrong_toml_field_type_does_not_hide_other_tasks(self):
        self.task();self.task(id='bad',updated_at='not a timestamp')
        data=self.payload();self.assertEqual(len(data['tasks']),1);self.assertTrue(any('bad' in w for w in data['warnings']))

    def test_null_database_updated_at_does_not_crash(self):
        row=self.task();self.database([{**row,'updated_at':None}])
        self.assertEqual(len(self.payload()['tasks']),1)

    def test_wrong_database_field_type_does_not_hide_file(self):
        row=self.task();self.database([{**row,'updated_at':'not a timestamp'}])
        data=self.payload();self.assertEqual(len(data['tasks']),1);self.assertTrue(any('不兼容' in w for w in data['warnings']))

    def test_minute_monitor_does_not_flood_calendar(self):
        self.task(rrule='FREQ=MINUTELY;INTERVAL=5',created_at=ms('2020-01-01T00:00:00Z'))
        data=self.payload();self.assertTrue(data['tasks'][0]['monitor']);self.assertEqual(data['events'],[])

    def test_missing_database_is_explicit_degradation(self):
        self.task();data=self.payload();self.assertFalse(data['coverage']['scheduler']);self.assertTrue(data['warnings'])

    def test_scheduler_jitter_replaces_only_one_daily_slot(self):
        row=self.task(rrule='FREQ=DAILY;BYHOUR=9,18;BYMINUTE=0;BYSECOND=0')
        self.database([{**row,'next_run_at':ms('2026-09-08T09:01:30+08:00')}])
        data=self.payload();day=[e for e in data['events'] if dt(e['start']).astimezone(timezone(timedelta(hours=8))).date()==self.now.date()]
        self.assertEqual(len(day),2);self.assertEqual(sum(e['kind']=='scheduled' for e in day),1)

    def test_interval_keeps_original_anchor(self):
        self.task(rrule='FREQ=WEEKLY;INTERVAL=2;BYDAY=TU;BYHOUR=10;BYMINUTE=0;BYSECOND=0')
        self.assertEqual(self.payload()['events'],[])

    def test_dst_preserves_wall_clock(self):
        self.task(timezone='America/New_York',rrule='FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0',created_at=ms('2026-03-06T00:00:00-05:00'))
        self.start=dt('2026-03-07T00:00:00-05:00');self.end=dt('2026-03-10T00:00:00-04:00');self.now=self.start
        events=self.payload()['events'];self.assertEqual(len(events),3)
        self.assertTrue(events[0]['start'].endswith('-05:00'));self.assertTrue(events[1]['start'].endswith('-04:00'))
        self.assertTrue(all('T09:00:00' in e['start'] for e in events))

    def test_monthly_31_skips_short_month(self):
        self.task(rrule='FREQ=MONTHLY;BYMONTHDAY=31;BYHOUR=10;BYMINUTE=0;BYSECOND=0',created_at=ms('2026-01-01T00:00:00Z'))
        self.start=dt('2026-02-01T00:00:00Z');self.end=dt('2026-03-01T00:00:00Z');self.now=self.start
        self.assertEqual(self.payload()['events'],[])

    def test_out_of_bounds_rejected(self):
        self.end=self.start+timedelta(days=100)
        with self.assertRaises(ValueError): self.payload()

    def test_reading_does_not_modify_inputs(self):
        row=self.task();self.database([row]);paths=list(self.home.rglob('*.*'));before={p:p.read_bytes() for p in paths}
        self.payload();self.assertEqual(before,{p:p.read_bytes() for p in paths})

    def test_overdue_not_marked_complete(self):
        row=self.task();self.database([{**row,'next_run_at':ms('2026-09-07T10:00:00+08:00')}])
        t=self.payload()['tasks'][0];self.assertTrue(t['overdue']);self.assertEqual(t['status'],'ACTIVE')


if __name__=='__main__': unittest.main()
