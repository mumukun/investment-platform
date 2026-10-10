# 一次构建、同一镜像发布

Change: CHG-20261010-001。新增能力在 GitHub/NAS 实机验收前为 `NEEDS_TARGET_VERIFICATION`；既有
`./deploy.sh <tag>` 和历史 Release 不变。marketNewsFeed 不在此次范围。

## 1. 候选构建

业务仓库 `CI` 只在 PR 和 main push 运行；候选 workflow 只接受本仓 main push 的成功 CI，不接受
PR/fork 产物，不由正式 Tag 触发。Dashboard API/Web matrix 并行构建，stock-analyzer 独立构建。
GitHub-hosted linux/amd64 runner 使用 BuildKit 和持久 cache，私有 GHCR 通过 workflow 的
GITHUB_TOKEN 写入。包必须保持 private，首次实际创建后核验访问权限。

唯一候选标签包含 SHA、run_id、run_attempt；发布身份始终使用 digest。发布后拉取该 digest 做隔离
smoke，成功才上传 `candidate-<SHA>/candidate.json`。CI 健康/迁移使用 fixture，不能冒充真实
AKShare、跨仓 HTTP、目标生产数据或页面验收。候选 scope 固定为 isolated-fixture。
候选同时记录 Docker config Image ID；在线路径验证 registry digest，离线路径验证同一 config ID。

Dashboard repository variables：`CANDIDATE_PRO_KLINE_ENABLED` 与
`CANDIDATE_LIMIT_UP_LADDER_ENABLED`，字符串 true/false，缺省 false。当前生产功能必须显式保持，
不能因缺省值关闭；部署器比较 NAS Compose 中冻结的参数，差异 fail closed。参数变化需新候选构建。
两组件合并时必须来自同一 workflow run、SHA、版本与参数。

## 2. 准备发布

使用 RELEASE_MANIFEST.yaml 管理正式治理记录，并在同一 Release 保存 image-release-v1 JSON
执行计划（deploy/image-release.example.json 是不可执行的 DRAFT 模板）。执行计划至少包含：

- `release_id/environment/status`，status 为 READY_FOR_FORMAL_RELEASE；
- 按 release_order 排序的 repositories；每项包含原样 candidate.json、精确 tag、dependencies；
- expected_production 的 tag/commit_sha、每个 Compose service 的完整 image_ids，以及 Dashboard build_time；
- rollback 的 tag/commit_sha/version，以及每组件 digest 或已保留的本地 Image ID，必须匹配 baseline；
- scope、compatibility、integration、real_data、configuration、rollback 的 PASS 与可核对证据；
- authorization 在准备阶段为 NOT_AUTHORIZED；正式发布时改为 FORMAL 并记录用户明确授权证据。

不得将 fixture smoke 直接填入 real_data/integration。没有正式授权不生成正式 Tag、不启动生产、不
迁移、不启用功能。版本更新优先纳入业务 PR；Release 收集期间如有并行 Change 仍须重新核对 SemVer。

仅 `preflight` / `prefetch` 可以接收 `NEEDS_TARGET_VERIFICATION` 计划：scope、compatibility
仍须 PASS 并有证据，四项目标门禁必须显式为 PASS、NOT_RUN 或 PENDING；失败或缺失仍拒绝。
精确候选、生产基线、回滚镜像、顺序和传输验证保持不变，本地 prefetch 先核对真实 GitHub 候选证据。
这些模式不启动业务容器、不迁移数据库。deploy / verify / rollback 仍要求全部门禁 PASS 与
READY_FOR_FORMAL_RELEASE；deploy / rollback 另要求正式发布授权。预取 receipt 不代表发布通过。

本地 `python3 scripts/image_release.py check <plan.json>` 验证结构；
`python3 scripts/image_release.py verify-ci <plan.json>` 使用 gh 查询成功 CI 和候选 run，并下载候选
artifact 与计划逐字段比较。合并后的 SHA 与 PR SHA 不同时，合并结果必须有自己的有效证据。
本地控制器依赖 Python 3、Docker CLI、已授权读取本项目 Actions artifact 的 GitHub CLI `gh`。

正式 Tag 创建在正式授权后，指向候选冻结 SHA；禁止 Tag workflow 重建。所有计划/候选/备份和
receipt 引用需落入正式 Manifest，并按治理要求提交后才成为共享事实。

## 3. NAS 一次性安装

现有受限 nas-deploy 保留。新命令 `/usr/local/sbin/nas-image-release` 只提供 preflight、prefetch、
deploy、verify、rollback；stdin 接收不含凭据的执行计划。应用目录固定，不接受任意命令、目录或
Compose 文件。共享执行器为治理代码，不包含复制的业务源码。

管理员从 deploy/nas-config.example.json 生成 root-owned、不可由其他用户写入的配置。填入真实的：

DS920plus 的已核对配置见 `deploy/nas-config.DS920plus.json`，安装步骤见
[DS920plus-setup.md](DS920plus-setup.md)。其他设备不能直接套用容器名与数据库名。

- 数据库 custom-format pg_dump 命令；输出只写 protected backup 文件；
- pg_restore -l 可读性校验命令（单独参数 `{backup}` 替换为备份路径）；
- 快速 health 命令、只输出应用版本的 version 命令；
- 对应生产 smoke 命令，包含鉴权、迁移与受影响的真实数据链路，不调用付费模型、不发送通知。

以上数组来自管理员维护的可信配置，永不从用户计划取命令。备份命令不得在参数里携带密码；使用
数据库容器已有本地授权或受保护的 pgpass。verify 可用固定管理员脚本将备份通过 stdin 送给
数据库容器内 pg_restore，不能输出实际数据或连接密钥。示例为空时安装与发布均拒绝，不猜测生产
数据库/container/user/schema。

执行 `sudo bash deploy/install-nas-image-release.sh <reviewed-root-config.json>`。此安装不修改
旧入口、不改 sudoers、不改 Docker 代理、不重启服务。管理员另外用 visudo 为部署用户授予以下
精确命令，不授予泛化 sudo/python/shell：

```
/usr/local/sbin/nas-image-release preflight
/usr/local/sbin/nas-image-release prefetch
/usr/local/sbin/nas-image-release deploy
/usr/local/sbin/nas-image-release verify
/usr/local/sbin/nas-image-release rollback
```

配置、三个 Python 模块与 wrapper 都保持 root-owned；state_root root-owned mode 700。NAS 登录私有
GHCR 使用只读包权限，凭据仅存在受保护的 Docker 配置；CI 不持有 NAS SSH/数据库密钥。
目标需 Python >=3.8、flock 和 Docker Compose V2；实际支持 `--no-build --pull never` 需实机检查。
DS920plus 已确认 Python 3.8.15、Docker 24.0.2、Compose 2.20.1；受限 wrapper 固定 PATH 与
`/usr/bin/python3`，覆盖非交互 SSH 默认 PATH 不含 `/usr/local/bin/docker` 的情况。目标 Python
模块导入与隔离 candidate 校验已通过，完整部署/备份/回滚仍需实机验收。

## 4. mihomo 与传输验收

镜像拉取由 Docker daemon 执行，应用容器 PROXY_URL 不证明 daemon 代理有效。
只读检查：`python3 scripts/check_docker_proxy.py --proxy <实际HTTP/mixed代理地址>`，报告 Docker
版本、daemon 代理是否配置、GHCR 直连/代理连接耗时。401 表示 registry 可达；这不证明私有包权限
或镜像下载吞吐。吞吐以实际 pinned image pull 阶段时间记录。

deploy/docker-proxy.example.json 只是 Docker Engine >=23 支持的配置片段；群晖旧版本需匹配实际
服务启动环境。不得覆盖现有 daemon 配置，不自动套用普通 Linux systemctl；管理员合并设置并在
明确维护窗口应用，核对原容器全部恢复。真实端口和 mihomo 规则依现场检查，不能假定 7890 有效。

备用：电脑拉取候选记录中的同一 digest，执行
`python3 scripts/image_release.py export-bundle <plan.json> --bundle-dir <new-directory>`。
该命令先验证 GitHub artifact、registry digest 与 CI config ID，按 Image ID 执行 docker save，
生成 tar 与 transport.json（归档 hash、固定 NAS 路径）。通过 SSH/Tailscale 传输到记录的路径，
将 transport.json 内容作为执行计划的 transport 字段。NAS 校验归档 hash 后 load，并再次校验
CI config ID、标签和平台；Compose 用完整 config ID 启动，不伪造 load 后可能丢失的 RepoDigests。
两种传输都使用同一 CI 产物、不重建；目标环境的在线与离线路径仍需分别实测。

## 5. 执行与恢复

### NAS 隔离候选与保留镜像验收

`scripts/verify_nas_candidates.py` 是 CHG-20261010-001 的固定管理员验收工具，不加入 sudoers。
复用 `verify_nas_restore.py` 的 root-only 备份保护、隔离 PostgreSQL 创建与清理。必须在审查后的
同一 scripts 目录运行；参数仅为已审查备份目录。所有镜像固定为已验证候选 digest 或旧生产 Image ID，
`--pull never`，不挂载宿主目录、不发布端口，应用共享临时 network=none 数据库的 loopback。
仅使用测试凭据，不复制生产 .env，不启动 stock 调度器；Dashboard 不配置上游 projection 地址。

工具在克隆数据库上运行候选迁移/API smoke、跨容器 stock watchlist HTTP/鉴权契约和静态 Web 服务，
随后启动旧镜像验证候选迁移后的读取兼容性，不自动 downgrade。失败清理自己的全部应用容器，
再由恢复工具清理自己的数据库与匿名卷；失败不生成成功 receipt。数据库原始错误与业务响应不输出。
成功将 candidate_acceptance 写入受保护 restore receipt。此证据不代表生产配置、外部数据刷新、
浏览器 E2E、新受限发布器 rollback/resume 或整个 Release 通过。

这次为检查真实备份上的应用兼容性，需要再次恢复到临时数据库；常规发布仍使用 fresh readable backup，
不把完整恢复演练强加到每次发布。预计恢复耗时与已完成的数据库恢复演练相近，应后台运行并保存日志。

先由部署用户安全 fetch 精确 Tag 和 origin/main；执行器只读校验已有 Tag/SHA/lineage，不以 root
执行用户仓库的 fetch/hooks。统一本地入口：

```
python3 scripts/image_release.py preflight <plan.json> --host <user@nas> --key <key-path>
python3 scripts/image_release.py prefetch <plan.json> --host <user@nas> --key <key-path> --receipt <prefetch-receipt.json>
python3 scripts/image_release.py deploy <plan.json> --host <user@nas> --key <key-path> --receipt <deployment-receipt.json>
python3 scripts/image_release.py verify <plan.json> --host <user@nas> --key <key-path> --receipt <verification-receipt.json>
```

本地 deploy 再次验证 GitHub 证据；NAS deploy 要求 FORMAL 授权证据。preflight 只读，prefetch 只下载
不启动；正式部署全程持有 NAS 共享 flock。多仓按计划顺序部署，上游 smoke 不通过不会继续下游。
每仓依次 pull/检查镜像 → 核对 baseline → custom backup/readability → 精确 checkout →
Compose `up -d --no-build --pull never` → 运行身份、health/version 和管理员 smoke。候选镜像可能
仍被 GHCR 保留但 smoke 未通过；仅成功 candidate artifact 可以进入计划。

阶段状态和时间写入 root-only journal，并返回不含凭据的 receipt。正式切换开始后备份不得重建覆盖；
断网重试先核对当前 image IDs 与此计划的 baseline/target，第三方 drift 停止。已经启动目标镜像时
仅重新核对备份与验收，不再次 restart。部分启动失败只允许本计划的旧/新/缺失容器状态恢复。
同一 Release ID 的候选与门禁不可变；重新授权或切换已验证的传输方式不改变 freeze hash。
修改候选或门禁须重新准备 Release。失败返回部分 receipt，控制器即使非零退出也会保存它；
连接中断时以 NAS 受保护 journal 为准。已验收的本地镜像重复执行跳过 pull/load。

`rollback` 反向恢复已由本计划开始部署的仓库，使用保留镜像和原 Tag，不重建、不自动数据库 downgrade。
回滚后本 Release 禁止继续 deploy。线上旧源码入口不参与新锁，过渡期间必须统一由治理入口串行
执行，不能同时手工运行 legacy deploy；彻底切换时再封闭旧入口。

## 6. 验收与共享记录

运行 `python3 -m unittest discover -s tests -v`，各业务仓执行自己的 CI 标准检查。对 linux/amd64
候选做真实 Docker smoke，不把 mock 发布单测冒充 NAS E2E。镜像 ID/标签、GHCR 私有拉取、受限
sudo、配置、readable backup 和回滚都需目标环境验收，未通过不得宣称新入口可生产使用。

有用户授权后才 Commit/Push/PR/Merge，当前改造不自动正式发布。Manifest 与 receipt 可通过一次
准备记录和一次收尾记录持久化，失败/部分发布也要及时保存；不要求每个健康探测创建独立 PR。
衡量候选准备和正式部署分别的耗时，收集 pull/backup/start/verify 各阶段，比较同等发布范围的结果。
