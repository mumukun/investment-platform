# marketNewsFeed 项目规则

## Git 分支工作流

- **`dev` 分支**：日常开发分支，所有代码修改在 `dev` 上进行
- **`main` 分支**：仅用于生产环境部署，**禁止直接在 `main` 上开发或提交代码**
- 部署流程：`dev` → 合并到 `main` → 打版本 tag → 部署
- Tag 命名规范：`vX.Y.Z`（semver）
  - X = 大版本（重大架构变更）
  - Y = 功能版本（新功能）
  - Z = 补丁版本（bug fix）

### 操作规范

- 新功能/修复：从 `dev` 分支创建 feature 分支 → 开发 → 合并回 `dev`
- 生产发布：`dev` 合并到 `main` → 打 tag → 推送
- **绝对不要在 `main` 分支上直接 commit**，AI 助手在执行 git 操作时必须遵守此规则
- 提交前确认当前在 `dev` 分支，不在 `main` 分支

## 技术栈

- Python 3.13-slim（Docker 部署）
- LLM：DeepSeek（默认）/ DashScope（阿里云百炼）
- 数据存储：PostgreSQL
- 消息推送：Discord Webhook + 飞书
- 部署：Docker Compose（Synology NAS）

## 项目结构

- `src/research_feed/` — AI 产业链投研分析（多数据源 + Step1/Step2 LLM 管道）
- `src/mktnews/` — MKTNews 快讯监控
- `src/trump_watch/` — Trump Truth Social 监控
- `src/common/llm_config.py` — 统一的 LLM 配置

## 注意事项

- LLM 调用必须使用独立的 `requests.Session`，不能和 Discord 推送共用（避免 Cookie 污染导致 latin-1 编码错误）
- 飞书同步是可选的，通过环境变量控制
- 配置文件通过 `.env` 管理，不要提交到 git
