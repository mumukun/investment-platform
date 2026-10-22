# 本地验证 — CHG-20261021-010

- 日期：2026-10-21 Asia/Shanghai。
- Dashboard：6b82051e8317972219affc40f79adb7a7cbac145。代码检查后提交；之后只补治理记录。
- Vitest：`npm test -- src/views/LimitUpLadderView.spec.ts`，6 passed / 1 file（3.16s）。覆盖矩阵/分组、筛选/空态、双向滚动、日期详情、未知连板、数据不可用/真实零家、缺失字段/未知标签隐藏、有效值及0值保留。
- `npm run build`：vue-tsc和Vite/PWA成功。仅既有大chunk提示，无构建失败。
- 版本：VERSION/package.json/package-lock.json两处/pyproject.toml/uv.lock统一0.30.1。
- `git diff --check`通过，提交范围无凭证或无关内容。

## 浏览器

本地Vite实际渲染同一Vue组件，独立预览壳、Element Plus、明确MOCK合成数据，12行业15只，包含缺扩展字段、未知连板、一字板、长题材及完整字段/炸板0样例。未使用真实行情、生产API、厂商或数据库；预览壳不代表完整应用外观。预览夹具源于现有Vitest示例，摘要计数未按合成扩展条目重算，截图不作为业务统计证据。

同一1280×900视口、相同夹具、切换矩阵后：

| DOM实测 | 修复前 | 修复后 |
| --- | --- | --- |
| 矩阵总高度 | 2599px | 1073px |
| 首个无扩展字段卡片高度 | 181px | 62px |
| 整页scrollWidth / viewport | 1280 / 1280 | 1280 / 1280 |

320×900：整页scrollWidth=320，矩阵内容896px，在内部横向滚动；键盘横向滚动后表头与内容scrollLeft同为20。搜索“完整”后匹配1只，首封09:31:00、末封14:22:00、炸板0、封单2.30亿均保留；所有事实dd均无scrollWidth>clientWidth，名称自然换行。部分字段缺失时不显示--占位，不冒充真实0。

- [修复前](matrix-before.png)
- [修复后](matrix-after.png)
- [320px完整字段](matrix-mobile.png)

临时浏览器页关闭、视口恢复、Vite服务停止、临时预览文件删除。未做生产/真机/全站视觉验收；Backend及Provider未改，未运行无关回归。当前只有本地提交，未推送、合并或发布。
