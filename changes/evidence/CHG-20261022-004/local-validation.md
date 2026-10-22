# CHG-20261022-004 本地验收

日期：2026-10-22。证据仅来自隔离本地工作树、合成数据与离线契约；没有生产数据写入、真实行情采集、回填或发布。

## 实现与兼容清单

- Provider工作树：`/Users/mukun/.codex/worktrees/swing-selection-optimization/stock-analyzer`。
- Consumer工作树：`/Users/mukun/.codex/worktrees/swing-selection-optimization/investment-research-dashboard`。
- 默认`swing-rules-v5.2.0`，候选`swing-rules-v6.0.0`；日线/盘中特征分别v3/v2。旧V5仅附加解释，回归核对决策字段逐项保持。
- selection-v3 stock/path的可选context/tier，原四决策保持；context价格为元、方向为元/日、量比为倍数、收盘位置0—1，原close_location_pct仍0—100。观测日、日线引用日、状态更新时间与确认日分开。
- PostgreSQL setup/state_event增加可空列，原模拟账本冻结证据；V6健康kind与Consumer归档按规则隔离。旧字段、旧记录、参与口径counts与历史分母不重定义。
- 鉴权、超时/失败、stale、历史回退和只读GET延续现行契约。故障不覆盖健康归档，未知/缺失不冒充0或已确认。

## 已执行

| 检查 | 结果 / 适用范围 |
| --- | --- |
| Provider `python scripts/check_config.py` | passed |
| Provider `pytest -q tests` | 786 passed，141 skipped，73 subtests；隔离库未配置的其他专项按原保护跳过 |
| Provider标准`unittest discover` | 547 tests，OK，22 skipped；初次共享环境缺httpx、旧测试配置兼容问题修复后在独立Python3.13环境重跑 |
| 波段全部`pytest tests/test_swing_*.py tests/test_backfill_swing_states.py` | 372 passed，15 subtests；覆盖旧规则、特征、状态、来源、健康、契约、账本与V6 |
| 最终规则/审计 `test_swing_engine_v6.py` + `test_swing_validation.py` | 24 passed；包括原精度、0/缺失、单/多组临界、真实连续日/不同完整周期、周期前阶段、复权、冻结、到期/同日失效及旧V5解释 |
| 最终`test_swing_v6_pipeline.py` | 5 passed；真实PostgreSQL runtime/store/health/contract/tracking，行情为合成；包括真实日线验收与收盘扫描、缩量留存、GET只读、版本隔离与账本冻结 |
| Consumer `pytest test_api.py -k swing` | 36 passed；覆盖V5/V6故障回退与可选字段 |
| Consumer完整后端 | 332 passed，3 skipped，9项席位测试在fixture保护处拒绝随机端口，不是波段断言失败；未绕过白名单或使用其他任务数据库 |
| Consumer `npm test` | 47文件，242 tests passed |
| Consumer最终受影响Vitest | 3文件，28 tests passed |
| Consumer `npm run build` | 类型检查/Vite/PWA passed；独立工作树npm ci锁定依赖，未改共享node_modules |
| Consumer Ruff、隔离库Alembic upgrade/check | passed；无新增Dashboard migration |
| Provider新增模块Ruff、compileall | passed |
| Provider→Consumer实际输出离线验证 | 用Provider真实构建的2股V6响应校验Consumer Pydantic模型，passed；不等于生产集成验收 |

Provider测试库与Dashboard测试库均由本任务独立PostgreSQL16容器创建；不使用生产或其他任务数据库。依赖在独立工作树安装，Python3.13；没有为依赖问题修改业务规则或降低测试门槛。

## 性能证据

`SWING_TEST_DATABASE_URL=<isolated-local-test-url> python tests/benchmark_swing_v6.py 2` 及 `20`。测试库名称/本机地址有保护；行情采集和市场/行业聚合使用明确合成返回，规则、存储与GET真实执行。原始结果见本目录benchmark-2.json与benchmark-20.json。

这是一次小样本本机对照，扫描时含tracemalloc开销，GET P95按10次读取得到；不得外推为全市场性能。计数为连接级execute调用（含元数据、锁和少量写语句，不含executemany批量写入）；两种规模均保持固定批次（V6比V5增加少量有界读取），没有逐股新增网络请求或N+1数据库读取。真实全市场扫描、网络等待、调度间隔容量仍待验证。

## 历史效果与未覆盖

参数采用状态：**待验证**。没有完整多股票时间外回放或未查看留出的收益报告，不能宣称冰山冷热更早入选、命中率改善或收益为正。000530只作代码案例，效果审计会要求将其排除。

`scripts/evaluate_swing_candidate.py`审计冻结重放输出：时间50/25/25、10日清除、中段3期、共同/新增/提前/延后/旧独有、次日开盘执行与收盘理论口径分开、30/50bps成本、5/10日整日块及Holm检验、同市况风险尾部/失败率。历史行情日期可在参数冻结之前，冻结须早于留出评估执行，不能提前查看留出调参。来源正确性和消融真实性仍需外部逐时点重放与人工证据；工具不代替这些工作，不自动激活规则。缺少重放数据的合成空输入示例见missing-replay-example.json，实际退出码2、待验证，未产生虚构收益。

完整页面浏览器、小屏/真机和生产验证未执行；组件真实折叠/表格DOM与现有页面测试已通过。没有发送外部消息、创建PR、合并、Tag或部署。代码和文档全部仅本地未提交。
