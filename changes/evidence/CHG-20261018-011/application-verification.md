# CHG-20261018-011 应用侧优化验证（2026-10-19）

## 已实现与边界

1. 保留上轮短线分钟量比优化，未减少采集或更改累计成交额语义。
2. 波段盘中按股票一次批量读取最近交易日中minute<=当前时间的最后非空金额，各策略路径共享。日历约束、缺失分钟、零值、日期上界和样本数按旧单股读取逐项对比。
3. V5.2有同日行情时跳过随后被覆盖的全市场档案查询；缺失则仍回退档案。档案业务值及COALESCE分类不变时不产生UPDATE，updated_at随实际内容变化更新；行情新鲜度仍使用行情快照时间。
4. 科技/全球通过既有索引按实体取最新记录。科技样本按实体取最近60个不同data_time的最新observed_at修订，保留原全局时间升序。相同排序键原查询未定义额外顺序，本轮不引入新的业务排序键。
5. job_run开始记录在工作前提交并关闭连接，成功/失败状态用独立短事务提交；工作不持有日志事务。正常状态与异常消息按旧字段记录，失败日志现在可实际持久化。
6. 短线跟踪非settled_only的限量查询下推LIMIT，仅加载返回股票/日期的价格；总数独立计算并使用同一REPEATABLE READ只读事务，避免并发回填造成总数与列表不一致。已结算筛选必须先按观察日计算状态，继续沿用完整计算；统计接口保留完整样本。
7. 复盘日期菜单只读取日期/域/业务时间，已存复盘仅读日期；readiness只读业务时间/质量/版本。详情仍使用完整JSON。
8. 科技/全球投影仅generated_at变化时不重写JSON。business_time和SyncState仍按旧逻辑推进成功时间，读取入口从business_time返回生成时间；data_time/collected_at与历史日期不重写，snapshot_id/409逻辑不变。失败不推进成功时间。
9. X成员同步最近时间查询增加(endpoint,created_at DESC)索引，默认dry-run并发准备入口，幂等及无效索引失败停止验证通过。原调用和周期不变。

本轮没有调整刷新频率、生产PG参数、统计扩展、历史保留、数据清理或采集范围；CHG-012飞书队列下架仍是独立本地修改。

## 本地PG16.14性能证据

| 场景 | 数据 | 原执行 | 新执行 | 结果 |
| --- | --- | --- | --- | --- |
| 短线分钟量比 | 120万行，1000股/20日 | 约830ms、40万返回行、2069临时写块 | 约100ms、2万返回行、0临时写块 | [既有计划](local-benchmark-wide.json)，目标分钟切片等价 |
| 波段同时间历史 | 10万分钟行，100股/20日 | 100次连接、1669.047ms | 1次连接、31.673ms | [本轮证据](application-benchmark.json)，逐股列表相等 |
| 科技最新报价 | 10万事实/100实体 | 16.184ms | 1.674ms | 同上，最新事实相等 |
| 全球最新报价 | 10万事实/100实体 | 40.883ms | 4.402ms | [证据](global-benchmark.json)，最新事实相等 |

只代表本机Docker合成数据及该段读取，不代表生产页面延迟或整体倍数。首次科技跨kind跳转计划在PG16回退，已按kind分别定位修正；[淘汰方案记录](application-benchmark-first-plan.json)仅解释取舍，不是交付性能。数值可能受并发测试与缓存影响。

## 回归与检查

- stock-analyzer：SHORT_HISTORY_TEST_DATABASE_URL、SHORT_TEST_DATABASE_URL、SWING_TEST_DATABASE_URL、TECH_BOARD_TEST_DB均指向127.0.0.1的自建chg_pg_query_011库；受影响short*/swing*/tech/global/local_db/application/watchlist-strategy测试466 passed，19 subtests。随后新增一致性事务的short_tracking 19项通过；现有排序单测补齐原缺失的验收mock，未改生产发布门禁。
- Dashboard：Python3.13、uv.lock隔离依赖，全新自建数据库经alembic upgrade head。backend/tests排除固定专用库的test_seat_tracking.py后260 passed、3 skipped。3项为未启用的独立资金个股集成；席位模块不在本次修改内，完整尝试中16项通过、9项因固定55441/seat_test环境限制未执行；该端口已有其他本地服务，未使用或修改它。
- Dashboard测试库重复使用曾导致demo/真实复盘残留并返回503，换全新自建库后相同API回归通过，未为测试改变业务逻辑。Starlette/httpx兼容弃用提示为现有依赖告警，不影响通过。
- Dashboard受影响Ruff、compileall、alembic check及VERSION/package/pyproject/lock元数据一致性通过。本轮无前端逻辑变化，不重复运行UI构建或人工页面验收。
- marketNewsFeed：只用合成配置和market_news_test随机schema，unittest discover 97 tests/OK；check_config、compileall、dry-run和diff检查通过。索引3项专项含查询计划不再Seq Scan、并发准备幂等、无效索引停止且不自动删除。
- 无真实消息、LLM费用或生产数据用于测试。

## 契约专项核对

Producer /api/integrations/investment-dashboard/global-board → Consumer /api/v1/global-board：investment-dashboard-global-board-v1。
Producer /api/integrations/investment-dashboard/tech-board → Consumer /api/v1/tech-board及members/history/concepts：investment-dashboard-tech-board-v1。
结构、必填项、原始价格/百分比单位、时区、映射和规则版本均未改。报价时间仍是来源时间，generated_at仍是有效Provider响应生成时间；只是重复事实时从投影元数据读取该值。保留未知版本拒绝、鉴权边界、缺失/失败的last-known-good、历史as_of和snapshot_id一致性；已有真实捕获fixture、模拟故障/修订/过期测试验证，无生产集成成功宣称。

## 发布与剩余

所有修改仅在隔离工作树，未提交、推送、合并或发布。生产尚未获得这些改进。X索引需在正式发布授权与备份后执行并发准备；不移动已有Tag，不从main浮动部署。不清理历史队列表或行情数据。需要上线后完整交易时段观测，才能给出系统整体收益。
