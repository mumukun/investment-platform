# Dependency Evidence

验证日期：2026-09-25
范围：`marketNewsFeed`、`stock-analyzer`、`investment-research-dashboard` 的 Architecture Dependency Baseline。
方法：只读、定向检索；未登录 Production，未推测生产 Tag、SHA 或镜像。

## 1. Verified Architecture

依赖箭头统一表示 Provider → Consumer。

```text
marketNewsFeed ──versioned research API───────────────> investment-research-dashboard
marketNewsFeed ──webhook notification────────────────> investment-research-dashboard
stock-analyzer ──versioned analysis APIs──────────────> investment-research-dashboard
stock-analyzer ──optional unversioned stock lookup────> marketNewsFeed
marketNewsFeed ···optional shared Feishu Base··· stock-analyzer
```

`marketNewsFeed → stock-analyzer` 未发现已实现的直接依赖。`stock-analyzer` 的 PRD 只描述了未来可选新闻联动，不是当前运行时事实。因此不存在固定的 `marketNewsFeed → stock-analyzer → Dashboard` 三层发布链。

## 2. Repository Roles

### marketNewsFeed

- 采集和分析新闻、X Watch、研究源等信息，写入自己的 PostgreSQL 事件账本。
- 主要表由 `src/common/db_schema.py` 定义，包括 `events`、`signals`、`topic_heat`、`ashare_map`、`daily_briefings`、同步队列和 X Watch 表。
- 通过 `investment-dashboard-research-v1` 向 Dashboard 提供结构化研究信息。
- 信号落库后可向 Dashboard 发送不携带业务数据的 webhook，通知 Dashboard 重新拉取版本化契约。
- 趋势股票报告可选查询 `stock-analyzer` 的通用股票接口；失败时降级并继续生成报告。
- 可选把 `News_*` 派生展示表写入既有 stock-analyzer 飞书 Base；它不是 PostgreSQL 事实源。
- Hermes/local ops 也消费同一个内部 Admin API 的运维接口，但 Hermes 不在本次三个业务 Repository 的发布图内。

### stock-analyzer

- 从腾讯、东方财富、akshare、Yahoo Finance 等外部市场源取得股票、行情和研究数据，写入自己的 PostgreSQL schema。
- 对 Dashboard 暴露自选股、监控、短线、波段、资金流、板块和美股等版本化内部 API。
- 对 Dashboard 另有 search/add/remove/update 受控维护命令；这些命令已文档化，但响应没有 contract version。
- 暴露通用 `/api/stocks/{query}` 接口，被 `marketNewsFeed` 的趋势股票报告可选消费。
- `INVESTMENT_DASHBOARD_URL` 只用于通知文本里的 Dashboard 页面链接，不是对 Dashboard 的 API 调用或 webhook。
- 未发现生产代码调用 `marketNewsFeed`、读取其数据库或消费其 webhook。
- 可选使用与 marketNewsFeed 共置的飞书 Base，但双方使用独立 table IDs，未发现 stock-analyzer 读取 `News_*` 表。

### investment-research-dashboard

- 通过 `backend/app/integrations/market_news_feed.py` 和 `backend/app/integrations/stock_analyzer.py` 统一访问两个上游。
- 使用自身 PostgreSQL 保存投研、自选股和美股等本地投影或快照；上游失败时相关同步保留最后成功数据并记录异常。
- 不直接读取两个上游的数据库、schema 或表。
- 对 marketNewsFeed 提供 `/api/v1/research/webhook`，验证共享 webhook secret 后触发正常的版本化读取流程。

## 3. Dependency Evidence

| Dependency | Type | Evidence | Verification Result | Notes |
| --- | --- | --- | --- | --- |
| marketNewsFeed → Dashboard | `runtime_contract` | `marketNewsFeed/src/admin_api.py`; `marketNewsFeed/docs/hermes-api.md`; `investment-research-dashboard/backend/app/integrations/market_news_feed.py`; `backend/app/research_sync.py` | `verified` | Bearer 鉴权，契约 `investment-dashboard-research-v1`，失败保留本地投影。 |
| marketNewsFeed → Dashboard | `async_integration` | `marketNewsFeed/src/common/dashboard_webhook.py`; `investment-research-dashboard/backend/app/api.py`; `src/views/ResearchLibraryView.vue` | `verified` | webhook 只通知重新同步；无业务数据；Dashboard 另有 5 分钟对账。 |
| stock-analyzer → Dashboard | `runtime_contract` | `stock-analyzer/stock_analyzer/api.py`; `stock-analyzer/docs/hermes-api.md`; `investment-research-dashboard/backend/app/integrations/stock_analyzer.py` | `verified` | Bearer 鉴权；Dashboard 对主要响应执行 Pydantic 和精确契约版本检查。 |
| stock-analyzer → Dashboard commands | `runtime_contract` | `stock-analyzer/stock_analyzer/api.py`; `stock-analyzer/docs/hermes-api.md`; `investment-research-dashboard/backend/app/integrations/stock_analyzer.py` | `verified` | search/add/remove/update 已文档化，但使用无 contract version 的操作专用 JSON。 |
| stock-analyzer → marketNewsFeed | `runtime_contract` | `marketNewsFeed/src/research_feed/trend_stock_report.py`; `stock-analyzer/stock_analyzer/api.py` | `verified` | `/api/stocks/{query}?live=true`；8 秒超时；失败被视为未在自选池，报告继续。 |
| marketNewsFeed → stock-analyzer | `no_direct_dependency` | `stock-analyzer` 生产代码定向搜索无 URL、Token、模块或表引用；`stock-analyzer/docs/prd/PRD-v3.2.md` 仅描述未来可选集成 | `verified` | 结果为 `NO_DIRECT_DEPENDENCY_FOUND`，不是 `UNKNOWN`。 |
| marketNewsFeed · stock-analyzer | `shared_storage` | `marketNewsFeed/src/research_feed/feishu_sync.py`; `docs/tech-design-v1.5.md`; `stock-analyzer/stock_analyzer/feishu_client.py` | `verified` | 可选共置在一个飞书 Base，使用不同 table IDs；未发现跨表读取，生产是否启用未检查。 |
| stock-analyzer → Dashboard local helper | `operational_dependency` | `investment-research-dashboard/local-api.sh`; `local-compose.sh` | `verified` | 仅本地开发：可启动同级 stock API 并检查 `/api/health`；发布依赖为 `none`。 |

## 4. Cross-Repository API Detail

| Provider → Consumer | Base URL Source | Authentication | Endpoint / Schema | Contract Version | Timeout | Retry | Fallback | Direct Health Dependency |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| marketNewsFeed → Dashboard | `MARKET_NEWS_FEED_BASE_URL` | Bearer | `GET /api/integrations/investment-dashboard/research`; `MarketNewsResearchEnvelope` | `investment-dashboard-research-v1` | `MARKET_NEWS_FEED_TIMEOUT_SECONDS`, default 20s | `MISSING` | Preserve local projection and record sync failure | `MISSING` |
| marketNewsFeed → Dashboard | `DASHBOARD_WEBHOOK_URL` | `X-Webhook-Secret` | `POST /api/v1/research/webhook`; notification only | `MISSING` | `DASHBOARD_WEBHOOK_TIMEOUT_SECONDS`, default 5s | `MISSING` | Periodic reconciliation plus last-known-good data | none |
| stock-analyzer → Dashboard | `STOCK_ANALYZER_BASE_URL` | Bearer | `/api/integrations/investment-dashboard/*`; typed Pydantic envelopes | Versioned contract family | `STOCK_ANALYZER_TIMEOUT_SECONDS`, default 20s | `MISSING` | Partial: persisted projections/snapshots; direct views fail explicitly | `MISSING` |
| stock-analyzer → Dashboard commands | `STOCK_ANALYZER_BASE_URL` | Bearer | `/api/stocks/search`, `/add`, `/{query}/remove`, `/{query}/update`; operation-specific JSON | `MISSING` | `STOCK_ANALYZER_TIMEOUT_SECONDS`, default 20s | `MISSING` | None; command failure is explicit | `MISSING` |
| stock-analyzer → marketNewsFeed | `TREND_STOCK_API_BASE` | Bearer | `GET /api/stocks/{query}?live=true`; unversioned `ok + stock` | `MISSING` | 8s | `MISSING` | Treat as absent stock and continue report | `MISSING` |

Dashboard 明确检查的 stock-analyzer 契约包括：watchlist v1、watchlist strategy v2、company profile v1、monitor v1、nextday v1、short-selection engine v1、swing selection v3、swing candles v1、swing stats v2、capital flow v1、sector workbench v1、US market v1、US calendar v1 和 US market history v1。

Dashboard 使用的 stock search/add/remove/update 命令虽有 `docs/hermes-api.md`，但没有 contract version；它们不能被版本化只读契约的覆盖结论代替。

## 5. Database Boundary

| Repository | Database Boundary | Evidence | Result |
| --- | --- | --- | --- |
| marketNewsFeed | `MARKET_NEWS_PG_DSN` / `MARKET_NEWS_PG_DATABASE`; project-owned tables | `src/common/database.py`; `src/common/db_schema.py`; `AGENTS.md` | Independent PostgreSQL database. |
| stock-analyzer | `STOCK_ANALYZER_DATABASE_URL` / `STOCK_ANALYZER_DB_SCHEMA`; explicit search path | `stock_analyzer/settings.py`; `stock_analyzer/local_db.py`; `.env.example` | Independent PostgreSQL database/schema. |
| Dashboard | `DATABASE_URL`; local projections and snapshots | `backend/app/config.py`; `backend/app/database.py`; `docker-compose.yml` | Independent PostgreSQL database. |

定向搜索未发现 Dashboard 使用 `MARKET_NEWS_PG_DSN`、`STOCK_ANALYZER_DATABASE_URL` 或直接查询上游表；也未发现 stock-analyzer 使用 marketNewsFeed 的 DSN、schema 或 PostgreSQL 表。三个 Repository 之间没有已验证的共享 PostgreSQL database/schema/table。

`marketNewsFeed` 的飞书同步会把独立 `News_*` 表放入既有 stock-analyzer 飞书 Base。该关系是可选 `shared_storage` 共置风险：共享 Base 容器和权限边界，但使用不同 table IDs，没有发现 stock-analyzer 读取新闻表，也不形成发布顺序。真实 Production 是否启用不在本步骤验证范围。

## 6. Environment Variable Dependency Inventory

只记录变量名，不记录任何值或凭证。

| Repository | Environment Variables | Dependency |
| --- | --- | --- |
| marketNewsFeed | `MARKET_NEWS_PG_DSN`, `MARKET_NEWS_PG_DATABASE` | Own PostgreSQL |
| marketNewsFeed | `MARKET_NEWS_API_HOST`, `MARKET_NEWS_API_PORT`, `MARKET_NEWS_API_TOKEN` | Inbound internal API |
| marketNewsFeed | `TREND_STOCK_API_BASE`, `STOCK_API_TOKEN` | stock-analyzer lookup |
| marketNewsFeed | `DASHBOARD_WEBHOOK_URL`, `DASHBOARD_WEBHOOK_SECRET`, `DASHBOARD_WEBHOOK_TIMEOUT_SECONDS`, `DASHBOARD_WEBHOOK_DEBOUNCE_SECONDS` | Dashboard notification |
| marketNewsFeed | `FEISHU_BASE_TOKEN`, `FEISHU_EVENT_TABLE_ID`, `FEISHU_SIGNAL_TABLE_ID`, `FEISHU_TOPIC_HEAT_TABLE_ID`, `FEISHU_BRIEFING_TABLE_ID` | Optional shared Feishu Base, marketNewsFeed-owned tables |
| stock-analyzer | `STOCK_ANALYZER_DATABASE_URL`, `STOCK_ANALYZER_DB_SCHEMA` | Own PostgreSQL |
| stock-analyzer | `STOCK_API_HOST`, `STOCK_API_PORT`, `STOCK_API_TOKEN` | Inbound internal API |
| stock-analyzer | `INVESTMENT_DASHBOARD_URL` | User-facing link only; no Dashboard API call |
| stock-analyzer | `FEISHU_APP_TOKEN`, `FEISHU_TABLE_ID`, `FEISHU_DAILY_STOCK_TABLE_ID`, `FEISHU_DAILY_SECTOR_TABLE_ID`, `FEISHU_ALERT_TABLE_ID`, `FEISHU_REPORT_TABLE_ID` | Optional shared Feishu Base, stock-analyzer-owned tables |
| Dashboard | `DATABASE_URL` | Own PostgreSQL |
| Dashboard | `MARKET_NEWS_FEED_BASE_URL`, `MARKET_NEWS_FEED_TOKEN`, `MARKET_NEWS_FEED_TIMEOUT_SECONDS`, `MARKET_NEWS_FEED_WEBHOOK_SECRET` | marketNewsFeed API and callback |
| Dashboard | `STOCK_ANALYZER_BASE_URL`, `STOCK_ANALYZER_TOKEN`, `STOCK_ANALYZER_TIMEOUT_SECONDS`, `WATCHLIST_PROJECTION_SYNC_SECONDS` | stock-analyzer API and local projection |

## 7. Version Domains

| Repository | Application Version | Contract Version | Rules Version |
| --- | --- | --- | --- |
| marketNewsFeed | `UNKNOWN`; multiple component constants exist, but no canonical application source | `src/admin_api.py::RESEARCH_CONTRACT_VERSION` | `MISSING` as a repository-wide canonical source |
| stock-analyzer | `stock_analyzer/version.py::APP_VERSION`; imported by the FastAPI app | Defined in API/contract modules and enforced by consumers | Separate domain rule constants, including short, swing, sector and capital-flow rules |
| Dashboard | Root `VERSION`; read by `backend/app/version.py` | Consumer-enforced versions in `backend/app/integrations/*` | Consumed from upstream responses; not the Dashboard application version |

Application version、contract version 与 rules version 是三个独立维度，不得互相替代。

## 8. Release Dependency Interpretation

- 三条已实现的业务边基线均为 `optional`：它们影响兼容性和影响分析，但不要求每次原子发布全部系统。
- 当 Consumer 的某个 Change 明确依赖 Provider 的新接口、字段或语义时，该 Change 的对应边临时升级为 `required`，发布顺序为 Provider → smoke → Consumer。
- `marketNewsFeed → stock-analyzer` 为 `none`，因为没有实现直接依赖。
- 本地开发 bootstrap 为 `none`，不能转换成生产发布顺序。
- 不存在固定三仓发布顺序；只在当前 Change 同时影响对应边两端时参与拓扑排序。

## 9. Deployment Compliance Evidence

| Repository | Result | Evidence | Notes |
| --- | --- | --- | --- |
| marketNewsFeed | `NON_COMPLIANT` | `deploy.sh` checkout/pull floating `main` | 未接受不可变 Tag 参数。 |
| stock-analyzer | `NON_COMPLIANT` | `deploy.sh`; `docs/deploy.md` 固定拉取 production `main` | 未接受不可变 Tag 参数。 |
| Dashboard | `NON_COMPLIANT` | `deploy.sh` 支持 git ref，但缺省为 floating `main` | 显式传入并验证 immutable Tag 时可按新治理执行；默认行为仍不合规。 |

本步骤只记录，不修改任何部署脚本。

## 10. Verification Answers

- A — marketNewsFeed 直接向 Dashboard 提供 API：`VERIFIED_DIRECT_DEPENDENCY`。
- B — stock-analyzer 直接向 Dashboard 提供 API：`VERIFIED_DIRECT_DEPENDENCY`。
- C — stock-analyzer 直接依赖 marketNewsFeed：`NO_DIRECT_DEPENDENCY_FOUND`。
- D — 共享 PostgreSQL database/schema/table：否。可选共享飞书 Base 容器：是，双方使用不同 table IDs，Production 是否启用为 `UNKNOWN`。
- E — Dashboard 直接访问上游数据库：否。
- F — 固定串行链 `marketNewsFeed → stock-analyzer → Dashboard`：否。两个系统是 Dashboard 的平行 Provider；另有 `stock-analyzer → marketNewsFeed` 可降级辅助调用。

## 11. Remaining Verification Items

- marketNewsFeed 的 canonical application version source 仍为 `UNKNOWN`；目标决策仍是 root `VERSION`。
- `stock-analyzer → marketNewsFeed` 的通用股票查询缺少 contract version 和专用契约文档。
- Dashboard 使用的 stock-analyzer 维护命令缺少 contract version。
- marketNewsFeed → Dashboard webhook 缺少独立 contract version；当前安全性依赖共享 secret，可靠性依赖周期对账。
- Consumer 未直接调用上游 `/api/health` 作为 gate；需要后续决定现有 freshness/readiness 是否足够。
- 可选共享飞书 Base 在 Production 是否启用、权限是否能按应用/表隔离，需要后续运行环境确认。
- Production Tag、Commit SHA 和 artifact digest 不在本步骤验证范围，继续保持 `UNKNOWN`。
