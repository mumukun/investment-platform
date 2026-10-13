# 市场结构与ETF P0 本地交付报告

Change：CHG-20261013-002。依据用户确认的 FINAL v2.0 PRD。当前为隔离分支的本地实现与验证，未Commit/Push/创建PR/Merge/Tag/部署/启用生产开关；不满足平台“已合入main且READY”的开发完成定义。生产版本 UNKNOWN。

## 1. 功能范围

已实现：独立导航与页面；10个指数适配位置；全A名义平均价格/日收益均值及中位数；互斥涨跌分布；MA20/60资格统计及新高/低；连续合格日等权/中位复合指数；风格5/20/60日收益及相对差；八ETF分组/12只代表ETF的份额、同日单位净值、严格1/5/20日估算申赎、分组加总、期初规模加权强度；逐基金历史与原始来源；流动性20日比较；确定性九状态候选/确认、证据/反证/观察条件、变化摘要与辅助诊断；历史查询及known/rebuilt双视图；缓存与独立开关。

部分覆盖：A500免费指数接口当前失败，指数和相对曲线空值；ETF A500代表基金159338本身已验证。历史沪深股票池成员及历史ST/停牌状态无法完整证明，因此历史为retrospective_partial，正式状态和连续全A复合历史可能证据不足；不将当前目录冒充历史池，不强行生成历史“准确率”。历史均线可展示取得实际日线的资格样本及分母；流动性活跃比不使用不完整历史样本作为全市场分母。

未启用：模型AI（无新增付费/外部模型请求）；P1机构持仓/完整ETF母集合、微盘池/自然语言研究；P2 ETF增量模型C及策略连接。这些不阻塞P0降级交付。

## 2. 仓库、版本与代码状态

| 仓库 | 本地提议版本 | 当前HEAD基线 | 影响 |
| --- | --- | --- | --- |
| stock-analyzer | 3.24.0 | 707d619916e2ad745bded153f1d4cdede7d705c9 | 事实、计算、源适配、研究、调度、新只读契约 |
| investment-research-dashboard | 0.19.0 | ceb1b03d15c18973f3d3c6d9574384e680293d74 | 本地投影/API、索引迁移、Vue页面、构建配置 |
| investment-platform | 无业务版本变化 | 1652fa9262ec856db94b324c8cc25040ca628b24 | Change、证据、新构建开关镜像身份兼容 |

三仓分支：feat/CHG-20261013-002-market-structure-etf。隔离目录 `/Users/mukun/.codex/worktrees/market-structure-etf/`。原checkout及其未提交内容保留。marketNewsFeed排除。逐文件清单见[git-inventory.json](git-inventory.json)及两业务仓库说明。

## 3. 免费源实测及审计

2026-10-13在本地隔离数据库实测。最初探针见 [source-probe.json](source-probe.json)，真实采集见 [initial-collection.json](initial-collection.json)、[current-collection.json](current-collection.json)，原始字段/单位/资金公式复核见 [source-audit.json](source-audit.json)。

- 日历：新浪接口8797条，未来日只作为日历，禁止生成未来观测。股票目录沪深5225家，包含ST；北交所被排除。
- 行情：已有批量缓存优先，缺失由腾讯公开批量行情补齐5225家，源实际报价时刻与本系统生成时刻分别记录。
- 指数：stock_zh_index_daily_em验证9条，初次各185交易日；csi000510失败，保留null，无主基准静默替代。
- SSE份额：原始TOT_VOL万份×10000。SZSE适配器已输出份，不重复换算；超过180自然日分段。
- 净值：AKShare现有13列对上游14列的适配失败；改用东方财富F10按FSRQ/DWJZ命名读取，12只各185条。LJJZ不参与资金公式。
- 映射：12只均以基金档案明确跟踪标的及交易型开放式全称验证，拒绝联接。年度拆分事件注册表已交叉检查，未验证事件或异常跳变不计资金。
- 回填：全目录当前公司历史实际日线，复权与名义价格分开取得，最多3线程及有限超时；失败保留缺口，不构造假数据。

历史补齐已完成：5222只本次抓取成功、3只断点续用、失败0；5225只共964148条股票事实版本，日期2025-12-31至2026-10-13。数量含追加修订，不能等同历史有效证券池完整性。见full-stock-backfill.log及source-audit.json。

## 4. 核心口径与质量

平均股价＝有效股票名义收盘价算术均值；日收益中位数为当日个股收益中位数。等权/中位指数由每天收益连续复合，起点1000；缺口不续接或重启冒充连续历史。MA20/60只用有足够实际调整价格的资格样本；新高/低使用本日与之前20个有效收盘比较。

ETF金额＝(本日份额−上一真实交易日份额)×本日单位净值。金额元、份额为份、净值元/份；比例5.2表示5.2%，相对收益单位pp。1/5/20日必须逐日完整；分组先按交易所/代码去重，再加金额，强度为完整窗口金额总和/同成员窗口期初AUM总和。只代表12只样本，不能识别机构，不能等同成交额或主力资金。

广度覆盖98%为完整，90%至98%为部分，不足90%不判正式状态；MA20资格覆盖和当日/五日前真实池同时达门槛才有广度轴。九状态以000985趋势三项同向和广度五日±5pp划分；默认连续两个完整收盘候选相同确认，盘中暂定。收盘数据未到齐时不能仅因时间已过就确认。ETF T+1只追加辅助资金记录，已确认价格/广度冻结。

规则market-structure-rules-v1.0.0，结构investment-dashboard-market-structure-v1，映射market-structure-etf-mapping-v1，均与应用版本独立。

## 5. 存储、迁移、调度及回退

Provider只新增market_structure_fact/generation及索引，独立schema，本任务未写旧策略评分。事实/快照追加、重复输入幂等，正式来源价格更正保留初值并标待核对；原始审计记录不删。

Dashboard复用Snapshot/SyncState，Alembic b2d4e6f80123只新增模块部分唯一/历史索引，downgrade只删新增索引、保留数据。测试环境upgrade/check及往返验证通过。关闭模块/采集即可回退；生产迁移未执行。

Provider开关MARKET_STRUCTURE_ENABLED/SYNC_ENABLED/HISTORY_BACKFILL_ENABLED默认false，增量调度17:10/20:30/08:10，PG advisory lock阻止重复，历史首次补齐单独显式开启。Dashboard MARKET_STRUCTURE_ENABLED默认false，SYNC_SECONDS默认1800；本地人工验证设0。前端VITE_MARKET_STRUCTURE_ENABLED构建时决定导航，默认false；Docker/候选清单/标签均携带此身份。现有服务需正常Provider地址和Bearer Token；无新业务服务。

本任务两个PostgreSQL容器仅为隔离开发/回归数据库，预览只绑定127.0.0.1，与生产无关联。

## 6. API及页面入口

Provider `/api/integrations/investment-dashboard/market-structure`沿用Bearer鉴权，GET只读缓存。Consumer `/api/v1/market-structure/overview`及indices/breadth/styles/liquidity/regime/history/etf/groups/单基金/data-quality/methodology/ai-analysis，仅读本地投影，沿用全站登录权限。参数as_of、lookback=5/20/60/120、mode=known/rebuilt；ETF窗口1/5/20。未知/无效404/422，空数据200结构化unavailable。失败刷新不清空已持久化快照。

真实响应见[api-response-excerpt.json](api-response-excerpt.json)，鉴权401、有效查询200、无效窗口/未来日期422及首次采集前known为空均通过，见[integration-checks.json](integration-checks.json)。访问入口：`http://127.0.0.1:15179/market-structure`。产品说明和契约文档位于Dashboard docs/product/market-structure-v2.md及docs/technical/market-structure-contract.md。

## 7. 验证

Provider 271项单测通过；Dashboard后端141项通过；前端20文件62项通过，production build通过。新增构建身份兼容22项及NAS标签检查2项通过。全窗口121日与末两日重算结果一致（new_generations=0），人工重复同步新增投影0条，见cross-window-recompute.json/idempotent-projection-sync.log。Provider独立数据库验证覆盖盘中到收盘、最终数据修订隔离、事实/代次幂等、known时间截止；Consumer验证跨时区截止、份额净值同日、家数不变量、版本拒绝、失败保留及本地GET不访问上游。

前端一次高并发回归触发旧视图5秒超时及后续状态干扰；降低为2 worker后62项全部通过，保留 [失败日志](frontend-tests-concurrent-failure.log)。未修改无关业务代码或放宽断言。

缓存接口20次本地测量：概览P95约686ms、历史约633ms、Provider约1001ms（Provider略超1秒目标），见 [performance.json](performance.json)。与全量重算并发时概览P95约1916ms，另保留performance-with-backfill-compute.json；性能目标尚未全部达成。改进计划：历史列表与逐基金原始审计按需读取，减少首屏约5MB完整窗口响应，并根据实际主机容量安排采集/重算。上述不代表生产/冷浏览器/弱网保证；首屏3秒与生产资源观察需实际部署后验证。本地1440×1000桌面及默认窄屏展示、ETF分组/单基金交互通过人工验收；不新增大规模DOM/截图回归。

一次完整121日重算实测306.37秒、峰值常驻内存约1.34GB（compute-performance.log）。任务与旧调度隔离并使用互斥锁，但仍共享主机CPU/内存；生产资源与首屏3秒目标尚未验证，需按实际部署容量观察。

## 8. 历史和研究限制

已生成2026-04-14至2026-10-13共121个交易日（120日展示窗口+前一基准日），原始行情2025-12-31开始用于均线预热。当天5225只有效收益，MA20资格5203/99.58%，MA60资格5173/99.00%；当前源报价11:14:35，ETF份额/净值最新日2026-10-12，计算与报价时间分开。历史成员不能证实的日期为事后部分重建，known历史在首次采集前为空，不能宣称为当时真实信号。首次可得保存本系统实际观察时刻，不将来源未知的发布时间回填成历史日期。

研究报告按时间顺序70/30留出，描述状态持续/转移、未来5/10/20日收益和回撤及1/2/3确认延迟、3/5/7pp敏感性；样本不足不报告胜率、显著性或预测能力。实测历史可用正式状态为0，研究报告状态insufficient_history（见classification-validation.json）；历史池缺口使广度五日轴不能正式确认；这是质量限制，非以虚构分类代替验证。

## 9. P1/P2

后续优先可追溯的历史证券池/停牌/ST事实及完整ETF母集合，再积累真实当时可得状态。机构持仓低频披露、微盘风格和模型C应单独Change验证；本期不连接交易策略或付费源。

## 10. 治理及授权

Change仍IN_PROGRESS（本地实现阶段）；没有业务PR及main合入，不标READY。已记录兼容、依赖顺序Provider→Consumer、回退和验证证据；未做正式Release freeze/gates或Release Manifest，**未完成发布准备且未授权生产部署**。后续若授权提交/PR/合并，按平台治理执行；正式发布单独授权。

页面验收截图：

![桌面预览](/Users/mukun/.codex/worktrees/market-structure-etf/investment-platform/changes/evidence/CHG-20261013-002/desktop-preview.jpg)

## 2026-10-13 用户来源政策修订

此报告前述P0自建指标结果属于初始1.0.0口径；按用户后续确认，当前1.2.0已停用无可靠免费第三方来源的个股池统计与依赖其的状态确认。实际新数据及接口验证见third-party-policy-integration.json，来源可用性见third-party-statistics-probe.json。乐咕已接入；同花顺全A保留10-12真实交易日；830000未就绪，不以自建均值代替。免费需Key来源允许研究，尚无真实Key启用。
