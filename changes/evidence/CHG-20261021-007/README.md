# CHG-20261021-007 验证证据

所有界面截图来自本地合成响应，不代表生产行情。真实MarketStructureView、Element Plus及ECharts渲染；无生产/厂商请求。

- [主视图与默认折叠历史](market-observation-preview.png)：样本收益与中证2000独立曲线，最近有效日为10月20日；10月21日缺失留空。历史摘要显示800005、BK1158各自有效日期10月16日。
- [键盘展开历史](historical-indices-preview.png)：Enter展开原生details，原800005元/股与BK1158指数点分别绘制，历史缺口保留；Enter收起。控制台error为空。
- [430px赚钱效应](market-observation-mobile.png)：指标按两列排布，文字换行，无页面横向溢出。仅本次区域的窄屏检查，非全站手机验收。
- [受影响Vitest](vitest.log)：3文件25项通过，包含3项新增视图测试与1项参考选择测试。
- [构建](build.log)：vue-tsc及Vite生产构建通过。

测试覆盖：真实零、无有效样本、历史参考日期、同日相对收益、未来数据边界、overview与days合并、原身份独立、折叠时不创建历史图表、展开/收起不增加API读取。没有后端或数据库变化，未运行后端/迁移测试；未进行生产部署或压测。

临时预览HTML/TS、端口5180服务和浏览器标签均已清理。依赖复用CHG005已安装的node_modules，仅创建本工作树临时符号链接，验证后移除；未新增依赖。
