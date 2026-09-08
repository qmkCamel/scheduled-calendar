# Changelog

## 0.1.0-beta.1 — 2026-09-08

首个开源预览版 / First public preview.

- 周、月、日程视图；搜索、状态筛选、日期导航与任务详情。
- 只读本地 Codex 定时任务，区分调度器下一次运行与周期预估。
- 独立监控区域，明确标记过期、暂停及无法解析的任务。
- 本机 HTTP 服务、实例验证、启动复用、状态查询和停止命令。
- 内置周期解析依赖与许可证，可离线启动。
- 仅声明 macOS + Python 3.11+；云任务未接入，依赖内部存储，适合试用反馈。

Week/month/agenda views, filtering and task details for local Codex schedules. The loopback service includes instance verification and explicit start/status/stop commands. Dependencies and license notices are bundled. This preview does not support cloud tasks or replace the native Scheduled page; compatibility depends on Codex's internal storage.
