# Governance Decisions

- 状态：Accepted
- 生效日期：2026-09-25

| ID | Decision |
| --- | --- |
| GOV-001 | `investment-platform` 是纯治理 Control Plane Repository，不承载业务代码。 |
| GOV-002 | 项目群不采用 Monorepo。 |
| GOV-003 | 项目群不采用 Git Submodule。 |
| GOV-004 | `main` 必须可构建、可测试、可发布，并且可以领先 Production。 |
| GOV-005 | Production 身份是不可变 Git Tag + 精确 Commit SHA，不是浮动 `main` 或 `latest`。 |
| GOV-006 | 一个业务需求对应一个 `CHG-YYYYMMDD-NNN` Change。 |
| GOV-007 | 一个 Change 使用一个 Codex 对话和一个持久化 Change 文件。 |
| GOV-008 | Feature/Fix/Hotfix 分支是临时工作空间，合并并核验后删除。 |
| GOV-009 | 默认不使用 release branch；仅大型长期 Freeze/UAT 可临时使用 `release/x.y`。 |
| GOV-010 | “准备发版”“准备发布”“封板”不等于“正式发布”。 |
| GOV-011 | 只有用户明确授权“正式发布”或明确等价动作，才允许正式 Tag 和 Production Deployment。 |
| GOV-012 | 跨系统修改默认 Backward Compatible，优先 Expand → Migrate → Contract。 |
| GOV-013 | Release Manifest 必须落盘，不能只存在于聊天上下文。 |
| GOV-014 | Release 阶段不默认扫描完整源码；优先使用 Change、diff、Tag、CI、测试和 Manifest。 |
| GOV-015 | 旧 `mukun-deploy-ready` 的有效能力已迁移到 `mukun-release-manager`；完整归档保留，Active 副本已移出，状态为 `ARCHIVED_INACTIVE`。 |
| GOV-016 | Dashboard 允许少量稳定的关键路径 E2E，不默认扩展大量 UI/截图/DOM 自动化。 |
| GOV-017 | `marketNewsFeed` 后续建立根 `VERSION`，运行时暴露 Version、Commit SHA、Build Time。 |
| GOV-018 | 三个业务仓库的真实 Production Tag、SHA 和 Artifact 必须后续从运行环境确认；当前记为 `UNKNOWN`。 |
| GOV-019 | Repository AGENTS migration completed；平台治理集中于 `investment-platform`。 |
| GOV-020 | 业务 Repository 的 `AGENTS.md` 只保留项目自身技术指令，不再重复 Change、Branch、Version、Release 或 Hotfix 治理。 |
| GOV-021 | `mukun-release-manager` 是 Investment Platform 唯一正式 Release Governance Skill。 |
| GOV-022 | STEP 1 `release-manager` 原始版本已归档，不再作为 Active Skill。 |
| GOV-023 | Global Codex rules 不再强制任何项目专属的分支前缀、集成分支或 release-candidate 模型。 |
| GOV-024 | Investment Platform 的分支与发布治理仅由 `investment-platform/AGENTS.md` 和 `investment-platform/RELEASE_RULES.md` 定义；Repository AGENTS 只保留项目技术约束。 |
| GOV-025 | `investment-platform` 在 unborn `main` 上直接创建首个 Governance Baseline Commit 是一次性 `BOOTSTRAP_EXCEPTION`；在存在稳定 base 后必须恢复正常 Change Branch 流程。 |
| GOV-026 | Governance-only / `NON_RELEASE_CHANGE` / `Release Impact: NONE` Change 即使为 `READY`，也不进入业务 Release，不分配 Release ID、不升级版本、不 Tag 且不部署。 |
