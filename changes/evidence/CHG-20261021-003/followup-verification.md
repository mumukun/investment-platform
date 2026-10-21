# CHG-20261021-003 追加验证：当日候选与真实确认日期

2026-10-21；本地Python3.13、PostgreSQL16，模拟行情和隔离数据库，无生产写入。

## 根因与边界

只读生产逐票核查发现：13:47的1049路径与昨日比较有294状态、252参与判断和1021价格变化，结构分不变。13:52响应833只，主导可计划参与中31只为盘中确认、28只沿用此前收盘确认。实际存在当日结果，但混合展示且缺少确认日期；盘中持久化未同步更新matched/missing/risk_reasons，部分个股今日状态仍附昨日依据。不能将问题仅归因缓存或仅把顶层日期改成今天。

不改变既有“完整日线结构＋盘中确认”策略、评分、阈值、排序和收盘账本。新增真实事件日期/时间是兼容字段，缺少盘中事件不猜作今日；缺少事件但收盘依据可核实时仅返回真实日线确认日期，精确时间仍未知。历史查询只使用不晚于观察日、相同规则版本的事件。

## 已完成与验证

| 检查 | 结果 |
| --- | --- |
| Provider标准unittest discover | 492 tests，OK，21项其他模块条件跳过 |
| Provider `pytest -q tests/test_swing*.py` | 321 passed，15 subtests passed |
| Provider `pytest -q tests/test_backfill_swing_states.py` | 2 passed |
| Provider `pytest -q tests/test_api_projection.py`，隔离真实PostgreSQL | 11 passed |
| Provider配置检查、compileall、改动Python F类lint | PASS |
| Consumer `pytest -q backend/tests/test_api.py` | 72 passed |
| Consumer波段页面与工具Vitest | 26 passed |
| Consumer `npm run build` | vue-tsc、Vite及PWA构建PASS |
| Consumer Ruff全backend lint/格式、uv lock --check | PASS |
| 三仓diff/暂存diff空白与范围检查 | PASS |

新增回归覆盖真实盘中循环→PostgreSQL写入→契约读取，确认本轮证据替代昨日阻断；今日确认事件与后来状态刷新分别保留、旧日延续动作说明、无事件不伪造日期、历史不读未来事件；Consumer透传和非法/未来日期拒绝；默认清单隔离昨日未计算条目、当日新确认与此前延续筛选及来源日期。既有陈旧/缺失/阻断/历史/收盘账本保护复验通过。

专用容器 `codex-swing-current-signals-chg003-db` 使用随机宿主端口127.0.0.1:58635，Provider测试库与Consumer测试库分开，Provider每例独立schema。首次两个Provider套件并行引发数据库级advisory锁干扰，改为串行后全通过；首次复用环境缺TestClient测试依赖，随后建立工作树独立venv并按requirements及CI测试依赖从缓存安装，标准检查通过。未调整业务锁或测试断言绕过失败。测试日志位于本机 `/tmp/CHG-20261021-003-followup-*`，不复制完整日志。

## 本地交付与限制

- Provider从真实生产v4.5.1/31f42130f5481ead0b7718b982d44c2f861ffbd5修复，本地提交01af36192b88ade58a271fda667e9bc1ea8487de，候选4.5.2。
- Consumer从真实生产v0.29.2/5961d61d44187fe2a2bfbe54f3bb7cd0e151ee8d修复，本地提交bed8100459c429e71823a46bcaae27717102cb11，候选0.29.3。
- 两仓使用 `hotfix/CHG-20261021-003-current-signals`，位于 `/Users/mukun/.codex/worktrees/swing-current-signals/` 下，提交后干净。沿用用户此前同一功能的本地提交授权；未Push/PR/Merge/Tag/部署，未标READY，未执行本次生产浏览器或手机视觉验收。
- 无新migration、历史回填、真实通知或新增数据商；marketNewsFeed与其他任务不纳入。仍需统一集成发布及生产逐票验证，候选版本可在正式冻结时随实际发布范围调整。原Release事实和其他checkout保留。
