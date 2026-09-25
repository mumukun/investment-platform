# Investment Platform Governance

治理规范版本：1.0（2026-09-25）。

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
- Change 在开发、测试、PR、合并和分支清理全部完成后才能标记 `READY`。
- “开发完成”表示：测试通过、PR 满足要求、已合入 `main`、临时分支已安全删除、Change 已进入
  `READY`；它不授权创建 Tag 或部署生产。

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

## 8. 测试与发布顺序

平台级证据分为 Repository Test、Contract Test、Integration Test 和 Critical-path E2E。允许少量
稳定黄金链路 E2E，不默认引入大规模浏览器测试、截图回归或脆弱 DOM selector 测试。

发布范围和顺序根据 `SYSTEM_MAP.yaml` 与当前 Change 的真实依赖动态计算，遵循 Provider/Upstream
→ Consumer/Downstream。每个上游部署和 smoke 成功后才继续下游；不相关仓库不得进入 Release。

## 9. 上下文效率与状态文件

开始新需求时按顺序读取：当前请求、对应 Change 文件、`SYSTEM_MAP.yaml`，然后只搜索相关模块和
受影响仓库。Release 阶段优先读取 Change 文件、Git status/diff、Tags、CI、测试证据和 Release
Manifest；禁止默认重新阅读完整源码，只有 gate 失败或证据不足时才深入。

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
