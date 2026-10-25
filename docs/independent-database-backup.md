# 独立数据库备份与恢复验证

CHG-20261025-005。工具完成不等于生产已启用：当前未安装NAS计划任务，未改变保留策略、archive_mode、代理、权限或生产容器。

`scripts/database_backup.py`通过已有本地Docker容器中的PostgreSQL工具运行。配置是name/container/database/user四字段数组，不含密码、连接串或Webhook；真实名称由部署时核对，不从旧记录推测。

```json
[{"name":"research-news","container":"reviewed-postgres-container","database":"reviewed_news_database","user":"reviewed_backup_role"}]
```

```sh
# 默认只检查连接，不创建备份
python3 scripts/database_backup.py --config reviewed-backups.json
# 明确授权后执行；目标必须是现有非符号链接目录
python3 scripts/database_backup.py --config reviewed-backups.json --destination /reviewed/backup-root --apply
python3 scripts/database_backup.py --verify /reviewed/backup-root/backup-ID
# 可选恢复验证：只使用已有本地不可变镜像，绝不拉取镜像
python3 scripts/database_backup.py --restore-check /reviewed/backup-root/backup-ID --image sha256:EXACT_LOCAL_IMAGE_ID
```

备份目录0700、文件0600，先写partial，再经pg_restore --list检查后更名。所有目标完成才生成archive_readable清单，记录字节数和SHA256；部分失败保留未完成目录，不冒充完整备份。校验通过仅证明文件完整，restore_verified仍false。

恢复检查始终新建无网络、无主机挂载、无端口、无自动重启的临时容器；逐库创建临时数据库并pg_restore --exit-on-error，重新校验源文件，清理由本次创建返回的精确容器ID。成功单独写restore收据，不改写原清单。它证明数据库能恢复，不等于应用版本兼容或业务验收。

建议生产定时任务在另行授权后调用相同工具，并将成功时间、清单路径、失败通知接入现有运维方式。市场新闻库应独立列入备份配置；RPO/RTO、保留周期、异机副本位置需按真实磁盘容量和可接受恢复窗口确定。工具不自动删除任何旧备份，也不代替异机副本。

本次只用新建的隔离测试数据库验证导出和无网络恢复。生产数据库、真实备份覆盖、独立存储故障恢复仍待实际验收。
