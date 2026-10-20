# 东方财富依赖盘点与逐步下线

核查日期：2026-10-15。Change：CHG-20261015-001。

## 当前使用约束（2026-10-20）

用户明确要求：因东方财富经常不可用，使用前必须取得其针对具体用途的明确同意。未经同意不得作为默认源、自动备用源、补数源或诊断探测来源；AKShare封装中的东方财富接口同样受限，不能用工具库名称掩盖真实提供方。旧清单、既有代码和历史例外不是新增或继续调用的授权。

本规则随CHG-20261020-002保存；国内股票请求另须直连。波段生产调查已确认4.4.2的批量日线仍有新浪→东方财富遗留备用，尚未完成业务代码整改；不因记录本条就声称生产已停用。后续修复应移除未经同意的自动回退，缺失明确显示，不伪造数据或删除历史。本轮不部署或重启。下文保留2026-10-15的历史盘点及当时迁移计划，不覆盖本条最新授权约束，也不代表当前生产状态。

## 核查范围与状态

业务代码主基线为stock-analyzer `99915d2b0b8d8b09cdefe07b9d8693cb967ff338`。
NAS实际APP_VERSION=3.24.2、stock-api Image ID=c924e65b…，与上一正式发布记录一致。
生产QUOTE_PROVIDER=tencent、QUOTE_USE_PROXY=false，但该配置不控制其他模块自行调用的东方财富接口。
HOTMAP_CACHE_REFRESH_ENABLED=true，刷新间隔5分钟；SECTOR_EVENT_ENABLED、SWING_ENGINE_ENABLED、市场结构开关均为true。
市场结构全股票历史回填开关未设置，默认关闭；FEISHU_EXPORT_ENABLED未设置，默认false。

CHG-20261014-002的市场结构腾讯→新浪日线替换仍是独立工作树中的未发布草稿，不把它算作生产已下线。
本次只盘点全部依赖并实施证券搜索第一批替换，不删除旧事实、不批量关闭功能、不运行生产回填。

## 实际依赖清单

| 数据/功能 | 入口和底层接口 | 调用位置与触发 | 目前状态 | 替代判断/顺序 |
| --- | --- | --- | --- | --- |
| 股票搜索 | add_stock.search_stocks → searchapi.eastmoney.com/api/suggest/get | 添加股票、Dashboard股票搜索API | 生产仍默认东财搜索，与QUOTE_PROVIDER无关 | 第一批：腾讯smartbox → 新浪suggest → AKShare交易所证券目录；本地代码与NAS只读验证通过，未发布 |
| 个股报价（可选） | sync.fetch_eastmoney_quote → push2.eastmoney.com/api/qt/stock/get；load_akshare_quotes → stock_zh_a_spot_em | sync、watch、add_stock、api中显式eastmoney/akshare分支 | 生产默认腾讯，这些兼容分支不是当前首选 | 后续检查旧配置使用者再下线；不能把配置可选分支说成当前所有报价仍走东财 |
| 全A快照 | hotmap_data.fetch_a_share_snapshot → stock_zh_a_spot_em；失败才stock_zh_a_spot（新浪） | hotmap_cache每5分钟、热图、短线/波段依赖的共享快照 | 高优先级且仍默认东财 | 第二批优先改造；先补齐腾讯/Sina字段与完整性检查，再停止东财，不能只翻转调用顺序 |
| 普通个股历史/热图历史 | sync_daily_stock.fetch_stock_history → stock_zh_a_hist；失败才stock_zh_a_hist_tx | 每日归档函数、hotmap_data历史预热共用；脚本通知/飞书与函数复用不是同一开关 | 东财首选、腾讯备用 | 已有腾讯OHLCV路径；缺成交额/换手率，需保留null并检查依赖。与swing_daily_data的新浪复权历史路径区分 |
| 概念成分/证券分类 | security_classification.fetch_concept_memberships → stock_board_concept_name_em、stock_board_concept_cons_em；新浪stock_sector_spot/detail备用 | 每日refresh_security_classifications、启动补采、自选列表分类事实 | 东财首选、新浪备用；有完整度和最后健康快照保护 | 第二批可复用新浪适配器，但概念名/代码和分类体系随厂商变化，保留来源与历史，不假装同一个板块 |
| 行业历史备用 | sync_daily_sector.fetch_sw_industry_history → index_hist_sw（申万官方）→ stock_board_industry_hist_em | 申万行业日报/板块日线入口 | 东财只是官方申万失败后的备用 | 保留申万官方优先；新浪/腾讯行业标签不自动等于申万指数，先确认映射和成交额单位 |
| 概念板块历史 | sync_daily_sector.fetch_concepts_history → stock_board_concept_name_em、stock_board_concept_hist_em；同花顺备用 | 可选板块日报/历史同步 | 东财首选、同花顺备用，尚非腾讯→新浪 | 需要准确的板块标识及历史序列；目前不能拿另一厂商近似概念静默续接原历史 |
| 公司概况/行业三级 | add_stock.fetch_industry → emweb.securities.eastmoney.com/PC_HSF10/CompanySurvey/PageAjax | add_stock、enrich、hotmap缺失行业补全、API company-profile、Dashboard公司摘要 | 默认东财F10；申万行业全量映射另走官方来源 | 分开迁移公司资料和行业分类；报价API不能补公司简介，其他厂商行业分类也不是同一套三级分类 |
| 涨停池与封板细节 | hotmap_data.apply_limit_pool_from_em → stock_zt_pool_em | hotmap_cache、hotmap；封板时间、炸板次数、封单额、连板等持久化与梯队功能 | 仍会调用；失败后的涨跌幅阈值估算不是这些原始细节的等价数据 | 第三批核对准确涨停池来源；不得用单次价格或自己估算冒充第三方封板事实 |
| 龙虎榜席位目录/交易 | seat_flow._directory/fetch_trades → stock_lhb_hyyyb_em、stock_lhb_yyb_detail_em | Dashboard营业部搜索、席位交易/题材注意力、席位追踪 | 仍默认东财，按请求及缓存触发 | 第三批核对新浪等公开龙虎榜字段；需席位标识映射、分页、买卖金额与日期一致，不能只改SOURCE标签 |
| 主力资金流/板块资金/分时确认 | capital_flow._eastmoney_json → push2delay.eastmoney.com；clist/get、ulist.np/get、fflow/kline/get、stock/kline/get | Dashboard资金流API；板块榜、指数/个股资金流与价格确认 | 独立东财来源且显式直连，不受QUOTE_PROVIDER控制 | 第三批：价格子能力可评估腾讯/Sina；超大/大单与主力净额统计需要验证定义，不能把别家的资金指标重命名成原口径 |
| 市场结构指数/ETF价格 | market_structure_sync.collect → stock_zh_index_daily_em、fund_etf_hist_em | 市场结构08:10/17:10/20:30采集（当前生产） | 生产尚用东财；故障修复草稿已改常规腾讯→新浪 | CHG-20261014-002：9个指数+12只ETF腾讯真实日线验证通过，Sina备用代表品种通过；未上线，不能算已退役 |
| 平均股价 | market_structure_sources.fetch_average_price → push2his.eastmoney.com/api/qt/stock/kline/get，secid=47.800005 | 市场结构原始日K、平均股价卡片与K线图 | 保留的特殊东财来源；访问故障尚未恢复，历史仍在库 | 腾讯/Sina公开检索暂未取得对应有效序列；不计算股票池均价、不混接其他平均股价厂商历史 |
| ETF单位净值 | market_structure_sources.fetch_nav → api.fund.eastmoney.com/f10/lsjz | ETF份额差×同日单位净值估算 | 仍用东财，不能把日K故障扩大解释为净值源全部故障 | 第三批需具名单位净值与净值日；市场价、IOPV、累计净值都不能直接替代单位净值 |
| ETF跟踪标的/类型/份额拆分 | fetch_mapping → fundf10.eastmoney.com/jbgk_*.html；fetch_adjustments → fund.eastmoney.com/Data/funddataIndex_Interface.aspx | 基金映射校验、剔除联接基金、拆分/合并检查 | 仍用东财档案及拆分记录 | 第三批核对腾讯/Sina或基金管理人官方档案；未经验证不能默认“无拆分”或从名字猜跟踪标的 |
| 市场结构全股票旧回填 | market_structure_sources.fetch_stock_history → stock_zh_a_hist(qfq/未复权)；scripts/market_structure_stock_backfill.py | 仅显式历史回填开关+手工参数路径；普通collector已禁止股票池自建统计 | 当前生产默认关闭，但代码仍存在，未删除 | 后续退役该旧入口/函数前确认不再有调用者；保留已有历史审计，不误报为当前每日采集 |

## 三个重要的等价性检查

1. installed AKShare的新浪stock_zh_a_spot最终选择的列没有换手率、PE/PB；源中虽有per/turnoverratio等信息，当前适配器丢弃了它们。直接改为首选会缺字段，且不同PE定义未经验证不能直接套用pe_ttm名称。
2. 目前腾讯普通历史备用只产生价格、成交量及若干价格变化值；没有原东财路径的成交额、换手率。源码把腾讯列amount解释为成交量（手），不能按列名当成交额。installed stock_zh_a_hist_tx默认adjust为空，当前路径也是未复权；波段策略另有明确qfq路径，迁移时仍需显式固定口径。
3. 申万行业、概念板块、龙虎榜席位及主力资金流的标识/定义不由“供应商名称相同”保证等价。替代时必须保留厂商、证券/板块标识、日期、单位和质量；缺失不能填零，旧快照不能改成新来源或当天。

## 仓库边界和误命中

- 这些行情接口的业务采集集中在stock-analyzer。Dashboard通过其Bearer API消费资金流、龙虎榜、公司资料与市场结构；自身源码里的平均股价身份、来源标签、新闻URL不等于直接调用东财行情。
- marketNewsFeed源码未发现直接调用上述股票数据接口；其stock-analyzer股票查询依赖和新闻文章域名不是此类行情接口。本批次不修改/发布News或Dashboard。
- us_market_runtime中的300059“东方财富”是证券名称，schema.py中的东财概念候选是名称映射，local_db.py中的来源默认值是存储标签；不能把这些文本算成额外网络调用。
- AKShare是工具库，不是独立数据厂商；调用stock_zh_a_hist、*_em等仍是东方财富。stock_info_a_code_name当前实现是交易所证券目录组合，不是另一个东财行情回退。

## 第一批已经实施的改动（未发布）

证券搜索改成腾讯smartbox → 新浪suggest → 交易所证券目录，网页接口直连、8秒超时；只解析安全的字符串，不执行JavaScript。
保留美股Yahoo路径和原A股返回字段，校验证券代码/交易所，过滤指数、境外/B股及重复项；修复官方目录备用仅按名称匹配、不能按代码查找的问题。
本批仍保持原搜索入口的A股股票范围，不把腾讯ETF检索有结果误报成添加股票全链路已经支持ETF。

验证：7项单测、compileall/diff通过；NAS进程内新腾讯/Sina适配器查询600519均返回正确名称和SH交易所。测试未写生产代码、环境、数据库或真实自选池。
Source retirement为渐进工作：第一批只退出股票搜索的searchapi域名，不能宣称东财整个平台已下线。

## 后续批次

第二批优先覆盖高频全A快照、普通历史及概念分类：验证字段齐全、样本完整度、时刻/交易日、复权、失效后最后健康记录，针对性测试通过后逐个停用东财调用。
第三批处理涨停池、资金流、龙虎榜、公司档案和ETF元数据；为各能力寻找有相同字段/定义的原始第三方数据，尚未验证的来源不承诺可替代。
平均股价继续作为独立例外查证。未找到可靠替代的能力先记录待迁移；是否停止某项完整功能需要明确处理其展示/降级行为，不能因行情日K失败而顺带移除全部基金或资金功能。
