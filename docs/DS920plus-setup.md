# DS920plus 一次性配置

对应 CHG-20261010-001。生产仍使用原入口；以下安装不启动应用、不创建正式 Tag、不重启 Docker。
完整模型及门禁见 [image-release.md](image-release.md)。

## 1. 先恢复 GitHub 操作权限

在开发电脑的终端运行，按网页提示完成登录：

```sh
gh auth login --hostname github.com --git-protocol ssh --web
gh auth status
```

使用可以访问 mumukun 三个仓库及 Actions 的账号（两个业务仓为 private，治理仓为 public）。已有 Git SSH key 可跳过上传；不在聊天中提供
Token。登录后由 Codex 创建 PR、检查 CI、按精确 PR head 合并并检查 main 候选。
Dashboard 两个 candidate repository variables 必须为字符串 `true`，与当前生产一致。

## 2. NAS 管理员安装

管理员需要在 NAS 交互终端输入自己的 sudo 密码；当前免密授权只覆盖旧 nas-deploy，不能用于安装
新入口。安装包只含治理脚本、配置与说明；对应提交和 SHA256 一同提供。先核对摘要，再解压审查。

在开发电脑连接 NAS：

```sh
ssh -i ~/.ssh/id_ed25519_synology_stock_analyzer -p 9352 freemumu@100.86.90.115
```

在 NAS 上执行（新建目录，不覆盖已有安装包或旧入口）：

```sh
sudo -i
mkdir -m 700 /root/CHG-20261010-001-image-release
tar -xzf /volume1/homes/freemumu/CHG-20261010-001-image-release.tar.gz -C /root/CHG-20261010-001-image-release
cd /root/CHG-20261010-001-image-release
```

审查 `deploy/nas-config.DS920plus.json`、`scripts/` 和安装器。已只读确认的配置是：

| 项目 | 实际值 |
| --- | --- |
| 部署账号 | freemumu |
| 数据库容器 | shared-postgres / PostgreSQL 16 |
| stock 数据库 | stock_analyzer（备份整个数据库，含 stock_analyzer schema） |
| Dashboard 数据库 | investment_dashboard |
| stock API 容器 | stock-api |
| Dashboard API / Web 容器 | investment-research-dashboard-nas-api-1 / investment-research-dashboard-nas-web-1 |

确认后安装及检查权限：

```sh
chown root:root deploy/nas-config.DS920plus.json
chmod 600 deploy/nas-config.DS920plus.json
bash deploy/install-nas-image-release.sh deploy/nas-config.DS920plus.json
if command -v visudo >/dev/null 2>&1; then
  visudo -cf deploy/sudoers.DS920plus
else
  echo "未发现 visudo，先人工审查固定 sudoers 文件"
  cat deploy/sudoers.DS920plus
fi
test ! -e /etc/sudoers.d/investment-platform-image-release && install -o root -m 440 deploy/sudoers.DS920plus /etc/sudoers.d/investment-platform-image-release
if command -v visudo >/dev/null 2>&1; then visudo -c; fi
sudo -l -U freemumu
```

新 sudoers 文件必须不存在才能使用上述 install；如已有同名文件，保留并检查已有规则，不覆盖。
root 模块、wrapper 和配置不能给予 freemumu 写权限。sudo 只允许五个固定模式，不允许任意 shell。
本机已确认常用目录没有 visudo；不要假设 `/usr/sbin/visudo` 存在。检查 sudo 列表中的五个固定
模式与审查文件一致，再从 freemumu 会话检查 `sudo -n -l`。sudo 规则加载验证与全局 visudo
语法检查分别记录，缺失工具时不能宣称后者通过。

在 root 会话中执行只读检查：

```sh
/usr/bin/python3 /usr/local/lib/investment-platform/nas_checks.py health stock-analyzer
/usr/bin/python3 /usr/local/lib/investment-platform/nas_checks.py version stock-analyzer
/usr/bin/python3 /usr/local/lib/investment-platform/nas_checks.py health investment-research-dashboard
/usr/bin/python3 /usr/local/lib/investment-platform/nas_checks.py version investment-research-dashboard
```

上述程序已在 NAS Python 3.8.15 中以不落盘方式运行通过；安装后的 root 权限仍需验收。
stock smoke 检查真实数据库 watchlist、Bearer 鉴权和版本契约，明确不刷新行情；Dashboard smoke
复用已有生产只读检查。它们不代替每次功能发布所需的真实数据、迁移和跨仓门禁。

## 3. 私有镜像只读登录

候选包首次创建后由 Codex 检查 GHCR visibility 必须是 private。NAS 管理员使用只读包权限完成
root Docker 登录，因为实际拉取由 root 发布器执行：

```sh
/usr/local/bin/docker login ghcr.io -u mumukun
```

在交互提示中输入 GitHub 支持的 read:packages 凭据；不要放入命令行、文件、聊天或提交。权限需覆盖
三个镜像包，root Docker 配置需保持受保护。登录不等于已验证拉取，之后用精确 candidate digest 实测。

## 4. Docker daemon 代理（单独维护窗口）

已确认 mihomo-1 使用 host 网络，HTTP 端口 7890，代理连接 GHCR 可达；Docker daemon 尚未配置代理。
ContainerManager 的现有配置位于 `/var/packages/ContainerManager/etc/dockerd.json`，普通账号无法读取。

管理员先备份配置并记录所有运行容器。真实启动参数使用
`/var/packages/ContainerManager/etc/dockerd.json`，实际路径为
`/volume1/@appconf/ContainerManager/dockerd.json`。2026-10-10 管理员合并 proxies 且
dockerd --validate 通过，但套件重启后 Docker info 代理仍为空。启动脚本会先运行
`updater postinst updatedockerdconf`，不能把直接修改此文件当作已生效的代理方案。

本机经实际重启验证生效的方案是独立服务 drop-in；不要覆盖套件原始 service 或同名文件：

```sh
(
set -e
umask 022
set -C
cat > /etc/systemd/system/pkg-ContainerManager-dockerd.service.d/90-investment-platform-mihomo.conf <<'EOF'
[Service]
Environment="HTTP_PROXY=http://127.0.0.1:7890"
Environment="HTTPS_PROXY=http://127.0.0.1:7890"
Environment="NO_PROXY=localhost,127.0.0.1,::1"
EOF
/usr/syno/bin/synosystemctl daemon-reload
)
```

本机已存在 root-owned 服务 drop-in 目录，且原服务没有代理参数；其他机器需先检查这些条件及
既有 no-proxy 规则，不直接复制。本机 mihomo 为 host 网络、restart=unless-stopped。
经授权维护窗口在 DSM 套件中心停止并启动 ContainerManager，会短暂中断容器服务。重启后
确认原运行容器全部恢复、mihomo 就绪、业务健康及版本、Docker info 中两个代理指向
`http://127.0.0.1:7890`，再测精确镜像 pull。没有重启授权时停在配置审查前。
无需更改业务容器现有 HTTP_PROXY；daemon 代理生效不等于私有镜像拉取或吞吐验收通过。

本次 JSON 配置及原运行容器名单备份在 `/root/docker-proxy-backup-q4wtqxb_`；如需回退，管理员
先审查并备份当前配置，只移除本次独立 drop-in、恢复已核对的配置，再 reload 和按维护流程重启。
备份目前用于本次维护，长期保留需另存到受保护持久目录。

## 5. 接下来由 Codex 验收

备份 `pg_restore --list` 通过后，管理员审查并运行
`scripts/verify_nas_restore.py <protected-backup-directory>`，执行实际隔离恢复。
工具固定使用已核对的 PostgreSQL 镜像 ID，创建无网络、无发布端口、无生产挂载的临时容器；
仅向自己的完整容器 ID 执行 createdb/pg_restore。成功后清理临时容器及匿名卷，在备份目录写入
0600 的 restore receipt（含备份摘要、镜像 ID 和应用表数量，不含实际数据）。它不调用生产
数据库，也不能替代新发布器或应用回滚验收。只有 root-owned 700 目录内的非空 600 备份被接受。
本机共享目录继承 Synology ACL：即使 mkdtemp/umask077，实测备份目录和文件仍为777，
且继承多个账号权限。不要仅根据创建命令推断备份保护成功。先用 synoacltool -get 和 stat
检查，在管理员核对三个对象都为本 Change 创建且 root-owned、非符号链接后，移除仅这三个
对象的继承 ACL 并设置 POSIX 权限。不得对整个共享目录或其他备份做递归操作：

```sh
(
set -e
backup_dir=/volume1/docker/CHG-20261010-001-backup-re4h3fb7
/usr/syno/bin/synoacltool -del "$backup_dir"
chmod 700 "$backup_dir"
for backup_path in "$backup_dir/stock_analyzer.dump" "$backup_dir/investment_dashboard.dump"; do
  /usr/syno/bin/synoacltool -del "$backup_path"
  chmod 600 "$backup_path"
done
stat -c '%n mode=%a owner=%U' "$backup_dir" "$backup_dir/stock_analyzer.dump" "$backup_dir/investment_dashboard.dump"
)
```

如任一步报错，停止；不得绕过恢复工具的权限检查。发布器的 state_root 也位于共享目录，
首次验收需实际核对 root-only 权限；未验证前不能进入生产部署。现有文件不以 umask 代替权限证据。
脚本或清理失败均不得视作通过；如果容器创建本身失败，检查本次唯一名称的残留资源，不做模糊清理。

完成登录和安装后告知 Codex，无需发送任何密码：

1. 检查 PR CI、main CI、候选 run/artifact 与私有包权限；冻结 SemVer 后生成新 SHA 的候选。
2. 核对生产 baseline、feature flags，检查新 sudo 入口和同一 digest 在线/离线传输。
3. 验证 protected backup 可读性、目标环境及回滚，保存计时与 receipt。
4. 全部门禁通过后整理正式 Release；收到本 Change 的正式发布授权才创建 Tag 和切换生产。

目前版本尚未 freeze；未修改应用 VERSION，也未复用生产已有 Tag。此改造完成合并不代表已正式发布。
