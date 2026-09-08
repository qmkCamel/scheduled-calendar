## ADDED Requirements

### Requirement: 最新候选包必须完整包含运行依赖

Skills-only 提审包 SHALL 包含当前源码的全部 scripts、web 和 skills 文件，排除 Python 缓存，且每个文件内容一致。

#### Scenario: 新增语言模块

- **WHEN** 当前网页引用 web/i18n.js
- **THEN** 上传 ZIP 包含该文件并通过源码与包文件集合、字节内容对比

### Requirement: 审核证据必须区分测试层次

验证记录 SHALL 标明模型显式技能调用、浏览器 UI 验收、本地命令测试与官方门户扫描的不同状态。

#### Scenario: 本地八个场景完成

- **WHEN** 使用隔离虚构任务完成本地正负场景
- **THEN** 记录输入、实际输出、工具行为及截图，并保持官方门户导入和扫描为未验证

### Requirement: 双语描述必须与源码一致

目录文案 SHALL 描述英文和简体中文切换、用户原文保留以及本地任务覆盖边界。

#### Scenario: 构建双语候选版本

- **WHEN** 发布者查看候选版本材料
- **THEN** 目录字段不再声明界面仅支持中文，版本与上传包一致
