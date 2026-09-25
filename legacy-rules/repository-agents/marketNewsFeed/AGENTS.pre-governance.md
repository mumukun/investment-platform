# marketNewsFeed 项目协作规范

本文档适用于整个仓库。AI 助手和开发者在修改代码、测试、提交及发布时都应遵守；若子目录存在更具体的 `AGENTS.md`，以更具体的规则为准。

## 1. 项目目标与运行方式

marketNewsFeed 是一个常驻运行的财经信息采集与投研分发服务，面向 A 股、美股科技产业链研究。系统从多个外部来源抓取内容，经规则和 LLM 分析后写入 PostgreSQL 主库，并按配置推送到 Discord、飞书或报告中心。

- 生产运行时：Python 3.13-slim
- 进程入口：`src/run_all.py`
- 容器入口：`Dockerfile` 中的 `python src/run_all.py`
- 部署方式：Docker Compose，目标环境为 Synology NAS
- 时区：业务展示和定时任务统一按 `Asia/Shanghai`；存储时间应保持现有模块约定，不要在无迁移方案时改变时间格式
- 依赖清单：`agent_docs/requirements.txt`
- 运行配置：仓库根目录 `.env`，由 `python scripts/check_config.py` 启动前校验

`src/run_all.py` 负责启动并监管所有常驻子进程。新增或移除常驻服务时，必须同步检查 `src/run_all.py`、`Dockerfile`、`docker-compose.yml`、配置校验和 README。

## 2. 模块边界

| 路径 | 职责 |
| --- | --- |
| `src/common/` | 跨模块配置、LLM、Discord、颜色和 cron 公共能力 |
| `src/mktnews/` | MKTNews 快讯抓取、分析、补发和推送 |
| `src/trump_watch/` | Truth Social 抓取、分析、补发和推送 |
| `src/research_feed/` | 多数据源采集、Step1/Step2 LLM 管道、数据账本（PostgreSQL 主库）、飞书同步、趋势股票和报告 |
| `src/research_feed/*/source.py` | 单一资讯源适配器；抓取与标准化应尽量封装在本目录 |
| `src/x_watch/` | X 高关注账号同步、帖子分析及多目标推送 |
| `src/admin_api.py` | 面向 Hermes/本地运维的最小权限管理 API |
| `scripts/` | 配置检查、数据层自检、迁移、回填和一次性维护脚本 |
| `tests/` | 自动化测试；测试不得依赖真实外网、真实 webhook 或生产数据库 |
| `docs/` | PRD、技术设计、架构审计和变更记录 |
| `data/` | 本地运行数据，不属于源码，不提交、不随意删除或覆盖 |

跨模块复用应优先放到 `src/common/`。不要复制一套新的 LLM 配置、环境变量解析、重试或推送实现，除非现有抽象确实不适用。

## 3. Git 分支工作流

- **`dev` 分支**：日常集成分支。
- **`main` 分支**：仅用于生产发布，禁止直接开发或提交。
- 新功能和修复：基于最新 `dev` 创建 `feature/*`、`fix/*` 或 `codex/*` 分支，完成后合并回 `dev`。
- 小型文档或仓库维护任务可按用户明确要求直接在 `dev` 修改，但提交前仍须确认不在 `main`。
- 生产发布：`dev` 合并到 `main`，创建 `vX.Y.Z` tag，再推送和部署。
- Tag 使用 SemVer：
  - `X`：不兼容或重大架构变更
  - `Y`：向后兼容的新功能
  - `Z`：向后兼容的问题修复

开始修改前执行：

```bash
git branch --show-current
git status --short
```

操作要求：

- 绝不在 `main` 上直接修改或 commit；若当前位于 `main`，先停止并切换到合适分支。
- 保留用户已有的未提交和未跟踪文件，不覆盖、不清理、不顺手纳入提交。
- 未经用户明确授权，不执行 merge、tag、push、发布或 `deploy.sh`。
- 不使用 `git reset --hard`、`git clean -fd`、强制推送等破坏性命令。
- commit 应聚焦单一目的，提交信息使用清晰的 `feat:`、`fix:`、`refactor:`、`test:`、`docs:` 或 `chore:` 前缀。

## 4. 本地开发与常用命令

首次安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r agent_docs/requirements.txt
```

配置与静态自检：

```bash
python scripts/check_config.py
python -m compileall -q src scripts tests
```

运行全部自动化测试：

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

运行单个测试：

```bash
python -m unittest tests.test_ctee_resilience
python -m unittest tests.test_x_watch_multi_feishu
```

本地启动全部服务：

```bash
python src/run_all.py
```

只在确有必要时单独启动具体模块；常驻监控会访问外网并可能产生真实 LLM 费用或消息推送。根目录的临时调试脚本（如 `test_discord.py`）不属于默认测试套件，不得在不确认目标 webhook 和影响的情况下运行。

## 5. 编码规范

- 以仓库现有 Python 风格为准，新增代码兼容 Python 3.13。
- 新增公共函数和复杂逻辑应添加类型标注；注释解释“为什么”，避免复述代码。
- 保持修改范围最小，不在功能修复中夹带大规模格式化或无关重构。
- 优先使用 `src/common/config.py` 的配置读取函数；必填项必须失败得清晰，布尔值沿用 `1/true/yes/on` 语义。
- 新增环境变量时，同步更新：
  1. 使用该变量的模块；
  2. 必要时更新 `scripts/check_config.py`；
  3. README 的 `.env` 示例和说明；
  4. Docker/部署配置（若容器需要显式传入）。
- 新增依赖前先确认标准库或现有依赖无法满足；若新增，固定到 `agent_docs/requirements.txt` 并验证 Docker 可安装。
- 外部请求必须设置超时。常驻循环不得因单条坏数据或一次网络失败永久退出，应沿用现有重试、退避、告警和健康状态机制。
- 抓取适配器应输出现有标准文章字段，保持 ID 稳定和去重语义；不要把来源特例扩散到主调度器。
- LLM 输出解析要容忍代码块、空字段和格式偏差，但不得静默伪造关键投资数据。
- 日志不得输出 API key、token、完整 webhook、Cookie、Authorization header 或包含凭据的 DSN。

## 6. HTTP、LLM 与推送的强约束

- **LLM 调用必须使用独立的 `requests.Session`，不得与抓取、Discord 或飞书推送共用。** 共享 Session 会导致 Cookie/请求头污染，并可能触发 latin-1 编码错误。
- 抓取、LLM、Discord、飞书等不同信任边界应各自维护 Session、代理和请求头。
- LLM provider、URL、模型和鉴权统一从 `src/common/llm_config.py` 获取；不要在业务模块硬编码新的 provider 默认值。
- 代理遵循现有 `PROXY_URL` 约定。CTEE 还支持 `CTEE_NETWORK_MODE` 和 `CTEE_PROXY_URL`，修改时须覆盖 direct、global_proxy、custom_proxy 三种模式。
- 推送逻辑必须支持失败重试并保持幂等。多目标推送时分别记录各目标状态，重试只发送失败目标，避免重复消息。
- 测试中必须 mock LLM、资讯源、Discord 和飞书请求；不得把真实凭据写入测试夹具。

## 7. 数据与迁移安全

- 数据库唯一后端为 PostgreSQL：`MARKET_NEWS_PG_DSN` 控制连接，`MARKET_NEWS_PG_DATABASE/USER/PASSWORD` 供启动前校验；不再提供 SQLite 后端或 `MARKET_NEWS_DB_BACKEND/DB_PATH` 配置。
- `data/`、`*.db`、`*.db-wal`、`*.db-shm`、seen/sent ID 文件都是运行状态，不提交到 Git。
- 自动化测试连接 PostgreSQL 测试库，每个测试使用独立 schema 隔离，并在测试后恢复被修改的模块级配置和环境变量。
- 不用生产数据库做开发测试，不删除或重建用户数据，不通过修改 seen/sent ID 文件制造重复推送。
- 表结构变更必须兼容已有数据库，优先采用可重复执行的增量迁移；不得假设数据库为空。
- 恢复手段是 PostgreSQL 备份：重要操作前执行 `pg_dump` 到 `data/backups/`，恢复流程为停应用→恢复→启动验证；历史 SQLite 快照仅作只读归档，不被运行路径引用。
- 回填、保留策略和清理脚本必须提供明确范围与批次限制；执行真实数据维护前需要用户确认并建议备份。

## 8. 测试要求

修改后至少运行与改动直接相关的测试，并优先补充回归测试。

| 改动类型 | 最低验证 |
| --- | --- |
| 纯文档 | 检查 diff、命令和路径是否与仓库一致 |
| 通用 Python 逻辑 | 目标单测 + `compileall` |
| 抓取源/解析器 | 使用固定响应的单测，覆盖成功、空结果、超时/封禁和去重 |
| LLM 分析/解析 | mock API，覆盖合法输出、缺字段、异常格式和失败重试 |
| 数据层/状态机 | PostgreSQL 测试库独立 schema 测试，覆盖初始化、升级、幂等和重试状态 |
| Discord/飞书多目标推送 | mock 各目标，覆盖部分失败及仅重试失败目标 |
| 环境变量/cron/启动入口 | `python scripts/check_config.py` + 相关单测 |
| Docker/依赖 | `docker compose config`；依赖或入口变化时再执行镜像构建 |

完整回归命令：

```bash
python -m unittest discover -s tests -p 'test_*.py'
python -m compileall -q src scripts tests
```

若因缺少凭据、网络或 Docker 无法运行某项验证，应明确记录未运行项和原因，不能声称已经通过。

## 9. 文档与变更同步

- 用户可见的功能、配置或运行命令变化应更新 `README.md`。
- 架构、数据模型或处理管道发生实质变化时，更新对应 `docs/tech-design-*.md`；需求语义变化时更新对应 PRD。
- 版本发布应更新 `docs/CHANGELOG.md`。
- 文档中的示例不得包含真实 token、chat_id、webhook、账号信息或生产 DSN；使用清晰占位符。
- 不为微小实现细节新增版本化 PRD/设计文档，优先更新当前有效文档。

## 10. 发布与部署

只有在用户明确要求发布/上线时才执行以下流程：

1. 确认 `dev` 工作区干净且测试通过。
2. 将 `dev` 合并到 `main`，禁止在 `main` 直接补提交。
3. 根据变更性质确定新的 `vX.Y.Z`，确认 tag 不存在。
4. 推送 `main` 和 tag。
5. 在 NAS 上运行 `deploy.sh` 或等价的 Docker Compose 命令。
6. 检查 `docker compose ps` 和服务日志，确认所有 `src/run_all.py` 子进程正常。
7. 如失败，保留日志并采取可回滚方案，不直接删除生产数据卷。

发布前重点检查：

- `.env` 未进入提交，新增配置已部署；
- 数据迁移向后兼容且已有备份；
- webhook/飞书群路由没有串用；
- LLM provider、模型名、代理和超时配置有效；
- Docker 镜像包含新增的运行时文件或脚本；
- tag 与 `docs/CHANGELOG.md` 一致。

## 11. 完成任务前检查清单

- 当前分支不是 `main`。
- `git diff` 只包含本次任务相关修改，没有覆盖用户已有工作。
- 新行为有测试，外部服务已 mock，测试未向真实渠道发送消息。
- 相关测试、`compileall` 和必要的配置检查已运行。
- 新增配置、依赖、入口、数据结构已经同步到对应文档和部署文件。
- 未提交 `.env`、数据库、日志、缓存、seen/sent ID 或其他运行数据。
- 最终说明列出修改内容、验证结果以及任何未验证风险。
