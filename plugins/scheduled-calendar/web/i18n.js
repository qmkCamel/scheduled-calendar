'use strict';
// UI/system text only. User-authored task names and prompts are never translated.
const CalendarI18n = (() => {
  const english = {
  "定时任务日历 · Codex": "Scheduled Calendar · Codex",
  "定时任务日历首页": "Scheduled Calendar home",
  "日历": "Calendar",
  "工作空间": "WORKSPACE",
  "定时任务日历": "Scheduled calendar",
  "迷你日历上个月": "Previous month in mini calendar",
  "迷你日历下个月": "Next month in mini calendar",
  "任务状态": "TASK STATUS",
  "已开启": "Active",
  "已暂停": "Paused",
  "已完成": "Completed",
  "状态未知": "Unknown status",
  "全部任务": "All tasks",
  "本地任务已连接": "Local tasks connected",
  "正在读取任务…": "Loading tasks…",
  "云端任务尚未接入": "Cloud tasks not connected",
  "一个更清楚的时间视角": "A clearer view of your time",
  "让每一项安排，一目了然": "Every task, at a glance",
  "把任务交给 Codex，把时间留给自己。": "Let Codex handle the tasks. Make time for yourself.",
  "刷新": "Refresh",
  "安排概览": "Schedule overview",
  "今日计划": "TODAY",
  "本周安排": "THIS WEEK",
  "次计划触发": "scheduled runs",
  "下一项任务": "UP NEXT",
  "正在读取…": "Loading…",
  "上一期": "Previous period",
  "下一期": "Next period",
  "今天": "Today",
  "日历视图": "Calendar view",
  "周": "Week",
  "月": "Month",
  "日程": "Agenda",
  "搜索任务…": "Search tasks…",
  "搜索任务": "Search tasks",
  "正在读取你的安排…": "Loading your schedule…",
  "● 调度器下一次　○ 周期预估": "● Next scheduled run　○ Recurrence estimate",
  "仅本机 · 云端尚未接入": "Local only · Cloud not connected",
  "等待同步": "Waiting to sync",
  "日历展示触发时间，不代表任务耗时。周期预估与历史日期不等于执行记录。": "Dates show trigger times, not task duration. Recurrence estimates and past dates are not execution records.",
  "关闭详情": "Close details",
  "语言": "Language",
  "跟随浏览器": "Browser default",
  "暂无记录": "No record",
  "调度器下一次": "Next scheduled run",
  "周期预估": "Recurrence estimate",
  "已暂停 · 原计划": "Paused · Original schedule",
  "暂无后续任务": "No upcoming task",
  "持续监控与待核对任务请见日历上方": "See monitors and tasks needing review above the calendar",
  "{count} 个本地任务 · 每 30 秒刷新": "{count} local tasks · Refreshes every 30s",
  "演示数据 · 非真实任务": "Demo data · Synthetic tasks",
  "更新于 {time}": "Updated at {time}",
  "持续监控 / 待核对": "MONITORS / NEEDS REVIEW",
  "暂停": "Paused",
  "+{count} 项安排": "+{count} more",
  "这段时间没有安排": "No events in this period",
  "可以切换日期，或查看其他任务状态。": "Try another date or task status.",
  "其他任务 · 本范围无触发日期": "Other tasks · No trigger dates in this range",
  "持续监控": "Continuous monitor",
  "周期已结束，待核对": "Recurrence ended; needs review",
  "本范围无计划": "No dates in this range",
  "没有匹配的任务": "No matching tasks",
  "试试其他关键词或任务状态。": "Try another keyword or task status.",
  "读取失败，请点击刷新重试。": "Could not load tasks. Click Refresh to retry.",
  "演示数据 · 以下为虚构任务，不会执行。": "Demo data · These synthetic tasks will not run.",
  "同步失败：{error}{snapshot}": "Sync failed: {error}{snapshot}",
  " 当前保留上次快照。": " Showing the last snapshot.",
  "暂时无法读取任务": "Tasks are temporarily unavailable",
  "状态": "Status",
  "所选日期": "Selected date",
  "任务概览": "Task overview",
  "下一次运行": "Next run",
  "暂停中，不会运行": "Paused; will not run",
  "无已知时间": "No known time",
  "最近运行": "Last run",
  "规则时区": "Schedule time zone",
  "（按本机推定）": " (inferred from this machine)",
  "任务类型": "Task type",
  "回到原任务继续": "Continue the original task",
  "独立定时任务": "Standalone scheduled task",
  "任务内容": "Task instructions",
  "无任务说明": "No task instructions",
  "周期未提供明确起点，按任务创建时间估算。有限次数、间隔周期请以 Codex 调度器为准。": "No explicit recurrence start was provided; the task creation time is used. For limited or interval recurrences, defer to the Codex scheduler.",
  "日历只读展示。要调整时间、暂停或继续任务，可复制下方指令发给 Codex。": "This calendar is read-only. To reschedule, pause, or resume a task, copy the request below and send it to Codex.",
  "复制任务管理指令": "Copy task management request",
  "已复制，粘贴给 Codex": "Copied; paste into Codex",
  "请复制上方指令": "Copy the request above",
  "请查看并帮我管理定时任务「{name}」（id: {id}），先展示当前安排。": "Please review and help me manage the scheduled task “{name}” (id: {id}). Show its current schedule first.",
  "本机时区": "Local time zone",
  "未找到本地任务目录。云端任务尚未接入。": "No local task directory found. Cloud tasks are not connected.",
  "未找到调度数据库；仅展示配置预估。": "Scheduler database not found; showing configuration estimates only.",
  "周期已无后续日期，任务仍显示开启；请在 Codex 核对。": "The recurrence has no future dates, but the task is still active. Check it in Codex.",
  "本范围任务过密，已限制展示数量。": "Too many occurrences in this range; the number displayed has been limited.",
  "调度器记录时间已过，未确认执行；日历不会将其标记为已完成。": "The recorded schedule time has passed; execution is unconfirmed. The calendar will not mark it completed.",
  "时间必须包含时区": "The timestamp must include a time zone",
  "周期规则过长": "Recurrence rule is too long",
  "缺少周期起点": "Missing recurrence start",
  "未知时区": "Unknown time zone"
};
  const supported = ['en', 'zh-CN'];
  function resolve(preference, languages = []) {
    if (supported.includes(preference)) return preference;
    const primary = languages[0] || 'en';
    return /^zh(?:-|$)/i.test(primary) ? 'zh-CN' : 'en';
  }
  function translate(locale, key, values = {}) {
    const template = locale === 'en' ? (english[key] ?? key) : key;
    return template.replace(/\{(\w+)\}/g, (match, name) => values[name] === undefined ? match : String(values[name]));
  }
  function systemMessage(locale, message) {
    if (locale !== 'en') return message;
    if (english[message]) return english[message];
    const patterns = [
      [/^任务 (.+) 读取失败：(.+)$/, (m,id,error) => `Could not read task ${id}: ${error}`],
      [/^任务 (.+) 的调度字段不兼容，已跳过该记录。$/, (m,id) => `Task ${id} has incompatible schedule fields; this record was skipped.`],
      [/^无法读取调度状态（(.+)）；仅展示配置预估。$/, (m,error) => `Could not read scheduler state (${error}); showing configuration estimates only.`],
      [/^任务「(.+)」需核对时间配置。$/, (m,name) => `Check the time configuration for task “${name}”.`],
      [/^无法解析此任务的时间或周期：(.+)$/, (m,error) => `Could not parse this task's time or recurrence: ${translate(locale,error)}`],
    ];
    for (const [pattern, replacement] of patterns) if (pattern.test(message)) return message.replace(pattern, replacement);
    return message;
  }
  return { resolve, translate, systemMessage, english };
})();
if (typeof module !== 'undefined') module.exports = CalendarI18n;
