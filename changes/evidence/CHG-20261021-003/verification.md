# CHG-20261021-003 验证记录

2026-10-21；Python3.13；本地隔离PostgreSQL16，无生产写入。

## 范围和结果

- Provider从实际生产v4.5.0/c0e30fc修复；Consumer从v0.29.1/3e44833修复。来源、选股阈值、rules_version=swing-rules-v5.2.0和selection-v3保持原值；候选应用PATCH4.5.1/0.29.2，未创建Tag。
- Provider9项新增数据库回归覆盖：实时与显式今日读取今日状态；昨日/非交易日历史；仅复制昨日时间不算更新；新分钟行情不掩盖过期状态；盘中结束后的验收门禁；未完成扫描和公共输入缺失；收盘至扫描间隙；完成收盘后切换。不创建当日scan或模拟买入记录。
- Consumer新增代理回归（delayed/stale两种）验证今日日期、旧日线验收基准、状态时效透传及不写收盘归档；新增界面用例验证今日盘中标识、状态时间、独立基准日期和过期警示。
- 历史、超时、版本不兼容与最后健康归档保护由既有相关回归复验。页面轮询保持30秒；后台实际计算时间与报价时间独立显示，不承诺每次轮询都重算。

## 已执行

| 检查 | 结果 |
| --- | --- |
| Provider `python -m unittest discover -s tests -p 'test_*.py'` | 487 tests，OK；21项其他模块条件跳过 |
| Provider `python -m pytest -q tests/test_swing*.py tests/test_backfill_swing_states.py` | 319 passed，15 subtests passed |
| Provider `python scripts/check_config.py`；compileall；改动Python F类lint | PASS |
| Consumer `python -m pytest -q backend/tests/test_api.py -k 'swing or version'` | 30 passed，39 deselected |
| Consumer `npm test -- --run src/views/SwingSelectionView.spec.ts src/utils/swingSelection.spec.ts` | 23 passed |
| Consumer `npm run build` | vue-tsc、Vite及PWA产物PASS |
| Consumer Ruff全backend lint/格式；Alembic upgrade/check；uv lock --check | PASS，无新migration |
| 三仓 `git diff --check`、范围与最终diff检查 | PASS，原checkout无关文件未改 |

测试专用容器：codex-swing-intraday-chg20261021-003-db，127.0.0.1:55487。Provider用独立schema；Consumer用独立数据库，不复用已有开发/生产数据库。依赖从本机缓存按锁文件安装，没有升级依赖。测试日志在本机/tmp/CHG-20261021-003-*；上表为结果摘要，不复制全量日志。

## 限制与授权

用户后续仅授权先提交代码，等待其他需求完成后一起发版本。Provider本地Commit为de24ae71fa2b16dcd4a7f0af624c0372c9caf468，Consumer为250a940a6db30c6838aaa72dcbf94409bd90e167；两业务工作树干净。提交前仅去掉新增测试文件尾部空行，沿用已通过的行为验证，不重跑全套测试。暂存diff/空白/凭据模式检查通过。

未Push/PR/Merge/Tag/部署，没有CI/镜像/生产恢复证据。生产仍运行旧版，后续获统一发布授权时按Provider→Consumer完成集成、精确版本上线与验收。marketNewsFeed排除，其他任务工作树及未提交文件保留。历史8只数据缺口未补造、未删除；本次不调用新增数据商。
