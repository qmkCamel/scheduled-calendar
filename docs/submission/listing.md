# 目录字段与发布说明

以下文案已按现有实现编写；发布者身份仍需在 Platform 选择已认证信息。项目署名 Edge 不等于身份已经认证。

| 字段 | 填写内容 |
| --- | --- |
| Submission type | Skills only |
| Package name | scheduled-calendar |
| Version | 0.1.0-beta.3 |
| Display name | Scheduled Calendar |
| 中文名称备选 | 定时任务日历 |
| Category | Productivity |
| Short description | Calendar for local Codex tasks |
| 中文短描述备选 | 把 Codex 的本地定时任务放进日历 |
| Website | https://github.com/qmkCamel/scheduled-calendar |
| Support | https://github.com/qmkCamel/scheduled-calendar/issues |
| Privacy | https://github.com/qmkCamel/scheduled-calendar/blob/main/plugins/scheduled-calendar/PRIVACY.md |
| Terms | https://github.com/qmkCamel/scheduled-calendar/blob/main/plugins/scheduled-calendar/TERMS.md |
| Logo / composer icon | 插件内 assets/logo.svg |
| Authentication | 无插件自有账号；无 API key；本地技能使用宿主权限 |
| Countries / regions | 发布者在门户按实际支持情况选择，不预选全球 |

## English long description

See your existing local Codex automations in week, month, and agenda views without migrating tasks. Search by name, filter task status, inspect descriptions, and distinguish the scheduler's next run from estimated recurrence dates. The calendar refreshes every 30 seconds.

This preview requires macOS, Python 3.11+, and a Codex environment with local shell and browser access. The calendar supports English and Simplified Chinese, follows the browser’s primary language, and offers a manual language selector. Task names and prompts remain in their original language. It opens a separate loopback browser page; it does not replace the native Scheduled page. Cloud tasks and remote-only environments are not supported.

The plugin reads local task definitions and scheduler metadata from Codex's internal TOML/SQLite storage. It does not modify or execute tasks. It starts a local HTTP process and stores service metadata and startup logs; closing the page does not stop the process. Ask to stop the calendar service when finished. There is no developer backend, telemetry, or advertising. Browser or AI hosts may read page content under their own policies.

Projected dates are estimates, not proof of execution or success. Codex storage updates may require adapter changes. Testing has been performed on one physical Mac, including Python 3.11 and 3.14; other platforms have not been validated. Independent community project, unaffiliated with OpenAI.

## 中文长描述

无需迁移任务，以周、月和日程查看已有 Codex 本地自动化安排。支持搜索、状态筛选和任务详情，每 30 秒刷新，区分调度器下一次运行与周期预估日期。

预览版要求 macOS、Python 3.11+，以及可使用本地终端与浏览器的 Codex 环境。界面支持英文和简体中文，默认跟随浏览器首选语言，也可手动切换；任务名称和正文保留原文。在独立本地浏览器页面打开，不替换原生 Scheduled 页面，不支持云端任务或仅远程运行的环境。

只读内部 TOML/SQLite 任务存储，不修改或执行任务。插件会启动本地 HTTP 进程并保存服务元数据和启动日志；关闭页面不自动停止进程，可要求停止日历服务。没有开发者后端、遥测或广告；浏览器及 AI 宿主访问页面时适用宿主自己的权限与隐私设置。

预估日期不代表已执行或执行成功；Codex 存储更新可能需要适配。目前在一台实体 Mac 上验证过 Python 3.11 与 3.14，其他平台未验收。本项目由社区独立开发，与 OpenAI 无关联。

## Starter prompts

1. Open the scheduled calendar for my local Codex tasks.
2. 用日历看看本周的本地自动化安排。
3. 打开本地任务日历，我想查看本月的安排。

这些提示用于打开可操作页面，不承诺自然语言直接设置日期或筛选状态。用户在页面内切换视图和筛选。

## Release notes / initial submission

Initial directory submission of Scheduled Calendar 0.1.0-beta.3, a macOS-only skills plugin for viewing existing local Codex automations. Includes branding, privacy and terms, a standalone skills-only ZIP, and synthetic reviewer fixtures. This candidate includes the bilingual interface and refreshed review evidence. No public MCP endpoint, OAuth, cloud task integration, or native Scheduled-page replacement is provided. Reviewer setup and limitations are documented in the supplied guide. No official review has been completed.

首次提交定时任务日历 0.1.0-beta.3，面向 macOS 本机任务，补充品牌图标、隐私与条款、专用上传包和虚构审核数据。本次包含双语界面与更新后的验收证据；不含公共 MCP、OAuth、云端任务接入或原生页面替换。审核环境与限制见复现指南，目前尚未完成官方审核。
