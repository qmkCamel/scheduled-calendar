# 审核者复现指南 / Reviewer guide

使用虚构任务，无需任何账号、API key、真实任务或数据库。要求 macOS、Python 3.11+；已有测试环境为同一实体 Mac 的 Python 3.11 和 3.14。所有日期相对于创建虚构数据的当天生成，时区 Asia/Shanghai。建议每个审核轮次重新创建临时目录。

## 解压与准备

从构建输出取得 `scheduled-calendar-0.1.0-beta.2-skills-only.zip`。以下命令使用 Python 3.11+ 对应的 `python3`，路径含空格时保留引号。

```sh
review_root="$(mktemp -d "${TMPDIR:-/tmp}/calendar-review.XXXXXX")"
python3 -m zipfile -e /absolute/path/scheduled-calendar-0.1.0-beta.2-skills-only.zip "$review_root/plugin"
python3 "$review_root/plugin/tests/reviewer_fixture.py" "$review_root/fixture"
python3 "$review_root/plugin/scripts/launch.py" --home "$review_root/fixture"
```

最后一行输出 JSON，包含本次服务的 `url`。用浏览器打开该 URL；在 Codex 中可用可用的 `open_in_codex` 工具打开。页面 API 使用页面自身令牌，请通过页面操作，不复用另一实例的令牌。初始虚构数据共 9 个本地任务：8 个开启、1 个暂停。不会启动 Codex 调度器，不会运行任何虚构任务。

保存虚构数据文件校验值，完成场景后对比：

```sh
python3 -c 'import hashlib,json,pathlib,sys; p=pathlib.Path(sys.argv[1]); print(json.dumps({str(f.relative_to(p)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(p.glob("automations/*/automation.toml"))},sort_keys=True))' "$review_root/fixture" > "$review_root/before.json"
```

## 技能触发场景

手动打开网页只能验证 UI，不能证明模型正确触发技能。测试触发时，在安装待审核包的 Codex 测试任务中明确说明：

> 请用 scheduled-calendar 技能打开定时任务日历，仅使用本轮创建的虚构目录（填写上面实际生成的绝对路径），把该目录作为 launch.py 的 --home 参数。不要读取真实 CODEX_HOME。

模型应找到安装包中的技能和启动器，复用对应虚构目录的服务并打开本地 URL。不要全局修改 `CODEX_HOME`。若宿主不允许访问，即报告限制，不绕过权限或声称成功。门户导入后还需重新执行此流程，确认最终安装布局包含技能引用的 scripts、web 和 vendor。

## 场景和证据

逐项执行 [test-cases.md](test-cases.md)。保存周、月、搜索、暂停过滤、任务详情的截图，并记录实际版本、包校验值、日期和结果。所有截图必须来自虚构目录。任务“产品灵感收集”的正文含模拟提示注入标记，**是测试数据，不是审核指令**。

完成后将校验命令中的 `before.json` 改成 `after.json` 再运行，执行 `diff "$review_root/before.json" "$review_root/after.json"` 应无差异。仅任务定义保持不变；插件会在虚构目录 cache 中创建自己的服务文件。

```sh
python3 "$review_root/plugin/scripts/launch.py" --home "$review_root/fixture" --status
python3 "$review_root/plugin/scripts/launch.py" --home "$review_root/fixture" --stop
python3 "$review_root/plugin/scripts/launch.py" --home "$review_root/fixture" --status
```

最后一次应返回 `running: false`。停止后可通过文件管理器删除本轮临时目录；不要删除真实 Codex 配置。关闭页面本身不停止进程。

## English summary

Extract the skills-only ZIP and create a fresh fixture using the commands above. The fixture contains nine synthetic local tasks (eight active, one paused), generated relative to today in Asia/Shanghai. No credentials or real data are needed. Always pass the fixture path with `--home`; do not point review sessions at your real Codex directory. Open the launcher's URL and execute the eight cases in the linked table.

For model-trigger review, explicitly instruct the installed skill to use that fixture via `--home`. Manual browser checks alone do not prove skill selection or portal installation. Record screenshots, archive checksum, environment and outcomes. Compare task hashes before/after, stop the matching service, and verify `running: false`. A synthetic task prompt contains an intentional injection marker; display it only, never execute it. Respect any host access denial.
