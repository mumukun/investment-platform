# CHG-20261021-011 本地验证

实施跨2026-10-21/22（Asia/Shanghai），Change ID保留开始日期。

## 代码与边界

- Provider `6f9465dd584f3326af244aab9526311d53a47342`：固定分钟调度、失败最多重试一次、缓存规避参数、完全一致的前后来源时钟、请求完成时效、完整流入/流出/净额指纹和只读连续性诊断。
- Consumer `e213921c3761b5f5ed6f05377f66259d9b069ab7`：可选v2诊断校验，默认5分钟实际取点与分钟明细切换、稀疏坐标tooltip按实际分钟查金额、长缺口/午休断开、隔离疑点和原始值可查。
- `investment-dashboard-capital-flow-sina-v2`只加可选samplingRulesVersion/sampleWarnings。金额、日期、原始series不变；规则标识不是契约兼容门槛。旧响应/归档没有扩展时继续接受。
- basis=net-values为历史弱证据，只提示；basis=full-batch为新完整金额指纹，趋势暂留空、明细保留。连续未变化不误判。均不证明缓存过期或真实资金事件，不以阈值删除大跳变。
- 无DDL、后台历史回填、上游写回、生产配置更改、重启、Tag或部署。只读SQL导出21日已存公开行业快照用于离线fixture，没有触发生产API或行情同步。后续验证均本地/离线，无外部行情API调用。

## 已执行

| 验证 | 结果 |
| --- | --- |
| Provider受影响pytest：test_sina_intraday/test_sector_fund_sina/test_capital_flow | 47通过，含显式隔离本地PG；见provider-tests.log |
| 独立PG持久化/同分钟幂等/失败不覆盖/观察时点过滤 | 通过；127.0.0.1:54329/chg_sectorfund_provider，测试随机schema由自身finally删除，无生产凭证或数据库 |
| Consumer契约与来源政策pytest | 30通过；旧契约、非法诊断/分钟/依据/数值等拒绝，见consumer-tests.log |
| Ruff format/check（受影响Backend） | 通过 |
| Provider compileall（受影响模块/测试） | 通过 |
| 前端4文件Vitest | 17通过；实际坐标/金额、零值/缺口、模式切换、旧净额不删、新完整批次留空、稀疏索引tooltip与选择；见frontend-tests.log |
| vue-tsc + Vite/PWA生产构建 | 通过；见build.log |
| 实际Provider→Consumer离线契约 | replay.py生成真实代码响应，再cross-contract.py解码校验；91条诊断、12条原始series完整保留 |
| git diff --check与提交范围 | 三仓通过，无无关内容、凭证或临时预览源码 |

测试有既有Starlette/httpx弃用提示，生产构建有既有大chunk提示，未作为失败。未运行未受影响的全仓Backend、Provider或全站回归，未做真实下一交易时段采样验收。

## 真实存档重放

observed-20261021.json为191个已存的48行业公开净额批次；SHA256见replay-report.json。09:31—15:00的交易分钟轴241点，缺50点；计入采样开始前09:30则全天242分钟缺51点。

旧数据没有完整流入/流出指纹，因此51次非相邻整批重现、连同其连续重复后继分钟共91个net-values提示，都不自动剔除。初次实验若全部隐藏会更碎，最终明确区分弱证据和完整指纹，避免用可疑推断修改历史。

5分钟趋势每条从191个实际样本取53个实际点（不含null间隔），减少约72%的绘图点；geometry-report.json逐点断言金额等于原分钟金额，未计算均值、重标时间或补值。保留3分钟及以上长缺口，午休不跨接。原始大台阶仍存在，不宣称已修正原始金额。

重放命令（从此治理worktree执行；Python使用已具依赖的3.13环境）：

```sh
python changes/evidence/CHG-20261021-011/replay.py
node --experimental-strip-types changes/evidence/CHG-20261021-011/replay-geometry.mjs
# 从同级Dashboard工作目录执行
PYTHONPATH=backend python ../investment-platform/changes/evidence/CHG-20261021-011/cross-contract.py
```

## 浏览器

真实Vue/ECharts离线重放，行业图使用公开真实存档；外层市场指标为明确占位、无上游请求，未验收其他资金模块。1440×1000前后同数据截图：before-replay.png、after-five-minute-replay.png；minute-detail-replay.png保留原始分钟路径。390×844下整页scrollWidth=viewport=390，图表720px在322px容器内横向滚动，模式切换有效。原始明细能恢复同一组值，不按美观隐藏数据。

初始临时预览桩用template导致本地运行时编译警告；改为render桩后干净启动并切换模式，warn/error均0。生产组件均为正常SFC，不包含预览桩。临时预览源码已删除，服务停止、浏览器页关闭、临时视口恢复。截图证明本地显示，不代表已部署。

## 限制与发布

缓存规避参数和完全一致的来源时钟不能证明两个独立HTTP接口原子绑定；具体来源缓存机制仍未知。新浪官方页面JS确实用ssi_get_extend(id=2)显示更新时间，但没有在本轮调用行情API验证新请求参数。需要正式发布后在真实交易时段看漏采和完整指纹重现是否减少；未授权新来源或东财兜底。

仅本地Commit，未Push/PR/Merge/Tag/部署。Provider计划4.5.4、Dashboard计划0.30.1；与矩阵CHG010同为待发布补丁，正式整合时协调最终版本，不能分别复用已发布Tag。Change保持REVIEW，不标READY。
