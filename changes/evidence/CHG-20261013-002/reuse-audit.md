# P0现状复用与缺口审计

开发基线成功fetch：平台1652fa9、Provider707d619（3.23.1）、Dashboardceb1b03（0.18.1）。当前checkout落后，独立工作区从这些origin/main建立。未读取生产凭据或验证生产，Production=UNKNOWN。

| 能力 | 复用 | 缺口/兼容措施 |
|---|---|---|
|全A行情|hotmap_data批量采集、a_share_snapshot|抓到的集合不能当理论应有池；独立按日目录/质量；北交所排除|
|日线/均线|已有a_share_daily_close、swing_daily_bar及AKShare|swing采集有预筛，不能全A；新增自有全A事实；前复权历史标事后重建|
|交易日|AKShare新浪交易日历已有使用|持久化真实日历，所有窗口按交易日，查询不联网|
|短线状态|现有market-regime|保持原枚举与评分；新market_structure_regime命名空间与版本|
|ETF|现有ETF二级报价|新增官方清算份额、同日单位净值、具名跟踪标的映射；不采用主力资金流字段|
|存储|Provider自己的local_db、Dashboard Snapshot与SyncState|新增Provider增量表；复用Dashboard表并追加索引，独立库/API消费|
|页面|Vue3/ECharts/ElementPlus、现有导航日期认证|新路由，独立模块开关；金额CNY元，前端亿元，收益差pp|
|模型|现有DeepSeek收费资源|本期不调用；确定性解读完整提供|
|历史验证|已有规则单测与时间序列研究约束|历史有效证券池/退市样本缺口必须公开；不输出预测概率|

与PRD差异：AKShare1.18.64沪市接口已把原万份转换成份；新增直接官方适配器保留原值与倍率。候选净值接口ValueError（14字段返回/13固定列名）；按具名FSRQ/DWJZ取值避免累计净值错配。页面卡片按10.3；研究报告与P2高级研究界面分开。没有新增服务、新闻调用、跨库读取或真实费用。
