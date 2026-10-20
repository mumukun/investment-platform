# NAS 外网下载代理默认

Change: CHG-20261016-005。用户明确要求 NAS 默认使用已有 mihomo，并使后续对话知晓。

## 国内股票数据直连（2026-10-20）

CHG-20261020-002记录用户补充要求：获取国内股票相关数据直接连接来源，不走HTTP/HTTPS/SOCKS代理，失败也不自动切换代理。此要求覆盖相关模块既有代理例外；不得仅因全局下载配置使用mihomo就让股票请求继承环境代理。腾讯、新浪等适配器及AKShare底层请求都需要按实际调用链落实并验证。

GitHub、GHCR、包管理器与同类外网依赖下载继续使用下述NAS代理默认。内网API、数据库及SSH保持原有边界。实现股票请求直连时只约束相关请求，不全局清空环境代理或更改Docker daemon、mihomo节点、凭据与规则。本记录不构成生产配置修改、重启或发布授权，也不声称当前所有股票采集入口已完成直连整改。

## 外网依赖下载

DS920plus 的 mihomo-1 使用 host 网络、restart=unless-stopped，HTTP/mixed 端口7890。2026-10-16实际核对 Docker `HttpProxy` 与 `HttpsProxy` 均为 `http://127.0.0.1:7890`，NoProxy已配置。既有 root-owned drop-in为 `/etc/systemd/system/pkg-ContainerManager-dockerd.service.d/90-investment-platform-mihomo.conf`。本轮未修改daemon或重启ContainerManager。

NAS用户默认shell配置为 `$HOME/.config/investment-platform/proxy.sh`，由 `.profile` 加载；修改前已保存原profile备份。该文件设置HTTP_PROXY/HTTPS_PROXY及小写变量，保留已有NO_PROXY，默认本地回环地址直连。仅影响该用户shell，不批量覆盖业务容器配置。非交互SSH一般不读.profile，外网下载命令须显式加载：

```sh
. "$HOME/.config/investment-platform/proxy.sh"
curl --max-time 20 https://ghcr.io/v2/
```

`401`是匿名仓库入口可达的正常响应，不能证明私有包授权；EOF只表示连接提前结束，不能单独断言是代理、GitHub或DNS故障。代理可达不保证每次大镜像下载成功。NAS部署用户与受限root发布器各自的Docker登录状态也不同，不复制root登录配置或输出Token。

Docker代理检查使用平台已有脚本，默认只检查mihomo，不额外请求直连：

```sh
python3 scripts/check_docker_proxy.py
# 仅在明确需要直连对照时
python3 scripts/check_docker_proxy.py --compare-direct
```

读取Docker JSON必须使用HttpProxy/HttpsProxy/NoProxy原始大小写；缺失则UNKNOWN，不输出“未走代理”。本轮初次人工查询误用了HTTPProxy/HTTPSProxy，已更正，保留在Release修正记录，不沿用错误结论。新增测试防止同类误判。

后续类似GitHub/GHCR、包管理器与依赖HTTP下载默认使用本代理。内网API、数据库、本地缓存读取保持直连；SSH协议不自动使用HTTP_PROXY，继续既有SSH配置。不要全局改mihomo规则、节点、代理认证、业务来源口径或私有仓库权限来掩盖失败。

镜像网络失败时优先保留原冻结计划，使用同一CI digest/config ID的受支持归档/缓存路径；既有发布器仍校验版本、SHA、平台、标签、备份与smoke，不能用latest、重建镜像或虚构RepoDigests。2026-10-16的恢复证据见REL-20261016-002。若缓存已丢失且受保护归档路径不可写，记录真实权限阻塞，不放宽sudo或以容器挂载绕过权限。

需要改变daemon代理时按 [DS920plus安装说明](DS920plus-setup.md#4-docker-daemon-代理单独维护窗口) 的已核实systemd方案，保留原配置，安排实际维护权限；直接改套件dockerd.json会被套件启动脚本重写。已有正确配置无需重启。
