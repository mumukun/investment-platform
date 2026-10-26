# CHG-20261026-006 本地验证证据

以下保留开发阶段本地验证范围；后续最终合并和正式发布见 REL-20261026-003。版本候选：stock-analyzer 4.12.0、Dashboard 0.39.0。

## 复现环境

两个业务 worktree 位于 `/private/tmp/CHG-20261026-006/`，基线分别 e85c12c、fcdd402；任务 Python 3.13 虚拟环境同目录 `venv`。独立容器 `codex-intraday-chg20261026-006-db`，本机端口 55506、PostgreSQL 16；Provider 各测试随机 schema，Consumer 独立测试库，非生产。行情/HTTP 返回合成或替身，不调用腾讯/新浪、东财/同花顺、通知、飞书或付费接口。

Provider 设置 `SWING_TEST_DATABASE_URL`、`SHORT_TEST_DATABASE_URL`，API 补跑另设 `API_PROJECTION_TEST_DATABASE_URL`；Consumer 设置隔离 `DATABASE_URL`、`SEED_DEMO_DATA=true`、`PYTHONPATH=backend`。DSN 不写入共享证据。

## 自动验证

- Provider：`python -m pytest -q`，文件为 `test_current_candidate_contracts.py`、`test_current_short.py`、`test_swing_intraday_discovery.py`、`test_swing_features.py`、`test_swing_availability.py`、`test_swing_contract_v3.py`、`test_swing_sources.py`、`test_short_tail.py`、`test_short_tail_refresh.py`、`test_swing_scheduler.py`、`test_watchlist_strategy_contract.py`、`test_api_projection.py`、`test_stock_data.py`、`test_swing_store.py`、`test_swing_runtime.py`、`test_swing_engine_v5.py`、`test_swing_engine_v6.py`（均在 tests/）。结果 229 passed、19 skipped、23 subtests passed。缺少专用 API 测试 DSN 的 19 项不能算通过；随后补跑 `tests/test_api_projection.py tests/test_swing_v6_pipeline.py`，25 passed、无跳过。最后 legacy 自选兼容回归单项 1 passed，计数不与前述简单累加。
- Consumer：`python -m pytest -q backend/tests/test_current_candidates.py backend/tests/test_swing_live_projection.py backend/tests/test_swing_smoke.py backend/tests/test_short_tail.py backend/tests/test_short_tail_pipeline.py backend/tests/test_short_tail_smoke.py backend/tests/test_watchlist_projection.py`：46 passed，无跳过。
- 前端：`npm test -- src/views/SwingSelectionView.spec.ts src/components/ShortTailSelection.spec.ts src/views/WatchlistView.spec.ts src/utils/swingSelection.spec.ts src/utils/observationTime.spec.ts`：5 文件、73 passed。
- `npm run build`：vue-tsc/Vite/PWA 通过，0.39.0。Provider check_config/compileall、Consumer compileall/全 backend Ruff、Provider 新模块 Ruff F 与两仓空白检查通过。
- 测试有 Starlette BlockingPortal 弃用提示，无功能失败。曾发现 Consumer DISTINCT/ORDER BY 表达式问题，修复后上述 46 项通过。未以先前失败日志作为成功证据。

## 核心证据与局限

Provider `tests/export_current_candidate_fixtures.py` 经实际任务、PG 与鉴权 HTTP 生成 Consumer `backend/tests/fixtures/current-candidates/` 两份合成契约；后者经真实客户端、PG 和 HTTP 页面读取，查询不再等待上游。详情跨内存清除仍从 PG 取同代证据。四分钟仅是年龄保留测试样例，产品无四分钟截止；新事实否决逐股替换，其余原结果保留。补充跨日自动跟随、手选历史固定、失败时保留内容。

波段黄金结果 `tests/fixtures/intraday-original-results.json` 从冻结原基线 e85c12c 在同一合成输入生成，四项路径的状态、分数、关键位、风险距离、确认等逐项一致。原 swing/short/tail 纯规则文件未修改。有限样本不证明实际全市场零差异；无收益承诺。

## 性能观测

`tests/benchmark_current_candidates.py`：5,224 合成证券，实际特征/规则/存储/发布与隔离 PG；仅外部行情抓取被替代。原首轮约 69 秒只处理 2,160 只；针对同时间历史 SQL、重复序列化及大 JSON 缓存优化后，单次测得 44.122 秒，9 批，处理和发布 5,224 只。

该值是本机单次 Provider 观测，不是 NAS、腾讯/新浪网络或大规模三入口端到端传播证据。120 秒仅为优化参考，不作显示或开发验收硬门禁。未测量的大规模 Consumer/页面传播、实际 NAS 盘中及人工体验明确保留，不能报告为通过。

详细原始本地日志位于任务临时目录的 `provider-verified.log`、`provider-projection-verified.log`、`consumer-verified.log`、`frontend-verified.log`、`frontend-build-verified.log`、`benchmark-wave-compressed.log`。共享记录只保存以上脱敏结论，不复制原始运行载荷。
