# 一次构建、同一镜像发布

Change: CHG-20261010-001；日常流程精简：CHG-20261011-003。镜像发布入口已在
REL-20261011-002 完成 GitHub/NAS 实机正式验收。marketNewsFeed 既有源码入口不在此次改造范围。

版本更新并入功能 PR，必要验证随开发完成。提交后只核对本次 diff 与成功 main CI/候选，
不再另开版本/READY/准备治理 PR、全量重审或填写重复证明文件。正式授权后调用一次 deploy；
receipt 已有的运行身份、备份和检查结果直接引用。归档/清理放在上线后，普通功能随部署直接生效。

NAS外网下载默认遵循 [mihomo代理指引](nas-outbound-proxy.md)，后续对话同样适用；Docker实际字段为HttpProxy/HttpsProxy，缺失不解释成直连。

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

## 日常使用（2026-10-11 起）

以 `RELEASE_RULES.md` 的精简流程为准：本地受影响验证 → 合并 main/自动 CI 候选 → 正式授权打 Tag →
一次 deploy → 集中记录。下面的安装、传输与隔离工具章节是能力说明，不是每次发版的待办清单。
已验证的 NAS 安装/配置无需重装；默认只用 registry，网络失败时才使用 archive。

默认不运行全库恢复、旧镜像兼容、发布器中断/回滚演练，也不重复 preflight/prefetch/verify。
数据库、契约、部署或恢复机制变化时，优先本地针对性测试，不自动追加演练。
旧工具仅用于用户明确要求或已说明且无法通过针对性检查排除的数据安全问题。
从用户要求提交/合并/准备发版开始计时，提交、合并、CI构建等待及助手准备均计入；
准备完成与正式授权后上线分别报告耗时，日常处理以约五分钟为目标，不能只计部署；
日常预检只核对已有证据一次，目标30–60秒，不再做整轮发布前验收。
REL-20261011-002 的NAS切换实测约211秒，包含两库约104秒备份；此值不代表完整发布耗时。

```sh
python3 scripts/image_release.py deploy <plan.json> --host <deploy-user@nas> --key <key-path> --receipt <deployment-receipt.json>
```

这个 deploy 已包含 CI/镜像/基线检查、按风险执行或跳过备份、切换、版本/健康与生产 smoke，不再另跑 verify。
正式 Tag/main 仍先由部署用户精确 fetch；不使用浮动 main/latest、不在 NAS 重建。
执行计划 gates 可引用已经验证且边界未变的证据，明确“复用、未重跑”；不把审核通过冒充新测试。
结果/失败 receipt 和 Manifest 集中收尾，不为每个阶段开 PR；分支清理不阻塞切换。

## 2. 准备发布

使用 RELEASE_MANIFEST.yaml 管理正式治理记录，并在同一 Release 保存 image-release-v1 JSON
执行计划（deploy/image-release.example.json 是不可执行的 DRAFT 模板）。执行计划至少包含：

- `release_id/environment/status`，status 为 READY_FOR_FORMAL_RELEASE；
- 按 release_order 排序的 repositories；每项包含原样 candidate.json、精确 tag、dependencies；
- expected_production 的 tag/commit_sha、每个 Compose service 的完整 image_ids，以及 Dashboard build_time；
- rollback 的 tag/commit_sha/version，以及每组件 digest 或已保留的本地 Image ID，必须匹配 baseline；
- scope、compatibility、integration、real_data、configuration、rollback 的 PASS 与可核对证据；
- authorization 在准备阶段为 NOT_AUTHORIZED；正式发布时改为 FORMAL 并记录用户明确授权证据。

### 发布前数据库备份决策

新计划在每个仓库条目内显式记录 `database_backup`；镜像与 SOURCE_TAG_BUILD 共用校验。
普通无数据影响发布采用以下形式（证据和理由必须替换为实际审查结果）：

```json
{
  "mode": "skip",
  "data_impact": "none",
  "rollback_compatible": true,
  "reason": "已核对迁移、启动、后台任务与重算，无覆盖或删除已有数据，旧代码可兼容运行",
  "evidence": "changes/本次Change.md及受影响测试"
}
```

`data_impact` 为 `none/additive/destructive/unknown`。只有 `none/additive` 且
`rollback_compatible=true` 可用 `skip`。回执为 `backup.status=SKIPPED`，无dump路径、哈希或虚构可读性；
镜像发布阶段也标记 `SKIPPED`。续跑核对同一冻结决策，允许兼容代码回退，无需dump。
`rollback_compatible=false` 的显式计划拒绝自动代码回退，不代表可自动恢复数据库。

有数据风险且范围明确时用 `mode=tables`，增加非空 `tables`，例如
`["stock_analyzer.swing_setup_snapshot", "stock_analyzer.swing_state_event"]`。
只接受精确的小写 schema.table 名，不接受通配符、重复项或命令片段；`unknown` 不能按表备份。
Change应说明关联对象、序列与恢复顺序，按表备份不保证能独立重建整个数据库。
范围不明或跨表复杂时用 `mode=full`；实际备份保留路径、大小、SHA256和可读性校验，失败在切换前停止。
旧冻结计划缺少该字段仍全库备份，历史记录不修改。

按表执行需要管理员配置额外的 `table_backup_command` 数组，唯一的独立参数 `{tables}` 展开成
`--strict-names` 和各项 `--table=schema.table`。命令来自受保护配置，不从发布计划接收；模板见
`deploy/nas-config.DS920plus.json`，shell入口通过 `"$@"` 传参，不拼接表名到shell代码。
缺少该配置拒绝按表发布，不能静默改成全库或跳过。原全库命令与校验命令仍保留。

这是发布器升级，需要经授权更新NAS安装代码；按表模式另需合并管理员实际配置中的新命令，
保留原有仓库与私密设置，不能用示例整份覆盖。旧NAS发布器忽略新字段仍全库导出，不能声称已生效。
部署前从核对过的旧安装保留机制回退文件，沿用既有安装入口，不重启业务/数据库、不改sudoers。
独立日常备份、增量链与WAL归档另行落地；当前未确认的定时备份不得视作已有保护。

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
receipt 引用需落入正式 Manifest，集中在收尾提交后成为共享事实，不要求逐阶段提交。

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
执行用户仓库的 fetch/hooks。以下是可用模式说明；日常只执行上面的 deploy，其他模式用于排障或已触发的专项检查：

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

### 固定隔离发布器验收

`scripts/verify_nas_runner.py` 是 CHG-20261010-001 的一次性目标验收工具。管理员从已审查的
root-only bundle 无参数运行；工具使用 root 临时目录和唯一 Compose 项目名，固定候选及保留
镜像，容器 network=none、无端口/宿主挂载/生产凭据，只执行 sleep 与版本读取。
它调用真实 Deployer 的备份文件检查、Compose 切换、镜像身份检查、journal 写入、续跑和回滚。
在 Compose 切换后注入控制器异常，重新加载 journal，检查完整/部分容器续跑和原备份保留；
最后恢复旧镜像、拒绝已回滚 Release 重用，清理自己的容器并核对生产身份/启动时间未变。
archive 分支注入一次缓存未命中，实际检查 SHA256 并执行 docker load，不删除现有镜像缓存。
因此结果只能证明已有层条件下的离线加载和隔离生命周期，不能证明冷缓存恢复耗时。

Git、备份内容和健康/smoke 为明确的测试配置；不是生产 Tag 验证、真实数据库备份或业务
smoke。真实备份恢复及应用兼容性由独立候选验收工具覆盖。此工具不调用安装入口、不修改
root 配置、不放宽正式发布门禁，不把成功写成正式 Release 或授权生产部署。


## 2026-10-11 实机正式发布验收

REL-20261011-002 已正式使用同一CI固定镜像发布到DS920plus：Stock Analyzer v3.23.0先于Dashboard v0.17.0；新备份、版本/镜像身份、生产smoke、真实席位契约、鉴权与新增迁移通过。受限发布入口已实机验证 exact-image capability；数据库回滚仍不自动downgrade，保留旧镜像和迁移前备份。详见 `releases/REL-20261011-002.yaml` 与 `releases/evidence/REL-20261011-002/`；用户确认公网历史9527存在家中路由回环限制；局域网HTTP9360页面与营业部搜索已在登录Chrome验收通过，操作入口可走Tailscale。

## marketNewsFeed 源码构建自动入口

新增 SOURCE_TAG_BUILD 分支，复用 image-release-v1 计划和已免密的 nas-image-release。
现有 stock-analyzer/Dashboard 的 CI_BUILD_ONCE 路径不变，不将 marketNewsFeed 宣称为镜像候选发布。
源码计划仅接受 marketNewsFeed、正式 SemVer Tag、完整 SHA、已验证的当前 Tag/SHA/Image ID、
同一目标 SHA 的测试证据、既有六项 gate 与明确正式授权。只支持 check/preflight/deploy/verify；
不接受镜像 export/prefetch、任意仓库/命令、浮动 ref 或直接数据库回滚。

NAS 管理员一次执行 `sudo bash deploy/enable-marketnews-source-release.sh`，保存受保护的旧
发布器/config 备份，保留实际 root 配置中的其他仓库命令，只启用已审查的 marketNewsFeed 配置。
这一步必须是管理员安装；不新增宽泛 sudo，不修改 sudoers、Docker 代理，不重启业务服务。
之后 Codex 可以复用已有 nas-image-release deploy 免密规则执行已授权的正式发布。

部署入口持同一全局 release.lock，核对真实生产基线，fetch 精确 Tag 并检查 origin/main lineage，
一次 custom pg_dump/pg_restore -l，可读后保留旧镜像和私密运行配置，再以部署用户执行业务
既有 deploy.sh。切换后重新读取实际容器 Image ID（不依赖旧脚本构建前的 Compose image 查询），
核对 Git SHA 与 Tag，检查本机 Admin 健康和 Bearer 保护的只读 research API。失败保存阶段与回执，
不会自动回滚数据库。已使用的 Release ID 不静默重建。健康 API 的内部 1.0 不是应用版本；
本项目仍以精确 Git Tag/SHA、绑定的实际 Image ID 标识此次 SOURCE_TAG_BUILD。

本机执行 `python3 scripts/image_release.py check <plan.json>`，安装后一次非写入应用的 preflight：
`python3 scripts/image_release.py preflight <plan.json> --host freemumu@100.86.90.115 --key <SSH-key>`。
后续得到正式发版授权后将 mode 改为 deploy 并提供 --receipt；常规发布不再重复 preflight/verify。
计划示例为 `deploy/marketnews-source-release.example.json`，其中占位 SHA/Image ID 必须替换为
当前真实身份，不作为可直接部署的生产计划。

## CHG-20261027-002 股票运行单元扩展（本地未发布）

新版stock-analyzer 使用 candidate-v2 及必需的 runtime_services.app 冻结 stock-api、stock-watch、stock-data；既有 candidate-v1 Manifest 保持原两进程，不静默套用新拓扑。新schema使未升级的NAS runner拒绝Candidate，防止旧工具忽略新增服务后使用浮动镜像。正式发布前必须安装本Change经过验证的runner；本地改动不表示已安装。仅允许该仓库增加已知stock-data，禁止任意服务名或遗漏旧核心服务。生产基线及rollback各自按被冻结的运行单元验证Image ID，普通部署不删除运行单元；减少服务走明确rollback流程。

首次扩展先验证旧基线/备份，再停旧API与业务采集者，才启动新增数据持有者；新数据心跳纳入验证。回退先验证所有在场容器没有无关漂移，按精确服务名停/移除仅新版本的数据容器，再切精确旧checkout/镜像。不会remove-orphans或删除数据卷。此变更仅更新本地发布工具，尚未安装NAS runner、打Tag或执行生产操作。
