# HTTP慢接口优化实现与验证（CHG-20261021-002）

2026-10-21，已按用户明确授权提交、合并并正式发布。本说明对应此前[真实生产慢接口清单](http-latency-audit-20261021.md)，不把本地结果当作线上收益。

## 生产发布与本次复测

2026-10-21 13:30（Asia/Shanghai）全部服务已切换并通过健康/smoke。发布：[REL-20261021-002](../releases/REL-20261021-002.yaml)（news2.4.1）、[REL-20261021-003](../releases/REL-20261021-003.yaml)（stock4.5.1、Dashboard0.29.2）。Provider/Consumer PR32/34及news PR11已合并；X提醒和中性标题为此前已上线功能，本次保留。新增波段盘中修复CHG-20261021-003一并上线。

以下为13:31左右少量带鉴权GET观察（服务内HTTP）；不同时间负载/数据不同，不代表全天P95或严格同负载A/B。新summary/compact参数是前端现在采用的读取方式，保留全文与原完整接口。

| 接口 | 排查时 | 本次上线后 | 状态 |
| --- | --- | --- | --- |
| 行业工作台 | 60.065秒502 | 0.051秒 | 200 |
| 个股bars（300188） | 37.308秒 | 0.171秒 | 200 |
| 波段列表 | 6.115–10.773秒 | 0.941秒 | 200 |
| 波段stats | 4.746 / 0.564秒 | 0.046秒 | 200 |
| 短线列表 | 6.324秒 | 2.065秒 | 200 |
| 研究列表（现summary=true、500条） | 9.435秒（完整） | 0.613秒 | 200 |
| 市场结构（现compact=true） | 8.788秒（完整） | 0.897秒 | 200 |
| Dashboard科技看板 | 本次未做同参数前测 | 1.271秒 | 200 |
| news研究100条 | 14.603秒 | 0.418秒 | 200 |
| X用户20条 | 8.684秒 | 0.036秒 | 200 |
| X用量 | 约4.7秒 | **4.099秒，仍有优化空间** | 200 |

公网HTTPS波段为1.528秒（TTFB0.959秒，gzip248662bytes），排查时6.952秒；健康0.265秒。真实波段trade_date=2026-10-21、selection_phase=intraday、日线验收基准2026-10-20，833条；状态时间13:25:56、freshness_status=delayed如实保留，不能解释成每秒重算。验证GET前后当日收盘归档ID/updated_at不变。

[服务内抽测](../releases/evidence/REL-20261021-003/http-after.jsonl)、[公网抽测](../releases/evidence/REL-20261021-003/http-public-after.json)、[部署回执](../releases/evidence/REL-20261021-003/deployment.receipt.json)。三库各执行一次既有可读备份；stock库备份329.961秒、Dashboard25.206秒，镜像拉取与容器启动也计入总等待。从用户指令05:05:59UTC到全部生产可用05:30:41UTC为24分42秒，未达到5分钟目标；治理归档在之后进行。

X用量聚合仍偏慢；后续需先取得对应查询计划再处理。完整波段仍约3.8MB，真实compact市场结构仍约4.05MB；此前合成数据的96%体积减少不能当作真实生产减少比例。

## 当前实施方案

先修重复计算、请求内外采和大JSON读取，复用现有PostgreSQL，不引入Redis。

| 原慢接口 | 本次落地 | 实际边界 |
| --- | --- | --- |
| 行业工作台（线上60秒502） | 等价COUNT(*)、同日输入代次失效、默认工作台后台发布 | 自定义行业/天数仍原计算路径；共享行业聚合可复用 |
| bars / candles（线上37秒/4.9秒） | 本地已存日线立即返回，持久化按参数隔离结果，后台合并刷新 | 冷且无数据503准备中；每进程最多2项、SDK单证券日线25秒预算，报价仍有原超时 |
| 涨停梯队（线上18秒） | 每个来源先取最近N个日期，再UNION；保留无run的历史fallback | 沿用既有索引与结果口径 |
| 波段/短线列表、波段stats | 默认参数读取已完成PG发布结果；报价用已采集行情 | 输入代次检查30秒、同代次最长5分钟重建；筛选/历史/旧契约仍原计算，不冒用默认名单 |
| 科技看板 | 上游发布完整包；Dashboard日期列表不拉正文，近期比较只读5份 | 保持snapshot_id与实时质量评估；不改变成分、报价或选股规则 |
| 研究资讯上游（线上14.6秒） | 先选本页ID再读原文/分析，增加稳定ID排序 | 输出契约不变；尚无生产SQL计划，不宣称全部14秒已消除 |
| Dashboard研究列表（线上9.4秒） | 摘要先显示，选择后取完整详情；保留原500条范围和筛选 | 默认旧API仍完整，新接口登录权限相同，SSE路由保持 |
| 市场结构（线上8.8秒/5.9MB） | 读取历史代次元数据、最多256份进程缓存；曲线响应剔除重复来源正文 | 全部日期、数值/null保留；完整默认响应及最新证据仍可读。冷缓存批量读，无逐日N+1 |
| X users / usage（线上8.7/4.7秒） | 初始化移至接收请求前且只成功执行一次 | 无新增X/LLM调用；锁/连接等待仍需上线分层观察 |

准备结果与真实业务时间分开存储；刷新失败立即标记旧结果、未验证90秒stale、300秒或跨上海自然日不可直接复用。波段过期禁止新发布，短线失败可显示真实旧归档并醒目提示不可作为当日新信号。健康归档不被失败/降级响应覆盖。

新增API/Nginx/新闻服务脱敏耗时日志，能区分响应准备、代理等待与完整传输；不记录查询串、认证头或客户端身份。SSE响应准备时间不解释为流连接总时长。

## 本地等价性与性能证据

独立Docker PostgreSQL16（127.0.0.1:55489，专用测试容器），合成数据，不使用生产数据。SQL与日期结果逐项相等；市场结构所有日期/事实与缺失值不变，研究条目ID集合/顺序相同。5次数据库读取样本取中位数，宿主CPU/磁盘有其他任务，以下不代表HTTP端到端或生产P95。

| 场景 | 优化前中位数 | 优化后中位数 |
| --- | --- | --- |
| 行业覆盖统计（95万行） | 2127.3 ms | 121.0 ms |
| 涨停日期查询（45万行） | 287.3 ms | 5.2 ms |
| 市场结构121日读取 | 262.7 ms | 16.8 ms |
| 研究列表500条读取 | 292.6 ms | 46.2 ms |

- 市场结构示例正文：5,364,139 → 209,083 bytes（减少96.1%），保留121天。
- 研究500条：7,109,890 → 309,390 bytes（减少95.6%），全文仍可按ID取回。
- 862条约3.95MB发布结果，连续20次读取只构建1次，本地读取中位数160.9ms；波段完整正文仍约4MB，尚未引入分页UI。
- [可复现脚本](../changes/evidence/CHG-20261021-002/benchmark-local.py)、[原始样本](../changes/evidence/CHG-20261021-002/benchmark-local.json)。脚本只允许本任务localhost测试库，临时schema自动清理。

## 验证

| 边界 | 结果与证据 |
| --- | --- |
| stock-analyzer受影响契约、SQL、图表、选股、科技及PG发布 | [98 passed + 15 subtests](../changes/evidence/CHG-20261021-002/optimization-stock-tests.log)；最终报价时效/失败立即stale等[15 passed](../changes/evidence/CHG-20261021-002/optimization-stock-followup.log) |
| Dashboard后端 | 新建测试库migration head；[286 passed / 3 skipped](../changes/evidence/CHG-20261021-002/optimization-dashboard-tests.log)；最后缓存批量读取、日志与短线故障边界[31 passed](../changes/evidence/CHG-20261021-002/optimization-dashboard-followup.log) |
| 前端 | [214 passed全量](../changes/evidence/CHG-20261021-002/optimization-frontend-tests.log)，最终三个页面[20 passed](../changes/evidence/CHG-20261021-002/optimization-frontend-followup.log)；[vue-tsc和production build](../changes/evidence/CHG-20261021-002/optimization-frontend-build.log) |
| marketNewsFeed | [24 passed + synthetic config check](../changes/evidence/CHG-20261021-002/optimization-news-tests.log)，外部HTTP/通知均mock |
| 静态/配置 | Dashboard Ruff、provider受影响文件F规则、三服务compileall、git diff --check均通过；provider synthetic config passed；本地现有Web镜像加载新nginx.conf执行nginx -t通过 |

Dashboard席位持久化测试文件要求固定localhost:55441/seat_test，未借用其他任务数据库，未纳入本轮全量命令；另3个测试按原条件skip。上述计数有重复回归，不简单相加。FastAPI TestClient有既有httpx弃用警告，不影响结果。未运行生产压测、外部真实行情请求、真实费用/消息、CI或发布smoke。

## 数据与发布影响

stock-analyzer增加幂等派生表api_read_projection（含build/check/failure时间与输入revision），原业务表无破坏性迁移。旧程序回退可保留该表。Dashboard只增加可选查询和详情端点，默认旧契约兼容；无需Alembic变更。news数据模型不变。已发布版本为stock4.5.1、Dashboard0.29.2、news2.4.1；规则/contract版本保持。

实际发布顺序：stock-analyzer、marketNewsFeed可独立在前，Dashboard在后；遵循同一次真实发布的依赖/契约检查。沿用此前已验证的生产版本回滚点，不从本地main推测新生产身份。

## 剩余验收和限制

1. 业务PR已合并且生产发布成功；本次抽测结果见上文，全天分布仍需积累新增日志。
2. 后续通过新增日志观察不同交易时段、冷启动和源故障的全天分布；本次少量上线抽测不能替代长期指标。
3. 自定义查询、历史大结果、stock市场结构上游组装、波段完整4MB和Dashboard大快照归档仍有成本；如实测仍慢，再针对实际剩余路径优化。news上游排序索引需取得生产计划后决定，当前不盲目加索引。
4. 图表按日期/参数的持久键暂未自动清理；根据实际增长另定保留策略。多实例若出现共享热点/并发负载，再评估Redis；这轮不新增该运维依赖。
5. CHG-20261021-003已在本次集成并验证后发布，原独立分支/worktree保留，未清理或覆盖其历史。

所有改动位于 `/Users/mukun/.codex/worktrees/http-latency-audit/` 四个独立仓库；原始checkout及其他任务工作保留。专用本地测试容器保留用于复现；NAS仅按本次正式授权发布所选三服务，其他任务容器不变。
