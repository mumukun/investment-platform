# 波段选股本地验证

2026-11-15。规则 `swing-rules-v5.5.0`，代码已按用户授权本地提交，未推送或启用生产。

## 结果

8组显式合成输入、24条独立路径：原可参与路径保留4条，因量价异常或位置/空间不足排除2条，其余18条继续观察或不参与。按股票合并后显示8只、3只可计划参与、5只观察。这些是行为样例，不是实际市场入选率。

同一股票可同时满足多路径；合成重叠样例主导路径为已确认的突破回踩。低位样例的主导路径为低位蓄势。连续放量滞涨样例仍可观察，但不得进入参与计划。未知上方压力保留空值，位置空间部分不得分。

板块0/5/10分的比较已保存 [comparison-summary.json](comparison-summary.json)，本组样例未发生排序翻转；不能据此推断全市场排序稳定。行业退潮样例在现有门禁下不参与，去掉该门禁的离线反事实可通过，提示门禁影响与5分权重不同。本次保留原门禁。

## 已执行

- provider `test_swing_quality.py`、`test_swing_engine_v5.py`、`test_swing_contract_v3.py`、`test_swing_features.py`、`test_swing_explanation_routes.py`、`test_swing_accumulation.py`：162项通过；最后补充复权冻结关键位进入状态机前换算用例后，质量与V5状态机31项复验通过。
- 新规则盘中特征→计算→PostgreSQL持久化→公开契约链路已跑通；版本隔离、观察总分为空、量价序列保留均核对。
- `test_swing_price_confirmation.py`、`test_swing_tracking_receipts.py`、`test_swing_health_rules.py`：通过。首次环境缺少SWING数据库变量导致的跳过已补跑；一个HTTP测试依赖缺失已通过复用本地依赖修复并复验。数据库为本任务新建的 localhost:55485 隔离容器，未使用业务数据库。
- Dashboard契约4项通过；provider生成的合成JSON通过前端契约校验。紧凑列表保留摘要、固定快照详情保留原始量价证据。
- 前端4个受影响测试文件62项通过；最终组件/列表修改后2个文件50项复验通过。
- TypeScript+Vite构建通过；Python compileall、check_config、针对新增文件及Dashboard后端修改的Ruff通过；diff空白检查通过。
- 浏览器查看了桌面列表、个股决策详情、结构分项与40/35/20/5分解；390px移动端卡片显示区间与阻断原因，未出现横向内容溢出。浏览器临时尺寸已复原。

## 未执行与边界

没有完整真实历史观察/确认时点与后续可成交价格数据集，本次没有收益回测、胜率估计或最优参数结论。确认条件冗余与按路径退出优劣尚待真实时间点研究；已有 `research-replay` 的 fixed5/structure/volatility 及成本/可成交性能力可复用，本次不改历史账本。

完整生产契约/生产浏览器验收未执行；本地预览拦截服务请求，只有合成数据。新分项需要匹配的消费者，默认生产规则保持原值。

## 本地交付

- 页面：http://127.0.0.1:5215/swing-selection
- Dashboard：`/private/tmp/CHG-20261115-001/investment-research-dashboard`，`npm run demo:swing-quality`。
- Provider：`/private/tmp/CHG-20261115-001/stock-analyzer`，`python scripts/preview_swing_quality.py --synthetic --output /tmp/swing-quality-preview.json`。
- 原工作区、短线、超跌反弹和marketNewsFeed均未修改。三个隔离仓库保留在 `feat/CHG-20261115-001-swing-quality`；已本地提交，未推送、合并、构建容器镜像或发布。

最终桌面截图：`/private/tmp/CHG-20261115-001/swing-quality-detail.jpg`。本地前端服务保留供用户预览；本任务临时数据库测试结束后停止，未触及其他容器。

列表多路径追加：SwingPathSummary及SwingSelectionView共49项定向测试通过，TypeScript/Vite构建通过，桌面与390×844卡片验证通过。提交编号见Change记录，提交阶段未重复运行已通过且仍适用的检查。
