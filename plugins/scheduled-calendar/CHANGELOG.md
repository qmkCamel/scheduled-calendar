# Changelog

## 0.1.0-beta.3 — 双语提审候选包

- 同步中英文界面与完整 i18n 运行文件，刷新目录说明。
- 提审构建按 manifest 移除所有演示截图，保留品牌图标。
- 校验所有运行文件均被打包，防止新增模块漏包；补充实际模型与浏览器审核场景证据。
- 技能摘要必须注明周期预估时间；本地验收不等于官方安全扫描或目录审核通过。

### 双语界面

- Add English and Simplified Chinese UI, browser-language detection, and a persistent manual language selector.
- Localize dates, system messages, task details, and task-management requests; keep user task text unchanged.
- Add matching synthetic screenshots for English and Chinese README files.
- 新增中英文界面、浏览器语言识别与手动切换；更新两版 README 的真实演示截图。

## 0.1.0-beta.2 — 提审材料

- 增加日历 Logo、使用条款、支持说明和公开链接。
- 增加无截图声明、插件位于根目录的 Skills-only 提审包构建器。
- 增加安全的虚构审核数据及包结构测试；日历运行代码保持不变。
- 本版本尚未通过官方目录审核。

## 0.1.0-beta.1 — 2026-09-08

首个开源预览版 / First public preview.

- 周、月、日程视图；搜索、状态筛选、日期导航与任务详情。
- 只读本地 Codex 定时任务，区分调度器下一次运行与周期预估。
- 独立监控区域，明确标记过期、暂停及无法解析的任务。
- 本机 HTTP 服务、实例验证、启动复用、状态查询和停止命令。
- 内置周期解析依赖与许可证，可离线启动。
- 仅声明 macOS + Python 3.11+；云任务未接入，依赖内部存储，适合试用反馈。

Week/month/agenda views, filtering and task details for local Codex schedules. The loopback service includes instance verification and explicit start/status/stop commands. Dependencies and license notices are bundled. This preview does not support cloud tasks or replace the native Scheduled page; compatibility depends on Codex's internal storage.
