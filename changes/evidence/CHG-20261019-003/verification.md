# CHG-20261019-003 验证

## 生产故障与实际源

v4.4.1精确SHA77d12f5、Image IDd790f5a8已在运行容器核验。15:30补数在15:54发布切换时中断，已完成1538只；15:55自动重试在local_db.connect初始化DDL发生DeadlockDetected。16:20授权人工续跑未再死锁，16:25:51以incomplete结束，备用源12次失败；不是功能恢复成功。只读接口仍明确blocked。

实际源抽查：新浪600009的qfq日线末日2026-10-16；东财直接请求及NAS既有mihomo代理均断开。现有腾讯函数实查返回2026-10-19：sh000001=3730.92、sz399001=11817.42、sz399006=2746.29、sh000688=1329.19。这证明该指数补源当时可用，不证明个股全部已更新，也不保证未来可用。

## 本地隔离验证

使用本任务独立postgres:16-alpine，loopback63325，未触及生产库。Dashboard Alembic upgrade head/check通过，无Dashboard新migration。Provider仅增schema_bootstrap元数据表，首次结构更新仍在事务和现有数据库advisory lock内；死锁只重试初始化，业务SQL不重放。

- Source完整unittest：441项执行，21项可选条件跳过，其他通过；最终维护dry-run异常路径进一步定向验证通过。现有Config check输出通过。
- Source波段/DB专项pytest：296项通过；最后增加锁存活检查并定向执行maintenance/close-tracking 64项通过。最终恢复专项9项通过（真实PG在清理前验证）；另补历史回退不刷今日报价的API定向测试，包括真实PG新进程在读事务持锁时无重复DDL、锁释放后旧running投影interrupted、旧数据拒收、指数补源、失败终态、retry跳过已完成日、只允许实时同规则历史回退。
- Dashboard受影响API pytest：23项通过，覆盖blocked/timeout、有效部分归档、过滤范围安全、契约错误不使用缓存掩盖；归档不被降级覆盖。
- 前端SwingSelectionView：12项通过；vue-tsc/Vite production build通过。语义日期/历史参考/中断状态与候选保留通过组件测试；未做重复浏览器截图验收。
- Backend Ruff通过，Source E9/F静态检查、compileall及diff --check通过。Source更严格的全规则Ruff有既存告警，不宣称该门禁全通过；Source CI本来使用unittest/compileall。

## 限制与状态

当前仅本地改动，未Commit/Push/PR/Tag/部署。API日期与rules_version保持历史真实值，恢复状态不追加今日报价；所有源都未更新且同规则无合格历史时仍明确blocked，不制造今日候选，不放松买入门禁。已保存历史只读可用与自动恢复不等于外部数据永远新鲜。本次未修改新闻、PG参数或删除业务数据。

## 2026-10-19正式生产发布

用户明确“修复后就尽快生产上线”。Source PR30 / v4.4.2 main5b1a7ff0e1a01e27ebe149b5e1183e04f4f66b17；Dashboard PR30+格式补正PR31 / v0.28.2 main98b7e67e252bfd5a932aecb3f827e82d22bea40c。首次Dashboard格式门禁失败未部署，补正AST相同；最终两仓main CI与候选均通过。Release REL-20261019-003部署器返回DEPLOY_PASS（10:41:07 UTC），两库可读备份、精确镜像、版本/健康/鉴权smoke通过。

18:42 CST受影响鉴权HTTP实查：Provider/Consumer均返回10/16历史788只、同rules-v5.2.0、recovery明确requested10/19/display10/16。Providerquote_refresh=historical，当前仍blocked/scan未完成，维护进程实际持锁且已处理711/5575，本轮0失败。schema_bootstrap实际指纹匹配；25个带--retry恢复时段存在。没有伪造10/19新名单，后台继续补数；当前日线是否完整不以服务200判断。详见Release Manifest和production-boundary.json。
