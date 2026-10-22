# 本地验证（2026-10-22）

## 问题与修复证据

- 两张用户截图分别为301291的2026-10-19历史观察、300188的2026-10-22当前观察；均只有K线派生基础字段，市值/估值缺失。
- 原Provider `read_chart` 在冷/过期时返回本地日线，后台再准备完整行情；原抽屉只读取一次，后台完成后不会更新。这是数据加载缺陷，后台抓取排队/耗时会放大等待，不应仅归于性能。
- 当前Provider默认`tencent,sina`；只读核对生产配置和最近日志的安全计数，没有本轮生产HTTP/供应商探测。腾讯适配器已有市值、PE/PB、振幅和量比解析，但未以此声称这两只股票当下各字段都经真实HTTP验证。
- 可选`basic.refresh_pending`支持冷缓存与完成结果区分；抽屉每2秒重读、最多15次，切换/关闭/卸载取消。完成后停止；重读失败保留原图与重试入口。
- 同证券、同实际交易日恢复已有市场快照/图表缓存字段，振幅从同口径日线计算；真实缺失仍列出原因，历史不混入今日数据。历史补齐失败继续使用有效日线，不再阻断基础报价；较旧报价不倒退实际交易日。
- 明确的“历史只提供最新自选补充策略”限制显示为信息，普通超时/契约错误仍可重试。原模块策略和历史K线不被替代。

## 验证结果

| Scope | Command / environment | Result |
| --- | --- | --- |
| Provider+PostgreSQL | `API_PROJECTION_TEST_DATABASE_URL=<本任务localhost测试库> python -m pytest tests/test_api_projection.py tests/test_swing_contract.py tests/test_local_db.py tests/test_stock_bars_contract.py tests/test_stock_data.py -q` | 90 passed，另8 subtests passed |
| Consumer契约 | `DATABASE_URL=<本任务localhost测试库> SEED_DEMO_DATA=true PYTHONPATH=backend python -m pytest backend/tests/test_stock_detail_contract.py backend/tests/test_stock_bars_contract.py -q` | 11 passed；既有Starlette/httpx弃用警告 |
| 前端完整回归 | `npm test` | 47文件、247 tests passed |
| 前端类型与生产构建 | `npm run build` | vue-tsc、Vite、PWA构建通过 |
| 静态检查 | Provider受影响Python的Ruff F规则，Consumer新增测试Ruff、Provider compileall，三仓`git diff --check` | PASS |

PostgreSQL容器`codex-swing-stock-detail-chg006-db`为本任务新建、随机本机端口61638；测试专属schema自动清理，收尾删除本任务容器，不操作其他任务或生产数据。真实PG用例验证冷响应标待补、完整缓存停止待补，以及301291/300188和10-19/10-22缓存严格隔离。

原始checkout依赖落后于main，曾因缺klinecharts/PWA/captcha/httpx2无法运行检查；已将最新任务的既有前端依赖复制到本工作树，使用其已有Python环境只读运行。未修改其他任务的依赖、锁文件或环境；不将最初的环境失败算作通过。

## 范围与限制

原治理checkout的手册文件、Dashboard原型图和其他任务工作树全部保留。本记录为详情修复首阶段；用户随后追加授权marketNewsFeed与八项性能优化，最新范围及验收见[性能验收](performance-verification.md)。

无DDL、生产补数、规则阈值、来源、依赖或正式版本变更。源码/文档均未提交；无Push/PR/Merge/Tag/部署。未验证生产发布后的真实页面、供应商当前响应或真机视觉。旧历史原本未保存的市值/PB/量比不能凭修复恢复，仍明确缺失。
