# 隐私说明 / Privacy

更新日期：2026-09-08。

## 读取的数据

插件只读访问当前 `CODEX_HOME` 下的本地任务配置和调度数据库，提取任务名称、说明、状态、周期、时区、创建/更新时间、下次/最近运行时间及关联任务标识。默认位置为 `~/.codex`。

不会读取认证凭据、聊天历史、任务执行结果或浏览历史。不会创建、修改、暂停、删除或执行定时任务。

## 处理与保存

任务数据通过仅监听 `127.0.0.1` 的 HTTP 服务发送到用户打开的本地日历页面。页面每 30 秒请求更新，任务数据保留在运行进程和页面内存中，不另建任务副本。

启动器在 `CODEX_HOME/cache/scheduled-calendar` 保存服务地址、进程标识、插件/配置目录、实例标识和启动日志。日志用于诊断服务启动，不主动记录任务正文。关闭页面不会自动停止服务，可使用 `scripts/launch.py --stop` 停止。

插件没有开发者服务器、遥测、广告、分析 SDK 或对外上传。使用 Codex 或其他浏览器/AI 连接器查看页面时，相关宿主可能读取可见内容；其行为受宿主自身的设置与隐私政策约束。

## 用户主动分享

“复制任务管理指令”会在用户点击时将包含任务名称与标识的文本放入剪贴板。用户自行粘贴给 Codex 后，内容由 Codex 处理。

提交 GitHub Issue 时，请使用虚构数据复现；不要贴出真实任务正文、认证凭据、数据库或未脱敏截图。

## English summary

This plugin reads local Codex automation definitions and scheduler metadata. It serves a read-only calendar on `127.0.0.1`, with no developer backend, analytics, advertising, or outbound data uploads. Task data remains in process/browser memory; local runtime metadata and startup logs are stored under `CODEX_HOME/cache/scheduled-calendar`.

Your browser or AI host may inspect page content according to its own policies. Copying a management prompt is an explicit user action. Stop the server with `scripts/launch.py --stop`. Please keep real tasks, credentials, and private screenshots out of public issues.
