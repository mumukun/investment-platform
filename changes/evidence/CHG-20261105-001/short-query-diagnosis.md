# 短线选股慢查询定位

日期：2026-11-05。状态：只读诊断完成、优化待实施。生产既有版本stock-analyzer6.7.0 / Dashboard2.7.0；源码核对当前发布实现。请求观察日11月5日，候选实际返回11月4日保存结果，保留真实日期。未修改生产代码、配置、数据库或策略，未触发选股/采集/结算写入。

## 实测结果

复用既有production smoke签名会话机制，仅执行GET；凭据仅在进程内，未输出或保存。API回环计时排除SSH、模块导入和浏览器网络/渲染。候选与环境采用2线程并发，复现页面同时发起请求；统计/跟踪串行有界测量，没有对超时统计重新发起请求。

| 真实请求 | 响应完成秒 | 响应字节 | 说明 |
| --- | ---: | ---: | --- |
| short-selection/tail，short-research-v1 | 2.629 | 4,848,431 | 当前研究候选985只 |
| swing-selection/list，v4、page=1/page_size=1 | 25.088 | 31,409,965 | 短线顶部环境实际调用；根items1只，current.items仍632只 |
| short-selection/stats，未指定规则 | 2.627 | 2,480 | 默认旧策略，不代表当前短线统计 |
| short-selection/tracking，未指定规则、limit=20000 | 1.437 | 1,070 | 默认旧策略，不代表当前短线跟踪 |
| short-selection/stats，rules_version=short-observation-v2 | 未在40.096秒内完成 | 未取得 | 本次客户端40秒超时，不代表服务端最终结果或接口一定失败 |
| short-selection/tracking，rules_version=short-observation-v2、limit=20000 | 14.692 | 1,655,689 | 当前模拟买入明细 |

初始并行诊断组26.828秒，包含JSON解析和字段体积计算，不直接等同浏览器首屏耗时。短线JSON解析完成2.768秒，波段环境25.745秒。首次诊断脚本在已保存JSON后打印摘要时遇到同名current_bytes标量/字典冲突；修正本地打印器，不重跑已有测量，原始测量文件完整保存，接口均实际成功。当前规则另测避免把默认旧规则快速空结果冒充当前性能。

## 已证实原因

1. 首屏被无关的大请求阻塞。ShortResearchSelection.vue:load在Promise.allSettled(shortResearch, swingSelection(page_size=1))结束后才赋值snapshot和清除loading。短线本身已经返回，也要等波段；每30秒load再次重复。市场环境本来只需要market/日期/质量，却经波段列表取31.4MB；这是首屏约25秒的直接等待链路，不是每次重新计算短线。
2. 短线候选重复返回。current.items和current.research.items都是985只、各2,383,259字节。current.research约2,429,370字节，整个current约4,848,162字节。research的strength_experiment汇总45,363字节；逐股实验字段合计332,089，features合计53,890，不能把小字段描述为主要瓶颈。候选每页30只实际为浏览器slice，服务器返回全部985只。
3. 实验页共享allCandidates，筛选可计划参与后在浏览器按板块/实验分/代码排序，本身没有独立首次GET；它继承首屏等待和全量下载问题。ShortStrengthExperiment使用v-show，会挂载并计算，但其渲染耗时本轮未测，不能认定CPU占比。
4. 后台current同步通用maintain_current每次完整fetch/model_dump后，save才比较generation；之后sleep5秒再重复。同批次仍消耗上游读取、JSON传输校验及对象构造，候选重复副本加重负担。
5. 模拟跟踪是独立问题。ShortSimulationWorkspace为v-if，仅点击tracking工作区后挂载；默认current_close显式short-observation-v2。ShortEffectTracking并行读取stats和limit=20000明细，await两者结束才显示；明细再在浏览器每页50切片。因此统计超时也会推迟已经可用的明细呈现，不能认定它在研究候选首屏无条件执行。
6. 当前统计/跟踪查询路径：Dashboard同步代理Provider；short_tracking.read选交易、相关日线/原始价格/停牌记录，逐笔calculate，并携带entry_evidence。stats调用无limit的read后做全样本及实验分组汇总；明细请求上限20000使已存在SQL LIMIT近似全量使用。两请求会独立执行读取和结果组装。已确认此重复工作与请求时计算结构；本轮没有cProfile/SQL ANALYZE，不宣称40秒具体由某条SQL或某个Python循环造成，也未测服务端排队/解析/计算的各自占比。
7. 历史尾盘模型另走short_simulation_archive.history，先读全历史正式批次、入场/结算事件、观察报价和日线，再组装并slice；stats再调用history(limit=0)。这是源码确认的潜在重复计算，本轮未对历史退出模型发起性能测量；不混作当前策略实测结果。

## 合并优化建议（未实施）

- 优先拆掉首屏等待：顶部全A环境提供独立几KB摘要接口；与候选独立赋值、loading和错误状态。保留原波段市场环境口径及日期一致性校验，不能用短线市场背景替代。模拟统计/明细也独立显示，某项失败不能阻塞另一项。
- 短线服务端分页：研究候选每页30、实验每页30，资格、筛选计数、分组、板块内排序在同一完整批次轻量投影上计算；不是只过滤当前页。列表保留原评分/观察分/实验分/组别/未评分原因、简要理由、确认日期、现价/结构区域/触发失效/数据时钟。单股完整features、路径证据、实验分解与审计信息点击读取。列表只出现一份当前页候选，接口元数据不夹带全量副本。
- 后台先读批次和状态摘要，仅新候选批次取一次完整证据并生成持久化轻量投影；未变化仍更新进度、降级/过期、时间。不依赖单进程内存，不新增外部缓存服务。显式摘要格式与旧完整接口兼容，既有模拟/历史证据保持。
- 模拟明细真实后端分页，每页50，加确定性顺序与服务端筛选；入场完整证据点击单条再取。保持所有样本全池总数/胜率分母，不让分页改变收益统计，不把研究候选与实验样本混算。
- 模拟统计改为后台只读基础事实并计算业务结果投影，查询读取同一修订的汇总和明细。修订关联规则、截止日、价格/结算数据修订、实验版本；补齐数据后刷新，不只按日期缓存。已有未结算、未入场、缺数、不同退出模型/实验分组语义保持。不以扩大超时或返回部分样本“算成功”。

## 后续验收

同等985候选/30每页，轻量候选响应<=1MB、首次及20次P95目标<=2秒；环境摘要目标<=20KB；模拟明细每页50，汇总/明细目标分别<=2秒，均需NAS实测。首屏在环境延迟/失败时仍能先显示候选，统计延迟时明细可先显示。缓存未命中、多worker、历史日期、过期状态、分组与分页全量一致性，以及零基础写入/零采集/收益规则不变均需直接验证。目标尚未达成，不将诊断完成称为性能修复完成。

源码定位：Dashboard ShortResearchSelection.vue:66-80、ShortStrengthExperiment.vue:6-23、ShortSimulationWorkspace.vue:20-44、ShortEffectTracking.vue:20-51、current_candidates.py:22-75/135-143/293-325；Provider current_candidates.py:166-187、short_tracking.py:152-253/493-562、short_simulation_archive.py:34-134。
