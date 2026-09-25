# Repository AGENTS Migration Report

- 状态：Completed
- 日期：2026-09-25
- 范围：`marketNewsFeed`、`stock-analyzer`、`investment-research-dashboard`
- STEP 5 规则入口收敛：Completed

## 1. Archive Verification

旧文件在改写前已逐字归档，并以 `cmp` 与 SHA-256 确认归档内容和原文件一致。

| Repository | Archive | Original Lines |
| --- | --- | ---: |
| marketNewsFeed | `legacy-rules/repository-agents/marketNewsFeed/AGENTS.pre-governance.md` | 199 |
| stock-analyzer | `legacy-rules/repository-agents/stock-analyzer/AGENTS.pre-governance.md` | 138 |
| investment-research-dashboard | `legacy-rules/repository-agents/investment-research-dashboard/AGENTS.pre-governance.md` | 123 |

## 2. Migration Summary

| Repository | Old Governance | New Governance | Preserved Technical Rules | Removed Governance Rules |
| --- | --- | --- | --- | --- |
| marketNewsFeed | `dev` 长期集成；feature/fix/codex → `dev`；发布时 `dev → main`；仓内定义 SemVer 和发布步骤 | 平台治理引用；仓内仅定义技术、数据、契约、验证、部署实现 | Python 3.13、`src/run_all.py`、模块边界、配置检查、unittest、compileall、PostgreSQL、迁移、备份、API/webhook、降级、NAS/Compose | `dev` 集成主线、无 Change ID 分支格式、`main=Production` 语义、仓内发布授权和发布步骤 |
| stock-analyzer | 仓内定义 `codex/<type>`、release candidate、发布授权、Tag、Hotfix 和分支清理 | 平台治理引用；仓内保留 stock 分析领域与运行约束 | 决策辅助红线、Python 引擎、PostgreSQL 独立 schema、dry-run、契约与规则版本、测试、API、调度器、健康检查 | `codex/*` 命名、候选分支、版本 bump、正式发布、Hotfix 和清理流程 |
| investment-research-dashboard | 仓内定义 `codex/<type>`、release candidate、授权语义、SemVer、Tag、发布和清理 | 平台治理引用；仓内保留 Dashboard 技术与产品安全约束 | Vue/FastAPI/PostgreSQL、双平行 Provider、integration clients、LKG/stale、Vitest/pytest/Ruff/Alembic/build、关键路径 E2E、VERSION、health/smoke | `codex/*` 命名、候选分支、发布授权、SemVer 决策、Tag/Release/cleanup 流程及全面禁止 E2E 的旧规则 |

## 3. Current Repository AGENTS Scope

三份新文件均只回答项目角色、集成方向、代码结构、启动、测试、构建、版本源、契约、数据库、
部署实现、健康检查和项目独有安全约束。Change ID、Branch、`main`、Version Governance、Release
Authorization、Tag、Manifest、Hotfix 和 Branch Lifecycle 集中由 `investment-platform` 管理。

当前行数：

| Repository | New Lines |
| --- | ---: |
| marketNewsFeed | 121 |
| stock-analyzer | 120 |
| investment-research-dashboard | 134 |

## 4. Preserved Deployment Evidence

- marketNewsFeed：`deploy.sh` 拉取浮动 `main`，标记 `NON_COMPLIANT`。
- stock-analyzer：`deploy.sh` 拉取浮动 `main` 且不接受 Tag 参数，标记 `NON_COMPLIANT`。
- Dashboard：`./deploy.sh <git-ref>` 可接受显式 Tag，但默认 ref 为浮动 `main`，标记
  `CURRENT DEFAULT IS NON_COMPLIANT`。

本步骤未修改任何部署脚本。

## 5. Documentation Convergence Status

### marketNewsFeed

- `.trae/rules/代码开发规则.md` 已在 STEP 5 移除长期 `dev` 及 `dev → main` 流程，改为引用
  Platform Governance；原文已归档。
- `.claude/settings.local.json` 保留未修改；permission allow-list 不构成 workflow authorization，
  其宽泛 `Bash(git *)` 需后续最小权限安全审查。
- `deploy.sh` 及相关说明仍体现浮动 `main` 部署，等待 Deployment Governance Change。

### stock-analyzer

- `docs/deploy.md` 仍描述生产部署拉取 `main`，等待 Deployment Governance Change。
- `.claude/settings.json` 与 `.claude/settings.local.json` 保留未修改；权限配置不覆盖平台授权。
- 未发现 README/docs 仍把 `codex/*` 或 release candidate branch 定义为仓库默认流程。

### investment-research-dashboard

- `CONTRIBUTING.md` 与 `docs/development/process.md` 已在 STEP 5 移除旧 Agent 分支前缀，改为引用
  Platform Branch Governance。
- `docs/technical/deployment-operations.md` 仍允许省略 deploy ref，等待 Deployment Governance Change。
- 未发现技术文档继续全面禁止关键路径 E2E；旧冲突仅存在于已归档 AGENTS。

## 6. Remaining Actions

1. 对 Claude permission allow-list 执行最小权限安全审查，但不得把工具权限解释为流程授权。
2. 分别执行三个 Repository 的 Deployment Governance Change，阻断浮动 `main` 部署。
3. 建立 marketNewsFeed root `VERSION` 与运行时构建元数据。
4. 为未版本化的 maintenance、stock lookup 和 webhook 接口建立契约治理。
5. 后续从真实运行环境建立 Production Tag、SHA 与 Artifact baseline。

## 7. Conflict Check Result

三份新 Repository AGENTS 中未发现以下平台治理冲突：

- `dev-first` / `develop-first` 默认流程；
- `codex/<type>` 默认分支命名；
- mandatory release candidate branch；
- `main` 必须等于 Production；
- Production 等于 floating/latest `main`；
- Repository 重新定义“准备发布”或“正式发布”授权。

结果：`MIGRATED`。
