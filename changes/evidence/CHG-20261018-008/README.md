# 标准指数参照扩展证据

2026-10-18本地实现与公开只读来源核验；不代表生产接入或NAS验收。

- `source-probe.json`：国证目录元数据、15条指数的报价/日线/成员首页和空尾页原始响应，以及三个精确同码腾讯报价字段。各请求URL和观测时间随数据保存。
- `source-validation.json`：15条的解析结果、成员数量、日线条数和报价源时间。688条成员关系去重为477只证券；创新药精选保留57条证券，含港股，不截断到50。
- `verification.json`：本次必要测试、构建、边界验证与未执行项。

官方目录入口：[国证指数目录](https://www.cnindex.com.cn/index/indexList?channelCode=-1&rows=3000&pageNum=1)。逐条详情可在[国证创新药精选980086](https://www.cnindex.com.cn/module/index-detail.html?act_menu=1&indexCode=980086)同一路径替换indexCode查看。成员、日K、报价接口完整URL保存在原始响应中。

399279、399418、399363的国证当前报价端为空，实测确认腾讯同码名称/代码/原始百分比/源时间。前两条日线仍来自国证，399363实际链路沿用腾讯日线。来源的15时更新时间按原值保留，不描述为港股16时收盘。

Provider的`tests/fixtures/tech_board_expansion_sources.json`保存公开原始捕获。Consumer的`backend/tests/fixtures/tech_board_expanded_envelope.json`由实际Provider解析并写入独立本地PostgreSQL后导出，含完整成员与原始指数数据；未采集的成员价格明确为空。Consumer投影/API测试使用隔离本地PostgreSQL，页面链路测试替换API传输和图表/详情入口组件，不声称实时HTTP端到端或截图验收。

两业务仓库版本仅作待发布准备。用户要求先本地提交，暂不发布，后续合并需求统一发布；本次没有Push、PR、Merge、Tag、生产或NAS写入。
