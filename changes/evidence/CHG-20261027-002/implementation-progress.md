# 本地实施与验证完成，未提交或发布

用户已授权开发和必要验证，2026-10-28追加长期项目规范。最终范围与限制见Change及architecture-verification.json；本文件不替代共享已提交状态。

## 工作树

三个仓库位于 `/private/tmp/CHG-20261027-002/`，同名分支 `fix/CHG-20261027-002-daily-data-reuse`，基线stock dde82a8 / governance217c091 / dashboard55ed3c1。原checkout的手册、原型及其他任务未改动。未Commit/Push/PR/Merge/Tag/部署，未标记READY。

## 已完成

- 平台AGENTS第14节、两业务AGENTS：独立基础目录/计划/来源/补数/写入，业务只读基础并写自己的结果；缺数、刷新、自选、功能开关不反向触发采集。新增公共能力由数据服务扩展。
- stock-data独立Compose进程，与API/业务同镜像/同PG，来源适配及功能生命周期分开。数据运行参数不加载完整业务Settings，错误策略参数不阻断数据启动；已有数据配置键保持兼容。会话锁、代次、事务所有权及退出后回调防护；API/business来源与基础writer角色拒绝。
- market_data的模型/增量schema/仓储/只读reader/catalog/worker及独立来源任务。覆盖A股参考、统一行情、快照、raw/qfq日线、真实5分钟及累计兼容、科技/轮动/题材、全球/海外、市场/行业/个股资金、席位、两融、市场结构与分类。仅既有授权；不读业务池决定数据范围。
- Quote来源钟、接收钟、source/price_basis，状态的data_time/data_date与checked/last_success分开；重复事实不重写，日线核验/修订审计分开，辅助来源版本和发布指针保留更正/回退。
- 行业分钟原始批次的capture/collect移入data模块，新写入market_auxiliary_fact；sector_fund_fact新写仅归业务，旧raw批次只读联合读取，测试验证业务表无新来源记录、旧数据回放与查询零写入。行业分钟与市场资金各自调度，故障隔离回归通过。
- 自选、短线、波段、图表、热图、行业资金/成员计算、席位与海外分析改读已发布数据。原native来源函数迁到data模块，旧业务查询不现场补数。业务资金投影有独立计算任务，无采集请求队列。
- swing_business_state及只读历史view分开原引用表内业务状态；基础表和业务表保留明确写入职责。旧记录不删除，不默认全表回填或历史清理。
- Dashboard首次缺数不POST，刷新只GET；旧POST410，客户端refresh=True在HTTP前拒绝，失败保留投影。新增只读status/quotes契约；legacy live明确stock-query-v2。
- 旧按功能采集CLI明确停用，dry-run只说明，apply退出2，不转发任务。业务scheduler不采集，数据程序独立轮转历史覆盖。typed样本查询及并发索引默认计划，验证索引有效/就绪。
- candidate-v2冻结三运行单元，旧NAS runner拒绝新schema；旧v1保留两服务。首迁停旧采集者，回退校验后精确停/移除新增数据容器，保留数据与旧镜像身份。没有执行NAS安装或发布。
- stock ADR-0003、术语、职责/运行说明、契约、Unreleased、Dashboard界面和消费边界文档均更新。

## 验证

- 股票最终全量：1101 passed / 1可选隔离benchmark跳过 / 73 subtests，73.59秒；包含最终行业原始批次迁移与采集故障隔离；1存量Starlette/AnyIO弃用警告。
- 基础写入角色保护的worker/仓储/日线/科技/题材/全球与边界定向57 passed / 19 subtests；行业原始批次迁移定向52 passed。均与最终全量重叠，不相加。
- Dashboard：后端35 passed（含隔离PG投影）；前端9 passed，vue-tsc/Vite/PWA构建通过；1存量Starlette/httpx警告。
- 治理70项测试通过，包含服务拓扑扩展、旧Manifest兼容、漂移与回退，仅替身/临时文件。
- Config/compile/Compose三个角色与命令/差异检查通过；新market_data完整Ruff及所有改动Python关键错误检查通过；Dashboard修改后端Ruff通过。整仓存量风格问题未扩入范围。

## 测试环境与保留项

只使用本任务标签CHG-20261027-002的PG16 tmpfs容器，首次为92bf5a00...，最后一次行业批次迁移回归使用重建的39184f8b...，本机57308，创建market_data_test/chg_pg_query_011/chg_sectorfund_provider/chg_sectorfund_dashboard隔离测试库。来源均由已有模拟源替身测试，没有生产读写或供应商诊断。Python依赖补充和npm依赖仅写任务临时目录，未修改共享venv或原node_modules。

两次回归结束后均验证精确ID、Change标签和tmpfs属性，并移除对应测试容器；未移除镜像或其他容器。保留所有未提交工作树、证据与复现依赖供审阅；不清理其他容器、分支或用户文件。

实际供应商吞吐/全市场分钟容量、NAS持续运行、并发大表索引、MAJOR版本选择、备份/精确生产身份、安装新版runner与正式发布均未执行；这些属于后续经明确授权的发布门禁。新服务健康表示进程心跳，业务继续核查具体基础覆盖。历史数据清理仍等待单独讨论。
