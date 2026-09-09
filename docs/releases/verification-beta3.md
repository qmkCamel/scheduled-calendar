# beta.3 社区发行验证

验证日期：2026-09-09。此记录针对社区市场安装包，官方门户提审状态未改变。

## 本地结果

- Python 3.11：36 项测试通过；HTTP/启停测试在正常宿主授权后执行。初次沙箱内测试因本机端口监听受限失败，未改动产品代码。
- Node：6 项语言测试通过。
- OpenSpec：`openspec validate publish-community-beta3 --strict` 通过，exit 0；遥测发送因网络受限失败，不影响校验结果。
- 社区 ZIP：70 个文件，公开插件文件集与字节均与源码一致；市场入口与仓库入口一致。
- 包内包含 `web/i18n.js`、两版演示截图、周期解析依赖与许可证。
- 在含空格路径解压，用隔离的 CLI 配置目录执行 README 中的本地市场添加及插件安装命令，实际安装版本为 `0.1.0-beta.3`。
- 从实际安装目录启动服务，读取 9 个虚构任务，确认语言脚本与包内文件一致；启动、复用、状态和停止检查通过，任务文件哈希不变，验证后服务已停止。
- 本次不修改 UI 或运行逻辑，不重复此前的浏览器场景；既有截图和交互证据见 [beta.3 提审验收记录](../submission/verification.md)。

## 社区资产

- ZIP：`scheduled-calendar-0.1.0-beta.3.zip`
- SHA-256：`6fb20c1e2944a5c4f9461bf5feeb19af453efcd01a11366388ee2e5fdaa93319`
- 附件：ZIP 与 `SHA256SUMS`。

## 公开发布结果

- [GitHub 预发布](https://github.com/qmkCamel/scheduled-calendar/releases/tag/v0.1.0-beta.3) 已公开：`isDraft=false`、`isPrerelease=true`，发布时间为 2026-09-09 04:58:42 UTC。
- `v0.1.0-beta.3` tag 对应提交 `eea73223ae4dfc1ba872b25c0375368761fb147e`。
- 从 GitHub 重新下载 ZIP 与 SHA256SUMS，二者均与本地构建逐字节一致，`shasum -a 256 -c SHA256SUMS` 返回 OK；GitHub 返回的资产摘要也与上面的 SHA-256 一致。
- 在另一个隔离配置目录按 README 执行 GitHub marketplace 添加命令与插件安装命令，实际版本为 `0.1.0-beta.3`，安装目录的插件文件与发布源码逐字节一致。
- GitHub Topics 已回读确认：`automation`、`calendar`、`codex`、`codex-plugin`、`local-first`。
- 未修改日历运行代码、现有个人插件安装或旧 beta.1 发行资产；未提交官方目录，也未发布社区宣传帖。
