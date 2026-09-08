"""Read-only adapter for Codex's local scheduled tasks. No task execution."""
from __future__ import annotations

import os
import sqlite3
import sys
import tomllib
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vendor'))
from dateutil.rrule import rrulestr
from dateutil.tz import gettz, tzlocal

UTC = timezone.utc
MAX_EVENTS = 3000
FIELDS = ('id', 'name', 'prompt', 'status', 'rrule', 'kind', 'target_thread_id',
          'created_at', 'updated_at', 'timezone', 'next_run_at', 'last_run_at')


def local_zone():
    name = os.environ.get('TZ')
    if not name:
        try:
            name = str(Path('/etc/localtime').resolve()).split('zoneinfo/')[-1]
            ZoneInfo(name)
        except (OSError, ValueError, KeyError):
            name = None
    return (gettz(name), name) if name and gettz(name) else (tzlocal(), '本机时区')


def stamp(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value / 1000, UTC)
    parsed = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('时间必须包含时区')
    return parsed


def iso(value):
    return value.isoformat() if value else None


def validate_row(row):
    for field in ('id', 'name', 'prompt', 'status', 'rrule', 'kind', 'timezone', 'target_thread_id'):
        if row.get(field) is not None and not isinstance(row[field], str):
            raise ValueError(f'{field} must be text')
    for field in ('created_at', 'updated_at', 'next_run_at', 'last_run_at'):
        if row.get(field) is not None and (isinstance(row[field], bool) or not isinstance(row[field], (int, float))):
            raise ValueError(f'{field} must be a timestamp')
    return row


def read_tasks(home: Path):
    warnings, files, database = [], {}, {}
    folder = home / 'automations'
    if not folder.exists():
        warnings.append('未找到本地任务目录。云端任务尚未接入。')
    for path in sorted(folder.glob('*/automation.toml')):
        try:
            with path.open('rb') as handle:
                raw = tomllib.load(handle)
            row = {key: raw[key] for key in FIELDS if key in raw}
            row['id'] = str(row.get('id') or path.parent.name)
            files[row['id']] = validate_row(row)
        except (OSError, ValueError) as exc:
            warnings.append(f'任务 {path.parent.name} 读取失败：{type(exc).__name__}')
    db = home / 'sqlite' / 'codex-dev.db'
    db_ok = False
    if db.exists():
        try:
            with closing(sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, timeout=1)) as conn:
                conn.row_factory = sqlite3.Row
                conn.execute('PRAGMA query_only=ON')
                columns = {r[1] for r in conn.execute('PRAGMA table_info(automations)')}
                selected = [key for key in FIELDS if key in columns]
                if 'id' not in selected:
                    raise ValueError('不兼容的表结构')
                for row in conn.execute('SELECT ' + ','.join(selected) + ' FROM automations'):
                    try:
                        database[str(row['id'])] = validate_row(dict(row))
                    except ValueError:
                        warnings.append(f'任务 {row["id"]} 的调度字段不兼容，已跳过该记录。')
                db_ok = True
        except (sqlite3.Error, ValueError) as exc:
            warnings.append(f'无法读取调度状态（{type(exc).__name__}）；仅展示配置预估。')
    else:
        warnings.append('未找到调度数据库；仅展示配置预估。')
    tasks = []
    for task_id in sorted(files.keys() | database.keys()):
        file, row = files.get(task_id, {}), database.get(task_id, {})
        file_newer = (file.get('updated_at') or 0) > (row.get('updated_at') or 0)
        merged = {**row, **file} if file_newer else {**file, **row}
        if file_newer:
            merged.pop('next_run_at', None)
            merged.pop('last_run_at', None)
        merged['source'] = 'local'
        merged['schedulerAvailable'] = bool(row) and not file_newer
        tasks.append(merged)
    return tasks, warnings, db_ok


def rule_for(task, zone):
    rule = str(task.get('rrule') or '').strip()
    if not rule:
        return None
    if len(rule) > 4096:
        raise ValueError('周期规则过长')
    # A creation-time anchor preserves COUNT/INTERVAL; never rebase to the viewed month.
    created = stamp(task.get('created_at'))
    if not created and 'DTSTART' not in rule:
        raise ValueError('缺少周期起点')
    anchor = created.astimezone(zone).replace(microsecond=0) if created else None
    if 'RRULE:' not in rule:
        rule = 'RRULE:' + rule
    return rrulestr(rule, dtstart=anchor)


def calendar_payload(home: Path, start: datetime, end: datetime, now=None):
    now = now or datetime.now(UTC)
    if start.tzinfo is None or end.tzinfo is None or not 0 < (end-start).total_seconds() <= 63*86400:
        raise ValueError('日期范围须为 1 至 63 天并包含时区')
    rows, warnings, db_ok = read_tasks(home)
    default_zone, zone_name = local_zone()
    tasks, events = [], []
    for raw in rows:
        task = {key: raw.get(key) for key in ('id', 'name', 'prompt', 'status', 'rrule', 'kind', 'target_thread_id')}
        task['name'] = str(task['name'] or task['id'])
        task['status'] = str(task['status'] or 'UNKNOWN').upper()
        task['source'] = 'local'
        task['timezone'] = raw.get('timezone') or zone_name
        task['timezoneAssumed'] = not bool(raw.get('timezone'))
        task['anchorAssumed'] = 'DTSTART' not in str(raw.get('rrule', ''))
        task['notes'] = []
        task['monitor'] = False
        task['nextRun'] = None
        task['lastRun'] = None
        task['nextKind'] = None
        task['overdue'] = False
        task['exhausted'] = False
        task['schedulerAvailable'] = raw['schedulerAvailable']
        try:
            zone = gettz(raw['timezone']) if raw.get('timezone') else default_zone
            if zone is None:
                raise ValueError('未知时区')
            next_run = stamp(raw.get('next_run_at'))
            task['lastRun'] = iso(stamp(raw.get('last_run_at')))
            rule = rule_for(raw, zone)
            text_rule = str(raw.get('rrule') or '')
            # Continuous or high-frequency tasks live in a separate lane, not 1000 calendar blocks.
            task['monitor'] = rule is None or any(f'FREQ={freq}' in text_rule for freq in ('SECONDLY', 'MINUTELY'))
            active = task['status'] == 'ACTIVE'
            if active and next_run:
                task['nextRun'], task['nextKind'] = iso(next_run), 'scheduled'
                task['overdue'] = next_run < now - timedelta(minutes=5)
            elif active and rule and not task['monitor']:
                # Bounded next-occurrence lookup; a far-future annual date can be outside the horizon.
                horizon = now + timedelta(days=370)
                following = next(rule.xafter(now, count=1, inc=True), None)
                if following and following <= horizon:
                    task['nextRun'], task['nextKind'] = iso(following), 'estimated'
                elif following is None:
                    task['exhausted'] = True
                    task['notes'].append('周期已无后续日期，任务仍显示开启；请在 Codex 核对。')
            task_events = []
            if active and next_run and start <= next_run < end and not task['monitor']:
                task_events.append({'taskId': task['id'], 'start': iso(next_run), 'kind': 'scheduled'})
            if rule and not task['monitor'] and task['status'] in ('ACTIVE', 'PAUSED'):
                # Replace only the first nominal future occurrence. Preserve other runs that day.
                replaced = next(rule.xafter(now, count=1, inc=True), None) if active and next_run else None
                count = 0
                for occurrence in rule.xafter(start, inc=True):
                    if occurrence >= end:
                        break
                    count += 1
                    if count > 600 or len(events)+len(task_events) >= MAX_EVENTS:
                        task['notes'].append('本范围任务过密，已限制展示数量。')
                        break
                    # Scheduler's next timestamp wins over its nominal recurrence, including jitter.
                    if active and next_run and occurrence == replaced and abs((occurrence-next_run).total_seconds()) < 3600:
                        continue
                    if active and next_run and now <= occurrence < next_run:
                        continue
                    task_events.append({'taskId': task['id'], 'start': iso(occurrence),
                                        'kind': 'paused' if not active else 'estimated'})
            events.extend(task_events)
            if task['overdue']:
                task['notes'].append('调度器记录时间已过，未确认执行；日历不会将其标记为已完成。')
        except (ValueError, TypeError, OverflowError, KeyError) as exc:
            task['notes'].append('无法解析此任务的时间或周期：' + str(exc))
            warnings.append(f'任务「{task["name"]}」需核对时间配置。')
        tasks.append(task)
    return {'tasks': tasks, 'events': sorted(events, key=lambda e: e['start']), 'warnings': warnings,
            'syncedAt': iso(now), 'timezone': zone_name,
            'coverage': {'local': True, 'scheduler': db_ok, 'cloud': False}}
