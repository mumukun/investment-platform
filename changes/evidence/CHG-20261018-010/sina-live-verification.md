# 新浪实取验证（2026-10-18）

证据类型：公开新浪实取 + 两侧本地HTTP + 各自隔离PostgreSQL + 实际Vue组件。无fetch拦截或行情值替身；不是生产部署。此前verification.md的MOCK记录仅为前轮历史，不能作为此次真实来源成功依据。

## 来源与口径

官方资金页 https://vip.stock.finance.sina.com.cn/moneyflow/，官方前端脚本 https://n.sinaimg.cn/finance/cnstock/pc/zjlx.z.js?ver=1.1 。JSON方法使用该页quotes_service的MoneyFlow服务，未传凭据。

- ssl_bkzj_bk核验48个行业身份；行业日资金ssl_bkzj_zjlrqs按bankuai=new_…读取opendate/avg_price/r0_net/r0_ratio。资金元换亿元，均价为元，r0_ratio乘100为百分数。48/48截至2026-10-16，完整行业指标48。
- ssc_bkzj_ssggzj计数，ssl_bkzj_ssggzj每页80按symbol完整分页并复核数量；ssl_qsfx_zjlrqs逐股读取带日日期的主力/总净额与未复权收盘价。90日行业历史、11日个股交易窗口均参照同源上证日历。原始002511、造纸名单样例随此目录保存。
- 行业成员源记录2829，排除236，可展示2593（唯一股票2589，行业有交叉）。2457条具完整3/5/10日资金，136条缺失保留原因，13行业全字段healthy、35行业partial。不能据“48项可查”宣称全部股票完整或当前分类完全准确。
- 原生活用纸等细分类不再冒充独立新浪分类；当前统一48个原生行业，板块与个股同代码。造纸行业源24条、展示22条，两条退市记录排除。新浪旧归属可能含业务已变更股票，界面有明确限制。
- ssx_bkzj_fszs分钟实测不用于生产逻辑：new_zzhy在14:58/14:59/15:00均价分别3.0281/8.8245/5.1462，同日行业日均价5.0176；未能核验一致性和主力金额，不据此绘图。见sina-minute-not-used.json。全市场新浪参考独立可用。

## 本地集成与页面

专属测试容器codex-sector-members-chg010-db，Provider schema chg010_sina_live；Provider与Consumer使用各自测试库，未访问生产或NAS。曾为旧实现日期门禁在旧sector_fund_run留过明确LOCAL目标日标记，**本次完整新浪验证使用sina_research真实行业日资金扫描，不依赖该标记，也未把它当真实行情**。

48个行业均经Dashboard HTTP读取summary、同代码detail及members，核对截止日2026-10-16、原生身份、日曲线与名单；Provider读取、客户端校验、Consumer Snapshot持久化、Consumer路由均实际执行。新浪全市场契约与其历史归档查询通过；nativeMemberRefreshStatus=202，现有真实缓存复用。行业/成员摘要及原始capture SHA见sina-source-and-http.json。

实际App、CapitalFlowView、行业折线图及个股组件挂载到明确本地验收入口，代理真实Consumer API；造纸5日下钻、22条名单、前5排行、002511搜索通过（+0.06亿、-4.40%、当日0.60亿，数据日2026-10-16）。1280桌面及390/320窄屏完成：文档宽等于视口，320的可见抽屉约307px、内部滚动宽307px，股票宽表内部滚动，排行/筛选纵向排列。视口恢复。

- sina-board-desktop.png：行业均价、MA20、日主力图。
- sina-members-desktop.png：真实排行与002511行。
- sina-members-mobile-390.png、sina-members-mobile-320.png：窄屏布局。

## 检查结果

Provider受影响pytest 56 PASS（成员分页/数值/交易日/队列/失败保留/行业历史/来源隔离/只读归档），check_config及compileall通过。Consumer受影响pytest 71 PASS（新来源校验、拒绝旧契约、来源隔离、归档/故障、市场契约及后台投影），Ruff通过；测试框架有1条Starlette/httpx弃用提示。Vitest完整191 PASS/38文件，Vue类型/Vite构建通过。git diff --check通过。

无新服务、依赖或DDL；未运行生产验收/真实AI/生产写入，未触发CI/推送/PR/合并/Tag/部署。行业分钟资金仍不可用，新规则未经预测效力校准；本记录不作行情授权或收益保证判断。
