# 国际化验收记录

日期：2026-09-08。所有浏览器验收均使用独立虚构数据目录，没有接触真实任务正文。

- 36 项 Python 数据、HTTP、服务生命周期测试通过。
- 6 项 Node 测试通过：首选语言回退、手动选择优先级、用户原文插值、系统警告、静态/动态文案覆盖、存储禁用、持久化。
- OpenSpec 严格校验与 JavaScript 语法检查通过。
- 浏览器实际观察默认跟随中文首选语言；手动选择英文后刷新仍保留英文。
- 月视图暂停筛选后切换中文，月份与筛选不变，英文任务名称和正文保持原样。
- 英文日程、暂停任务详情、搜索无结果空态通过；两版浏览器错误日志为空。
- 390px 窄屏实测语言/状态选择可用，页面 scrollWidth 等于 viewport 390px；月历内部允许横向滚动。
- 两组虚构任务使用相同 ID 与周期，分别提供中英文名称/正文。截图使用实际渲染页面，不修改截图文字。

## 截图

- `plugins/scheduled-calendar/assets/calendar-demo-en.png`：英文月视图。
- `plugins/scheduled-calendar/assets/calendar-demo-zh-CN.png`：中文月视图。
- `artifacts/calendar-localization/`：详情与窄屏验收截图（不进 Git）。

当前仅修改独立源码，未升级已有个人插件，未发布新的版本或覆盖 beta.1 发行资产。README 已明确源码与已发布版本的语言能力差异。
