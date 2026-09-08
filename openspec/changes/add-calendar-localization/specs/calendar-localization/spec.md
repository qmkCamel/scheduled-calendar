## ADDED Requirements

### Requirement: Language selection
界面 SHALL 支持英文和简体中文，默认按浏览器首选语言选择，非中文回退英文；用户可以手动切换并保存来源范围内的偏好。

#### Scenario: Switching languages preserves context
- **WHEN** 用户在月视图筛选暂停任务后切换语言
- **THEN** 日期、视图、筛选保持不变，文案与日期格式切换

#### Scenario: Browser storage is unavailable
- **WHEN** 浏览器禁止读取或写入 localStorage
- **THEN** 日历仍能加载并在当前页面切换语言

### Requirement: Authentic localized screenshots
两份 README SHALL 使用对应语言的真实界面截图，数据为同一组虚构任务；任务原文不自动翻译。

#### Scenario: Documentation language matches screenshot
- **WHEN** 用户阅读英文或中文 README
- **THEN** 截图语言与文档匹配，且明确说明使用虚构数据
