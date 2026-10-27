# 公共数据入口、库表与迁移归属

2026-10-27梳理 / 2026-10-28本地实施；CHG-20261027-002；APPROVED。配套[实施方案](CHG-20261027-002-shared-market-data.md)。表中“当前行为”指重构前源码，迁移后的职责见末节；本地实现不表示生产已切换，也不是新来源授权清单。最终以用户最新原则为准：业务不触发、不控制采集，业务派生数据与基础事实分开。

源码基线：stock-analyzer `dde82a8`，Dashboard `55ed3c1`，marketNewsFeed `2dce081`；日线相关同时核对本 Change 现有未提交实现。后续实施按这里的类别逐项核销，不靠文件名推断读写责任。

## 1. 现有入口与目标归属

| 当前入口 / 关键调用 | 当前行为 | 目标归属与迁移阶段 |
| --- | --- | --- |
| `stock_data.py`、`swing_sources.py`、`sync.py` 的来源适配 | 腾讯/新浪等能力路由、报价/日线/全市场快照；各调用方仍可独立发请求 | 保留适配层，公共数据 worker 成为执行调用方；阶段二/三 |
| `watch.py::_fetch_quotes` | 按自选关注级别抓 A 股/美股，更新自选报价并运行监控 | 数据目录按自己的计划采集，不读关注级别；watch只读报价并保存自己的投影/告警；阶段二 |
| `hotmap_cache.py`、`sync.py` | 全市场抓取并落库，hotmap_cache 再驱动短线分钟输入 | 抓取/快照/累计采样→数据程序；短线计算独立读已提交批次；阶段二 |
| `short_engine_runtime.py`、`short_engine_store.py` | 从全市场快照生成带空字段的盘中累计样本，写公共分钟表及短线结果 | 公共写入先归统一 writer；评分/候选/事件/结果归短线；阶段一/二 |
| `short_tail_refresh.py::prepare_references/fetch_preview_quotes/refresh_preview` | 准备基础资料，全市场分批抓报价，计算并发布当前预选与证据 | 资料和报价→数据程序；分批消费与截止判断→短线；阶段二/三 |
| `short_tail.py::cycle` | 为正式候选与次日跟踪额外抓报价并保存策略观察 | 报价读公共数据；策略的决策观察/证据可继续自存；阶段二 |
| `swing_runtime.py::fetch_pool_quotes`、盘中 cycle | 抓活跃池报价，写公共分钟表，计算状态 | 数据程序按全市场固定计划采集，不读活跃池；状态与事件→波段；阶段一/二 |
| `swing_intraday_discovery.py` | 读全市场及历史，同时写公共分钟事实并发现候选 | 公共输入/写入→数据程序；发现与评分→波段；阶段二 |
| `swing_maintenance.py`、`swing_daily_data.py`、新 `swing_daily_ingestion.py` | 日线获取、窗口核验、落库、健康与基础资料维护 | 采集/事实/核验→数据程序；函数可复用、不复制第二套；阶段一/三 |
| `sync_daily_stock.py` | 按证券抓历史，写日收盘/指标等 | 公共历史维护→数据程序；派生计算使用相同已验证输入；阶段三 |
| `swing_intraday_data.py::backfill_candidate_history` | 新浪五分钟历史解析并写旧公共分钟表 | 真正区间事实→market_intraday_kline；改由全证券数据计划维护，不按候选触发；阶段一/三 |
| `candidate_history.py::fetch_candidate_histories/fetch_chart_history` | 功能/图表可触发日线抓取和补缺 | 消费函数只读仓储；缺口由数据程序独立计划推进，不提交命令；阶段三 |
| `short_tracking.py` | 复盘发现日线缺口时抓取并保存公共日线 | 数据程序独立维护历史；复盘只读，缺失时说明，不提交补数；阶段三 |
| `hotmap_data.py` | 获取全市场输入、历史窗口补缺 | 数据层供输入；报表不自补数；阶段二/三 |
| `security_classification.py`、`sync_daily_sector.py`、交易规则/日历准备 | 证券分类、概念、行业与指数历史等基础事实维护 | 专用来源适配保留；由数据程序统一执行原有效日程；阶段三 |
| `tech_board.py::refresh` | 成员/指数/个股/日线获取，与板块发布耦合，写 tech_board_fact | 来源事实→数据程序；科技聚合/排名/响应→功能；阶段四 |
| `rotation_board.py::refresh` | 重复获取部分成员报价、轮动指数与日线，复用 tech_board_fact | 与科技同证券报价合并；轮动算法独立；阶段四 |
| `tech_concepts.py` | 概念成员报价与研究运行，复用 tech_board_fact | 成员/报价→数据程序；概念研究/运行证据→功能；阶段四 |
| `capital_flow.py::build_capital_flow_envelope` | 仍会取新浪市场资金等；不因名称 envelope 视为纯读取 | 原始市场资金→数据程序；契约构建/方向与速度计算→消费者；阶段四 |
| `sector_fund_sina_intraday.py` | 来源分钟时钟前后核对、完整 48 行业批次保存 | 直接复用有效校验与原子保存，交数据程序调度；阶段四 |
| `sector_fund_sina.py/research.py`、`sector_fund_research.py` | 资金历史、行业/指数事实维护及研究 | 事实获取/落库→数据程序；研究计算保留；阶段四；来源严格按既有授权 |
| `sector_fund_members.py::request_collection/process_pending` | 有只读 GET 与显式 POST 202；当前 API BackgroundTasks 可执行采集 | 数据程序按行业成员计划维护；页面只重新读取；POST采集控制语义弃用，阶段四/五 |
| `market_structure_sources.py/sync.py`、相关 backfill CLI | 专用指数/ETF/证券报价、日线和结构事实维护 | 保留专用口径与授权适配，交数据程序执行；阶段三（通用证券）/四（专用事实） |
| `global_board.py`、`us_market_runtime.py`、海外日历任务 | 海外资产/事件采集与分析混合 | 事实按市场日历采集，分析仍由各自任务执行；阶段四 |
| `margin_observation.py`、`margin_sources.py` | 披露事实采集与融资研究 | 采集→数据程序；研究/响应只读已保存披露；阶段四 |
| `seat_flow.py`、`seat_tracking.py`、`seat_sources.py` | 目录、交易明细及案例查询可同步获取第三方事实 | 获准席位事实→数据程序；研究/跟踪读事实；通用个股历史复用公共日线；阶段四 |
| `api.py::_fetch_live_quote` | legacy GET 显式 live 参数内抓 A 股/美股报价 | 不保留采集命令桥；最终只读已采集报价并标明实际时间，行为变更按兼容顺序收口；阶段五 |
| `api.py::_refresh_dashboard_watchlist_quotes` | 显式 refresh_quotes=true 会抓取并更新自选；默认 false | 取消触发采集；读取公共报价只生成自己的投影，不控制数据计划；正常客户端已固定 false；阶段二/五 |
| `api.py` candles/bars + chart projection 的 refresh builder | 本地优先，但后台 refresh 可用 fetch_chart_history/fetch_basic_info | 图表构建只读；缺口显示覆盖不足，既不后台补数也不登记请求；阶段三 |
| `api.py` company-profile → `add_stock.py::fetch_industry` | 旧函数指向东财 F10，但通用传输层拒绝；失败返回空资料 | 读取已有真实资料；无获准替代时明确缺失，禁止恢复 F10 或拿其他行业体系冒名替代；阶段三 |
| `api.py::_selection_quotes` | 已从当日 a_share_snapshot 读取，过滤陈旧值 | 保留只读方向，改用统一 reader 的实际来源时间/口径；不能误记成仍抓来源 |
| `watchlist_strategy_service.py`、`current_watchlist.py` | 组装短线/波段画像，保存自选派生结果 | 保留功能职责，输入只读公共事实和引擎结果；新增/修改自选既不触发行情HTTP，也不改变数据目录/频率 |
| `api_projection.py` publisher / chart projection | 负责缓存/发布，并可能间接调用仍含来源 I/O 的 builder | 只做投影；基础缺口由独立数据计划处理，不能隐藏后台采集或需求登记 |
| `scripts/*` 中以上能力的维护/回填入口 | 可被 scheduler、人工或其他任务执行，可能绕开常驻任务 | 保留为独立数据运维入口，参与单持有者协议；业务/API/投影不能调用；阶段三/四/五 |

配套核验包含直接 HTTP、SDK/AKShare、浏览器专用适配、函数内延迟 import、后台任务、CLI 及备用/重试路径；不以静态搜索某一个 fetch 前缀作为完整性证明。

## 2. 公共事实与结果表

| 库表/组 | 内容及主要消费者 | 最终写入者 |
| --- | --- | --- |
| a_share_snapshot | 当日全市场快照；热力/短线/波段/行业与选股报价覆盖 | 数据程序；不以应用 update_time 代替来源时间 |
| a_share_daily_close、a_share_daily_metric | 已保存日价格与通用日指标；热力、行业、报表等 | 数据程序的事实/通用派生任务 |
| a_share_security_profile、security_classification_snapshot、security_concept_membership、security_trade_rule | 身份、上市/ST/分类/成员与交易限制 | 数据程序；不从代码猜交易限制 |
| swing_reference（calendar、目录等基础 kind） | 日历、目录、基础配置的已观察版本；短线/波段/行业 | 基础kind迁入market_auxiliary_fact；旧基础记录兼容读取，业务专属记录保留自己的归属 |
| intraday_stock_bar | 按分钟记录的累计采样，旧行还混有历史 K 线；短线、波段、同刻成交额和复盘 | 统一数据 writer；新行明确种类、源时点 |
| swing_daily_bar | 原价/前复权日线、量额；波段/板块/图表/跟踪 | 数据程序 |
| swing_daily_validation、swing_daily_change | 同源完整日期集合核验证据与实际修订审计；健康检查/排障 | 数据程序；不是价格缓存 |
| swing_daily_refresh、swing_suspension、swing_index_daily | 单证券维护状态、停牌/指数事实 | 数据程序；保留原业务口径 |
| tech_board_fact | 科技/轮动/概念共享成员、报价、日线、目录及采集覆盖诊断 | 数据程序；concept_run经核对仅记录采集覆盖/失败，不是策略结论，保留原位置；业务分析不写入 |
| sector_fund_fact | 行业窗口、成员资金排名及业务归档；存量混有分钟原始批次 | 新写仅归业务；分钟原始批次新写market_auxiliary_fact，旧raw记录只读兼容 |
| global_board_fact | 多资产报价与其他源事实；全球/科技/轮动/海外研究 | 数据程序，保留资产时区、单位和来源身份 |
| market_structure_fact | 指数、ETF、净值、拆分等结构事实 | 数据程序；不同编制/价格净值不混接 |
| margin_disclosure、margin_collection | 融资融券披露与采集记录 | 数据程序 |
| us_market_calendar_event/run | 海外事件事实与采集状态 | 数据程序；策略结论不混入事件事实 |
| market_quote_latest（新增） | 公共最新报价，跨功能读取；只保留每来源/口径最新有效值 | 数据程序 |
| market_data_state（新增） | 轻量事实就绪/版本/数据进程心跳，无业务请求 | 仅数据程序；不建request表、不接受业务采集请求 |
| market_intraday_kline（新增） | 真实区间 K 线，与累计采样明确分开 | 数据程序 |
| market_auxiliary_fact（新增） | 日历/基础参考、现有表未承载的公司资料、席位目录/明细、市场资金源事实 | 数据程序；严格领域模型，不保存页面响应或整包重复历史 |
| short_candidate_snapshot、short_signal_event/outcome、short_tail_run/observation、setup/factor ledger | 短线候选/信号/规则证据/结果；observation 是特定策略当时使用的证据 | 短线功能；不回写公共事实 |
| swing_feature_snapshot、swing_setup_snapshot、swing_state_event、swing_signal_outcome、swing_scan_run/simulated_trade | 波段特征、观察池、状态、结果与运行证据 | 波段功能 |
| intraday_sector_snapshot、intraday_market_snapshot | 从公共输入计算的盘中市场/行业统计 | 对应通用计算/功能任务；不是第三方原始行情写入口 |
| watchlist_item | 自选主数据，以及兼容展示所需报价投影列 | 完全归自选业务；业务从公共报价生成展示投影，数据程序不读写watchlist_item |
| watchlist_strategy_snapshot、watchlist_alert_event | 自选画像与告警证据 | 自选功能 |
| tech_board_run、global_board_run、sector_fund_run、market_structure_generation、us_market_snapshot | 按版本生成的分析/聚合/研究结果，需按实际 kind 区分 | 功能/发布任务；采集完成不等于分析完成 |
| api_read_projection | Provider 已计算响应/当前候选等投影及检查状态 | 各功能publisher；基础source revision迁market_data_state，数据程序不再改业务投影 |
| job_run | 定时/维护运行诊断；混合时区 TEXT 存量另评估 | 调度/数据/计算任务记录各自运行；不能作为事实新鲜度唯一来源 |

“数据程序独占公共事实写入”按表或共享表的 kind/字段边界执行，不表示把所有结果表都交给它，也不表示要把所有旧表统一改名。最终基础writer不访问业务结果/自选池；混合位置逐步迁读写，旧记录保留兼容。

## 3. 跨仓消费者与排除项

| 仓库 / 位置 | 当前职责与本轮处理 |
| --- | --- |
| Dashboard `backend/app/integrations/stock_analyzer.py` | Bearer API Consumer。核对模型、版本、日期与失败降级；不能直接读 Provider PG。watchlist 请求明确传 refresh_quotes=false |
| Dashboard current_candidates / watchlist / market_data / tech/global/rotation 等 projection | 保留后台 API 同步和本地投影；迁移上游采集不删除下游同步；移除成员采集触发等交互，改为读取真实状态/结果。投影写放大不在本轮改造 |
| Dashboard snapshots | 兼有当前缓存、历史与计算证据；不能整表迁 Redis，也不能整表当一次性缓存清掉。历史清理按用户要求搁置 |
| marketNewsFeed `src/research_feed/trend_stock_report.py` | 可选调用 `/api/stocks/{query}?live=true`，8 秒超时；最终读取已采集行情，保留原价格字段并核验日期/降级。新闻核心采集、LLM、outbox、飞书及其数据库排除 |
| 原工作区手册/原型与其他 Change | 不修改、提交、回滚或清理 |

## 4. 源码定位与后续核销规则

关键证据函数：`short_engine_runtime.bar_rows_from_snapshot`、`short_engine_store.save_intraday_bars`、`swing_store.save_intraday_bars/insert_intraday_bars`、`swing_runtime.fetch_pool_quotes`、`short_tail_refresh.fetch_preview_quotes`、`tech_board.save/refresh/envelope`、`capital_flow.build_capital_flow_envelope`、`api._fetch_live_quote/_refresh_dashboard_watchlist_quotes/_selection_quotes`、`api_projection` 的后台构建路径。

实施核销以“调用链停止来源请求、公共写入归数据层、计划独立、旧接口按版本迁移、对应失败场景测试通过”五项为准。还必须证明业务不能提交采集请求、不能改变范围/节奏，数据程序不读取业务池或写业务结果。完成迁移的能力必须有执行证据，未迁移能力继续明确记录，不能只把 import 改名后标记完成。未获用户确认前不填写已迁移或已上线。

## 5. 本地落地核销（未发布）

| 职责 | 实施入口 |
| --- | --- |
| 独立数据目录/计划与单持有者 | market_data/catalog.py、worker.py、runtime.py；Compose stock-data |
| 公共行情/日线/真实分钟/快照 | market_data/sources.py、store.py、reader.py；raw与qfq、来源钟与检查时间分开 |
| 板块/全球/题材原生来源 | market_data/board_sources.py、global_sources.py、rotation_sources.py、concept_sources.py；原业务模块保留只读视图 |
| 资金、席位、两融、海外与市场结构基础输入 | fund_jobs/source、industry_intraday_sources、seat_jobs/facts、margin_facts、us_sources、maintenance_jobs；行业分钟与市场资金分别调度，来源故障互不阻断；仅既有授权 |
| 业务派生结果 | 行业分钟原始批次新写market_auxiliary_fact，旧sector_fund_fact raw只读兼容；策略各自结果表、sector_fund业务结果、api_read_projection；新swing_business_state承接原引用表业务种类，旧记录经只读view兼容 |
| 无业务驱动采集 | API/business角色拒绝基础来源和writer；缺数不入队；旧源CLI停用；Dashboard刷新只GET |
| 运行单元和回退 | 同镜像三个服务；candidate-v2冻结服务，保留旧两服务Manifest，首迁先停旧采集者，回退精确停止新增数据进程 |

最终本地测试、未验证项目及Git状态见Change证据。来源真实吞吐、NAS持续运行、正式MAJOR/Tag及安装runner均不在本地验证结果中。历史清理继续搁置。
