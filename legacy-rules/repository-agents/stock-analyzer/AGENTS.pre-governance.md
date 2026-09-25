# stock-analyzer 项目约束

个人股票自选池追踪 + 盯盘决策辅助 + 全 A 盘中短线选股引擎。以项目自有 PostgreSQL 作为自选、行情、规则结果和事件的唯一事实源，Python 计算量化信号，并通过版本化契约向投研看板（`investment-research-dashboard`）提供能力。飞书仅作为可关闭的通知或报表承载，不得进入业务查询和计算的同步依赖。本文件是 AI 协作与人工开发的最高约束，与 README.md / SECURITY.md 冲突时以更严格者为准。

## 产品定位红线

- 只做决策辅助：输出信号、风险提示与研究结论，不自动下单，不读取券商账户，不承诺收益。
- 引擎输出的是研究候选与状态，不是买卖指令；"可计划参与"表示系统条件满足，须人工确认。
- 市场环境不适合时允许输出"今日无可参与候选"，不为凑数降低标准。
- LLM 只用于解释公告、题材与结论，不得生成或修改量化评分。
- 60 日趋势与 PE/PB 等估值指标不参与短线选股评分（可服务独立中线报告）。

## 安全约束

- 飞书、大模型、行情源等凭证与资源 ID 只存在于 `.env` 或部署环境变量，不写入代码、文档、日志与测试。
- 对外服务必须鉴权；集成契约使用服务端到服务端 Bearer Token。
- 脚本与调度任务默认支持 `--dry-run`，写操作先可预演。

## 数据与职责边界

- PostgreSQL 是唯一主数据中心；自选池、候选层状态、分钟快照、规则结果、策略服务快照与事件账本均由项目自有表持久化。
- 飞书 Bitable、电子表格和机器人均为可选承载：只允许接收 PostgreSQL 派生的导出或通知，关闭或失败不得影响行情、规则计算、内部 API、Dashboard 查询和容器冷启动；禁止双主写入。
- 禁止直接读写其他项目的数据库或内部字段；与看板、其他上游的协作一律走版本化公开契约。
- 上游主数据（自选池、行业映射、证券主数据）只在本项目修改；看板不得通过契约反向更新本项目。
- 每日证券主数据（涨停价、跌停价、涨跌幅限制、ST、上市日期等）必须按交易日维护，不得按股票代码近似推断交易规则。

## 对投研看板的契约义务

- 查询契约只读、版本化、Bearer 鉴权；自选股仅开放已确认的新增、暂停和恢复窄命令。字段定义与演进记录在 `docs/hermes-api.md` 与当前 PRD-v3.9 第十六、十七章。
- 所有实时数据必须带 `data_time` 与 `generated_at`；数据过期显式标记 `degraded`，不得伪装实时。
- 上游不可用、契约不匹配、数据过期必须成为看板可见的状态，不返回空响应冒充正常。
- 隐私最小化：契约不含成本价、持仓数量、持仓状态与账户信息。
- 契约破坏性变更需要新版本号；当前 V4 经用户确认直接替换旧波段算法，不保留 V3 运行或兼容分支。

## 文档惯例

- PRD 按版本存放于 `docs/prd/`（当前方向：`PRD-v4.0.md` 趋势优先的全 A 5～20 日波段结构选股，状态：已确认并进入开发）。
- 集成契约字段与示例维护在 `docs/hermes-api.md`。
- 重要变更更新 `CHANGELOG.md`；阈值调整必须关联 `rules_version` 并保留历史。

## 引擎实现地图（PRD-v3.8 阶段一~二已落地的部分）

- `stock_analyzer/short_engine.py`：确定性规则核心（市场状态六态、板块六维评分与生命周期、八类角色、机会分/风险分双轨与档位硬否决、同题材上限、状态机两周期确认、同时段量比）。所有阈值集中在常量区，调整必须更新 `RULES_VERSION`；纯函数、无 DB/网络访问，`tests/test_short_engine.py` 覆盖。
- `stock_analyzer/short_engine_store.py`：P0 数据表读写（`security_trade_rule` 每日证券主数据、`short_candidate_snapshot` 状态连续性、`short_signal_event`/`short_signal_outcome` 结果账本）。表 DDL 集中在 `local_db.py`，只新增不破坏。
- `stock_analyzer/short_engine_contract.py`：唯一短线契约（`investment-dashboard-short-selection-engine-v1`、`investment-dashboard-market-regime-v1`）；盘中量价（VWAP/同时段量比）未接入前显式标记 `intraday_coverage=missing` 并封顶"等待确认"（§20.2），不得伪造升级。
- 环境变量：`SHORT_SELECTION_ENGINE_ENABLED` 默认开启，仅作为运维停机开关；端点停用时返回 503，不回退旧算法或旧契约。
- 开发库：`shared-postgres`（127.0.0.1:5433，用户 admin）中项目自持数据库 `stock_analyzer`，schema 由 `local_db.connect()` 首次连接自动创建；引擎结果账本评估口径（MFE/MAE、路径标签）见 PRD §17.6。

## 波段结构引擎实现地图（PRD-v4.0）

- V4 趋势优先口径：趋势通道为主路径，低位蓄势与突破回踩为辅助；首次突破只确认，结构、量价、市场/板块和 ATR 风险共同决定参与状态。

- `swing_features.py` / `swing_engine.py`：独立计算 5～20 日结构特征、120 日位置、三条路径完成度、同组分位与状态机，不导入遗留短线引擎。
- `swing_daily_data.py` / `swing_runtime.py`：日线快照、收盘扫描及盘中完整 5 分钟确认；同时段成交额覆盖不足时保持等待确认。
- `swing_store.py` / `local_db.py`：自有特征、结构、状态事件、分钟快照和结果账本，仅做增量表结构变更。
- `swing_outcomes.py` / `swing_contract.py`：理论成交与 T+1/3/5/10 日结果回填，以及 selection/history/stats 三个版本化只读契约。
- 环境变量：`SWING_ENGINE_ENABLED` 默认开启、`SWING_ENGINE_SHADOW_MODE` 默认关闭；V4 直接运行，不保留旧波段链路。

## 开发与验证

- 修改规则、契约或数据模型时，同步更新 `tests/` 中对应的契约与规则测试。
- 短线规则变更以独立 `RULES_VERSION` 隔离历史；发布前使用最近完整交易日数据验证，不保留旧算法运行分支。
- 回测验证按时间滚动，禁止随机拆分时间序列；不得用过拟合阈值宣称策略有效。

## Git 分支与任务隔离

- 当前有效开发模型是 `main + 短期任务分支 + 发布 Tag`。`main` 是稳定主线和默认合并目标，不直接承载普通开发。
- 远端若仍存在 `dev`，视为历史或专项维护线；当前任务未明确指定时，不从它创建新任务、不把发布内容合入它，也不擅自删除它。
- 普通任务从已经确认并成功更新的 `origin/main` 创建，默认命名：
  - 功能：`codex/feat/<short-name>`
  - 修复：`codex/fix/<short-name>`
  - 重构：`codex/refactor/<short-name>`
  - 性能：`codex/perf/<short-name>`
  - 文档：`codex/docs/<short-name>`
  - 测试：`codex/test/<short-name>`
  - 工程：`codex/chore/<short-name>`
  - 紧急修复：`codex/hotfix/<short-name>`
  - 发布候选：`codex/release-vX.Y.Z`
- 一个独立目标对应一个短期分支。同一未合并任务的后续修改复用原分支；已合并分支不承接新工作。
- 修改前必须检查 `git status --short --branch`、`git branch --show-current`、`git worktree list`、真实远程和默认分支，并记录基线 Commit。fetch 失败时不得声称已同步最新代码。
- 当前位于 `main` 且任务需要写入时，先创建任务分支。存在其他任务改动或需要并行开发时，使用独立 worktree，不移动、stash、清理或提交用户已有文件。
- 已确认远程和基线后，普通任务可使用 `git fetch --prune origin` 与 `git switch --no-track -c codex/<type>/<name> origin/main` 创建；不得使用 `switch -C`、`checkout -B` 重置同名分支。
- Codex 管理的 worktree 可能处于 detached HEAD。推送、交接或清理前先保护当前 Commit、未提交和未跟踪成果，再从该成果创建可追踪分支；不得为恢复分支名称而重置到 `main`。
- worktree 只隔离文件和 Git 状态，不隔离 PostgreSQL、端口、容器或外部服务；并行任务必须使用独立测试 schema、端口或明确共享边界。
- 不使用 `git reset --hard`、`git checkout --`、`git clean -fd`、普通 `--force` 或模糊通配符处理分支与工作区。

## 授权、Commit 与同步

- 普通“修改”或“修复”只授权编辑和验证，不自动授权 Commit、Push、PR、Merge、Tag、生产部署或远程分支删除。
- “提交”只授权本地提交；“推送”或“创建 PR”才授权推送当前任务分支；合并 `main`、生产发布、Tag 和分支清理分别以当前任务的明确授权为准。
- Commit 使用 Conventional Commits，例如 `feat:`、`fix:`、`refactor:`、`perf:`、`docs:`、`test:`、`chore:`、`release:` 或 `merge:`；每个 Commit 只包含一个可审查目标。
- 提交前检查 `git diff`、`git diff --stat`、`git diff --check`，只暂存明确文件，不使用 `git add .` 吞入来源不明的改动。
- 已推送或多人共享的任务分支通过合并目标分支同步；未经确认不 rebase、不重写历史。确需覆盖未共享分支时也只能在明确授权后使用限定目标的 `--force-with-lease`。
- 解决冲突时理解双方意图并重新运行受影响验证，不通过整文件覆盖或仅消除冲突标记来判断完成。

## PR 与合并

- 默认通过 PR 合入 `main`。不得因为“代码已完成”自动合并；PR、合并和发布均遵循当前任务授权。
- PR 前同步并确认 `origin/main`，检查范围、测试、契约、配置、迁移、CHANGELOG、已知限制和回滚方式；Codex 自检不能替代仓库要求的人工审查与 CI。
- PR 说明至少包含目标、主要改动、验证证据、数据或契约影响、风险、已知限制和回滚点。
- 没有现有约定时，单一短任务优先 squash；需要保留多分支整合或发布关系时使用 merge commit。禁止通过重写受保护分支绕过检查。

## 测试与发布门禁

- 通用 Python 改动至少运行目标单测、`python -m compileall -q stock_analyzer scripts tests` 和 `git diff --check`；发布前运行完整 `python -m unittest discover -s tests -p 'test_*.py'` 与 `python scripts/check_config.py`。
- 规则、市场日期或行情变更必须覆盖正常、缺失、陈旧、非交易日、上游拒绝和最后健康快照降级路径；不得只验证 HTTP 200。
- PostgreSQL 表结构或批量数据操作必须使用向后兼容、可重复执行的迁移；生产执行前创建并验证备份，禁止用生产库做测试。
- 契约修改同时更新契约模型、调用方兼容说明、测试和 `docs/hermes-api.md`；破坏性变化必须使用新 `contract_version`。
- 发布准备仅包括版本、CHANGELOG、候选分支、完整验证和推送候选分支，不合并 `main`、不打 Tag、不部署生产。

## 正式发布与回滚

- 只有用户在当前任务明确要求合并 `main`、打 Tag 或发布生产时才执行正式发布。历史授权和其他仓库的发布授权不得沿用。
- `stock_analyzer/version.py` 中的 `APP_VERSION` 是应用版本来源；`CHANGELOG.md` 的目标版本和 `vX.Y.Z` Tag 必须一致。规则、契约和映射版本独立演进，不随应用版本自动递增。
- 正式发布顺序：确认范围与回滚点 → 完整门禁 → 合入并推送 `main` → 从已推送且验证过的 `main` Commit 创建 annotated Tag → 只推送该 Tag → 部署 → 生产 smoke。
- 当前 `deploy.sh` 会更新并部署 `main`，不接受 Tag 参数。部署前必须确认 `origin/main`、目标 Tag 和待部署 Commit 三者完全相同；部署后确认 NAS `HEAD` 仍精确匹配该 Tag。若不相同则停止，不得把浮动 `main` 冒充 Tag 发布。
- 数据库或运行状态可能受影响时，先记录上一稳定 Tag 并创建可读备份；验证失败时停止后续动作，优先回滚应用到上一稳定 Tag，不用临时假数据或未审查兼容层掩盖失败。
- 生产验证至少包括容器状态、错误日志、`/api/health` 的应用版本、鉴权、受影响契约、实际数据交易日、`generated_at`、质量状态、非模拟标记、PostgreSQL 连接和调度器状态。

## Hotfix

- 先确认真实生产 Tag、Commit 和影响范围。只有 `main` 与生产基线一致时才从 `main` 创建 `codex/hotfix/<name>`；否则从实际生产 Tag/Commit 或指定维护线创建。
- Hotfix 只包含恢复生产所需的最小修复，运行完整相关门禁，合入 `main` 后创建新的 Patch Tag，不移动既有 Tag。
- 修复必须回灌仍需该修复的维护线，避免后续版本回退；生产验证成功后再按普通短期分支规则清理。

## 合并证据与分支清理

- 普通任务分支只有在确认合入正确目标、分支尖端没有新增独有提交、没有未提交或未推送成果、没有开放/依赖 PR、流水线或活跃 worktree 使用时才可清理。
- 普通 merge 可用 `git merge-base --is-ancestor` 和 `git branch --merged` 辅助核验；Squash/Rebase 合并必须结合平台合并记录、源 SHA 和最终 diff，不能仅凭提交不可达判断“未合并”。
- 正式发布不自动授权删除远程分支。只有用户明确要求“发布并清理分支”或单独授权时，才删除本次范围内已经核验的精确分支。
- 清理顺序：安全移除不再需要的 worktree → 删除精确远程分支 → 使用 `git branch -d` 删除本地分支 → `git fetch --prune` 复核。`-d` 失败时报告原因，不自动升级为 `-D`。
- 永久保留 `main`、仓库明确指定的维护线和所有发布 Tag。分支是工作空间，不是版本档案。

## 完成报告

- 明确报告当前分支、最终 Commit、变更范围、验证证据、文档/版本/CHANGELOG 状态、未包含的用户改动和已知风险。
- 明确区分仅本地修改、已提交、已推送、已合并 `main`、已打 Tag 与已部署生产；涉及生产数据时报告实际数据日期、质量、最后成功时间和回滚点。
- 列出已删除的分支，以及因证据或授权不足而保留的分支，不用“已完成”替代真实发布状态。
