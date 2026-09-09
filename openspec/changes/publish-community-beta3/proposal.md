# 发布 beta.3 社区安装包并补齐发现入口

## 原因

公开预发布资产仍为 beta.1，中英文 README 也将用户固定安装到旧版。beta.3 的双语能力与提审包已完成验证，需要通过社区发行入口提供给试用者。GitHub Topics 当前为空。

## 变更

- 使用现有 build_release.py 发布完整的 beta.3 社区市场 ZIP 与 SHA256SUMS。
- 同步中英文 README、包内使用说明与发布说明，明确 macOS、本地任务和只读范围。
- 校验解压包的语言资源、运行依赖和隔离安装流程。
- 添加 codex、codex-plugin、calendar、automation、local-first Topics。

## 范围

不修改日历运行逻辑，不升级用户现有插件，不操作官方目录审核，不代发宣传帖。
