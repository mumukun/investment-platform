# CHG-20261018-012 验证

## 范围

基于marketNewsFeed main 1a4d0a7，下架Base队列生产者、消费者、重试、近期标记和保留任务。移除约900行不再调用的相关代码；公共OpenAPI函数、报告、飞书IM、历史Base维护脚本及映射读写仍保留。没有DROP/TRUNCATE/DELETE迁移，既有队列表原样保留。三个生产入口和简报不再构造或写入队列；新库不创建队列表。

## 测试

- PostgreSQL 16.14，临时Docker容器codex-retire-feishu-chg012-db，仅127.0.0.1随机端口，数据库market_news_test；每个PG测试使用独立随机schema，完成后清理。
- 配置全部合成，禁用dotenv自动加载，不读取用户/生产凭据；旧FEISHU_SYNC_ENABLED和RETENTION_ENABLED设true，已下架的cron故意设为非法字符串。
- 配置检查：scripts/check_config.py，config check ok；不再依赖下架cron。
- unittest discover -s tests -p 'test_*.py'：98 tests，20.841秒，OK。包括数据库账本、三个采集入口、CTEE、鉴权及research契约、X/飞书多通道状态等既有回归。
- 新增4项专项：新库无队列表仍持久化事件/信号/发送状态；初始化及事实写入不改变旧队列归档；旧启用开关不注册Base任务；报告OpenAPI保留鉴权、请求体和时间格式行为。
- compileall -q src scripts tests、git diff --check通过。
- 首轮测试配置生成器遗漏了required_range的默认SECONDS参数，导致两个测试类无法导入；补齐纯测试配置后完整重跑通过，未因此改变业务配置。

## 限制与状态

未实发消息、调用真实LLM或访问飞书生产API；未修改NAS环境、生产数据或重启服务。现有约155MiB队列表不会因代码下架立即释放空间。代码与Change暂留隔离工作树，未提交/推送/合并/发布。生产应用仍运行此前版本，停止入队需要后续正式发布后生效；历史数据删除另行预览和授权。
