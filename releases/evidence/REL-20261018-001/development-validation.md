# CHG-20261018-001

生产确认：v4.2.0 / bb70dbaf / image config12df64cb，stats-v3 HTTP500为UnboundLocalError；不是缺少源数据或鉴权错误。原release的真实跨仓probe保留，不能用通用smoke PASS覆盖它。

修复从v4.2.0 Tag建立hotfix分支；只移动函数导入、版本4.2.1及回归测试，无DDL/契约/策略更改。hotfix PR19。

本地：386项unittest（5项既有环境跳过）；32项专项包含独立PostgreSQL空账本、完整五日样本、stats/history计数与收益一致性；23项pytest；compileall、diff检查。Dashboard0.26.0没有代码变更，稳定回滚后重促成原精确镜像；marketNewsFeed没有代码或部署变更。

补充默认CI也必跑的空账本接口行为回归（不依赖数据库fixture环境），确保初始化异常不会被数据库环境跳过掩盖。最终专项33项；全量387项（加一项默认CI回归）。
