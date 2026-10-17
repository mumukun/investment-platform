# CHG-20261018-000 开发证据

- Provider PR17：https://github.com/mumukun/stock-analyzer/pull/17；分支88130a68ddf8f86b0eb06efb3a358e67a853a180。
- Consumer PR24：https://github.com/mumukun/investment-research-dashboard/pull/24；分支359912676b103280a6839d9d8b0bc733bf86e35a。
- Provider：unittest383项（5项既有外部环境测试跳过）；专项pytest23项；check_config、compileall、diff --check。新账本/质量/幂等/历史/行业聚合/非交易日及可重复DDL在本任务独立PostgreSQL容器验证，未使用生产凭据。维护脚本 --dry-run 正确报告缺数且不发布。
- Consumer：后端pytest213项；前端Vitest178项；Ruff格式/检查、Alembic upgrade/check、默认及三个既有专业功能开关全部true构建通过。测试覆盖缺数暂停、逐日收益、字段保留、健康和旧版归档不覆盖。
- 真实免费源（本机只读）：沪主板1702、科创618、深市2906、北交所351，共5577；Sina真实交易日历到2026-12-31。000001日线2026-03-02至10-16共154根，金额及OHLC合法。Eastmoney停复牌记录验证包含未来公告、复牌日、连续停牌、截止日边界；只按明确全天区间认定，不用未来计划假定已停牌。
- 上述fixture/本地证据不冒充生产补齐或发布成功。正式发布必须冻结合并main CI及同一候选镜像，再由既有发布器完成基线、备份、切换与smoke；上线后只验证本次改变的边界和数据维护结果。
- 三条形态引擎只改变RULES_VERSION；阈值与权重未改。行业历史取完整日期成员、北交所目录名称属于输入修复。

发布前Provider补充PR18：释放已完成Future、显式spawn隔离DB/V8进程状态、对已返回但仍有缺口的批次使用既有前复权备用源重试。新规则数据门槛不放宽。补充测试后384项，最终数据库边界回归保留独立测试记录。四个指数真实历史均154根，末日2026-10-16；不使用旧9/9指数冒充当日输入。

最终补充：独立PostgreSQL跑完30项收盘账本/数据门槛专项，全部通过；Provider全量384项。看板合并main9b243f3通过CI39064009106及候选39064215427，api/web三项既有构建开关均true。Provider最终已冻结PR18合并main bb70dbaf，对应CI39064893822与候选39064929691通过；旧6a83241候选不用于发布。
