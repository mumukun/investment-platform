# Investment Platform Governance

治理规范版本：1.1（2026-10-11）。

本仓库是 `marketNewsFeed`、`stock-analyzer` 与
`investment-research-dashboard` 的 Control Plane / Governance Repository。它管理跨仓库
Change、依赖、Git、版本、发布、契约、集成测试和 Hotfix；不承载业务代码，不是
Monorepo，也不是其他仓库的父 Git Repository。

## 1. 规则优先级

治理规则按以下顺序解释：

1. 用户当前明确指令；
2. 本文件；
3. 目标业务仓库的 `AGENTS.md`；
4. Skill；
5. Script / CI 实现。

业务仓库可以定义自己的构建、测试、数据库、运行时和部署实现，但不得重新定义平台统一的
Change ID、分支模型、`main` 语义、发布授权、版本治理和跨仓库发布模型。发现冲突时停止相关
写操作，在 Change 文件中记录冲突并请求处理，不静默选择较低优先级规则。

## 2. 仓库边界

- 四个仓库保持完全独立，不使用 Git Submodule，不复制业务源码到本仓库。
- `SYSTEM_MAP.yaml` 记录路径、角色、依赖、版本源、部署入口、健康检查和契约文档。
- 只操作当前 Change 明确涉及的仓库；不得默认修改或发布全部仓库。
- 跨仓库提交分别保存在各自仓库，不创建跨仓库混合 Commit。
- 本仓库的治理文件和状态文件必须提交后才成为共享事实；聊天记录不替代持久化状态。

## 3. Change 模型

- 一个业务需求对应一个 Change ID：`CHG-YYYYMMDD-NNN`。
- 一个 Change 使用一个 Codex 对话和一个 `changes/<CHANGE_ID>.md` 文件。
- 新 Change 从 `changes/TEMPLATE.md` 建立；已有 Change 优先读取其状态和证据，不重新发现全部上下文。
- Change 只列真实受影响仓库、依赖、接口、数据库、兼容策略、测试、回滚和发布影响。
- 日常 Change 使用精简模板；没有变化的接口/数据库/契约不逐项填写 None，不复制测试日志。
- Change 在开发、必要测试、PR 和合并完成后即可标记 `READY`；安全分支清理放在收尾，不阻塞发布。
- 业务 PR 合并且必要检查通过后，可先将本地 Change 标记 `READY`；不为状态更新单独开治理 PR
  或等待其 CI。发布后统一归档提交，共享事实仍以已提交的记录为准。
- “开发完成”表示：测试通过、PR 满足要求、已合入 `main`、Change 已进入 `READY`；临时分支允许
  记录待清理。它不授权创建 Tag 或部署生产。

## 4. 分支与 `main`

普通分支格式：

- `feat/CHG-YYYYMMDD-NNN-description`
- `fix/CHG-YYYYMMDD-NNN-description`
- `hotfix/CHG-YYYYMMDD-NNN-description`

一个 Change 涉及多个仓库时，各仓库使用同一 Change ID，但只在确实受影响的仓库创建分支。
分支是临时工作空间；合并后在确认 PR、独有提交、未推送内容、worktree、CI 和依赖均已解除后
删除。历史由 Commit、PR、Change、Tag 和 Release Manifest 保存。

原则上唯一长期分支是 `main`。`main` 必须始终可构建、可测试、可发布，可以领先 Production，
但不得直接承载普通开发。默认禁止 release branch；只有大型版本需要长期 Freeze/UAT 且 `main`
仍需接收其他开发时，才可经明确决定创建临时 `release/x.y`，发布后删除。

## 5. Production、版本与 Tag

- Production 身份必须是不可变 `vMAJOR.MINOR.PATCH` Tag 与精确 Commit SHA；不得使用浮动
  `main` 或 `latest`。
- 当前生产身份无法从真实环境确认时记录 `UNKNOWN`，不得根据本地分支或最新 Tag 推测。
- 每个业务仓库独立使用 Semantic Version；只有发生代码变化的仓库升级版本。
- PATCH 是向后兼容修复，MINOR 是向后兼容功能，MAJOR 是破坏性变化。
- Tag 禁止移动、覆盖或复用，且必须能追溯到 Release Manifest。
- `marketNewsFeed` 后续建立根目录 `VERSION`，并在运行时暴露 Version、Commit SHA 和 Build Time；
  在对应 Change 实施前只记录该决策，不修改业务仓库。

## 6. 发布授权

“准备发版”“准备发布”“封板”含义相同，只授权收集 `READY` Changes、预检、依赖与契约检查、
版本和 Commit freeze、回滚计划、Release Manifest 与 release gates。它们禁止正式 Tag、生产部署和
Feature Activation。

本项目为单人自用，默认执行 `RELEASE_RULES.md` 的日常精简流程。正式发布请求可在同一轮完成
简短准备和发布，不要求先单独“准备发版”、反复确认或逐阶段提交治理 PR。

只有用户在当前请求中明确说“正式发布”或给出明确等价授权，才允许创建并推送不可变 Tag、部署
精确 Tag/Artifact、生产 smoke、集成/E2E 验证、必要的 Feature Activation 和 Release closeout。
详细流程以 `RELEASE_RULES.md` 为准；任何关键 gate 失败都必须 fail closed。

## 7. 兼容性、数据库与 Feature Flag

- 跨仓库修改默认向后兼容，优先采用 Expand → Migrate → Contract。
- 同一 Release 默认不得同时增加替代接口/字段并删除旧接口/字段。
- Breaking Change 必须明确标记、单独分析、提升 MAJOR，并提供 migration plan。
- 数据库迁移默认采用 Add → Backfill → Migrate Read/Write → Verify → Remove Later；破坏性
  migration 单独审查。
- 高风险、跨仓库、用户可见或需要灰度的能力优先分离 Deployment 和 Feature Activation；
  Feature Flag 不是所有功能的强制要求。
- 单人自用的普通功能随部署直接生效，不仅因用户可见或涉及两个仓库就新增 Feature Flag、
  灰度、观察期或独立激活步骤；已有开关按实际用途处理。

## 8. 测试与发布顺序

平台级证据分为 Repository Test、Contract Test、Integration Test 和 Critical-path E2E。允许少量
稳定黄金链路 E2E，不默认引入大规模浏览器测试、截图回归或脆弱 DOM selector 测试。
复用冻结 main SHA 的本地/CI 证据；正式发布不重复全套测试、隔离数据库恢复、旧镜像兼容、
发布器中断/回滚演练。演练默认不执行；数据库、契约、部署或恢复机制变化优先本地针对性测试，
仅已识别且未能排除的实际数据安全风险需要另行确定最小验证。未受影响的能力不重验。

发布范围和顺序根据 `SYSTEM_MAP.yaml` 与当前 Change 的真实依赖动态计算，遵循 Provider/Upstream
→ Consumer/Downstream。每个上游部署和 smoke 成功后才继续下游；不相关仓库不得进入 Release。

## 9. 上下文效率与状态文件

开始新需求时按顺序读取：当前请求、对应 Change 文件、`SYSTEM_MAP.yaml`，然后只搜索相关模块和
受影响仓库。Release 阶段优先读取 Change 文件、Git status/diff、Tags、CI、测试证据和 Release
Manifest；禁止默认重新阅读完整源码，只有 gate 失败或证据不足时才深入。
已读取且未变化的规则无需每阶段重读；提交后不默认再开一轮全量代码审查。

实际 Release Manifest 应从根目录 `RELEASE_MANIFEST.yaml` 模板生成并保存为
`releases/<release_id>.yaml`。Release 状态、Tag、SHA、Artifact、验证和回滚点必须落盘。

## 10. Skills 与完成报告

- `change-manager` 管理 Change，不发布生产。
- `mukun-release-manager` 是唯一正式 Release Governance Skill，管理准备发布和经明确授权的正式发布。
- `hotfix-manager` 管理真实生产基线上的紧急修复，并复用统一发布规则。
- 旧 `mukun-deploy-ready` 已完整归档并移出 Active Skills；不得执行其冲突语义。
- `dashboard-contract-check` 保留为契约专项能力。

完成治理任务时报告修改文件、验证结果、涉及和排除的仓库、当前 Git 状态、未解决风险及下一步。
没有明确授权时，不 Commit、Push、Merge、Tag、部署、启用 Feature Flag 或删除远程分支。

## 11. Product design guidance

Dashboard 的新增与修改界面统一遵循业务仓库 `docs/design/product-design-system.md`，覆盖配色语义、排版、组件、运行状态与异常行为。平台入口见 [产品设计指导](docs/product-design-guidance.md)。不以历史原型替代现行规范，不因此改变业务数据、契约或发布授权。


## 11. NAS 外网下载与代理默认（2026-10-16）

- 用户2026-10-20明确要求：国内股票相关数据请求直接连接来源，不使用HTTP/HTTPS/SOCKS代理，不在失败后自动切换代理。腾讯、新浪等股票数据适配器应避免继承进程环境代理；既有模块的代理例外不得覆盖此要求。本条是实施约束，不表示所有现有入口已完成修复。
- 下述mihomo默认仅用于GitHub、GHCR、包管理器等外网依赖下载，不用于国内股票数据采集。它不授权生产配置修改、重启或发布。
- DS920plus 的外网 HTTP/HTTPS 下载默认使用现有 mihomo `http://127.0.0.1:7890`；包括 GHCR 镜像与同类依赖下载。先读 [NAS 代理指引](docs/nas-outbound-proxy.md)，不凭应用代理变量推断 Docker 拉取路径。
- Docker daemon 的实际 JSON 字段为 **`HttpProxy` / `HttpsProxy` / `NoProxy`**，区分大小写；字段缺失记 UNKNOWN，不能解释为直连。优先复用 `scripts/check_docker_proxy.py`。本机现有 systemd drop-in 已生效，不为每次发布重复改配置/重启。
- NAS 登录 shell 已加载 `$HOME/.config/investment-platform/proxy.sh`；非交互 SSH 的 HTTP/HTTPS 下载先显式 source 此文件。保留本地/内网直连与已有业务容器出口；SSH Git 仍走既有 SSH 配置，不把 HTTP 代理当作 SSH 代理。
- 默认不做直连比较或静默绕过代理；明确排障才用 `--compare-direct`。EOF、代理可达、私有仓库鉴权和镜像传输分别判断，不把 GHCR `/v2/` 的未认证401当成断网。
- GHCR 失败时保留冻结 SHA/Tag/CI Artifact，使用既有受限发布器支持的同一精确镜像传输/缓存校验，不改凭据、镜像身份、权限或发布门禁。其他对话必须沿用本默认。

## 12. 东方财富来源使用约束（2026-10-20）

- 用户再次明确：个股数据只使用腾讯和新浪，未经用户明确同意不得扩大来源范围。用户随后追加整仓来源核查、可等价替代的东财入口替换，以及系统字段/功能与供应商解耦；CHG-20261020-003追加范围覆盖此前仅波段的限制，但不授权新增数据商、推送、合并或发版。
- 用户明确要求：东方财富数据经常不可用，使用前必须取得用户针对具体用途的明确同意。未经同意不得新增、启用、恢复或调用东方财富数据源，包括默认源、自动备用、补数、故障修复和诊断探测；直接HTTP和AKShare等封装调用同样受限。
- 不得把“已有备用源”、旧配置、旧文档例外或其他接口的授权当作本次同意。获准使用某项接口不自动授权其他用途；缺少腾讯/新浪等已允许来源的数据时保留明确缺失或标明日期的历史，不自行回退东财。
- 已确认的线上遗留调用必须记录为待整改，不得仅修改文档就宣称已停用；本要求不授权删除历史数据、擅自停用整个生产服务、重启或发布。

## 13. 行情与供应商解耦约束（2026-10-20）

- 用户要求系统字段与业务功能不得强行依赖某个供应商；通用数据经中性字段/单位/日期/复权及能力适配边界，默认仅腾讯和新浪，可按已实现能力切换。未来新增来源必须先获授权并完成适配/契约验证，不要求页面/策略读取厂商原始列名。
- 同名行业、资金口径、指数或ETF价格/净值不自动等价；无法替代的能力明确缺失，保存历史，不以改名、拼接或估算绕过完整性要求。来源/分类身份用于追溯，不应成为通用业务的厂商开关。
- 跨仓来源清单及限制见[股票数据来源核查](docs/stock-data-sources.md)。本轮未发布，不以本地代码整改宣称生产行为已改变。
