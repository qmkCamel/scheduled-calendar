# 官方目录提审材料

状态：beta.3 本地提审材料与场景验收已完成；关闭服务场景包含宿主权限批准后的重试。未上传 Platform、未完成官方安全扫描、未提交审核。目标为 Skills only；没有公共 MCP 服务。

## 文件

- [listing.md](listing.md)：可粘贴的中英文目录文案、链接及发布说明。
- [reviewer-guide.md](reviewer-guide.md)：使用独立虚构任务的完整复现流程。
- [test-cases.md](test-cases.md)：5 个正向和 3 个负向审核场景，包含预期及证据边界。
- [publisher-checklist.md](publisher-checklist.md)：账号、身份、地区与最终声明。
- [验证记录](verification.md)：本次包结构、测试和虚构数据验证结果。
- [逐场景实际答复](evidence/model-results.json)：经路径和本机地址脱敏的模型结果，含初次问题与重试。
- [最终包文件清单](evidence/package-manifest.json)：最终 ZIP 的校验值及 63 个文件的逐项哈希。
- [条款](../../plugins/scheduled-calendar/TERMS.md)、[支持](../../plugins/scheduled-calendar/SUPPORT.md)、[隐私](../../plugins/scheduled-calendar/PRIVACY.md)。

## 生成上传文件

从仓库根目录运行：

```sh
python3 plugins/scheduled-calendar/scripts/build_submission.py --output dist/submission
```

输出 `scheduled-calendar-<version>-skills-only.zip` 与 `SHA256SUMS`。ZIP 根目录直接包含 `.codex-plugin/plugin.json` 和 `skills/scheduled-calendar/SKILL.md`，没有市场目录和仓库包装层。运行脚本、网页和依赖的相对位置保持不变。与本地插件相比，上传包只移除 manifest 的 `interface.screenshots` 和未引用的演示截图，不改变技能说明或运行代码。

Logo 为原创、无外部引用的 512×512 SVG 日历图标；`logo` 和 `composerIcon` 使用同一文件。官方错误参考列出 SVG 为支持格式。无需 AI 服务生成或外部字体。

GitHub Release 的旧 beta.1 ZIP 是本地市场安装包，不能替代此提审 ZIP。构建结果不代表服务端扫描或审核通过。

## 官方依据与差异

核对日期：2026-09-08。

- [提交指南](https://developers.openai.com/plugins/deploy/submission)提供一般材料流程、身份认证和发布流程。
- [提交错误参考](https://developers.openai.com/plugins/deploy/submission-errors)进一步区分 Skills-only：四个公开链接可选；截图声明被排除；要求根目录插件、有效技能及品牌图片。该页把 5 正向 / 3 负向用例列为 MCP 最终提交要求，一般指南则统一建议准备。这里仍完整提供八个场景，供审核和自检使用，不把它们表述为已证实的 Skills-only 强制门槛。

执行门户实际展示的验证流程。任何身份不匹配、归一化或扫描提示都应读完后处理，不能自动替发布者确认。
