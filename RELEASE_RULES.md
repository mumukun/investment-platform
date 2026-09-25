# Release Rules

本文件定义 Investment Platform 的详细发布流程。原则与授权边界以 `AGENTS.md` 为准；
`mukun-release-manager` 负责按本文件执行，不得扩大授权。

## 1. Release 状态与记录

建议 Release ID 使用 `REL-YYYYMMDD-NNN`。实际 Manifest 从根目录 `RELEASE_MANIFEST.yaml` 复制为
`releases/<release_id>.yaml` 后填写，并随状态推进提交到本仓库。

状态流：

`DRAFT → READY_FOR_FORMAL_RELEASE → IN_PROGRESS → RELEASED`

异常状态：`BLOCKED`、`FAILED`、`PARTIAL`、`ROLLED_BACK`、`CANCELLED`。

Release 只包含明确选择且状态为 `READY` 的 Changes，以及这些 Changes 实际影响的仓库。不得因为仓库
在同一目录或系统图中存在就自动纳入。

## 2. 授权语义

| 用户表达 | 允许 | 禁止 |
| --- | --- | --- |
| 开发完成 | 完成测试、PR、合并 `main`、安全删除任务分支、Change 标记 `READY` | Tag、生产部署、Feature Activation |
| 准备发版 / 准备发布 / 封板 | 收集 READY Changes、预检、版本与 SHA freeze、依赖/契约检查、回滚计划、Manifest、release gates | 正式 Tag、Push Tag、生产部署、Feature Activation |
| 正式发布 | 创建并推送 Tag、构建/选择精确 Artifact、部署、smoke、集成/E2E、必要的 Feature Activation、closeout | 超出 Manifest 范围的仓库和变更 |

“合并 main”“打 Tag”“部署某环境”等动作型请求只授权其明确动作，不自动升级为完整正式发布。正式发布
授权只对当前请求明确的 Release、仓库和环境有效。

## 3. Prepare Release

准备发布按以下顺序执行：

1. 读取目标 READY Change 文件、`SYSTEM_MAP.yaml` 和已有 Manifest；确认范围而非扫描全部仓库。
2. 对每个受影响仓库读取有效 `AGENTS.md`，检查 Git status、目标 `main`、远端、worktree、未完成 Git
   操作、相关 diff、版本源、Tags 和已记录 CI/测试证据。
3. 锁定拟发布的精确 Commit SHA。工作区、未推送提交或来源不明的差异不得进入 freeze。
4. 根据 Change 依赖和已验证的系统关系计算 release order；未验证关系不得假装为确定依赖。
5. 验证跨仓库契约、最低兼容版本、数据库阶段和 Feature Flag/激活计划。
6. 按每仓实际变化独立计算 SemVer；未变化仓库不升级、不发布。
7. 记录每仓上一稳定生产版本。真实生产 Tag、SHA 或 Artifact 无法获取时填 `UNKNOWN`，关键回滚基线
   未知则 Release 不得进入正式发布。
8. 运行仓库要求的 release gates；证据必须对应被冻结的 SHA。代码、依赖、配置、迁移或合并结果变化
   后，相关证据失效并需重跑。
9. 写入 Manifest：Changes、仓库、旧/新版本、SHA、拟用 Tag、Artifact 计划、依赖、顺序、回滚、测试和
   验证计划。
10. 所有关键 gate 通过后标记 `READY_FOR_FORMAL_RELEASE`。此阶段不得创建正式 Tag、部署生产或启用 Feature Flag。

## 4. Version 与 Tag

- 各业务仓库独立采用 `MAJOR.MINOR.PATCH`。
- PATCH：向后兼容的 Bug、安全或小范围配置修复。
- MINOR：向后兼容的新功能、行为或公开能力。
- MAJOR：破坏性 API、运行时、数据或迁移变化；必须包含 migration plan。
- 正式 Tag 为 `vMAJOR.MINOR.PATCH`，必须映射到 Manifest 中冻结的唯一 Commit SHA。
- 已存在的 Tag 不移动、不覆盖、不复用。发布错误通过新版本修正。
- Artifact 必须记录可验证 identity 和 digest；禁止将 `latest` 作为正式身份。

## 5. Compatibility 与数据库门禁

跨仓库能力默认采用 Expand → Migrate → Contract：

1. Provider 先增加向后兼容字段、接口或能力；
2. 部署并验证 Provider；
3. Consumer 迁移读取/写入并验证；
4. 完成观测期和使用迁移；
5. 旧契约删除放入后续 Change/Release。

数据库默认采用 Add → Backfill → Migrate Read/Write → Verify → Remove Later。新增代码与删除旧列不得
默认在同一 Release 发生。破坏性契约或 Migration 必须独立审查、提升 MAJOR，并有恢复或前向修复方案。

## 6. Test 与 Release Gates

按受影响范围收集：

- Repository Test：各仓库规定的 lint、unit、migration、build；
- Contract Test：Provider schema、Consumer adapter、兼容与降级；
- Integration Test：真实依赖边界、鉴权、超时、幂等和 last-known-good；
- Critical-path E2E：少量稳定黄金链路，不默认扩大为脆弱 UI 测试集；
- Release Gate：版本/Tag/SHA 一致性、CI、备份、回滚、Artifact、配置和生产前检查。

测试必须注明来源是 fixture、非生产环境还是真实 Production；fixture 通过不能冒充生产联通成功。

## 7. Formal Release

只有明确“正式发布”授权后执行：

1. 重新验证 Manifest 为 `READY_FOR_FORMAL_RELEASE`，冻结 SHA、版本、依赖、顺序和回滚点未变化。
2. 确认所有关键 gate 仍有效；任一失败立即停止。
3. 为每个目标仓库在冻结 SHA 创建不可变正式 Tag，并只推送该精确 Tag。
4. 构建或选择由 Tag/SHA 产生的 Artifact，记录 identity 与 digest。
5. 按动态 release order 部署 Provider/Upstream；每一步完成版本检查、health、migration 和 smoke。
6. 上游成功后才部署 Consumer/Downstream；再运行 Contract、Integration 和 Critical-path E2E。
7. 需要 Feature Flag 时，仅在部署与端到端验证完成后启用，并单独记录激活验证与关闭路径。
8. 生产版本、Tag、SHA、Artifact、迁移、测试、时间、验证和回滚点完整落盘后标记 `RELEASED`。

正式发布不是跨仓库原子事务。中途失败时 Manifest 必须记录已 Tag、已推送、已部署和未部署的精确范围。

## 8. Fail Closed 与回滚

以下任一情况阻止继续：

- 生产基线或回滚版本未知；
- 冻结 SHA、Tag、版本源或 Artifact 不一致；
- 必需 CI/Test/Contract/Migration gate 失败或证据过期；
- 依赖关系、部署顺序或兼容策略无法确认；
- 备份不可读、回滚不可执行或关键配置未验证；
- 上游 smoke、版本检查或契约检查失败；
- 发现未纳入 Manifest 的代码或仓库。

失败后保留日志与证据，停止下游部署和 Feature Activation。应用优先回滚到 Manifest 记录的上一稳定
Tag/Artifact；数据库优先前向修复，只有 downgrade 已验证且不会丢失新数据时才回退。Release 根据真实
状态标记 `FAILED`、`PARTIAL` 或 `ROLLED_BACK`，不得伪报成功。

## 9. Release Branch 与清理

默认不创建 release branch。只有大型版本需要长期 Freeze/UAT 且 `main` 必须继续开发时，才允许明确
创建 `release/x.y`；其基线、包含范围、修复回灌和删除条件写入 Manifest。Release 成功后安全删除。

正式发布 closeout 只能清理 Manifest 明确列出且属于本次 Release 的临时分支。清理前需核验 PR 已合并、
分支尖端无独有成果、无未提交/未推送内容、无活跃 worktree、依赖 PR、CI 或其他使用者，且不属于受保护或
历史归属不明分支；Squash/Rebase 需结合平台合并证据，不能只看祖先关系。任一条无法证明时标记 `REVIEW` 并保留分支。

## 10. 上下文效率

Release 阶段只读取 Change 文件、系统图、Manifest、相关 AGENTS、Git status/diff、版本源、Tags、CI 和测试
结果。禁止默认重新扫描完整源码。只有 gate 失败、证据不一致或兼容性无法判断时，才深入受影响模块。
