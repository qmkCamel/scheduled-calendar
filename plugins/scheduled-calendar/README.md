# 定时任务日历

**macOS 开源预览版。** 需要 Python 3.11+，界面为简体中文。当前验证过 macOS + Python 3.11/3.14；Windows、Linux 和其他 Codex 存储版本未验收。

在 Codex 中说 **“打开定时任务日历”**，以周、月或日程查看自动化安排。

支持：真实本地任务、日期导航、搜索、状态筛选、任务详情、实际下一次运行、周期预估、持续监控区域、待核对提示；每 30 秒刷新。

插件打开独立的 Codex 浏览器面板。它不会替换原生“已安排任务”页面。云端任务尚未接入，页面始终标明覆盖范围。

## 运行

需要 Python 3.11+。安装后由技能自动启动，也可以手动运行：

```sh
python3 scripts/launch.py
```

打开输出的 `url`。服务仅监听 `127.0.0.1`。下面两个命令可以查看状态或停止服务；启动器会核对实例身份，避免停止其他进程。

```sh
python3 scripts/launch.py --status
python3 scripts/launch.py --stop
```

关闭页面不会自动停止服务。插件不会设置开机自启。缺少 Python 3.11+ 时，先安装受支持的 Python；无需 `pip install`，不要用系统自带旧 Python 运行。

## 安装与卸载

发行包根目录包含 `.agents/plugins/marketplace.json` 与 `plugins/scheduled-calendar/`。将解压目录保留在固定位置，在根目录执行：

```sh
codex plugin marketplace add .
codex plugin add scheduled-calendar@scheduled-calendar-community
```

安装后在新的 Codex 任务中说“打开定时任务日历”。这会加载技能并打开浏览器面板。如果宿主拒绝读取私密页面，可由你自行打开启动器给出的本地 URL；不要绕过宿主权限限制。

卸载前先在已安装插件目录运行 `python3 scripts/launch.py --stop`，然后执行：

```sh
codex plugin remove scheduled-calendar@scheduled-calendar-community
```

卸载不会删除 Codex 的任务。若此前安装过开发版 `scheduled-calendar@personal`，先停止该版本服务并移除该插件，避免同名技能同时启用。仅删除不再需要的解压发行目录，不要删除 `~/.codex/automations` 或数据库。

## 数据与边界

- 默认读取 `~/.codex/automations/*/automation.toml` 及 `~/.codex/sqlite/codex-dev.db`，支持 `CODEX_HOME`。数据库以只读模式打开。
- 调度器 next_run_at 为已知下一次运行；其余日期是规则预估。已过日期不代表执行成功。
- 没有 DTSTART 时，使用创建时间估算 COUNT/INTERVAL 的起点；没有时区时推定本机时区。详情显示这两种假设。
- 已暂停任务可以查看原计划，已完成任务在日程中展示记录，不生成未来运行。
- 没有固定时间的监控及分钟级任务放入持续监控区域。过期未运行任务放入待核对区域。
- 内部数据格式不是公开稳定 API，读取异常会明确提示。云端、其他主机任务及运行结果暂未接入。
- 不收集遥测、不联网、不执行任务正文、不修改任务。所有用户内容通过 DOM textContent 展示。

## 开发验证

```sh
python3 -m unittest discover -s tests -v
```

`vendor/` 内置 python-dateutil 2.9.0.post0 和 six 1.17.0，许可证随各自 dist-info 目录保留。依赖用于 RFC 5545 周期解析，不需要模型 API key。

## 反馈与授权

请通过发布仓库的 GitHub Issues 提交反馈，提供 macOS、Python、Codex 版本和使用虚构数据的复现步骤。请勿附上真实任务正文、数据库、凭据或私密截图。

源码采用 [MIT License](LICENSE)，依赖授权见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)，数据处理见 [PRIVACY.md](PRIVACY.md)。本项目独立开发，与 OpenAI 无关联，未提交官方插件目录审核。

## English

Scheduled Calendar is an experimental, read-only calendar for existing **local Codex automations**. It provides week/month/agenda views, search, status filters, task details, and automatic refresh. No task migration or model API key is needed. The UI is currently Simplified Chinese.

This preview targets macOS with Python 3.11+. It opens a standalone loopback browser panel, does not replace Codex's native Scheduled page, and does not support cloud tasks. Its adapter reads internal Codex files and may need updates when Codex changes. Recurrence dates are estimates, not proof of execution. See the privacy policy and verification record before sharing real task content with an AI/browser host.
