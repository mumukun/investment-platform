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
/usr/sbin/visudo -cf deploy/sudoers.DS920plus
test ! -e /etc/sudoers.d/investment-platform-image-release && install -o root -m 440 deploy/sudoers.DS920plus /etc/sudoers.d/investment-platform-image-release
/usr/sbin/visudo -c
```

新 sudoers 文件必须不存在才能使用上述 install；如已有同名文件，保留并检查已有规则，不覆盖。
root 模块、wrapper 和配置不能给予 freemumu 写权限。sudo 只允许五个固定模式，不允许任意 shell。

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

管理员先备份、审查现有 JSON 和服务启动参数，再将 `deploy/docker-proxy.example.json` 的 proxies
设置合并进现有 JSON，保留其他配置和原有 no-proxy 规则；不要整文件覆盖。应用配置和通过 DSM
套件中心重启 ContainerManager 需要另行确认维护窗口。重启前记录所有运行容器，重启后核对全部恢复、
mihomo 已就绪、Docker info 中 daemon HTTP/HTTPS proxy 生效，再测精确镜像 pull。没有重启授权时
停在配置审查前。无需更改业务容器现有 HTTP_PROXY。

## 5. 接下来由 Codex 验收

完成登录和安装后告知 Codex，无需发送任何密码：

1. 检查 PR CI、main CI、候选 run/artifact 与私有包权限；冻结 SemVer 后生成新 SHA 的候选。
2. 核对生产 baseline、feature flags，检查新 sudo 入口和同一 digest 在线/离线传输。
3. 验证 protected backup 可读性、目标环境及回滚，保存计时与 receipt。
4. 全部门禁通过后整理正式 Release；收到本 Change 的正式发布授权才创建 Tag 和切换生产。

目前版本尚未 freeze；未修改应用 VERSION，也未复用生产已有 Tag。此改造完成合并不代表已正式发布。
