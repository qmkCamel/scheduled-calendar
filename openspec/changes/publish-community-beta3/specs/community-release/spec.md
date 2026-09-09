## ADDED Requirements

### Requirement: 社区预览版必须提供与文档一致的安装入口

社区发行版 SHALL 包含本地市场入口、完整插件与运行依赖，中英文 README 必须引用相同版本。

#### Scenario: 用户下载 beta.3 并安装

- **WHEN** 用户校验并解压 beta.3 社区 ZIP
- **THEN** 可以从解压根目录添加社区市场并安装插件，插件版本为 0.1.0-beta.3，包含英文和简体中文界面资源

### Requirement: 公开发行状态必须有远端证据

发布记录 SHALL 区分本地构建、Git 提交与公开预发布，核对远端 tag、发行资产和 Topics。

#### Scenario: 社区包发布完成

- **WHEN** 宣称 beta.3 社区版已发布
- **THEN** GitHub 存在对应预发布与 ZIP、SHA256SUMS，下载内容与本地构建一致，Topics 可读取
