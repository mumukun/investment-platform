# 盘中资金曲线修复验证（2026-10-19）

## 原因与实现

生产Provider v4.4.0 /759c9c9、stock-watch同镜像；Dashboard v0.28.0 /122a79d的API/Web均与REL-20261018-010镜像及OCI revision一致。只读SSH inspect和源health核验，无生产写入/重启/发布。原Sina-v1分支硬编码行业分钟unavailable，是此前未核验ssx_bkzj_fszs而主动停用，非CHG-011本地PG优化造成。

保留拒绝旧分钟历史，不使用异常价格/ratio推算主力额。改为后台每60秒读取新浪官方行业实时表ssl_bkzj_bk与前后ssi_get_extend(id=2)资金批次时间，48行业身份/完整数量/有限值/非负入出流/入出净额恒等式及交易分钟、陈旧/未来/跨分钟批次核验。每源分钟一批聚合JSON，复用sector_fund_fact既有主键与索引；网络完成后才开启短写事务。GET只读采样事实。

新显式capital-flow-sina-v2标识全部单净额，旧v1原语义保留。来源时间是官方资金整体批次时间，不能当作每行业或股票的逐笔时钟；供应商自身分类/延迟限制仍存在。与全市场及日主力资金分开，禁止合计或比较为同口径。无预测/主力金额/价格确认。行业实时表与行业均价/日资金原数据均不修改。

曲线从首次实际采集分钟开始；缺失为null断线，单点可见且不平滑；午休不计入过期时钟，延迟显式stale。5/15/30分钟差仅使用对应墙钟边界的真实样本，缺数显示--，不按样本个数冒充时长。旧新浪历史继续可查，同版本失败保留最后有效曲线。

## 真实公开源与隔离HTTP/PG

- 专属本地PG16容器codex-sina-intraday-chg001-db，127.0.0.1:63446；Provider chg_sectorfund_provider、Consumer investment_dashboard各自数据库，Consumer不直读Provider表。
- 真实公开新浪数据自14:24采样，14:26未采集保留null，未补造早盘；14:29:47最近批次，共5批、48行业。不是生产采集，不将此本地数据搬到生产。
- 两侧实际Uvicorn TCP HTTP、Bearer鉴权Provider、实际Consumer客户端与本地快照持久化，默认12条、造纸/玻璃/电子器件分别返回200；48行业分两组24条经Consumer HTTP全部通过，代码集合逐项相等。
- 未带源Token 401、未核验行业400；旧v1仍unavailable。调用前后Provider采样批数相同，证明读链路未触发采集。摘要见[live-http.json](live-http.json)，完整造纸新契约响应见[paper-live-envelope.json](paper-live-envelope.json)。仅使用本地合成鉴权字符串，未读取生产凭据。
- 实际Vue组件、Element Plus、Vite代理真实Consumer HTTP，无fetch拦截/行情替身。默认窄屏446px下曲线可见，维持图表内部横向滚动；点选电子信息后抽屉显示“盘中资金采样 / 采样事实 / 行业全部单净流入”，未具边界样本时5/15/30分钟为--。当前本地日资金尚未采集，日频面板明确降级，不影响盘中曲线。本轮未重验日频采集、个股行情或生产页面。

## 回归

- Provider：受影响Sina采样/日频/成员/资金/只读API/调度测试92 passed、1 optional skipped；该成员PG测试随后显式设置SECTOR_FUND_MEMBERS_TEST_DATABASE_URL补跑1 passed，共93项通过。新测试含时钟、数值、目录、重复写、失败保留、未来/他日查询、缺失断线、后台采样、路由选择转发。
- Consumer：受影响契约/市场投影/Sina研究/板块研究/复盘/API共113 passed。首次同名已用测试库混入本次真实盘中归档后，demo复盘latest选择真实未收盘日返回503；换独立全新investment_dashboard_chg019001_tests、执行既有alembic upgrade后同组113通过，未修改业务代码掩盖数据污染。Starlette/httpx现有弃用提示1条。
- 前端：资金页面、曲线标签及行业面板3文件9 tests passed；Vue类型检查与Vite生产构建通过。新页面回归覆盖全部单说明、保留null、单独事实入口、精确5分钟变化与缺失15分钟显示--。
- 受影响Ruff、compileall、各仓git diff --check、Dashboard VERSION/package/lock/pyproject/uv.lock的0.28.1一致性通过。Provider4.4.1。无新依赖/DDL/迁移；本地只运行既有迁移建立测试库。

## 状态与限制

修改仅在隔离hotfix/CHG-20261019-001-sina-intraday工作树，未暂存、提交、推送、合并、Tag或部署。生产保持原版本，修复尚未生效。未来正式上线需Provider→Dashboard，首个快照后显示单点，随后逐步积累曲线；未采集的历史分钟无法恢复。未更改PG参数或历史保留；CHG-011优化、CHG-012飞书队列下架、marketNewsFeed及用户原checkout未动。

临时Provider/Consumer/Vite进程和验收标签页已停止；专属测试容器在测试全部结束后清理。保留工作树和本记录，治理文件尚未提交，不标READY或生产成功。
