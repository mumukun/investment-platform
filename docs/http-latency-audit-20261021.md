# 当前生产系统 HTTP 慢接口排查（2026-10-21）

Change：CHG-20261021-002。采样时间：2026-10-21 约 11:08–11:16，Asia/Shanghai。状态：本报告保留排查时的生产基线；整改与生产复测见[优化结果](http-latency-optimization-20261021.md)，已于2026-10-21正式发布。

## 结论

当前线上确实有几十秒请求：行业工作台 60.065 秒后返回 502，个股 K 线 bars 37.308 秒，涨停梯队 17.958 秒，上游科技看板 20.958 秒、资讯研究接口 14.603 秒。用户举例的波段列表，本次观察为 6.115–10.773 秒；最近约 12 小时日志有客户端断开，但本次没有复现它超过 30 秒。

慢请求集中在三类：读取时同步拉外部行情；读取时对大量历史事实重新聚合、去重或计算；读取和返回完整大 JSON。三个服务虽然使用独立数据库，却运行在同一 NAS、共用 PostgreSQL 实例，重查询有共同的 CPU/磁盘竞争边界。跨服务受影响的程度还需持续耗时日志确认，不能把所有慢请求都归于单一 SQL。

健康接口内网 6–8 毫秒，公网 0.206 秒；自选列表、已投影的美股日历等也很快。因此不能认定整个 HTTP 网络都需要几十秒。公网波段 6.952 秒中，首字节等待 6.771 秒；公网 gzip 已生效，主要等待发生在服务端。

## 基线与方法

| 服务 | 当前运行证据 |
| --- | --- |
| Dashboard | 容器 OCI 标签 v0.29.1，提交 `3e44833217d2b280a10baf58c082225d2028c07a`；运行 digest/config ID 与 REL-20261020-002 一致 |
| stock-analyzer | 容器 OCI 标签 v4.5.0，提交 `c0e30fce57ccc7a4b92bbc528e6763302b388a20`；运行 digest/config ID 已保存 |
| marketNewsFeed | 运行 image ID `sha256:0400749e403879bcaef29efd4e28b271c9847748db8d8bcaf3fd9189b0053b25`。NAS checkout 为 v2.4.0 / `99c71ec4417a4e7feda35ac5a4f9a5f9c0ff66bd`；镜像没有 version/revision 标签，不能仅凭 checkout 宣称整镜像身份。运行中的 admin_api、storage、x_monitor、database 四个相关文件哈希与该提交一致 |

共执行 70 次低频 GET 观察：Dashboard 容器内 HTTP 52 次、上游 stock/news HTTP 12 次、开发电脑访问用户给出的公网 HTTPS 域名 6 次。每条扫描队列顺序执行，期间最多两条 HTTP 观察队列重叠，不做并发压测。业务请求均携带有效鉴权，凭据只存在于进程内存，证据不保存业务响应正文、Cookie、Token、客户端 IP。

数据库使用 READ ONLY 事务及会话级 5 秒诊断超时，只读取活动/统计/索引与 EXPLAIN 计划；没有 EXPLAIN ANALYZE，没有生产索引或参数修改。证据中的 `statement_timeout=5000` 是诊断会话设置，`reset_val=0` 才是观察到的默认值。业务 GET 按既有逻辑可能更新行情或归档缓存，不能将这类调用描述成绝对无副作用的数据库读。

口径：下表秒数是各次实际观察值，通常只有 1–3 个样本；不同请求不在同一瞬间，负载及缓存状态可能变化。范围不能当作全天最小/最大值，更不是 P95。响应大小是未压缩应用 JSON，公网列另列 gzip 线缆字节。

## 已确认的慢接口与方案

Dashboard 接口均为 `/api/v1` 前缀；上游 stock 路径前缀为 `/api/integrations/investment-dashboard`。

| 优先级 | 线上接口 | 本次实际耗时 / 状态 | 定位证据与解决方案 |
| --- | --- | --- | --- |
| P0 | Dashboard `/sector-workbench` → stock 同名接口 | **60.065 秒，502** | 已捕获 `swing_daily_bar GROUP BY trade_date COUNT(DISTINCT code)` 查询运行 63.77 秒仍等待磁盘。已有 `(trade_date,code)` 唯一主键；先将每日期去重计数改为等价 `COUNT(*)`，再把覆盖率及工作台聚合移到已存在的批处理/快照路径，读请求取已完成结果。缓存外的日期探测也须优化 |
| P0 | Dashboard `/stocks/{code}/bars` → stock 同名接口；样本 300188 | **37.308 秒，200**；公网另一时点 4.867 秒 | 37.308 秒几乎全部等首字节，正文只有 10.6 KB。即使已有本地 bars，仍无条件调用 `fetch_chart_history`，每次新建 spawn 进程并 `.result()` 等外部历史抓取，之后再等实时报价。改为已缓存日线先返回，后台按证券/日期/复权口径补新或缺失区间；同一键去重刷新、设置任务总预算。保留 stale/缺失标记，避免将旧价伪装实时 |
| P1 | Dashboard `/limit-up-ladder` → stock 同名接口 | **17.958 秒，200**，148.7 KB | 活动 SQL 与 EXPLAIN 均显示取日期时 UNION 完整 `a_share_snapshot`，计划约 45 万输入行后排序去重，只为返回少数日期。先分别在日期层面限量，再合并；优先读取小型 run 元数据，保留没有 run 的历史 fallback 日期。无需先新增重复索引 |
| P1 | Dashboard `/swing-selection` → stock 同名接口 | **6.115 / 10.773 秒，200**；公网 6.952 秒 | 默认 limit=20000，862 个证券约 3.99 MB；上游逐批同步刷新这 862 个证券行情，60 个一批约 15 批，失败可重试。GET 还重建契约并更新 Dashboard 大快照。把完整规则结果按数据版本生成一次，行情与名单分开刷新；列表分页及详情按需获取，独立下发健康缺口。历史请求不刷新行情但仍 4.503 秒，说明只删外部抓取不足以解决全部耗时 |
| P1 | Dashboard `/short-selection` → stock 同名接口 | Dashboard **6.324 秒**，公网 3.790 秒；stock **14.424 秒** | 实际日志已有 2 次 504。上游构建选股、读取分钟量比，必要时再次构建选股，然后同步刷新候选行情。优先复用同一轮计算与报价结果，后台生成发布快照，普通 GET 读取。当前扫描样本数/候选数变化，不能将不同时间的 14 秒与 6 秒相减作为分层耗时 |
| P1 | stock `/tech-board` | **20.958 秒，200**，4.68 MB | 读请求查询并组装报价、成分、历史、当日样本和概念完整包。已有 tech_board_run 发布结果，但当前 envelope 仍从事实重组。优先复用版本化发布投影；只在事实改变时生成，保留 snapshot_id、报价时间和失败保留语义 |
| P1 | marketNewsFeed `/api/integrations/investment-dashboard/research?limit=100` | **14.603 秒，200**，180 KB | 当前代码 join events/signals，按 `COALESCE` 时间、level、strength 排序，随后返回正文和分析。已确认慢；尚未取得该 SQL 的执行计划，不能宣称某一索引就是唯一原因。先补最小查询计划，设计稳定时间/ID增量游标和对应索引，先选本页 ID 再取正文，保留更新消息同步，避免只按发布时间增量漏更新 |
| P1 | marketNewsFeed `/api/x-watch/users?limit=20` | **8.684 秒，200**，2.1 KB | 当前 `_x_monitor()` 每次都 `init_db()`，用户列表和 counts 各调用一次；因此一个 GET 重复执行 schema/init/列检查。将初始化移至启动一次，GET 仅做用户及计数 SELECT。慢时是否还叠加锁/连接等待未分层计时 |
| P1 | Dashboard `/research` | **9.435 秒，200**，1.40 MB | 默认读 500 条并序列化 ResearchItem 全部列，含 source_payload/analysis。先改列表摘要+游标分页，正文详情按需读取；索引须按生产计划确认。`limit=50` 另一次实测 0.153 秒/132 KB，支持缩小首屏，但不是同负载 A/B 证明 |
| P1 | Dashboard `/market-structure/overview`；stock `/market-structure` | Dashboard **8.788 秒**/5.92 MB；stock **8.118 秒**/5.55 MB | 默认读取 lookback+1 天完整快照，返回 `overview`、`days`、`etf_overview`，有重复内容。概览只取当前摘要，曲线取必需字段；详情与历史另按需读取。`lookback=5` 另一次 0.284 秒/585 KB；不能直接把 60 日语义改成 5 日来冒充等价优化 |
| P2 | Dashboard `/swing-selection/stats`；stock 同名 stats | Dashboard **4.746 / 0.564 秒**；stock **6.961 秒** | 统计路径读取全部跟踪样本，并读取关联价格、停牌、事件重新计算。按跟踪数据版本复用聚合统计，快照失效条件包括行情/复权、交易日历和跟踪结果变化；不能只按日期缓存导致修订不生效 |
| P2 | Dashboard `/stocks/{code}/candles`；样本 300188 | **4.904 秒，200**，8.8 KB | 需与 bars 一起治理，复用证券历史缓存；按代码+截止日+天数+复权口径缓存，历史不反复外采。不同日期、规则语义不能混用缓存 |
| P2 | marketNewsFeed `/api/x-watch/usage` | **4.681 秒，200**，4.6 KB | GET 同样先 init_db，再对 usage 全量分组求和。初始化移出读取；若计划确认聚合变重，再复用累计/日级统计。此次没有调用真实 X 收费接口 |
| P2 | Dashboard `/us-industries/history` | **4.227 秒，200**，1.54 MB | 默认返回 30 个完整 payload；改历史摘要和按日详情。`limit=5` 另一次 0.034 秒/256 KB。保留可访问完整历史的入口 |
| P2 | Dashboard `/tech-board`、`/tech-board/boards/{id}/history` | 概览 **3.028 秒**；history **3.923 秒**；members 1.756 秒 | 每个子接口加载并 deepcopy 整份科技快照；概览另加载至多 120 个完整 archive，仅取 key 和最近比较。日期列表只读元数据；最近比较仅取需要的 5 份；成员/历史直接取所需片段。读请求保留 snapshot_id 一致性校验 |
| P2 | Dashboard `/dashboard/premarket`、`/events`；stock `/global-board`、`/watchlist` | 盘前 2.473 秒；事件 2.339 秒；stock 全球 3.339 秒，自选 limit1 2.203 秒 | 少量样本，尚未完成独立分层归因；先记录分阶段耗时，检查整包读取/缺分页，避免凭本次值扩大重构。Dashboard 全球已投影读取仅 0.327 秒，可复用这种边界 |

## 请求链条与等待放大

1. 波段页面首次用 `Promise.allSettled(selection, stats)` 等两者完成后才赋值名单。统计慢时会推迟已经取得的列表展示。应分别更新列表和统计；前端加载边界调整不能替代后端优化。
2. 波段 GET 同步依赖外部报价；上游价格批次有 10 秒单次 timeout 和重试，每一批有局部超时，但整个名单没有统一请求总预算。因此“单次 timeout=10”不等于“接口最多 10 秒”。
3. Dashboard 实际 `STOCK_ANALYZER_TIMEOUT_SECONDS=60`；Web Nginx 没有显式设置代理读取超时，线上日志已有 upstream timed out。不能仅把 timeout 加到更大，延长排队会掩盖问题。行业工作台前端 60 秒已结束，63.77 秒时后端查询仍在运行，说明连接超时没有自动终止后台 SQL。
4. 读取大 JSON 会叠加 PostgreSQL JSON 解码、Python组装/校验、Dashboard归档、再次序列化和浏览器解析。公网波段 gzip 后约 256 KB，本次下载只约 0.18 秒；gzip 不是未开启，也不能解决之前的计算/数据库等待。

## 数据库现场证据及边界

`swing_daily_bar` 统计约 94.8 万活行、16.5 万死行；`a_share_snapshot` 约 44.9 万活行；分钟表 `intraday_stock_bar` 约 1182 万活行。这些是 `pg_stat_user_tables` 估计值，非本轮 COUNT(*) 扫描。

行业覆盖率 SQL 的计划使用已有主键反向 Index Only Scan，随后 Incremental Sort 和按日期 Aggregate；它不是“缺少索引导致没有任何索引扫描”。去掉主键已保证不必要的 DISTINCT，可以先减少排序，再把完整性聚合移出请求路径。涨停日期 SQL 的计划对约 45 万输入行排序去重，LIMIT 不能让前面少读相应行。

观察到活跃请求存在 DataFileRead 和 WALWrite 等待；CPU快照随时点变化，不能据此称 CPU/内存一直耗尽。stock 库累计临时写入约 527 GB、历史 deadlocks=2，统计没有近期 reset 时间；这是累计计数，不能归因于本次 HTTP、某个查询或刚发布版本。未启用 I/O 计时；`shared_preload_libraries` 为空。本轮没有查询到 `pg_stat_statements` 的可用证据，也未为排查安装扩展或重启数据库。

## 实施顺序与验收

| 批次 | 具体交付 | 验证与拟定目标，尚非已实现收益 |
| --- | --- | --- |
| 第 1 批 | 补齐按路由的结构化耗时；修工作台覆盖率查询及涨停日期 SQL；bars 本地先返回和刷新去重；X初始化移出GET | 先验证 SQL/返回语义等价；现有历史 fallback、缺失和失败保留不变。已有缓存的读接口目标内网 P95 ≤1 秒；单个慢外源不会把普通读取拖至几十秒 |
| 第 2 批 | 波段/短线结果及统计按事实版本预生成；行情单独刷新；波段名单与统计独立展示；上游科技接口复用已发布结果 | 对同一冻结数据比较代码、评分、规则版本、模拟收益、总数与日期完全一致；同证券/数据版本只允许一次后台刷新。热缓存列表目标公网 P95 ≤2 秒；上游断网时仍快速返回标明日期的旧快照或明确不可用 |
| 第 3 批 | 资讯摘要分页/增量同步、市场结构按需读取、科技历史日期仅元数据、美股历史摘要 | 首屏数据量目标约 ≤200–300 KB gzip，按实际场景校准；完整历史与详情仍可访问。修订、复权和状态变化应正确使缓存失效 |

先用现有 FastAPI、Nginx 与 PostgreSQL，不引入 Redis、微服务拆分或整套监控集群。Nginx 记录 method、规范化 path、status、request_time、upstream_connect_time、upstream_header_time、upstream_response_time、bytes、request_id；应用记录 SQL/上游/组装/归档阶段与缓存命中。日志不记录 Cookie、Authorization、业务正文、个人参数；SSE 单独计量首事件与断连，不能按连接总时长报慢接口。

有了耗时日志后，再按路由汇总交易时段和非交易时段的样本数、P50/P95/P99、>3/10/30 秒数量、502/504、499和缓存命中，覆盖下一完整交易时段。持续观测或修复实施尚未建立，不能将本报告当作监控已上线。SQL变更需用隔离数据库及接近生产规模的数据验证计划和语义；只为已证实查询添加必要索引，生产操作单独遵守既有Change/发布授权。

## 覆盖范围与未执行项

已测主要列表/统计/历史、个股图、资金流、行业工作台、涨停、科技、全球、市场结构、资讯、美股、复盘、自选、席位本地订阅/报告/复核等。完整原始耗时见下方证据和附表。

未枚举每只股票、每个日期、每个参数组合；没有对创建/删除/采集/同步/AI分析等写接口做生产耗时测试；没有调用东方财富依赖的席位远程目录/明细接口。`research/stream` 是预期长连接，不以连接持续时间算慢接口。认证验证码、OAuth回调、真实安装设备体验未测。静态路由清单是对应生产代码的声明盘点，不能把未测路由标记为快。

约12小时 Nginx 日志中，短线列表 504=2；个股 bars 499=6；波段列表 499=2；波段 stats 499=1。499只说明客户端先断开，不能仅凭它认定服务器已运行了具体多少秒。另有波段401=317和策略画像404=21，属于鉴权/可用性线索，不能计为慢成功请求。日志未记录耗时字段，无法从这些历史记录还原全天慢接口排行。日志汇总含本轮探测，不能当成纯用户流量统计。

## 证据与代码定位

- [运行身份与配置](../changes/evidence/CHG-20261021-002/runtime.json)
- [Dashboard 内网第一轮37次](../changes/evidence/CHG-20261021-002/dashboard-probes.jsonl)、[补测15次](../changes/evidence/CHG-20261021-002/dashboard-followup.jsonl)、[上游12次](../changes/evidence/CHG-20261021-002/provider-probes.jsonl)、[公网6次](../changes/evidence/CHG-20261021-002/public-probes.jsonl)
- [Nginx脱敏汇总](../changes/evidence/CHG-20261021-002/nginx-summary.json)、[数据库活动](../changes/evidence/CHG-20261021-002/postgres-observation.json)、[收尾活动](../changes/evidence/CHG-20261021-002/postgres-after.json)、[表统计/索引/EXPLAIN](../changes/evidence/CHG-20261021-002/postgres-plans.json)
- [路由声明盘点](../changes/evidence/CHG-20261021-002/route-inventory.json)、[全部实测列表](../changes/evidence/CHG-20261021-002/all-observations.md)

生产精确提交代码定位：

- [stock api：行情覆盖、短线重算、波段读链路](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/api.py#L316)
- [bars：读本地后继续外采](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/stock_bars_contract.py#L170)、[每次创建采集进程并等待](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/candidate_history.py#L83)
- [行业覆盖率查询](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/sector_activity_contract.py#L34)、[涨停日期查询](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/local_db.py#L768)
- [科技上游完整组装](https://github.com/mumukun/stock-analyzer/blob/c0e30fce57ccc7a4b92bbc528e6763302b388a20/stock_analyzer/tech_board.py#L627)
- [Dashboard 波段代理与归档](https://github.com/mumukun/investment-research-dashboard/blob/3e44833217d2b280a10baf58c082225d2028c07a/backend/app/api.py#L881)、[市场结构完整历史](https://github.com/mumukun/investment-research-dashboard/blob/3e44833217d2b280a10baf58c082225d2028c07a/backend/app/market_structure.py#L465)、[科技快照加载](https://github.com/mumukun/investment-research-dashboard/blob/3e44833217d2b280a10baf58c082225d2028c07a/backend/app/tech_board.py#L619)
- [资讯上游查询](https://github.com/mumukun/marketNewsFeed/blob/99c71ec4417a4e7feda35ac5a4f9a5f9c0ff66bd/src/research_feed/storage.py#L591)、[X读取时初始化](https://github.com/mumukun/marketNewsFeed/blob/99c71ec4417a4e7feda35ac5a4f9a5f9c0ff66bd/src/admin_api.py#L70)

初次排查阶段只保存报告和脱敏证据。随后用户明确授权实施、提交及正式发布，结果见优化说明与REL-20261021-002/003。原治理checkout既有文档保持。
